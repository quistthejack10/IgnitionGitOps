"""Generic TCP/UDP driver (PRD FR-C4).

M3: raw socket client + listener with configurable framing (delimiter, fixed-length,
length-prefixed), encoding (ASCII, hex, binary struct unpack), and a test console. Covers
barcode scanners, scales, printers, serial-over-IP. Built on asyncio sockets.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from forge_common.events import Event

from app.base import Connection, Source


class TcpConnection(Connection):
    async def connect(self) -> None:
        raise NotImplementedError("TCP/UDP connect (M3)")

    async def test(self) -> bool:
        raise NotImplementedError("TCP/UDP test console (M3)")


class TcpFrameSource(Source):
    async def stream(self) -> AsyncIterator[Event]:
        raise NotImplementedError("TCP framed-read stream (M3)")
        yield  # pragma: no cover
