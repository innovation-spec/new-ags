import { useState, type ReactNode } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Activity,
  Bot,
  Boxes,
  BrainCircuit,
  ChartNoAxesCombined,
  DatabaseZap,
  FlaskConical,
  Gauge,
  GitBranch,
  Layers3,
  Menu,
  PackageSearch,
  PanelLeftClose,
  PanelLeftOpen,
  Route,
  ServerCog,
  ShieldCheck,
} from "lucide-react";
import { api } from "../api/client";
import { useTenant } from "../context/TenantContext";
import { StatusBadge } from "./StatusBadge";
import { ThemeToggle } from "./ThemeToggle";
import { Button } from "@/components/ui/button";
import {
  NativeSelect,
  NativeSelectOption,
} from "@/components/ui/native-select";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

const nav = [
  { to: "/", label: "Overview", icon: Gauge },
  { to: "/assistant", label: "AI Assistant", icon: Bot },
  {
    to: "/recommendations",
    label: "Recommendations",
    icon: ChartNoAxesCombined,
  },
  // { to: '/inventory', label: 'Catalog & Inventory', icon: Boxes },
  { to: "/agents", label: "Agent Runs", icon: Route },
  { to: "/state", label: "Shared State Lab", icon: GitBranch },
  { to: "/resilience", label: "Resilience & PPO", icon: ShieldCheck },
  { to: "/memory", label: "Memory", icon: BrainCircuit },
  // { to: '/models', label: 'Models & Schemas', icon: Layers3 },
  // { to: '/operations', label: 'Daily Operations', icon: Activity },
  // { to: '/coverage', label: 'R&D Coverage', icon: PackageSearch },
  { to: "/demo-lab", label: "Demo Lab", icon: FlaskConical },
];
