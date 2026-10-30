"""Admit a paper-owned, unformalized target using an authenticated source freeze."""
from pathlib import Path
from hashlib import sha256, file_digest
import json
import re
import shutil

from ara.bank import load_bank
from ara.runtime.cache import canonical, digest
from ara.runtime.calls import require
from ara.runtime.freeze_fork import verified_freeze_prefix, write_freeze_prefix
from ara.runtime.proposal import validated_packet
from ara.types import Proposition, RouteGraph, RouteNode

ROOT_RESERVE = 6_000_000_000
SHM_RESERVE = 2_000_000_000
GROWTH_RESERVE = 1_000_000_000
AUTHORITY = 'paper_owned_target_not_search_result'


def file_sha256(path):
    with Path(path).open('rb') as stream:
        return file_digest(stream,'sha256').hexdigest()


def screen_request(config, root, value):
    """Use the native provider output screens without creating ModelCalls/canaries."""
    from ara.runtime.cli import make_provider
    from ara.runtime.construction_stages import dispatch_settings
    settings = [config]
    for kind in ('write_essay', 'audit_essay'):
        _, overrides, selected = dispatch_settings(config, kind)
        if overrides and selected not in settings:
            settings.append(selected)
    for setting in settings:
        provider = make_provider(setting, root)
        if hasattr(provider, 'scan_output'):
            provider.scan_output(value)


def capacity(destination, root, projected_bytes):
    destination = Path(destination).resolve()
    parent = destination
    while not parent.exists():
        parent = parent.parent
    root_free = shutil.disk_usage('/').free
    free = shutil.disk_usage(parent).free
    reserve = SHM_RESERVE if destination.is_relative_to('/dev/shm') else ROOT_RESERVE
    return dict(root_free_bytes=root_free, root_reserve_bytes=ROOT_RESERVE,
                destination_free_bytes=free, destination_reserve_bytes=reserve,
                projected_bytes=projected_bytes,
                fits=root_free >= ROOT_RESERVE and free-projected_bytes >= reserve)


def admit(source, destination, request, root, *, plan_only=False):
    require(isinstance(request, dict) and set(request)=={
        'candidate_id', 'source_freeze_hash', 'proposal', 'grounding_files'}, 'invalid proposal admission fields')
    candidate=request['candidate_id']
    require(isinstance(candidate,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,100}',candidate),
            'invalid proposal candidate id')
    snapshot=verified_freeze_prefix(source,load_bank(Path(root)/'bank'))
    require(request['source_freeze_hash']==snapshot['freeze_hash'], 'proposal source freeze binding mismatch')
    proposal=request['proposal']
    require(isinstance(proposal,dict) and 'route_id' not in proposal, 'admission must not supply a route')
    require(isinstance(proposal.get('target_text'),str) and proposal['target_text'].strip(), 'proposal target text required')
    files=request['grounding_files']
    require(isinstance(files,list), 'grounding files must be a list')
    for item in files:
        require(isinstance(item,dict) and set(item)=={'path','sha256'}, 'invalid grounding file binding')
        require(file_sha256(item['path'])==item['sha256'], 'grounding file hash mismatch')
    # This target has no formula, supports, inferred edges, assumptions, or H authority.
    identity=digest(canonical(request))
    target=Proposition('paper:'+candidate,proposal['target_text'])
    route=RouteGraph('paper:'+identity[:24], 'proposal-root',
                     (RouteNode('proposal-root',target,'leaf'),), 'OPEN', ('proposal-root',))
    packet={**proposal,'route_id':route.id}
    prepared=validated_packet(route,packet,snapshot['events'])
    screen_request(snapshot['run']['config'],root,dict(request=request,proposal=prepared))
    imported=len(snapshot['prefix'])+sum(len(v) for v in snapshot['artifacts'].values())+65*len(snapshot['rows'])
    # Full prefix, methodology/export duplication, and one GB for fresh writer receipts.
    space=capacity(destination,root,3*imported+GROWTH_RESERVE)
    summary=dict(candidate_id=candidate,route_id=route.id,authority=AUTHORITY,
                 request_sha256=identity,source_run=str(snapshot['source']),
                 source_freeze_hash=snapshot['freeze_hash'],
                 prefix_sha256=sha256(snapshot['prefix']).hexdigest(),import_bytes=imported,
                 new_freeze=False,h_admitted=False,search_launched=False,inferences=0,
                 status='ready' if space['fits'] else 'held_capacity',capacity=space)
    if plan_only:
        return summary
    require(space['fits'], 'proposal admission held: projected disk reserve')
    log,run,_=write_freeze_prefix(snapshot,destination)
    config={**run['config'],'cache_dir':str(Path(destination).resolve()/'candidate-cache'),
            'essay_min_words':packet['minimum_words'],'essay_word_limit':min(6000,run['config']['essay_word_limit'])}
    log.record('freeze_fork_configuration',config=config)
    log.human('admit-proposal',canonical(request))
    log.record('proposal_target_admitted',**summary,request=request,graph=route.to_dict())
    log.record('route',graph=route.to_dict(),authority=AUTHORITY,search_launched=False,inferences=0)
    log.record('essay_proposal_mode',**prepared)
    log.record('awaiting_selection',route_ids=[route.id],authority=AUTHORITY)
    (Path(destination)/'proposal-admission.json').write_text(canonical(summary)+'\n')
    return summary


def check_selection_capacity(events, run_dir, root):
    if not any(e['stage']=='proposal_target_admitted' for e in events):
        return
    size=(Path(run_dir)/'events.jsonl').stat().st_size
    space=capacity(run_dir,root,2*size+GROWTH_RESERVE)
    require(space['fits'], 'proposal selection held: projected disk reserve')


def promote_queue_entry(entry, run_dir):
    """Only a verified native receipt can turn held metadata into a selectable row."""
    from ara.runtime.logging import EventLog
    require(entry.get('status')=='OPEN-proposal-pending' and entry.get('route_id') is None
            and entry.get('dispatch_hold')=='awaiting_native_grounding_admission', 'candidate is not held grounding')
    events=EventLog(Path(run_dir)/'events.jsonl').read()
    admissions=[json.loads(e['payload_json']) for e in events if e['stage']=='proposal_target_admitted']
    require(len(admissions)==1, 'missing unique proposal admission')
    admission=admissions[0]
    require(admission['candidate_id']==entry['id'] and admission['source_run']==str(Path(entry['run_dir']).resolve())
            and admission['authority']==AUTHORITY, 'candidate admission binding mismatch')
    request=admission['request']
    require(any(f['path']==entry['grounding_packet'] and file_sha256(f['path'])==f['sha256']
                for f in request['grounding_files']), 'candidate grounding binding mismatch')
    route=RouteGraph.from_dict(admission['graph'])
    require(route.to_dict()==next(json.loads(e['payload_json'])['graph'] for e in events if e['stage']=='route'),
            'admitted target route mismatch')
    from ara.runtime.proposal import from_events
    require(from_events(events,route.id)==validated_packet(route,{**request['proposal'],'route_id':route.id},events),
            'admitted proposal mismatch')
    return {**entry,'status':'OPEN-proposal','route_id':route.id,'source_run':entry['run_dir'],
            'run_dir':str(Path(run_dir).resolve()),'dispatch_hold':None,'reuse_admitted_run':True}
