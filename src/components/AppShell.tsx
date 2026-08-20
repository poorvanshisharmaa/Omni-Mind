import { Link, useRouterState } from "@tanstack/react-router";
import { AudioLines, FileText, Languages, Moon, Search, Sun } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { cn } from "@/lib/utils";

const NAV = [
  { to: "/", label: "Meeting Intelligence", icon: AudioLines },
  { to: "/documents", label: "Document Intelligence", icon: FileText },
  { to: "/translator", label: "Universal Translator", icon: Languages },
] as const;

function ThemeToggle() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  return (
    <button
      type="button"
      aria-label="Toggle color theme"
      onClick={() => setDark((d) => !d)}
      className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-card text-muted-foreground transition-colors hover:text-foreground"
    >
      {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </button>
  );
}

export function AppShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-sidebar-border bg-sidebar md:flex">
        <div className="flex h-16 items-center gap-2.5 px-5">
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-[11px] font-semibold tracking-tight text-primary-foreground">
            OM
          </span>
          <span className="text-[15px] font-semibold tracking-tight text-sidebar-foreground">
            OmniMind
          </span>
        </div>
        <nav className="flex flex-col gap-0.5 px-3 py-2">
          <p className="px-2 pb-2 pt-3 text-[11px] font-medium uppercase tracking-widest text-muted-foreground">
            Workspaces
          </p>
          {NAV.map(({ to, label, icon: Icon }) => {
            const active = pathname === to;
            return (
              <Link
                key={to}
                to={to}
                className={cn(
                  "flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors",
                  active
                    ? "bg-sidebar-accent font-medium text-sidebar-accent-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/60 hover:text-sidebar-foreground",
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto px-5 py-5 text-[11px] leading-relaxed text-muted-foreground">
          Enterprise workspace
          <br />
          BFSI · SOC 2 · Data residency IN
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-border bg-background/85 px-5 backdrop-blur md:px-8">
          <label className="relative flex w-full max-w-md items-center">
            <Search className="pointer-events-none absolute left-3 h-4 w-4 text-muted-foreground" />
            <input
              placeholder="Cross-lingual search across meetings & documents…"
              className="h-9 w-full rounded-md border border-input bg-card pl-9 pr-3 text-sm outline-none placeholder:text-muted-foreground focus:border-ring focus:ring-2 focus:ring-ring/25"
            />
          </label>
          <div className="ml-auto flex items-center gap-2">
            <span className="hidden rounded-md border border-border px-2 py-1 text-[11px] text-muted-foreground sm:inline">
              12 languages
            </span>
            <ThemeToggle />
          </div>
        </header>

        <nav className="flex gap-1 border-b border-border px-4 py-2 md:hidden">
          {NAV.map(({ to, label, icon: Icon }) => (
            <Link
              key={to}
              to={to}
              className={cn(
                "flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs",
                pathname === to
                  ? "bg-secondary font-medium text-secondary-foreground"
                  : "text-muted-foreground",
              )}
            >
              <Icon className="h-3.5 w-3.5" />
              {label.split(" ")[0]}
            </Link>
          ))}
        </nav>

        <main className="flex-1 px-5 py-8 md:px-10">
          <div className="mx-auto max-w-6xl">
            <header className="mb-8">
              <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
              {subtitle && (
                <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground">{subtitle}</p>
              )}
            </header>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
