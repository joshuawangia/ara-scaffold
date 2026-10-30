"""Final verification dissent consumes the same durable repair budget."""
import json
import pytest

from ara.runtime.providers import Response
from test_calls import rig, response
from test_publication import install_publication, paper, polished


def final_editor(rig, monkeypatch, *, all_rounds=False, interrupt=False):
    from ara.runtime import essay_audit
    calls, route, _ = install_publication(rig, monkeypatch)
    monkeypatch.setattr(calls, 'verify_originality_citations',
                        lambda draft: (draft, dict(items=[dict(status='verified')])))
    original = calls.provider.complete
    seen, repairs = [], []
    audits = 0
    def complete(kind, prompt, schema, maximum):
        nonlocal audits
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        seen.append((kind, data))
        if kind == 'polish_essay' and data['mode'] == 'repair':
            repairs.append(data)
            title = {1:'Q', 2:'R', 3:'S'}[data['repair_round']]
            markdown = '# '+title+'\n'+data['markdown'].split('\n', 1)[1]
            return Response(response(dict(polished(paper()), markdown=markdown)))
        value = original(kind, prompt, schema, maximum)
        if kind == 'audit_publication':
            audits += 1
            title = next(s['text'] for s in data['sentences'] if s['field']=='title')
            bad = ((audits-1)//3 in (0,2,4,6)) if all_rounds else (audits==5 or (interrupt and title=='Q'))
            if bad:
                out = json.loads(value.text())
                number = next(s['sentence'] for s in data['sentences'] if s['field']=='title')
                next(label for label in out['labels'] if label['sentence']==number)['publication_issue']='unsupported_elaboration'
                return Response(response(out))
        return value
    monkeypatch.setattr(calls.provider, 'complete', complete)
    if interrupt:
        gate = essay_audit.audit_consensus
        state = dict(count=0, enabled=True)
        def interrupted(*args, **kwargs):
            state['count'] += 1
            if state['enabled'] and state['count']==3:
                raise RuntimeError('interrupted after accepted repair')
            return gate(*args, **kwargs)
        monkeypatch.setattr(essay_audit, 'audit_consensus', interrupted)
    else:
        state = None
    return calls, route, seen, repairs, state


@pytest.mark.parametrize('inline', [False, True])
def test_final_gate_flag_gets_targeted_repair_and_fresh_gates(rig, monkeypatch, inline):
    from ara.runtime.publication import polish
    calls, route, seen, repairs, _ = final_editor(rig, monkeypatch)
    calls.config['publication_inline_repairs'] = inline
    result, _ = polish(calls, route, paper())
    assert result['polished'] and result['native_citations']['status']=='pass'
    assert result['repair_rounds']==result['accepted_repair_rounds']==1
    assert result['draft']['title']=='Q'
    assert [r['repair_round'] for r in repairs]==[1]
    assert repairs[0]['flagged_sentences'][0]['field']=='title'
    assert sum(kind=='audit_publication' for kind,_ in seen)==12


def test_pre_and_post_verification_share_three_round_total(rig, monkeypatch):
    from ara.runtime.publication import polish
    calls, route, seen, repairs, _ = final_editor(rig, monkeypatch, all_rounds=True)
    result, _ = polish(calls, route, paper())
    assert not result['polished'] and result['draft']==paper()
    assert result['repair_rounds']==result['accepted_repair_rounds']==3
    assert [r['repair_round'] for r in repairs]==[1,2,3]
    assert sum(kind=='audit_publication' for kind,_ in seen)==21
    before = len(seen)
    from ara.runtime.calls import Rejected
    with pytest.raises(Rejected, match='repair budget exhausted'):
        polish(calls, route, paper())
    assert len(seen)==before


def test_resume_uses_saved_repair_and_remaining_rounds_only(rig, monkeypatch):
    from ara.runtime.publication import polish
    calls, route, seen, repairs, state = final_editor(rig, monkeypatch, interrupt=True)
    with pytest.raises(RuntimeError, match='interrupted after accepted repair'):
        polish(calls, route, paper())
    assert [r['repair_round'] for r in repairs]==[1]
    before = len(seen)
    state['enabled'] = False
    result, _ = polish(calls, route, paper())
    assert result['polished'] and result['draft']['title']=='R'
    assert result['repair_rounds']==result['accepted_repair_rounds']==2
    assert [r['repair_round'] for r in repairs]==[1,2]
    assert all(data['mode']=='repair' for kind,data in seen[before:] if kind=='polish_essay')
    assert repairs[-1]['markdown'].startswith('# Q\n')


def test_resumed_candidate_is_screened_before_logging_or_dispatch(rig, monkeypatch):
    from ara.runtime.publication import polish
    from ara.runtime.calls import Rejected
    calls, route, seen, _, state = final_editor(rig, monkeypatch, interrupt=True)
    with pytest.raises(RuntimeError):
        polish(calls, route, paper())
    before_events = calls.log.read()
    before_calls = len(seen)
    original_screen = calls.screen_imported_draft
    def screen(draft, *, kind):
        if draft['title']=='Q':raise Rejected('effective_provider_scan')
        return original_screen(draft,kind=kind)
    monkeypatch.setattr(calls,'screen_imported_draft',screen)
    state['enabled']=False
    with pytest.raises(Rejected,match='effective_provider_scan'):
        polish(calls,route,paper())
    assert calls.log.read()==before_events
    assert len(seen)==before_calls
