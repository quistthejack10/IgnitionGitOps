"""Prometheus metrics helpers (PRD FR-P5: Prometheus endpoint on every service)."""

from __future__ import annotations

from prometheus_client import Counter, make_asgi_app

# Mount at /metrics on each FastAPI service.
metrics_app = make_asgi_app()

# Shared counters services can import and increment.
request_counter = Counter(
    "forge_requests_total",
    "Total requests handled, labelled by service and route.",
    ["service", "route"],
)
