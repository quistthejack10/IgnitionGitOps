# scripts

Spike and integration test scripts. Not part of the deployed system — developer tools only.

| Script | Milestone | Purpose |
|---|---|---|
| `m1_benchmark.py` | M1 | Load synthetic ISA-95 graph into Postgres+AGE and benchmark 5-hop genealogy traversal. Gates ADR-0001. |
| `m1_seam_test.py` | M1 | Publish one NATS event from Python; verified by observing the flow-engine log. Proves the polyglot seam. |

## Prerequisites

```bash
pip install -e libs/forge-common -e services/graph-core
docker compose up -d postgres nats
```

## M1 benchmark

```bash
# Quick local run (100K entities):
python scripts/m1_benchmark.py --count 100000 --runs 20

# Real spike (10M entities — allow ~10-20 min):
python scripts/m1_benchmark.py --count 10000000 --runs 100
```

Results are written to `docs/m1-benchmark-results.md`.

## M1 seam test

```bash
docker compose up -d nats flow-engine
python scripts/m1_seam_test.py
# Then: docker compose logs flow-engine | grep nats.received
```
