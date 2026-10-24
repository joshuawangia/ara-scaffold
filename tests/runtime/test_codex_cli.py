"""Subscription CLI boundary, exercised with a real disposable executable."""
import json
from pathlib import Path

import pytest
import yaml

from ara.runtime.cli import make_calls
from ara.runtime.logging import EventLog
from ara.types import Proposition

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def codex(tmp_path, monkeypatch):
    home = tmp_path/'operator'
    (home/'.codex/memories').mkdir(parents=True)
    (home/'.gitconfig').write_text('[user]\nname = Operator Sentinel\nemail = sentinel@example.invalid\n')
    (home/'.codex/AGENTS.md').write_text('PRIVATE_CONTEXT_SENTINEL')
    (home/'.codex/memories/memory.md').write_text('PRIVATE_MEMORY_SENTINEL')
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', str(home/'.gitconfig'))
    monkeypatch.setenv('GIT_CONFIG_NOSYSTEM', '1')
    monkeypatch.delenv('CODEX_HOME', raising=False)
    auth = home/'.codex/auth.json'
    auth.write_text(json.dumps({'auth_mode':'chatgpt', 'tokens':{
        'access_token':'offline-access', 'refresh_token':'offline-refresh', 'id_token':'offline-id',
        'account_id':'offline-account'}, 'last_refresh':'2026-10-24T00:00:00Z'}))
    binary = tmp_path/'fake-codex'
    config = yaml.safe_load((ROOT/'config.yaml').read_text())
    config.update(provider='codex_cli', model='gpt-5.4', stages={}, fallbacks=[], token_cap=500000,
                  cost_cap_usd=0, cache_dir=str(tmp_path/'cache'),
                  codex_cli={'binary':str(binary), 'auth_file':str(auth), 'retries':0,
                             'retry_backoff_seconds':0, 'timeout_seconds':10})
    def write(mode='ok', token='offline-access'):
        binary.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args=sys.argv[1:]
if args == ['--version']:
 print('codex-cli 0.163.0'); sys.exit()
def arg(k): return args[args.index(k)+1]
assert args[0]=='exec'
assert all(k in args for k in ['--ephemeral','--ignore-user-config','--skip-git-repo-check','--json','--ignore-rules'])
assert arg('-s')=='read-only'
assert 'approval_policy="never"' in args and 'features.shell_tool=false' in args
assert 'features.goals=false' in args
assert not list(Path.cwd().iterdir())
assert Path(arg('-C'))==Path.cwd()
assert not Path(__OPERATOR_HOME__).exists()
assert not any(k in os.environ for k in ['OPENAI_API_KEY','CODEX_API_KEY','ANTHROPIC_API_KEY'])
assert os.environ['CODEX_REFRESH_TOKEN_URL_OVERRIDE']=='disabled://refresh'
home=Path(os.environ['CODEX_HOME'])
assert sorted(p.name for p in home.iterdir())==['auth.json']
assert (home/'auth.json').is_symlink()
auth=json.loads((home/'auth.json').read_text())
assert auth['tokens']['access_token']==__TOKEN__
try:
 (home/'auth.json').write_text('bad')
except OSError: pass
else: raise AssertionError('auth writable')
assert not (Path.home()/'.codex/AGENTS.md').exists()
assert not (Path.home()/'.codex/memories').exists()
prompt=sys.stdin.read()
schema=json.loads(Path(arg('--output-schema')).read_text())
canary='ARA_ISOLATION_CANARY' in prompt
value={k:'' for k in schema['properties']} if canary else {'formula':{'op':'atom','name':'P'}}
if canary: value['system_prompt']='ARA isolation preflight.'
mode=__MODE__ if not canary else 'ok'
def emit(d): print(json.dumps(d))
emit({'type':'thread.started','thread_id':'11111111-1111-4111-8111-111111111111'})
emit({'type':'turn.started','model':arg('-m')})
if mode.startswith('tool:'):
 emit({'type':'item.completed','item':{'type':mode.split(':',1)[1],'command':'PRIVATE_CONTEXT_SENTINEL','text':'P'}})
if mode=='unknown': emit({'type':'future.event','text':'PRIVATE_CONTEXT_SENTINEL'})
if mode=='warning': emit({'type':'item.completed','item':{'type':'error','message':'P'}})
if mode=='item_error':
 emit({'type':'item.completed','item':{'type':'error','message':'HTTP 401 offline-access'}}); sys.exit(1)
if mode=='auth':
 emit({'type':'error','message':'HTTP 401 unauthorized offline-access'}); sys.exit(1)
if mode=='rate':
 emit({'type':'error','message':'rate limit "api_key":"offline-access" P'}); sys.exit(1)
if mode=='usage':
 emit({'type':'error','message':"You've hit your usage limit PRIVATE_CONTEXT_SENTINEL"}); sys.exit(1)
if mode=='diagnostic':
 print('"api_key":"offline-access" P',file=sys.stderr); sys.exit(7)
