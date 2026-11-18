# ===== AI GENERATED: sprint6_load_acceptance =====
# Purpose: Measure the specified 30-trip/20-user/10-request-per-second development workload.
# Inputs: Isolated test DB and in-process ASGI app; no production credentials or external storage.
# Returns: Request failures and measured latency percentiles in a standalone JSON report.
# Flow: Seed real workflow trips; pace 300 authenticated report reads; measure every response.

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from statistics import mean

import pytest

from backend.src.Entity.access import RoleCode
from backend.tests.conftest import USING_POSTGRES, auth_headers
from backend.tests.test_finance_workflows import completed
from backend.tests.test_finance_workflows import finance_world as finance_world


@pytest.mark.skipif(os.environ.get("RUN_LOAD_TESTS") != "1", reason="opt-in 30-second load run")
def test_thirty_trips_twenty_users_ten_requests_per_second(finance_world, tmp_path):
    world = finance_world
    for _trip_index in range(30):
        completed(world)
    roles = list(RoleCode)
    actors = [world.employees.create((roles[index % len(roles)],)) for index in range(20)]
    headers = [auth_headers(actor) for actor in actors]
    scheduled_start = time.perf_counter()

    def request_report(index):
        started = time.perf_counter()
        response = world.client.get("/api/v1/finance/reports", headers=headers[index % len(headers)])
        return response.status_code, (time.perf_counter() - started) * 1000

    with ThreadPoolExecutor(max_workers=20) as executor:
        pending = []
        for index in range(300):
            delay = scheduled_start + index / 10 - time.perf_counter()
            if delay > 0:
                time.sleep(delay)
            pending.append(executor.submit(request_report, index))
        outcomes = [future.result(timeout=30) for future in pending]
    durations = sorted(duration for _status, duration in outcomes)
    failures = [status for status, _duration in outcomes if status != 200]
    elapsed = time.perf_counter() - scheduled_start
    report = {
        "database": "PostgreSQL" if USING_POSTGRES else "SQLite",
        "transport": "in-process ASGI",
        "trips": 30,
        "users": 20,
        "target_requests_per_second": 10,
        "requests": len(outcomes),
        "failures": len(failures),
        "elapsed_seconds": round(elapsed, 2),
        "achieved_requests_per_second": round(len(outcomes) / elapsed, 2),
        "mean_ms": round(mean(durations), 2),
        "p50_ms": round(durations[149], 2),
        "p95_ms": round(durations[284], 2),
        "p99_ms": round(durations[296], 2),
        "scope": "Local application/database test; excludes real Clerk, network/TLS and Supabase.",
    }
    destination = Path(os.environ.get("LOAD_TEST_REPORT", str(tmp_path / "sprint-5-6-load.json")))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    assert not failures, f"Load run returned unsuccessful statuses: {failures}"
    assert elapsed <= 35, "The 30-second workload exceeded its 5-second drain allowance."
