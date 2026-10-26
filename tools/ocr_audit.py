"""Local-only intake audit; content and per-page receipts stay in ignored runs/."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import time

from ara.runtime.cache import canonical
from ara.runtime.extraction import load_papers
from ara.runtime.logging import EventLog
from ara.runtime.ocr import LocalOCR, recover_papers
from ara.runtime.ocr_spans import character_classes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--fulltext-dir', type=Path, required=True)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--cache', type=Path, default=Path('cache/ocr'))
    parser.add_argument('--tiers', type=int, choices=(1, 2), default=2)
    parser.add_argument('--paper-id', action='append', default=[])
    args = parser.parse_args()
    root = Path('runs').resolve()
    if not args.run_dir.resolve().is_relative_to(root):
        parser.error('--run-dir must be under the checkout runs/ directory')
    if args.run_dir.exists() and any(args.run_dir.iterdir()):
        parser.error('--run-dir must be empty')
    log = EventLog(args.run_dir / 'events.jsonl')
    log.human('ocr-audit', canonical({k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}))
    start = time.perf_counter()
    papers = load_papers(args.manifest, args.fulltext_dir, tuple(args.paper_id))
    initialization = time.perf_counter()
    engine = LocalOCR(args.cache)
    init_seconds = time.perf_counter() - initialization
    summaries = []
    vl_engine = None
    if args.tiers == 2:
        from ara.runtime.ocr_vl import LocalVLOCR
        vl_engine = LocalVLOCR(args.cache)
    for paper in papers:
        recovered = recover_papers((paper,), args.fulltext_dir, log, args.cache, engine=engine, vl_engine=vl_engine, use_vl=args.tiers == 2)[0]
        records = [json.loads(e['payload_json']) for e in log.read() if e['stage'] == 'extraction_ocr_page']
        records = [row for row in records if row['source_id'] == paper.source_id]
        affected = set(paper.affected_pages)
        structural = []
        for row in records:
            original = paper.pages[row['page'] - 1].text
            structural.append({k:v for k,v in row.items() if k not in ('text','line_confidences')} |
                              dict(original_words=len(original.split()), ocr_words=len(row['text'].split()),
                                   original_classes=character_classes(original), ocr_classes=character_classes(row['text'])))
        final = {row['page']: row for row in records}
        targeted = [row for page, row in final.items() if page in affected]
        summary = dict(source_id=paper.source_id, pdf_sha256=paper.pdf_sha256,
                       affected=len(affected), attempted=len(targeted),
                       recovered=sum(row['recovered'] for row in targeted),
                       recovered_tier1=sum(row['recovered'] and row['tier'] == 1 for row in targeted),
                       recovered_vl=sum(row['recovered'] and row['tier'] == 2 for row in targeted),
                       still_flagged=len(set(recovered.affected_pages)),
                       spans_total=sum(row.get('spans_total', 0) for row in targeted),
                       spans_repaired=sum(row.get('spans_repaired', 0) for row in targeted),
                       spans_remaining=sum(row.get('spans_remaining', 0) for row in targeted),
                       confidence=sum(row['confidence'] for row in targeted)/len(targeted) if targeted else None,
                       seconds=sum(row['seconds'] for row in records if row['page'] in affected),
                       blank_controls=len(final)-len(targeted),
                       blank_seconds=sum(row['seconds'] for row in records if row['page'] not in affected),
                       unavailable=recovered.unavailable)
        (args.run_dir / f'{paper.source_id}.json').write_text(canonical(dict(summary=summary, pages=structural,
            original=asdict(paper), recovered=asdict(recovered))))
        summaries.append(summary)
        (args.run_dir / 'summary.json').write_text(canonical(dict(engine=engine.identity, papers=summaries,
            initialization_seconds=init_seconds, elapsed_seconds=time.perf_counter()-start)))
        print(canonical(summary), flush=True)


if __name__ == '__main__':
    main()
