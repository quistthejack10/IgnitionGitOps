"""Typed mirror of schemas/event.schema.json — the bus envelope.

Keeping a pydantic model in sync with the JSON Schema lets Python services produce and
consume events with validation while the Go flow-engine validates against the same schema.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Event(BaseModel):
    """The envelope for every message on the NATS bus (CloudEvents-aligned)."""

    specversion: str = "1.0"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    source: str
    subject: str | None = None
    time: datetime = Field(default_factory=_now)
    datacontenttype: str = "application/json"
    traceparent: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
