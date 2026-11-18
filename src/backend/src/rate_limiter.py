# ===== AI GENERATED: rate_limiter =====
# Purpose: Bounded, atomic per-process sliding-window request budgets.
# Inputs: Trusted client/account keys, positive limits and a monotonic clock.
# Returns: Admission decisions; saturation fails closed without clearing other budgets.
# Flow: Expire inactive keys, prune the current window, then atomically admit an event.
# AI MODIFIED: Bound both key/event memory and avoid resets and count/record races.

import threading
import time
from collections import OrderedDict, deque
from collections.abc import Callable

WINDOW_SECONDS = 60.0
MAXIMUM_TRACKED_KEYS = 10000
MAXIMUM_TRACKED_EVENTS = 100000
MAXIMUM_EVENTS_PER_KEY = 1000


class SlidingWindowLimiter:
    """Single-process budgets; a shared edge/store is required across workers."""

    def __init__(
        self,
        clock: Callable[[], float] = time.monotonic,
        maximum_keys: int = MAXIMUM_TRACKED_KEYS,
        maximum_events: int = MAXIMUM_TRACKED_EVENTS,
    ) -> None:
        if maximum_keys < 1 or maximum_events < 1:
            raise ValueError("Limiter capacities must be positive")
        self._clock = clock
        self._maximum_keys = maximum_keys
        self._maximum_events = maximum_events
        self._events: OrderedDict[str, deque[float]] = OrderedDict()
        self._event_count = 0
        self._lock = threading.Lock()

    def _prune(self, events: deque[float], cutoff: float) -> None:
        while events and events[0] <= cutoff:
            events.popleft()
            self._event_count -= 1

    def _expire(self, now: float) -> None:
        cutoff = now - WINDOW_SECONDS
        while self._events:
            key = next(iter(self._events))
            events = self._events[key]
            if events[-1] > cutoff:
                break
            self._event_count -= len(self._events.pop(key))

    def allow(self, key: str, maximum: int, *, consume: bool = True) -> bool:
        """Check and optionally consume one event under the same lock; denials add nothing."""
        if not 1 <= maximum <= MAXIMUM_EVENTS_PER_KEY:
            raise ValueError("Rate limit must be between 1 and 1000 per minute")
        with self._lock:
            now = self._clock()
            self._expire(now)
            events = self._events.get(key)
            if events is not None:
                self._prune(events, now - WINDOW_SECONDS)
                if len(events) >= maximum:
                    return False
            elif len(self._events) >= self._maximum_keys:
                return False
            if self._event_count >= self._maximum_events:
                # Reclaim expired prefixes on otherwise active keys before failing closed.
                for tracked in self._events.values():
                    self._prune(tracked, now - WINDOW_SECONDS)
                if self._event_count >= self._maximum_events:
                    return False
            if consume:
                if events is None:
                    events = self._events[key] = deque()
                events.append(now)
                self._event_count += 1
                self._events.move_to_end(key)
            return True

    def record(self, key: str) -> bool:
        """Record a bounded event; callers can detect capacity exhaustion."""
        return self.allow(key, MAXIMUM_EVENTS_PER_KEY)

    def count(self, key: str, window_seconds: float) -> int:
        """Read a counter within the supported one-minute retention window."""
        if not 0 < window_seconds <= WINDOW_SECONDS:
            raise ValueError("Window must be within one minute")
        with self._lock:
            now = self._clock()
            self._expire(now)
            events = self._events.get(key)
            if events is None:
                return 0
            self._prune(events, now - WINDOW_SECONDS)
            return sum(moment > now - window_seconds for moment in events)

    def reset(self) -> None:
        """Clear counters for isolated tests or an explicit process lifecycle reset."""
        with self._lock:
            self._events.clear()
            self._event_count = 0
