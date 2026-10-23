"""Versioned measured input estimates and run-local, upward-only correction."""
import json
import math
import threading
from pathlib import Path

from ara.runtime.cache import canonical, digest

TABLE = json.loads(Path(__file__).with_name('claude_code_calibration.json').read_text())
TABLE_HASH = digest(canonical(TABLE))
METHOD = TABLE['version'] + ': p99*1.05 plus measured CLI overhead; not a tokenizer bound'


class CalibrationState:
    def __init__(self):
        self._lock = threading.RLock()
        self._factors = {}

    def restore(self, events):
        for event in events:
            if event['stage'] != 'provider_estimate_observation' or event['label'] != 'SYSTEM':
                continue
            row = json.loads(event['payload_json'])
            if row.get('calibration_sha256') != TABLE_HASH:
                continue
            factor = row['factor_after']
            if not isinstance(factor, (int, float)) or not math.isfinite(factor) or factor <= 0:
                raise ValueError('invalid recorded calibration factor')
            key = row['model'], row['kind']
            self._factors[key] = max(self.factor(*key), factor)

    def factor(self, model, kind):
        with self._lock:
            return self._factors.get((model, kind), TABLE['factors'].get(kind, {'factor':TABLE['fallback_factor']})['factor'])

    def initial(self, model, kind, size):
        return math.ceil(size * self.factor(model, kind)) + TABLE['runtime_overhead_tokens']

    def observe(self, model, kind, size, estimated, actual):
        with self._lock:
            before = self.factor(model, kind)
            underestimated = actual > estimated
            after = max(before, max(0, actual - TABLE['runtime_overhead_tokens']) / max(1, size) * TABLE['margin']) if underestimated else before
            self._factors[model, kind] = after
            return dict(calibration_version=TABLE['version'], calibration_sha256=TABLE_HASH,
                        model=model, request_bytes=size, estimated_initial_input_tokens=estimated,
                        actual_input_tokens=actual, underestimated=underestimated,
                        factor_before=before, factor_after=after,
                        comparison='CLI aggregate input including cache versus initial estimate; conservative, not per-turn attribution')
