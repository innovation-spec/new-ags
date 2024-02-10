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
