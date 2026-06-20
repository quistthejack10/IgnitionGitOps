# connectivity

Manages **Connections** and exposes their data as **Sources** (subscribe/poll → Events on the
bus) and **Sinks** (writes, wrapped by store-and-forward). PRD §7.1.

- `base.py` — `Connection` / `Source` / `Sink` / `StoreAndForwardBuffer` contracts + health types.
- `manager.py` — `ConnectionManager` + health registry (FR-C11).
- `drivers/` — launch-set stubs: `opcua`, `mqtt_sparkplug`, `tcp`, `sql`, `rest` (M3).

## Status (M0)
Contracts + driver skeletons. Real protocol logic, store-and-forward, and the health dashboard
land in M3. Phase 2+ adds Kafka, Modbus, file watcher, EtherNet/IP, SAP.
