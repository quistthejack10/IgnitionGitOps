#!/usr/bin/env python3
"""M1 graph-engine benchmark spike (ADR-0001 gate).

Loads a synthetic ISA-95 genealogy graph into Postgres + Apache AGE and measures
5-hop traversal latency. Pass/fail against the 500 ms p95 NFR determines whether
we keep AGE or fall back to Neo4j/Dgraph.

Usage:
    python scripts/m1_benchmark.py [--count N] [--hops H] [--runs R] [--dsn DSN]

Defaults: 100_000 entities (use 10_000_000 for the real spike), 5 hops, 100 runs.
The default DSN reads from FORGE_POSTGRES_DSN env var or falls back to localhost.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "graph-core"))

from app.store import AgeStore

P95_TARGET_MS = 500
BATCH_SIZE = 500


async def seed_graph(store: AgeStore, entity_count: int) -> list[str]:
    """Seed a synthetic ISA-95 genealogy graph; return a list of Lot _ids to sample."""
    print(f"\n[seed] Target: {entity_count:,} entities in batches of {BATCH_SIZE}")

    # --- Equipment hierarchy: sites -> areas -> lines -> cells -> units ---
    # Keep the hierarchy small (~1K nodes) so most of the count goes to Lots/WOs.
    n_sites = max(1, entity_count // 100_000)
    n_areas_per_site = 4
    n_lines_per_area = 3
    equipment_ids: list[str] = []

    print("[seed] Building equipment hierarchy...")
    for s in range(n_sites):
        site_id = f"site-{s:04d}"
        await store.create_entity("Equipment", {"_id": site_id, "name": f"Site {s}", "level": "Site"})
        equipment_ids.append(site_id)

        for a in range(n_areas_per_site):
            area_id = f"area-{s:04d}-{a:02d}"
            await store.create_entity("Equipment", {"_id": area_id, "name": f"Area {s}-{a}", "level": "Area"})
            await store.create_relationship("PART_OF", area_id, site_id)
            equipment_ids.append(area_id)

            for ln in range(n_lines_per_area):
                line_id = f"line-{s:04d}-{a:02d}-{ln:02d}"
                await store.create_entity("Equipment", {"_id": line_id, "name": f"Line {s}-{a}-{ln}", "level": "Line"})
                await store.create_relationship("PART_OF", line_id, area_id)
                equipment_ids.append(line_id)

    # --- Work Orders (one per line, staggered) ---
    n_work_orders = max(1, entity_count // 10)
    line_ids = [eid for eid in equipment_ids if eid.startswith("line-")]
    if not line_ids:
        line_ids = equipment_ids[:1]

    print(f"[seed] Creating {n_work_orders:,} work orders...")
    wo_ids: list[str] = []
    for i in range(0, n_work_orders, BATCH_SIZE):
        batch_end = min(i + BATCH_SIZE, n_work_orders)
        for j in range(i, batch_end):
            wo_id = f"wo-{j:08d}"
            line_id = line_ids[j % len(line_ids)]
            await store.create_entity(
                "WorkOrder",
                {"_id": wo_id, "orderNumber": wo_id, "state": "Complete"},
            )
            await store.create_relationship("RUNS_ON", wo_id, line_id)
            wo_ids.append(wo_id)
        pct = (batch_end / n_work_orders) * 100
        print(f"\r[seed]   work orders {batch_end:,}/{n_work_orders:,} ({pct:.0f}%)", end="", flush=True)
    print()

    # --- Lots (the bulk of entity_count, chained for genealogy traversal) ---
    n_lots = entity_count - len(equipment_ids) - n_work_orders
    n_lots = max(10, n_lots)

    print(f"[seed] Creating {n_lots:,} lots with genealogy edges...")
    lot_ids: list[str] = []
    for i in range(0, n_lots, BATCH_SIZE):
        batch_end = min(i + BATCH_SIZE, n_lots)
        for j in range(i, batch_end):
            lot_id = f"lot-{j:08d}"
            await store.create_entity("Lot", {"_id": lot_id, "lotId": lot_id, "quantity": random.randint(1, 1000)})
            lot_ids.append(lot_id)

            # Connect each lot to a work order (CONSUMED_BY) to build the genealogy graph.
            wo_id = wo_ids[j % len(wo_ids)]
            await store.create_relationship("CONSUMED_BY", lot_id, wo_id, {"quantity": random.randint(1, 100)})

            # Chain 20% of lots to a "parent" lot to create multi-hop paths.
            if j > 0 and j % 5 == 0:
                parent_lot_id = lot_ids[j - random.randint(1, min(5, j))]
                await store.create_relationship("PRODUCED_FROM", lot_id, parent_lot_id)

        pct = (batch_end / n_lots) * 100
        print(f"\r[seed]   lots {batch_end:,}/{n_lots:,} ({pct:.0f}%)", end="", flush=True)
    print()

    print(f"[seed] Done. Total entities: ~{len(equipment_ids) + n_work_orders + n_lots:,}")
    return lot_ids


async def run_benchmark(
    store: AgeStore,
    lot_ids: list[str],
    hops: int,
    runs: int,
) -> dict[str, float]:
    """Run R genealogy traversals; return latency percentiles in ms."""
    sample_ids = random.choices(lot_ids, k=runs)

    # Warm-up: 10% of runs, not timed.
    n_warmup = max(1, runs // 10)
    print(f"\n[bench] Warm-up ({n_warmup} runs)...")
    for lid in sample_ids[:n_warmup]:
        cypher = (
            f"MATCH path = (l:Lot {{_id: '{lid}'}})-[*1..{hops}]->(n) "
            "RETURN length(path) AS depth"
        )
        await store.raw_cypher(cypher, ["depth"])

    # Timed runs.
    print(f"[bench] Timing {runs} {hops}-hop traversals...")
    latencies: list[float] = []
    for lid in sample_ids:
        cypher = (
            f"MATCH path = (l:Lot {{_id: '{lid}'}})-[*1..{hops}]->(n) "
            "RETURN length(path) AS depth, n.`_id` AS node_id"
        )
        t0 = time.perf_counter()
        await store.raw_cypher(cypher, ["depth", "node_id"])
        latencies.append((time.perf_counter() - t0) * 1000)

    latencies.sort()
    n = len(latencies)
    return {
        "p50_ms": latencies[int(n * 0.50)],
        "p95_ms": latencies[int(n * 0.95)],
        "p99_ms": latencies[int(n * 0.99)],
        "min_ms": latencies[0],
        "max_ms": latencies[-1],
        "mean_ms": sum(latencies) / n,
    }


def write_results(results: dict[str, float], args: argparse.Namespace) -> Path:
    out = Path(__file__).parent.parent / "docs" / "m1-benchmark-results.md"
    passed = results["p95_ms"] < P95_TARGET_MS
    status = "PASS" if passed else "FAIL"
    recommendation = (
        "**Keep Postgres + Apache AGE.** p95 is within the 500 ms target."
        if passed
        else f"**Consider fallback to Neo4j or Dgraph.** p95 ({results['p95_ms']:.1f} ms) exceeds the 500 ms target."
    )

    content = f"""# M1 Benchmark Results — Postgres + Apache AGE

