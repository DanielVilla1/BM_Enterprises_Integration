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

# AI MODIFIED: Cover memory saturation, concurrent admission and verified-account budgets.


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


def test_key_saturation_does_not_erase_an_existing_block() -> None:
    limiter = SlidingWindowLimiter(maximum_keys=2)
    assert limiter.allow("blocked", 1)
    assert limiter.allow("other", 1)
    for number in range(10):
        assert not limiter.allow(f"new-{number}", 1)
        assert not limiter.allow("blocked", 1)
    assert limiter.count("blocked", 60) == 1


def test_event_capacity_fails_closed_and_expired_keys_are_reclaimed() -> None:
    now = {"value": 1000.0}
    limiter = SlidingWindowLimiter(clock=lambda: now["value"], maximum_keys=2, maximum_events=2)
    assert limiter.allow("first", 10)
    assert limiter.allow("first", 10)
    assert not limiter.allow("second", 10)
    now["value"] += 61
    assert limiter.allow("second", 10)
    assert limiter.count("first", 60) == 0


def test_concurrent_admissions_never_exceed_the_budget() -> None:
    from concurrent.futures import ThreadPoolExecutor

    limiter = SlidingWindowLimiter()
    with ThreadPoolExecutor(max_workers=16) as executor:
        decisions = list(executor.map(lambda _number: limiter.allow("same", 10), range(100)))
    assert sum(decisions) == 10
    assert limiter.count("same", 60) == 10


def test_successful_api_calls_are_limited_per_verified_employee(
    client, employees, headers_for, monkeypatch
) -> None:
    tightened = providers.get_settings().model_copy(update={"rate_limit_api_user_per_minute": 2})
    monkeypatch.setattr(providers, "get_settings", lambda: tightened)
    first = employees.create((RoleCode.DRIVER,))
    second = employees.create((RoleCode.DRIVER,))
    assert [client.get("/api/v1/me", headers=headers_for(first)).status_code for _ in range(3)] == [
        200,
        200,
        429,
    ]
    assert client.get("/api/v1/me", headers=headers_for(second)).status_code == 200


def test_forwarded_header_cannot_reset_the_peer_ip_budget(client, monkeypatch) -> None:
    tightened = providers.get_settings().model_copy(update={"rate_limit_api_ip_per_minute": 2})
    monkeypatch.setattr(providers, "get_settings", lambda: tightened)
    statuses = [
        client.get("/api/v1/me", headers={"X-Forwarded-For": f"192.0.2.{number}"}).status_code
        for number in range(3)
    ]
    assert statuses == [401, 401, 429]


def test_upload_budget_blocks_before_sanitizing_or_storing(
    client, session_factory, employees, monkeypatch, fake_storage
) -> None:
    from backend.tests.conftest import auth_headers
    from backend.tests.dispatch_support import World
    from backend.tests.image_support import make_jpeg

    tightened = providers.get_settings().model_copy(update={"rate_limit_upload_user_per_minute": 1})
    monkeypatch.setattr(providers, "get_settings", lambda: tightened)
    world = World(client, session_factory, employees)
    delivered = world.delivered_trip()
    url = f"/api/v1/trips/{delivered.trip_id}/or-documents"
    response = client.post(
        url,
        headers=auth_headers(delivered.driver),
        files={"file": ("or.jpg", make_jpeg(), "image/jpeg")},
    )
    assert response.status_code == 201
    stored_paths = set(fake_storage.objects)
    blocked = client.post(
        url,
        headers=auth_headers(delivered.driver),
        files={"file": ("or.jpg", b"not an image", "image/jpeg")},
    )
    assert blocked.status_code == 429
    assert blocked.headers["retry-after"] == "60"
    assert set(fake_storage.objects) == stored_paths


def test_security_headers_cover_success_and_throttled_responses(
    client, employees, headers_for, monkeypatch
) -> None:
    tightened = providers.get_settings().model_copy(update={"rate_limit_api_user_per_minute": 1})
    monkeypatch.setattr(providers, "get_settings", lambda: tightened)
    person = employees.create((RoleCode.DRIVER,))
    for expected in (200, 429):
        response = client.get("/api/v1/me", headers=headers_for(person))
        assert response.status_code == expected
        assert response.headers["cache-control"] == "no-store"
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
