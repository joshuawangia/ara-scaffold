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
    helper = tmp_path/'codex-code-mode-host'
    helper.write_text('#!/usr/bin/env python3\nprint("P")\n')
    helper.chmod(0o700)
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
instruction_arg=next(a for a in args if a.startswith('model_instructions_file='))
assert 'Do not use tools' in Path(json.loads(instruction_arg.split('=',1)[1])).read_text()
assert 'features.goals=false' in args
assert 'skills.bundled.enabled=false' in args and 'skills.include_instructions=false' in args
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
if mode.startswith('web'):
 import subprocess
 assert subprocess.check_output(['/run/codex-code-mode-host'],text=True).strip()=='P'
 try: Path('/run/codex-code-mode-host').write_text('R')
 except OSError: pass
 else: raise AssertionError('tool host writable')
 assert 'web_search="live"' in args
 assert 'tools.web_search=true' in args
 assert 'web_search="disabled"' not in args
 assert 'features.shell_tool=false' in args and 'features.unified_exec=false' in args
 assert 'mcp_servers={}' in args
 value={'text':'P Q', 'sources':[{'url':'https://example.org/P','title':'P','snippets':['P Q']}]}
 if mode != 'web_no_event':
  for phase in ('started','updated','completed'):
   action={'type':'search','query':'P','queries':['P','Q']}
   if mode=='web_pending' and phase!='completed': action={'type':'other'}
   if mode=='web_other_completed': action={'type':'other'}
   emit({'type':'item.'+phase,'item':{'id':'web_1','type':'web_search','query':'P','action':action}})
 if mode=='web_commentary': emit({'type':'item.completed','item':{'id':'msg_1','type':'agent_message','text':'P'}})
 if mode=='web_bad_url': value['sources'][0]['url']='file://example.org/P'
 if mode=='web_bad_schema': value={'sources':[]}
 if mode=='web_unknown_action': emit({'type':'item.completed','item':{'id':'web_2','type':'web_search','action':{'type':'shell','command':'PRIVATE_CONTEXT_SENTINEL'}}})
 if mode.startswith('web_tool:'):
  emit({'type':'item.completed','item':{'type':mode.split(':',1)[1],'text':'PRIVATE_CONTEXT_SENTINEL'}})
if mode=='verify_web':
 assert 'web_search="disabled"' in args
 data=json.loads(prompt.split('INPUT_JSON'+chr(10),1)[1])
 assert data['evidence']['urls']==['https://example.org/P']
 assert any(b.get('citations') for b in data['evidence']['content'])
 value={'originality':{'assessment':'possible_overlap','evidence_urls':['https://example.org/P'],'detail':'P'},
        'items':[{**i,'status':'verified','action':'retain','detail':'P','evidence_urls':['https://example.org/P'],'source_excerpt':'P Q'} for i in data['items']]}
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
if mode=='wire_optional': value={'formula':{'op':'atom','name':'P','args':None,'terms':None,'variable':None}}
if mode=='bad_schema': value={'bad':'P'}
if mode in ('preflight','local_invalid'):
 value=json.loads(prompt.split('placeholder JSON, without using tools:'+chr(10),1)[1])
 assert set(schema['required'])==set(schema['properties'])
 assert schema['additionalProperties'] is False
 assert 'uniqueItems' not in json.dumps(schema)
 if mode=='local_invalid': value['roots']=['P','P']
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


def test_extraction_refuses_but_web_estimates(codex):
    from ara.runtime.codex_cli import CodexCLIProvider
    from ara.runtime.claude_code import ClaudeCodeError
    config,auth,write,tmp=codex
    provider=CodexCLIProvider(config)
    for kind in ('extract_paper',):
        with pytest.raises(ClaudeCodeError,match='stage_requires_api_provider'):
            provider.estimate(kind,'P',{},10)
    assert provider.estimate('search_evidence','P',None,10).input_tokens > 0


def test_nonfatal_warning_retains_only_count(codex):
    config,auth,write,tmp=codex
    log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P');write('warning')
    assert calls.formalise(Proposition('p','P')).name=='P'
    row=[e for e in log.read() if e['label']=='MODEL'][-1]
    assert json.loads(row['payload_json'])['cli']['warning_events']==1
    assert not any(item['type']=='error' for item in json.loads(row['response'])['content'])


def test_auth_source_required_without_worker_home_fallback(codex, monkeypatch):
    from ara.runtime.codex_cli import CodexCLIProvider, CodexCLIError
    config, auth, write, tmp = codex
    monkeypatch.setenv('CODEX_HOME', str(auth.parent))
    del config['codex_cli']['auth_file']
    with pytest.raises(CodexCLIError, match='subscription_auth_file_required'):
        CodexCLIProvider(config)


