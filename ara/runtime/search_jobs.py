"""Run independent searches, then retry job-local failures once in input order."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event

from ara.runtime.budget import BudgetStop
from ara.runtime.calls import CountRequestRefused, Rejected
from ara.runtime.search_publication import SearchPublication


def job_failure(exc):
    # ModelCalls has already exhausted transport/validation retries. Accounting,
    # context and infrastructure stops must never be downgraded to missing work.
    return isinstance(exc, (Rejected, CountRequestRefused)) or (
        isinstance(exc, BudgetStop) and exc.scope != 'run')


def run_search_jobs(log, jobs, concurrency, new_engine, *, restored=None):
    publication = SearchPublication(log, [goal for _, goal in jobs])
    halted = Event()
    restored = restored or {}
    results = [restored.get(i) for i in range(len(jobs))]
    attempts = [0] * len(jobs)
    failures = {}
    fatal = {}

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
                futures = {pool.submit(run, index, attempt): index for index in pending}
                retry = []
                for future in as_completed(futures):
                    index = futures[future]
                    if future.cancelled():
                        continue
                    try:
                        results[index] = future.result()
                    except BaseException as exc:
                        failures[index] = type(exc).__name__
                        if job_failure(exc):
                            retry.append(index)
                        else:
                            fatal[index] = exc
                            halted.set()
                            for queued in futures:
                                queued.cancel()
                pending = sorted(retry)
    finally:
        publication.publish()
    log.record('search_phase_finished', status='stopped' if fatal else
               'partial' if any(result is None for result in results) else 'complete',
               jobs=[dict(job_index=i, goal=goal.to_dict(), attempts=attempts[i],
                          status='completed' if results[i] is not None else
                                 'failed' if attempts[i] else 'cancelled',
                          failure=failures.get(i)) for i, (_, goal) in enumerate(jobs)])
    return results, fatal[min(fatal)] if fatal else None
