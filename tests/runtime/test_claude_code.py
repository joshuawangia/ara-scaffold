"""Exercise the real subprocess boundary with a disposable offline executable."""
import json
import os
from pathlib import Path

import pytest
import yaml

from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.logging import EventLog
from ara.runtime.budget import BudgetStop
from ara.types import Proposition
from test_calls import rig, register

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def cli(tmp_path, monkeypatch):
    from ara.runtime.claude_code import ClaudeCodeProvider
    home = tmp_path / 'home'
    home.mkdir()
    (home / '.gitconfig').write_text('[user]\nname = Operator Sentinel\nemail = sentinel@example.invalid\n')
    (home / '.claude/skills/private-skill').mkdir(parents=True)
    monkeypatch.setenv('HOME', str(home))
    monkeypatch.setenv('GIT_CONFIG_GLOBAL', str(home / '.gitconfig'))
    monkeypatch.setenv('GIT_CONFIG_NOSYSTEM', '1')
    monkeypatch.setenv('CLAUDE_CODE_OAUTH_TOKEN', 'offline-token')
    credentials = home/'.claude/.credentials.json'
    credentials.write_text(json.dumps({'claudeAiOauth': {'accessToken': 'offline-token',
        'refreshToken': 'offline-refresh-token', 'expiresAt': 4102444800000,
        'scopes': ['user:profile', 'user:inference', 'user:mcp_servers']}, 'mcpOAuth': {'P': {'accessToken': 'offline-mcp'}}}))
    credentials.chmod(0o600)
    binary = tmp_path / 'claude'
    binary.write_text('''#!/usr/bin/env python3
import json, os, sys, uuid, time
from pathlib import Path
args=sys.argv[1:]
if args == ['--version']:
 print('2.1.306 (Claude Code)'); sys.exit()
def arg(k): return args[args.index(k)+1]
assert '--safe-mode' in args and '--disable-slash-commands' in args
assert '--strict-mcp-config' in args and json.loads(arg('--mcp-config')) == {'mcpServers':{}}
assert arg('--tools') == '' and arg('--setting-sources') == ''
assert '--no-session-persistence' in args and '--exclude-dynamic-system-prompt-sections' in args
assert json.loads(arg('--settings'))['disableAllHooks'] is True
assert not list(Path.cwd().iterdir())
assert Path(os.environ['CLAUDE_CONFIG_DIR']) != Path.home()/'.claude'
assert not any(k.startswith('ANTHROPIC_') for k in os.environ)
auth_path=Path(os.environ['CLAUDE_CONFIG_DIR'])/'.credentials.json'
if auth_path.exists():
 assert 'CLAUDE_CODE_OAUTH_TOKEN' not in os.environ
 assert auth_path.stat().st_mode & 0o777 == 0o600
 auth=json.loads(auth_path.read_text())
 assert set(auth)=={'claudeAiOauth'} and 'refreshToken' not in auth['claudeAiOauth']
 assert auth['claudeAiOauth']['scopes']==['user:inference']
 token=auth['claudeAiOauth']['accessToken']
else:
 token=os.environ['CLAUDE_CODE_OAUTH_TOKEN']
prompt=sys.stdin.read()
config=Path(__file__).with_suffix('.json')
mode=json.loads(config.read_text())['mode']
canary='ARA_ISOLATION_CANARY' in prompt
trace=Path(__file__).with_suffix('.trace')
with trace.open('a') as f: f.write(json.dumps({'args':args,'prompt':prompt,'cwd':str(Path.cwd()),'event':'start','time':time.monotonic(),'config_dir':os.environ['CLAUDE_CONFIG_DIR']})+'\\n')
if not canary and mode=='timeout': time.sleep(5)
if not canary and mode=='slow': time.sleep(.3)
if not canary and mode=='invalid_json': print('SECRET PROMPT ECHO'); sys.exit(0)
if not canary and mode=='exit': print('SECRET PROMPT ECHO',file=sys.stderr); sys.exit(7)
if not canary and mode in ('plain_rate','plain_stdout_rate'): print('rate limit SECRET PROMPT ECHO',file=sys.stdout if mode=='plain_stdout_rate' else sys.stderr); sys.exit(1)
schema=json.loads(arg('--json-schema'))
assert '$schema' not in schema
if canary:
 value={k:[] if v['type']=='array' else '' for k,v in schema['properties'].items()}
 value.update(system_prompt=arg('--system-prompt'),tools='StructuredOutput',other_context='Anthropic runtime defaults')
 debug='Skipping skill dir discovery\\nproject memory is off\\nSafe mode: installed plugins are disabled\\n[claudeai-mcp] Disabled in safe mode\\n'
 if mode=='bad_canary': value['agents_md']='P'
 if mode=='tools_present': value['tools']='StructuredOutput, Bash'
 if mode=='forbidden_context': value['other_context']='private-project'
 if mode=='memory_present': value['memory']='P'
 if mode=='forbidden_debug': debug+='private-skill'
 if mode=='missing_debug': debug=''
 Path(arg('--debug-file')).write_text(debug)
else:
 value={'formula':{'op':'atom','name':'P'}}
 if mode=='identity': value['formula']['name']='sentinel@example.invalid'
 if mode=='identity_encoded': value['formula']['name']='sentinel@example.invalid'
 if mode=='identity_name': value['formula']['name']='Operator Sentinel'
 if mode=='bad_schema': value={'unknown':'P'}
 if mode=='secret_encoded': value['formula']['name']=token
 if mode.startswith('construction_correction_'): value={'roots':[],'relevance':'P','omissions':[]}
usage={'input_tokens':10,'output_tokens':5,'cache_read_input_tokens':2,'cache_creation_input_tokens':3}
result={'type':'result','subtype':'success','is_error':False,'stop_reason':'tool_use','terminal_reason':'completed',
 'num_turns':1,'session_id':arg('--session-id'),'usage':usage,'modelUsage':{arg('--model'):{'inputTokens':10,'outputTokens':5}},
 'total_cost_usd':0.125,'structured_output':value,'result':json.dumps(value)}
if not canary and mode=='wrong_model': result['modelUsage']={'claude-opus-4-8':{}}
if not canary and mode=='missing_output': result.pop('structured_output')
if not canary and mode=='bad_usage': result['usage']['input_tokens']=-1
if not canary and mode=='missing_usage': result.pop('usage')
if not canary and mode=='refusal': result['stop_reason']='refusal'
correction_limit=mode.startswith('construction_correction_') and '"mode":"targeted_correction"' in prompt
if not canary and (mode in ('rate','usage') or correction_limit):
 result.update(subtype='error_during_execution',is_error=True,api_error_status=429,
               result='usage limit SECRET PROMPT ECHO' if mode.endswith('usage') else 'rate limit SECRET PROMPT ECHO')
 print(json.dumps(result)); sys.exit(1)
if not canary and mode=='slow':
 with trace.open('a') as f: f.write(json.dumps({'event':'end','time':time.monotonic()})+'\\n')
encoded=json.dumps(result)
if mode=='identity_encoded': encoded=encoded.replace('@','\\\\u0040')
if mode=='secret_encoded': encoded=encoded.replace(token, ''.join('\\\\u%04x'%ord(c) for c in token))
print(encoded)
''')
    binary.chmod(0o755)
    mode = binary.with_suffix('.json')
    mode.write_text(json.dumps({'mode':'ok'}))
    config = yaml.safe_load((ROOT/'config.yaml').read_text())
    config.update(provider='claude_code', model='claude-opus-5-5', token_cap=1000000,
                  cost_cap_usd=0, validation_attempts=1,
                  claude_code={'binary':str(binary),'timeout_seconds':1,'retry_backoff_seconds':0,
                               'forbidden_terms':['private-project']})
    def make():
        provider=ClaudeCodeProvider(config)
        log=EventLog(tmp_path/'run/events.jsonl')
        return ModelCalls(config,provider,log,Cache(tmp_path/'cache'),ROOT,'P'),log
    def set_mode(value): mode.write_text(json.dumps({'mode':value}))
    return make,set_mode,config,binary


