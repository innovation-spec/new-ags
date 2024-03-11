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
