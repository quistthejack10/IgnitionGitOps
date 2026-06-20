# ADR-0001: Graph engine — Postgres + Apache AGE

- **Status:** Proposed (gated by M1 benchmark)
- **Date:** 2026-06-20

## Context

Forge's data model is user-defined and graph-shaped: genealogy, equipment hierarchies, and
routing are graph problems (PRD §2.1, §7.3). We need entity + relationship storage that can
serve multi-hop traversals at scale (NFR: GraphQL 3-hop over 1M entities < 500 ms p95;
scale target 10M entities) while staying **operable on a single on-prem gateway**.

## Decision

Use **Postgres + Apache AGE** (openCypher on Postgres) behind a `PropertyGraphStore`
abstraction layer in `services/graph-core`. Co-locate **TimescaleDB** in the same Postgres
estate for time-series. One engine to operate, back up, and restore.

## Rationale

- Single database engine for relational + graph + time-series — minimal ops burden on a
  gateway with no dedicated DBA (persona: Marcus).
- AGE speaks openCypher, matching the graph traversal model.
- The `PropertyGraphStore` interface isolates AGE specifics so we can swap engines.

## Consequences

- **Risk:** AGE multi-hop performance at 10M entities is unproven for our access patterns.
- **Mitigation / gate:** M1 spike loads 10M synthetic entities and benchmarks a 5-hop trace.
  If AGE misses the p95 target, fall back to **embedded Neo4j Community** or **Dgraph** —
  the abstraction layer keeps the blast radius to graph-core.
- This ADR is **not final** until the M1 benchmark resolves it.
