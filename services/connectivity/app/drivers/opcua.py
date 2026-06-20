"""OPC-UA driver (PRD FR-C1).

M3: browse address space in-UI, subscribe to monitored items, read/write nodes,
Basic256Sha256 + username/cert auth, auto-reconnect with subscription transfer (via asyncua).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from forge_common.events import Event

from app.base import Connection, Source


class OpcUaConnection(Connection):
    async def connect(self) -> None:
        raise NotImplementedError("OPC-UA connect (M3)")

    async def test(self) -> bool:
        raise NotImplementedError("OPC-UA test-before-save (M3)")


class OpcUaSubscriptionSource(Source):
    def __init__(self, connection: OpcUaConnection, node_ids: list[str]) -> None:
        self.connection = connection
        self.node_ids = node_ids

    async def stream(self) -> AsyncIterator[Event]:
        raise NotImplementedError("OPC-UA monitored-item stream (M3)")
        yield  # pragma: no cover
