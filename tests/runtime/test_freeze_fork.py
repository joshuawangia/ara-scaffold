"""Verified frozen-prefix reuse; placeholder inputs and fake calls only."""
import json
from pathlib import Path

import pytest
import yaml

from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.logging import EventLog
from ara.runtime.frozen_catalogue import frozen_artifact
from ara.types import RunEvent, TokenUsage
from test_search_alignment import T, ROOT


def source(tmp_path):
    directory=tmp_path/'source';log=EventLog(directory/'events.jsonl')
    config=yaml.safe_load((ROOT/'config.yaml').read_text())
    config.update(provider='mock',cache_dir=str(tmp_path/'cache'),target_candidates=1)
    bank=load_bank(ROOT/'bank')
    log.record('run_started',config=config,topic='P',audience='P',literature='P',bank_version=bank.bank_version)
    log.emit(RunEvent('2026-10-01T00:00:00Z','build_t','MODEL',usage=TokenUsage(input_tokens=7),cost_usd=0.01))
    artifact=frozen_artifact(T,[dict(name=n,kind='atom',arity=0,definition=n,evidence_ids=['t2']) for n in ('P','Q')])
    (directory/'commitments.json').write_text(T.to_json())
    (directory/'frozen-t.json').write_text(canonical(artifact))
    log.record('symbol_catalogue_frozen',**artifact['symbol_catalogue'])
    log.record('commitments_frozen',commitments=T.to_dict(),bank_version=bank.bank_version)
    prefix=(directory/'events.jsonl').read_bytes()
    log.record('candidates',candidates=[])
    return directory,config,bank,prefix


def test_fork_exact_prefix_and_single_accounting(tmp_path):
    from ara.runtime.freeze_fork import fork_from_freeze
    from ara.runtime.budget import Budget
    from ara.runtime.provenance import imported_event_indices
    src,config,bank,prefix=source(tmp_path)
    original={p.name:p.read_bytes() for p in src.iterdir() if p.is_file()}
    dst=tmp_path/'fork'
    log,run,t=fork_from_freeze(src,dst,bank)
    assert (dst/'events.jsonl').read_bytes().startswith(prefix)
    assert (dst/'commitments.json').read_bytes()==original['commitments.json']
    assert t==T
    events=log.read()
    assert sum(e['stage']=='commitments_frozen' for e in events)==1
    assert not any(e['stage']=='candidates' for e in events)
    budget=Budget(config,log)
    assert budget.used_tokens==budget.imported_tokens==7
    assert float(budget.used_cost)==0.01
    assert imported_event_indices(events)==set(range(4))
    assert {p.name:p.read_bytes() for p in src.iterdir() if p.is_file()}==original
    with pytest.raises(ValueError,match='empty'):
        fork_from_freeze(src,dst,bank)
    assert Budget(config,log).used_tokens==7


@pytest.mark.parametrize('defect',['chain','anchor','artifact','catalogue','duplicate','bank'])
def test_fork_refuses_before_destination_or_provider(tmp_path,defect):
    from ara.runtime.freeze_fork import fork_from_freeze
    src,config,bank,prefix=source(tmp_path)
    if defect=='chain':
        p=src/'events.jsonl';p.write_bytes(p.read_bytes().replace(b'2026-',b'2025-',1))
    elif defect=='anchor': (src/'events.anchor').write_text('0'*64+'\n')
    elif defect=='artifact': (src/'commitments.json').write_text('{"commitments":[]}')
    elif defect=='catalogue': (src/'frozen-t.json').write_text('{}')
    elif defect=='duplicate': EventLog(src/'events.jsonl').record('commitments_frozen',commitments=T.to_dict(),bank_version=bank.bank_version)
    elif defect=='bank':
        from dataclasses import replace
        bank=replace(bank,bank_version='Q')
    dst=tmp_path/'fork'
    with pytest.raises(ValueError): fork_from_freeze(src,dst,bank)
    assert not dst.exists()


def test_native_fork_cli_starts_at_targets(tmp_path):
    from ara.runtime.cli import main
    from ara.runtime.calls import ModelCalls
    from ara.runtime.cache import Cache
    from ara.runtime.providers import MockProvider,Response
    from test_search_alignment import raw,GOAL,cut,P,PQ
    src,config,bank,prefix=source(tmp_path)
    kinds=[]
    def factory(config,log,topic):
        provider=MockProvider({})
        def complete(kind,prompt,*args):
            kinds.append(kind);inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1])
            if kind=='propose_targets': value={'targets':[GOAL.to_dict()]}
            elif kind=='map_leaf': value={'t_id':'open'}
            elif kind=='propose_cuts': value={'proposals':[cut()] if inputs['goal']['id']=='q' else []}
            elif kind=='formalise_slots': value={'slots':[dict(slot='conditional',formula=PQ.to_dict()),dict(slot='antecedent',formula=P.to_dict())]}
            else: pytest.fail(kind)
            return Response(raw(value))
        provider.complete=complete
        config={**config,'forward_pass_depth':0}
        return ModelCalls(config,provider,log,Cache(tmp_path/'cache'),ROOT,topic)
    dst=tmp_path/'fork'
    assert main(['fork-from-freeze','--source-run',str(src),'--run-dir',str(dst)],calls_factory=factory)==0
    assert kinds[0]=='propose_targets' and 'build_t' not in kinds
    events=EventLog(dst/'events.jsonl').read()
    assert any(e['stage']=='awaiting_selection' for e in events)
    assert sum(e['stage']=='commitments_frozen' for e in events)==1
