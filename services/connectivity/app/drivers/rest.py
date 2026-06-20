"""REST/HTTP driver (PRD FR-C6).

M3: outbound request node (basic/bearer/API-key/OAuth2 client-credentials auth) and inbound
webhook endpoints that trigger flows. Built on httpx; inbound webhooks are registered on the
api-gateway and bridged to the bus.
"""

from __future__ import annotations

from forge_common.events import Event

from app.base import Connection, Sink


class RestConnection(Connection):
    async def connect(self) -> None:
        raise NotImplementedError("REST connect/auth (M3)")

    async def test(self) -> bool:
        raise NotImplementedError("REST test-before-save (M3)")


class RestSink(Sink):
    async def write(self, event: Event) -> None:
        raise NotImplementedError("REST outbound request (M3)")
