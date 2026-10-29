"""Rebuild accepted ranges from pinned MODEL receipts, without provider calls."""
from dataclasses import replace
import copy
import json

from ara.runtime.cache import canonical, digest
from ara.runtime.extraction import (ExtractedItem, PaperExtraction, V4_PROMPT_SHA256, V5_PRE_UNION_PROMPT_SHA256, V5_UNION_PROMPT_SHA256,
                                   extraction_acceptance_identity)
from ara.runtime.providers import Response


class OfflineExtractionProvider:
    """Retain provenance identity while making generation/counting impossible."""
    def __init__(self, config):
        self.config = config
        self.model = config['model']

    def model_for(self, kind):
        from ara.runtime.providers import stage_settings
        return stage_settings(self.config, kind)['model']

    def estimate(self, *args, **kwargs):
        raise RuntimeError('offline extraction cannot count or dispatch requests')

    def complete(self, *args, **kwargs):
        raise RuntimeError('offline extraction cannot count or dispatch requests')


def is_thin(pages, items):
    return len(pages) >= 8 and len(items) <= max(1, len(pages) // 10)


def accepted_ranges(events, papers, config, root, log):
    from ara.runtime.calls import (ModelCalls, normalize_extraction, extraction_defaults,
                                   normalize_patch_ids, merge_extraction_patch, prune_extraction_relations, require)
    selected = {p.source_id: p for p in papers}
    expected = extraction_acceptance_identity(config, root)
    results = {}
    cfg = None
    windows = {}
    accepted = {}
    mappings = {}
    seen = set()
    refined_pages = {}
    # No generation/cache boundary is used. Only the native pure response check
    # runs; source text and all referenced accepted evidence are verified first.
    checker = ModelCalls.__new__(ModelCalls)
    checker.root = root
    checker.config = {**config, 'extraction_require_inference': False}
    for event in events:
        payload = json.loads(event['payload_json'])
        stage = event['stage']
        if stage == 'extraction_started' or (stage == 'extraction_batch_started' and 'config' in payload):
            cfg = payload['config']
        elif stage == 'extraction_paper_started':
            source = payload['source_id']
            accepted[source], mappings[source] = {}, {}
        elif stage in ('extraction_range', 'extraction_reconciliation_window'):
            windows[payload['source_id']] = payload
        elif stage == 'extraction_thin_retry':
            refined_pages.setdefault(payload['source_id'], set()).update(payload['pages'])
        structural_repair = stage == 'extraction_structure_repaired' and payload.get('status') == 'accepted'
        if not structural_repair and (stage != 'extract_paper' or event['label'] != 'MODEL' or payload.get('status') != 'accepted'):
            continue
        event_id = digest(canonical(event))
        if event_id in seen or (not structural_repair and (not event.get('response') or '\nINPUT_JSON\n' not in event['prompt'])):
            continue
        seen.add(event_id)
        request = payload['inputs'] if structural_repair else json.loads(event['prompt'].split('\nINPUT_JSON\n')[1])
        source = request['source_id']
        if source not in selected or cfg is None or source not in windows:
            continue
        paper = selected[source]
        previous = extraction_acceptance_identity(cfg, root)
        if any(previous[k] != expected[k] for k in ('provider', 'stage', 'require_inference')):
            log.record('extraction_range_salvage_excluded', source_id=source, receipt_hash=event_id, reason='Incompatible effective extraction profile.')
            continue
        if structural_repair:
            require(previous == expected and payload['policy'] == 'terminal-edge-pruning-v1',
                    'incompatible structural repair receipt')
        template = (root / 'prompts' / 'extract_paper.txt').read_text() if structural_repair else event['prompt'].split('\nLOCAL_RESPONSE_SCHEMA')[0]
        if digest(template) not in (V4_PROMPT_SHA256, V5_PRE_UNION_PROMPT_SHA256, V5_UNION_PROMPT_SHA256, expected['prompt_sha256']):
            # Older, unreviewed contracts cannot qualify through a version label.
            log.record('extraction_range_salvage_excluded', source_id=source, receipt_hash=event_id, reason='Unreviewed predecessor prompt contract.')
            continue
        if request.get('pdf_sha256') != paper.pdf_sha256:
            log.record('extraction_range_salvage_excluded', source_id=source, receipt_hash=event_id, reason='Source PDF hash mismatch.')
            continue
        source_text = {p.page: p.text for p in paper.readable_pages}
        if any(source_text.get(p['page']) != p['text'] for p in request.get('pages', [])):
            raise ValueError('salvage source page text mismatch')
        if request.get('record', json.loads(paper.record_json)) != json.loads(paper.record_json):
            raise ValueError('salvage source record mismatch')
        original = accepted.setdefault(source, {})
        mapping = mappings.setdefault(source, {})
        existing = []
        for group in request.get('ranges', []):
            for item in group['items']:
                if original.get(item['id']) != item:
                    raise ValueError('salvage reference lacks accepted evidence receipt')
                existing.append(ExtractedItem(**{k:v for k,v in item.items() if k != 'citation'}))
        if structural_repair:
            from ara.runtime.validation import validate_local
            candidate = payload['candidate']
            require(digest(canonical(candidate)) == payload['candidate_hash'], 'repair candidate hash mismatch')
            validate_local(checker.response_schema('extract_paper', request), candidate, config)
            raw, removals, total = prune_extraction_relations(candidate, existing)
            require(bool(removals) and len(removals) * 4 <= total, 'repair share exceeds 25%')
            require(raw == payload['repaired'] and len(removals) == payload['removed'] and total == payload['total'],
                    'structural repair receipt mismatch')
            require(any(i['kind'] == 'inference' for i in raw['items']), 'repaired range requires at least one inference')
        else:
            raw = json.loads(Response(json.loads(event['response'])).text())
        if cfg.get('provider') == 'codex_cli':
            from ara.runtime.codex_schema import normalize_output
            raw = normalize_output(checker.response_schema('extract_paper', request), raw, config)
        normalize_extraction(raw)
        inputs = copy.deepcopy(request)
        if request.get('mode') == 'targeted_correction':
            candidate = copy.deepcopy(request['candidate'])
            if cfg.get('provider') == 'codex_cli':
                candidate = normalize_output(checker.response_schema('extract_paper', request), candidate, config)
            normalize_extraction(candidate)
            normalize_patch_ids(raw, candidate)
            raw = merge_extraction_patch(candidate, raw)
            inputs['mode'] = inputs.get('original_mode')
            for key in ('candidate', 'original_mode', 'validation_error'):
                inputs.pop(key, None)
        extraction_defaults(raw)
        window = windows[source]
        prefix = window['prefix']
        ids = request.get('evidence_page_ids', [p['page'] for p in request.get('pages', [])])
        pages = tuple(p for p in paper.readable_pages if p.page in ids)
        result, gaps, _ = checker._extraction_response(paper, inputs, pages, prefix, tuple(existing),
                                                       allow_incomplete=True, recorded_data=raw)
        turn = int(prefix.removeprefix('joined') or 1) if prefix.startswith('joined') else 1
        obligations = [dict(id=f'{source}:{prefix}:turn:{turn}:gap:{n}', source_id=source,
                            range=prefix, turn=turn, pages=ids, description=g['description']) for n,g in enumerate(gaps)]
        # Preserve every accepted item from distinct attempts. Namespaces avoid
        # inventing equivalence or overwriting an earlier item with the same ID.
        for item in json.loads(canonical(result.to_dict()))['items']:
            original[item['id']] = item
            mapping[item['id']] = f'{source}:salvage:{event_id[:16]}:{item["id"]}'
        def mapped(id):
            return mapping[id]
        converted = tuple(replace(i, id=mapped(i.id),
            premise_ids=tuple(map(mapped, i.premise_ids)), conclusion_id=mapped(i.conclusion_id) if i.conclusion_id else None,
            qualification_ids=tuple(map(mapped, i.qualification_ids)), applies_to=tuple(map(mapped, i.applies_to))) for i in result.items)
        # Obligation identities are namespaced by the batch, retaining cross-pass
        # distinctions. Historical resolutions are mapped through accepted IDs.
        batch = mappings[source].setdefault('__batch__', event_id[:16])
        def obligation_id(id): return f'{source}:salvage:{batch}:{id}'
        obligations = [{**o, 'id': obligation_id(o['id'])} for o in obligations]
        resolutions = [{**r, 'obligation_id': obligation_id(r['obligation_id']),
                        'evidence_ids': [mapped(i) for i in r['evidence_ids']]} for r in json.loads(result.resolutions_json)]
        result = replace(result, items=converted, obligations_json=canonical(obligations),
                         resolutions_json=canonical(resolutions))
        results.setdefault(source, []).append(dict(result=result, pages=ids if inputs.get('mode') != 'reconcile_ranges' else [],
                                                    receipt=event_id, refined='-refine' in prefix))
        log.record('extraction_range_revalidated', source_id=source, receipt_hash=event_id,
                   pages=ids, items=len(converted), graph_hash=digest(canonical(result.to_dict())))
    for source, entries in results.items():
        for entry in entries:
            if set(entry['pages']) <= refined_pages.get(source, set()):
                entry['refined'] = True
    return results
