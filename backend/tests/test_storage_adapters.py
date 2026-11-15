# ===== AI GENERATED: test_storage_adapters =====
# Purpose: Interface tests for the Supabase Storage client, image sanitizer, body cap
# Inputs: httpx mock transport, generated images, a raw ASGI harness
# Returns: pass/fail
# Flow:
# 1. Storage: auth headers, paths, bounded retries, strict response checks
# 2. Sanitizer: decoding, pixel limits, colour modes
# 3. Body cap: streamed bodies without Content-Length are cut off

import asyncio
import json
from io import BytesIO

import httpx
import pytest
from PIL import Image

from backend.src.Contract.i_storage import InvalidImageError, StorageError
from backend.src.Infrastructure.Imaging.pillow_image_sanitizer import PillowImageSanitizer
from backend.src.Infrastructure.Supabase.supabase_object_storage import SupabaseObjectStorage
from backend.src.request_limits import BodySizeLimitMiddleware

BUCKET = "delivery-documents"


def _storage(handler, sleeps: list[float] | None = None) -> SupabaseObjectStorage:
    return SupabaseObjectStorage(
        "https://project.supabase.test",
        "service-key-fake",
        BUCKET,
        transport=httpx.MockTransport(handler),
        sleeper=(sleeps.append if sleeps is not None else (lambda _seconds: None)),
    )


def test_upload_sends_the_service_key_and_a_private_path() -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(
            url=str(request.url),
            auth=request.headers["authorization"],
            api_key=request.headers["apikey"],
            content_type=request.headers["content-type"],
            upsert=request.headers["x-upsert"],
            body=request.content,
        )
        return httpx.Response(200, json={"Key": "ok"})

    _storage(handler).put("signed-or/trip 1/file name.jpg", b"IMAGE", "image/jpeg")
    assert seen["url"] == (
        f"https://project.supabase.test/storage/v1/object/{BUCKET}/signed-or/trip%201/file%20name.jpg"
    )
    assert seen["auth"] == "Bearer service-key-fake" and seen["api_key"] == "service-key-fake"
    assert seen["content_type"] == "image/jpeg" and seen["upsert"] == "false" and seen["body"] == b"IMAGE"


