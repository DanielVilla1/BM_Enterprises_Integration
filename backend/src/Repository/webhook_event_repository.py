# ===== AI GENERATED: WebhookEventRepository =====
# Purpose: Idempotency ledger for provider webhook deliveries
# Inputs: Session
# Returns: True when the event id was newly recorded
# Flow:
# 1. Look up the event id
# 2. Insert when absent; report duplicate otherwise

from sqlalchemy.orm import Session

from .orm_models import ProcessedWebhookRow


class WebhookEventRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def try_register(self, event_id: str, event_type: str) -> bool:
        if self._session.get(ProcessedWebhookRow, event_id) is not None:
            return False
        self._session.add(ProcessedWebhookRow(event_id=event_id, event_type=event_type))
        self._session.flush()
        return True
