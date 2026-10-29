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


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
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
    result=forward_candidates(t,provenance,load_bank(Path(__file__).resolve().parents[1]/'bank'),
        EventLog(args.out/'events.jsonl'),depth=args.depth,node_cap=args.node_cap)
    summary=dict(**result,forward_candidates=len(result['candidates']),commitments=len(t.commitments),
        endorsed_papers=len(endorsed_papers(t,provenance)),source=str(args.source),source_sha256=hashes,
        disclaimer='Bounded native formal candidates only; no model rendering, semantic novelty or exhaustive census claimed. No paid calls.')
    assert all(hashlib.sha256((args.source/name).read_bytes()).hexdigest()==sha and
               (args.source/name).read_bytes()==(args.out/name).read_bytes() for name,sha in hashes.items())
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('candidates','source_sha256')},indent=2))


if __name__=='__main__':
    main()
