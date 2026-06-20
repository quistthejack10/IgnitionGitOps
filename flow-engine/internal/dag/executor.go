package dag

import (
	"context"
	"log"
)

// Executor runs flows against incoming events.
//
// Design contract (PRD §8, FR-F5, FR-F7):
//   - at-least-once event processing; MES action nodes are made idempotent via their
//     IdempotencyKey so re-delivery is safe.
//   - per-node metrics (executions/sec, error rate, p95 latency) and structured execution logs.
//   - failed events go to a dead-letter queue with replay.
//
// M0 is a skeleton: Run is a no-op loop until canceled. M1 wires NATS subscribe + one event
// round-trip; M4 implements the node dispatch, wire-tap test mode, and dead-letter/replay.
type Executor struct {
	natsURL string
	flows   map[string]*Flow
}

func NewExecutor(natsURL string) *Executor {
	return &Executor{natsURL: natsURL, flows: make(map[string]*Flow)}
}

// Load registers a published flow for execution.
func (e *Executor) Load(f *Flow) {
	e.flows[f.ID] = f
}

// Run blocks until the context is canceled.
func (e *Executor) Run(ctx context.Context) error {
	log.Printf("executor ready (flows loaded=%d); NATS wiring lands in M1", len(e.flows))
	<-ctx.Done()
	return ctx.Err()
}

// dispatch walks a flow's nodes in topological order for a single event.
//
// Placeholder for M4: looks up each node's handler in the node registry and pipes the payload
// along the edges, recording per-node timing and routing failures to the dead-letter queue.
func (e *Executor) dispatch(f *Flow) {
	for _, id := range f.TopoOrder() {
		_ = id // node handler invocation implemented in M4
	}
}
