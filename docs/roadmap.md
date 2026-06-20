# Plan of Attack / Roadmap

Maps PRD §9 phasing to an execution order. Each milestone ends in a demoable slice.
Requirement tags: **[P0]** MVP · **[P1]** fast-follow · **[P2]** later.

## M0 — Scaffold *(current)*
Monorepo, shared contracts (`schemas/`), key service stubs (api-gateway, graph-core,
flow-engine), CI, infra compose, docs + ADRs.

## M1 — De-risk the core *(PRD month-2 spike)*
- Stand up Postgres + Apache AGE; load **10M synthetic entities**; benchmark a **5-hop
  genealogy trace** against the **<500 ms p95** target.
- **Gate ADR-0001** (keep AGE vs. swap Neo4j/Dgraph) *before* building on it.
- Prove the polyglot seam: `forge-common` ↔ NATS ↔ Go flow-engine round-trip of one event.

## M2 — Graph Core + generated API (FR-M1–M7) [P0]
Entity/relationship designer backend, schema evolution with impact analysis, generated
GraphQL + REST CRUD, graph explorer queries, time-series binding. Ship `packs/isa95-starter`.
*Unblocks everything else.*

## M3 — Connectivity P0 (FR-C1–C6, C11, C12)
OPC-UA, MQTT + Sparkplug B, embedded broker/UNS, TCP/UDP, SQL (PG/MSSQL/MySQL), REST;
connection health UX; store-and-forward on every sink. Drivers emit events to the bus.

## M4 — Flow engine + builder P0 (FR-F1–F5)
Go executor with the launch node catalog (triggers · transforms · logic · MES-actions ·
sinks), test/debug mode with wire-tap, draft/published versioning + JSON export, per-node
observability + dead-letter/replay. reactflow canvas in `web`.

## M5 — Screens (FR-S1, S2) + MES app packs (FR-A1, A2, A3)
Dashboard + form builders; work-order execution, downtime/OEE, traceability packs — all
built on primitives.

## M6 — Platform services (FR-P1–P5, P7)
Keycloak OIDC/RBAC, immutable audit trail, backup & restore, offline licensing, platform
observability, MCP server (read + core actions).

## M7 — MVP demo gate
The PRD §9 acceptance scenario end-to-end on a single Docker Compose node, **no code, no
internet**: connect OPC-UA + Sparkplug → import ISA-95 pack → model two lines → deploy flow
templates (machine state→downtime, counts→work-order progress) → live OEE dashboard +
operator dispatch screen.

## Phase 2 (months 9–15)
Kafka, Modbus, Oracle/ODBC, file watcher; quality pack; flow templates/marketplace;
instance-level security; HA Helm; multi-site console; screen templates/theming; agent-drafted
flows via MCP.

## Phase 3 (months 15–24)
Hub-and-spoke collectors; EtherNet/IP + SAP connectors; maintenance-lite; embeddable widgets;
21 CFR Part 11 package; ARM64; ontology interchange format.

## Carried risks (PRD §11)
- **Scope (3 products at once)** → ruthless P0; MES apps stay thin packs; M7 demo is the scope contract.
- **AGE performance** → M1 benchmark gates the architecture; abstraction layer keeps the swap open.
- **Flow correctness** → at-least-once + idempotency keys as an explicit contract; dead-letter + replay from M4.

## Open questions tracked as ADRs (PRD §12)
Graph engine final call (M1), scripting sandbox (Python vs. DSL vs. QuickJS), licensing model,
write-to-PLC governance UX, UNS namespace standard, community edition strategy. None block M0.
