"""Offline native forward census of a verified freeze; no model or network calls."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import socket

from ara.bank import load_bank
from ara.runtime.commitment_provenance import load_commitment_provenance
from ara.runtime.frozen_catalogue import validate_frozen_artifact
from ara.runtime.logging import EventLog
from ara.runtime.novelty import endorsed_papers
from ara.runtime.synthesis import forward_candidates
from ara.types import CommitmentSet


def fake_alignment(out, commitments, catalogue, provenance, path):
    """Exercise the actual pre-freeze pass with explicit, separately retained fake judgments."""
    import yaml
    from ara.runtime.cache import Cache, canonical
    from ara.runtime.calls import ModelCalls
    from ara.runtime.providers import MockProvider, Response
    from ara.runtime.orchestration import prepare_commitments
    root=Path(__file__).resolve().parents[1]
    judgments=json.loads(path.read_text())
    expected={(j['left'],j['right']):j for j in judgments}
    if len(expected)!=len(judgments):
        raise ValueError('duplicate fake alignment pair')
    used=set()
    config=yaml.safe_load((root/'config.yaml').read_text())
    config.update(provider='mock',validation_attempts=1,token_cap=1000000000,
                  cost_cap_usd=1000000000,working_t_token_budget=1000000000)
    provider=MockProvider({})
    calls=ModelCalls(config,provider,EventLog(out/'aligned/events.jsonl'),Cache(out/'aligned/cache'),root,'P')
    def complete(kind,prompt,*args):
        assert kind=='judge_symbol_alignment'
        pair=json.loads(prompt.split('\nINPUT_JSON\n')[1])['candidate']
        key=pair['left']['name'],pair['right']['name']
        if key in expected:
            used.add(key)
        value=expected.get(key,dict(left=key[0],right=key[1],relation='unrelated',
            reason='Offline fake default; no semantic judgment made.'))
        return Response(dict(model=config['model'],stop_reason='end_turn',
            content=[dict(type='text',text=canonical(value))],usage=dict(input_tokens=1,output_tokens=1)))
    provider.complete=complete
    calls.build_t=lambda *_:commitments
    calls.log.record('offline_fake_alignment',source=str(path.resolve()),judgments=judgments,
        note='Explicit synthetic judgments. Generous replay caps and fake accounting; no semantic or live-budget proof.')
    calls.log.record('build_t_merged',commitments=commitments.to_dict(),symbols=catalogue['symbols'],provenance=provenance['commitments'])
    result=prepare_commitments(calls,load_bank(root/'bank'),'P','P')
    if used!=set(expected):
        raise ValueError('fake alignment pair not selected by native ranking')
    final=validate_frozen_artifact(json.loads((out/'aligned/frozen-t.json').read_text()),result)
    meta=load_commitment_provenance(out/'aligned',result,final)
    receipt=meta.get('alignment')
    return result,meta,dict(status=receipt['status'],refusal_reason=receipt['refusal_reason'],
        fake_judgments=judgments,selected_pairs=len(receipt['candidates']),
        mapping={a:b for a,b in receipt['mapping'].items() if a!=b},
        bridge_ids=[id for id,row in meta['commitments'].items() if row['stance']=='model_alignment'],
        symbols_before=len(catalogue['symbols']),symbols_after=len(final['symbols']))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--fake-alignments',type=Path,help='External JSON judgments for a disclosed offline fake aligner; all other candidates are unrelated.')
    parser.add_argument('--depth',type=int,default=2)
    parser.add_argument('--node-cap',type=int,default=500)
    args=parser.parse_args()
    def refuse(*unused,**kwargs):
        raise AssertionError('offline census prohibits network access')
    socket.socket.connect=refuse
    args.out.mkdir(parents=True,exist_ok=False)
    names=('commitments.json','frozen-t.json','commitment-provenance.json')
    hashes={name:hashlib.sha256((args.source/name).read_bytes()).hexdigest() for name in names}
    for name in names:
        shutil.copyfile(args.source/name,args.out/name)
    t=CommitmentSet.from_json((args.out/'commitments.json').read_text())
    catalogue=validate_frozen_artifact(json.loads((args.out/'frozen-t.json').read_text()),t)
    provenance=load_commitment_provenance(args.out,t,catalogue)
    alignment = None
    if args.fake_alignments:
        t,provenance,alignment = fake_alignment(args.out, t, catalogue, provenance, args.fake_alignments)
    result=forward_candidates(t,provenance,load_bank(Path(__file__).resolve().parents[1]/'bank'),
        EventLog(args.out/'events.jsonl'),depth=args.depth,node_cap=args.node_cap)
    summary=dict(**result,forward_candidates=len(result['candidates']),commitments=len(t.commitments),
        endorsed_papers=len(endorsed_papers(t,provenance)),fake_alignment=alignment,source=str(args.source),source_sha256=hashes,
        disclaimer='Bounded native formal candidates only; fake judgments when supplied prove plumbing, not semantic equivalence, originality or exhaustive coverage. No paid calls.')
    assert all(hashlib.sha256((args.source/name).read_bytes()).hexdigest()==sha and
               (args.source/name).read_bytes()==(args.out/name).read_bytes() for name,sha in hashes.items())
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('candidates','source_sha256')},indent=2))


if __name__=='__main__':
    main()
