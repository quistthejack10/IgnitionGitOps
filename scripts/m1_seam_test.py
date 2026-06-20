#!/usr/bin/env python3
"""M1 polyglot seam proof: Python → NATS → Go.

Publishes one test event from Python (via forge_common.NatsBus) to the NATS subject
`forge.events.test`, then waits briefly for any round-trip echo.

To observe the full seam:
  1. Start NATS: docker compose up -d nats
  2. Start flow-engine: docker compose up -d flow-engine
     (or: cd flow-engine && go run ./cmd/flow-engine)
  3. Run this script: python scripts/m1_seam_test.py
  4. Check flow-engine logs for: nats.received subject=forge.events.test

Usage:
    python scripts/m1_seam_test.py [--nats NATS_URL] [--subject SUBJECT]
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "libs" / "forge-common"))

from forge_common.bus import NatsBus
from forge_common.events import Event


async def main() -> None:
    parser = argparse.ArgumentParser(description="Forge M1 polyglot seam test")
    parser.add_argument(
        "--nats",
        default=os.environ.get("FORGE_NATS_URL", "nats://localhost:4222"),
    )
    parser.add_argument("--subject", default="forge.events.test")
    args = parser.parse_args()

    bus = NatsBus(args.nats)
    print(f"[seam] Connecting to NATS at {args.nats} ...")
    await bus.connect()

    evt = Event(
        type="dev.forge.test.ping",
        source="scripts/m1_seam_test",
        subject=args.subject,
        data={"msg": "hello from Python", "milestone": "M1"},
    )

    print("[seam] Publishing event:")
    print(f"       subject : {args.subject}")
    print(f"       type    : {evt.type}")
    print(f"       id      : {evt.id}")
    print(f"       data    : {evt.data}")
    print()

    await bus.publish(args.subject, evt)

    print("[seam] Published. Waiting 2 s for flow-engine to receive ...")
    await asyncio.sleep(2)

    await bus.close()
    print("[seam] Done.")
    print()
    print("→ Check flow-engine logs for:")
    print(f'      nats.received subject={args.subject} type={evt.type} id={evt.id[:8]}...')


if __name__ == "__main__":
    asyncio.run(main())
