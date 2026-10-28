"""CQ retrieval/strictness and bounded native scheme correction on placeholders."""
import json
import pytest
from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.orchestration import NativeEngine
from ara.runtime.providers import TokenUsage
from ara.types import Commitment, CommitmentSet, CriticalQuestion, Formula, PremiseFill, Proposal, Proposition
from test_search_alignment import rig, ROOT, P, Q, R
from test_cross_paper import frozen_metadata


def setup(tmp_path, reply, t=None):
    t = t or CommitmentSet((Commitment('p', 'P', 'a:1', P), Commitment('q', 'Q', 'b:1', Q),
                            Commitment('r', 'R', 'c:1', R)))
    calls, requests = rig(tmp_path, reply)
    artifact, provenance = frozen_metadata(t, tuple(c.citation.split(':')[0] for c in t.commitments))
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    return calls, requests, t


def proposal():
    return Proposal('sign', (PremiseFill('sign_relation','P','p'), PremiseFill('observed_sign','Q','q')), 'S')


def test_cq_retrieves_outside_premises_ranks_and_shrinks(tmp_path, monkeypatch):
    t = CommitmentSet(tuple(Commitment(str(i), 'Q', 'a:1', Q) for i in range(20)) +
                      (Commitment('z', 'R Q', 'b:1', Formula('and',(R,Q))),))
    calls, requests, t = setup(tmp_path, lambda kind, d: dict(cq_id='cq1',answer='R',answered=True,supporting_t_ids=['z']), t)
    calls.config['model_context_token_bound'] = 10000
    def count(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return TokenUsage(input_tokens=1000*len(data['commitments']['commitments']), output_tokens=maximum)
    monkeypatch.setattr(calls.provider,'estimate',count)
    assert calls.answer_cq(CriticalQuestion('cq1','R Q'),proposal(),t).answered
    data = requests[-1][1]
    assert data['commitments']['commitments'][0]['id'] == 'z'
    assert len(data['commitments']['commitments']) == 1
    assert data['cq_retrieval']['ranking'] == 'shared_symbols_then_content_overlap_then_id'
    slices = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='cq_context_slice']
    assert len(slices) > 1 and slices[-1]['decision']=='fits'


@pytest.mark.parametrize('text', ['Partly: P', 'To some extent, P', 'Only partially P'])
def test_partial_cq_is_disclosed_and_not_supported(tmp_path,text):
    calls, _, t = setup(tmp_path,lambda kind,d: dict(cq_id='cq1',answer=text,answered=True,supporting_t_ids=['p']))
    answer = calls.answer_cq(CriticalQuestion('cq1','P'),proposal(),t)
    assert not answer.answered and answer.answer == text and answer.supporting_t_ids == ('p',)
    assert any(e['stage']=='cq_answer_downgraded' for e in calls.log.read())


@pytest.mark.parametrize('alternative', ['best_explanation','sign'])
def test_unsupported_cq_gets_one_different_scheme_correction(tmp_path,alternative):
    s = Formula('atom',name='S')
    attempts = []
    def reply(kind,d):
        if kind=='map_leaf': return dict(t_id='open')
        if kind=='propose_cuts':
            attempts.append(d)
            bank = 'sign' if len(attempts)==1 else alternative
            slots = ('sign_relation','observed_sign') if bank=='sign' else ('observations','explanation','alternatives')
            ids = ('p','q') if bank=='sign' else ('p','q','r')
            cut = dict(bank_id=bank,conclusion_text='S',conclusion_ref='current_goal',
                premises=[dict(slot=slot,text=tid.upper(),t_id=tid,scope_id=None) for slot,tid in zip(slots,ids)])
            return dict(proposals=[cut,dict(cut,bank_id='absent')] if len(attempts)==1 else [cut])
        if kind=='formalise_slots': return dict(slots=[dict(slot=b['slot'],formula=b['formula']) for b in d['slot_bindings']])
        if kind=='answer_cq': return dict(cq_id=d['question']['id'],answer='P',answered=d['proposal']['bank_id']!='sign',supporting_t_ids=['p'])
        raise AssertionError(kind)
    calls, _, t = setup(tmp_path,reply)
    routes = NativeEngine(load_bank(ROOT/'bank'),calls)._engine(t).search(Proposition('s','S',s)).routes
    assert len(attempts)==2
    assert attempts[-1]['rejection_feedback'][0]['reason']=='CQ_UNSUPPORTED'
    assert any(r.status=='CLOSED' for r in routes) == (alternative!='sign')
    assert any(r.status=='OPEN' for r in routes)
    assert len(routes)==(2 if alternative!='sign' else 1)
    rows=[json.loads(line) for path in (tmp_path/'search-traces').glob('*.jsonl') for line in path.read_text().splitlines()]
    indices=[(r['state_id'],r['node_id'],r['proposal_index']) for r in rows if r['action']=='proposal']
    assert len(indices)==len(set(indices))



def test_retrieval_excludes_restricted_evidence_but_full_T_ids_remain_valid(tmp_path):
    from ara.runtime.commitment_provenance import make_commitment_provenance
    from ara.engine.routes import cq_supported
    from ara.types import CQAnswer
    calls,requests,t=setup(tmp_path,lambda kind,d: dict(cq_id='cq1',answer='Q',answered=True,supporting_t_ids=['q']))
    artifact,provenance=frozen_metadata(t,('a','b','c'))
    provenance['commitments']['p'].update(stance='attacked',attribution='attacked_view')
    provenance=make_commitment_provenance(t,artifact['symbol_catalogue'],provenance['commitments'])
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    answer=calls.answer_cq(CriticalQuestion('cq1','P'),proposal(),t)
    data=requests[-1][1]
    assert 'p' not in [c['id'] for c in data['commitments']['commitments']]
    # Citations are validated against all T, not the retrieved candidate list.
    assert answer.supporting_t_ids==('q',) and answer.answered
    assert not cq_supported(CQAnswer('cq1','Partly P',True,('q',)),'cq1',t)


def test_cq_lexical_overlap_retrieves_definitions_without_shared_symbols(tmp_path):
    calls,requests,t=setup(tmp_path,lambda kind,d: dict(cq_id='cq1',answer='Q',answered=False,supporting_t_ids=[]))
    artifact,provenance=frozen_metadata(t,('a','b','c'),{'Q':'placeholder unresolved issue'})
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    calls.answer_cq(CriticalQuestion('cq1','unresolved issue'),proposal(),t)
    rows=requests[-1][1]['cq_retrieval']['candidates']
    assert [r['commitment_id'] for r in rows]==['q']
    assert rows[0]['shared_symbols']==0 and rows[0]['content_overlap']==2
