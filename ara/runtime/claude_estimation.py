"""Versioned measured input estimates and run-local, upward-only correction."""
import json
import math
import threading
from pathlib import Path

from ara.runtime.cache import canonical, digest

TABLE = json.loads(Path(__file__).with_name('claude_code_calibration.json').read_text())
TABLE_HASH = digest(canonical(TABLE))
OBSERVATION_VERSION = 'like-for-like-v2'
METHOD = TABLE['version'] + ': p99*1.05 plus measured CLI overhead; ' + OBSERVATION_VERSION + '; not a tokenizer bound'


class CalibrationState:
    def __init__(self):
        self._lock = threading.RLock()
        self._factors = {}
        self._overheads = {}

    def restore(self, events):
        from ara.runtime.provenance import imported_event_indices
        inherited = imported_event_indices(events)
        for index, event in enumerate(events):
            if index in inherited:
                continue
            if event['stage'] != 'provider_estimate_observation' or event['label'] != 'SYSTEM':
                continue
            row = json.loads(event['payload_json'])
            if row.get('calibration_sha256') != TABLE_HASH or row.get('observation_version') != OBSERVATION_VERSION:
                continue
            factor = row['factor_after']
            if not isinstance(factor, (int, float)) or not math.isfinite(factor) or factor <= 0:
                raise ValueError('invalid recorded calibration factor')
            key = row['model'], row['kind']
            self._factors[key] = max(self.factor(*key), factor)
            overhead = row['runtime_overhead_after']
            if type(overhead) is not int or overhead < 0:
                raise ValueError('invalid recorded calibration overhead')
            self._overheads[key[0]] = max(self.overhead(key[0]), overhead)

    def factor(self, model, kind):
        with self._lock:
            return self._factors.get((model, kind), TABLE['factors'].get(kind, {'factor':TABLE['fallback_factor']})['factor'])

    def overhead(self, model):
        with self._lock:
            return self._overheads.get(model, TABLE['runtime_overhead_tokens'])

    def initial(self, model, kind, size):
        with self._lock:
            return math.ceil(size * self.factor(model, kind)) + self.overhead(model)

    def observe(self, model, kind, size, initial, aggregate, actual, *, first_turn):
        with self._lock:
            before = self.factor(model, kind)
            overhead_before = self.overhead(model)
            estimated = initial if first_turn else aggregate
            underestimated = actual > estimated
            after = before
            overhead_after = overhead_before
            if kind == 'isolation_canary':
                # A one-turn canary isolates fixed runtime cost from text scaling.
                if first_turn:
                    residual = max(0, actual - math.ceil(size * before))
                    overhead_after = max(overhead_before, math.ceil(residual * TABLE['margin']))
                    self._overheads[model] = overhead_after
            elif underestimated:
                turns = 1 if first_turn else 2
                replay = 0 if first_turn else aggregate - 2 * initial
                residual = max(0, actual - replay - turns * overhead_before)
                after = max(before, residual / (turns * max(1, size)) * TABLE['margin'])
            self._factors[model, kind] = after
            return dict(calibration_version=TABLE['version'], calibration_sha256=TABLE_HASH,
                        observation_version=OBSERVATION_VERSION,
                        model=model, request_bytes=size, estimated_initial_input_tokens=initial,
                        estimated_input_tokens=estimated, actual_input_tokens=actual,
                        underestimated=underestimated, factor_before=before, factor_after=after,
                        runtime_overhead_before=overhead_before, runtime_overhead_after=overhead_after,
                        comparison=('first_turn_input_vs_initial_context' if first_turn else
                                    'aggregate_input_vs_aggregate_reservation'))
