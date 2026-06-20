# platform services

On-prem platform plumbing (PRD §7.6). Built out in **M6**; this directory is a placeholder so
the structure and ownership are clear.

| Capability | PRD | Notes |
|---|---|---|
| **AuthN/Z** | FR-P1 | OIDC via bundled Keycloak federating to AD/LDAP; RBAC roles (Admin, Builder, Supervisor, Operator, Viewer, Service); per-resource permissions; API keys + scoped service tokens |
| **Audit trail** | FR-P2 | Immutable log of every config change (who/what/when/before/after) and MES transaction; exportable; 21 CFR Part 11 alignment (P2) |
| **Backup & restore** | FR-P3 | One-command full backup (config + graph + time-series) to local/S3-compatible; scheduled |
| **Offline licensing** | FR-P4 | License-file based, no phone-home; read-only grace on expiry, never data loss |
| **Observability** | FR-P5 | Prometheus endpoint (already in `forge-common`), structured JSON logs, health/readiness, optional bundled Grafana |

The MCP server (FR-P7) lives in `api-gateway` but runs every action through the RBAC + audit
pipeline defined here.
