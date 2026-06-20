# packs

MES application functionality ships as **packs** — bundles of model definitions
(`model.schema.json`), flow definitions (`flow.schema.json`), and screen definitions — that are
**data on top of the platform primitives**, not separate codebases. This realizes the PRD
dogfooding goal (§4.1.3) and success metric (§10): 100% of shipped MES functionality is built
on public primitives.

Each pack has a `pack.json` manifest listing its contents.

| Pack | PRD | Status |
|---|---|---|
| `isa95-starter/` | FR-M3 | Model pack ready (M0); imported in M2 |
| `work-order/` | FR-A1 | Manifest stub; built in M5 |
| `downtime-oee/` | FR-A2 | Manifest stub; built in M5 |

Phase 2 adds a quality pack (FR-A4) and a parameterized template/marketplace format (FR-F6).
