# Helm chart (Phase 2 HA)

Placeholder for the **HA cluster** deployment (PRD §6.1 option 2): k3s/Kubernetes + Helm,
3+ nodes, per-plant `values-<plant>.yaml` overrides for multi-site rollouts, rolling upgrades,
and horizontal scaling of flow partitions (FR-F7).

Built in Phase 2. The single-node Docker Compose path (repo root `docker-compose.yml`) is the
v1 entry point.
