"""Offline native CQ/gap probe. Reads frozen artifacts; writes only a new evidence directory."""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import yaml

from ara.bank import load_bank
from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.gaps import detect_gaps
from ara.runtime.logging import EventLog
from ara.runtime.providers import MockProvider, Response
from ara.types import CommitmentSet, Formula, Proposition, RouteGraph, Term


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[1]
    for name in ('commitments.json','frozen-t.json','commitment-provenance.json'):
        shutil.copyfile(args.source/name,args.out/name)
    t=CommitmentSet.from_dict(json.loads((args.out/'commitments.json').read_text()))
    config=yaml.safe_load((root/'config.yaml').read_text())
    config.update(model_context_token_bound=200000,token_cap=100000000,validation_attempts=1)
    provider=MockProvider({})
    # Reuse the production offline counter without transport/credential initialization.
    from ara.runtime.codex_cli import CodexCLIProvider
    from ara.runtime.claude_estimation import CalibrationState
    counter=object.__new__(CodexCLIProvider)
    counter.config={**config, 'model':'gpt-6-luna'}
    counter.calibration_state=CalibrationState()
    provider.estimate=counter.estimate
    provider.initial_context_tokens=counter.initial_context_tokens
    provider.context_output_tokens=counter.context_output_tokens
    gap_candidates={}
    dispatched=[]
    def complete(kind,prompt,*unused):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='answer_cq':
            # Mechanical candidates never establish an answer or missing linking claim.
            result=dict(cq_id=data['question']['id'],answer='Offline candidate retrieval only.',answered=False,supporting_t_ids=[])
            dispatched.append(dict(kind=kind,cq_id=data['question']['id'],retrieval=data['cq_retrieval']))
        elif kind=='propose_targets':
            gap_id=(data.get('resolution_gap') or {}).get('id')
            if gap_id is not None:
                index=gap_candidates.setdefault(gap_id,len(gap_candidates)+1)
                formula=Formula('predicate',name='F',terms=(Term('constant','a'),)*index)
                target=Proposition('offline-'+str(index),'F('+','.join(['a']*index)+')',formula)
            else:
                target=Proposition('offline-r','R',Formula('atom',name='R'))
            result=dict(targets=[target.to_dict()])
            dispatched.append(dict(kind=kind,gap_id=gap_id))
        elif kind=='classify_target':
            result=dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',resolves_gap=True,reason='Offline fake classification, not semantic evidence.')
        else: raise AssertionError(kind)
        return Response({'model':config['model'],'stop_reason':'end_turn',
            'content':[{'type':'text','text':canonical(result)}],
            'usage':{'input_tokens':5,'output_tokens':3}})
    provider.complete=complete
    calls=ModelCalls(config,provider,EventLog(args.out/'events.jsonl'),Cache(args.out/'cache'),root,'')
    vocabulary=calls.search_vocabulary(t)
    detection=detect_gaps(t,vocabulary['symbol_catalogue'],vocabulary['commitment_provenance'])
    bank=load_bank(root/'bank')
    routes=[]
    for path in sorted((args.source/'routes').glob('*.json')):
        graph=RouteGraph.from_dict(json.loads(path.read_text()))
        if graph.status!='OPEN': continue
        questions=[]
        for node in graph.nodes:
            if node.proposal is None: continue
            entry=bank.get(node.proposal.bank_id)
            for q in entry.critical_questions:
                before=len(dispatched)
                calls.answer_cq(q,node.proposal,t)
                request=dispatched[-1] if len(dispatched)>before else None
                # Identical requests may be served by the native cache; each call still logs a counted slice.
                receipt=next(json.loads(e['payload_json']) for e in reversed(calls.log.read()) if e['stage']=='cq_context_slice')
                questions.append(dict(node_id=node.id,bank_id=entry.id,cq_id=q.id,
                    candidate_ids=[r['commitment_id'] for r in receipt['candidates']],
                    scores=receipt['candidates'],total_tokens=receipt['total_tokens'],
                    cached=request is None,support_established=False))
        routes.append(dict(route_id=graph.id,cqs=questions,reason='no_scheme_CQs' if not questions else 'retrieval_leads_only'))
    if detection['gaps']:
        targets=calls.propose_targets(t)
    else:
        calls.log.record('gaps_detected', **{k:v for k,v in detection.items() if k != 'gaps'}, gaps=[],
                         commitments_sha256=vocabulary['commitments_sha256'])
        targets=()  # No gap-resolution request exists; do not dispatch an unrelated generic pool.
    cqs=[q for r in routes for q in r['cqs']]
    result=dict(source=str(args.source),routes=routes,offline_cq_candidates=sum(bool(q['candidate_ids']) for q in cqs),
        cq_total=len(cqs),ctx_max=max((q['total_tokens'] for q in cqs),default=0),
        gaps_found=len(detection['gaps']),gaps_by_kind=dict(Counter(g.kind for g in detection['gaps'])),
        gaps=[g.to_dict() for g in detection['gaps']],set_search=detection['set_search'],
        fake_resolution_candidates=len(gap_candidates),
        fake_resolution_proposal_calls=sum(d['kind']=='propose_targets' and d.get('gap_id') is not None for d in dispatched),
        counter='CodexCLIProvider offline calibration for gpt-6-luna; no credential or transport initialization',
        fake_resolution_targets_retained=sum(t.gap is not None for t in targets),
        disclaimer='Offline fake provider; lexical/symbol candidates are not substantive CQ support or proof of resolution. No paid calls.')
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('routes','gaps')},indent=2))


if __name__=='__main__': main()
