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


def publication_context_policy(maximum, margin=16384):
    """The pinned editor has a native 1M window; retain conservative reserves."""
    require(type(maximum) is int and maximum > 0,
            'publication output allowance must be a positive integer')
    require(type(margin) is int and margin > 0,
            'publication context margin must be a positive integer')
    window = 1000000
    output = maximum * 2  # ClaudeCodeProvider.context_output_tokens, including its two-turn reserve.
    bound = window - output - margin
    require(bound > 0, 'publication context reserves exhaust the model window')
    return dict(provider='claude_code', model=MODEL, window_tokens=window,
                output_allowance_tokens=output, margin_tokens=margin,
                admission_bound_tokens=bound,
                basis='Pinned Opus 5.5 native context window; operator-authorized publication policy',
                references=['https://code.claude.com/docs/en/model-config#extended-context',
                            'https://platform.claude.com/docs/en/models/overview'],
                admission_note='Native admission also counts request output within this conservative bound; full evidence retained.')


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


def validate_polish(value, original, figure_ids, *, whole=False, currency=None, reading_markdown=None, minimum_words=3000, proposal=None):
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
        required = ('proposal',) if proposal else (
            'introduction','argument','objection','repl','limit','conclusion')
        require(all(term in labels for term in required), 'publication required section missing')
    require([x['paragraph'] for x in value['change_log']] == list(range(len(body))), 'publication paragraph change log incomplete')
    require(set(CITATION.findall(markdown)) == set(CITATION.findall(original)), 'publication citation inventory changed')
    require(set(NODE.findall(markdown)) == set(NODE.findall(original)), 'publication node coverage changed')
    if whole:
        require(not NODE.findall(abstract[1]), 'publication abstract must not duplicate node markers')
        from ara.runtime.publication_currency import check_currency
        check_currency(markdown,currency,proposal=proposal)
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


def verified_legacy_import(events, route, draft):
    """Legacy metadata is import-compatible only for the current accepted draft."""
    start = max((i for i,e in enumerate(events) if e['stage'] == 'essay_composition_started'), default=0)
    active = events[start:]
    finals = [(i,json.loads(e['payload_json'])) for i,e in enumerate(active) if e['stage'] == 'final_draft']
    if not finals:
        return False
    index, final = finals[-1]
    if final.get('route_id') != route.id or final.get('draft') != draft:
        return False
    gates = [json.loads(e['payload_json']) for e in active[:index] if e['stage'] == 'essay_audit_consensus']
    if not gates:
        return False
    gate = gates[-1]
    return (gate.get('audit_kind') == 'audit_essay' and gate.get('status') == 'complete'
            and gate.get('route_id') == route.id and gate.get('faithful') is True
            and gate.get('flags') == [] and gate.get('k',0) >= 3
            and len(gate.get('samples',[])) >= 3
            and all(s.get('faithful') is True and s.get('flags') == [] for s in gate['samples'])
            and gate.get('draft_sha256') == digest(canonical(draft)))


