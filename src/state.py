from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict


def _today_str() -> str:
    return date.today().isoformat()


@dataclass
class BotState:
    last_reset_date: str = field(default_factory=_today_str)
    orders_today: int = 0
    errors_in_row: int = 0
    stopped_reason: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "last_reset_date": self.last_reset_date,
            "orders_today": self.orders_today,
            "errors_in_row": self.errors_in_row,
            "stopped_reason": self.stopped_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BotState":
        return cls(
            last_reset_date=str(data.get("last_reset_date", _today_str())),
            orders_today=int(data.get("orders_today", 0)),
            errors_in_row=int(data.get("errors_in_row", 0)),
            stopped_reason=data.get("stopped_reason"),
        )


def load_state(state_dir: Path) -> BotState:
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "state.json"
    if not path.exists():
        return BotState()
    with path.open("r", encoding="utf-8") as file:
        return BotState.from_dict(json.load(file))


def save_state(state_dir: Path, state: BotState) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "state.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(state.to_dict(), file, ensure_ascii=False, indent=2)
        file.write("\n")
