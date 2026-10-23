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
if not canary and mode=='plain_rate': print('rate limit SECRET PROMPT ECHO',file=sys.stderr); sys.exit(1)
schema=json.loads(arg('--json-schema'))
assert '$schema' not in schema
if canary:
 value={k:'' for k in schema['properties']}
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
 'session_id':arg('--session-id'),'usage':usage,'modelUsage':{arg('--model'):{'inputTokens':10,'outputTokens':5}},
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


@pytest.mark.parametrize('mode',['rate','usage','plain_rate'])
def test_bounded_logged_retry(cli,mode):
    make,set_mode,_,binary=cli
    calls,log=make()
    set_mode(mode)
    with pytest.raises((BudgetStop,Rejected)): calls.formalise(Proposition('p','P'))
    assert len(binary.with_suffix('.trace').read_text().splitlines())==4
    assert sum(e['stage']=='provider_retry' for e in log.read())==2
    assert len(model_events(log))==4
    if mode!='plain_rate':
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
def test_private_auth_snapshot_cleanup_and_source_unchanged(cli,mode):
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
    assert calls.provider.auth_mode=='config-link'
    from ara.runtime.export import methodology
    text=methodology(log.path)
    assert 'private 0600 OAuth snapshot' in text and 'Same-user processes' in text
    assert 'offline-token' not in text and 'offline-refresh-token' not in text


def test_config_auth_has_no_token_in_same_user_process_environment(cli,monkeypatch):
    import subprocess
    make,_,_,binary=cli
    original=subprocess.Popen
    observed=[]
    class Observe(original):
        def __init__(self, command, *args, **kwargs):
            super().__init__(command,*args,**kwargs)
            if command[0]==str(binary) and '-p' in command:
                shown=subprocess.check_output(['ps','eww','-o','args=','-p',str(self.pid)])
                observed.append(b'offline-token' not in shown and b'offline-refresh-token' not in shown)
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
