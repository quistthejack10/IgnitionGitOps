# M1 Benchmark Results — Postgres + Apache AGE

**Status: PASS** (target: p95 < 500 ms)

## Parameters
| Setting | Value |
|---|---|
| Entity count | 2,000 |
| Hops | 5 |
| Benchmark runs | 10 |
| DSN | `localhost:5432/forge` (host/db only) |

## Latency (genealogy traversal, 5-hop)
| Percentile | Latency |
|---|---|
| p50 | 124.5 ms |
| p95 | 130.8 ms ✅ |
| p99 | 130.8 ms |
| min | 116.4 ms |
| max | 130.8 ms |
| mean | 123.2 ms |

## Recommendation
**Keep Postgres + Apache AGE.** p95 is within the 500 ms target.

## Raw JSON
```json
{
  "p50_ms": 124.50262000004386,
  "p95_ms": 130.76778300001024,
  "p99_ms": 130.76778300001024,
  "min_ms": 116.44799200007583,
  "max_ms": 130.76778300001024,
  "mean_ms": 123.20109930003582
}
```

## ADR-0001 Action
Update `docs/adr/0001-graph-engine-postgres-age.md` status to **Accepted**.
