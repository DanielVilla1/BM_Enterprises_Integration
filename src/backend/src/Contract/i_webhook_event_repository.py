# ===== AI GENERATED: IWebhookEventRepository =====
# Purpose: Port for the processed-webhook ledger (idempotency)
# Inputs: provider event id and type
# Returns: whether the event was newly recorded
# Flow:
# 1. try_register inserts once; a repeat returns False

from typing import Protocol


class IWebhookEventRepository(Protocol):
    def try_register(self, event_id: str, event_type: str) -> bool: ...
