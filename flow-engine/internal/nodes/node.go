// Package nodes defines the node-category interfaces for the flow engine, matching the launch
// node catalog (PRD FR-F2). Concrete node implementations land in M4.
package nodes

import (
	"context"
	"encoding/json"
)

// Payload is the data flowing along flow edges. It carries the bus event plus per-node context
// accumulated during execution.
type Payload struct {
	Event   json.RawMessage `json:"event"`   // the originating event.schema.json envelope
	Context map[string]any  `json:"context"` // values added by upstream nodes
}

// Handler is implemented by every concrete node type.
type Handler interface {
	// Execute processes the payload and returns zero or more outputs to fan out to edges.
	Execute(ctx context.Context, in Payload) ([]Payload, error)
}

// The launch catalog (FR-F2) groups nodes into these categories. Concrete types in M4:
//
//	Trigger:   connection source, schedule (cron), platform event, manual
//	Transform: mapping, expression, script (sandboxed), filter, deadband, debounce,
//	           aggregate/window, join/merge, split, lookup
//	Logic:     switch/route, condition, loop-over-list, delay, retry/error policy
//	MES:       create/update entity, create relationship, record telemetry, transition
//	           work-order state, raise notification
//	Sink:      connection sink, UNS publish, REST call, email/webhook notification
//
// Registry maps a node "type" string from flow.schema.json to its Handler constructor.
type Registry map[string]func(config map[string]any) Handler
