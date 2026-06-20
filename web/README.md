# web

Forge UI (React + TypeScript + Vite). App shell routes to the four surfaces: **Connections**,
**Flow Builder**, **Model Studio**, **Dashboards** (PRD §7.2/7.3/7.5).

- `src/canvas/FlowCanvas.tsx` — the shared **reactflow** canvas backing both the flow builder
  (FR-F1) and Model Studio (FR-M2); the two modes differ in palette and serialization target.
- `src/api/client.ts` — minimal GraphQL/REST client pointed at api-gateway (dev-proxied).

## Run (dev)

```bash
npm install
npm run dev        # http://localhost:5173, proxies /api + /graphql to :8000
npm run build      # tsc + vite build
```

## Status (M0)
App shell + interactive canvas placeholder. Node palettes, dashboard/form builders, and
operator screens land in M2/M4/M5.
