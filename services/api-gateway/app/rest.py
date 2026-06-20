"""Versioned REST surface.

CRUD endpoints are generated per entity type from the user's data model (FR-M5) in M2.
This M0 stub exposes only a discovery root so the prefix is live and testable.
"""

from __future__ import annotations

from fastapi import APIRouter

api_v1 = APIRouter(tags=["v1"])


@api_v1.get("/")
async def root() -> dict[str, object]:
    return {
        "api": "forge",
        "version": "v1",
        "note": "Entity CRUD routes are generated from the data model (FR-M5, M2).",
        "surfaces": ["/api/v1", "/graphql", "/metrics", "/healthz", "/readyz"],
    }