def test_configured_auth_does_not_open_worker_login(codex, monkeypatch):
    from ara.runtime.codex_cli import CodexCLIProvider
    config, auth, write, tmp = codex
    selected = tmp/'subscription/auth.json'
    selected.parent.mkdir()
    selected.write_bytes(auth.read_bytes())
    config['codex_cli']['auth_file'] = str(selected)
    monkeypatch.setenv('CODEX_HOME', str(auth.parent))
    original = Path.open
    def guarded(path, *args, **kwargs):
        assert path != auth, 'worker credential file must not be opened'
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded)
    provider = CodexCLIProvider(config)
    assert provider._credential_source == selected
    selected.unlink()
    from ara.runtime.codex_cli import CodexCLIError
    with pytest.raises(CodexCLIError, match='subscription_login_required'):
        provider._authentication()


def test_generic_visible_tools_disclosed_but_events_rejected(codex, monkeypatch):
    import ara.runtime.codex_cli as module
    from ara.runtime.calls import Rejected
    from ara.runtime.export import methodology
    config, auth, write, tmp = codex
    config['model'] = 'gpt-6-luna'
    original = module.subprocess.run
    def visible_tools(*args, **kwargs):
        result = original(*args, **kwargs)
        result.stdout = result.stdout.replace('\\"tools\\": \\"\\"',
            '\\"tools\\": \\"functions.apply_patch, functions.spawn_agent, functions.read_mcp_resource\\"')
        return result
    monkeypatch.setattr(module.subprocess, 'run', visible_tools)
    log = EventLog(tmp/'events.jsonl')
    calls = make_calls(config, log, 'P')
    canary = next(json.loads(e['payload_json']) for e in log.read() if e['label']=='MODEL')
    expected = ['functions.apply_patch', 'functions.read_mcp_resource', 'functions.spawn_agent']
    assert canary['cli']['visible_tool_names'] == expected
    assert canary['isolation']['visible_tool_names'] == expected
    assert canary['isolation']['tool_event_rejection'] == 'active'
    exported = methodology(log.path)
    assert all(name in exported for name in expected)
    assert 'visible definitions do not authorize use' in exported
    assert calls.formalise(Proposition('p', 'P')).name == 'P'
    write('tool:command_execution')
    with pytest.raises(Rejected, match='cli_tool_event'):
        calls.formalise(Proposition('q', 'Q'))


@pytest.mark.parametrize('field,text,code', [
    ('skills','P','isolation_context_present'), ('memory','P','isolation_context_present'),
    ('agents_md','P','isolation_context_present'), ('claude_md','P','isolation_context_present'),
    ('tools','private-project','isolation_forbidden_content'),
    ('tools','sentinel@example.invalid','operator_identity_in_output'),
])
def test_visible_tools_never_waive_operator_scans(codex, monkeypatch, field, text, code):
    import ara.runtime.codex_cli as module
    from ara.runtime.calls import Rejected
    config, auth, write, tmp = codex
    config['codex_cli']['forbidden_terms'] = ['private-project']
    original = module.subprocess.run
    def contaminated(*args, **kwargs):
        result = original(*args, **kwargs)
        result.stdout = result.stdout.replace('\\"'+field+'\\": \\"\\"',
                                             '\\"'+field+'\\": \\"'+text+'\\"')
        return result
    monkeypatch.setattr(module.subprocess, 'run', contaminated)
    with pytest.raises(Rejected, match=code):
        make_calls(config, EventLog(tmp/'events.jsonl'), 'P')


def test_strict_wire_preflight_and_local_authority(codex):
    from ara.runtime.calls import InvalidOutput
    from ara.runtime.codex_schema import VERSION
    config, auth, write, tmp = codex
    write('preflight');log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    value=calls._call_once('select_t_roots',{},schema_smoke=True)
    assert value['roots']==[]
    wire=calls._call_once('formalise',{},schema_smoke=True)
    assert wire['formula']['name']=='P' and 'args' not in wire['formula']
    # The raw wire retains added nulls while the returned native value omits them.
    raw=json.loads([e for e in log.read() if e['label']=='MODEL'][-1]['response'])
    assert json.loads(raw['content'][0]['text'])['formula']['args'] is None
    rows=[json.loads(e['payload_json']) for e in log.read() if e['label']=='MODEL']
    assert all(r['cli']['schema_transform']==VERSION for r in rows)
    assert rows[-1]['cli']['wire_schema_hash']!=rows[-1]['cli']['native_schema_hash']
    before=calls.budget.used_tokens
    write('local_invalid')
    with pytest.raises(InvalidOutput):calls._call_once('select_t_roots',{},schema_smoke=True)
    assert calls.budget.used_tokens>before
    assert not list((tmp/'cache').rglob('*.json'))


