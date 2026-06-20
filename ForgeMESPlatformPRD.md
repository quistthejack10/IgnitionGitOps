# Product Requirements Document

## Forge MES Platform (working name)

**A fully customizable, graph-native MES platform that runs on an on-prem gateway**

| | |
|---|---|
| Version | 0.1 (Draft) |
| Author | Jackson |
| Date | June 11, 2026 |
| Status | Draft for review |

---

## 1. Executive Summary

Forge is an on-premises Manufacturing Execution System platform, not a fixed-function MES application. It ships as a containerized gateway that deploys on plant-floor hardware (industrial PC, VM, or k3s cluster) and gives manufacturers three core capabilities that today require stitching together three different product categories:

1. **Universal connectivity** to industrial and IT data sources: OPC-UA, MQTT (including Sparkplug B), raw TCP/UDP sockets, Modbus TCP, any SQL database (Postgres, SQL Server, MySQL, Oracle), Kafka, REST APIs, and flat files.
2. **A visual flow builder** for ingesting, transforming, contextualizing, and routing data between any source and any destination, in the spirit of Node-RED / HighByte Pipelines / Crosser, but deeply integrated with the MES data model.
3. **A user-defined graph data model** where end users design their own entity types and relationships (equipment, materials, work orders, lots, operators, defects, anything) on a visual canvas, with an ISA-95-aligned starter ontology, and query it through a generated GraphQL API.

The positioning insight: Fuuz proved the market wants a customizable MES platform rather than rigid modules, but it is cloud-native. Rhize proved a graph database with ISA-95 as the schema is the right backbone for manufacturing data, but it is headless and engineer-oriented. HighByte/Crosser proved OT teams will adopt no-code flow tooling at the edge, but they stop at data movement and don't execute manufacturing logic. Forge combines all three patterns in a single on-prem deployable: **the customizability of Fuuz, the graph backbone of Rhize, and the flow-builder UX of HighByte — running entirely inside the plant network.**

A deliberate differentiator from all three: Forge is **agent-ready by design**. Every platform capability (graph queries, flow deployment, work order actions) is exposed through an MCP server so AI agents can operate the system with the same governed permissions as human users.

---

## 2. Problem Statement

### 2.1 The problems

**Traditional MES is rigid and expensive to change.** Conventional MES products (legacy on-prem suites and most modern SaaS) impose a fixed data model and fixed screens. Every deviation from the vendor's assumed process — a foundry that thinks in heats and ladles instead of batches and lots — becomes a paid customization project or an ugly workaround. Manufacturers end up with shadow spreadsheets and Access databases living next to the MES.

**Connectivity is always a separate purchase.** Plants buy an MES, then discover they also need a protocol gateway, an integration platform, a historian connector, and custom middleware to actually get data into it. Each integration is a brittle point-to-point project.

**Cloud-native platforms exclude a large segment.** Fuuz and similar platforms solve customizability but require cloud connectivity. Many plants — defense suppliers, regulated industries, facilities with unreliable WAN links, or simply IT organizations with data-sovereignty policies — cannot or will not send production data to someone else's cloud. The plant floor also can't stop when the internet does.

**Relational schemas can't keep up with manufacturing reality.** Genealogy ("which heats fed which castings shipped to which customer?"), equipment hierarchies, and routing relationships are graph problems. Modeling them in fixed relational tables means either an explosion of join tables or denormalized reporting hacks. Rhize demonstrated that ISA-95's object model has an inherent graph structure and that a graph database represents it exactly — every job response connects to its operations requests, personnel, equipment, and materials consumed and produced.

### 2.2 Who feels it

Mid-market discrete and process manufacturers (50–2,000 employees per site) with: a controls/SCADA team but no software team, heterogeneous brownfield equipment, ERP at level 4 (often SAP or a tier-2), and either no MES or a legacy one they're afraid to touch.

---

## 3. Market & Competitive Context

