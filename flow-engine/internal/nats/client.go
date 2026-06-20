// Package nats wraps the NATS client for the flow-engine.
//
// Python services and the Go engine never share types directly; they agree on the JSON
// event envelope (schemas/event.schema.json). This package handles the wire-level
// connect/subscribe/decode on the Go side of the polyglot seam.
package nats

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/forge-mes/flow-engine/internal/event"
	natsgo "github.com/nats-io/nats.go"
)

const (
	maxReconnects = 10
	reconnectWait = 2 * time.Second
)

// Handler is called for every event received on a subscribed subject.
type Handler func(e event.Event)

// Connect establishes a NATS connection with automatic reconnection.
func Connect(url string) (*natsgo.Conn, error) {
	nc, err := natsgo.Connect(url,
		natsgo.MaxReconnects(maxReconnects),
		natsgo.ReconnectWait(reconnectWait),
		natsgo.DisconnectErrHandler(func(_ *natsgo.Conn, err error) {
			log.Printf("nats.disconnected err=%v", err)
		}),
		natsgo.ReconnectHandler(func(nc *natsgo.Conn) {
			log.Printf("nats.reconnected url=%s", nc.ConnectedUrl())
		}),
	)
	if err != nil {
		return nil, fmt.Errorf("nats connect %s: %w", url, err)
	}
	log.Printf("nats.connected url=%s", nc.ConnectedUrl())
	return nc, nil
}

// Subscribe registers a handler on the given NATS subject pattern (supports wildcards, e.g. forge.events.>).
// Each message is deserialized from the shared event.schema.json envelope before dispatch.
func Subscribe(nc *natsgo.Conn, subject string, handler Handler) (*natsgo.Subscription, error) {
	sub, err := nc.Subscribe(subject, func(msg *natsgo.Msg) {
		var e event.Event
		if err := json.Unmarshal(msg.Data, &e); err != nil {
			log.Printf("nats.decode_error subject=%s err=%v raw=%s", msg.Subject, err, string(msg.Data))
			return
		}
		log.Printf("nats.received subject=%s type=%s id=%s source=%s", msg.Subject, e.Type, e.ID, e.Source)
		handler(e)
	})
	if err != nil {
		return nil, fmt.Errorf("nats subscribe %s: %w", subject, err)
	}
	log.Printf("nats.subscribed subject=%s", subject)
	return sub, nil
}
