# Forge MES Platform

A fully customizable, **graph-native MES platform** that runs entirely on an on-prem
gateway — combining universal industrial connectivity, a visual flow builder, and a
user-defined graph data model, with every capability exposed via REST, GraphQL, and MCP.

See [`ForgeMESPlatformPRD.md`](./ForgeMESPlatformPRD.md) for the full product spec, and
[`docs/architecture.md`](./docs/architecture.md) for the system design.

> **Status:** M0 scaffold. This repo contains the monorepo structure, shared contracts,
> and runnable stubs for the core services. It is **not yet a bootable platform** — see
> [`docs/roadmap.md`](./docs/roadmap.md) for the plan of attack.

## Repository layout

| Path | What lives here | Language |
|---|---|---|
| `schemas/` | **Shared contracts** (events, flow defs, model defs) — the polyglot seam | JSON Schema |
| `libs/forge-common/` | Shared Python lib: settings, logging, NATS bus, metrics | Python |
| `services/api-gateway/` | REST + GraphQL + Webhooks + MCP server | Python (FastAPI) |
| `services/graph-core/` | Property-graph store over Postgres+AGE; GraphQL generation | Python |
| `services/connectivity/` | OPC-UA / MQTT-Sparkplug / TCP / SQL / REST drivers | Python |
| `services/platform/` | Auth (OIDC), audit, backup, licensing | Python (later) |
| `flow-engine/` | DAG runtime executing versioned flow definitions | Go |
| `web/` | Operator/builder UI: flow + model canvases, dashboards | React + TS |
| `packs/` | MES app packs (model + flow + screen templates as data) | Data |
| `deploy/` | Docker Compose overrides, Helm chart (Phase 2 HA) | YAML |
| `docs/` | Architecture, roadmap, ADRs | Markdown |

## Reference stack (PRD §6.3)

Postgres + Apache AGE (graph) · TimescaleDB (time-series) · NATS JetStream + MQTT broker
(event bus / UNS) · FastAPI + strawberry-graphql + MCP (API) · React + reactflow (web) ·
Keycloak (identity) · Docker Compose / Helm (packaging).

## Quickstart (dev)

```bash
# Bring up infra dependencies (graph DB, event bus, MQTT, identity)
docker compose up -d postgres nats mqtt

# Lint / build each component
make lint        # ruff (python) + go vet + tsc (web)
make build       # go build + web build
```

Per-service setup lives in each component's own `README`. See `make help` for tasks.
