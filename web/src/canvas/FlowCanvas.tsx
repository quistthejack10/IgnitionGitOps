import { useCallback } from "react";
import ReactFlow, {
  addEdge,
  Background,
  Connection,
  Controls,
  Edge,
  Node,
  useEdgesState,
  useNodesState,
} from "reactflow";
import "reactflow/dist/style.css";

// Shared reactflow canvas backing both the Flow Builder (FR-F1) and Model Studio (FR-M2).
// The two modes differ in node palette and how the graph is persisted:
//   - "flow"  -> serialized to schemas/flow.schema.json and deployed to the Go engine.
//   - "model" -> serialized to schemas/model.schema.json and sent to graph-core.
// M0 renders a minimal interactive canvas to prove the integration; palettes land in M2/M4.
const initialNodes: Node[] = [
  { id: "1", position: { x: 80, y: 80 }, data: { label: "source" } },
  { id: "2", position: { x: 340, y: 160 }, data: { label: "transform" } },
];
const initialEdges: Edge[] = [{ id: "e1-2", source: "1", target: "2" }];

export function FlowCanvas({ mode }: { mode: "flow" | "model" }) {
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const onConnect = useCallback(
    (c: Connection) => setEdges((eds) => addEdge(c, eds)),
    [setEdges]
  );

  return (
    <div style={{ height: "100%" }}>
      <h2 style={{ marginTop: 0 }}>{mode === "flow" ? "Flow Builder" : "Model Studio"}</h2>
      <div style={{ height: "85%", border: "1px solid #ddd" }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}
