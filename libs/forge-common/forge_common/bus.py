"""Thin NATS JetStream wrapper that speaks the Event envelope.

This is the Python side of the polyglot seam (ADR-0003). The Go flow-engine connects to the
same NATS and exchanges the same JSON event envelope. Real JetStream stream/consumer setup,
ack handling, and dead-letter wiring land in M1/M4 — this stub establishes the interface.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import nats

from forge_common.events import Event

Handler = Callable[[Event], Awaitable[None]]


class NatsBus:
    """Connect/publish/subscribe over NATS using the shared Event envelope."""

    def __init__(self, url: str) -> None:
        self._url = url
        self._nc: nats.NATS | None = None

    async def connect(self) -> None:
        self._nc = await nats.connect(self._url)

    async def close(self) -> None:
        if self._nc is not None:
            await self._nc.drain()
            self._nc = None

    async def publish(self, subject: str, event: Event) -> None:
        if self._nc is None:
            raise RuntimeError("NatsBus.connect() must be called before publish()")
        await self._nc.publish(subject, event.model_dump_json().encode())

    async def subscribe(self, subject: str, handler: Handler) -> None:
        if self._nc is None:
            raise RuntimeError("NatsBus.connect() must be called before subscribe()")

        async def _wrap(msg: "nats.aio.msg.Msg") -> None:  # type: ignore[name-defined]
            await handler(Event.model_validate_json(msg.data))

        await self._nc.subscribe(subject, cb=_wrap)