def model_events(log):
    return [e for e in log.read() if e['label']=='MODEL']


def test_native_preflight_receipts_schema_cache_and_export(cli):
    from ara.runtime.export import methodology
    make,_,config,binary=cli
    calls,log=make()
    assert len(model_events(log))==1
    value=calls.formalise(Proposition('p','P'))
    assert value.name=='P'
    event=model_events(log)[-1]
    payload=json.loads(event['payload_json'])
    assert event['usage']['input_tokens']==10 and event['usage']['cache_write_tokens']==3
    assert event['cost_usd']==0 and payload['provider']=='claude_code'
    assert payload['subscription_usage']['cost_equivalent_usd']==.125
    assert payload['cli']['exit_status']==0 and payload['cli']['session_id']
    assert payload['cli']['version']=='2.1.306 (Claude Code)'
    assert event['model_id']==event['model_version']=='claude-opus-5-5'
    calls.formalise(Proposition('p','P'))
    assert len(binary.with_suffix('.trace').read_text().splitlines())==2
    assert json.loads(model_events(log)[-1]['payload_json'])['cache_hit']
    doc=methodology(log.path)
    assert 'subscription_usage' in doc and 'claude_code' in doc and 'byte-identical' in doc
    make()  # Every new run context preflights, even with the same cache/log.
    assert len(binary.with_suffix('.trace').read_text().splitlines())==3


@pytest.mark.parametrize('mode',['bad_canary','forbidden_debug','forbidden_context','memory_present','tools_present','missing_debug'])
def test_preflight_fails_closed(cli,mode):
    make,set_mode,_,binary=cli
    set_mode(mode)
    with pytest.raises((BudgetStop,Rejected)): make()
    assert len(binary.with_suffix('.trace').read_text().splitlines())==1


@pytest.mark.parametrize('mode',['identity','identity_encoded','identity_name','invalid_json','exit','timeout',
                                 'wrong_model','missing_output','bad_usage','missing_usage','refusal'])
def test_provider_errors_never_echo_output(cli,mode):
    make,set_mode,_,_=cli
    calls,log=make()
    set_mode(mode)
    with pytest.raises((BudgetStop,Rejected)): calls.formalise(Proposition('p','P'))
    text=log.path.read_text()
    assert 'SECRET PROMPT ECHO' not in text and 'sentinel@example.invalid' not in text
    assert 'Operator Sentinel' not in text
    assert any(e['stage']=='provider_error' for e in log.read())
    assert not list(calls.cache.path.glob('*.json'))


@pytest.mark.parametrize('mode',['rate','usage','plain_rate','plain_stdout_rate'])
def test_bounded_logged_retry(cli,mode):
    make,set_mode,_,binary=cli
    calls,log=make()
    set_mode(mode)
    with pytest.raises((BudgetStop,Rejected)): calls.formalise(Proposition('p','P'))
    assert len(binary.with_suffix('.trace').read_text().splitlines())==4
    assert sum(e['stage']=='provider_retry' for e in log.read())==2
    assert len(model_events(log))==4
    if mode not in ('plain_rate','plain_stdout_rate'):
        assert calls.budget.used_tokens==80
    else:
        assert calls.budget.used_tokens>80
        assert json.loads(model_events(log)[-1]['payload_json'])['accounting']=='reservation_unknown_actual'
    assert 'SECRET PROMPT ECHO' not in log.path.read_text()


def test_local_validation_remains_authoritative(cli):
    make,set_mode,_,_=cli
    calls,log=make()
    set_mode('bad_schema')
    with pytest.raises(Rejected): calls.formalise(Proposition('p','P'))
    assert json.loads(model_events(log)[-1]['payload_json'])['status']=='rejected'
    assert not list(calls.cache.path.glob('*.json'))


def test_context_and_token_caps_refuse_without_stage_dispatch(cli):
    make,_,config,binary=cli
    calls,log=make()
    config['token_cap']=calls.budget.used_tokens
    with pytest.raises(BudgetStop): calls.formalise(Proposition('p','P'))
    assert len(binary.with_suffix('.trace').read_text().splitlines())==1
    config['token_cap']=1000000
    config['model_context_token_bound']=1
    with pytest.raises(BudgetStop): calls.formalise(Proposition('p','Q'))
    assert len(binary.with_suffix('.trace').read_text().splitlines())==1


