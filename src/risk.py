from __future__ import annotations

from dataclasses import dataclass

from src.state import BotState


@dataclass(frozen=True)
class RiskLimits:
    max_orders_per_day: int
    max_daily_loss_pct: float
    max_positions: int
    max_yen_per_symbol: int


class RiskManager:
    def __init__(self, limits: RiskLimits) -> None:
        self.limits = limits

    def can_place_order(self, state: BotState) -> bool:
        return state.orders_today < self.limits.max_orders_per_day

    def register_order(self, state: BotState) -> None:
        state.orders_today += 1

    def reached_daily_order_limit(self, state: BotState) -> bool:
        return state.orders_today >= self.limits.max_orders_per_day
