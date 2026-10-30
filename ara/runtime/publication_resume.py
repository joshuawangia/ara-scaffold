"""Recover accepted publication repairs without replenishing their round budget."""
from copy import deepcopy
import json

from ara.runtime.calls import require
from ara.runtime.cache import canonical, digest


def repair_state(events, route_id, original_sha256, *, inline=False):
    active = False
    used = 0
    candidate = None
    accepted = set()
    current_rounds = set()
    attempts = {}
    inline_used = 0
    inline_pending = None
    for event in events:
        stage = event['stage']
        if stage == 'publication_started':
            data = json.loads(event['payload_json'])
            active = data.get('route_id') == route_id and data.get('original_sha256') == original_sha256
            current_rounds = set()
            if active and 'resumed_repair_rounds' in data:
                require(type(data['resumed_repair_rounds']) is int and data['resumed_repair_rounds'] == used,
                        'publication resume counter does not match repair history')
            if active and 'resumed_inline_passes' in data:
                require(data['resumed_inline_passes'] == inline_used,
                        'publication inline resume counter does not match history')
            continue
        if not active:
            continue
        if stage == 'publication_inline_started':
            data = json.loads(event['payload_json'])
            number = data.get('pass_number')
            require(type(number) is int and number == inline_used + 1 and number <= 3,
                    'publication inline pass history exceeds or resets budget')
            require(candidate is not None and data.get('candidate_sha256') == digest(canonical(candidate)),
                    'publication inline pass candidate mismatch')
            inline_used = number
            inline_pending = data['candidate_sha256']
        elif stage == 'publication_inline_repair':
            data = json.loads(event['payload_json'])
            require(inline_pending is not None and data.get('pass_number') == inline_used
                    and data.get('before_sha256') == inline_pending,
                    'publication inline repair lacks its bounded request')
            candidate = {key: deepcopy(data[key]) for key in ('markdown', 'figure_placements', 'change_log')}
            inline_pending = None
        elif stage == 'publication_candidate':
            require(candidate is None and used == 0, 'publication candidate cannot reset repair history')
            data = json.loads(event['payload_json'])
            candidate = {key: deepcopy(data[key]) for key in ('markdown', 'figure_placements', 'change_log')}
        elif stage == 'publication_title_format_repair':
            data = json.loads(event['payload_json'])
            require(candidate is not None and data.get('before_sha256') == digest(canonical(candidate)),
                    'publication title formatting candidate mismatch')
            candidate = {key: deepcopy(data[key]) for key in ('markdown', 'figure_placements', 'change_log')}
        if stage == 'polish_essay' and event['label'] == 'MODEL' and event.get('prompt'):
            try:
                inputs = json.loads(event['prompt'].split('\nINPUT_JSON\n', 1)[1])
            except (IndexError, ValueError):
                require(False, 'publication repair history has an unreadable request')
            if inputs.get('mode') != 'repair':
                continue
            number = inputs.get('repair_round')
            require(type(number) is int and 1 <= number <= 3,
                    'publication repair history has an invalid round')
            require(number not in accepted and
                    (number == used + 1 or number == used and number in current_rounds),
                    'publication repair history restarts a consumed round')
            used = max(used, number)
            current_rounds.add(number)
            attempts[number] = attempts.get(number, 0) + 1
            require(attempts[number] <= 2, 'publication structural retry budget exhausted')
        elif stage == 'publication_repair':
            data = json.loads(event['payload_json'])
            number = data.get('round')
            require(type(number) is int and number == used and number not in accepted,
                    'publication accepted repair lacks its bounded model request')
            require(all(key in data for key in ('markdown', 'figure_placements', 'change_log')),
                    'publication accepted repair is incomplete')
            candidate = {key: deepcopy(data[key]) for key in ('markdown', 'figure_placements', 'change_log')}
            accepted.add(number)
    require(used == 0 or used in accepted,
            'publication has an unfinished or structurally refused repair; its budget cannot reset')
    require(inline or used < 3, 'publication repair budget exhausted; retain the verified pre-polish export')
    return dict(candidate=candidate, repair_rounds=used, accepted_repair_rounds=len(accepted),
                inline_passes=inline_used)
