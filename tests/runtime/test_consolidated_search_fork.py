"""A consolidated v5 freeze enters the native packed-search fork unchanged."""
import json

from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.cli import main
from ara.runtime.logging import EventLog
from ara.runtime.providers import MockProvider, Response
from ara.runtime.search_alignment import catalogue_inputs
from ara.types import CommitmentSet, Formula, Proposition
from test_extraction import rig, ROOT
from test_hypothesis_construction_fork import snapshot
from test_search_alignment import raw
from test_vocabulary_consolidation import launch


def test_native_v5_fork_keeps_history_out_of_search_prompts(rig, monkeypatch, tmp_path):
    rc, source, _, _ = launch(rig, monkeypatch, tmp_path)
    assert rc == 0
    original = snapshot(source)
    t = CommitmentSet.from_json((source/'commitments.json').read_text())
    full = catalogue_inputs(source, t)
    assert full['commitment_provenance']['schema_version'] == 'commitment-provenance-v5'
    assert full['commitment_provenance']['consolidation']['schema_version'] == 'vocabulary-consolidation-v3'
    destination = tmp_path/'packed-fork'
    sent = []
    target = Proposition('r', 'R', Formula('atom', name='R'),
                         basis_commitment_ids=tuple(c.id for c in t.commitments))
    def factory(settings, log, topic):
        provider = MockProvider({})
        def complete(kind, prompt, *args):
            data = json.loads(prompt.split('\nINPUT_JSON\n')[1]);sent.append((kind, data))
            if kind == 'propose_targets':
                value = {'targets': [target.to_dict()]}
            elif kind == 'classify_conflict':
                value = dict(classification='compatible', reason='F(a)')
            elif kind == 'classify_target':
                value = dict(novelty='new_assertion', fidelity='matches', classification='own_thesis', reason='R')
            elif kind == 'map_leaf':
                value = {'t_id': 'open'}
            elif kind == 'propose_cuts':
                value = {'proposals': []}
            else:
                raise AssertionError('unexpected generation: ' + kind)
            return Response(raw(value))
        provider.complete = complete
        return ModelCalls({**settings, 'forward_pass_depth': 0, 'search_concurrency': 1,
                           'model_context_token_bound': 239232}, provider, log,
                          Cache(destination/'cache'), ROOT, topic)
    assert main(['fork-from-freeze', '--source-run', str(source), '--run-dir', str(destination)],
                calls_factory=factory) == 0
    assert snapshot(source) == original
    for name in ('commitments.json', 'frozen-t.json', 'commitment-provenance.json'):
        assert (destination/name).read_bytes() == (source/name).read_bytes()
    assert catalogue_inputs(destination, t) == full
    assert 'propose_targets' in [kind for kind, _ in sent]
    assert not {'build_t', 'build_t_batch', 'judge_symbol_alignment'} & {kind for kind, _ in sent}
    leaf_requests = [(kind, data) for kind, data in sent if kind in ('map_leaf', 'propose_cuts')]
    assert {kind for kind, _ in leaf_requests} == {'map_leaf', 'propose_cuts'}
    for _, data in leaf_requests:
        assert set(target.basis_commitment_ids) <= {c['id'] for c in data['commitments']['commitments']}
        assert data['search_slice']['basis_context']['basis_coverage'] == 1.0
        assert 'commitment_provenance' not in data
        assert data['provenance_sha256'] == full['provenance_sha256']
        assert data['consolidation_disclosure'] == full['consolidation_disclosure']
        assert data['consolidation_disclosure']['sha256'] == full['commitment_provenance']['consolidation']['sha256']
        assert 'checks' not in data['goal_novelty']['consistent_basis']
        assert data['search_slice']['evidence_projection']['goal_novelty_sha256']
        assert 'original_commitments' not in canonical(data)
    events = EventLog(destination/'events.jsonl').read()
    assert sum(e['stage']=='commitments_frozen' for e in events) == 1
    assert any(e['stage']=='awaiting_selection' for e in events)
    evidence = [json.loads(e['payload_json']) for e in events if e['stage']=='search_context_evidence']
    assert evidence and all(e['goal_novelty']['consistent_basis']['checks'] for e in evidence)
    counts = [json.loads(e['payload_json']) for e in events if e['stage']=='search_context_slice']
    assert counts and all(c['decision']=='fits' and c['total_tokens']<=239232 for c in counts)
