"""Linked report evidence: shared event bodies and lossless per-run projections."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

from ara.runtime.cache import canonical, digest


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


class EvidenceFiles:
    def __init__(self, destination):
        self.destination = destination
        self.events = {}

    def write(self, name, value):
        write_json(self.destination / name, value)
        return name

    def records(self, run, prefix):
        imported = set()
        for row in run['records']:
            if row['event']['stage'] == 'extraction_provenance_import':
                count = json.loads(row['event']['payload_json'])['records']
                imported.update(range(row['seq'] + 1, row['seq'] + 1 + count))
        envelopes = []
        for row in run['records']:
            event = row['event']
            event_hash = digest(canonical(event))
            if event_hash not in self.events:
                filename = self.write('events/' + event_hash + '.json', event)
                self.events[event_hash] = dict(event_hash=event_hash, file=filename,
                    stage=event['stage'], label=event['label'], timestamp=event['timestamp'],
                    original_in=[], imported_by=[], occurrences=[])
            entry = self.events[event_hash]
            group = 'imported_by' if row['seq'] in imported else 'original_in'
            if prefix not in entry[group]:
                entry[group].append(prefix)
            entry['occurrences'].append(dict(run=prefix, seq=row['seq'], chain_hash=row['hash']))
            envelopes.append({**{k: v for k, v in row.items() if k != 'event'}, 'event_ref': entry['file']})
        return self.write(prefix + '-events.json', envelopes)

    def artifacts(self, run, prefix):
        entries = []
        for i, artifact in enumerate(run['artifacts']):
            entry = {k: v for k, v in artifact.items() if k != 'content'}
            source = Path(run['directory']) / artifact['path']
            if artifact.get('status') != 'symlink not followed':
                # Numeric names prevent source filenames from becoming report URLs.
                name = f'{prefix}/artifacts/{i}{source.suffix}'
                target = self.destination / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
                entry['file'] = name
            entries.append(entry)
        return self.write(prefix + '-artifacts.json', entries), entries

    def projection(self, value, run):
        """Compact event views point to the sole original body instead of copying it."""
        if isinstance(value, dict):
            if {'seq', 'timestamp', 'stage', 'label', 'payload'} <= value.keys():
                # Sidecar receipts have their own seq space and stay in trace files.
                if value['stage'] != 'search_trace':
                    row = run['records'][value['seq']]
                    return {**{k: v for k, v in value.items() if k not in ('payload', 'decision')},
                            'event_ref': 'events/' + digest(canonical(row['event'])) + '.json'}
            return {k: self.projection(v, run) for k, v in value.items()}
        if isinstance(value, list):
            return [self.projection(v, run) for v in value]
        return value