def test_stage_model_system_and_input_are_preserved(cli):
    make,_,config,binary=cli
    config['stages']['formalise']={'model':'claude-opus-4-8','system_prompt':'P'}
    calls,log=make()
    calls.formalise(Proposition('p','P'))
    sent=json.loads(binary.with_suffix('.trace').read_text().splitlines()[-1])
    assert sent['prompt']==calls.render('formalise',{'proposition':Proposition('p','P').to_dict()})[1]
    args=sent['args']
    assert args[args.index('--system-prompt')+1]=='P'
    assert model_events(log)[-1]['model_version']=='claude-opus-4-8'
    assert json.loads(args[args.index('--json-schema')+1])=={
        k:v for k,v in calls.response_schema('formalise',{}).items() if k!='$schema'}


@pytest.mark.parametrize('limit',[2,4])
def test_configurable_concurrency_and_fresh_sessions(cli,limit):
    from concurrent.futures import ThreadPoolExecutor
    make,set_mode,config,binary=cli
    if limit==2: config['claude_code']['concurrency']=limit
    calls,log=make()
    set_mode('slow')
    with ThreadPoolExecutor(max_workers=8) as pool:
        results=list(pool.map(lambda i:calls.formalise(Proposition(str(i),'P')),range(8)))
    assert len(results)==8
    active=peak=0
    starts=[]
    for e in [json.loads(row) for row in binary.with_suffix('.trace').read_text().splitlines()][1:]:
        if e['event']=='start': active+=1; starts.append(e)
        else: active-=1
        peak=max(peak,active)
    assert peak==limit and active==0
    assert len({s['cwd'] for s in starts})==8
    events=model_events(log)
    assert len({json.loads(e['payload_json'])['cli']['session_id'] for e in events})==9
    assert calls.budget.used_tokens==180 and calls.budget._pending_tokens==0


def test_concurrent_budget_admission_cannot_oversubscribe(cli):
    from concurrent.futures import ThreadPoolExecutor
    make,set_mode,config,binary=cli
    calls,log=make()
    set_mode('slow')
    estimate=calls.count_request('formalise',{'proposition':Proposition('p','P').to_dict()})
    config['token_cap']=calls.budget.used_tokens+sum(estimate.reservation.to_dict().values())
    def invoke(i):
        try: calls.formalise(Proposition(str(i),'P')); return True
        except BudgetStop: return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(invoke,range(2)))
    assert sorted(results)==[False,True]
    assert calls.budget._pending_tokens==0


def test_unpaid_planning_uses_local_subscription_estimate(cli):
    from ara.runtime.planning import CountingProvider
    _,_,config,binary=cli
    provider=CountingProvider(config,'provider')
    assert 'p99*1.05' in provider.estimate_method
    assert provider.estimate('formalise','P',{},32).input_tokens>len('P')
    assert not binary.with_suffix('.trace').exists()
    with pytest.raises(RuntimeError,match='planning forbids'): provider.complete('P')


def test_no_tool_retrieval_or_extraction_fallback(cli):
    make,_,_,binary=cli
    calls,log=make()
    with pytest.raises(Rejected,match='stage_requires_api_provider'):
        calls.call('search_evidence',{'draft':{},'items':[]})
    assert len(binary.with_suffix('.trace').read_text().splitlines())==1


def test_second_turn_replay_is_reserved(cli):
    from ara.runtime.claude_code import ClaudeCodeProvider
    from ara.runtime.cache import canonical
    _,_,config,_=cli
    provider=ClaudeCodeProvider(config)
    schema={'type':'object'}
    estimate=provider.estimate('formalise','P',schema,100)
    import math
    from ara.runtime.claude_estimation import TABLE
    size=math.ceil(len(('P'+canonical(schema)).encode())*TABLE['fallback_factor'])+TABLE['runtime_overhead_tokens']
    assert estimate.input_tokens>=2*size+100
    assert estimate.output_tokens==200
    assert provider.initial_context_tokens(estimate)==size
    assert provider.context_output_tokens(100)==200


def test_ancestor_instructions_refuse_before_process(cli,tmp_path,monkeypatch):
    import tempfile
    from contextlib import contextmanager
    make,_,_,binary=cli
    base=tmp_path/'isolated'
    base.mkdir()
    (tmp_path/'AGENTS.md').write_text('P')
    @contextmanager
    def directory(**kwargs): yield str(base)
    monkeypatch.setattr(tempfile,'TemporaryDirectory',directory)
    with pytest.raises(Rejected,match='isolation_ancestor_instructions'): make()
    assert not binary.with_suffix('.trace').exists()


def test_existing_provider_cache_identity_is_unchanged(tmp_path):
    from ara.runtime.providers import MockProvider
    config=yaml.safe_load((ROOT/'config.yaml').read_text())
    provider=MockProvider({})
    log=EventLog(tmp_path/'events.jsonl')
    cache=Cache(tmp_path/'cache')
    # Legacy 0e0a7fc cache key for the ordinary placeholder formalise request.
    cache.put('8b2f7488b279c12f31d3eb3bea14de323956c67221fde5271e130337a9ef94e0',{
        'raw':{'model':'claude-opus-5','stop_reason':'end_turn',
               'usage':{'input_tokens':5,'output_tokens':3},
               'content':[{'type':'text','text':'{"formula":{"op":"atom","name":"P"}}'}]}})
    calls=ModelCalls(config,provider,log,cache,ROOT,'P')
    assert calls.formalise(Proposition('p','P')).name=='P'
    assert provider.calls==0
    assert json.loads(model_events(log)[-1]['payload_json'])['cache_hit']


def test_configured_system_prompt_partitions_existing_cache(rig):
    calls,provider,log=rig
    p=Proposition('p','P')
    calls.config['system_prompt']='P'
    register(calls,provider,'formalise',{'proposition':p.to_dict()},{'formula':{'op':'atom','name':'P'}})
    assert calls.formalise(p).name=='P'
    calls.config['system_prompt']='Q'
    register(calls,provider,'formalise',{'proposition':p.to_dict()},{'formula':{'op':'atom','name':'Q'}})
    assert calls.formalise(p).name=='Q'
    assert provider.calls==2


