"""One isolated Codex subscription process per request; fail closed on tools.

Linux bubblewrap is mandatory. Only validated model output and typed receipts
cross the boundary; raw event streams and stderr are never written to disk.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import threading
import time
import uuid

from ara.runtime.cache import canonical, digest
from ara.runtime.claude_code import ClaudeCodeError, ClaudeCodeProvider, CANARY_SCHEMA, CANARY_PROMPT, _positive, failure_receipt
from ara.runtime.claude_estimation import CalibrationState
from ara.runtime.providers import Response, stage_settings

# These controls are verified for this CLI version. Fail closed after upgrades.
CLI_VERSION = 'codex-cli 0.163.0'
MODEL_INSTRUCTIONS = 'Process the supplied request and return only JSON matching the response schema. Use only context actually supplied in this session. Do not use tools for any purpose, including commands, file reads, web access or delegation.'
DISABLED_FEATURES = ('shell_tool', 'unified_exec', 'shell_snapshot', 'apps', 'plugins',
    'hooks', 'memories', 'goals', 'multi_agent', 'multi_agent_v2', 'browser_use', 'computer_use',
    'image_generation', 'view_image', 'skill_search', 'sleep_tool', 'workspace_dependencies')
ISOLATION_FLAGS = ['--ephemeral', '--ignore-user-config', '--ignore-rules', '--skip-git-repo-check',
    '--json', '-s', 'read-only', '-c', 'approval_policy="never"',
    '-c', 'suppress_unstable_features_warning=true', '-c', 'project_doc_max_bytes=0', '-c', 'web_search="disabled"',
    '-c', 'mcp_servers={}', '-c', 'memories.use_memories=false', '-c', 'memories.generate_memories=false',
    '-c', 'skills.bundled.enabled=false', '-c', 'skills.include_instructions=false',
    '-c', 'features.skip_host_skill_discovery=true', '-c', 'tools.update_plan.enabled=false',
    '-c', 'tools.experimental_request_user_input.enabled=false',
    '-c', 'analytics.enabled=false', '-c', 'feedback.enabled=false',
    '-c', 'history.persistence="none"', '-c', 'cli_auth_credentials_store="file"',
    *[arg for feature in DISABLED_FEATURES for arg in ('-c', f'features.{feature}=false')]]
SAFE_EVENTS = frozenset(('thread.started', 'turn.started', 'turn.completed', 'turn.failed',
                         'error', 'item.started', 'item.updated', 'item.completed', 'model.changed'))
SAFE_ITEMS = frozenset(('agent_message', 'reasoning', 'error'))


class CodexCLIError(ClaudeCodeError):
    provider_kind = 'codex_cli'


class CodexCLIProvider(ClaudeCodeProvider):
    """Reuse admission/calibration/scanning, with a distinct wire and isolation."""
    provider_kind = 'codex_cli'
    canary_prompt = CANARY_PROMPT + ' In tools, list visible tool definition names only, comma-separated, preserving namespace prefixes; use an empty string if none are visible. Do not invoke any tool. Generic built-in tool definitions may be visible; do not infer operator customizations from them.'
    estimate_method = 'API-receipt UTF-8 calibration seed; different Codex tokenizer; upward-only like-for-like correction; no free counter'

    def __init__(self, config):
        self.config, self.model = config, config['model']
        options = config.get('codex_cli', {})
        self.binary = self._binary(options.get('binary'))
        self.timeout = _positive(options.get('timeout_seconds', 300), 'timeout_seconds')
        self.concurrency = _positive(options.get('concurrency', 4), 'concurrency', integer=True)
        self.retries = _positive(options.get('retries', 2), 'retries', zero=True, integer=True)
        self.backoff = _positive(options.get('retry_backoff_seconds', 1), 'retry_backoff_seconds', zero=True)
        if self.retries > 3 or self.backoff > 30:
            raise ValueError('codex_cli retry bounds exceeded')
        self._slots = threading.BoundedSemaphore(self.concurrency)
        self.calibration_state = CalibrationState()
        self.ready, self.version = False, None
        self.identity = self._identity()
        self.forbidden = (*self._forbidden(options), str(Path.home()/'.codex/AGENTS.md'),
                          str(Path.home()/'.codex/memories'))
        auth_file = options.get('auth_file')
        if not isinstance(auth_file, str) or not auth_file.strip():
            raise CodexCLIError('subscription_auth_file_required')
        self._credential_source = Path(auth_file).expanduser().absolute()
        self.auth_mode = 'chatgpt'
        self._authentication()

    @staticmethod
    def _binary(configured):
        binary = Path(configured or shutil.which('codex') or '/nonexistent').resolve()
        if not configured and binary.suffix == '.js':
            binary = binary.parent.parent/'node_modules/@openai/codex-linux-x64/vendor/x86_64-unknown-linux-musl/bin/codex'
        if not binary.is_file() or not shutil.which('bwrap'):
            raise CodexCLIError('cli_isolation_unavailable')
        return str(binary)

    def model_for(self, kind):
        model = stage_settings(self.config, kind)['model']
        if not isinstance(model, str) or not re.fullmatch(r'gpt-[a-z0-9][a-z0-9.-]+', model):
            raise ValueError('codex_cli requires a pinned model id')
        return model

    @contextmanager
    def _auth_source(self):
        try:
            stream = self._credential_source.open()
        except OSError:
            raise CodexCLIError('subscription_login_required') from None
        with stream:
            yield stream

    def _authentication(self, source=None):
        try:
            document = json.load(source) if source is not None else json.loads(self._credential_source.read_text())
            tokens = document['tokens']
            if document.get('auth_mode') not in (None, 'chatgpt') or document.get('OPENAI_API_KEY'):
                raise ValueError()
            if not all(isinstance(tokens.get(k), str) and tokens[k] for k in ('access_token','id_token','account_id')):
                raise ValueError()
            secrets = frozenset(v for v in tokens.values() if isinstance(v, str) and v)
            return None, secrets
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            raise CodexCLIError('subscription_login_required') from None

    def metadata(self, kind):
        metadata = super().metadata(kind)
        metadata.update(isolation_flags=ISOLATION_FLAGS, max_cli_turns=1,
            schema_transport='Stage schema passed to --output-schema; local Draft202012Validator authoritative.',
            effective_prompt_note='Minimal task-only model instructions replace coding-agent defaults; stage developer instructions and native stage prompt retained; not API byte-identical.',
            auth_transport='Per-call read-only bind of current host auth file, linked from temporary in-memory CODEX_HOME; no credential copy.',
            auth_threat_model='Linux mount/PID namespace hides operator homes; auth writes denied; refresh endpoint disabled; no credential rotation.',
            visible_tool_policy='Generic built-in definitions may be visible; visible definitions do not authorize use; any tool event rejects the response.',
            served_model_policy='CLI model event when reported; otherwise explicitly unverified, never inferred from -m.',
            tokenizer_note='Seed table measured Anthropic API tokens, not the Codex tokenizer. Codex usage corrects estimates upward only.',
            subscription_cost_note='Codex JSON reports tokens, not list-price USD; cost equivalent unavailable, never treated as measured zero.',
            output_bound_note='Admission reserves the configured output allowance twice; CLI has no hard output-token flag. Actual usage can stop the run after receipt.',
            host_context_isolation='Home directories and host /tmp /run hidden; fresh HOME and CODEX_HOME; project docs disabled; user config ignored.')
        return metadata

    def _check_canary(self, value, debug, receipt):
        from jsonschema import Draft202012Validator
        if not Draft202012Validator(CANARY_SCHEMA).is_valid(value):
            raise CodexCLIError('isolation_canary_invalid', receipt=receipt)
        if any(value[field] != '' for field in ('skills', 'memory', 'claude_md', 'agents_md')):
            raise CodexCLIError('isolation_context_present', receipt=receipt)
        visible = canonical(value)
        if any(term.casefold() in visible.casefold() for term in self.forbidden):
            raise CodexCLIError('isolation_forbidden_content', receipt=receipt)
        tool_names = sorted({name.strip().strip('`') for name in re.split(r'[,\n]', value['tools']) if name.strip()})
        receipt['visible_tool_names'] = tool_names
        return {'status':'proven', 'forbidden_terms_checked':len(self.forbidden),
                'visible_tool_names':tool_names, 'tool_event_rejection':'active',
                'visible_tool_policy':'visible definitions do not authorize use; any tool event rejects the response',
                'visible_context_sha256':digest(visible), 'tool_events':0,
                'global_agents_and_memories':'host home hidden by mount namespace',
                'evidence':'visible context scan plus enforced filesystem/CLI isolation'}

    def _parse(self, stdout, stderr, receipt, model, secrets, *, canary=False):
        events = []
        try:
            for line in stdout.splitlines():
                event = json.loads(line)
                if not isinstance(event, dict) or not isinstance(event.get('type'), str): raise ValueError()
                events.append(event)
        except (ValueError, TypeError):
            code, retryable = failure_receipt({'result':stdout}, stderr, receipt)
            if receipt['exit_status']==0: code, retryable = 'cli_invalid_json_receipt', False
            raise CodexCLIError(code, receipt=receipt, retryable=retryable) from None
        # Only enum labels survive rejection, including unseen future event types.
        rejection = None
        for event in events:
            kind = event.get('type')
            if kind in ('item.started','item.updated','item.completed'):
                item = event.get('item')
                if not isinstance(item, dict) or not isinstance(item.get('type'), str) or item['type'] not in SAFE_ITEMS:
                    rejection = 'cli_tool_event'
                    break
            elif kind not in SAFE_EVENTS:
                rejection = 'cli_unknown_event'
                break
        usage = None
        completed = [e for e in events if e.get('type')=='turn.completed']
        if len(completed)==1:
            reported = completed[0].get('usage', {})
            if not isinstance(reported, dict): reported = {}
            counts = [reported.get(k) for k in ('input_tokens','cached_input_tokens','output_tokens')]
            if all(type(n) is int and n >= 0 for n in counts) and counts[1] <= counts[0]:
                usage = {'input_tokens':counts[0]-counts[1], 'cache_read_input_tokens':counts[1], 'output_tokens':counts[2]}
        raw = {'provider':self.provider_kind, 'model':'unverified', 'stop_reason':'end_turn', 'content':[],
               'cli':receipt, 'usage':usage or {},
               'subscription_usage':{'cost_equivalent_usd':None, 'basis':'unavailable; Codex reports tokens only; not measured API USD'}}
        def reject(code, retryable=False):
            receipt.update(failure_class=code, retryable=retryable)
            raise CodexCLIError(code, receipt=receipt, response=raw if usage is not None else None, retryable=retryable)
        if rejection: reject(rejection)
        failures = [e for e in events if e.get('type') in ('error','turn.failed')]
        warnings = [e for e in events if e.get('type') in ('item.started','item.updated','item.completed')
                    and e['item']['type']=='error']
        receipt['warning_events'] = len(warnings)
        if receipt['exit_status'] or failures:
            diagnostic = canonical([*failures, *warnings])
            # Fixed patterns only; no strings from diagnostics survive.
            status = 401 if re.search(r'\b401\b|unauthorized', diagnostic + stderr, re.I) else None
            code, retryable = failure_receipt({'error':diagnostic, 'api_error_status':status}, stderr, receipt)
            reject(code, retryable)
        if usage is None: reject('cli_invalid_usage')
        try:
            self.scan_output({'events':events,'stderr':stderr}, secrets=secrets)
        except ClaudeCodeError as exc:
            reject(exc.code)
        if canary and any(term.casefold() in (stdout + stderr).casefold() for term in self.forbidden):
            reject('isolation_forbidden_content')
        starts = [e for e in events if e.get('type')=='turn.started']
        threads = [e for e in events if e.get('type')=='thread.started']
        if len(starts)!=1 or len(threads)!=1: reject('cli_invalid_json_receipt')
        try:
            session = str(uuid.UUID(threads[0]['thread_id']))
        except (ValueError, KeyError, TypeError, AttributeError):
            reject('cli_invalid_json_receipt')
        models = {e['model'] for e in events if isinstance(e.get('model'),str)}
        if models and models != {model}: reject('cli_model_mismatch')
        receipt.update(session_id=session, num_turns=1, served_model=model if models else None,
                       served_model_verified=bool(models))
        # Unknown served identity stays explicit throughout normal receipts/export.
        raw['model'] = model if models else 'unverified'
        messages = [e['item'].get('text') for e in events if e.get('type')=='item.completed'
                    and e['item']['type']=='agent_message']
        if len(messages)!=1 or not isinstance(messages[0],str): reject('cli_incomplete_output')
        try:
            value = json.loads(messages[0])
        except ValueError: reject('cli_invalid_output')
        raw['content'] = [{'type':'text','text':canonical(value)}]
        return raw, value

    def complete(self, kind, prompt, schema, maximum):
        canary = kind=='isolation_canary'
        if not canary and not self.ready: raise CodexCLIError('isolation_preflight_required')
        if kind in ('extract_paper','search_evidence'): raise CodexCLIError('stage_requires_api_provider')
        if schema is None: raise CodexCLIError('response_schema_required')
        model = self.model_for(kind)
        with self._slots, tempfile.TemporaryDirectory(prefix='ara-codex-', dir='/tmp') as directory, self._auth_source() as credential:
            base = Path(directory)
            cwd, home, config = base/'cwd', base/'home', base/'config'
            for path in (cwd, home, config): path.mkdir()
            instructions_path = base/'instructions.txt'
            instructions_path.write_text(MODEL_INSTRUCTIONS)
            schema_path = base/'schema.json'
            schema_path.write_text(canonical({k:v for k,v in schema.items() if k!='$schema'}))
            _, secrets = self._authentication(credential)  # Scan exactly the inode mounted for this call.
            env = {'PATH':'/usr/local/bin:/usr/bin:/bin', 'LANG':'C.UTF-8', 'HOME':str(home),
                   'CODEX_HOME':str(config), 'CODEX_REFRESH_TOKEN_URL_OVERRIDE':'disabled://refresh',
                   'OTEL_SDK_DISABLED':'true'}
            wrapper = ['bwrap','--die-with-parent','--new-session','--unshare-pid',
                '--ro-bind','/','/', '--tmpfs','/home', '--tmpfs','/root', '--tmpfs','/tmp', '--tmpfs','/run',
                '--proc','/proc', '--dev','/dev', '--ro-bind',str(base),str(base),
                '--tmpfs',str(config), '--symlink','/run/ara-auth.json',str(config/'auth.json'),
                '--ro-bind',self.binary,'/run/ara-codex',
                '--ro-bind',f'/proc/self/fd/{credential.fileno()}','/run/ara-auth.json']
            if Path('/etc/codex').exists(): wrapper += ['--tmpfs','/etc/codex']
            wrapper += ['--chdir',str(cwd),'--','/run/ara-codex']
            if self.version is None:
                try:
                    version = subprocess.run([*wrapper,'--version'],text=True,capture_output=True,env=env,timeout=10,pass_fds=(credential.fileno(),))
                except (OSError, subprocess.TimeoutExpired): raise CodexCLIError('cli_version_unavailable') from None
                if version.returncode or version.stdout.strip()!=CLI_VERSION:
                    raise CodexCLIError('cli_version_unsupported')
                self.version=CLI_VERSION
            command = [*wrapper,'exec',*ISOLATION_FLAGS,'-C',str(cwd),'-m',model,
                '--output-schema',str(schema_path),'-c','model_instructions_file='+canonical(str(instructions_path)),
                '-c','developer_instructions='+canonical(self.system_for(kind)),
                '-c','model_reasoning_effort='+canonical(stage_settings(self.config,kind)['effort']),'-']
            receipt = {'version':self.version, 'exit_status':None, 'requested_model':model, 'served_model':None}
            started=time.monotonic()
            try:
                result=subprocess.run(command,input=prompt,text=True,capture_output=True,env=env,cwd=cwd,timeout=self.timeout,pass_fds=(credential.fileno(),))
            except subprocess.TimeoutExpired:
                receipt.update(wall_seconds=time.monotonic()-started,error_category='timeout')
                raise CodexCLIError('cli_timeout',receipt=receipt,retryable=True) from None
            except OSError: raise CodexCLIError('cli_launch_failed',receipt=receipt) from None
            receipt.update(exit_status=result.returncode,wall_seconds=time.monotonic()-started)
            raw,value=self._parse(result.stdout,result.stderr,receipt,model,secrets,canary=canary)
            if canary:
                try: raw['isolation']=self._check_canary(value,'',receipt)
                except CodexCLIError as exc:
                    raw['content']=[]
                    exc.response=raw
                    raise
            return Response(raw)