if mode=='identity': value={'formula':{'op':'atom','name':'sentinel@example.invalid'}}
if mode=='secret': value={'formula':{'op':'atom','name':'offline-access'}}
if mode=='bad_schema': value={'bad':'P'}
if mode=='mismatch': emit({'type':'model.changed','model':'gpt-5.3-codex'})
if mode=='canary_leak': value['other_context']='PRIVATE_CONTEXT_SENTINEL'
emit({'type':'item.completed','item':{'id':'item_0','type':'agent_message','text':json.dumps(value)}})
emit({'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':20,'output_tokens':10}})
'''.replace('__OPERATOR_HOME__', repr(str(home))).replace('__TOKEN__', repr(token)).replace('__MODE__',repr(mode)))
        binary.chmod(0o700)
    write()
    return config, auth, write, tmp_path


def test_native_calls_and_receipts(codex):
    config, auth, write, tmp = codex
    log = EventLog(tmp/'events.jsonl')
    calls = make_calls(config, log, 'P')
    assert calls.formalise(Proposition('p','P')).name == 'P'
    rows=[json.loads(e['payload_json']) for e in log.read() if e['label']=='MODEL']
    assert len(rows)==2
    assert all(r['provider']=='codex_cli' and r['cli']['num_turns']==1 for r in rows)
    assert all(r['cli']['served_model']=='gpt-5.4' for r in rows)
    assert all(e['cost_usd']==0 for e in log.read())
    assert calls.budget.used_tokens==220
    assert rows[0]['isolation']['status']=='proven'


@pytest.mark.parametrize('tool', ['command_execution','file_read','file_change','web_search','mcp_tool_call','tool_call','function_call'])
def test_tool_event_rejected_without_echo(codex, tool):
    from ara.runtime.calls import Rejected
    config, auth, write, tmp = codex
    log=EventLog(tmp/'events.jsonl'); calls=make_calls(config,log,'P')
    write('tool:'+tool)
    with pytest.raises(Rejected, match='cli_tool_event'):
        calls.formalise(Proposition('p','P'))
    text=log.path.read_text()
    assert 'PRIVATE_CONTEXT_SENTINEL' not in text and 'offline-access' not in text
    assert not list((tmp/'cache').rglob('*.json'))


def test_fresh_credential_and_read_only_link(codex):
    config, auth, write, tmp=codex
    calls=make_calls(config,EventLog(tmp/'events.jsonl'),'P')
    replacement=auth.with_suffix('.new')
    doc=json.loads(auth.read_text()); doc['tokens']['access_token']='new-access'
    replacement.write_text(json.dumps(doc)); replacement.replace(auth)
    write(token='new-access')
    assert calls.formalise(Proposition('p','P')).name=='P'
    assert json.loads(auth.read_text())==doc


@pytest.mark.parametrize('mode,code', [('unknown','cli_unknown_event'),('rate','cli_usage_limit'),
    ('usage','cli_usage_limit'),('auth','cli_auth_error'),('item_error','cli_auth_error'),('diagnostic','cli_exit_error'),
    ('identity','operator_identity_in_output'),('secret','credential_in_cli_output'),('mismatch','cli_model_mismatch')])
def test_suppressed_failures(codex,mode,code):
    from ara.runtime.calls import Rejected
    config, auth, write, tmp=codex
    log=EventLog(tmp/'events.jsonl'); calls=make_calls(config,log,'P'); write(mode)
    with pytest.raises(Rejected,match=code): calls.formalise(Proposition('p','P'))
    text=log.path.read_text()
    assert 'offline-access' not in text and 'PRIVATE_CONTEXT_SENTINEL' not in text
    assert 'sentinel@example.invalid' not in text


@pytest.mark.parametrize('mixed', [False, True])
def test_api_key_refused(codex, mixed):
    from ara.runtime.codex_cli import CodexCLIProvider, CodexCLIError
    config,auth,write,tmp=codex
    doc=json.loads(auth.read_text()) if mixed else {}
    doc['OPENAI_API_KEY']='offline-key'
    auth.write_text(json.dumps(doc))
    with pytest.raises(CodexCLIError,match='subscription_login_required'): CodexCLIProvider(config)


def test_auth_reread_retry_once(codex, monkeypatch):
    from ara.runtime.calls import Rejected
    import ara.runtime.codex_cli as module
    config,auth,write,tmp=codex
    config['codex_cli']['retries']=3
    log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    write('auth')
    original=module.subprocess.run
    invocations=[]
    def run(args, **kwargs):
        result=original(args,**kwargs)
        if 'exec' in args:
            invocations.append(1)
            doc=json.loads(auth.read_text());doc['tokens']['access_token']='replacement-access'
            replacement=auth.with_suffix('.new');replacement.write_text(json.dumps(doc));replacement.replace(auth)
            write(token='replacement-access')
        return result
    monkeypatch.setattr(module.subprocess,'run',run)
    assert calls.formalise(Proposition('p','P')).name=='P'
    assert len(invocations)==2
    assert len([e for e in log.read() if e['stage']=='auth_refresh_retry'])==1
    monkeypatch.setattr(module.subprocess,'run',original)
    write('auth',token='replacement-access')
    with pytest.raises(Rejected,match='cli_auth_error'): calls.formalise(Proposition('q','Q'))
    assert len([e for e in log.read() if e['stage']=='auth_refresh_retry'])==2


def test_schema_validation_is_authoritative(codex):
    from ara.runtime.calls import InvalidOutput
    config,auth,write,tmp=codex
    calls=make_calls(config,EventLog(tmp/'events.jsonl'),'P');write('bad_schema')
    with pytest.raises(InvalidOutput):calls.formalise(Proposition('p','P'))
    assert not list((tmp/'cache').rglob('*.json'))


def test_calibration_and_methodology(codex):
    from ara.runtime.export import methodology
    from ara.runtime.claude_estimation import TABLE_HASH
    config,auth,write,tmp=codex
    log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    calls.formalise(Proposition('p','P'))
    observations=[json.loads(e['payload_json']) for e in log.read() if e['stage']=='provider_estimate_observation']
    assert all(o['calibration_sha256']==TABLE_HASH for o in observations)
    assert all(o['comparison']=='first_turn_input_vs_initial_context' for o in observations)
    assert all(o['actual_input_tokens']==100 for o in observations)
    provider=calls.provider
    before=provider.calibration_state.factor(provider.model,'formalise')
    estimate=provider.estimate('formalise','P',{'type':'object'},10)
    from ara.types import TokenUsage
    raw={'usage':{'input_tokens':100000,'output_tokens':10},'cli':{'num_turns':1}}
    observation=provider.observe('formalise','P',{'type':'object'},estimate,raw)
    assert observation['factor_after']>before
    raw['usage']['input_tokens']=1
    after=provider.observe('formalise','P',{'type':'object'},estimate,raw)
    assert after['factor_after']==observation['factor_after']
    exported=methodology(log.path)
    assert 'codex_cli' in exported and 'different Codex tokenizer' in exported
    assert '0.163.0' in exported and '--ephemeral' in exported
    assert 'unavailable_calls' in exported


@pytest.mark.parametrize('mode', ['rate','usage'])
def test_limit_retries_bounded(codex,mode):
    from ara.runtime.calls import Rejected
    config,auth,write,tmp=codex
    config['codex_cli']['retries']=2
    log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P');write(mode)
    with pytest.raises(Rejected,match='cli_usage_limit'): calls.formalise(Proposition('p','P'))
    retries=[json.loads(e['payload_json']) for e in log.read() if e['stage']=='provider_retry']
    assert len(retries)==2 and all(r['delay_seconds']<=30 for r in retries)


def test_served_model_not_inferred(codex,monkeypatch):
    import ara.runtime.codex_cli as module
    config,auth,write,tmp=codex
    original=module.subprocess.run
    def run(*args,**kwargs):
        result=original(*args,**kwargs)
        result.stdout=result.stdout.replace(', "model": "gpt-5.4"','')
        return result
    monkeypatch.setattr(module.subprocess,'run',run)
    log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    calls.formalise(Proposition('p','P'))
    rows=[e for e in log.read() if e['label']=='MODEL']
    assert all(e['model_version']=='unverified' for e in rows)
    assert all(json.loads(e['payload_json'])['cli']['served_model'] is None for e in rows)


def test_isolation_canary_rejects_context(codex,monkeypatch):
    import ara.runtime.codex_cli as module
    from ara.runtime.calls import Rejected
    config,auth,write,tmp=codex
    original=module.subprocess.run
    def run(*args,**kwargs):
        result=original(*args,**kwargs)
        result.stdout=result.stdout.replace('\\"memory\\": \\"\\"', '\\"memory\\": \\"P\\"')
        return result
    monkeypatch.setattr(module.subprocess,'run',run)
    with pytest.raises(Rejected,match='isolation_context_present'):
        make_calls(config,EventLog(tmp/'events.jsonl'),'P')


def test_stage_model_pin(codex):
    config,auth,write,tmp=codex
    config['stages']={'formalise':{'model':'gpt-5.3-codex'}}
    log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    calls.formalise(Proposition('p','P'))
    rows=[e for e in log.read() if e['label']=='MODEL']
    assert rows[0]['model_id']=='gpt-5.4'
    assert rows[1]['model_id']==rows[1]['model_version']=='gpt-5.3-codex'


def test_extraction_and_web_refuse(codex):
    from ara.runtime.codex_cli import CodexCLIProvider
    from ara.runtime.claude_code import ClaudeCodeError
    config,auth,write,tmp=codex
    provider=CodexCLIProvider(config)
    for kind in ('extract_paper','search_evidence'):
        with pytest.raises(ClaudeCodeError,match='stage_requires_api_provider'):
            provider.estimate(kind,'P',{},10)


def test_nonfatal_warning_retains_only_count(codex):
    config,auth,write,tmp=codex
    log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P');write('warning')
    assert calls.formalise(Proposition('p','P')).name=='P'
    row=[e for e in log.read() if e['label']=='MODEL'][-1]
    assert json.loads(row['payload_json'])['cli']['warning_events']==1
    assert not any(item['type']=='error' for item in json.loads(row['response'])['content'])
