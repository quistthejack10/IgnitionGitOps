"""MCP server scaffold (PRD FR-P7).

Forge is "agent-ready by design": every platform capability is exposed via MCP so AI agents
operate under the same RBAC + audit pipeline as humans. This M0 stub declares the intended
tool surface as no-ops; real handlers (and the RBAC/audit wrapper) land in M6.
"""

from __future__ import annotations

# The governed tool surface agents will call. Each maps to an existing platform capability.
MCP_TOOLS: list[dict[str, str]] = [
    {"name": "graph.query", "description": "Run a read-only query over the graph model."},
    {"name": "connection.health", "description": "Read connection state/latency/throughput."},
    {"name": "flow.search", "description": "Search and inspect flow definitions."},
    {"name": "mes.action", "description": "Execute a permitted MES action (e.g. create downtime event)."},
]


def list_tools() -> list[dict[str, str]]:
    """Return the declared MCP tool surface. Wired to the real MCP runtime in M6."""
    return MCP_TOOLS