| Product | What they got right | Gap Forge exploits |
|---|---|---|
| **Fuuz (MFGx)** | Fully customizable schema, screens, dashboards, integrations, and process flows; event-driven architecture; UNS in a single platform; no-code through pro-code spectrum; device gateway for plant connectivity | Cloud-native multi-tenant SaaS; the gateway is a data collector, not the platform itself; pricing/positioning aimed at consolidating ERP-adjacent systems |
| **Rhize** | Graph DB with ISA-95 standard as the schema; headless GraphQL API; event-driven; manufacturing knowledge graph and genealogy as first-class use cases; runs on customer's own Kubernetes infrastructure | Headless — no operator screens, no visual modeling UX; demands deep ISA-95 literacy; targets sophisticated engineering teams, not plant OT staff |
| **HighByte Intelligence Hub** | Edge-deployed industrial DataOps; code-free modeling, transformation, and pipelines; built for OT teams; distributed hub management | Data movement and contextualization only — no persistence layer for MES records, no execution logic, no operator UI |
| **Crosser / Node-RED** | Visual flow paradigm proven with non-programmers; huge module ecosystems (Node-RED); autonomous edge execution after deployment (Crosser) | General-purpose; no manufacturing data model; Node-RED specifically lacks enterprise RBAC, observability, and flow governance |
| **Tulip** | No-code app builder operators love; edge connectivity kits | App-centric, not data-model-centric; cloud-first; weak deep genealogy |
| **Ignition (Inductive Automation)** | On-prem, unlimited licensing, strong OT adoption, scripting extensibility | SCADA-first; MES requires Sepasoft modules with their own fixed models; no native graph; "customization" means writing Python |

**Forge's wedge:** the only platform where an OT engineer can, in one product and one afternoon on-prem, (a) connect a PLC via OPC-UA, (b) drag a flow that maps tag changes into (c) a graph entity they designed themselves, and (d) put a screen in front of an operator — with no cloud dependency and no per-tag licensing.

---

## 4. Goals & Non-Goals

### 4.1 Goals

1. Deploy to first value (one machine connected, one flow running, one entity populated, one dashboard live) in **under one day** with no vendor professional services.
2. 100% on-prem operation: zero hard cloud dependencies, fully functional with no internet access, including licensing.
3. Every MES capability built **on** the platform primitives (graph model + flows + screens) rather than beside them — proving the platform is sufficient by dogfooding.
4. All functionality reachable through API (REST + GraphQL) and MCP, so the UI is a client, not a gatekeeper.

### 4.2 Non-Goals (v1)

- Not a SCADA/HMI replacement: no real-time control, no PLC writes for machine control loops, no alarm management at SCADA fidelity. (Flows may write setpoints/recipe parameters with explicit governance, but Forge does not replace Ignition/FactoryTalk.)
- Not an ERP: no financials, no purchasing, no payroll. ERP is an integration target.
- Not a historian replacement at extreme scale: the embedded time-series store targets the typical plant (≤ ~100K tags, 1-second-class resolution), not 1M-tag enterprise historians.
- No multi-tenant SaaS offering in v1. Single-org, possibly multi-site.
- No advanced production scheduling/APS engine in v1.

---

## 5. Personas

**Priya — Controls/SCADA Engineer (primary builder).** Owns PLCs, OPC servers, Ignition. Comfortable with tags, SQL, and a bit of Python. She configures connections, builds flows, and extends the data model. Forge must feel like a natural extension of her toolbox, not enterprise software thrown over the wall.

**Marcus — Plant IT Administrator.** Owns the VM cluster, AD/LDAP, backups, and the firewall. He needs Forge to install cleanly into his environment, authenticate against his identity provider, log to his SIEM, and never demand an inbound internet connection.

**Dana — Production Supervisor (primary consumer).** Lives in dashboards and work order screens. Needs to dispatch work, see downtime and OEE, and trace a quality escape backward through genealogy. Will never open the flow builder; the screens built for her must be fast and tablet-friendly.

**Leo — Operator.** Scans a badge, sees his queued job, records production counts and scrap, logs a downtime reason in three taps. Gloved hands, shop-floor terminal.

**Avery — Continuous Improvement / Quality Engineer (power consumer).** Writes graph queries and builds analysis dashboards; defines new entity types (e.g., "Defect Mode", "Containment Action") without waiting on anyone.

**Agent — AI assistant.** A Claude-class agent connected via MCP, asking "which work orders are blocked on material?" or executing "create a downtime event on Press 3" under a scoped service identity.

---

## 6. System Architecture Overview

### 6.1 Deployment shape

Forge ships as an OCI container bundle deployable three ways:

1. **Single-node gateway** (Docker Compose): industrial PC or VM, 8 cores / 32 GB RAM / 500 GB SSD recommended baseline. The standard entry point.
2. **HA cluster** (k3s/Kubernetes + Helm chart): 3+ nodes for plants where MES downtime stops shipping. Per-plant `values-<plant>.yaml` overrides for multi-site rollouts.
3. **Hub-and-spoke** (Phase 3): lightweight collector gateways at remote lines/buildings, store-and-forward to a central plant instance.

### 6.2 Core services

```
┌─────────────────────────────────────────────────────────────┐
│                     Forge Gateway (on-prem)                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Connectivity │  │ Flow Engine  │  │  Graph Core       │  │
│  │ Service      │─▶│ (DAG runtime)│─▶│  (entity/relation │  │
│  │ OPC-UA, MQTT │  │              │  │   store + GraphQL)│  │
│  │ TCP, Modbus, │  └──────┬───────┘  └─────────┬─────────┘  │
│  │ SQL, Kafka,  │         │                    │            │
│  │ REST, Files  │         ▼                    ▼            │
│  └──────────────┘  ┌──────────────┐  ┌───────────────────┐  │
│         │          │ Event Bus    │  │ Time-Series Store │  │
│         │          │ (internal    │  │ (telemetry,       │  │
│         └─────────▶│  pub/sub +   │  │  hypertables)     │  │
│                    │  UNS broker) │  └───────────────────┘  │
│                    └──────┬───────┘                          │
│                           ▼                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ Screen/App   │  │ API Gateway  │  │ Platform Services │  │
│  │ Builder +    │  │ REST,GraphQL,│  │ AuthN/Z (OIDC),   │  │
│  │ Runtime      │  │ Webhooks,MCP │  │ Audit, Backup,    │  │
│  └──────────────┘  └──────────────┘  │ Licensing, Logs   │  │
│                                      └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Event-driven backbone.** Every state change in the platform (tag change passed through a flow, entity created, work order state transition) is an event on the internal bus. Flows subscribe to events; events trigger flows. The bus doubles as an embedded MQTT broker so the platform natively presents a Unified Namespace to the rest of the plant.

### 6.3 Recommended reference stack

| Layer | Recommendation | Rationale |
|---|---|---|
| Graph core | Postgres + Apache AGE (openCypher on Postgres), with a property-graph abstraction layer | One database engine to operate/back up; relational + graph + (with Timescale) time-series in a single Postgres estate; avoids operating Dgraph/Neo4j separately. Fallback option: embedded Neo4j Community or Dgraph if AGE performance limits emerge |
| Time-series | TimescaleDB (same Postgres instance or dedicated) | Proven hypertable compression and continuous aggregates; team familiarity |
| Event bus | NATS JetStream (embedded) + embedded MQTT broker (e.g., EMQX/Mosquitto) bridged | NATS is light enough for a gateway; JetStream gives persistence/replay; MQTT side exposes the UNS |
| Flow engine | Custom DAG runtime (Python workers or Go) executing versioned flow definitions stored as JSON | Owning the runtime enables MES-aware nodes, per-node metrics, and store-and-forward semantics third-party engines don't give |
| Connectivity | Drivers: open62541/python-opcua (OPC-UA), paho + Sparkplug B codec (MQTT), pycomm3 (EtherNet/IP, Phase 2), pymodbus, asyncio sockets (TCP/UDP), SQLAlchemy/ODBC (databases), aiokafka | Mature OSS, team experience |
| API layer | FastAPI (REST + generated GraphQL), strawberry-graphql; MCP server (Anthropic SDK) | GraphQL is generated from the user's model, Rhize-style |
| Frontend | React + reactflow (flow & model canvases) + a grid/widget dashboard runtime | reactflow is the de facto standard for node editors |
| Identity | Keycloak (bundled) federating to AD/LDAP/OIDC | On-prem identity without reinventing auth |
| Packaging | Docker Compose + Helm chart; air-gapped offline bundle (images + license file) | Matches deployment goals |

---

## 7. Functional Requirements

Requirements are tagged **[P0]** (MVP), **[P1]** (fast follow), **[P2]** (later phase).

### 7.1 Connectivity Layer

The connectivity service manages **Connections** (a configured endpoint) and exposes their data as **Sources** (subscriptions/polls) and **Sinks** (writes) usable in flows.

- **FR-C1 [P0] OPC-UA client.** Browse server address space in-UI, subscribe to nodes (monitored items with configurable sampling/queue), read/write nodes, support Basic256Sha256 security policies, username and certificate auth, and auto-reconnect with subscription transfer.
- **FR-C2 [P0] MQTT client.** Connect to external brokers (TLS, client certs), subscribe/publish arbitrary topics, JSON payload parsing. **Sparkplug B** support: decode NBIRTH/DBIRTH/NDATA/DDATA, maintain metric state, honor bdSeq/rebirth semantics.
- **FR-C3 [P0] Embedded MQTT broker (UNS).** The gateway itself runs a broker; any platform event or flow output can be published to a structured namespace (e.g., `site/area/line/cell/...`). External clients (Ignition, analytics) can subscribe.
- **FR-C4 [P0] Generic TCP/UDP.** Raw socket client and listener with configurable framing (delimiter, fixed-length, length-prefixed), encoding (ASCII, hex, binary struct unpack), and a test console. This covers barcode scanners, scales, printers, and legacy serial-over-IP devices.
- **FR-C5 [P0] SQL databases.** Connection support for PostgreSQL, SQL Server, MySQL/MariaDB at launch; Oracle [P1]; ODBC generic [P1]. Capabilities: polled query source (with watermark/change-tracking column), one-shot query node in flows, insert/update/upsert sink, stored procedure call. Connection pooling, read-only enforcement option per connection.
- **FR-C6 [P0] REST/HTTP.** Outbound request node (auth: basic, bearer, API key, OAuth2 client credentials); inbound webhook endpoints that trigger flows.
- **FR-C7 [P1] Kafka.** Consumer source (consumer-group managed) and producer sink; Avro/JSON schema support.
- **FR-C8 [P1] Modbus TCP.** Polled register reads, coil/register writes, configurable word/byte order.
- **FR-C9 [P1] File/Directory watcher.** CSV/XML/JSON pickup from network shares with archival/error folders — still how a shocking amount of plant data moves.
- **FR-C10 [P2] EtherNet/IP (CIP) direct driver** for Allen-Bradley tag reads without an OPC server, and **SAP connector** (RFC/IDoc or OData).
- **FR-C11 [P0] Connection management UX.** Health dashboard for all connections (state, latency, throughput, last error), test-before-save, secrets stored encrypted (never echoed back), import/export of connection configs (secrets excluded).
- **FR-C12 [P0] Store-and-forward.** Every sink supports buffered delivery: if a destination is down, payloads queue to disk (configurable cap and overflow policy) and drain in order on recovery.

### 7.2 Flow Builder

A **Flow** is a versioned, directed acyclic graph of nodes executed by the flow engine. Flows are the only mechanism for data movement and automation logic — one mental model everywhere.

- **FR-F1 [P0] Visual canvas.** Drag-drop nodes, typed ports (events, records, scalars), connection validation, pan/zoom, sub-flow grouping, copy/paste, undo/redo.
- **FR-F2 [P0] Node catalog (launch set).**
  - *Triggers:* connection source (tag change, MQTT message, query result, webhook, TCP frame), schedule (cron), platform event (entity created/updated, work order state change), manual.
  - *Transforms:* mapping (visual field mapper), expression (sandboxed expression language), script (sandboxed Python) for the pro-code escape hatch, filter, deadband, debounce, aggregate/window (time and count), join/merge, split, lookup (graph query or SQL).
  - *Logic:* switch/route, condition, loop-over-list, delay, retry/error policy.
  - *MES actions:* create/update graph entity, create relationship, record telemetry point, transition work order state, raise notification.
  - *Sinks:* any connection sink, UNS publish, REST call, email/webhook notification.
- **FR-F3 [P0] Test & debug mode.** Run a flow against a captured or hand-crafted payload without side effects (sinks mocked); inspect the payload at every node ("wire-tap" view); per-node execution time.
- **FR-F4 [P0] Versioning & deployment.** Flows have draft/published states and full version history with diff and one-click rollback. Published flows export/import as JSON for Git-based promotion between environments (dev → test → prod), aligning with prompts-as-code style discipline.
- **FR-F5 [P0] Observability.** Per-flow and per-node metrics (executions/sec, error rate, p95 latency), structured execution logs, dead-letter queue for failed events with replay, alerting thresholds.
- **FR-F6 [P1] Flow templates & marketplace format.** Parameterized templates ("OPC tag → downtime event," "Sparkplug device → equipment telemetry") instantiable per machine; a packaging format so the community/integrators can share flows.
- **FR-F7 [P1] Horizontal scaling.** Flow partitions distributable across worker replicas in the k3s deployment; at-least-once execution semantics with idempotency keys on MES action nodes.

### 7.3 Graph Data Modeling ("Model Studio")

This is the heart of the product. Users define their own ontology; the platform generates storage, APIs, and UI bindings from it.

- **FR-M1 [P0] Entity type designer.** Visual canvas to create entity types with typed properties (string, number, boolean, datetime, enum, JSON, file ref), validation rules, computed properties [P1], and display settings (label template, icon, color).
- **FR-M2 [P0] Relationship designer.** Define named, directed relationship types between entity types (e.g., `Lot —CONSUMED_BY→ WorkOrder`, `Equipment —PART_OF→ Line`) with cardinality constraints and properties on edges (quantity, timestamp). Rendered as an editable graph diagram — this canvas *is* the user's data architecture document.
- **FR-M3 [P0] ISA-95 starter ontology.** An optional, importable model pack: Equipment (with hierarchy levels Site/Area/Line/Cell/Unit), Material Definition/Lot/Sublot, Personnel, Work Order/Job Order/Job Response, Operations Definition/Segment. Users can adopt it wholesale, extend it, rename it to their dialect ("Heat" instead of "Batch"), or ignore it. The pack encodes ISA-95's object relationships so genealogy and scheduling semantics work out of the box, following Rhize's insight that ISA-95's object model maps naturally onto a graph.
- **FR-M4 [P0] Schema evolution.** Add properties and types live; renames preserve data; deletes require explicit migration confirmation with impact analysis (which flows/screens/queries reference the deleted member). Full model version history.
- **FR-M5 [P0] Generated GraphQL API.** Every entity and relationship type is immediately queryable and mutable via generated GraphQL (filtering, pagination, nested traversal: "work orders → consumed lots → source heats → furnace → maintenance events"). REST CRUD endpoints generated in parallel for simple integrations.
- **FR-M6 [P0] Graph explorer.** Interactive visual query tool: start from any entity instance, expand relationships, filter, save explorations as shareable views. This is the genealogy/traceability UX for Avery and Dana.
- **FR-M7 [P0] Time-series binding.** Any entity can declare telemetry channels (e.g., Equipment.temperature). Flows write points to the time-series store keyed to the entity; queries can join graph context with telemetry ranges ("temperature curve of the furnace during Heat 4512").
- **FR-M8 [P1] Row/instance-level security.** Permission rules scoped by entity type and by relationship (e.g., supervisors see only their area's entities via the equipment hierarchy).
- **FR-M9 [P2] Ontology import/export** as JSON-LD/RDF-adjacent format for interchange and AI-agent consumption.

### 7.4 MES Application Layer

Shipped as **model packs + flow templates + screen templates** built entirely on the primitives above — installable, inspectable, and editable by the customer.

- **FR-A1 [P0] Work order execution.** Import or create work orders (typically from ERP via flow), state machine (Created → Released → Running → Held → Complete → Closed) with configurable states/transitions, operation steps, dispatch list screen, operator start/stop/count/scrap recording.
- **FR-A2 [P0] Downtime & OEE.** Downtime events auto-created from equipment state flows, reason-code tree (user-defined), operator reason assignment screen, OEE calculation (availability × performance × quality) as continuous aggregates, Pareto and trend dashboards.
- **FR-A3 [P0] Traceability/genealogy.** Material consumption/production recording in work order flows produces the lot graph automatically; forward and backward trace queries and visual trace explorer.
- **FR-A4 [P1] Quality.** Inspection plans bound to operations, data collection screens (variable & attribute), out-of-spec event triggers, hold/disposition workflow.
- **FR-A5 [P2] Maintenance-lite.** Meter/usage-based maintenance triggers from telemetry, work request entities. (Integrate to CMMS rather than replace it.)

### 7.5 Screens & Dashboards

- **FR-S1 [P0] Dashboard builder.** Grid-based canvas with widgets (time-series chart, stat card, table, Pareto, gauge, entity list, graph view) bound to GraphQL/time-series queries; auto-refresh; kiosk mode for andon displays.
- **FR-S2 [P0] Form/app screens.** Form builder bound to entity types (create/edit instances), barcode/badge scan input support, large-touch-target operator mode.
- **FR-S3 [P1] Screen templates** shipped with each MES app pack; theming (the dark graphite/HPHMI aesthetic ships as the default theme).
- **FR-S4 [P2] Embeddable widgets** (iframe/web-component) so screens can live inside Ignition Perspective or SharePoint.

### 7.6 Platform Services

- **FR-P1 [P0] AuthN/AuthZ.** OIDC (bundled Keycloak) with AD/LDAP federation; RBAC roles (Admin, Builder, Supervisor, Operator, Viewer, Service); per-resource permissions (connections, flows, model, screens); API keys and service accounts with scoped tokens.
- **FR-P2 [P0] Audit trail.** Immutable log of every configuration change (who/what/when/before/after) and every MES transaction; exportable; this is the foundation for regulated-industry stories (21 CFR Part 11 alignment [P2]).
- **FR-P3 [P0] Backup & restore.** One-command full backup (config + graph + time-series) to local path or S3-compatible target; scheduled; tested restore procedure documented.
- **FR-P4 [P0] Offline licensing.** License file based; no phone-home requirement; grace behavior on expiry (read-only, never data loss).
- **FR-P5 [P0] Observability of the platform itself.** Prometheus metrics endpoint, structured JSON logs, health/readiness endpoints, optional bundled Grafana.
- **FR-P6 [P1] Multi-site administration.** Central console managing config promotion to multiple gateways; site-scoped namespaces.
- **FR-P7 [P0] MCP server.** Platform tools exposed via MCP: query the graph, read connection health, search/inspect flows, execute permitted MES actions. Every MCP action runs under a service identity through the same RBAC and audit pipeline as human users. [P1]: agent-authored flow drafts (agent proposes, human publishes).

---

## 8. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | Sustain 10,000 tag changes/sec ingest through flows on reference hardware (8c/32GB); flow node p95 latency < 50 ms; GraphQL 3-hop traversal over 1M entities < 500 ms p95; operator screen interactions < 200 ms |
| Scale targets (v1) | 100K configured tags/metrics, 500 concurrent flows, 10M graph entities, 200 concurrent UI users per gateway |
| Availability | Single node: restart-to-ready < 2 min, no data loss of acknowledged events (WAL + store-and-forward). HA cluster: no single point of failure, rolling upgrades |
| Reliability | At-least-once flow event processing with idempotent MES actions; store-and-forward on every external sink |
| Security | TLS everywhere (internal + external), encrypted secrets at rest (KMS-style local keystore), no default credentials, signed container images, SBOM published, deployable in fully air-gapped networks, outbound-only if any WAN is used |
| Compatibility | x86-64 Linux primary; ARM64 [P2]; browsers: current Chrome/Edge (shop floor terminals on Chromium-based kiosks) |
| Data retention | Configurable per telemetry channel (raw + downsampled tiers via continuous aggregates); graph data retained indefinitely by default |
| Upgrades | In-place upgrade with automatic schema migration and pre-upgrade backup; rollback path documented |

---

## 9. MVP Definition & Phasing

### Phase 1 — MVP (target: 6–9 months)

Connectivity: OPC-UA, MQTT + Sparkplug B, embedded broker/UNS, TCP/UDP, Postgres/SQL Server/MySQL, REST, store-and-forward. Flow builder: canvas, launch node set, test mode, versioning, per-node observability. Model Studio: entity/relationship designer, ISA-95 starter pack, generated GraphQL + REST, graph explorer, time-series binding. Apps: work order execution + downtime/OEE packs. Screens: dashboard + form builders. Platform: OIDC/RBAC, audit, backup, offline licensing, MCP server (read + core actions). Deployment: Docker Compose single node.

**MVP acceptance scenario (the demo that must work):** On a fresh industrial PC, in one working day, a controls engineer installs Forge, connects to an OPC-UA server and a Sparkplug B broker, imports the ISA-95 pack, models a two-line plant, deploys flow templates that turn machine states into downtime events and counts into work order progress, and puts a live OEE dashboard and an operator dispatch screen in front of a supervisor — without writing code and without internet access.

### Phase 2 (months 9–15)

Kafka, Modbus, Oracle/ODBC, file watcher; quality app pack; flow templates/marketplace format; instance-level security; HA Helm deployment; multi-site console; screen templates/theming; agent-drafted flows via MCP.

### Phase 3 (months 15–24)

Hub-and-spoke collectors; EtherNet/IP direct + SAP connectors; maintenance-lite; embeddable widgets; 21 CFR Part 11 package; ARM64; ontology interchange format.

---

## 10. Success Metrics

| Metric | Target |
|---|---|
| Time-to-first-value (install → first live dashboard) | < 1 day, measured in onboarding telemetry (opt-in, local report) |
| % of pilot customers extending the data model themselves (no vendor PS) | > 70% within 60 days |
| Flow reliability | > 99.9% of triggered events processed without manual intervention |
| MVP design-partner conversions | ≥ 3 paying design partners by GA |
| Support load | < 2 support tickets per site per month after month 2 |
| Dogfood proof | 100% of shipped MES app functionality built on public platform primitives |

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| **Scope: building three products at once** (DataOps + graph platform + MES apps) | Fatal if unmanaged | Ruthless P0 discipline; MES apps are thin packs on primitives, not separate codebases; MVP demo scenario is the scope contract |
| Graph performance on Postgres/AGE at scale | Slow genealogy queries undermine the core pitch | Benchmark at 10M entities early (month 2 spike); abstraction layer keeps Neo4j/Dgraph swap possible |
| "Customizable" becomes "blank page paralysis" for mid-market buyers | Stalled deployments | ISA-95 pack + app packs + flow templates as the default path; customization is the escape hatch, not the requirement |
| Flow engine correctness (ordering, exactly-once expectations) | Data integrity incidents destroy trust | At-least-once + idempotency keys as an explicit, documented contract; dead-letter + replay tooling from day one |
| Channel/credibility: nobody buys MES from a new vendor | No pipeline | Design-partner-led development (foundry vertical first, where the founder's domain depth is provable); SI partner program in Phase 2 |
| Ignition/Sepasoft and Tulip move down/over into this space | Squeezed positioning | The graph model + agent-ready MCP surface are structural differentiators neither can bolt on quickly |
| Security posture of a gateway touching PLC networks | One CVE headline kills OT trust | Threat model before GA, third-party pentest, signed images, SBOM, no inbound internet, documented Purdue-model placement (DMZ-friendly) |

---

## 12. Open Questions

1. **Graph engine final call:** Postgres+AGE vs. embedded Neo4j vs. Dgraph — decide via the month-2 genealogy benchmark spike (10M entities, 5-hop traces).
2. **Expression/scripting sandbox:** embedded Python (restricted) vs. a purpose-built expression language vs. JS (QuickJS)? Tension between Priya's Python comfort and sandboxing safety.
3. **Licensing model:** per-gateway flat (Ignition-style, strong differentiator) vs. tiered by tag/entity counts? Per-gateway unlimited is the recommended default pending pricing research.
4. **Write-to-PLC governance:** what approval/interlock UX makes OT teams comfortable enabling setpoint writes from flows?
5. **UNS namespace standard:** enforce ISA-95 topic structure on the embedded broker or leave fully free-form with a recommended template?
6. **Edition strategy:** is there a free single-connection community edition to drive bottom-up adoption (the Node-RED playbook)?

---

## Appendix A — Competitive sources

- Fuuz platform architecture (multi-enterprise mesh, UNS data layer, no/low/pro-code, event-driven), fuuz.com
- Rhize Manufacturing Data Hub docs (graph DB with ISA-95 schema, headless GraphQL MES, event handler), docs.rhize.com
- HighByte Intelligence Hub (edge Industrial DataOps, code-free modeling and pipelines, distributed hub management), highbyte.com
- Crosser vs Node-RED analyses (flow paradigm strengths; enterprise gaps in Node-RED: RBAC, observability, governance), crosser.io / iiot-world.com
