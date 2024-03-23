import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Bot,
  Boxes,
  BrainCircuit,
  Database,
  GitBranch,
  PackageSearch,
  Sparkles,
  Users,
} from "lucide-react";

import { api } from "../api/client";
import { useTenant } from "../context/TenantContext";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { ErrorState, Loading } from "../components/AsyncState";
import { Button } from "@/components/ui/button";

export function OverviewPage() {
  const { tenantId, tenant } = useTenant();

  const stats = useQuery({
    queryKey: ["stats", tenantId],
    queryFn: () => api.demo.stats(tenantId),
    enabled: Boolean(tenantId),
  });

  return (
    <>
      <PageHeader
        eyebrow="Local multi-tenant platform"
        title={`Systems overview${tenant ? ` · ${tenant.name}` : ""}`}
        description="Overview of customers, products, inventory, recommendations, agents, state events, external results and memory."
        actions={
          <Button asChild>
            <Link to="/demo-lab">
              <Sparkles />
              Run demo suite
            </Link>
          </Button>
        }
      />

      {stats.isLoading ? (
        <Loading />
      ) : stats.error ? (
