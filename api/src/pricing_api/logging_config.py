"""Structured (JSON) logging for pricing_api.

One JSON object per line on stdout -- readable by `docker compose logs
api` and greppable during an incident, without adding a new dependency
(the stdlib `logging` module is enough for this project's scale).
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

_RESERVED_ATTRS = set(vars(logging.makeLogRecord({})).keys())


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = {k: v for k, v in vars(record).items() if k not in _RESERVED_ATTRS}
        payload.update(extra)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("pricing_api")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger


logger = configure_logging()
