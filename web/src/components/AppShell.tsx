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

function Navigation({
  collapsed = false,
  afterNavigate,
}: {
  collapsed?: boolean;
  afterNavigate?: () => void;
}) {
  return (
    <nav className="flex flex-1 flex-col gap-1 overflow-y-auto py-2">
      {nav.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          onClick={afterNavigate}
          className={({ isActive }) =>
            cn(
              "flex h-10 items-center gap-3 rounded-md px-3 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground",
              isActive && "bg-primary/10 text-primary shadow-sm",
              collapsed && "justify-center px-0",
            )
          }
          title={collapsed ? label : undefined}
        >
          <Icon className="size-4 shrink-0" />
          {!collapsed && <span>{label}</span>}
        </NavLink>
      ))}
    </nav>
  );
}

function Brand({ collapsed = false }: { collapsed?: boolean }) {
  return (
    <div
      className={cn(
        "flex h-14 items-center gap-3 border-b px-2",
        collapsed && "justify-center",
      )}
    >
      <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-primary/20 bg-primary/10 text-primary">
        <DatabaseZap className="size-5" />
      </div>
      {!collapsed && (
        <div className="min-w-0">
          <strong className="block text-xs tracking-[.16em]">AGASTHYA</strong>
          <span className="block truncate text-[11px] text-muted-foreground">
            AI Systems Console
          </span>
        </div>
      )}
    </div>
  );
}

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { tenants, tenantId, setTenantId, isLoading } = useTenant();
  const health = useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 30_000,
  });
  const shellStatus: ReactNode = (
    <>
      <StatusBadge
        status={
          health.data?.openai_enabled ? "OpenAI enabled" : "OpenAI disabled"
        }
      />
      <span className="local-pill">
        <DatabaseZap className="size-3.5" />
        Local stack
      </span>
    </>
  );

  return (
    <div className={cn("app-shell", collapsed && "sidebar-collapsed")}>
      <aside className="sidebar hidden md:flex">
        <Brand collapsed={collapsed} />
        <Navigation collapsed={collapsed} />
        <div className="mt-auto grid gap-2 border-t pt-3">
          <div
            className={cn(
              "flex items-center gap-2 px-2 text-xs text-muted-foreground",
              collapsed && "justify-center",
            )}
          >
            <ServerCog className="size-4" />
            {!collapsed && (
              <>
                <span>FastAPI</span>
                <span className="ml-auto">
                  <StatusBadge
                    status={health.data?.status === "ok" ? "ok" : "unavailable"}
                  />
                </span>
              </>
            )}
          </div>
          <Button
            variant="ghost"
            size={collapsed ? "icon" : "sm"}
            onClick={() => setCollapsed((v) => !v)}
            className={cn(!collapsed && "justify-start")}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? <PanelLeftOpen /> : <PanelLeftClose />}
            {!collapsed && "Collapse"}
          </Button>
        </div>
      </aside>

      <div className="main-column">
        <header className="topbar">
          <div className="flex min-w-0 items-center gap-2">
            <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
              <SheetTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="md:hidden"
                  aria-label="Open navigation"
                >
                  <Menu />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="flex w-[300px] flex-col p-3">
                <SheetHeader className="sr-only">
                  <SheetTitle>Navigation</SheetTitle>
                  <SheetDescription>
                    Agasthya console navigation
                  </SheetDescription>
                </SheetHeader>
                <Brand />
                <Navigation afterNavigate={() => setMobileOpen(false)} />
              </SheetContent>
            </Sheet>
            <div className="tenant-control min-w-0">
              <span className="hidden sm:inline">Active tenant</span>
              <NativeSelect
                aria-label="Active tenant"
                value={tenantId}
                disabled={isLoading || !tenants.length}
                onChange={(e) => setTenantId(e.target.value)}
                className="min-w-[190px]"
              >
                {!tenantId && (
                  <NativeSelectOption value="">
                    Loading tenants…
                  </NativeSelectOption>
                )}
                {tenants.map((tenant) => (
                  <NativeSelectOption key={tenant.id} value={tenant.id}>
                    {tenant.name}
                  </NativeSelectOption>
                ))}
              </NativeSelect>
            </div>
          </div>
          <div className="topbar-status">
            <div className="hidden items-center gap-2 lg:flex">
              {shellStatus}
            </div>
            <ThemeToggle />
          </div>
        </header>
        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
