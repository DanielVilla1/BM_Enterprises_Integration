# ===== AI GENERATED: rate_limiter =====
# Purpose: In-process sliding-window counters for auth failures and webhooks
# Inputs: a key (client address + purpose) and a window length
# Returns: counts used by providers to answer 429
# Flow:
# 1. record() timestamps an event for a key
# 2. count() prunes old events and returns how many remain
# Single-process only: with several workers each keeps its own counts.

import threading
import time
from collections import deque
from collections.abc import Callable

MAXIMUM_TRACKED_KEYS = 50000


class SlidingWindowLimiter:
    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._events: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def record(self, key: str) -> None:
        with self._lock:
            if len(self._events) >= MAXIMUM_TRACKED_KEYS and key not in self._events:
                self._events.clear()
            self._events.setdefault(key, deque()).append(self._clock())

    def count(self, key: str, window_seconds: float) -> int:
        with self._lock:
            events = self._events.get(key)
            if events is None:
                return 0
            cutoff = self._clock() - window_seconds
            while events and events[0] <= cutoff:
                events.popleft()
            if not events:
                del self._events[key]
                return 0
            return len(events)

    def reset(self) -> None:
        with self._lock:
            self._events.clear()
