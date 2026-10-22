"""Append-only delta sidecars, sealed by one existing hash-chain append."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import os
import uuid

from ara.runtime.cache import canonical, digest


class TraceFile:
    def __init__(self, path):
        self.path = path
        self.stream = path.open('xb')
        self.hash = hashlib.sha256()
        self.count = 0
        self.last_action = None

    def record(self, action, **payload):
        raw = (canonical(dict(seq=self.count, action=action, **payload)) + '\n').encode()
        self.stream.write(raw)
        self.stream.flush()
        self.hash.update(raw)
        self.count += 1
        self.last_action = action

    def close(self):
        try:
            self.stream.flush()
            os.fsync(self.stream.fileno())
        finally:
            self.stream.close()


class SearchTraceFiles:
    def __init__(self, log):
        self.log = log

    @contextmanager
    def open_search(self, search_id):
        directory = self.log.path.parent / 'search-traces'
        directory.mkdir(exist_ok=True)
        path = directory / f'{digest(search_id)[:16]}-{uuid.uuid4().hex}.jsonl'
        writer = TraceFile(path)
        try:
            yield writer
        except BaseException:
            writer.close()  # Retain the unsealed prefix as partial; never fabricate an end.
            raise
        else:
            writer.close()
            if writer.last_action != 'end':
                raise ValueError('search trace did not end; unsealed sidecar retained')
            self.log.record('search_trace_receipt', version=2, search_id=search_id,
                            path=str(path.relative_to(self.log.path.parent)),
                            source_log=str(self.log.path.resolve()),
                            line_count=writer.count, sha256=writer.hash.hexdigest())
