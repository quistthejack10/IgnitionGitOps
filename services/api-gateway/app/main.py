"""Forge API gateway — the single front door (PRD §7.6).

Exposes health/readiness/metrics, a versioned REST surface, a GraphQL endpoint (whose schema
is generated from the user's data model in later milestones), and the MCP server. This M0 stub
wires the surfaces together with placeholder behavior so the service boots and is observable.
"""

from __future__ import annotations

from fastapi import FastAPI

from forge_common import Settings, get_logger, metrics_app

from app.graphql import graphql_router
from app.mcp_server import MCP_TOOLS
from app.rest import api_v1

settings = Settings(service_name="api-gateway", port=8000)
log = get_logger(settings.service_name, settings.log_level)

app = FastAPI(title="Forge API Gateway", version="0.0.1")

# Platform observability (FR-P5)
app.mount("/metrics", metrics_app)

# Versioned REST surface (FR-M5 generates REST CRUD in parallel with GraphQL)
app.include_router(api_v1, prefix="/api/v1")

# Generated GraphQL surface (FR-M5)
app.include_router(graphql_router, prefix="/graphql")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Liveness."""
    return {"status": "ok", "service": settings.service_name}


@app.get("/readyz")
async def readyz() -> dict[str, object]:
    """Readiness. M0 stub: always ready. Later checks NATS/Postgres/Keycloak reachability."""
    return {"ready": True, "dependencies": {"nats": "unchecked", "postgres": "unchecked"}}


@app.on_event("startup")
async def _startup() -> None:
    log.info("api_gateway.startup", mcp_tools=[t["name"] for t in MCP_TOOLS])
