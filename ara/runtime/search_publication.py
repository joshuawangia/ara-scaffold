"""Durable worker journals, published into the run chain in input/polarity order."""
from __future__ import annotations

import hashlib
import uuid

from ara.runtime.logging import EventLog
from ara.types import RunEvent


class SearchPublication:
    def __init__(self, log, goals):
        self.log = log
        self.batch_id = uuid.uuid4().hex
        directory = log.path.parent / 'search-journals' / self.batch_id
        self.journals = [EventLog(directory / f'{i:04d}.jsonl') for i in range(len(goals))]
        log.record('search_publication_started', batch_id=self.batch_id,
                   order='input target, then positive/negative polarity',
                   jobs=[dict(job_index=i, goal=goal.to_dict(),
                              journal=str(journal.path.relative_to(log.path.parent)))
                         for i, (goal, journal) in enumerate(zip(goals, self.journals, strict=True))])

    def run(self, index, search, goal):
        with self.log.destination(self.journals[index]):
            self.log.record('search_job_started', job_index=index)
            try:
                result = search(goal)
            except BaseException as exc:
                self.log.record('search_job_failed', job_index=index, reason=type(exc).__name__)
                raise
            self.log.record('search_job_finished', job_index=index)
            return result

    def publish(self):
        # Called only after the pool drains, including its failure path. A crash
        # or publication failure leaves the started batch visibly incomplete.
        for index, journal in enumerate(self.journals):
            with self.log.destination(journal):
                events = self.log.read()
            self.log.record('search_job_publication', batch_id=self.batch_id, job_index=index,
                            journal=str(journal.path.relative_to(self.log.path.parent)),
                            event_count=len(events),
                            sha256=hashlib.sha256(journal.path.read_bytes()).hexdigest() if events else None,
                            anchor_sha256=hashlib.sha256(journal.anchor.read_bytes()).hexdigest() if events else None)
            self.log.emit_many(RunEvent.from_dict(event) for event in events)
            self.log.record('search_job_published', batch_id=self.batch_id, job_index=index)
        self.log.record('search_publication_finished', batch_id=self.batch_id)
