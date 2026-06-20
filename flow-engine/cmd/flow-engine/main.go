// Command flow-engine is the Forge flow DAG runtime (ADR-0002).
//
// M1: connects to NATS and subscribes to forge.events.> — proves the polyglot seam.
//     /readyz now reports actual NATS connectivity.
// M4: full executor wiring (node dispatch, wire-tap, dead-letter/replay).
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"

	"github.com/forge-mes/flow-engine/internal/dag"
	"github.com/forge-mes/flow-engine/internal/event"
	natsclient "github.com/forge-mes/flow-engine/internal/nats"
	natsgo "github.com/nats-io/nats.go"
)

func main() {
	natsURL := getenv("FORGE_NATS_URL", "nats://localhost:4222")
	addr := getenv("FORGE_HEALTH_ADDR", ":8081")

	// --- NATS connection (polyglot seam, M1) ---
	nc, err := natsclient.Connect(natsURL)
	if err != nil {
		log.Fatalf("fatal: %v", err)
	}
	defer nc.Drain() //nolint:errcheck

	var eventsReceived atomic.Int64

	_, err = natsclient.Subscribe(nc, "forge.events.>", func(e event.Event) {
		eventsReceived.Add(1)
	})
	if err != nil {
		log.Fatalf("fatal: %v", err)
	}

	// --- Executor skeleton (M4 wires actual flow execution) ---
	exec := dag.NewExecutor(natsURL)
	log.Printf("flow-engine starting: nats=%s health=%s", natsURL, addr)

	// --- Health / readiness server ---
	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"status":"ok","service":"flow-engine"}`)
	})
	mux.HandleFunc("/readyz", func(w http.ResponseWriter, _ *http.Request) {
		natsStatus := natsConnStatus(nc)
		ready := natsStatus == "connected"
		status := http.StatusOK
		if !ready {
			status = http.StatusServiceUnavailable
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(status)
		body, _ := json.Marshal(map[string]any{
			"ready":          ready,
			"nats":           natsStatus,
			"events_received": eventsReceived.Load(),
		})
		w.Write(body) //nolint:errcheck
	})

	srv := &http.Server{Addr: addr, Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("health server: %v", err)
		}
	}()

	// --- Run until signal ---
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	if err := exec.Run(ctx); err != nil && err != context.Canceled {
		log.Printf("executor stopped: %v", err)
	}

	<-ctx.Done()
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = srv.Shutdown(shutdownCtx)
	log.Printf("flow-engine stopped (events_received=%d)", eventsReceived.Load())
}

func natsConnStatus(nc *natsgo.Conn) string {
	switch nc.Status() {
	case natsgo.CONNECTED:
		return "connected"
	case natsgo.CONNECTING, natsgo.RECONNECTING:
		return "connecting"
	default:
		return "disconnected"
	}
}

func getenv(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}
