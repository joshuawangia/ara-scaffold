"""Sectioned competition writing using the ordinary logged model boundary."""
from __future__ import annotations

import json
import re

from ara.runtime.cache import canonical, digest
from ara.runtime.extraction import HEADER
from ara.runtime.grounding import evidence_items, references


MAX_SECTION_WORDS = 1800
MAX_CONTEXT_CHARS = 80000
NEIGHBOR_CHARS = 12000


def source_context(calls, route):
    """Exact T support plus bounded source context, never a second premise set."""
    from ara.runtime.calls import require
    from ara.runtime.route_policy import frozen_from_events
    from ara.runtime.citations import catalogue, support_ids
    events = calls.log.read()
    frozen = frozen_from_events(events)
    provenance = calls.search_vocabulary(frozen)['commitment_provenance'] if frozen is not None else None
    ids = support_ids(route, frozen)
    citations = catalogue(events, ids)
    starts = [json.loads(e['payload_json']) for e in events if e['stage'] == 'run_started']
    literature = starts[0].get('literature') if starts else None
    papers = {p['source_id']: p for p in json.loads(literature[len(HEADER):])['papers']} if (
        isinstance(literature, str) and literature.startswith(HEADER)) else {}
    supports, contexts, bibliography = [], [], []
    for tid in sorted(ids):
        commitment = frozen.get(tid) if frozen is not None else None
        require(commitment is not None, 'essay support missing frozen commitment')
        source = provenance['commitments'][tid] if provenance else None
        supports.append(dict(commitment=commitment.to_dict(), provenance=source))
        bibliography.append(citations[tid]['bibliography'] if tid in citations
                            else dict(id=tid, text=commitment.citation, url=None))
        if source is None:
            contexts.append(dict(evidence_id=tid, unavailable='source provenance unavailable'))
            continue
        paper = papers.get(source['source_id'])
        if paper is None:
            contexts.append(dict(evidence_id=tid, source_id=source['source_id'],
                                 unavailable='logged source graph unavailable'))
            continue
        items = evidence_items(paper)
        anchor = next((i for i in items if i['id'] == tid), None)
        near = references(anchor) if anchor else set(source['omitted_support_ids'])
        ranked = sorted((i for i in items if i['id'] != tid), key=lambda i: (
            not (i['id'] in near or tid in references(i)),
            min(abs(i['page_start'] - source['page_end']), abs(source['page_start'] - i['page_end'])), i['id']))
        chosen, used = [], 0
        for item in ranked:
            size = len(canonical(item))
            if len(chosen) < 6 and used + size <= NEIGHBOR_CHARS:
                chosen.append(item)
                used += size
        contexts.append(dict(evidence_id=tid, source_id=source['source_id'],
            source_authors=source['source_authors'], status=paper['status'], items=chosen,
            omitted_item_count=len(ranked) - len(chosen),
            open_gaps=paper.get('open_gaps', []), resolutions=paper.get('resolutions', []),
            authority='context_only_not_additional_T_support'))
    result = dict(supporting_commitments=supports, paper_context=contexts,
                  allowed_bibliography=bibliography,
                  critical_questions=[dict(node_id=n.id, **a.to_dict()) for n in route.nodes for a in n.cq_answers],
                  disclosed_limits=dict(open_node_ids=list(route.frontier),
                      omitted_support_ids=sorted({id for s in supports if s['provenance']
                          for id in s['provenance']['omitted_support_ids']})))
    require(len(canonical(result)) <= MAX_CONTEXT_CHARS,
            'essay required source context exceeds bound; no evidence was truncated')
    return result


def _markers(body):
    return set(re.findall(r'\[\[node:([^\]]+)\]\]', body))


