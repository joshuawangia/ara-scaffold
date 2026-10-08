"""Append-only, hash-chained events with a separate append-only tail checkpoint."""
from __future__ import annotations

import fcntl
import json
import math
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from ara.runtime.cache import canonical, digest
from ara.types import RunEvent


class LogTampered(ValueError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_log(path: Path) -> list[dict]:
    """Verify the entire chain; export can operate on this file alone."""
    previous = '0' * 64
    records = []
    try:
        with Path(path).open() as stream:
            for index, line in enumerate(stream):
                row = json.loads(line)
                checksum = row.pop('hash')
                if (not line.endswith('\n') or row['seq'] != index or
                        row['previous'] != previous or digest(canonical(row)) != checksum):
                    raise LogTampered('log chain was modified')
                RunEvent.from_dict(row['event'])
                previous = checksum
                records.append({**row, 'hash': checksum})
    except (KeyError, TypeError, json.JSONDecodeError, ValueError) as exc:
        raise LogTampered('invalid or modified log') from exc
    return records


class EventLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.anchor = self.path.with_suffix('.anchor')
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._locked():
            self._verify()

    @contextmanager
    def _locked(self) -> Iterator[None]:
        with self.path.with_suffix('.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def _verify(self) -> list[dict]:
        records = read_log(self.path) if self.path.exists() else []
        checkpoints = self.anchor.read_text().splitlines() if self.anchor.exists() else []
        expected = [r['hash'] for r in records]
        if checkpoints != expected or (self.path.exists() != self.anchor.exists()):
            raise LogTampered('log/checkpoint mismatch: modified, truncated, or interrupted append')
        return records

    def emit(self, event: RunEvent) -> None:
        with self._locked():
            records = self._verify()
            row = {'seq': len(records), 'previous': records[-1]['hash'] if records else '0' * 64,
                   'event': event.to_dict()}
            row['hash'] = digest(canonical(row))
            # Never rewrite either file, including when recovering a failed append.
            for path, text in ((self.path, canonical(row) + '\n'), (self.anchor, row['hash'] + '\n')):
                with path.open('a') as stream:
                    stream.write(text)
                    stream.flush()
                    os.fsync(stream.fileno())

    def record(self, stage: str, label: str = 'SYSTEM', **payload) -> None:
        self.emit(RunEvent(now(), stage, label, payload_json=canonical(payload)))

    def human(self, stage: str, text: str, *, elapsed_seconds: float = 0,
              reported_minutes: float = 0, **payload) -> None:
        if any(not math.isfinite(x) or x < 0 for x in (elapsed_seconds, reported_minutes)):
            raise ValueError('human time must be finite and nonnegative')
        self.record(stage, 'HUMAN', text=text, elapsed_seconds=elapsed_seconds,
                    reported_minutes=reported_minutes, **payload)

    def read(self) -> list[dict]:
        with self._locked():
            return [r['event'] for r in self._verify()]
