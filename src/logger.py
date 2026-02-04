from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


@dataclass
class JsonlLogger:
    log_dir: Path

    def _log_path(self, now: datetime) -> Path:
        filename = f"{now:%Y-%m-%d}.jsonl"
        return self.log_dir / filename

    def log_event(self, event: str, payload: Dict[str, Any] | None = None) -> None:
        now = datetime.utcnow()
        record = {
            "timestamp": now.isoformat(timespec="seconds") + "Z",
            "event": event,
            "payload": payload or {},
        }
        self.log_dir.mkdir(parents=True, exist_ok=True)
        path = self._log_path(now)
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
