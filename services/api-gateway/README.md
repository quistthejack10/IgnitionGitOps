# api-gateway

The single front door (PRD §7.6): REST (`/api/v1`), generated GraphQL (`/graphql`), inbound
webhooks, and the MCP server. Observability at `/metrics`, `/healthz`, `/readyz`.

## Run (dev)

```bash
pip install -e ../../libs/forge-common -e .
uvicorn app.main:app --reload --port 8000
curl localhost:8000/healthz
```

## Status (M0)
Surfaces wired with placeholder behavior. The GraphQL/REST schema is generated from the user's
data model in M2 (graph-core); MCP handlers + RBAC/audit land in M6.
