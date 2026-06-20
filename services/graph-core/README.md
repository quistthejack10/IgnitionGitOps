# graph-core

The heart of Forge (PRD §7.3): the user-defined graph data model. Provides:

- `store.py` — `PropertyGraphStore` interface + `AgeStore` (Postgres+AGE) skeleton. The
  abstraction is the swap point gated by the M1 benchmark (ADR-0001).
- `model.py` — typed mirror of `schemas/model.schema.json`.
- `schema_gen.py` — generates the GraphQL API from a `Model` (FR-M5).

## Status (M0)
Interfaces + a GraphQL SDL sketch generator. AGE query execution, schema evolution, graph
explorer, and time-series binding land in M2 (after the M1 graph-engine benchmark).
