// Package dag models and executes Forge flow definitions.
//
// The types here mirror schemas/flow.schema.json — the language-agnostic contract authored in
// the web flow builder. The engine never shares types with the Python services directly; it
// agrees on this JSON shape (ADR-0002, ADR-0003).
package dag

// Category is a node-catalog category (PRD FR-F2).
type Category string

const (
	CategoryTrigger   Category = "trigger"
	CategoryTransform Category = "transform"
	CategoryLogic     Category = "logic"
	CategoryMES       Category = "mes"
	CategorySink      Category = "sink"
)

// Status is the flow lifecycle state (FR-F4).
type Status string

const (
	StatusDraft     Status = "draft"
	StatusPublished Status = "published"
)

// Node is one vertex in the flow DAG.
type Node struct {
	ID             string         `json:"id"`
	Type           string         `json:"type"`
	Category       Category       `json:"category"`
	Label          string         `json:"label,omitempty"`
	Config         map[string]any `json:"config,omitempty"`
	IdempotencyKey string         `json:"idempotencyKey,omitempty"` // FR-F7 at-least-once safety
}

// Edge connects two node ports ("nodeId:portName").
type Edge struct {
	From string `json:"from"`
	To   string `json:"to"`
}

// Flow is a versioned, directed acyclic graph of nodes.
type Flow struct {
	ID      string `json:"id"`
	Name    string `json:"name"`
	Version int    `json:"version"`
	Status  Status `json:"status"`
	Nodes   []Node `json:"nodes"`
	Edges   []Edge `json:"edges"`
}

// TopoOrder returns node IDs in execution (topological) order.
//
// M4 implements Kahn's algorithm with cycle detection (flows must be acyclic). M0 returns the
// declared order as a placeholder so the executor skeleton compiles and runs.
func (f *Flow) TopoOrder() []string {
	ids := make([]string, 0, len(f.Nodes))
	for _, n := range f.Nodes {
		ids = append(ids, n.ID)
	}
	return ids
}
