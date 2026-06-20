// Command flow-engine is the Forge flow DAG runtime (ADR-0002).
//
// It connects to NATS, loads published flow definitions (schemas/flow.schema.json), and
// executes them with at-least-once semantics and per-node observability. This M0 entrypoint
// starts the health server and bootstraps the executor; NATS wiring and node logic land in
// M1/M4.
package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/forge-mes/flow-engine/internal/dag"
)

func main() {
	natsURL := getenv("FORGE_NATS_URL", "nats://localhost:4222")
	addr := getenv("FORGE_HEALTH_ADDR", ":8081")

	exec := dag.NewExecutor(natsURL)
	log.Printf("flow-engine starting: nats=%s health=%s", natsURL, addr)

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"status":"ok","service":"flow-engine"}`))
	})
	mux.HandleFunc("/readyz", func(w http.ResponseWriter, _ *http.Request) {
		// M1: report NATS connectivity. M0: always ready.
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"ready":true}`))
	})

	srv := &http.Server{Addr: addr, Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("health server error: %v", err)
		}
	}()

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	// M1: exec.Run subscribes to flow-trigger subjects and dispatches events through the DAG.
	if err := exec.Run(ctx); err != nil {
		log.Printf("executor stopped: %v", err)
	}

	<-ctx.Done()
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = srv.Shutdown(shutdownCtx)
	log.Println("flow-engine stopped")
}

func getenv(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}
