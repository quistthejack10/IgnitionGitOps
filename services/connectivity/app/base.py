"""Connectivity core abstractions (PRD §7.1).

A `Connection` is a configured endpoint. It exposes `Source`s (subscriptions/polls that emit
Events onto the bus) and `Sink`s (writes). Every Sink is wrapped by store-and-forward so a
down destination buffers to disk and drains in order on recovery (FR-C12).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from forge_common.events import Event


class ConnectionState(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class ConnectionHealth:
    """Health row for the connection dashboard (FR-C11)."""

    state: ConnectionState = ConnectionState.DISCONNECTED
    last_error: str | None = None
    latency_ms: float | None = None
    throughput_per_sec: float | None = None


class Source(ABC):
    """Emits inbound data as a stream of Events."""

    @abstractmethod
    async def stream(self) -> AsyncIterator[Event]:
        """Yield Events as data arrives (subscription) or is polled."""
        raise NotImplementedError
        yield  # pragma: no cover - makes this an async generator for typing


class Sink(ABC):
    """Writes outbound data. Wrapped by store-and-forward (FR-C12)."""

    @abstractmethod
    async def write(self, event: Event) -> None: ...


class Connection(ABC):
    """A configured endpoint exposing sources and sinks."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.health = ConnectionHealth()

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def test(self) -> bool:
        """Test-before-save: validate config/credentials without persisting (FR-C11)."""


@dataclass
class StoreAndForwardBuffer:
    """Disk-backed buffer in front of every Sink (FR-C12).

    M3 implements the on-disk queue with a configurable cap + overflow policy and in-order
    drain on recovery. This stub captures the contract.
    """

    cap: int = 100_000
    overflow_policy: str = "drop-oldest"  # or "block"
    _pending: list[Event] = field(default_factory=list)

    async def enqueue(self, event: Event) -> None:
        raise NotImplementedError("StoreAndForwardBuffer.enqueue (M3)")

    async def drain(self, sink: Sink) -> None:
        raise NotImplementedError("StoreAndForwardBuffer.drain (M3)")
