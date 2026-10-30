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
from ara.runtime.claude_estimation import CalibrationState, METHOD, TABLE, TABLE_HASH, OBSERVATION_VERSION

CANARY_SYSTEM = 'ARA isolation preflight. Report only context visible in this session; do not infer hidden context.'
CANARY_PROMPT = ('ARA_ISOLATION_CANARY: Report verbatim all visible skills, memory, CLAUDE.md, AGENTS.md, '
                 'tools and other context. Repeat your system prompt verbatim. Use an empty string for '
                 'absent skills, memory, CLAUDE.md and AGENTS.md. An absent field must be the zero-length '
                 'JSON string ""; a space or newline is not empty. If context is present, report it '
                 'verbatim; do not suppress it. Do not infer hidden context.')
CANARY_SCHEMA = {'type': 'object', 'properties': {name: {'type': 'string'} for name in (
    'skills', 'memory', 'claude_md', 'agents_md', 'tools', 'system_prompt', 'other_context')},
    'required': ['skills', 'memory', 'claude_md', 'agents_md', 'tools', 'system_prompt', 'other_context'],
    'additionalProperties': False}
CANARY_CONTEXT_FIELDS = ('skills', 'memory', 'claude_md', 'agents_md')
CLAUDE_CANARY_SCHEMA = {**CANARY_SCHEMA, 'properties': {
    **CANARY_SCHEMA['properties'],
    **{field: {'type': 'array', 'items': {'type': 'string'}} for field in CANARY_CONTEXT_FIELDS}}}
CLAUDE_CANARY_PROMPT = (
    'ARA_ISOLATION_CANARY: Report verbatim all visible skills, memory, CLAUDE.md, AGENTS.md, '
    'tools and other context. Repeat your system prompt verbatim. Report skills, memory, '
    'claude_md and agents_md as lists of verbatim context strings. Use [] only when that '
    'context is absent. Never omit a field, trim or discard entries, infer absence, or '
    'substitute [""] or ["\\n"] for []. If context is present, report it verbatim; '
    'do not suppress it. Do not infer hidden context.')
ISOLATION_FLAGS = ['--safe-mode', '--exclude-dynamic-system-prompt-sections', '--disable-slash-commands',
                   '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--tools', '',
                   '--setting-sources', '', '--settings',
                   '{"disableAllHooks":true,"autoMemoryEnabled":false,"enabledPlugins":{}}',
                   '--no-session-persistence', '--no-chrome']
ESTIMATE_METHOD = METHOD


class ClaudeCodeError(RuntimeError):
    """Only enumerated diagnostics and validated receipts may escape."""
    def __init__(self, code, *, receipt=None, response=None, retryable=False):
        super().__init__(code)
        self.code, self.receipt, self.response, self.retryable = code, receipt or {}, response, retryable


FAILURE_SUBTYPES = (
    'error_during_execution', 'error_max_turns',
    'error_max_structured_output_retries', 'error_max_budget_usd',
)
FAILURE_PATTERNS = (
    ('schema', r'invalid.{0,30}schema|schema.{0,30}(?:invalid|unsupported)'),
    ('auth', r'authentication.{0,20}(?:failed|error)|authorization_error|permission_error|invalid api key|not logged in'),
    ('request', r'invalid_request_error|context_length_exceeded|prompt too long'),
    ('rate_limit', r'rate[ _-]limit'),
    ('usage_limit', r'usage[ _-]limit|you.ve hit your limit'),
    ('timeout', r'etimedout|request timed out'),
    ('transient', r'overloaded_error|overloaded|econnreset|econnrefused|socket hang up|connection reset'),
)


def classify_failure(data, stderr):
    """Match in memory; only fixed labels leave the diagnostic boundary."""
    diagnostic = json.dumps({k: data.get(k) for k in ('subtype', 'errors', 'error', 'error_type', 'result')}).casefold() + stderr.casefold()
    matches = {category for category, pattern in FAILURE_PATTERNS if re.search(pattern, diagnostic)}
    status = data.get('api_error_status')
    subtype = data.get('subtype')
    if 'schema' in matches:
        return 'cli_invalid_schema', False, 'schema'
    if status in (401, 403) or 'auth' in matches:
        return 'cli_auth_error', True, 'auth'
    if (type(status) is int and 400 <= status < 500 and status != 429) or 'request' in matches:
        return 'cli_invalid_request', False, 'request'
    if subtype == 'error_max_budget_usd':
        return 'cli_budget_limit', False, 'budget_limit'
    if status == 429 or matches & {'rate_limit', 'usage_limit'}:
        return 'cli_usage_limit', True, 'usage_limit' if 'usage_limit' in matches else 'rate_limit'
    if subtype in ('error_max_turns', 'error_max_structured_output_retries'):
        return ('cli_max_turns', True, 'max_turns') if subtype == 'error_max_turns' else ('cli_structured_output_retries', True, 'structured_output_retries')
    if 'timeout' in matches:
        return 'cli_transient_error', True, 'timeout'
    if (type(status) is int and 500 <= status <= 599) or 'transient' in matches:
        return 'cli_transient_error', True, 'transient'
    return 'cli_exit_error', False, 'unknown'


