# ADR-0003: Event bus — NATS JetStream + embedded MQTT broker

- **Status:** Accepted
- **Date:** 2026-06-20

## Context

Forge is event-driven: every state change is an event, flows subscribe to and emit events
(PRD §6.2). The platform must also **natively present a Unified Namespace (UNS)** over MQTT
so external clients (Ignition, analytics) can subscribe (FR-C3). All of this runs on-prem
with no cloud dependency, and acknowledged events must survive restart (NFR: WAL +
store-and-forward, restart-to-ready < 2 min).

## Decision

Use **NATS JetStream** (embedded) as the internal pub/sub backbone, bridged to an **embedded
MQTT broker** (Mosquitto or EMQX) that exposes the UNS. Internal services publish/subscribe
the `event.schema.json` envelope on NATS subjects; UNS-bound payloads are bridged to MQTT
topics structured as `site/area/line/cell/…`.

## Rationale

- NATS is light enough for a single gateway yet gives JetStream **persistence and replay**
  (needed for dead-letter/replay, FR-F5, and at-least-once semantics).
- Keeping the internal bus (NATS) separate from the external UNS surface (MQTT) lets us
  govern what is exposed to the plant without coupling internal subjects to MQTT topics.

## Consequences

- A bridge component must map selected NATS subjects ↔ MQTT topics (and Sparkplug B where
  applicable). Tracked in connectivity / M3.
- UNS topic-structure enforcement vs. free-form is an open question (PRD §12) — default to a
  recommended ISA-95 template, not hard enforcement.
- Subject/topic naming conventions live alongside `event.schema.json`.
