// Package event provides the Go mirror of schemas/event.schema.json — the CloudEvents-aligned
// envelope shared between all Forge services over the NATS bus (ADR-0002, ADR-0003).
//
// Keeping this in sync with the JSON Schema is the Go side of the polyglot seam. The Python
// side lives in libs/forge-common/forge_common/events.py.
package event

import "time"

// Event is the envelope for every message on the NATS bus.
type Event struct {
	Specversion     string         `json:"specversion"`
	ID              string         `json:"id"`
	Type            string         `json:"type"`
	Source          string         `json:"source"`
	Subject         string         `json:"subject,omitempty"`
	Time            time.Time      `json:"time"`
	Datacontenttype string         `json:"datacontenttype,omitempty"`
	Traceparent     string         `json:"traceparent,omitempty"`
	Data            map[string]any `json:"data"`
}