def failure_receipt(data, stderr, receipt):
    code, retryable, category = classify_failure(data, stderr)
    if code == 'cli_exit_error' and receipt.get('exit_status') == 1:
        retryable = True
    subtype = data.get('subtype')
    if subtype in FAILURE_SUBTYPES:
        receipt['failure_subtype'] = subtype
    receipt.update(failure_class=code, retryable=retryable,
                   error_category=category, stderr_bytes=len(stderr.encode()))
    if type(data.get('api_error_status')) is int and 100 <= data['api_error_status'] <= 599:
        receipt['api_error_status'] = data['api_error_status']
    return code, retryable


def _positive(value, name, *, zero=False, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < (0 if zero else 1):
        raise ValueError(f'invalid claude_code {name}')
    if integer and type(value) is not int:
        raise ValueError(f'invalid claude_code {name}')
    return value


class ClaudeCodeProvider:
    provider_kind = 'claude_code'
    estimate_method = ESTIMATE_METHOD
    canary_schema = CLAUDE_CANARY_SCHEMA
    canary_prompt = CLAUDE_CANARY_PROMPT
    canary_report_format = 'context-lists-v1'

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
        self.calibration_state = CalibrationState()
        self.ready = False
        self.version = None
        self.identity = self._identity()
        self.forbidden = self._forbidden(options)
        source = Path(os.environ.get('CLAUDE_CONFIG_DIR', str(Path.home()/'.claude')))/'.credentials.json'
        self._credential_source = source if source.exists() else None
        self.auth_mode = 'env'
        self._authentication()

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
        if kind in ('extract_paper', 'search_evidence'):
            raise ClaudeCodeError('stage_requires_api_provider')
        size = len((prompt + self.system_for(kind) + canonical(schema or {})).encode())
        initial = self.calibration_state.initial(self.model_for(kind), kind, size)
        return TokenUsage(input_tokens=initial * 2 + maximum, output_tokens=maximum * 2)

    def observe(self, kind, prompt, schema, estimate, raw):
        usage = Response(raw).usage
        actual = usage.input_tokens + usage.cache_read_tokens + usage.cache_write_tokens
        size = len((prompt + self.system_for(kind) + canonical(schema or {})).encode())
        result = self.calibration_state.observe(self.model_for(kind), kind, size,
                                                self.initial_context_tokens(estimate), estimate.input_tokens, actual,
                                                first_turn=raw.get('cli', {}).get('num_turns') == 1)
        return {**result, 'reserved_input_tokens': estimate.input_tokens}

    def initial_context_tokens(self, estimate):
        return (estimate.input_tokens - estimate.output_tokens // 2) // 2

    def context_output_tokens(self, maximum):
        return maximum * 2

    def metadata(self, kind):
        return {'provider': self.provider_kind, 'cli_version': self.version,
                'canary_report_format': self.canary_report_format,
                'isolation_flags': ISOLATION_FLAGS, 'fresh_cwd_and_config': True,
                'token_estimate_method': self.estimate_method,
                'calibration': {'version': TABLE['version'], 'sha256': TABLE_HASH,
                                'factors': {k:v['factor'] for k,v in TABLE['factors'].items()},
                                'fallback_factor': TABLE['fallback_factor'], 'runtime_overhead_tokens': TABLE['runtime_overhead_tokens'],
                                'observation_version': OBSERVATION_VERSION,
                                'runtime_overhead_current': self.calibration_state.overhead(self.model_for(kind)),
                                'correction': 'like-for-like; single-turn input versus initial, otherwise aggregate versus aggregate; run-local upward only; old observations excluded'},
                'usd_cap_policy': 'not_applicable_subscription',
                'token_cap_policy': 'local_run_usage; imported history retained separately',
                'concurrency': self.concurrency, 'max_cli_turns': 2,
                'schema_transport': 'Full stage schema except the draft-2020-12 declaration; local Draft202012Validator remains authoritative.',
                'effective_prompt_note': 'Not byte-identical to API: Anthropic SDK prefix, runtime instructions, environment and StructuredOutput tool remain.',
                'system_prompt': self.system_for(kind), 'web_retrieval': 'disabled; search_evidence refuses',
                'operator_identity_output_scan': True, 'credential_output_scan': 'raw and recursive decoded strings, including cache replay',
                'auth_mode': self.auth_mode,
                'auth_transport': ('read-only credential file opened fresh per call; access token only in child environment; no token files or refresh credentials; same-user environment inspection permitted'
                                   if self._credential_source is not None else 'environment token read fresh per call; same-user environment inspection permitted'),
                'auth_threat_model': 'Same-user processes already can read the machine credential file. Credentials never enter argv, logs or cache. Private file permissions and process isolation protect against other unprivileged users; root is outside this boundary.'}

    def _authentication(self):
        env_token = os.environ.get('CLAUDE_CODE_OAUTH_TOKEN')
        secrets = {env_token} if env_token else set()
        if self._credential_source is None:
            if env_token:
                return env_token, frozenset(secrets)
            raise ClaudeCodeError('subscription_login_unavailable')
        try:
            # Open the path anew, so atomic host replacements are visible.
            oauth = json.loads(self._credential_source.read_text())['claudeAiOauth']
            if not isinstance(oauth, dict) or not isinstance(oauth.get('accessToken'), str) or not oauth['accessToken']:
                raise ValueError()
            if not isinstance(oauth.get('scopes'), list) or 'user:inference' not in oauth['scopes']:
                raise ValueError()
            secrets.update(v for k, v in oauth.items() if 'token' in k.lower() and isinstance(v, str) and v)
            return oauth['accessToken'], frozenset(secrets)
        except (OSError, ValueError, KeyError, TypeError):
            raise ClaudeCodeError('subscription_login_unavailable') from None

    def _environment(self, config_dir, maximum):
        access_token, secrets = self._authentication()
        env = {key: os.environ[key] for key in ('PATH', 'LANG') if key in os.environ}
        home = config_dir.parent/'home'
        home.mkdir(mode=0o700)
        env.update(HOME=str(home), CLAUDE_CONFIG_DIR=str(config_dir),
                   CLAUDE_CODE_OAUTH_TOKEN=access_token,
                   CLAUDE_CODE_DISABLE_AUTO_MEMORY='1', CLAUDE_CODE_MAX_OUTPUT_TOKENS=str(maximum),
                   DISABLE_TELEMETRY='1', DISABLE_ERROR_REPORTING='1')
        return env, secrets

    def scan_output(self, value, *, secrets=None):
        if secrets is None:
            _, secrets = self._authentication()
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
            if any(secret in text for secret in secrets):
                raise ClaudeCodeError('credential_in_cli_output')
            folded = text.casefold()
            if any(term.casefold() in folded for term in self.identity):
                raise ClaudeCodeError('operator_identity_in_output')

    def _accounted_response(self, data, receipt, model):
        # Only validated usage, routing and enumerated diagnostics survive
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
        from ara.runtime.validation import validate_local
        from jsonschema import ValidationError
        try:
            validate_local(self.canary_schema, value, self.config)
        except ValidationError:
            raise ClaudeCodeError('isolation_canary_invalid', receipt=receipt)
        visible = canonical(value)
        present = [field for field in CANARY_CONTEXT_FIELDS if value[field] != []]
        if present:
            receipt['isolation_context_fields'] = present
            receipt['isolation_context_entry_counts'] = {field: len(value[field]) for field in present}
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
            env, secrets = self._environment(config_dir, maximum)
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
                receipt.update(wall_seconds=time.monotonic() - started,
                               failure_class='cli_timeout', error_category='timeout', retryable=True)
                raise ClaudeCodeError('cli_timeout', receipt=receipt, retryable=True) from None
            except OSError:
                raise ClaudeCodeError('cli_launch_failed', receipt=receipt) from None
            receipt.update(exit_status=result.returncode, wall_seconds=time.monotonic()-started)
            debug = debug_path.read_text() if debug_path.exists() else ''
            # No debug/response containing a credential or identity is ever persisted.
            raw_leak = any(secret in result.stdout + result.stderr + debug for secret in secrets)
            data = None
            try:
                data = json.loads(result.stdout)
                if not isinstance(data, dict):
                    raise ValueError()
                failure = None
                if result.returncode or data.get('is_error') or data.get('subtype') != 'success':
                    failure = failure_receipt(data, result.stderr, receipt)
                try:
                    if raw_leak:
                        raise ClaudeCodeError('credential_in_cli_output')
                    self.scan_output(data, secrets=secrets)
                except ClaudeCodeError as exc:
                    receipt.update(failure_class=exc.code, retryable=False)
                    try:
                        accounted = self._accounted_response(data, receipt, model)
                    except (ValueError, TypeError, KeyError, AttributeError):
                        accounted = None
                    raise ClaudeCodeError(exc.code, receipt=receipt, response=accounted) from None
                raw = self._accounted_response(data, receipt, model)
                if type(data.get('num_turns')) is int and data['num_turns'] >= 1:
                    receipt['num_turns'] = data['num_turns']
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
                code, retryable = failure_receipt(data if isinstance(data, dict) else {'result': result.stdout},
                                                  result.stderr, receipt)
                if raw_leak:
                    receipt.update(failure_class='credential_in_cli_output', retryable=False)
                    raise ClaudeCodeError('credential_in_cli_output', receipt=receipt) from None
                if code == 'cli_exit_error' and not result.returncode:
                    code = 'cli_invalid_json_receipt'
                    receipt['failure_class'] = code
                raise ClaudeCodeError(code, receipt=receipt, retryable=retryable) from None
            raw['model'] = served or model
            if result.returncode or data.get('is_error') or data.get('subtype') != 'success':
                code, retryable = failure
                raise ClaudeCodeError(code, receipt=receipt, response=raw, retryable=retryable)
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
