from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Signal:
    symbol: str
    action: str
    reason: str


def select_symbols() -> List[str]:
    return ["7203", "6758"]


def generate_signals(symbols: List[str]) -> List[Signal]:
    return [Signal(symbol=symbol, action="HOLD", reason="paper_mode") for symbol in symbols]