def test_concurrent_stop_artifacts_are_serialized(rig,monkeypatch):
    import threading
    import time
    from concurrent.futures import ThreadPoolExecutor
    calls,_,_=rig
    write=Path.write_text
    active=peak=0
    def slow_write(path,*args,**kwargs):
        nonlocal active,peak
        if path.name!='partial.json': return write(path,*args,**kwargs)
        active+=1
        peak=max(peak,active)
        time.sleep(.05)
        result=write(path,*args,**kwargs)
        active-=1
        return result
    monkeypatch.setattr(Path,'write_text',slow_write)
    barrier=threading.Barrier(2)
    def stop(i):
        barrier.wait()
        with pytest.raises(BudgetStop): calls.budget.stop('P'*i,'formalise')
    with ThreadPoolExecutor(max_workers=2) as pool: list(pool.map(stop,[1,100]))
    assert peak==1
    assert json.loads((calls.log.path.parent/'partial.json').read_text())['status']=='STOPPED'


def test_json_escaped_credential_rejected_before_retention(cli):
    make,set_mode,_,_=cli
    calls,log=make()
    set_mode('secret_encoded')
    with pytest.raises(Rejected,match='credential_in_cli_output'):
        calls.formalise(Proposition('p','P'))
    for path in (*log.path.parent.rglob('*'),*calls.cache.path.rglob('*')):
        if path.is_file(): assert 'offline-token' not in path.read_text()
    event=model_events(log)[-1]
    assert event['usage']['input_tokens']==10
    assert json.loads(event['payload_json'])['accounting']=='actual'
    assert not list(calls.cache.path.glob('*.json'))


def test_cached_credential_rejected_without_logging_and_evicted(cli):
    make,_,_,_=cli
    calls,log=make()
    calls.formalise(Proposition('p','P'))
    path=next(calls.cache.path.glob('*.json'))
    saved=json.loads(path.read_text())
    saved['raw']['content'][0]['text']=json.dumps({'formula':{'op':'atom','name':'offline-token'}})
    path.write_text(json.dumps(saved))
    with pytest.raises(Rejected,match='credential_in_cli_output'):
        calls.formalise(Proposition('p','P'))
    assert 'offline-token' not in log.path.read_text()
    assert not path.exists()


@pytest.mark.parametrize('kind',['select_t_roots','build_t_batch'])
@pytest.mark.parametrize('corrections',[None,0,1])
@pytest.mark.parametrize('mode',['rate','usage'])
def test_native_construction_transport_retries(cli,kind,corrections,mode):
    from ara.runtime.construction import construction_call
    make,set_mode,_,binary=cli
    calls,log=make()
    set_mode(mode)
    remaining={kind:corrections}
    with pytest.raises(Rejected,match='cli_usage_limit'):
        construction_call(calls,kind,{'papers':[]},None,remaining)
    assert remaining[kind]==corrections
    assert len(binary.with_suffix('.trace').read_text().splitlines())==4
    assert sum(e['stage']=='provider_retry' for e in log.read())==2
    assert not any(e['stage']=='construction_targeted_correction' for e in log.read())


@pytest.mark.parametrize('mode',['rate','usage'])
def test_targeted_construction_retry_does_not_spend_more_corrections(cli,mode):
    from ara.runtime.construction import construction_call
    make,set_mode,_,binary=cli
    calls,log=make()
    set_mode('construction_correction_'+mode)
    remaining={'select_t_roots':1}
    def check(data):
        if data['relevance']!='Q': raise Rejected('P')
        return data
    with pytest.raises(Rejected,match='cli_usage_limit'):
        construction_call(calls,'select_t_roots',{'papers':[]},check,remaining)
    assert remaining['select_t_roots']==0
    assert len(binary.with_suffix('.trace').read_text().splitlines())==5
    assert sum(e['stage']=='provider_retry' for e in log.read())==2
    assert sum(e['stage']=='construction_targeted_correction' for e in log.read())==1
    stages=[json.loads(e['payload_json']) for e in model_events(log) if e['stage']=='select_t_roots']
    assert [p['attempt'] for p in stages]==[1,2,2,2]


@pytest.mark.parametrize('mode',['ok','exit','timeout'])
def test_live_auth_source_unchanged_and_no_token_files(cli,mode):
    make,set_mode,_,binary=cli
    source=binary.parent/'home/.claude/.credentials.json'
    original=source.read_bytes()
    calls,log=make()
    set_mode(mode)
    if mode=='ok':
        calls.formalise(Proposition('p','P'))
    else:
        with pytest.raises(Rejected): calls.formalise(Proposition('p','P'))
    assert source.read_bytes()==original
    traces=[json.loads(row) for row in binary.with_suffix('.trace').read_text().splitlines()]
    assert all(not Path(t['config_dir']).exists() for t in traces)
    assert calls.provider.auth_mode=='env'
    from ara.runtime.export import methodology
    text=methodology(log.path)
    assert 'read-only credential file' in text and 'Same-user processes' in text
    assert 'offline-token' not in text and 'offline-refresh-token' not in text


def test_only_access_token_reaches_child_environment(cli,monkeypatch):
    import subprocess
    make,_,_,binary=cli
    original=subprocess.Popen
    observed=[]
    class Observe(original):
        def __init__(self, command, *args, **kwargs):
            if command[0]==str(binary) and '-p' in command:
                env=kwargs['env']
                assert env['CLAUDE_CODE_OAUTH_TOKEN']=='offline-token'
                assert 'offline-refresh-token' not in json.dumps(env)
                assert 'offline-token' not in json.dumps(command)
                assert not (Path(env['CLAUDE_CONFIG_DIR'])/'.credentials.json').exists()
                observed.append(True)
            super().__init__(command,*args,**kwargs)
    monkeypatch.setattr(subprocess,'Popen',Observe)
    calls,log=make()
    calls.formalise(Proposition('p','P'))
    assert observed==[True,True]


def test_environment_only_login_is_explicitly_disclosed(cli):
    make,_,_,binary=cli
    (binary.parent/'home/.claude/.credentials.json').unlink()
    calls,log=make()
    assert calls.provider.auth_mode=='env'
    from ara.runtime.export import methodology
    assert 'same-user environment inspection permitted' in methodology(log.path)


