from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")


@dataclass(frozen=True)
class MarketSession:
    start: time
    end: time


SESSIONS = (
    MarketSession(start=time(9, 0), end=time(11, 30)),
    MarketSession(start=time(12, 30), end=time(15, 30)),
)


def is_weekday(now: datetime) -> bool:
    return now.weekday() < 5


def is_market_open(now: datetime | None = None) -> bool:
    current = now.astimezone(JST) if now else datetime.now(JST)
    if not is_weekday(current):
        return False
    current_time = current.time()
    return any(session.start <= current_time <= session.end for session in SESSIONS)


def current_jst_date(now: datetime | None = None) -> str:
    current = now.astimezone(JST) if now else datetime.now(JST)
    return current.date().isoformat()
