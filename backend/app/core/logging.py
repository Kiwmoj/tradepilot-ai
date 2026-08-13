"""Structured logging configuration."""

import logging
import sys
from typing import Any, Optional

from app.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)

    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if settings.log_format == "json":
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s",'
            '"message":"%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
    handler.setFormatter(formatter)
    root.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(
    logger: logging.Logger,
    event_type: str,
    message: str,
    symbol: Optional[str] = None,
    user_id: Optional[int] = None,
    **kwargs: Any,
) -> None:
    extra = {"event_type": event_type, "symbol": symbol, "user_id": user_id, **kwargs}
    logger.info("[%s] %s | %s", event_type, message, {k: v for k, v in extra.items() if v is not None})
