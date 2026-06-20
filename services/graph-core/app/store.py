"""Property-graph storage abstraction (PRD §7.3, ADR-0001).

`PropertyGraphStore` is the engine-agnostic interface the rest of Forge depends on. The
default `AgeStore` targets Postgres + Apache AGE (openCypher). Keeping all engine specifics
behind this interface is what makes the M1 benchmark a *reversible* decision: if AGE misses
the genealogy p95 target, a Neo4j/Dgraph implementation can be dropped in without touching
callers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PropertyGraphStore(ABC):
    """Create/query entities (vertices) and relationships (edges)."""

    @abstractmethod
    async def create_entity(self, type_name: str, properties: dict[str, Any]) -> str:
        """Create an entity of the given type; return its id."""

    @abstractmethod
    async def create_relationship(
        self, rel_type: str, from_id: str, to_id: str, properties: dict[str, Any] | None = None
    ) -> str:
        """Create a directed relationship between two entities; return its id."""

    @abstractmethod
    async def get(self, entity_id: str) -> dict[str, Any] | None:
        """Fetch a single entity by id."""

    @abstractmethod
    async def query(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Run an openCypher query (used for traversals/genealogy)."""


class AgeStore(PropertyGraphStore):
    """Postgres + Apache AGE implementation (skeleton).

    M2 fills these in by executing AGE's `cypher(...)` SQL function over an asyncpg pool.
    """

    def __init__(self, dsn: str, graph_name: str = "forge") -> None:
        self._dsn = dsn
        self._graph_name = graph_name
        self._pool: Any | None = None  # asyncpg.Pool, created in connect()

    async def connect(self) -> None:
        raise NotImplementedError("AgeStore.connect: create asyncpg pool, LOAD age, set search_path (M2)")

    async def create_entity(self, type_name: str, properties: dict[str, Any]) -> str:
        raise NotImplementedError("AgeStore.create_entity (M2)")

    async def create_relationship(
        self, rel_type: str, from_id: str, to_id: str, properties: dict[str, Any] | None = None
    ) -> str:
        raise NotImplementedError("AgeStore.create_relationship (M2)")

    async def get(self, entity_id: str) -> dict[str, Any] | None:
        raise NotImplementedError("AgeStore.get (M2)")

    async def query(self, cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError("AgeStore.query (M2)")
