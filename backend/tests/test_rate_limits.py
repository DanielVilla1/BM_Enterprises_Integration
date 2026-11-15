# ===== AI GENERATED: test_rate_limits =====
# Purpose: Rate limits on failed authentication and the public webhook (API4)
# Inputs: repeated bad requests from one client address
# Returns: pass/fail
# Flow:
# 1. Failed auth attempts beyond the limit return 429 problem+json
# 2. The sliding window expires old events
# 3. The webhook endpoint is throttled per client

from backend.src import providers
from backend.src.Entity.access import RoleCode
from backend.src.rate_limiter import SlidingWindowLimiter


def test_repeated_failed_authentication_is_throttled(client) -> None:
    statuses = [
        client.get("/api/v1/me", headers={"Authorization": "Bearer junk"}).status_code for _ in range(21)
    ]
    assert statuses[:20] == [401] * 20
    assert statuses[20] == 429
    blocked = client.get("/api/v1/me")
    assert blocked.status_code == 429
    assert blocked.headers["retry-after"] == "60"
    assert blocked.headers["content-type"].startswith("application/problem+json")
    assert blocked.json()["code"] == "RATE_LIMITED"


def test_successful_requests_do_not_consume_the_failure_budget(client, employees, headers_for) -> None:
    person = employees.create((RoleCode.DRIVER,))
    statuses = [client.get("/api/v1/me", headers=headers_for(person)).status_code for _ in range(30)]
    assert set(statuses) == {200}


def test_sliding_window_forgets_old_events() -> None:
    now = {"value": 1000.0}
    limiter = SlidingWindowLimiter(clock=lambda: now["value"])
    for _ in range(3):
        limiter.record("client")
    assert limiter.count("client", 60) == 3
    now["value"] += 61
    assert limiter.count("client", 60) == 0
    limiter.record("client")
    assert limiter.count("client", 60) == 1


def test_webhook_endpoint_is_throttled_per_client(client, monkeypatch) -> None:
    tightened = providers.get_settings().model_copy(update={"rate_limit_webhook_per_minute": 3})
    monkeypatch.setattr(providers, "get_settings", lambda: tightened)
    statuses = [
        client.post(
            "/api/v1/webhooks/clerk", content=b"{}", headers={"content-type": "application/json"}
        ).status_code
        for _ in range(5)
    ]
    assert statuses == [400, 400, 400, 429, 429]
