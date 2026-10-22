"""Offline replay of ignored extraction receipts through the native response boundary.

No recorded content belongs in this module or fixtures. Outputs remain under runs/.
Replay validates each historical request independently; it does not predict a
corrected model response or a completed paper. Network access is forbidden.
"""
from __future__ import annotations

import argparse
from dataclasses import fields
import json
from pathlib import Path
import socket
import subprocess

from ara.runtime.cache import Cache, canonical, digest
from ara.runtime.calls import InvalidOutput, ModelCalls, Rejected, require
from ara.runtime.extraction import ExtractedItem, load_papers
from ara.runtime.logging import EventLog, read_log
from ara.runtime.providers import Response
from ara.types import TokenUsage

ROOT = Path(__file__).resolve().parents[1]


class NeedsResponse(Exception):
    pass


class RecordedProvider:
    model = 'claude-opus-5'

    def __init__(self, raw):
        self.raw = raw
        self.used = False

    def estimate(self, kind, prompt, schema, maximum):
        # Replay tests acceptance, not live token counting/admission or spending.
        return TokenUsage(input_tokens=1, output_tokens=maximum)

    def complete(self, kind, prompt, schema, maximum):
        if self.used:
            raise NeedsResponse('replay has no new model correction')
        self.used = True
        return Response(self.raw)


class ReplayCalls(ModelCalls):
    def __init__(self, *args, request, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.seeded = False

    def _call_once(self, kind, inputs, check=None, *, attempt=1):
        if self.request.get('mode') == 'targeted_correction' and not self.seeded:
            self.seeded = True
            # Recreate the historical rejected candidate, without inventing a
            # provider response or charging it. The logged patch is then checked
            # by the native merge and whole-graph validator.
            raise InvalidOutput(self.request['validation_error'], {
                'error': self.request['validation_error'],
                'rejected_response': canonical(self.request['candidate'])})
        if self.provider.used:
            raise NeedsResponse('next correction requires a new response')
        return super()._call_once(kind, inputs, check, attempt=attempt)


def replay(log_paths, destination, corrections=None):
    destination = destination.resolve()
    destination.relative_to(ROOT / 'runs')
    destination.mkdir(parents=True, exist_ok=False)
    rows = []
    excluded = []
    seen = set()
    for path in log_paths:
        path = path.resolve()
        if subprocess.run(['git', '-C', str(path.parent), 'check-ignore', '-q', str(path)]).returncode:
            raise ValueError('real replay inputs must be gitignored')
        events = [r['event'] for r in read_log(path)]
        start = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'extraction_started')
        config = start['config']
        selected = tuple({json.loads(e['prompt'].split('\nINPUT_JSON\n')[1])['source_id']
                          for e in events if e['stage'] == 'extract_paper' and e['label'] == 'MODEL'
                          and '\nINPUT_JSON\n' in e['prompt']})
        papers = {p.source_id: p for p in load_papers(Path(start['manifest']), Path(start['fulltext_dir']), selected)}
        for index, event in enumerate(events):
            if event['stage'] != 'extract_paper' or event['label'] != 'MODEL':
                continue
            identity = digest(canonical(event))
            if identity in seen:
                continue
            seen.add(identity)
            if '\nINPUT_JSON\n' not in event['prompt'] or event['response'] is None:
                excluded.append(dict(log=str(path), event=index,
                                     reason='schema_preflight' if '\nINPUT_JSON\n' not in event['prompt']
                                     else 'no_provider_response'))
                continue
            request = json.loads(event['prompt'].split('\nINPUT_JSON\n')[1])
            paper = papers[request['source_id']]
            if paper.pdf_sha256 != request.get('pdf_sha256'):
                raise ValueError('replay source PDF hash differs from recorded request')
            source_pages = {p.page: p.text for p in paper.pages}
            if any(source_pages.get(p['page']) != p['text'] for p in request.get('pages', [])):
                raise ValueError('replay page text differs from recorded request')
            inputs = {k: v for k, v in request.items() if k not in
                      ('topic', 'candidate', 'validation_error', 'original_mode')}
            if request.get('mode') == 'targeted_correction':
                inputs['mode'] = request.get('original_mode')
            ids = request.get('evidence_page_ids', [p['page'] for p in request.get('pages', [])])
            pages = tuple(p for p in paper.pages if p.page in ids)
            names = {f.name for f in fields(ExtractedItem)}
            existing = tuple(ExtractedItem(**{k: v for k,v in item.items() if k in names})
                             for r in request.get('ranges', []) for item in r['items'])
            directory = destination / f'{path.parent.name}-{index}'
            log = EventLog(directory / 'events.jsonl')
            cfg = {**config, 'token_cap': 1000000000, 'cost_cap_usd': 1000000,
                   'extraction_cost_cap_usd': 1000000}
            if corrections is not None:
                cfg['extraction_targeted_corrections'] = corrections
            calls = ReplayCalls(cfg, RecordedProvider(json.loads(event['response'])), log,
                                Cache(directory/'cache'), ROOT, request.get('topic', ''), request=request)
            def validate_context(context):
                require(set(context['pages']) <= {p.page for p in paper.readable_pages},
                        'reconciliation requests unread page')
                # All existing evidence IDs can be requested, not only the window.
                all_ids = {i['id'] for prior in events[:index] if prior['stage'] == 'extract_paper'
                           and prior['label'] == 'MODEL'
                           for r in json.loads(prior['prompt'].split('\nINPUT_JSON\n')[1]).get('ranges', [])
                           for i in r['items']} | {i.id for i in existing}
                require(set(context['evidence_ids']) <= all_ids, 'reconciliation requests unknown evidence')
            outcome, reason = 'accepted', None
            try:
                calls._extraction_response(paper, inputs, pages, 'replay', existing,
                                           allow_incomplete=True, validate_context=validate_context)
            except NeedsResponse:
                outcome = 'correction'
                correction_records = [json.loads(e['payload_json']) for e in log.read()
                               if e['stage'] == 'extraction_targeted_correction']
                reason = correction_records[-1]['reason']
            except Rejected as exc:
                outcome, reason = 'terminal', str(exc)
                if 'provider stop: max_tokens' in reason and len(pages) > 1:
                    outcome = 'subdivision'
            normalized = [json.loads(e['payload_json']) for e in log.read()
                          if e['stage'] == 'extraction_normalized']
            if outcome == 'accepted' and normalized:
                outcome = 'normalized'
            row = dict(log=str(path), event=index, source_id=paper.source_id,
                       mode=request.get('mode', 'range'), pages=ids,
                       historical_status=json.loads(event['payload_json'])['status'],
                       outcome=outcome, reason=reason, normalizations=normalized)
            rows.append(row)
    counts = {kind: sum(r['outcome'] == kind for r in rows) for kind in
              ('accepted', 'normalized', 'correction', 'subdivision', 'terminal')}
    result = dict(responses=len(rows), counts=counts, rows=rows, excluded=excluded)
    (destination/'summary.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(responses=len(rows), counts=counts)))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--corrections', type=int)
    args = parser.parse_args()
    def forbidden(*args, **kwargs):
        raise AssertionError('network forbidden during replay')
    socket.socket.connect = forbidden
    replay(args.log, args.output, args.corrections)


if __name__ == '__main__':
    main()
