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
        <ErrorState error={stats.error} />
      ) : (
        <section className="metric-grid">
          <MetricCard
            label="Customers"
            value={stats.data?.customers ?? 0}
            icon={<Users />}
          />
          <MetricCard
            label="Products"
            value={stats.data?.products ?? 0}
            icon={<PackageSearch />}
          />
          <MetricCard
            label="Inventory rows"
            value={stats.data?.inventory_rows ?? 0}
            icon={<Boxes />}
          />
          <MetricCard
            label="Recommendations"
            value={stats.data?.recommendations ?? 0}
            icon={<Sparkles />}
          />
          <MetricCard
            label="Agent runs"
            value={stats.data?.agent_runs ?? 0}
            icon={<Bot />}
          />
          <MetricCard
            label="State events"
            value={stats.data?.state_events ?? 0}
            icon={<GitBranch />}
          />
          <MetricCard
            label="External results"
            value={stats.data?.external_results ?? 0}
            icon={<Database />}
          />
          <MetricCard
            label="Memory records"
            value={stats.data?.memory_entries ?? 0}
            icon={<BrainCircuit />}
          />
        </section>
      )}
    </>
  );
}
