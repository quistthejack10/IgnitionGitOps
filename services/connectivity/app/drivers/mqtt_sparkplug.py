"""MQTT + Sparkplug B driver (PRD FR-C2, FR-C3).

M3: connect to external brokers (TLS/client certs), subscribe/publish arbitrary topics with
JSON parsing; decode Sparkplug NBIRTH/DBIRTH/NDATA/DDATA, maintain metric state, honor
bdSeq/rebirth. Also bridges selected NATS subjects to the embedded broker's UNS (ADR-0003).
"""

from __future__ import annotations

from collections.abc import AsyncIterator

from forge_common.events import Event

from app.base import Connection, Sink, Source


class MqttConnection(Connection):
    async def connect(self) -> None:
        raise NotImplementedError("MQTT connect (M3)")

    async def test(self) -> bool:
        raise NotImplementedError("MQTT test-before-save (M3)")


class MqttSource(Source):
    async def stream(self) -> AsyncIterator[Event]:
        raise NotImplementedError("MQTT/Sparkplug subscribe stream (M3)")
        yield  # pragma: no cover


class MqttSink(Sink):
    async def write(self, event: Event) -> None:
        raise NotImplementedError("MQTT publish (M3)")
