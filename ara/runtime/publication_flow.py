"""One operator-instructed whole-paper edit through the native model boundary."""
from collections import Counter
import json

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import require


def prompt_record(path):
    # Decode bytes without universal-newline translation: the receipt binds the file.
    raw = path.read_bytes()
    text = raw.decode('utf-8')
    require(bool(text.strip()), 'publication flow prompt is empty')
    return dict(path=str(path.resolve()), text=text, sha256=digest(text))


def render(config, inputs):
    record = config.get('publication_flow_prompt', {})
    text = record.get('text')
    require(isinstance(text, str) and digest(text) == record.get('sha256'),
            'publication flow prompt hash mismatch')
    # Only the manuscript accompanies the exact editing instruction. The provider
    # transports its Markdown in the one-field response schema; no second editor prompt.
    return text, text + '\nINPUT_JSON\n' + canonical(dict(markdown=inputs['markdown']))


def start(calls, route, draft):
    from ara.runtime.publication import verified_legacy_import
    events = calls.log.read()
    record = calls.config.get('publication_flow_prompt')
    prior = [json.loads(e['payload_json']) for e in events if e['stage'] == 'publication_flow_prompt']
    if not record:
        require(not prior, 'flow publication must resume with its original prompt')
        return None
    render(calls.config, dict(markdown=''))
    calls.screen_imported_draft(record, kind='polish_flow')
    require(verified_legacy_import(events, route, draft), 'flow publication requires the verified original')
    binding = dict(**record, route_id=route.id, source_sha256=digest(canonical(draft)))
    require(all(p == binding for p in prior), 'flow publication prompt/source binding changed')
    require(prior or not any(e['stage'] == 'publication_started' for e in events),
            'flow publication requires a dedicated verified-source run')
    require(not any(e['stage'] == 'publication_flow_edit_started' for e in events)
            or any(e['stage'] == 'publication_candidate' for e in events),
            'publication flow edit already attempted; no reroll')
    if not prior:
        calls.log.record('publication_flow_prompt', **binding)
    return binding


def edit(calls, draft, figure_ids, check):
    from ara.runtime.publication import CITATION
    from ara.runtime.publication_inline import with_markdown
    require(not any(e['stage'] == 'publication_flow_edit_started' for e in calls.log.read()),
            'publication flow edit already attempted; no reroll')
    markdown = '# ' + draft['title'] + '\n\n' + draft['body']
    calls.log.record('publication_flow_edit_started',
                     prompt_sha256=calls.config['publication_flow_prompt']['sha256'],
                     source_sha256=digest(canonical(draft)))
    def validate(value):
        require(Counter(CITATION.findall(value['markdown'])) == Counter(CITATION.findall(markdown)),
                'publication flow citation occurrence inventory changed')
        body = value['markdown'] + '\n\n' + '\n\n'.join('{{fig:' + id + '}}' for id in sorted(figure_ids))
        candidate = with_markdown(value, body, 'Single operator-instructed flow edit; raw response retained.')
        return check(candidate)
    return calls.call('polish_flow', dict(markdown=markdown), validate, fresh=True, validation_attempts=1)
