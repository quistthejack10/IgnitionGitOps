"""Structured JSON logging (PRD NFR: structured JSON logs, SIEM-friendly)."""

from __future__ import annotations

import logging

import structlog


def get_logger(service_name: str, level: str = "INFO") -> structlog.stdlib.BoundLogger:
    """Return a structlog logger emitting JSON, bound to the service name."""
    logging.basicConfig(format="%(message)s", level=getattr(logging, level.upper(), logging.INFO))
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
    )
    return structlog.get_logger().bind(service=service_name)