def polish(calls, route, draft, *, currency=None):
    from ara.runtime.essay_audit import audit_consensus
    calls.screen_imported_draft(draft, kind='audit_publication')
    from ara.runtime.hypotheses import validate_disclosure
    validate_disclosure(calls.log.read(),route,draft)
    from ara.runtime.publication_flow import start as start_flow
    flow = start_flow(calls, route, draft)
    from ara.runtime.proposal import activate, validate_disclosure as validate_proposal_disclosure
    proposal = activate(calls, route)
    validate_proposal_disclosure(proposal, draft, allow_legacy=bool(proposal) and verified_legacy_import(calls.log.read(), route, draft))
    from ara.runtime.publication_resume import repair_state
    inline_enabled = calls.config.get('publication_inline_repairs', False)
    title_only = calls.config.get('publication_title_format_only', False)
    require(not (inline_enabled and title_only), 'choose inline repairs or title formatting only')
    require(not flow or inline_enabled and not title_only, 'flow publication requires inline repairs only')
    resumed = repair_state(calls.log.read(), route.id, digest(canonical(draft)), inline=inline_enabled or title_only)
    require(not title_only or resumed['candidate'] is not None,
            'title formatting requires an accepted publication candidate')
    if resumed['candidate'] is not None:
        calls.screen_imported_draft(as_draft(resumed['candidate']['markdown'], draft['bibliography']),
                                    kind='audit_publication')
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
        validate_proposal_disclosure(proposal, as_draft(value['markdown'], draft['bibliography']))
        reading,_ = reading_copy(value['markdown'],evidence,records,currency)
        validate_polish(value,original,figure_ids,whole=True,currency=currency,reading_markdown=reading,minimum_words=policy['minimum_words'],proposal=proposal)
        return value
    def repair_failure(exc, before_value, after_value):
        from ara.runtime.publication_audit import repair_length_feedback
        feedback = dict(validator_failure=str(exc), minimum_words=policy['minimum_words'], maximum_words=policy['maximum_words'])
        try:
            before = reading_copy(before_value['markdown'],evidence,records,currency)[0]
            after = reading_copy(after_value['markdown'],evidence,records,currency)[0]
            feedback.update(repair_length_feedback(before, after))
        except Rejected as length_error:
            feedback['length_diagnostics_unavailable'] = str(length_error)
        return Rejected(canonical(feedback))
    def check_inline(value):
        try:
            return check_whole(value)
        except Rejected as exc:
            raise repair_failure(exc, candidate, value) from exc
    def check_composed(value):
        from ara.runtime.proposal import insert_disclosure
        before = as_draft(value['markdown'], draft['bibliography'])
        disclosed = insert_disclosure(proposal, before)
        if disclosed == before:
            return check_whole(value)
        # Validate the model's inventories and indices before metadata shifts them.
        validate_polish(value, original, figure_ids)
        markdown = '# ' + disclosed['title'] + '\n\n' + disclosed['body']
        improvements = {p: c['improvement'] for p,c in zip(paragraphs(value['markdown']), value['change_log'])}
        normalized = dict(value, markdown=markdown,
            figure_placements=[dict(id=m[1], after_paragraph=len(paragraphs(markdown[:m.start()]))-1)
                               for m in FIGURE.finditer(markdown)],
            change_log=[dict(paragraph=i, improvement=improvements.get(p,
                'Required proposal disclosure inserted; substantive text retained. Original model edits are recorded.'))
                        for i,p in enumerate(paragraphs(markdown))])
        check_whole(normalized)
        calls.log.record('publication_proposal_disclosure_inserted', route_id=route.id,
                         before_sha256=digest(canonical(value)), after_sha256=digest(canonical(normalized)),
                         model_change_log=value['change_log'], semantic_repair_rounds_unchanged=True)
        return normalized
    def format_titles(value, failed, origin):
        from ara.runtime.publication_verification import title_format_body
        from ara.runtime.publication_inline import with_markdown
        current = as_draft(value['markdown'], draft['bibliography'])
        formatted = title_format_body(current, failed, {r['record'].get('title') for r in records.values()})
        body_start = value['markdown'].index(current['body'])
        markdown = (value['markdown'][:body_start] + formatted
                    + value['markdown'][body_start+len(current['body']):])
        updated = with_markdown(value, markdown,
            'Exact cited work-title delimiters changed to italics; wording retained.')
        check_whole(updated)
        calls.log.record('publication_title_format_repair', before_sha256=digest(canonical(value)),
            failed_items=failed, diagnosis_origin=origin, whole_paper_rounds_unchanged=True,
            inline_passes_unchanged=True, **updated)
        return updated
    figure_ids = {f['id'] for f in figures}
    chunks = sections(draft,calls.log.read())
    original = '\n\n'.join(chunks)
    calls.log.record('publication_started', route_id=route.id, original_draft=draft,
                     original_sha256=digest(canonical(draft)), requested_model=MODEL,
                     resumed_repair_rounds=resumed['repair_rounds'], resumed_inline_passes=resumed['inline_passes'])
    base = dict(**({'proposal': proposal} if proposal else {}), outline=calls.essay_outline(route), source_evidence=evidence,
                minimum_words=policy['minimum_words'], maximum_words=policy['maximum_words'],
                figures=[dict(id=f['id'],caption=f['caption']) for f in figures], original_title=draft['title'], literature_currency=currency)
    accepted = []
    candidate = resumed['candidate']
    if candidate is not None:
        check_whole(candidate)
    audit = dict(faithful=False)
    failure = None
    repair_rounds = resumed['repair_rounds']
    accepted_repair_rounds = resumed['accepted_repair_rounds']
    inline_passes = resumed['inline_passes']
    native_citations = dict(status='not_run',reason='polish failed; original draft retained')
    try:
        if title_only:
            from ara.runtime.publication_verification import logged_title_failures
            failed = logged_title_failures(calls.log.read(), as_draft(candidate['markdown'], draft['bibliography']))
            if failed:
                candidate = format_titles(candidate, failed, 'exact_logged_request')
        if candidate is None and flow:
            from ara.runtime.publication_flow import edit
            candidate = edit(calls, draft, figure_ids, check_whole)
            calls.log.record('publication_candidate', **candidate)
        if candidate is None:
            for index,chunk in enumerate(chunks):
                result = calls.call('polish_essay',dict(**base,mode='section',section_index=index,
                    markdown=chunk,paragraphs=paragraphs(chunk)),
                    lambda value,chunk=chunk: validate_polish(value,chunk,figure_ids))
                accepted.append(result)
                calls.log.record('publication_section',route_id=route.id,section_index=index,**result)
            merged = '\n\n'.join(v['markdown'] for v in accepted)
            candidate = calls.call('polish_essay',dict(**base,mode='whole',markdown=merged,
                original_markdown=original,paragraphs=paragraphs(merged)),
                check_composed)
            calls.log.record('publication_candidate', **candidate)
        while True:
            current = as_draft(candidate['markdown'],draft['bibliography'])
            citation_check(current,evidence)
            try:
                if not title_only:
                    audit = audit_consensus(calls,route,current,publication_context=publication_context)
                try:
                    verifier = calls._for_construction_stage('audit_publication', {})
                    calls.log.record('publication_verification_provider',
                                     provider=verifier.config['provider'], model=verifier.config['model'])
                    cleaned, verification = verifier.verify_originality_citations(current)
                    native_citations = dict(status='pass' if cleaned == current and all(i['status']=='verified' for i in verification['items']) else 'fail', result=verification)
                    if native_citations['status'] == 'pass':
                        audit = audit_consensus(calls,route,current,publication_context=publication_context)
                    else:
                        failed = [item for item in verification['items'] if item['status'] != 'verified']
                        if failed and all(item.get('kind') == 'quotation' for item in failed):
                            from ara.runtime.publication_verification import quotation_flags, title_format_body
                            if inline_enabled or title_only:
                                candidate = format_titles(candidate, failed, 'current_verification')
                                continue
                            title_format_body(current,failed,{r['record'].get('title') for r in records.values()})
                            inputs = verifier.audit_inputs(route,current,publication_context=publication_context)
                            flags = quotation_flags(current,inputs,failed)
                            audit = {**audit, 'faithful': False, 'flags': flags,
                                     'extra_steps': [f['sentence'] for f in flags],
                                     'native_verification_issues': failed, 'title_format_only': True,
                                     'repair_instruction': 'Only replace quotation marks around the identified work-title occurrences with Markdown italics (*title*). Preserve every other character, all title wording and every citation.'}
                            calls.log.record('publication_verification_flags', **audit)
                            raise EssayAuditFailed(audit,inputs,[])
                except (ClaudeCodeError, Rejected) as exc:
                    if str(exc) != 'stage_requires_api_provider':
                        raise
                    native_citations = dict(status='blocked',reason=str(exc))
                    calls.log.record('publication_verification_blocked',**native_citations)
                break
            except EssayAuditFailed as rejection:
                audit = rejection.result
                if title_only:
                    raise
                if inline_enabled:
                    from ara.runtime.publication_inline import LIMIT, repair, eligible_sentences
                    eligible = eligible_sentences(candidate['markdown'], rejection)
                    if eligible:
                        require(inline_passes < LIMIT, 'publication inline pass budget exhausted')
                        inline_passes += 1
                        candidate = repair(calls, candidate, rejection, base, check_inline, inline_passes)
                        continue
                if flow or repair_rounds == 3 or not audit.get('flags'):
                    raise
                inputs = rejection.inputs
                flagged = [dict(**sentence,
                    role=next(f['role'] for f in audit['flags'] if f['sentence']==sentence['sentence']),
                    reasons=[f['reason'] for f in audit['flags'] if f['sentence']==sentence['sentence']])
                    for sentence in inputs['sentences'] if sentence['sentence'] in audit['extra_steps']]
                from ara.runtime.publication_audit import repair_locations, validate_repair_scope, validate_sentence_repair
                prior = paragraphs(candidate['markdown'])
                flagged = repair_locations(candidate['markdown'], flagged)
                allowed_blocks = sorted({s['location']['block_index'] for s in flagged})
                allowed = sorted({s['location']['paragraph_index'] for s in flagged
                                  if s['location']['paragraph_index'] is not None})
                require(bool(allowed_blocks), 'publication audit repair could not locate flagged spans')
                def validate_repair(value):
                    try:
                        check_whole(value)
                        if audit.get('title_format_only'):
                            from ara.runtime.publication_verification import title_format_body
                            expected = title_format_body(current,audit['native_verification_issues'],
                                                         {r['record'].get('title') for r in records.values()})
                            require(as_draft(value['markdown'],draft['bibliography'])['body'] == expected,
                                    'work-title formatting repair changed wording or other occurrences')
                        validate_repair_scope(candidate['markdown'], value['markdown'], allowed_blocks)
                        validate_sentence_repair(candidate['markdown'], value['markdown'], flagged)
                    except Rejected as exc:
                        raise repair_failure(exc, candidate, value) from exc
                    return value
                repair_rounds += 1
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
    if not success:
        native_citations = dict(status='not_run',reason='polish failed; original draft retained')
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
        inline_passes=inline_passes,
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
                                       as_draft(reading_markdown,result['draft']['bibliography'])['body'])


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
        inline_passes=result.get('inline_passes',0),
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
                      publication_inline_repairs=getattr(args,'inline_repairs',False),
                      publication_title_format_only=getattr(args,'title_format_only',False),
                      publication_min_words=minimum,essay_min_words=minimum,essay_word_limit=6000,max_output_tokens=24576,
                      cache_dir=str(args.run_dir/'publication/cache'))
        if getattr(args, 'flow_prompt', None):
            from ara.runtime.publication_flow import prompt_record
            config.update(publication_flow_prompt=prompt_record(args.flow_prompt),
                          publication_inline_repairs=True, system_prompt='')
        # A writer's Codex client window belongs to the separately selected
        # Codex auditor, never to the Claude publication provider.
        config.pop('model_context_window', None)
        config.pop('model_context_margin_tokens', None)
        context_policy = publication_context_policy(
            config.get('polish_essay_max_output_tokens', config['max_output_tokens']),
            config.get('publication_context_margin_tokens', 16384))
        config['model_context_token_bound'] = context_policy['admission_bound_tokens']
        config['publication_context_policy'] = context_policy
        if args.audit_provider == 'codex_cli':
            audit_model = args.audit_model or writer_settings['model']
            require(audit_model.startswith('gpt-'), 'Codex publication audit requires a configured GPT model')
            config['stages']['audit_publication'] = dict(provider='codex_cli', model=audit_model,
                effort=writer_settings['effort'], system_prompt=writer_settings.get('system_prompt', ''),
                model_context_token_bound=writer_settings['model_context_token_bound'])
            config['stages']['audit_publication'].update({key: writer_settings[key] for key in
                ('model_context_window', 'model_context_margin_tokens', 'propose_targets_max_output_tokens')
                if key in writer_settings})
        elif args.audit_model is not None:
            require(args.audit_model == MODEL, 'Claude publication audit uses the pinned publication model')
        config.setdefault('claude_code', {}).setdefault('timeout_seconds', 900)
        if args.unknown_usage_policy:
            config['unknown_usage_policy'] = args.unknown_usage_policy
        calls = calls_factory(config,log,run['topic'],imported_draft=draft)
        if config.get('publication_flow_prompt'):
            calls.screen_imported_draft(config['publication_flow_prompt'], kind='polish_flow')
        validate_local(json.loads((root/'schemas/write_essay.json').read_text()),draft,run['config'])
        log.record('publication_configuration',config=config,draft_path=str(draft_path),draft_sha256=digest(canonical(draft)))
        log.record('publication_context_policy', **context_policy)
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