**Status: {status}** (target: p95 < {P95_TARGET_MS} ms)

## Parameters
| Setting | Value |
|---|---|
| Entity count | {args.count:,} |
| Hops | {args.hops} |
| Benchmark runs | {args.runs} |
| DSN | `{args.dsn.split('@')[-1]}` (host/db only) |

## Latency (genealogy traversal, {args.hops}-hop)
| Percentile | Latency |
|---|---|
| p50 | {results["p50_ms"]:.1f} ms |
| p95 | {results["p95_ms"]:.1f} ms {"✅" if results["p95_ms"] < P95_TARGET_MS else "❌"} |
| p99 | {results["p99_ms"]:.1f} ms |
| min | {results["min_ms"]:.1f} ms |
| max | {results["max_ms"]:.1f} ms |
| mean | {results["mean_ms"]:.1f} ms |

## Recommendation
{recommendation}

## Raw JSON
```json
{json.dumps(results, indent=2)}
```

## ADR-0001 Action
Update `docs/adr/0001-graph-engine-postgres-age.md` status to **{"Accepted" if passed else "Rejected — switching to Neo4j/Dgraph"}**.
"""
    out.write_text(content)
    return out


async def main() -> None:
    parser = argparse.ArgumentParser(description="Forge M1 AGE benchmark spike")
    parser.add_argument("--count", type=int, default=100_000, help="Entity count (default 100K; use 10M for real spike)")
    parser.add_argument("--hops", type=int, default=5, help="Max hops for traversal (default 5)")
    parser.add_argument("--runs", type=int, default=100, help="Timed benchmark runs (default 100)")
    parser.add_argument(
        "--dsn",
        default=os.environ.get("FORGE_POSTGRES_DSN", "postgresql://forge:forge@localhost:5432/forge"),
    )
    args = parser.parse_args()

    print("Forge M1 benchmark — Postgres + Apache AGE")
    print(f"  DSN: {args.dsn.split('@')[-1]}  entities: {args.count:,}  hops: {args.hops}  runs: {args.runs}")

    store = AgeStore(args.dsn)
    await store.connect()

    t_seed_start = time.perf_counter()
    lot_ids = await seed_graph(store, args.count)
    seed_secs = time.perf_counter() - t_seed_start
    print(f"\n[seed] Seeding done in {seed_secs:.1f}s ({args.count / seed_secs:,.0f} entities/s)")

    results = await run_benchmark(store, lot_ids, args.hops, args.runs)
    await store.close()

    print(f"\n{'='*50}")
    print(f"  p50: {results['p50_ms']:.1f} ms")
    print(f"  p95: {results['p95_ms']:.1f} ms  ({'PASS ✅' if results['p95_ms'] < P95_TARGET_MS else 'FAIL ❌'}  target < {P95_TARGET_MS} ms)")
    print(f"  p99: {results['p99_ms']:.1f} ms")
    print(f"{'='*50}\n")

    out = write_results(results, args)
    print(f"Results written to: {out}")

    sys.exit(0 if results["p95_ms"] < P95_TARGET_MS else 1)


if __name__ == "__main__":
    asyncio.run(main())
