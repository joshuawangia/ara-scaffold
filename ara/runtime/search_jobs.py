"""Run independent searches, then retry job-local failures once in input order."""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from threading import Event

from ara.runtime.budget import BudgetStop
from ara.runtime.calls import CountRequestRefused, Rejected
from ara.runtime.search_publication import SearchPublication
from ara.runtime.search_diagnostics import accepted_inferences, write_pause


def job_failure(exc):
    # ModelCalls has already exhausted transport/validation retries. Accounting,
    # run-wide accounting and infrastructure stops must not become missing work.
    # Counted search-context refusals carry search scope and leave siblings running.
    return isinstance(exc, (Rejected, CountRequestRefused)) or (
        isinstance(exc, BudgetStop) and exc.scope != 'run')


def run_search_jobs(log, jobs, concurrency, new_engine, *, restored=None, pause_after=10):
    publication = SearchPublication(log, [goal for _, goal in jobs])
    halted = Event()
    restored = restored or {}
    results = [restored.get(i) for i in range(len(jobs))]
    attempts = [0] * len(jobs)
    failures = {}
    fatal = {}
    completed = 0
    accepted = sum(len(jobs[i][0]._licenses) for i in restored)
    paused = False

    def run(index, attempt):
        if halted.is_set():
            return None
        attempts[index] = attempt
        engine, goal = jobs[index]
        try:
            return publication.run(index, engine.search, goal, attempt=attempt)
        except BaseException as exc:
            if not job_failure(exc):
                halted.set()
            raise

    pending = [i for i in range(len(jobs)) if i not in restored]
    try:
        with ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix='ara-search') as pool:
            for attempt in (1, 2):
                if halted.is_set() or not pending:
                    break
                # Retry only after all initial jobs drain, ordered independently
                # of completion timing. A fresh engine discards failed licenses.
                if attempt == 2:
                    for index in pending:
                        engine = new_engine()
                        engine._search_serial = index % 2
                        jobs[index] = (engine, jobs[index][1])
                queue = iter(pending)
                futures = {}
                retry = []
                while True:
                    # Until an inference is seen, never dispatch beyond the
                    # remaining completion allowance, even with parallel jobs.
                    slots = concurrency if not pause_after or accepted else min(concurrency, pause_after - completed)
                    while not halted.is_set() and len(futures) < slots:
                        index = next(queue, None)
                        if index is None:
                            break
                        futures[pool.submit(run, index, attempt)] = index
                    if not futures:
                        break
                    ready, _ = wait(futures, return_when=FIRST_COMPLETED)
                    for future in sorted(ready, key=lambda f: futures[f]):
                        index = futures.pop(future)
                        if future.cancelled():
                            continue
                        try:
                            results[index] = future.result()
                            if results[index] is not None:
                                completed += 1
                        except BaseException as exc:
                            failures[index] = type(exc).__name__
                            if job_failure(exc):
                                retry.append(index)
                            else:
                                fatal[index] = exc
                                halted.set()
                                for queued in futures:
                                    queued.cancel()
                        if pause_after and not accepted:
                            accepted = accepted_inferences(publication.journals[index])
                    if pause_after and completed >= pause_after and accepted == 0 and not fatal:
                        paused = True
                        halted.set()
                pending = sorted(retry)
    finally:
        publication.publish()
    pause = write_pause(log, publication, jobs, results, attempts, restored, completed, pause_after) if paused else None
    log.record('search_phase_finished', status='stopped' if fatal else 'paused' if paused else
               'partial' if any(result is None for result in results) else 'complete',
               jobs=[dict(job_index=i, goal=goal.to_dict(), attempts=attempts[i],
                          status='completed' if results[i] is not None else
                                 'failed' if attempts[i] else 'cancelled',
                          failure=failures.get(i)) for i, (_, goal) in enumerate(jobs)])
    return results, fatal[min(fatal)] if fatal else pause