def test_codex_preflight_gate_complete_and_stale(codex):
    from ara.runtime.codex_preflight import codex_schema_preflight, require_codex_preflight
    config, auth, write, tmp = codex
    write('preflight');log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    with pytest.raises(ValueError,match='requires a successful'):require_codex_preflight(config,ROOT)
    result=codex_schema_preflight(calls)
    assert result['passed'] and result['accepted']==result['total']==18
    assert 'outline_essay' in {case['case'] for case in result['manifest']['cases']}
    assert 'revise_essay' in {case['case'] for case in result['manifest']['cases']}
    config['codex_cli']['schema_preflight_log']=str(log.path)
    require_codex_preflight(config,ROOT)
    config['stages']={'construction_correction':{'effort':'low'}}
    # Correction settings must be independently pinned.
    assert config['effort']!='low'
    with pytest.raises(ValueError,match='stale'):require_codex_preflight(config,ROOT)
    config['stages']={};config['model']='gpt-6-luna'
    with pytest.raises(ValueError,match='stale'):require_codex_preflight(config,ROOT)


@pytest.mark.parametrize('damage',['missing_receipt','cached','wrong_wire','missing_case','chain'])
def test_codex_preflight_gate_rejects_incomplete_receipts(codex,damage):
    from ara.runtime.codex_preflight import codex_schema_preflight, require_codex_preflight
    from ara.types import RunEvent
    config, auth, write, tmp = codex
    write('preflight');log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    assert codex_schema_preflight(calls)['passed']
    damaged=EventLog(tmp/'damaged/events.jsonl')
    for event in log.read():
        payload=json.loads(event['payload_json'])
        if event['stage']=='select_t_roots' and event['label']=='MODEL':
            if damage=='missing_receipt':continue
            if damage=='cached':payload['cache_hit']=True
            if damage=='wrong_wire':payload['cli']['wire_schema_hash']='P'
        if damage=='missing_case' and event['stage']=='codex_schema_preflight_accepted' and payload['case']=='select_t_roots':continue
        damaged.emit(RunEvent.from_dict({**event,'payload_json':json.dumps(payload)}))
    if damage=='chain':damaged.path.write_text(damaged.path.read_text().replace('gpt-5.4','gpt-6-luna'))
    config['codex_cli']['schema_preflight_log']=str(damaged.path)
    with pytest.raises(ValueError):require_codex_preflight(config,ROOT)


def test_codex_preflight_failure_tests_every_case(codex):
    from ara.runtime.codex_preflight import codex_schema_preflight, require_codex_preflight
    config, auth, write, tmp = codex
    write('bad_schema');log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    result=codex_schema_preflight(calls)
    assert not result['passed'] and result['accepted']==0 and result['total']==18
    assert sum(e['stage']=='codex_schema_preflight_failed' for e in log.read())==18
    config['codex_cli']['schema_preflight_log']=str(log.path)
    with pytest.raises(ValueError):require_codex_preflight(config,ROOT)


def test_codex_pilot_requires_preflight_before_provider(codex):
    from ara.runtime.cli import main
    config, auth, write, tmp=codex
    path=tmp/'config.yaml';path.write_text(yaml.safe_dump(config))
    def forbidden(*args):pytest.fail('provider constructed before schema gate')
    assert main(['run','--config',str(path),'--topic','P','--literature',str(ROOT/'tests/fixtures/runtime/smoke-literature.txt'),
                 '--run-dir',str(tmp/'pilot')],calls_factory=forbidden)==2


def test_codex_cache_replays_normalized_wire(codex):
    config, auth, write, tmp=codex
    write('wire_optional');log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    first=calls.formalise(Proposition('p','P'))
    tokens=calls.budget.used_tokens
    assert calls.formalise(Proposition('p','P'))==first
    assert calls.budget.used_tokens==tokens
    rows=[json.loads(e['payload_json']) for e in log.read() if e['label']=='MODEL']
    assert rows[-1]['cache_hit'] is True and rows[-1]['status']=='accepted'


def test_codex_resume_can_supply_new_proof_without_editing_history(codex):
    from ara.runtime.cli import main
    from ara.runtime.codex_preflight import codex_schema_preflight
    from ara.bank import load_bank
    config, auth, write, tmp=codex
    write('preflight');proof=EventLog(tmp/'proof/events.jsonl')
    assert codex_schema_preflight(make_calls(config,proof,'P'))['passed']
    history=EventLog(tmp/'pilot/events.jsonl')
    history.record('run_started',config=config,topic='P',bank_version=load_bank(ROOT/'bank').bank_version)
    reached=[]
    def factory(resolved,*args):
        reached.append(resolved['codex_cli']['schema_preflight_log'])
        raise ValueError('P')  # Stop after observing admission, before pilot calls.
    args=['resume-construction','--run-dir',str(history.path.parent),'--unknown-usage-policy','count-at-reservation']
    assert main(args,calls_factory=factory)==2 and reached==[]
    assert main([*args,'--codex-schema-preflight-log',str(proof.path)],calls_factory=factory)==2
    assert reached==[str(proof.path)]
    stored=json.loads(history.read()[0]['payload_json'])['config']
    assert stored['codex_cli'].get('schema_preflight_log') is None


