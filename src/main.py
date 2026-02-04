from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from src.kabu_api import KabuApiClient
from src.logger import JsonlLogger
from src.market_time import current_jst_date, is_market_open
from src.risk import RiskLimits, RiskManager
from src.state import BotState, load_state, save_state
from src.strategy import generate_signals, select_symbols


@dataclass(frozen=True)
class Settings:
    base_url: str
    password: str
    max_orders_per_day: int
    max_daily_loss_pct: float
    max_positions: int
    max_yen_per_symbol: int
    stop_file: Path
    loop_interval_sec: int
    out_of_market_sleep_sec: int
    error_max_count: int
    log_dir: Path
    state_dir: Path


REQUIRED_ENV_VARS = (
    "KABU_API_BASE_URL",
    "KABU_API_PASSWORD",
    "MAX_ORDERS_PER_DAY",
    "MAX_DAILY_LOSS_PCT",
    "MAX_POSITIONS",
    "MAX_YEN_PER_SYMBOL",
)


def load_settings() -> Settings:
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise SystemExit(f"Missing required env vars: {', '.join(missing)}")
    return Settings(
        base_url=os.environ["KABU_API_BASE_URL"],
        password=os.environ["KABU_API_PASSWORD"],
        max_orders_per_day=int(os.environ["MAX_ORDERS_PER_DAY"]),
        max_daily_loss_pct=float(os.environ["MAX_DAILY_LOSS_PCT"]),
        max_positions=int(os.environ["MAX_POSITIONS"]),
        max_yen_per_symbol=int(os.environ["MAX_YEN_PER_SYMBOL"]),
        stop_file=Path(os.getenv("STOP_FILE", "STOP")),
        loop_interval_sec=int(os.getenv("LOOP_INTERVAL_SEC", "30")),
        out_of_market_sleep_sec=int(os.getenv("OUT_OF_MARKET_SLEEP_SEC", "60")),
        error_max_count=int(os.getenv("ERROR_MAX_COUNT", "3")),
        log_dir=Path(os.getenv("LOG_DIR", "data/logs")),
        state_dir=Path(os.getenv("STATE_DIR", "data/state")),
    )


def reset_daily_state(state: BotState, logger: JsonlLogger, state_dir: Path) -> None:
    state.last_reset_date = current_jst_date()
    state.orders_today = 0
    state.errors_in_row = 0
    state.stopped_reason = None
    save_state(state_dir, state)
    logger.log_event("daily_reset", {"date": state.last_reset_date})


def main() -> int:
    load_dotenv()
    settings = load_settings()
    logger = JsonlLogger(settings.log_dir)
    state = load_state(settings.state_dir)
    risk = RiskManager(
        RiskLimits(
            max_orders_per_day=settings.max_orders_per_day,
            max_daily_loss_pct=settings.max_daily_loss_pct,
            max_positions=settings.max_positions,
            max_yen_per_symbol=settings.max_yen_per_symbol,
        )
    )

    try:
        token = KabuApiClient(settings.base_url, settings.password).get_token()
    except Exception as exc:
        logger.log_event("startup_error", {"error": str(exc)})
        raise

    logger.log_event("startup", {"paper": True, "token_ok": bool(token)})

    while True:
        if settings.stop_file.exists():
            logger.log_event("stop_file_detected", {"path": str(settings.stop_file)})
            break

        if state.stopped_reason:
            logger.log_event("stopped", {"reason": state.stopped_reason})
            break

        current_date = current_jst_date()
        if current_date != state.last_reset_date:
            reset_daily_state(state, logger, settings.state_dir)

        try:
            if is_market_open():
                symbols = select_symbols()
                signals = generate_signals(symbols)
                logger.log_event(
                    "heartbeat",
                    {
                        "market_open": True,
                        "signals": [signal.__dict__ for signal in signals],
                        "orders_today": state.orders_today,
                    },
                )

                if risk.reached_daily_order_limit(state):
                    logger.log_event("risk_limit_reached", {"limit": "MAX_ORDERS_PER_DAY"})

                time.sleep(settings.loop_interval_sec)
            else:
                logger.log_event("market_closed", {"market_open": False})
                time.sleep(settings.out_of_market_sleep_sec)

            state.errors_in_row = 0
        except Exception as exc:
            state.errors_in_row += 1
            logger.log_event(
                "runtime_error",
                {"error": str(exc), "errors_in_row": state.errors_in_row},
            )
            if state.errors_in_row >= settings.error_max_count:
                state.stopped_reason = "error_limit_reached"
                save_state(settings.state_dir, state)
                logger.log_event("auto_stop", {"reason": state.stopped_reason})
                break

        save_state(settings.state_dir, state)

    save_state(settings.state_dir, state)
    logger.log_event("shutdown", {"orders_today": state.orders_today})
    return 0


if __name__ == "__main__":
    sys.exit(main())