def sectioned_essay(calls, route, inputs, validate):
    from ara.runtime.calls import require, word_count
    evidence = source_context(calls, route)
    base = {**inputs, 'source_evidence': evidence}
    minimum, maximum = inputs['minimum_words'], inputs['word_limit']
    budget_min, budget_max = max(4800, minimum), min(5600, maximum)
    require(budget_min <= budget_max, 'essay limits cannot fit section budgets')
    node_ids = {n.id for n in route.nodes}

    def check_plan(data):
        sections = data['sections']
        require(len({s['id'] for s in sections}) == len(sections), 'duplicate essay section id')
        require(budget_min <= sum(s['word_budget'] for s in sections) <= budget_max,
                'essay section budgets outside requested range')
        require(set().union(*(set(s['node_ids']) for s in sections)) == node_ids,
                'essay section plan node coverage mismatch')
        return data

    plan = calls.call('outline_essay', {**base, 'budget_min': budget_min, 'budget_max': budget_max}, check_plan)
    calls.log.record('essay_section_plan', route_id=route.id, plan=plan)
    accepted = []
    allowed = {b['id']: b for b in evidence['allowed_bibliography']}
    directory = calls.log.path.parent / 'writing' / digest(route.id)[:16]
    directory.mkdir(parents=True, exist_ok=True)

    def save():
        (directory / 'sections.json').write_text(canonical(dict(route_id=route.id, plan=plan, sections=accepted)))

    def request(section, mode, **extra):
        def check(data):
            require(data['title'] == section['heading'], 'essay section heading changed')
            markers = _markers(data['body'])
            require(set(section['node_ids']) <= markers <= node_ids, 'essay section node coverage mismatch')
            require(word_count(data) <= MAX_SECTION_WORDS and len(data['body']) <= 24000,
                    'essay section exceeds bounded size')
            body = re.sub(r'\[\[node:[^\]]+\]\]|\[cite:[^\]]+\]', '', data['body'])
            require(sum(any(c.isalnum() for c in t) for t in body.split()) >= 2,
                    'essay section needs at least two text tokens')
            cited = set(re.findall(r'\[cite:([^\]]+)\]', data['body']))
            bib = data['bibliography']
            require(len({b['id'] for b in bib}) == len(bib), 'duplicate section citation id')
            require(cited == {b['id'] for b in bib} and all(allowed.get(b['id']) == b for b in bib),
                    'essay section citation lacks exact T evidence')
            required = {r['evidence_id'] for r in inputs['outline'].get('source_roles', [])
                        if r['node_id'] in section['node_ids']}
            required.update(n.t_id for n in route.nodes if n.id in section['node_ids']
                            and n.kind == 'leaf' and n.t_id != 'open')
            require(required <= cited, 'essay section missing supporting citation')
            if mode == 'expand':
                old = extra['current_section']
                used = {b['id'] for b in old['bibliography']} | cited
                data = dict(title=old['title'], body=old['body'] + '\n\n' + data['body'],
                            bibliography=[allowed[id] for id in sorted(used)])
                require(word_count(data) <= MAX_SECTION_WORDS and len(data['body']) <= 24000,
                        'expanded essay section exceeds bounded size')
            return data
        return calls.call('write_essay', {**base, 'mode': mode, 'section_plan': plan, 'section': section,
            'previous_sections': list(accepted), 'section_word_limit': MAX_SECTION_WORDS, **extra}, check)

    def assemble():
        used = {b['id'] for s in accepted for b in s['bibliography']}
        return dict(title=plan['title'], body='\n\n'.join(s['title'] + '\n\n' + s['body'] for s in accepted),
                    bibliography=[allowed[id] for id in sorted(used)])

    for section in plan['sections']:
        draft = request(section, 'section')
        accepted.append(draft)
        calls.log.record('essay_section_accepted', route_id=route.id, section_id=section['id'],
                         words=word_count(draft), round=0, draft=draft)
        save()

    for round_number in range(1, 4):
        total = word_count(assemble())
        if minimum <= total <= maximum:
            break
        mode = 'expand' if total < minimum else 'condense'
        ranked = sorted(range(len(accepted)), key=lambda i: (
            -(plan['sections'][i]['word_budget'] - word_count(accepted[i])) if mode == 'expand'
            else -(word_count(accepted[i]) - plan['sections'][i]['word_budget']), i))
        for index in ranked:
            total = word_count(assemble())
            if minimum <= total <= maximum:
                break
            # Re-evaluate direction if a replacement overshot the opposite bound.
            if (mode == 'expand') != (total < minimum):
                break
            section, old = plan['sections'][index], accepted[index]
            available = MAX_SECTION_WORDS - word_count(old)
            if mode == 'expand' and available <= 0:
                continue
            expansion = dict(additional_word_target=min(available, max(100, section['word_budget'] - word_count(old))),
                             additional_word_limit=available) if mode == 'expand' else {}
            replacement = request(section, mode, current_section=old, measured_words=word_count(old),
                                  total_words=total, round=round_number, **expansion)
            before, after = word_count(old), word_count(replacement)
            improves = after > before if mode == 'expand' else after < before
            calls.log.record('essay_length_revision', route_id=route.id, section_id=section['id'],
                             round=round_number, mode=mode, before=before, after=after, accepted=improves)
            if improves:
                accepted[index] = replacement
                save()
    draft = assemble()
    calls.log.record('essay_assembled', route_id=route.id, words=word_count(draft),
                     minimum_words=minimum, word_limit=maximum, sections_path=str(directory / 'sections.json'))
    return validate(draft)
