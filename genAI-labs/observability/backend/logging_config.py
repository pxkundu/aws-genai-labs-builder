"""Structured logging configuration for the observability lab."""

from __future__ import annotations

import logging
import os
from logging.config import dictConfig
from typing import Any, Dict

import structlog


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SERVICE_NAME = os.getenv("SERVICE_NAME", "genai-observability-service")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def configure_logging() -> None:
    """Configure standard logging and structlog for JSON output."""
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    pre_chain = [
        structlog.contextvars.merge_contextvars,
        timestamper,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "plain": {
                    "format": "%(message)s",
                },
                "json": {
                    "()": "python_json_logger.jsonlogger.JsonFormatter",
                    "fmt": "%(timestamp)s %(level)s %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "level": LOG_LEVEL,
                    "class": "logging.StreamHandler",
                    "formatter": "plain",
                }
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
                "uvicorn.error": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
                "uvicorn.access": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
                "": {"handlers": ["default"], "level": LOG_LEVEL},
            },
        }
    )

    structlog.configure(
        processors=pre_chain
        + [
            structlog.processors.add_logger_name,
            structlog.processors.EventRenamer("message"),
            add_service_metadata,
            redact_sensitive_keys,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(LOG_LEVEL)),
        context_class=structlog.contextvars.wrap_dict(dict),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def add_service_metadata(logger: Any, name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Inject service-level metadata into each log entry."""
    event_dict.setdefault("service", SERVICE_NAME)
    event_dict.setdefault("environment", ENVIRONMENT)
    return event_dict


REDACT_KEYS = {"authorization", "api_key", "password", "secret", "ssn"}
REDACTED = "[REDACTED]"


def redact_sensitive_keys(logger: Any, name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Redact sensitive information from log entries."""
    for key in list(event_dict.keys()):
        if key.lower() in REDACT_KEYS:
            event_dict[key] = REDACTED
    return event_dict
