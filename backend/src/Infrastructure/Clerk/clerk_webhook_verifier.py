# ===== AI GENERATED: ClerkWebhookVerifier =====
# Purpose: Verify Clerk (Svix) webhook signatures over the raw body
# Inputs: signing secret, raw bytes, request headers
# Returns: parsed JSON payload or WebhookSignatureError
# Flow:
# 1. Fail closed when no secret is configured
# 2. Let svix validate id, timestamp and signature (it returns None)
# 3. Map any failure to WebhookSignatureError

import json

from svix.webhooks import Webhook, WebhookVerificationError

from ...Contract.i_webhook_verifier import WebhookSignatureError


class ClerkWebhookVerifier:
    """Implements IWebhookVerifier."""

    def __init__(self, signing_secret: str) -> None:
        self._signing_secret = signing_secret

    def verify(self, raw_body: bytes, headers: dict[str, str]) -> dict[str, object]:
        if not self._signing_secret:
            raise WebhookSignatureError("webhook secret not configured")
        try:
            Webhook(self._signing_secret).verify(raw_body, headers)
            verified_payload = json.loads(raw_body)
        except (
            WebhookVerificationError,
            ValueError,
            TypeError,
        ) as verification_error:  # ValueError covers bad JSON
            raise WebhookSignatureError("signature rejected") from verification_error
        if not isinstance(verified_payload, dict):
            raise WebhookSignatureError("payload is not an object")
        return verified_payload
