# ===== AI GENERATED: clock =====
# Purpose: Business date in the Philippines (UTC+8, no daylight saving)
# Inputs: none
# Returns: today's date in Manila
# Flow:
# 1. Offset UTC by +8 hours; a fixed offset avoids needing tz databases

from datetime import UTC, date, datetime, timedelta, timezone

MANILA_OFFSET = timezone(timedelta(hours=8))


def manila_today() -> date:
    """Today's calendar date for BM Enterprises."""
    return datetime.now(UTC).astimezone(MANILA_OFFSET).date()
