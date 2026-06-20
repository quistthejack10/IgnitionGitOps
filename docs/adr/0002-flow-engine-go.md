# ADR-0002: Flow DAG runtime in Go

- **Status:** Accepted
- **Date:** 2026-06-20

## Context

The flow engine is the throughput-critical path: NFR targets **10,000 tag changes/sec**
ingest through flows with **per-node p95 < 50 ms** on reference hardware (PRD §8). It must
own its runtime to provide MES-aware nodes, per-node metrics, store-and-forward, and
at-least-once execution with idempotency (PRD §6.3, FR-F7).

## Decision

Implement the flow DAG runtime as a standalone **Go** service (`flow-engine/`). Python is
used for everything else (API, graph-core, connectivity, platform).

## Rationale

- Go's concurrency model and low GC overhead fit a high-fan-in, latency-sensitive event
  processor better than Python's GIL-bound runtime.
- A standalone service scales horizontally (Phase 2: flow partitions across worker replicas).
- Communication with Python services is via the **JSON contracts in `schemas/`** over NATS —
  no shared in-process types, so the language split is clean.

## Consequences

- Two backend toolchains (Python + Go) — CI lints/builds both; contributors need both.
- The pro-code "script node" sandbox (PRD §12 open question) must be callable from Go
  (e.g. embedded interpreter or sidecar) — tracked separately.
- Flow definitions are language-agnostic JSON (`flow.schema.json`), authored in the web UI.
