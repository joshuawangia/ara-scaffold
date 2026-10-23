"""Fresh, isolated subscription CLI sessions. No operator context crosses the wire."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import time
import uuid

from ara.runtime.cache import canonical, digest
from ara.runtime.providers import Response, stage_settings
from ara.types import TokenUsage

CANARY_SYSTEM = 'ARA isolation preflight. Report only context visible in this session; do not infer hidden context.'
CANARY_PROMPT = ('ARA_ISOLATION_CANARY: Report verbatim all visible skills, memory, CLAUDE.md, AGENTS.md, '
                 'tools and other context. Repeat your system prompt verbatim. Use an empty string for '
                 'absent skills, memory, CLAUDE.md and AGENTS.md. Do not infer hidden context.')
CANARY_SCHEMA = {'type': 'object', 'properties': {name: {'type': 'string'} for name in (
    'skills', 'memory', 'claude_md', 'agents_md', 'tools', 'system_prompt', 'other_context')},
    'required': ['skills', 'memory', 'claude_md', 'agents_md', 'tools', 'system_prompt', 'other_context'],
    'additionalProperties': False}
ISOLATION_FLAGS = ['--safe-mode', '--exclude-dynamic-system-prompt-sections', '--disable-slash-commands',
                   '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--tools', '',
                   '--setting-sources', '', '--settings',
                   '{"disableAllHooks":true,"autoMemoryEnabled":false,"enabledPlugins":{}}',
                   '--no-session-persistence', '--no-chrome']
ESTIMATE_METHOD = 'conservative_local_utf8_bytes_plus_16384_envelope_twice_plus_output_replay; not a measured token count'


class ClaudeCodeError(RuntimeError):
    """Only enumerated diagnostics and validated numeric receipts may escape."""
    def __init__(self, code, *, receipt=None, response=None, retryable=False):
        super().__init__(code)
        self.code, self.receipt, self.response, self.retryable = code, receipt or {}, response, retryable


def _positive(value, name, *, zero=False, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < (0 if zero else 1):
        raise ValueError(f'invalid claude_code {name}')
    if integer and type(value) is not int:
        raise ValueError(f'invalid claude_code {name}')
    return value


class ClaudeCodeProvider:
    provider_kind = 'claude_code'
    estimate_method = ESTIMATE_METHOD

    def __init__(self, config):
        self.config, self.model = config, config['model']
        options = config.get('claude_code', {})
        self.binary = options.get('binary', 'claude')
        self.timeout = _positive(options.get('timeout_seconds', 300), 'timeout_seconds')
        self.concurrency = _positive(options.get('concurrency', 4), 'concurrency', integer=True)
        self.retries = _positive(options.get('retries', 2), 'retries', zero=True, integer=True)
        if self.retries > 3:
            raise ValueError('claude_code retries must be between 0 and 3')
        self.backoff = _positive(options.get('retry_backoff_seconds', 1), 'retry_backoff_seconds', zero=True)
        if self.backoff > 30:
            raise ValueError('claude_code retry_backoff_seconds must be at most 30')
        self._slots = threading.BoundedSemaphore(self.concurrency)
        self.ready = False
        self.version = None
        self.identity = self._identity()
        self.forbidden = self._forbidden(options)
        self._oauth, self._env_token, self._secrets = self._authentication()
        self.auth_mode = 'config-link' if self._oauth is not None else 'env'

    def _identity(self):
        values = []
        for key in ('user.email', 'user.name'):
            result = subprocess.run(['git', 'config', '--get', key], capture_output=True, text=True)
            if result.returncode or not result.stdout.strip():
                raise ClaudeCodeError('operator_identity_unavailable')
            values.append(result.stdout.strip())
        return tuple(values)

    def _forbidden(self, options):
        """Inventory names/paths only; never load operator prompt or memory bodies."""
        home = Path.home()
        supplied = options.get('forbidden_terms', [])
        if not isinstance(supplied, list):
            raise ValueError('claude_code forbidden_terms must be a list')
        terms = set(supplied)
        if not all(isinstance(term, str) and term.strip() for term in terms):
            raise ValueError('claude_code forbidden_terms must contain nonempty strings')
        roots = [home/'.claude/skills', home/'.agents/skills', home/'.codex/skills']
        installed = home/'.claude/plugins/installed_plugins.json'
        if installed.exists():
            data = json.loads(installed.read_text())
            for entries in data.get('plugins', {}).values():
                for entry in entries:
                    if entry.get('installPath'):
                        roots.append(Path(entry['installPath'])/'skills')
        for root in roots:
            terms.add(str(root))
            if root.exists():
                for entry in root.iterdir():
                    if entry.name.startswith('.'):
                        continue
                    terms.add(entry.name)
                    skill = entry/'SKILL.md'
                    if skill.is_file():
                        # Read just the metadata header; no skill body becomes context.
                        with skill.open() as stream:
                            if stream.readline().strip() == '---':
                                for line in stream:
                                    if line.strip() == '---':
                                        break
                                    match = re.fullmatch(r'name:\s*[\"\']?([^\"\'\n]+)[\"\']?\s*', line.strip())
                                    if match:
                                        terms.add(match[1].strip())
        projects = home/'.claude/projects'
        terms.add(str(projects))
        terms.add(str(home/'.claude/memory'))
        if projects.exists():
            for project in projects.iterdir():
                if project.is_dir():
                    terms.add(str(project))
                    terms.add(str(project/'memory'))
        settings = home/'.claude.json'
        if settings.exists():
            for name in json.loads(settings.read_text()).get('projects', {}):
                terms.add(name)
                if len(Path(name).name) > 2:
                    terms.add(Path(name).name)
        # Explicit operator terms supplement names discoverable from Claude's registries.
        return tuple(sorted(terms))

    def model_for(self, kind):
        model = stage_settings(self.config, kind)['model']
        if not isinstance(model, str) or not re.fullmatch(r'claude-[a-z0-9][a-z0-9.-]+', model):
            raise ValueError('claude_code requires a pinned full model id')
        return model

    def system_for(self, kind):
        return CANARY_SYSTEM if kind == 'isolation_canary' else stage_settings(self.config, kind).get('system_prompt', '')

    def estimate(self, kind, prompt, schema, maximum):
        # Byte-per-token bound plus headroom for CLI defaults/schema tooling. Two
        # CLI turns are permitted, so reserve the whole context/output twice.
        size = len((prompt + self.system_for(kind) + canonical(schema or {})).encode()) + 16384
        if kind in ('extract_paper', 'search_evidence'):
            raise ClaudeCodeError('stage_requires_api_provider')
        return TokenUsage(input_tokens=size * 2 + maximum, output_tokens=maximum * 2)

    def initial_context_tokens(self, estimate):
        return (estimate.input_tokens - estimate.output_tokens // 2) // 2

    def context_output_tokens(self, maximum):
        return maximum * 2

    def metadata(self, kind):
        return {'provider': self.provider_kind, 'cli_version': self.version,
                'isolation_flags': ISOLATION_FLAGS, 'fresh_cwd_and_config': True,
                'token_estimate_method': self.estimate_method, 'usd_cap_policy': 'not_applicable_subscription',
                'concurrency': self.concurrency, 'max_cli_turns': 2,
                'schema_transport': 'Full stage schema except the draft-2020-12 declaration; local Draft202012Validator remains authoritative.',
                'effective_prompt_note': 'Not byte-identical to API: Anthropic SDK prefix, runtime instructions, environment and StructuredOutput tool remain.',
                'system_prompt': self.system_for(kind), 'web_retrieval': 'disabled; search_evidence refuses',
                'operator_identity_output_scan': True, 'credential_output_scan': 'raw and recursive decoded strings, including cache replay',
                'auth_mode': self.auth_mode,
                'auth_transport': ('private 0600 OAuth snapshot; no token in child environment; deleted after each call; refresh disabled; inference-only CLI scope metadata'
                                   if self.auth_mode == 'config-link' else 'environment token; same-user environment inspection permitted'),
                'auth_threat_model': 'Same-user processes already can read the machine credential file. Credentials never enter argv, logs or cache. Private file permissions and process isolation protect against other unprivileged users; root is outside this boundary.'}

    def _authentication(self):
        source = Path(os.environ.get('CLAUDE_CONFIG_DIR', str(Path.home()/'.claude')))/'.credentials.json'
        env_token = os.environ.get('CLAUDE_CODE_OAUTH_TOKEN')
        secrets = {env_token} if env_token else set()
        try:
            oauth = json.loads(source.read_text())['claudeAiOauth']
            if not isinstance(oauth, dict) or not isinstance(oauth.get('accessToken'), str) or not oauth['accessToken']:
                raise ValueError()
            secrets.update(v for k, v in oauth.items() if 'token' in k.lower() and isinstance(v, str) and v)
            # Copy authentication data only. No MCP credentials or operator settings.
            # Omit refresh credentials: a child must not rotate the machine login.
            if not isinstance(oauth.get('scopes'), list) or 'user:inference' not in oauth['scopes']:
                raise ValueError()
            snapshot = {k: oauth[k] for k in ('accessToken', 'expiresAt', 'subscriptionType',
                                             'subscriptionTypeSource', 'rateLimitTier') if k in oauth}
            # Match env-token mode's inference-only discovery: profile scope makes
            # the CLI fetch account identity and inject it into model context.
            # This limits CLI behavior, not the token's server-side permissions.
            snapshot['scopes'] = ['user:inference']
            return snapshot, None, frozenset(secrets)
        except FileNotFoundError:
            if env_token:
                return None, env_token, frozenset(secrets)
        except (OSError, ValueError, KeyError, TypeError):
            pass
        raise ClaudeCodeError('subscription_login_unavailable')

    def _environment(self, config_dir, maximum):
        env = {key: os.environ[key] for key in ('PATH', 'HOME', 'LANG') if key in os.environ}
        env.update(CLAUDE_CONFIG_DIR=str(config_dir),
                   CLAUDE_CODE_DISABLE_AUTO_MEMORY='1', CLAUDE_CODE_MAX_OUTPUT_TOKENS=str(maximum),
                   DISABLE_TELEMETRY='1', DISABLE_ERROR_REPORTING='1')
        if self._oauth is not None:
            # A private snapshot, rather than a symlink/hardlink that the CLI could
            # write through to the original. TemporaryDirectory removes it on exit.
            path = config_dir/'.credentials.json'
            with open(path, 'x', opener=lambda name, flags: os.open(name, flags, 0o600)) as stream:
                json.dump({'claudeAiOauth': self._oauth}, stream)
        else:
            env['CLAUDE_CODE_OAUTH_TOKEN'] = self._env_token
        return env

    def scan_output(self, value):
        def strings(node):
            if isinstance(node, dict):
                for key, child in node.items():
                    yield from strings(key)
                    yield from strings(child)
            elif isinstance(node, list):
                for child in node:
                    yield from strings(child)
            elif isinstance(node, str):
                yield node
                # Cache content and CLI result fields may themselves contain JSON.
                if node.lstrip().startswith(('{', '[', '"')):
                    try:
                        decoded = json.loads(node)
                    except (ValueError, RecursionError):
                        return
                    yield from strings(decoded)
        for text in strings(value):
            if any(secret in text for secret in self._secrets):
                raise ClaudeCodeError('credential_in_cli_output')
            folded = text.casefold()
            if any(term.casefold() in folded for term in self.identity):
                raise ClaudeCodeError('operator_identity_in_output')

    def _accounted_response(self, data, receipt, model):
        # Only validated numeric fields and locally generated routing data survive
        # rejection. Never copy unscanned CLI model/session/content strings here.
        usage = Response.usage_fields(data['usage'])
        if not {'input_tokens', 'output_tokens'} <= data['usage'].keys() or not all(
                type(n) is int and n >= 0 for n in usage.to_dict().values()):
            raise ValueError()
        equivalent = data['total_cost_usd']
        _positive(equivalent, 'reported_cost', zero=True)
        return {'model': model, 'stop_reason': 'end_turn', 'content': [],
                'usage': {'input_tokens': usage.input_tokens, 'output_tokens': usage.output_tokens,
                          'cache_read_input_tokens': usage.cache_read_tokens,
                          'cache_creation_input_tokens': usage.cache_write_tokens,
                          'server_tool_use': {'web_search_requests': usage.server_tool_uses}},
                'cli': receipt, 'provider': self.provider_kind,
                'subscription_usage': {'cost_equivalent_usd': equivalent,
                                       'basis': 'CLI reported list-price equivalent; not measured API USD'}}

    def _check_canary(self, value, debug, receipt):
        from jsonschema import Draft202012Validator
        if not Draft202012Validator(CANARY_SCHEMA).is_valid(value):
            raise ClaudeCodeError('isolation_canary_invalid', receipt=receipt)
        visible = canonical(value)
        if any(value[field] != '' for field in ('skills', 'memory', 'claude_md', 'agents_md')):
            raise ClaudeCodeError('isolation_context_present', receipt=receipt)
        if ('StructuredOutput' not in value['tools'] or re.search(
                r'\b(?:Bash|Read|Write|Edit|Glob|Grep|WebFetch|WebSearch|Agent|Skill|ToolSearch)\b', value['tools'])):
            raise ClaudeCodeError('isolation_tools_present', receipt=receipt)
        if CANARY_SYSTEM not in value['system_prompt']:
            raise ClaudeCodeError('isolation_system_mismatch', receipt=receipt)
        combined = (visible + debug).casefold()
        if any(term.casefold() in combined for term in self.forbidden):
            raise ClaudeCodeError('isolation_forbidden_content', receipt=receipt)
        required = ('Skipping skill dir discovery', 'project memory is off',
                    'Safe mode: installed plugins are disabled', '[claudeai-mcp] Disabled in safe mode')
        if not all(marker in debug for marker in required):
            raise ClaudeCodeError('isolation_debug_unproven', receipt=receipt)
        return {'status': 'proven', 'forbidden_terms_checked': len(self.forbidden),
                'visible_context_sha256': digest(visible), 'debug_sha256': digest(debug),
                'user_skills_empty': True, 'memory_empty': True, 'claude_md_empty': True,
                'agents_md_empty': True, 'debug_markers_present': True,
                'operator_identity_suppressed': True,
                'accepted_defaults': ['Anthropic built-in plugins', 'SDK prefix and runtime instructions',
                                      'environment information', 'StructuredOutput tool']}

    def complete(self, kind, prompt, schema, maximum):
        canary = kind == 'isolation_canary'
        if not canary and not self.ready:
            raise ClaudeCodeError('isolation_preflight_required')
        if kind in ('extract_paper', 'search_evidence'):
            raise ClaudeCodeError('stage_requires_api_provider')
        model = self.model_for(kind)
        if schema is None:
            raise ClaudeCodeError('response_schema_required')
        with self._slots, tempfile.TemporaryDirectory(prefix='ara-claude-', dir='/tmp') as directory:
            base = Path(directory)
            cwd, config_dir = base/'cwd', base/'config'
            cwd.mkdir(); config_dir.mkdir()
            for parent in (cwd, *cwd.parents):
                if any((parent/name).exists() for name in ('AGENTS.md', 'CLAUDE.md', '.claude/CLAUDE.md')):
                    raise ClaudeCodeError('isolation_ancestor_instructions')
            env = self._environment(config_dir, maximum)
            if self.version is None:
                try:
                    version = subprocess.run([self.binary, '--version'], capture_output=True, text=True,
                                             cwd=cwd, env=env, timeout=10)
                except (OSError, subprocess.TimeoutExpired):
                    raise ClaudeCodeError('cli_version_unavailable') from None
                if version.returncode or not re.fullmatch(r'\d+\.\d+\.\d+ \(Claude Code\)\s*', version.stdout):
                    raise ClaudeCodeError('cli_version_unavailable')
                self.version = version.stdout.strip()
            session_id = str(uuid.uuid4())
            command = [self.binary, '-p', '--session-id', session_id, '--model', model, '--output-format', 'json',
                       '--json-schema', canonical({k: v for k, v in schema.items() if k != '$schema'}), '--system-prompt', self.system_for(kind),
                       '--effort', stage_settings(self.config, kind)['effort'], '--max-turns', '2', *ISOLATION_FLAGS]
            debug_path = base/'debug'
            if canary:
                command += ['--debug-file', str(debug_path)]
            started = time.monotonic()
            receipt = {'version': self.version, 'exit_status': None, 'session_id': session_id,
                       'requested_model': model, 'served_model': None}
            try:
                result = subprocess.run(command, input=prompt, text=True, capture_output=True,
                                        cwd=cwd, env=env, timeout=self.timeout)
            except subprocess.TimeoutExpired:
                receipt['wall_seconds'] = time.monotonic() - started
                raise ClaudeCodeError('cli_timeout', receipt=receipt) from None
            except OSError:
                raise ClaudeCodeError('cli_launch_failed', receipt=receipt) from None
            receipt.update(exit_status=result.returncode, wall_seconds=time.monotonic()-started)
            debug = debug_path.read_text() if debug_path.exists() else ''
            # No debug/response containing a credential or identity is ever persisted.
            raw_leak = any(secret in result.stdout + result.stderr + debug for secret in self._secrets)
            try:
                data = json.loads(result.stdout)
                if not isinstance(data, dict):
                    raise ValueError()
                try:
                    if raw_leak:
                        raise ClaudeCodeError('credential_in_cli_output')
                    self.scan_output(data)
                except ClaudeCodeError as exc:
                    try:
                        accounted = self._accounted_response(data, receipt, model)
                    except (ValueError, TypeError, KeyError, AttributeError):
                        accounted = None
                    raise ClaudeCodeError(exc.code, receipt=receipt, response=accounted) from None
                raw = self._accounted_response(data, receipt, model)
                session = str(uuid.UUID(data['session_id']))
                if session != session_id:
                    raise ValueError()
                models = data['modelUsage']
                if not isinstance(models, dict) or not models or any(
                        not re.fullmatch(r'claude-[a-z0-9][a-z0-9.-]+', m) for m in models):
                    raise ValueError()
                served = next(iter(models)) if len(models) == 1 else None
                receipt.update(session_id=session, served_model=served, served_models=list(models))
            except (ValueError, TypeError, KeyError, AttributeError):
                if raw_leak:
                    raise ClaudeCodeError('credential_in_cli_output', receipt=receipt) from None
                limited = bool(re.search(r'(?:rate|usage)[ _-]limit|you.ve hit your limit',
                                         result.stdout + result.stderr, re.IGNORECASE))
                raise ClaudeCodeError('cli_usage_limit' if limited else
                                      'cli_invalid_json_receipt' if not result.returncode else 'cli_exit_error',
                                      receipt=receipt, retryable=limited) from None
            raw['model'] = served or model
            diagnostic = json.dumps(data, ensure_ascii=False).casefold()
            if result.returncode or data.get('is_error') or data.get('subtype') != 'success':
                limited = data.get('api_error_status') == 429 or any(word in diagnostic for word in ('rate limit', 'usage limit', 'usage_limit', 'rate_limit', "you've hit your limit"))
                raise ClaudeCodeError('cli_usage_limit' if limited else 'cli_exit_error', receipt=receipt,
                                      response=raw, retryable=limited)
            if served != model:
                raise ClaudeCodeError('cli_model_mismatch', receipt=receipt, response=raw)
            if (data.get('stop_reason') not in ('tool_use', 'end_turn') or 'structured_output' not in data
                    or data.get('permission_denials') or Response(raw).usage.server_tool_uses):
                raise ClaudeCodeError('cli_incomplete_output', receipt=receipt, response=raw)
            if canary:
                try:
                    raw['isolation'] = self._check_canary(data['structured_output'], debug, receipt)
                except ClaudeCodeError as exc:
                    exc.response = raw
                    raise
            raw['content'] = [{'type': 'text', 'text': canonical(data['structured_output'])}]
            return Response(raw)
