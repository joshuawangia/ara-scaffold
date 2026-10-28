"""Post-draft publication through the native logged and isolated model boundary."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import ModelCalls, Rejected, require
from ara.runtime.claude_code import ClaudeCodeError
from ara.runtime.freeze_fork import effective_run
from ara.runtime.writing import source_context
from ara.types import RouteGraph

MODEL = 'claude-opus-5-5'
FIGURE = re.compile(r'\{\{fig:([^}]+)\}\}')
CITATION = re.compile(r'\[cite:([^\]]+)\]')
NODE = re.compile(r'\[\[node:([^\]]+)\]\]')


class RunSources:
    """Read-only view of native evidence builders, without opening a provider."""
    essay_outline = ModelCalls.essay_outline
    search_vocabulary = ModelCalls.search_vocabulary

    def __init__(self, log, root):
        self.log, self.root = log, root


def paragraphs(markdown):
    return [p.strip() for p in re.split(r'\n\s*\n', markdown)
            if p.strip() and not p.lstrip().startswith('#') and not FIGURE.fullmatch(p.strip())]


def strip_figures(markdown):
    return FIGURE.sub('', markdown)


def validate_polish(value, original, figure_ids, *, whole=False):
    markdown = value['markdown']
    body = paragraphs(strip_figures(markdown))
    if whole:
        words = len(NODE.sub('', FIGURE.sub('', markdown)).split())
        require(4500 <= words <= 6000, 'publication word count outside 4500–6000')
        abstract = re.search(r'^## Abstract\s*\n(.*?)(?=^## \d+\.)',markdown,re.M|re.S)
        require(abstract is not None and 150 <= len(abstract[1].split()) <= 200, 'publication abstract must contain 150–200 words')
        require(re.match(r'^# [^\n]+\n',markdown) is not None, 'publication title missing')
        headings = re.findall(r'^## (\d+)\. (.+)$',markdown,re.M)
        require([int(n) for n,_ in headings] == list(range(1,len(headings)+1)), 'publication numbered sections invalid')
        labels = ' '.join(h.lower() for _,h in headings)
        require(all(term in labels for term in ('introduction','argument','objection','repl','limit','conclusion')), 'publication required section missing')
        original_paragraphs = paragraphs(original)
        main = body[1:]
    else:
        original_paragraphs, main = paragraphs(original), body
    require([x['paragraph'] for x in value['change_log']] == list(range(len(body))), 'publication paragraph change log incomplete')
    require(len(main) == len(original_paragraphs), 'publication paragraph inventory changed')
    for before,after in zip(original_paragraphs,main):
        require(CITATION.findall(before) == CITATION.findall(after), 'publication paragraph citation sequence changed')
        require(NODE.findall(before) == NODE.findall(after), 'publication paragraph node markers changed')
    if whole:
        require(set(CITATION.findall(body[0])) <= set(CITATION.findall(original)), 'publication abstract citation invented')
        require(not NODE.findall(body[0]), 'publication abstract must not duplicate node markers')
    found = FIGURE.findall(markdown)
    placements = value['figure_placements']
    require(found == [p['id'] for p in placements] and len(found) == len(set(found)) and set(found) <= figure_ids,
            'publication figure inventory mismatch')
    if whole:
        require(set(found) == figure_ids, 'publication required figure missing')
    for match,placement in zip(FIGURE.finditer(markdown),placements):
        require(placement['after_paragraph'] == len(paragraphs(markdown[:match.start()]))-1,
                'publication figure paragraph position mismatch')
    require(not re.search(r'^#{1,6} (?:References|Bibliography)\b',markdown,re.M|re.I), 'references are constructed from T, not model output')
    require(not re.search(r'^\s*(?:Author|By|Affiliation|Email)\s*:',markdown,re.M|re.I), 'publication must be anonymous')
    return value


def sections(draft, events):
    headings = []
    for event in events:
        if event['stage'] == 'essay_section_plan':
            headings = [s['heading'] for s in json.loads(event['payload_json'])['plan']['sections']]
    body = draft['body']
    if headings and all(h in body.split('\n\n') for h in headings):
        for index,heading in enumerate(headings,1):
            body = re.sub(r'(?m)^' + re.escape(heading) + '$', f'## {index}. {heading}', body, count=1)
    chunks = re.split(r'(?=^## )', body, flags=re.M)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def citation_check(draft, evidence):
    allowed = {b['id']: b for b in evidence['allowed_bibliography']}
    used = set(CITATION.findall(draft['body']))
    require(used == {b['id'] for b in draft['bibliography']}, 'publication citation/bibliography mismatch')
    require(all(allowed.get(b['id']) == b for b in draft['bibliography']), 'publication citations lack exact T provenance')
    return dict(passed=True, cited_ids=sorted(used), basis='exact frozen T citation membership; source semantics assessed by native audit')


def as_draft(markdown, bibliography):
    lines = markdown.splitlines()
    return dict(title=lines[0].removeprefix('# ').strip(), body='\n'.join(lines[1:]).strip(), bibliography=bibliography)


def polish(calls, route, draft):
    from ara.runtime.publication_figures import figure_data
    evidence = source_context(calls, route)
    citation_check(draft,evidence)
    figures = figure_data(calls,route)
    figure_ids = {f['id'] for f in figures}
    chunks = sections(draft,calls.log.read())
    original = '\n\n'.join(chunks)
    calls.log.record('publication_started', route_id=route.id, original_draft=draft,
                     original_sha256=digest(canonical(draft)), requested_model=MODEL)
    base = dict(outline=calls.essay_outline(route), source_evidence=evidence,
                figures=[dict(id=f['id'],caption=f['caption']) for f in figures], original_title=draft['title'])
    accepted = []
    candidate = None
    audit = dict(faithful=False)
    failure = None
    try:
        for index,chunk in enumerate(chunks):
            result = calls.call('polish_essay',dict(**base,mode='section',section_index=index,
                markdown=chunk,paragraphs=paragraphs(chunk)),
                lambda value,chunk=chunk: validate_polish(value,chunk,figure_ids))
            accepted.append(result)
            calls.log.record('publication_section',route_id=route.id,section_index=index,**result)
        merged = '\n\n'.join(v['markdown'] for v in accepted)
        candidate = calls.call('polish_essay',dict(**base,mode='whole',markdown=merged,
            original_markdown=original,paragraphs=paragraphs(merged)),
            lambda value: validate_polish(value,original,figure_ids,whole=True))
        for attempt in range(2):
            current = as_draft(candidate['markdown'],draft['bibliography'])
            citation_check(current,evidence)
            try:
                audit = calls.audit_essay(route,current)
                break
            except Rejected:
                events = calls.log.read()
                verdicts = [json.loads(e['payload_json']) for e in events if e['stage']=='essay_audit']
                audit = verdicts[-1] if verdicts else dict(faithful=False)
                if attempt or not audit.get('extra_steps'):
                    raise
                inputs = calls.audit_inputs(route,current)
                flagged = [s['text'] for s in inputs['sentences'] if s['sentence'] in audit['extra_steps']]
                prior = paragraphs(candidate['markdown'])
                allowed = [i for i,p in enumerate(prior) if any(s in NODE.sub('',p) for s in flagged)]
                require(bool(allowed), 'publication audit repair could not locate flagged paragraphs')
                def validate_repair(value):
                    validate_polish(value,original,figure_ids,whole=True)
                    after = paragraphs(value['markdown'])
                    require(all(a == b for i,(a,b) in enumerate(zip(prior,after)) if i not in allowed),
                            'publication repair changed an unflagged paragraph')
                    return value
                candidate = calls.call('polish_essay',dict(**base,mode='repair',markdown=candidate['markdown'],
                    original_markdown=original,paragraphs=prior,allowed_paragraphs=allowed,
                    flagged_sentences=flagged,audit=audit),validate_repair)
                calls.log.record('publication_repair',allowed_paragraphs=allowed,**candidate)
    except Rejected as exc:
        failure = str(exc)
        audit = {**audit,'faithful':False}
    success = bool(audit['faithful'])
    chosen = as_draft(candidate['markdown'],draft['bibliography']) if success else draft
    local_citations = citation_check(chosen,evidence)
    native_citations = dict(status='not_run',reason='polish failed; original draft retained')
    if success:
        try:
            cleaned, verification = calls.verify_originality_citations(chosen)
            native_citations = dict(status='pass' if cleaned == chosen and all(i['status']=='verified' for i in verification['items']) else 'fail', result=verification)
            if native_citations['status'] == 'pass':
                calls.audit_essay(route,chosen)
        except (ClaudeCodeError, Rejected) as exc:
            if str(exc) != 'stage_requires_api_provider':
                raise
            native_citations = dict(status='blocked',reason=str(exc))
            calls.log.record('publication_verification_blocked',**native_citations)
    markdown = candidate['markdown'] if success else '# '+draft['title']+'\n\n'+original
    placements = candidate['figure_placements'] if success else [
        dict(id=f['id'],after_paragraph=len(paragraphs(markdown))-1) for f in figures]
    if not success:
        markdown += '\n\n' + '\n\n'.join('{{fig:' + f['id'] + '}}' for f in figures)
    from ara.runtime.publication_references import bibliography_records, render_references
    records = bibliography_records(calls.log,evidence)
    result = dict(route_id=route.id,route_sha256=digest(route.to_json()),polished=success,audit=audit,polish_failure=failure,
        local_citations=local_citations,native_citations=native_citations,
        words=len(NODE.sub('',FIGURE.sub('',markdown)).split()),
        original_sha256=digest(canonical(draft)),draft=chosen,
        markdown=markdown+render_references(chosen,evidence,records),bibliographic_records=records,
        figure_placements=placements,placement_origin='model' if success else 'deterministic_fallback',
        change_log=candidate['change_log'] if success else [],section_changes=accepted)
    return publish(calls.log, result)


def publish(log, result):
    """Persist a validated audit artifact and its marker-free reading copy."""
    result = {**result, 'audit_markdown': result['markdown'],
              'markdown': NODE.sub('', result['markdown'])}
    directory = log.path.parent/'publication'
    directory.mkdir(exist_ok=True)
    name = digest(canonical(result))[:16]
    target = directory/name
    target.mkdir(exist_ok=True)
    (target/'paper.md').write_text(result['markdown'])
    (target/'publication.json').write_text(canonical(result))
    log.record('publication_completed',path=str(target.relative_to(log.path.parent)),
        markdown_sha256=digest(result['markdown']),polished=result['polished'],audit=result['audit'],
        local_citations=result['local_citations'],native_citations=result['native_citations'],words=result['words'],
        bibliographic_records=result['bibliographic_records'])
    (directory/'latest.json').write_text(canonical(dict(path=name,sha256=digest(canonical(result)))))
    return result,target


def load_publication(run_dir):
    from ara.runtime.logging import EventLog
    stages = [e['stage'] for e in EventLog(run_dir/'events.jsonl').read()
              if e['stage'] in ('publication_configuration','publication_started','publication_completed')]
    require(bool(stages) and stages[-1] == 'publication_completed',
            'latest publication attempt is incomplete; previous output cannot be reused')
    pointer = json.loads((run_dir/'publication/latest.json').read_text())
    require(re.fullmatch('[a-f0-9]{16}',pointer['path']) is not None,'invalid publication pointer')
    directory = run_dir/'publication'/pointer['path']
    result = json.loads((directory/'publication.json').read_text())
    require(digest(canonical(result)) == pointer['sha256'],'publication digest mismatch')
    require((directory/'paper.md').read_text() == result['markdown'],'publication Markdown changed')
    return result,directory


def publication_command(args, log, root, calls_factory):
    events = log.read()
    run = effective_run(events)
    graphs = {g.id:g for e in events if e['stage']=='route'
              for g in [RouteGraph.from_dict(json.loads(e['payload_json'])['graph'])]}
    if args.command != 'polish':
        result,directory = load_publication(args.run_dir)
        route_id = result['route_id']
    else:
        route_id = args.route
        if route_id is None:
            selections = [json.loads(e['payload_json']) for e in events if e['stage']=='select']
            route_id = selections[-1].get('text') if selections else next(iter(graphs)) if len(graphs)==1 else None
    require(route_id in graphs,'publication needs a known --route')
    route = graphs[route_id]
    if args.command != 'polish':
        require(result['route_sha256'] == digest(route.to_json()), 'publication route changed')
    if args.command == 'polish':
        draft_path = args.draft or args.run_dir/('draft.json' if (args.run_dir/'draft.json').exists() else 'draft.unverified.json')
        draft = json.loads(draft_path.read_text())
        from ara.runtime.validation import validate_local
        validate_local(json.loads((root/'schemas/write_essay.json').read_text()),draft,run['config'])
        config = deepcopy(run['config'])
        config.update(provider='claude_code',model=MODEL,stages={},fallbacks=[],validation_attempts=1,
                      essay_min_words=4500,essay_word_limit=6000,max_output_tokens=24576,
                      cache_dir=str(args.run_dir/'publication/cache'))
        if args.unknown_usage_policy:
            config['unknown_usage_policy'] = args.unknown_usage_policy
        log.record('publication_configuration',config=config,draft_path=str(draft_path),draft_sha256=digest(canonical(draft)))
        calls = calls_factory(config,log,run['topic'])
        result,directory = polish(calls,route,draft)
        print(str(directory/'paper.md'))
        print('audit=' + ('pass' if result['polished'] else 'fail') + '; native_citations=' + result['native_citations']['status'])
        return 0 if result['polished'] and result['native_citations']['status']=='pass' else 2
    if args.command == 'figures':
        from ara.runtime.publication_figures import generate_figures
        manifest = generate_figures(RunSources(log,root),route,directory/'figures')
        log.record('publication_figures',route_id=route_id,manifest=manifest)
        print(str(directory/'figures/manifest.json'))
    else:
        from ara.runtime.publication_pdf import render_pdf
        manifest = json.loads((directory/'figures/manifest.json').read_text())
        proof = render_pdf(result['markdown'],manifest,directory/'figures',directory/'paper.pdf')
        (directory/'pdf-checks.json').write_text(canonical(proof))
        log.record('publication_pdf',route_id=route_id,**proof,
                   polished=result['polished'],native_citations=result['native_citations']['status'])
        print(str(directory/'paper.pdf'))
    return 0