@pytest.mark.parametrize('mode', ['web', 'web_commentary', 'web_pending'])
def test_web_search_evidence_receipt_and_methodology(codex, mode):
    from ara.runtime.export import methodology
    config, auth, write, tmp = codex
    log = EventLog(tmp/'events.jsonl'); calls = make_calls(config, log, 'P')
    calls.config['token_cap'] = 3000000
    write(mode)
    evidence = calls.search_evidence({}, [])
    assert evidence['urls'] == ['https://example.org/P']
    assert 'P Q' in evidence['text']
    excerpts = [c for b in evidence['content'] for c in b.get('citations', [])]
    assert excerpts == [{'type':'web_search_result_location', 'url':'https://example.org/P', 'cited_text':'P Q'}]
    rows = [json.loads(e['payload_json']) for e in log.read() if e['label']=='MODEL']
    assert rows[0]['isolation']['status'] == 'proven'
    web = rows[-1]['cli']['web_search']
    assert web['queries'] == ['P', 'Q']
    assert web['result_urls'] == evidence['urls']
    assert len(web['events']) == 1
    assert web['source_provenance'] == 'model-reported from Codex web search; not raw tool results'
    report = methodology(log.path)
    summary = json.loads(report.split('```json\n', 1)[1].split('\n```', 1)[0])
    assert summary['provider_methodology']['evidence_retrieval'][0]['method'] == 'Codex web search'
    assert 'https://example.org/P' in report
    assert 'web_search="disabled"' in rows[0]['isolation_flags']
    assert 'web_search="live"' in rows[-1]['isolation_flags']
    before = calls.budget.used_tokens
    assert calls.search_evidence({}, []) == evidence
    assert calls.budget.used_tokens == before


@pytest.mark.parametrize('mode,code', [
    *[('web_tool:'+t, 'cli_tool_event') for t in ('command_execution','file_read','file_change','mcp_tool_call','tool_call','function_call')],
    ('web_no_event','cli_web_search_missing'), ('web_bad_url','cli_invalid_web_evidence'),
    ('web_bad_schema','cli_invalid_web_evidence'), ('web_unknown_action','cli_tool_event'),
    ('web_other_completed','cli_tool_event'),
])
def test_web_search_fails_closed(codex, mode, code):
    from ara.runtime.calls import Rejected
    config, auth, write, tmp = codex
    log = EventLog(tmp/'events.jsonl'); calls = make_calls(config, log, 'P')
    calls.config['token_cap'] = 3000000
    write(mode)
    with pytest.raises(Rejected, match=code): calls.search_evidence({}, [])
    assert 'PRIVATE_CONTEXT_SENTINEL' not in log.path.read_text()
    assert not list((tmp/'cache').rglob('*.json'))


@pytest.mark.parametrize('quote,retained', [('P Q', True), ('P S', False)])
def test_web_evidence_reaches_native_verifier(codex, quote, retained):
    config, auth, write, tmp = codex
    config['token_cap'] = 3000000
    calls = make_calls(config, EventLog(tmp/'events.jsonl'), 'P')
    draft = {'title':'P', 'body':'"'+quote+'"', 'bibliography':[]}
    write('web')
    # Cache the real transport response, then run the native search/classification path.
    calls.search_evidence(draft, calls.verification_items(draft))
    write('verify_web')
    cleaned, result = calls.verify_originality_citations(draft)
    assert (quote in cleaned['body']) is retained
    assert result['items'][0]['status'] == ('verified' if retained else 'unverified')
    assert result['originality']['assessment'] == 'possible_overlap'


def test_web_admission_separates_initial_context_from_replay(codex):
    config, auth, write, tmp = codex
    calls = make_calls(config, EventLog(tmp/'events.jsonl'), 'P')
    count = calls.count_request('search_evidence', {'draft':{},'items':[]}, maximum=32, admission=True)
    assert count.initial_input_tokens < 10000
    assert count.reservation.server_tool_uses == config['web_search_max_uses']
    assert count.reservation.input_tokens == count.initial_input_tokens * 2 + 32 + config['model_context_token_bound'] * config['web_search_max_uses']


def test_web_requires_packaged_tool_host(codex):
    from ara.runtime.calls import Rejected
    config, auth, write, tmp = codex
    calls = make_calls(config, EventLog(tmp/'events.jsonl'), 'P')
    calls.config['token_cap'] = 3000000
    (tmp/'codex-code-mode-host').unlink()
    write('web')
    with pytest.raises(Rejected, match='cli_web_helper_unavailable'):
        calls.search_evidence({}, [])
