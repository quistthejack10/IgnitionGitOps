"""Connection manager + health registry (PRD FR-C11).

Owns the lifecycle of all configured Connections and serves the health dashboard data
(state, latency, throughput, last error). Secrets are stored encrypted and never echoed back
(FR-C11) — the encrypted keystore lands with platform services in M6.
"""

from __future__ import annotations

from app.base import Connection, ConnectionHealth


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, Connection] = {}

    def register(self, conn_id: str, connection: Connection) -> None:
        self._connections[conn_id] = connection

    def health(self) -> dict[str, ConnectionHealth]:
        """Health snapshot for every connection (drives FR-C11 dashboard and MCP tool)."""
        return {cid: c.health for cid, c in self._connections.items()}
