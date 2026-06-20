import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { FlowCanvas } from "./canvas/FlowCanvas";

// App shell with the four primary surfaces (PRD §7.2/7.3/7.5).
// M0 routes render placeholders; the flow + model canvases share the reactflow component.
export function App() {
  return (
    <BrowserRouter>
      <div style={{ fontFamily: "system-ui", display: "flex", height: "100vh" }}>
        <nav style={{ width: 200, padding: 16, background: "#1b1f24", color: "#e6e6e6" }}>
          <h3>Forge MES</h3>
          <ul style={{ listStyle: "none", padding: 0, lineHeight: 2 }}>
            <li><Link style={{ color: "#9ecbff" }} to="/connections">Connections</Link></li>
            <li><Link style={{ color: "#9ecbff" }} to="/flows">Flow Builder</Link></li>
            <li><Link style={{ color: "#9ecbff" }} to="/model">Model Studio</Link></li>
            <li><Link style={{ color: "#9ecbff" }} to="/dashboards">Dashboards</Link></li>
          </ul>
        </nav>
        <main style={{ flex: 1, padding: 16 }}>
          <Routes>
            <Route path="/" element={<Placeholder title="Forge MES" note="Select a surface." />} />
            <Route path="/connections" element={<Placeholder title="Connections" note="Connection health dashboard (FR-C11, M3)." />} />
            <Route path="/flows" element={<FlowCanvas mode="flow" />} />
            <Route path="/model" element={<FlowCanvas mode="model" />} />
            <Route path="/dashboards" element={<Placeholder title="Dashboards" note="Grid/widget dashboard runtime (FR-S1, M5)." />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

function Placeholder({ title, note }: { title: string; note: string }) {
  return (
    <div>
      <h2>{title}</h2>
      <p style={{ color: "#666" }}>{note}</p>
    </div>
  );
}