def test_upload_retries_server_errors_with_backoff_then_succeeds() -> None:
    attempts = {"count": 0}
    sleeps: list[float] = []

    def handler(_request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        return httpx.Response(503) if attempts["count"] < 3 else httpx.Response(200)

    _storage(handler, sleeps).put("a/b.jpg", b"x", "image/jpeg")
    assert attempts["count"] == 3 and sleeps == [0.5, 1.0]


def test_upload_gives_up_after_bounded_attempts_and_never_retries_client_errors() -> None:
    attempts = {"count": 0}

    def always_down(_request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        return httpx.Response(500)

    with pytest.raises(StorageError):
        _storage(always_down).put("a/b.jpg", b"x", "image/jpeg")
    assert attempts["count"] == 3
    attempts["count"] = 0

    def forbidden(_request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        return httpx.Response(403)

    with pytest.raises(StorageError):
        _storage(forbidden).put("a/b.jpg", b"x", "image/jpeg")
    assert attempts["count"] == 1


def test_upload_retries_transport_failures() -> None:
    attempts = {"count": 0}

    def flaky(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise httpx.ConnectError("refused", request=request)
        return httpx.Response(200)

    _storage(flaky).put("a/b.jpg", b"x", "image/jpeg")
    assert attempts["count"] == 2


def test_signed_url_is_built_from_the_response_and_requests_a_short_expiry() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content)
        return httpx.Response(200, json={"signedURL": f"/object/sign/{BUCKET}/a/b.jpg?token=abc"})

    url = _storage(handler).create_signed_url("a/b.jpg", 120)
    assert url == f"https://project.supabase.test/storage/v1/object/sign/{BUCKET}/a/b.jpg?token=abc"
    assert captured["body"] == {"expiresIn": 120}
    assert captured["url"].endswith(f"/object/sign/{BUCKET}/a/b.jpg")


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(404),
        httpx.Response(200, content=b"not json"),
        httpx.Response(200, json={"other": "shape"}),
        httpx.Response(200, json={"signedURL": "https://evil.example/steal"}),
        httpx.Response(200, json={"signedURL": 12}),
    ],
)
def test_signed_url_rejects_failures_and_unexpected_shapes(response: httpx.Response) -> None:
    with pytest.raises(StorageError):
        _storage(lambda _request: response).create_signed_url("a/b.jpg", 60)


def test_unconfigured_storage_fails_closed() -> None:
    with pytest.raises(StorageError):
        SupabaseObjectStorage("", "", BUCKET).put("a/b.jpg", b"x", "image/jpeg")
    with pytest.raises(StorageError):
        SupabaseObjectStorage("", "", BUCKET).create_signed_url("a/b.jpg", 60)


def test_delete_is_best_effort() -> None:
    _storage(lambda _request: httpx.Response(500)).delete("a/b.jpg")

    def broken(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    _storage(broken).delete("a/b.jpg")
    SupabaseObjectStorage("", "", BUCKET).delete("a/b.jpg")


def _encode(image: Image.Image, image_format: str) -> bytes:
    buffer = BytesIO()
    image.save(buffer, image_format)
    return buffer.getvalue()


def test_sanitizer_converts_unusual_colour_modes_for_jpeg() -> None:
    cmyk = _encode(Image.new("CMYK", (10, 10), (0, 0, 0, 0)), "JPEG")
    result = PillowImageSanitizer().sanitize(cmyk)
    assert result.content_type == "image/jpeg" and result.extension == "jpg"
    with Image.open(BytesIO(result.content)) as stored:
        assert stored.mode == "RGB"


def test_sanitizer_keeps_png_transparency() -> None:
    original = _encode(Image.new("RGBA", (8, 8), (1, 2, 3, 128)), "PNG")
    result = PillowImageSanitizer().sanitize(original)
    with Image.open(BytesIO(result.content)) as stored:
        assert stored.mode == "RGBA" and stored.getpixel((0, 0))[3] == 128


def test_sanitizer_rejects_images_with_too_many_pixels() -> None:
    big = _encode(Image.new("RGB", (100, 100)), "JPEG")
    with pytest.raises(InvalidImageError):
        PillowImageSanitizer(maximum_pixels=5000).sanitize(big)


def test_sanitizer_rejects_truncated_images() -> None:
    complete = _encode(Image.effect_noise((200, 200), 80).convert("RGB"), "JPEG")
    with pytest.raises(InvalidImageError):
        PillowImageSanitizer().sanitize(complete[: len(complete) // 3])


def _run_streaming(maximum: int, chunks: list[bytes]):
    sent: list[dict] = []

    async def application(scope, receive, send):
        while True:
            message = await receive()
            if not message.get("more_body"):
                break
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    queue = [{"type": "http.request", "body": chunk, "more_body": True} for chunk in chunks[:-1]]
    queue.append({"type": "http.request", "body": chunks[-1], "more_body": False})

    async def receive():
        return queue.pop(0)

    async def send(message):
        sent.append(message)

    scope = {"type": "http", "headers": [], "state": {"trace_id": "trace123"}}
    asyncio.run(BodySizeLimitMiddleware(application, maximum)(scope, receive, send))
    return sent


def test_streamed_bodies_without_a_length_are_cut_off_at_the_cap() -> None:
    sent = _run_streaming(10, [b"123456", b"123456"])
    assert sent[0]["status"] == 413
    assert json.loads(sent[1]["body"])["code"] == "PAYLOAD_TOO_LARGE"
    ok = _run_streaming(10, [b"12345", b"12345"])
    assert ok[0]["status"] == 200
