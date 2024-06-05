import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { OverviewPage } from "./pages/OverviewPage";
import { AssistantPage } from "./pages/AssistantPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";
import { InventoryPage } from "./pages/InventoryPage";
import { AgentRunsPage } from "./pages/AgentRunsPage";
import { StateLabPage } from "./pages/StateLabPage";
import { ResiliencePage } from "./pages/ResiliencePage";
import { MemoryPage } from "./pages/MemoryPage";
import { ModelsSchemasPage } from "./pages/ModelsSchemasPage";
import { OperationsPage } from "./pages/OperationsPage";
import { CoveragePage } from "./pages/CoveragePage";
import { DemoLabPage } from "./pages/DemoLabPage";

export function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<OverviewPage />} />
        <Route path="assistant" element={<AssistantPage />} />
        <Route path="recommendations" element={<RecommendationsPage />} />
        {/* <Route path="inventory" element={<InventoryPage />} /> */}
        <Route path="agents" element={<AgentRunsPage />} />
        <Route path="state" element={<StateLabPage />} />
        <Route path="resilience" element={<ResiliencePage />} />
        <Route path="memory" element={<MemoryPage />} />
        {/* - <Route path="models" element={<ModelsSchemasPage />} /> */}
        {/* <Route path="operations" element={<OperationsPage />} /> */}
        {/* <Route path="coverage" element={<CoveragePage />} /> */}
        <Route path="demo-lab" element={<DemoLabPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