@pytest.mark.parametrize('location',['structured','key','routing','nested_result'])
def test_every_decoded_credential_string_is_checked(cli,location):
    make,set_mode,_,binary=cli
    source=binary.read_text()
    injection={
        'structured': "value['formula']['name']=token",
        'key': "value={token:{'P':['Q']}}",
        'routing': "result['modelUsage']={'claude-'+token:{}}",
        'nested_result': "result['result']=json.dumps({'P':[token]})",
    }[location]
    if location in ('structured','key'):
        source=source.replace("if mode=='secret_encoded': value['formula']['name']=token", "if mode=='secret_encoded': "+injection)
    else:
        source=source.replace("if mode=='secret_encoded': value['formula']['name']=token", "if mode=='secret_encoded': pass")
        source=source.replace('encoded=json.dumps(result)', "if mode=='secret_encoded': "+injection+"\nencoded=json.dumps(result)")
    binary.write_text(source)
    calls,log=make()
    set_mode('secret_encoded')
    with pytest.raises(Rejected,match='credential_in_cli_output'): calls.formalise(Proposition('p','P'))
    assert 'offline-token' not in log.path.read_text()
    assert not list(calls.cache.path.glob('*.json'))
    assert model_events(log)[-1]['usage']['input_tokens']==10


def test_credential_with_json_special_characters_is_checked(cli):
    make,set_mode,_,binary=cli
    source=binary.parent/'home/.claude/.credentials.json'
    auth=json.loads(source.read_text())
    auth['claudeAiOauth']['accessToken']='off"line\\token'
    source.write_text(json.dumps(auth))
    calls,log=make()
    set_mode('secret_encoded')
    with pytest.raises(Rejected,match='credential_in_cli_output'): calls.formalise(Proposition('p','P'))
    assert not list(calls.cache.path.glob('*.json'))
    assert model_events(log)[-1]['usage']['input_tokens']==10


@pytest.mark.parametrize('subscription', [True, False])
def test_subscription_token_cap_excludes_only_imported_history(cli, tmp_path, subscription):
    from ara.runtime.budget import Budget
    from ara.runtime.provenance import import_receipts
    from ara.types import RunEvent, TokenUsage
    from ara.runtime.logging import now
    from decimal import Decimal
    _, _, config, _ = cli
    history = EventLog(tmp_path/'history/events.jsonl')
    history.emit(RunEvent(now(), 'formalise', 'MODEL', usage=TokenUsage(input_tokens=1000),
                          payload_json=json.dumps({'cache_hit':False})))
    log = EventLog(tmp_path/'cap/events.jsonl')
    import_receipts(log, history.read())
    config['token_cap'] = 100
    budget = Budget(config, log)
    assert budget.used_tokens == 1000
    if not subscription:
        with pytest.raises(BudgetStop, match='token cap'):
            budget.reserve(TokenUsage(input_tokens=1), 'formalise', subscription=False)
        return
    reservation = budget.reserve(TokenUsage(input_tokens=60), 'formalise', subscription=True)
    assert budget.imported_tokens == 1000
    log.emit(RunEvent(now(), 'formalise', 'MODEL', usage=TokenUsage(input_tokens=60),
                      payload_json=json.dumps({'cache_hit':False})))
    reopened = Budget(config, log)
    assert reopened.used_tokens == 1060 and reopened.imported_tokens == 1000
    reopened.after('formalise', subscription=True)
    reopened.charge(TokenUsage(input_tokens=41), Decimal(0))
    with pytest.raises(BudgetStop, match='token cap exceeded by actual usage'):
        reopened.after('formalise', subscription=True)
    stop = json.loads(log.read()[-1]['payload_json'])
    assert stop['local_tokens'] == 101 and stop['imported_tokens'] == 1000
    budget.settle(reservation, TokenUsage(input_tokens=60), Decimal(0))
    budget.after('formalise', subscription=True)
    with pytest.raises(BudgetStop, match='token cap'):
        budget.reserve(TokenUsage(input_tokens=41), 'formalise', subscription=True)


