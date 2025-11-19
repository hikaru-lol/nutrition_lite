from __future__ import annotations

from datetime import datetime, timezone

from app.application.auth.ports.clock_port import ClockPort


class SystemClock(ClockPort):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)
