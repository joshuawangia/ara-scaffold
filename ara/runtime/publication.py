"""Post-draft publication through the native logged and isolated model boundary."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import ModelCalls, Rejected, EssayAuditFailed, require
from ara.runtime.claude_code import ClaudeCodeError
from ara.runtime.freeze_fork import effective_run
from ara.runtime.writing import source_context
from ara.types import RouteGraph

REPAIR_VALIDATION_ATTEMPTS = 2
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


def length_policy(minimum_words=3000):
    require(type(minimum_words) is int and 1 <= minimum_words <= 6000,
            'publication minimum must be an integer from 1 to 6000')
    return dict(minimum_words=minimum_words, maximum_words=6000,
                minimum_basis='ARA publication profile; not a competition minimum',
                maximum_basis='operator-specified full-draft ceiling',
                count_basis='reading text including title, abstract and inline citations; excluding references, node markers and figure placeholders',
                editorial_preference='prefer a tight supported paper over padding')


def validate_polish(value, original, figure_ids, *, whole=False, currency=None, reading_markdown=None, minimum_words=3000):
    markdown = value['markdown']
    body = paragraphs(strip_figures(markdown))
    if whole:
        length_policy(minimum_words)
        words = len(NODE.sub('', FIGURE.sub('', reading_markdown if reading_markdown is not None else markdown)).split())
        require(minimum_words <= words <= 6000, f'publication word count outside {minimum_words}–6000')
        abstract = re.search(r'^## Abstract\s*\n(.*?)(?=^## \d+\.)',markdown,re.M|re.S)
        require(abstract is not None and 150 <= len(abstract[1].split()) <= 200, 'publication abstract must contain 150–200 words')
        require(re.match(r'^# [^\n]+\n',markdown) is not None, 'publication title missing')
        headings = re.findall(r'^## (\d+)\. (.+)$',markdown,re.M)
        require([int(n) for n,_ in headings] == list(range(1,len(headings)+1)), 'publication numbered sections invalid')
        labels = ' '.join(h.lower() for _,h in headings)
        require(all(term in labels for term in ('introduction','argument','objection','repl','limit','conclusion')), 'publication required section missing')
    require([x['paragraph'] for x in value['change_log']] == list(range(len(body))), 'publication paragraph change log incomplete')
    require(set(CITATION.findall(markdown)) == set(CITATION.findall(original)), 'publication citation inventory changed')
    require(set(NODE.findall(markdown)) == set(NODE.findall(original)), 'publication node coverage changed')
    if whole:
        require(not NODE.findall(body[0]), 'publication abstract must not duplicate node markers')
        from ara.runtime.publication_currency import check_currency
        check_currency(markdown,currency)
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


def polish(calls, route, draft, *, currency=None):
    from ara.runtime.essay_audit import audit_consensus
    calls.screen_imported_draft(draft, kind='audit_publication')
    from ara.runtime.hypotheses import validate_disclosure
    validate_disclosure(calls.log.read(),route,draft)
    policy = length_policy(calls.config.get('publication_min_words', 3000))
    calls.log.record('publication_length_policy', route_id=route.id, **policy)
    from ara.runtime.publication_figures import figure_data
    evidence = source_context(calls, route)
    citation_check(draft,evidence)
    figures = figure_data(calls,route)
    publication_context = dict(original_draft=draft, literature_currency=currency)
    from ara.runtime.publication_references import bibliography_records, render_references, reading_copy
    source_ids = {e['work'] for e in currency['evidence'].values() if e['work']} if currency else set()
    records = bibliography_records(calls.log,evidence,source_ids)
    if currency:
        for id,record in currency['sources'].items():
            records.setdefault(id,dict(record=record,verification='logged_currency_record'))
    def check_whole(value):
        validate_disclosure(calls.log.read(),route,as_draft(value['markdown'],draft['bibliography']))
        reading,_ = reading_copy(value['markdown'],evidence,records,currency)
        validate_polish(value,original,figure_ids,whole=True,currency=currency,reading_markdown=reading,minimum_words=policy['minimum_words'])
        return value
    figure_ids = {f['id'] for f in figures}
    chunks = sections(draft,calls.log.read())
    original = '\n\n'.join(chunks)
    calls.log.record('publication_started', route_id=route.id, original_draft=draft,
                     original_sha256=digest(canonical(draft)), requested_model=MODEL)
    base = dict(outline=calls.essay_outline(route), source_evidence=evidence,
                minimum_words=policy['minimum_words'], maximum_words=policy['maximum_words'],
                figures=[dict(id=f['id'],caption=f['caption']) for f in figures], original_title=draft['title'], literature_currency=currency)
    accepted = []
    candidate = None
    audit = dict(faithful=False)
    failure = None
    repair_rounds = 0
    accepted_repair_rounds = 0
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
            check_whole)
        for attempt in range(4):
            current = as_draft(candidate['markdown'],draft['bibliography'])
            citation_check(current,evidence)
            try:
                audit = audit_consensus(calls,route,current,publication_context=publication_context)
                break
            except EssayAuditFailed as rejection:
                audit = rejection.result
                if attempt == 3 or not audit.get('flags'):
                    raise
                inputs = rejection.inputs
                flagged = [dict(**sentence,
                    role=next(f['role'] for f in audit['flags'] if f['sentence']==sentence['sentence']),
                    reasons=[f['reason'] for f in audit['flags'] if f['sentence']==sentence['sentence']])
                    for sentence in inputs['sentences'] if sentence['sentence'] in audit['extra_steps']]
                from ara.runtime.publication_audit import repair_locations, validate_repair_scope, validate_sentence_repair, repair_length_feedback
                prior = paragraphs(candidate['markdown'])
                flagged = repair_locations(candidate['markdown'], flagged)
                allowed_blocks = sorted({s['location']['block_index'] for s in flagged})
                allowed = sorted({s['location']['paragraph_index'] for s in flagged
                                  if s['location']['paragraph_index'] is not None})
                require(bool(allowed_blocks), 'publication audit repair could not locate flagged spans')
                def validate_repair(value):
                    try:
                        check_whole(value)
                        validate_repair_scope(candidate['markdown'], value['markdown'], allowed_blocks)
                        validate_sentence_repair(candidate['markdown'], value['markdown'], flagged)
                    except Rejected as exc:
                        feedback = dict(validator_failure=str(exc), minimum_words=policy['minimum_words'], maximum_words=policy['maximum_words'])
                        try:
                            before = reading_copy(candidate['markdown'],evidence,records,currency)[0]
                            after = reading_copy(value['markdown'],evidence,records,currency)[0]
                            feedback.update(repair_length_feedback(before, after))
                        except Rejected as length_error:
                            feedback['length_diagnostics_unavailable'] = str(length_error)
                        raise Rejected(canonical(feedback)) from exc
                    return value
                repair_rounds = attempt + 1
                candidate = calls.call('polish_essay',dict(**base,mode='repair',repair_round=repair_rounds,markdown=candidate['markdown'],
                    original_markdown=original,paragraphs=prior,allowed_paragraphs=allowed,allowed_blocks=allowed_blocks,
                    flagged_sentences=flagged,audit_failures=audit['flags'],audit=audit),validate_repair,
                    validation_attempts=REPAIR_VALIDATION_ATTEMPTS)
                accepted_repair_rounds += 1
                calls.log.record('publication_repair',round=repair_rounds,flagged_sentences=flagged,
                                 audit_failures=audit['flags'],allowed_paragraphs=allowed,allowed_blocks=allowed_blocks,**candidate)
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
                audit_consensus(calls,route,chosen,publication_context=publication_context)
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
    reading, citation_receipt = reading_copy(markdown,evidence,records,currency)
    references = render_references(chosen,evidence,records,currency,citation_receipt)
    result = dict(route_id=route.id,route_sha256=digest(route.to_json()),polished=success,audit=audit,polish_failure=failure,
        local_citations=local_citations,native_citations=native_citations,word_limits=policy,
        repair_rounds=repair_rounds,accepted_repair_rounds=accepted_repair_rounds,
        repair_validation_attempts=REPAIR_VALIDATION_ATTEMPTS,
        words=len(NODE.sub('',FIGURE.sub('',reading)).split()),
        audit_words=len(NODE.sub('',FIGURE.sub('',markdown)).split()),
        reading_markdown=reading+references,citation_receipt=citation_receipt,literature_currency=currency,
        original_sha256=digest(canonical(draft)),draft=chosen,
        markdown=markdown+references,bibliographic_records=records,
        figure_placements=placements,placement_origin='model' if success else 'deterministic_fallback',
        change_log=candidate['change_log'] if success else [],section_changes=accepted)
    return publish(calls.log, result)


def validate_publication_disclosure(events, result, audit_markdown, reading_markdown):
    """Check both authenticated copies against the current hypothesis policy."""
    if any(e['stage']=='hypotheses_admitted' for e in events):
        routes=[json.loads(e['payload_json'])['graph'] for e in events if e['stage']=='route']
        route=next((r for r in reversed(routes) if r['id']==result['route_id']),None)
        require(route is not None, 'hypothesis publication requires recorded route')
        from ara.runtime.hypotheses import validate_disclosure
        validate_disclosure(events,RouteGraph.from_dict(route),
            as_draft(audit_markdown,result['draft']['bibliography']))
        from ara.runtime.hypotheses import route_disclosure, validate_conditional_statement
        validate_conditional_statement(route_disclosure(events,RouteGraph.from_dict(route)),
                                       reading_markdown)


def publish(log, result):
    """Persist a validated audit artifact and its marker-free reading copy."""
    validate_publication_disclosure(log.read(), result, result['markdown'],
                                   result.get('reading_markdown', result['markdown']))
    result = {**result, 'audit_markdown': result['markdown'],
              'markdown': NODE.sub('', result.get('reading_markdown',result['markdown']))}
    directory = log.path.parent/'publication'
    directory.mkdir(exist_ok=True)
    name = digest(canonical(result))[:16]
    target = directory/name
    target.mkdir(exist_ok=True)
    (target/'paper.md').write_text(result['markdown'])
    (target/'publication.json').write_text(canonical(result))
    (target/'citation-receipt.json').write_text(canonical(result.get('citation_receipt',{})))
    log.record('publication_completed',path=str(target.relative_to(log.path.parent)),
        markdown_sha256=digest(result['markdown']),polished=result['polished'],audit=result['audit'],
        local_citations=result['local_citations'],native_citations=result['native_citations'],words=result['words'],
        bibliographic_records=result['bibliographic_records'],repair_rounds=result['repair_rounds'],
        accepted_repair_rounds=result['accepted_repair_rounds'],word_limits=result['word_limits'],
        repair_validation_attempts=result['repair_validation_attempts'])
    (directory/'latest.json').write_text(canonical(dict(path=name,sha256=digest(canonical(result)))))
    return result,target


def load_publication(run_dir):
    from ara.runtime.logging import EventLog
    events = EventLog(run_dir/'events.jsonl').read()
    stages = [e['stage'] for e in events
              if e['stage'] in ('publication_configuration','publication_started','publication_completed')]
    require(bool(stages) and stages[-1] == 'publication_completed',
            'latest publication attempt is incomplete; previous output cannot be reused')
    pointer = json.loads((run_dir/'publication/latest.json').read_text())
    require(re.fullmatch('[a-f0-9]{16}',pointer['path']) is not None,'invalid publication pointer')
    directory = run_dir/'publication'/pointer['path']
    result = json.loads((directory/'publication.json').read_text())
    require(digest(canonical(result)) == pointer['sha256'],'publication digest mismatch')
    require((directory/'paper.md').read_text() == result['markdown'],'publication Markdown changed')
    validate_publication_disclosure(events, result, result.get('audit_markdown', result['markdown']),
                                   result['markdown'])
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
        from ara.runtime.providers import stage_settings
        config = deepcopy(run['config'])
        writer_settings = stage_settings(config, 'audit_essay')
        minimum = args.min_words if args.min_words is not None else config.get('publication_min_words', 3000)
        length_policy(minimum)
        config.update(provider='claude_code',model=MODEL,stages={},fallbacks=[],validation_attempts=1,
                      publication_min_words=minimum,essay_min_words=minimum,essay_word_limit=6000,max_output_tokens=24576,
                      cache_dir=str(args.run_dir/'publication/cache'))
        if args.audit_provider == 'codex_cli':
            audit_model = args.audit_model or writer_settings['model']
            require(audit_model.startswith('gpt-'), 'Codex publication audit requires a configured GPT model')
            config['stages']['audit_publication'] = dict(provider='codex_cli', model=audit_model,
                effort=writer_settings['effort'], system_prompt=writer_settings.get('system_prompt', ''))
        elif args.audit_model is not None:
            require(args.audit_model == MODEL, 'Claude publication audit uses the pinned publication model')
        config.setdefault('claude_code', {}).setdefault('timeout_seconds', 900)
        if args.unknown_usage_policy:
            config['unknown_usage_policy'] = args.unknown_usage_policy
        calls = calls_factory(config,log,run['topic'],imported_draft=draft)
        validate_local(json.loads((root/'schemas/write_essay.json').read_text()),draft,run['config'])
        log.record('publication_configuration',config=config,draft_path=str(draft_path),draft_sha256=digest(canonical(draft)))
        from ara.runtime.publication_currency import load_currency
        currency = load_currency(args.literature_currency, log)
        result,directory = polish(calls,route,draft,currency=currency)
        print(str(directory/'paper.md'))
        print('audit=' + ('pass' if result['polished'] else 'fail') + '; native_citations=' + result['native_citations']['status'])
        return 0 if result['polished'] and result['native_citations']['status']=='pass' else 2
    if args.command == 'figures':
        from ara.runtime.publication_figures import generate_figures
        manifest = generate_figures(RunSources(log,root),route,directory/'figures',result.get('citation_receipt'))
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
