# ===== AI GENERATED: request_limits =====
# Purpose: Hard cap on request body size for every route (OWASP API4)
# Inputs: Content-Length header and the streamed body
# Returns: 413 application/problem+json when the cap is exceeded
# Flow:
# 1. Reject early when the declared length is over the cap
# 2. Count streamed bytes as well (chunked bodies have no length)
# 3. Never reaches the application once over the cap

import json

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class BodyTooLargeError(Exception):
    """Raised inside the receive wrapper once the streamed body exceeds the cap."""


class BodySizeLimitMiddleware:
    def __init__(self, app: ASGIApp, maximum_bytes: int) -> None:
        self._app = app
        self._maximum_bytes = maximum_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        declared = dict(scope["headers"]).get(b"content-length", b"")
        if declared.isdigit() and int(declared) > self._maximum_bytes:
            await self._reject(scope, send)
            return
        received_bytes = 0
        response_started = False

        async def counting_receive() -> Message:
            nonlocal received_bytes
            message = await receive()
            if message["type"] == "http.request":
                received_bytes += len(message.get("body", b""))
                if received_bytes > self._maximum_bytes:
                    raise BodyTooLargeError
            return message

        async def tracking_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self._app(scope, counting_receive, tracking_send)
        except BodyTooLargeError:
            if not response_started:
                await self._reject(scope, send)

    async def _reject(self, scope: Scope, send: Send) -> None:
        trace_id = scope.get("state", {}).get("trace_id", "")
        body = json.dumps(
            {
                "type": "urn:bm-enterprises:problem:payload-too-large",
                "title": "Payload too large",
                "status": 413,
                "detail": "The request body is too large.",
                "code": "PAYLOAD_TOO_LARGE",
                "trace_id": trace_id,
            }
        ).encode()
        headers = [
            (b"content-type", b"application/problem+json"),
            (b"content-length", str(len(body)).encode()),
            (b"x-trace-id", str(trace_id).encode()),
        ]
        await send({"type": "http.response.start", "status": 413, "headers": headers})
        await send({"type": "http.response.body", "body": body})
