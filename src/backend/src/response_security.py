# ===== AI GENERATED: ResponseSecurityMiddleware =====
# Purpose: Prevent financial/identity responses from being cached or MIME-sniffed.
# Inputs: ASGI scope and response headers.
# Returns: API responses with explicit private-data controls.
# Flow: Add security headers before forwarding response start; never log bodies/tokens.

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ResponseSecurityMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def secure_response(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["Cache-Control"] = "no-store"
                headers["Pragma"] = "no-cache"
                headers["X-Content-Type-Options"] = "nosniff"
                headers["Referrer-Policy"] = "no-referrer"
                headers["X-Frame-Options"] = "DENY"
            await send(message)

        await self.app(scope, receive, secure_response if scope["type"] == "http" else send)
