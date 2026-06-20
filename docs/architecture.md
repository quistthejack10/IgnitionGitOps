# Forge Architecture

Distilled from PRD §6. This is the map a contributor reads before touching a service.

## Deployment shape

Forge ships as an OCI container bundle. v1 entry point is a **single-node gateway**
(Docker Compose) on an industrial PC or VM (8c / 32GB / 500GB baseline). Phase 2 adds an
**HA k3s/Helm** deployment; Phase 3 adds **hub-and-spoke** collectors.

## Core services & data flow

```
Connectivity ──▶ Flow Engine ──▶ Graph Core ──▶ GraphQL/REST
 (drivers)        (Go DAG)        (Postgres+AGE)
     │               │                │
     └────────▶ Event Bus ◀───────────┘
            (NATS JetStream + MQTT/UNS)
                     │
              Time-Series Store (TimescaleDB)

API Gateway (REST · GraphQL · Webhooks · MCP)  ── fronts everything
Platform Services (OIDC · Audit · Backup · Licensing · Observability)
Web (flow canvas · model studio · dashboards · operator screens)
```

| Service | Responsibility | Lang | PRD |
|---|---|---|---|
| **Connectivity** | Manage Connections; expose Sources (subscribe/poll) and Sinks (write); store-and-forward | Python | §7.1 |
| **Flow Engine** | Execute versioned flow DAGs; at-least-once + idempotency; per-node metrics | Go | §7.2 |
| **Graph Core** | User-defined entity/relationship model; generated GraphQL+REST; graph explorer; time-series binding | Python | §7.3 |
| **Event Bus** | Internal pub/sub (NATS JetStream, persistence/replay) + embedded MQTT broker presenting the UNS | infra | §6.2 |
| **Time-Series** | Telemetry hypertables, continuous aggregates, downsampling tiers | infra (Timescale) | §7.3 |
| **API Gateway** | Single front door: REST, generated GraphQL, inbound webhooks, MCP server | Python | §7.6 |
| **Platform Services** | OIDC/RBAC (Keycloak), immutable audit, backup/restore, offline licensing, platform metrics | Python | §7.6 |
| **Web** | Flow builder + Model Studio canvases (reactflow), dashboard/form builders, operator screens | React/TS | §7.2/7.3/7.5 |

## Event-driven backbone

Every state change (tag change through a flow, entity created, work-order transition) is an
**event on the bus**. Flows subscribe to events and events trigger flows. The bus doubles as
an embedded MQTT broker, natively presenting a **Unified Namespace** (`site/area/line/cell/…`)
to the rest of the plant.

## The polyglot seam: `schemas/`

The Go flow-engine and the Python services **never share types directly**. They agree on
language-agnostic JSON contracts in [`../schemas`](../schemas):

- `event.schema.json` — the envelope for everything published on NATS.
- `flow.schema.json` — a versioned flow definition (the DAG the engine executes).
- `model.schema.json` — entity/relationship type definitions emitted by Model Studio and
  consumed by graph-core to generate storage + GraphQL.

When wiring real behavior, start here: producers and consumers validate against these schemas.

## Dogfooding principle

MES application functionality (work orders, downtime/OEE, traceability) ships as
**packs** — model + flow + screen templates that are *data* on top of the primitives, not
separate codebases. This is enforced as a goal (PRD §4.1.3) and a success metric (§10).
