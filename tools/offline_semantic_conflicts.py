"""Offline real-freeze semantic-pair plumbing; synthetic judgments are not evidence."""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import yaml
from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.logging import EventLog
from ara.runtime.providers import MockProvider, Response
from ara.runtime.search_alignment import symbols
from ara.types import CommitmentSet, Formula, Proposition, Term


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    root=Path(__file__).resolve().parents[1]
    for name in ('commitments.json','frozen-t.json','commitment-provenance.json'):
        shutil.copyfile(args.source/name,args.out/name)
    t=CommitmentSet.from_json((args.out/'commitments.json').read_text())
    config=yaml.safe_load((root/'config.yaml').read_text())
    config.update(token_cap=100000000,cost_cap_usd=1000,validation_attempts=1)
    provider=MockProvider({})
    from ara.runtime.codex_cli import CodexCLIProvider
    from ara.runtime.claude_estimation import CalibrationState
    counter=object.__new__(CodexCLIProvider)
    counter.config={**config,'model':'gpt-6-luna'}
    counter.calibration_state=CalibrationState()
    provider.estimate=counter.estimate
    provider.initial_context_tokens=counter.initial_context_tokens
    provider.context_output_tokens=counter.context_output_tokens
    labels=('contradicts','in_tension','compatible','unrelated')
    dispatched=[]
    arity=max((s[2] for c in t.commitments for s in symbols(c.formula) if s[0]=='F'),default=0)+1
    formula=Formula('predicate',name='F',terms=(Term('constant','a'),)*arity)
    def complete(kind,prompt,*unused):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='classify_conflict':
            index=sum(row['kind']==kind for row in dispatched)
            result=dict(classification=labels[index%4],reason='Offline synthetic classification; no semantic evidence.')
            dispatched.append(dict(kind=kind,commitment_ids=[p['commitment_id'] for p in data['pair']],**result))
        elif kind=='propose_targets':
            assert data['resolution_gap']['kind']=='semantic_conflict'
            result=dict(targets=[Proposition('offline','F('+','.join(['a']*arity)+')',formula).to_dict()])
            dispatched.append(dict(kind=kind,gap_id=data['resolution_gap']['id']))
        elif kind=='classify_target':
            result=dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',resolves_gap=True,
                        reason='Offline fake judgment, not substantive evidence.')
        else:raise AssertionError(kind)
        return Response(dict(model=config['model'],stop_reason='end_turn',content=[dict(type='text',text=canonical(result))],
                             usage=dict(input_tokens=5,output_tokens=3)))
    provider.complete=complete
    calls=ModelCalls(config,provider,EventLog(args.out/'events.jsonl'),Cache(args.out/'cache'),root,'')
    detection=calls.discover_gaps(t)
    semantic=[g for g in detection['gaps'] if g.kind=='semantic_conflict']
    targets=calls.propose_gap_targets(t,semantic[:1],1)
    receipts=[(e['stage'],json.loads(e['payload_json'])) for e in calls.log.read()]
    ranked=next(p for stage,p in receipts if stage=='semantic_pairs_ranked')
    counts=[p for stage,p in receipts if stage=='context_admission' and p['kind']=='classify_conflict']
    summary=dict(source=str(args.source),eligible_pairs=ranked['eligible_pairs'],semantic_pairs=len(ranked['pairs']),
        pair_limit=ranked['limit'],classifier_dispatches=sum(d['kind']=='classify_conflict' for d in dispatched),
        synthetic_classifications=dict(Counter(d['classification'] for d in dispatched if d['kind']=='classify_conflict')),
        synthetic_semantic_gaps=len(semantic),representative_resolution_candidates=len(targets),
        ctx_max=max((p['input_tokens']+p['output_tokens'] for p in counts),default=0),
        pairs=ranked['pairs'],gap_examples=[g.to_dict() for g in semantic[:3]],
        disclaimer='Fake provider and classifier: verifies plumbing only, not actual disagreement or successful resolution. No paid calls.')
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('pairs','gap_examples')},indent=2))


if __name__=='__main__':main()
