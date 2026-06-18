"""Structured logging configuration using structlog."""
from __future__ import annotations

import logging
import sys

import structlog
from structlog.types import EventDict, Processor


def add_app_context(
    logger: logging.Logger,  # noqa: ARG001
    method_name: str,  # noqa: ARG001
    event_dict: EventDict,
) -> EventDict:
    event_dict["app"] = "myward"
    return event_dict


def setup_logging(debug: bool = False) -> None:
    """Configure structlog for the application."""
    log_level = logging.DEBUG if debug else logging.INFO

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_app_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if sys.stderr.isatty():
        # Human-readable in development
        processors: list[Processor] = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    else:
        # JSON in production / CI
        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Redirect stdlib logging through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)
