# flow-engine (Go)

The throughput-critical flow DAG runtime (ADR-0002). Executes versioned flow definitions
(`schemas/flow.schema.json`) with at-least-once semantics, idempotent MES actions, per-node
metrics, and dead-letter/replay (PRD §7.2, §8).

- `cmd/flow-engine/` — entrypoint: health server + executor bootstrap.
- `internal/dag/` — `Flow`/`Node`/`Edge` types (mirror of the flow schema) + `Executor`.
- `internal/nodes/` — node-category `Handler` interface + registry (FR-F2 catalog).

## Run (dev)

```bash
go vet ./... && go build ./...
go run ./cmd/flow-engine          # serves /healthz on :8081
```

## Status (M0)
Compiles and serves health. NATS wiring + one event round-trip land in M1; the node catalog,
wire-tap test mode, and dead-letter/replay in M4.