@pytest.mark.parametrize('subtype,status,diagnostic,code,attempts', [
    ('error_max_turns', None, 'Reached max turns SECRET PROMPT ECHO', 'cli_max_turns', 3),
    ('error_during_execution', 503, 'overloaded SECRET PROMPT ECHO', 'cli_transient_error', 3),
    ('error_during_execution', 400, 'invalid JSON schema SECRET PROMPT ECHO', 'cli_invalid_schema', 1),
    ('error_during_execution', 401, 'authentication failed SECRET PROMPT ECHO', 'cli_auth_error', 2),
    ('error_during_execution', 422, 'invalid request SECRET PROMPT ECHO', 'cli_invalid_request', 1),
    ('error_during_execution', None, 'SECRET PROMPT ECHO', 'cli_exit_error', 2),
])
def test_exit_one_classification_preserves_usage_and_bounds_retries(cli, subtype, status, diagnostic, code, attempts):
    make, _, _, binary = cli
    calls, log = make()
    injection = ("if not canary:\n result.update(subtype=" + repr(subtype) +
                 ",is_error=True,api_error_status=" + repr(status) + ",errors=[" + repr(diagnostic) +
                 "])\n print(json.dumps(result)); sys.exit(1)\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)', injection+'encoded=json.dumps(result)'))
    with pytest.raises(Rejected, match=code):
        calls.formalise(Proposition('p','P'))
    assert len(model_events(log)) == attempts + 1
    assert sum(e['stage'] in ('provider_retry','unclassified_exit_retry','auth_refresh_retry') for e in log.read()) == attempts-1
    assert calls.budget.used_tokens == 20*(attempts+1)
    payload = json.loads(model_events(log)[-1]['payload_json'])
    assert payload['cli']['failure_class'] == code
    assert payload['cli']['failure_subtype'] == subtype
    assert 'SECRET PROMPT ECHO' not in log.path.read_text()


def test_transient_exit_retries_to_success_without_losing_usage(cli):
    make, _, _, binary = cli
    calls, log = make()
    injection = ("if not canary and len(trace.read_text().splitlines()) == 2:\n"
                 " result.update(subtype='error_max_turns',is_error=True)\n"
                 " print(json.dumps(result)); sys.exit(1)\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)', injection+'encoded=json.dumps(result)'))
    assert calls.formalise(Proposition('p','P')).name == 'P'
    assert [json.loads(e['payload_json'])['status'] for e in model_events(log)] == ['accepted','rejected','accepted']
    assert calls.budget.used_tokens == 60
    assert sum(e['stage']=='provider_retry' for e in log.read()) == 1


@pytest.mark.parametrize('retries,exit_status,recovers,expected', [
    (3,1,False,2), (3,1,True,2), (0,1,False,1), (3,7,False,1),
])
def test_unclassified_exit_retries_once_with_named_event(cli, retries, exit_status, recovers, expected):
    make, _, config, binary = cli
    config['claude_code']['retries'] = retries
    calls, log = make()
    condition = 'not canary' + (' and len(trace.read_text().splitlines()) == 2' if recovers else '')
    injection = ("if " + condition + ":\n result.update(subtype='error_during_execution',is_error=True)\n"
                 " print(json.dumps(result)); sys.exit(" + str(exit_status) + ")\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)', injection+'encoded=json.dumps(result)'))
    if recovers:
        assert calls.formalise(Proposition('p','P')).name == 'P'
    else:
        with pytest.raises(Rejected, match='cli_exit_error'):
            calls.formalise(Proposition('p','P'))
    assert len(model_events(log)) == expected+1
    assert sum(e['stage']=='unclassified_exit_retry' for e in log.read()) == expected-1
    assert calls.budget.used_tokens == 20*(expected+1)


@pytest.mark.parametrize('diagnostic', [
    '{"token":"new-secret-value"}',
    '{"password":"new-secret-value"}',
    'invalid value: P',
])
def test_kappa2_diagnostics_never_retain_free_text(cli, diagnostic):
    make, _, _, binary = cli
    calls, log = make()
    injection = ("if not canary:\n result.update(subtype='error_during_execution',is_error=True)\n"
                 " print(" + repr(diagnostic) + ",file=sys.stderr)\n print(json.dumps(result)); sys.exit(1)\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)', injection+'encoded=json.dumps(result)'))
    with pytest.raises(Rejected, match='cli_exit_error'):
        calls.formalise(Proposition('p','P'))
    receipt = json.loads(model_events(log)[-1]['payload_json'])['cli']
    assert 'stderr_first_line' not in receipt
    assert receipt['failure_subtype'] == 'error_during_execution'
    assert receipt['error_category'] == 'unknown'
    assert receipt['stderr_bytes'] == len((diagnostic+'\n').encode())
    # Inspect both provider_error and MODEL event payloads, not just the helper.
    for event in log.read():
        payload = json.loads(event['payload_json'])
        assert diagnostic not in json.dumps(payload, ensure_ascii=False)
        assert 'new-secret-value' not in json.dumps(payload)
        assert 'stderr_first_line' not in json.dumps(payload)


@pytest.mark.parametrize('field', ['subtype', 'error_type', 'error', 'errors', 'result'])
def test_json_diagnostics_are_suppressed(cli, field):
    make, _, _, binary = cli
    calls, log = make()
    diagnostic = '{"token":"new-secret-value"}'
    injection = ("if not canary:\n result.update(subtype='error_during_execution',is_error=True)\n"
                 " result[" + repr(field) + "]=" + repr(diagnostic) + "\n"
                 " print(json.dumps(result)); sys.exit(1)\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)', injection+'encoded=json.dumps(result)'))
    with pytest.raises(Rejected, match='cli_exit_error'):
        calls.formalise(Proposition('p','P'))
    receipt = json.loads(model_events(log)[-1]['payload_json'])['cli']
    assert receipt['error_category'] == 'unknown'
    if field == 'subtype':
        assert 'failure_subtype' not in receipt
    else:
        assert receipt['failure_subtype'] == 'error_during_execution'
    assert 'new-secret-value' not in log.path.read_text()


@pytest.mark.parametrize('diagnostic,category', [
    ('rate limit invalid value: P', 'rate_limit'),
    ('usage limit invalid value: P', 'usage_limit'),
    ('authentication error invalid value: P', 'auth'),
    ('request timed out invalid value: P', 'timeout'),
    ('invalid schema invalid value: P', 'schema'),
    ('overloaded invalid value: P', 'transient'),
    ('prompt too long invalid value: P', 'request'),
])
def test_exit_diagnostic_retains_only_recognized_category(cli, diagnostic, category):
    make, _, _, binary = cli
    calls, log = make()
    injection = ("if not canary:\n result.update(subtype='error_during_execution',is_error=True)\n"
                 " print(" + repr(diagnostic) + ",file=sys.stderr)\n print(json.dumps(result)); sys.exit(1)\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)', injection+'encoded=json.dumps(result)'))
    with pytest.raises(Rejected):
        calls.formalise(Proposition('p','P'))
    receipt = json.loads(model_events(log)[-1]['payload_json'])['cli']
    assert receipt['error_category'] == category
    assert 'stderr_first_line' not in receipt
    assert diagnostic not in log.path.read_text()


def test_unclassified_non_json_exit_retries_once_and_accounts_reservations(cli):
    make, _, config, binary = cli
    config['claude_code']['retries'] = 3
    calls, log = make()
    injection = "if not canary:\n print('worker stopped',file=sys.stderr); sys.exit(1)\n"
    binary.write_text(binary.read_text().replace('schema=json.loads', injection+'schema=json.loads'))
    estimate = calls.count_request('formalise', {'proposition':Proposition('p','P').to_dict()}).reservation
    with pytest.raises(Rejected, match='cli_exit_error'):
        calls.formalise(Proposition('p','P'))
    events = model_events(log)
    assert len(events) == 3
    assert sum(e['stage']=='unclassified_exit_retry' for e in log.read()) == 1
    assert calls.budget.used_tokens == 20+2*sum(estimate.to_dict().values())
    assert all(json.loads(e['payload_json'])['accounting']=='reservation_unknown_actual' for e in events[1:])
    assert all('stderr_first_line' not in json.loads(e['payload_json'])['cli'] for e in events[1:])
    assert 'worker stopped' not in log.path.read_text()


@pytest.mark.parametrize('category,code', [('authentication_error','cli_auth_error'),('authorization_error','cli_auth_error'),
                                             ('permission_error','cli_auth_error'),('invalid_request_error','cli_invalid_request'),
                                             ('context_length_exceeded','cli_invalid_request')])
@pytest.mark.parametrize('field', ['error', 'subtype'])
def test_json_error_categories_follow_retry_policy(cli, category, code, field):
    make, _, _, binary = cli
    calls, log = make()
    injection = ("if not canary:\n result.update(subtype='error_during_execution',is_error=True,error={'type':"+repr(category)+"})\n"
                 " result.update(" + repr({"subtype": category, "error": None} if field == "subtype" else {}) + ")\n"
                 " print(json.dumps(result)); sys.exit(1)\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)', injection+'encoded=json.dumps(result)'))
    with pytest.raises(Rejected, match=code):
        calls.formalise(Proposition('p','P'))
    auth = code == 'cli_auth_error'
    assert len(model_events(log)) == (3 if auth else 2)
    assert sum(e['stage']=='auth_refresh_retry' for e in log.read()) == int(auth)
    assert not any(e['stage'] in ('provider_retry','unclassified_exit_retry') for e in log.read())
    receipt=json.loads(model_events(log)[-1]['payload_json'])['cli']
    assert receipt['error_category'] == ('auth' if code == 'cli_auth_error' else 'request')
    if field == 'subtype':
        assert 'failure_subtype' not in receipt


def test_security_rejection_suppresses_json_diagnostics(cli):
    make, _, _, binary = cli
    calls, log = make()
    injection = ("if not canary:\n result.update(subtype='error_worker_crash',is_error=True,error={'type':token})\n"
                 " print(json.dumps(result)); sys.exit(1)\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)', injection+'encoded=json.dumps(result)'))
    with pytest.raises(Rejected, match='credential_in_cli_output'):
        calls.formalise(Proposition('p','P'))
    receipt=json.loads(model_events(log)[-1]['payload_json'])['cli']
    assert 'failure_subtype' not in receipt
    assert receipt['error_category'] == 'unknown'
    assert receipt['retryable'] is False
    assert 'offline-token' not in log.path.read_text()



def test_credential_file_replaced_between_calls_is_read_fresh(cli):
    make,_,_,binary=cli
    calls,log=make()
    calls.formalise(Proposition('p','P'))
    source=binary.parent/'home/.claude/.credentials.json'
    auth=json.loads(source.read_text())
    auth['claudeAiOauth']['accessToken']='offline-replaced-token'
    replacement=source.with_suffix('.replacement')
    replacement.write_text(json.dumps(auth)); replacement.chmod(0o600)
    replacement.replace(source)
    injection="if not canary: assert token == 'offline-replaced-token', 'stale credential'\n"
    binary.write_text(binary.read_text().replace('schema=json.loads',injection+'schema=json.loads'))
    assert calls.formalise(Proposition('q','P')).name=='P'
    assert len(model_events(log))==3
    assert 'offline-replaced-token' not in log.path.read_text()
    assert source.read_text()==json.dumps(auth)


@pytest.mark.parametrize('recovers,retries,measured,attempts', [
    (True,3,True,2), (False,3,True,2), (False,0,True,1), (True,3,False,2),
])
def test_auth_reread_retry_is_once_and_accounted(cli,recovers,retries,measured,attempts):
    make,_,config,binary=cli
    config['claude_code']['retries']=retries
    calls,log=make()
    injection=("if not canary and (token == 'offline-token' or not "+repr(recovers)+"):\n"
               " source=Path(__file__).parent/'home/.claude/.credentials.json'\n"
               " auth=json.loads(source.read_text()); auth['claudeAiOauth']['accessToken']='offline-replaced-token'\n"
               " replacement=source.with_suffix('.replacement'); replacement.write_text(json.dumps(auth)); replacement.chmod(0o600); replacement.replace(source)\n"
               " result.update(subtype='error_during_execution',is_error=True,api_error_status=401)\n"
               +(" result.pop('usage')\n" if not measured else '')+
               " print(json.dumps(result)); sys.exit(1)\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)',injection+'encoded=json.dumps(result)'))
    estimate=calls.count_request('formalise', {'proposition':Proposition('p','P').to_dict()}).reservation
    if recovers:
        assert calls.formalise(Proposition('p','P')).name=='P'
    else:
        with pytest.raises(Rejected,match='cli_auth_error'): calls.formalise(Proposition('p','P'))
    assert len(model_events(log))==attempts+1
    assert sum(e['stage']=='auth_refresh_retry' for e in log.read())==attempts-1
    assert not any(e['stage']=='provider_retry' for e in log.read())
    assert calls.budget.used_tokens==(20*(attempts+1) if measured else 40+sum(estimate.to_dict().values()))
    assert 'offline-replaced-token' not in log.path.read_text()
    assert 'offline-token' not in log.path.read_text()


def test_inflight_credential_is_scanned_after_host_replacement(cli,monkeypatch):
    make,_,_,binary=cli
    calls,log=make()
    monkeypatch.delenv('CLAUDE_CODE_OAUTH_TOKEN')
    injection=("if not canary:\n"
               " source=Path(__file__).parent/'home/.claude/.credentials.json'\n"
               " auth=json.loads(source.read_text()); auth['claudeAiOauth']['accessToken']='offline-replaced-token'\n"
               " source.write_text(json.dumps(auth))\n"
               " result['result']=json.dumps({'P':token})\n")
    binary.write_text(binary.read_text().replace('encoded=json.dumps(result)',injection+'encoded=json.dumps(result)'))
    with pytest.raises(Rejected,match='credential_in_cli_output'): calls.formalise(Proposition('p','P'))
    assert 'offline-token' not in log.path.read_text()
    assert not list(calls.cache.path.glob('*.json'))


def test_operator_home_is_not_discoverable_by_child(cli, monkeypatch):
    """A clean config alone must not expose HOME-based instruction discovery."""
    make, _, _, binary = cli
    home = Path.home()
    (home/'.claude/CLAUDE.md').write_text('P')
    (home/'.claude/projects').mkdir()
    (home/'.claude/projects/memory.md').write_text('Q')
    monkeypatch.setenv('XDG_CONFIG_HOME', str(home/'.claude'))
    monkeypatch.setenv('CLAUDE_MEMORY_PATH', str(home/'.claude/projects'))
    source = binary.read_text()
    needle = "if mode=='bad_canary': value['agents_md']='P'"
    replacement = """if (Path.home()/'.claude/CLAUDE.md').exists(): value['claude_md']='P'
 assert 'CLAUDE_MEMORY_PATH' not in os.environ
 """ + needle
    binary.write_text(source.replace(needle, replacement))
    calls, log = make()
    calls.formalise(Proposition('p', 'P'))
    calls.formalise(Proposition('q', 'Q'))
    assert len(model_events(log)) == 3
    assert (home/'.claude/CLAUDE.md').read_text() == 'P'


@pytest.mark.parametrize('context', ['\n', 'P'])
def test_canary_context_diagnostics_do_not_relax_rejection(cli, context):
    make, _, _, binary = cli
    binary.write_text(binary.read_text().replace(
        "if mode=='bad_canary': value['agents_md']='P'",
        "value['claude_md']=" + repr([context])))
    with pytest.raises(Rejected, match='isolation_context_present'):
        make()
    log = EventLog(binary.parent/'run/events.jsonl')
    errors = [json.loads(e['payload_json']) for e in log.read() if e['stage']=='provider_error']
    receipt = errors[-1]['cli']
    assert receipt['isolation_context_fields'] == ['claude_md']
    assert receipt['isolation_context_entry_counts'] == {'claude_md': 1}
    assert not list((binary.parent/'cache').glob('*.json'))


def test_every_cli_invocation_has_private_empty_home(cli, monkeypatch):
    import subprocess
    make, _, _, binary = cli
    original = subprocess.Popen
    homes = []
    class Observe(original):
        def __init__(self, command, *args, **kwargs):
            if command[0] == str(binary):
                env = kwargs['env']
                home = Path(env['HOME'])
                assert home != Path.home()
                assert home.parent == Path(env['CLAUDE_CONFIG_DIR']).parent
                assert home.stat().st_mode & 0o777 == 0o700
                assert not list(home.iterdir())
                homes.append(str(home))
            super().__init__(command, *args, **kwargs)
    monkeypatch.setattr(subprocess, 'Popen', Observe)
    calls, _ = make()
    calls.formalise(Proposition('p', 'P'))
    assert len(homes) == 3  # Version + canary share one process directory; next call is fresh.
    assert homes[0] == homes[1] and homes[1] != homes[2]


CONTEXT_FIELDS = ('skills', 'memory', 'claude_md', 'agents_md')


def test_list_canary_wire_accepts_only_actual_empty_lists(cli):
    make, _, _, binary = cli
    calls, log = make()
    trace = json.loads(binary.with_suffix('.trace').read_text().splitlines()[0])
    schema = json.loads(trace['args'][trace['args'].index('--json-schema')+1])
    for field in CONTEXT_FIELDS:
        assert schema['properties'][field] == {'type': 'array', 'items': {'type': 'string'}}
        assert field in schema['required']
    assert '[]' in trace['prompt']
    payload = json.loads(model_events(log)[0]['payload_json'])
    assert payload['isolation']['status'] == 'proven'
    assert payload['canary_report_format'] == 'context-lists-v1'
    assert calls.provider.ready


@pytest.mark.parametrize('field', CONTEXT_FIELDS)
@pytest.mark.parametrize('value,reason', [
    ([''], 'isolation_context_present'),
    (['\n'], 'isolation_context_present'),
    ([' ', '\t'], 'isolation_context_present'),
    (['P'], 'isolation_context_present'),
    ('', 'isolation_canary_invalid'),
    ('\n', 'isolation_canary_invalid'),
    (None, 'isolation_canary_invalid'),
    (False, 'isolation_canary_invalid'),
    ({}, 'isolation_canary_invalid'),
    ([None], 'isolation_canary_invalid'),
    ([[]], 'isolation_canary_invalid'),
])
def test_list_canary_rejects_nonempty_and_wrong_types_before_dispatch(cli, field, value, reason):
    make, _, _, binary = cli
    needle = "if mode=='bad_canary': value['agents_md']='P'"
    binary.write_text(binary.read_text().replace(needle, f'value[{field!r}]={value!r}\n '+needle))
    with pytest.raises(Rejected, match='^'+reason+'$'):
        make()
    rows = binary.with_suffix('.trace').read_text().splitlines()
    assert len(rows) == 1 and 'ARA_ISOLATION_CANARY' in json.loads(rows[0])['prompt']
    assert not list((binary.parent/'cache').glob('*.json'))
    # Rejected context is not persisted as a response body or diagnostic text.
    log = EventLog(binary.parent/'run/events.jsonl')
    event = model_events(log)[0]
    assert json.loads(event['response'])['content'] == []


@pytest.mark.parametrize('field', CONTEXT_FIELDS)
def test_list_canary_missing_fields_are_not_defaulted(cli, field):
    make, _, _, binary = cli
    needle = "if mode=='bad_canary': value['agents_md']='P'"
    binary.write_text(binary.read_text().replace(needle, f'value.pop({field!r})\n '+needle))
    with pytest.raises(Rejected, match='^isolation_canary_invalid$'):
        make()
    assert len(binary.with_suffix('.trace').read_text().splitlines()) == 1
    assert not list((binary.parent/'cache').glob('*.json'))


def test_claude_list_schema_does_not_change_inherited_codex_contract():
    from types import SimpleNamespace
    from ara.runtime.claude_code import ClaudeCodeProvider, CANARY_SCHEMA, CANARY_PROMPT
    from ara.runtime.codex_cli import CodexCLIProvider
    claude = object.__new__(ClaudeCodeProvider)
    codex = object.__new__(CodexCLIProvider)
    claude_schema = ModelCalls.response_schema(SimpleNamespace(provider=claude), 'isolation_canary', {})
    codex_schema = ModelCalls.response_schema(SimpleNamespace(provider=codex), 'isolation_canary', {})
    assert all(claude_schema['properties'][field]['type'] == 'array' for field in CONTEXT_FIELDS)
    assert codex_schema == CANARY_SCHEMA
    assert all(codex_schema['properties'][field]['type'] == 'string' for field in CONTEXT_FIELDS)
    assert CodexCLIProvider.canary_prompt.startswith(CANARY_PROMPT)
    assert claude_schema is not codex_schema
    assert claude.canary_report_format == 'context-lists-v1'
    assert codex.canary_report_format == 'context-strings-v1'


@pytest.mark.parametrize('context,reason', [
    ('offline-token', 'credential_in_cli_output'),
    ('sentinel@example.invalid', 'operator_identity_in_output'),
])
def test_list_context_keeps_sensitive_output_screening(cli, context, reason):
    make, _, _, binary = cli
    needle = "if mode=='bad_canary': value['agents_md']='P'"
    binary.write_text(binary.read_text().replace(needle, "value['memory']="+repr([context])+'\n '+needle))
    with pytest.raises(Rejected, match='^'+reason+'$'):
        make()
    log = EventLog(binary.parent/'run/events.jsonl')
    assert context not in log.path.read_text()
    assert len(binary.with_suffix('.trace').read_text().splitlines()) == 1
    assert not list((binary.parent/'cache').glob('*.json'))
