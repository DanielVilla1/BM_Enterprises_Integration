# ===== AI GENERATED: IWebhookVerifier =====
# Purpose: Port for verifying signed webhook deliveries
# Inputs: raw body bytes and request headers
# Returns: parsed payload or WebhookSignatureError
# Flow:
# 1. Signature is checked against the raw body, never re-serialized JSON

from typing import Protocol


class WebhookSignatureError(Exception):
    """Signature missing, malformed, stale or wrong."""


class IWebhookVerifier(Protocol):
    def verify(self, raw_body: bytes, headers: dict[str, str]) -> dict[str, object]: ...
