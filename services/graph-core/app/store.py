"""Property-graph storage abstraction (PRD §7.3, ADR-0001).

`PropertyGraphStore` is the engine-agnostic interface the rest of Forge depends on. The
`AgeStore` targets Postgres + Apache AGE (openCypher). All AGE specifics are isolated here —
the ADR-0001 swap point if the M1 benchmark fails the 500 ms p95 target.

Key AGE execution pattern:
    Every Cypher query runs through AGE's SQL wrapper:
        SELECT * FROM cypher('forge', $$ <cypher> $$, '<params_json>') AS (<cols> agtype)
    The `agtype` custom Postgres type is registered as text in each connection so asyncpg
    can decode it without the apache-age Python driver.
"""

from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from typing import Any

import asyncpg


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
    async def query(
        self, cypher: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Run an openCypher query; return a list of row dicts."""


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Per-connection AGE setup (asyncpg pool `init` hook)."""
    await conn.execute("LOAD 'age'")
    await conn.execute('SET search_path = ag_catalog, "$user", public')
    # Register agtype as text so asyncpg can decode it without the apache-age driver.
    await conn.set_type_codec(
        "agtype",
        encoder=str,
        decoder=str,
        schema="ag_catalog",
        format="text",
    )


def _parse_agtype(raw: str) -> Any:
    """Parse an agtype text value into a Python object.

    AGE encodes vertex/edge values as JSON-like strings with type suffixes
    (e.g. '{"id": 1}::vertex'). Strip the suffix and parse the JSON body.
    """
    if raw is None:
        return None
    # Strip AGE type suffix (::vertex, ::edge, ::path) if present.
    if "::" in raw:
        raw = raw.rsplit("::", 1)[0]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


class AgeStore(PropertyGraphStore):
    """Postgres + Apache AGE implementation.

    All Cypher is executed via AGE's cypher() SQL function. Parameters are passed as a
    JSON string argument — AGE does not support positional SQL parameters inside Cypher.
    """

    def __init__(self, dsn: str, graph_name: str = "forge") -> None:
        self._dsn = dsn
        self._graph = graph_name
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(self._dsn, init=_init_connection)

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    def _cypher(self, stmt: str, params: dict[str, Any] | None = None) -> str:
        """Wrap a Cypher statement in AGE's cypher() SQL call.

        Returns the raw SQL string. Columns are always aliased as `result agtype`.
        Use _cypher_cols() when multiple column aliases are needed.
        """
        if params:
            params_json = json.dumps(params).replace("'", "''")
            return f"SELECT * FROM cypher('{self._graph}', $$ {stmt} $$, '{params_json}') AS (result agtype)"
        return f"SELECT * FROM cypher('{self._graph}', $$ {stmt} $$) AS (result agtype)"

    def _cypher_cols(self, stmt: str, cols: list[str], params: dict[str, Any] | None = None) -> str:
        col_defs = ", ".join(f"{c} agtype" for c in cols)
        if params:
            params_json = json.dumps(params).replace("'", "''")
            return f"SELECT * FROM cypher('{self._graph}', $$ {stmt} $$, '{params_json}') AS ({col_defs})"
        return f"SELECT * FROM cypher('{self._graph}', $$ {stmt} $$) AS ({col_defs})"

    async def create_entity(self, type_name: str, properties: dict[str, Any]) -> str:
        """Create a vertex of `type_name`; auto-assign `_id` (UUID) if not provided."""
        if "_id" not in properties:
            properties = {"_id": str(uuid.uuid4()), **properties}
        entity_id: str = properties["_id"]

        # Build a Cypher property map literal from the dict.
        props_cypher = _dict_to_cypher_props(properties)
        stmt = f"CREATE (v:{type_name} {props_cypher}) RETURN v"
        sql = self._cypher_cols(stmt, ["v"])

        assert self._pool is not None
        await self._pool.fetchval(sql)
        return entity_id

    async def create_relationship(
        self, rel_type: str, from_id: str, to_id: str, properties: dict[str, Any] | None = None
    ) -> str:
        props = properties or {}
        rel_id = str(uuid.uuid4())
        props_cypher = _dict_to_cypher_props({"_id": rel_id, **props})
        stmt = (
            f"MATCH (a {{_id: '{from_id}'}}), (b {{_id: '{to_id}'}}) "
            f"CREATE (a)-[r:{rel_type} {props_cypher}]->(b) "
            "RETURN r"
        )
        sql = self._cypher_cols(stmt, ["r"])
        assert self._pool is not None
        await self._pool.fetchval(sql)
        return rel_id

    async def get(self, entity_id: str) -> dict[str, Any] | None:
        stmt = f"MATCH (v {{_id: '{entity_id}'}}) RETURN v LIMIT 1"
        sql = self._cypher_cols(stmt, ["v"])
        assert self._pool is not None
        row = await self._pool.fetchrow(sql)
        if row is None:
            return None
        parsed = _parse_agtype(row["v"])
        return parsed.get("properties") if isinstance(parsed, dict) else None

    async def query(
        self, cypher: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Run raw Cypher; return a list of dicts (one per result row, keyed by column name).

        The caller is responsible for the RETURN clause. The SQL wrapper uses a single
        `result agtype` column — for multi-column results use _cypher_cols directly.
        """
        sql = self._cypher(cypher, params)
        assert self._pool is not None
        rows = await self._pool.fetch(sql)
        return [{"result": _parse_agtype(r["result"])} for r in rows]

    async def raw_cypher(
        self, cypher: str, cols: list[str], params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Multi-column Cypher query used by the benchmark and genealogy traversals."""
        sql = self._cypher_cols(cypher, cols, params)
        assert self._pool is not None
        rows = await self._pool.fetch(sql)
        return [{col: _parse_agtype(r[col]) for col in cols} for r in rows]


def _dict_to_cypher_props(d: dict[str, Any]) -> str:
    """Convert a Python dict to a Cypher property map literal: {key: 'val', num: 42}."""
    parts: list[str] = []
    for k, v in d.items():
        if isinstance(v, str):
            escaped = v.replace("'", "\\'")
            parts.append(f"{k}: '{escaped}'")
        elif isinstance(v, bool):
            parts.append(f"{k}: {str(v).lower()}")
        elif v is None:
            parts.append(f"{k}: null")
        else:
            parts.append(f"{k}: {v}")
    return "{" + ", ".join(parts) + "}"
