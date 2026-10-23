"""Bounded native reports retain full placeholder evidence in linked files."""
import json
from html.parser import HTMLParser
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.logging import EventLog, read_log
from ara.runtime.provenance import checkpoint, import_receipts
from ara.runtime.report import generate_report
from test_report import fixture


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == 'href' and value and not value.startswith('#'):
                self.paths.append(value.split('#')[0])


def test_large_imported_history_is_external_and_unique(tmp_path, monkeypatch):
    import ara.runtime.report_render as rendering
    monkeypatch.setattr(rendering.shutil, 'which', lambda _: None)
    first = fixture(tmp_path/'first')
    large = 'PΩ<&>' * 400_000
    first.record('placeholder_detail', content=large)
    (first.path.parent/'large.txt').write_text(large)
    second = EventLog(tmp_path/'second/events.jsonl')
    import_receipts(second, tuple(first.read()), checkpoint(first.path))
    second.record('placeholder_end', content='Q')
    out = tmp_path/'out'
    generate_report([first.path.parent, second.path.parent], out)
    assert (out/'report.html').stat().st_size < 15_000_000
    html = (out/'report.html').read_text()
    assert large[:10_000] not in html
    data = json.loads((out/'data.json').read_text())
    index = json.loads((out/data['events_index']).read_text())
    expected = {digest(canonical(r['event'])): r['event'] for log in (first, second) for r in read_log(log.path)}
    assert {e['event_hash'] for e in index} == set(expected)
    assert len(index) == len(expected)
    for entry in index:
        assert json.loads((out/entry['file']).read_text()) == expected[entry['event_hash']]
    original = next(e for e in index if expected[e['event_hash']]['stage'] == 'placeholder_detail')
    assert original['imported_by'] == ['run-1']
    assert original['original_in'] == ['run-0']
    for run, log in zip(data['runs'], (first, second)):
        envelopes = json.loads((out/run['events_file']).read_text())
        restored = [{**{k:v for k,v in r.items() if k != 'event_ref'},
                     'event': json.loads((out/r['event_ref']).read_text())} for r in envelopes]
        assert restored == read_log(log.path)
    artifacts = json.loads((out/data['runs'][0]['artifacts_file']).read_text())
    artifact = next(a for a in artifacts if a['path'] == 'large.txt')
    assert (out/artifact['file']).read_text() == large
    parser = Links(); parser.feed(html)
    assert parser.paths and all((out/p).is_file() for p in parser.paths)
    assert 'Imported by' in html


def test_section_budget_keeps_paper_items_and_explicit_links(tmp_path, monkeypatch):
    import ara.runtime.report_render as rendering
    monkeypatch.setattr(rendering.shutil, 'which', lambda _: None)
    monkeypatch.setattr(rendering, 'SECTION_BYTES', 2000, raising=False)
    log = fixture(tmp_path/'input')
    items = [dict(id=f'p{i}', text='P' * 4000, kind='claim') for i in range(25)]
    log.record('extraction_outcome', source_id='paper-p', status='partial', items=items, reason='Q')
    out=tmp_path/'out'; generate_report([log.path.parent], out)
    html=(out/'report.html').read_text()
    assert 'HTML view truncated' in html and 'see file' in html
    data=json.loads((out/'data.json').read_text())
    run=data['runs'][0]
    paper=next(p for p in run['extraction']['papers'] if p['source_id']=='paper-p')
    full=json.loads((out/paper['file']).read_text())
    assert full['outcome']['items']==items
    assert len(html.encode()) < 50_000


def test_global_budget_keeps_all_run_files(tmp_path, monkeypatch):
    import ara.runtime.report_render as rendering
    monkeypatch.setattr(rendering.shutil, 'which', lambda _: None)
    monkeypatch.setattr(rendering, 'HTML_BYTES', 25_000)
    logs = [fixture(tmp_path/f'input-{i}') for i in range(8)]
    out=tmp_path/'out'
    generate_report([log.path.parent for log in logs], out)
    assert (out/'report.html').stat().st_size < 25_000
    manifest=json.loads((out/'data.json').read_text())
    assert len(manifest['runs']) == 8 and manifest['html_truncated_sections']
    for run in manifest['runs']:
        assert all((out/name).is_file() for name in run['sections'].values())
        assert all((out/p['file']).is_file() for p in run['extraction']['papers'])
        assert (out/run['events_file']).is_file()
        assert all((out/t['file']).is_file() and (out/t['dot']).is_file() for t in run['tree_exports'])
