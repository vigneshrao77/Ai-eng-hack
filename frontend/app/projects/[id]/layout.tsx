"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useParams } from "next/navigation";
import {
  Layers,
  Network,
  ShieldAlert,
  Gauge,
  Split,
  Users2,
  CalendarDays,
  FileCheck2,
  ArrowLeft,
} from "lucide-react";

export default function ProjectLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const params = useParams();
  const id = (params?.id as string) || "acmelims-demo";

  const navItems = [
    { name: "Overview", href: `/projects/${id}/overview`, icon: Layers },
    { name: "Twin Graph", href: `/projects/${id}/twin`, icon: Network },
    { name: "GxP Scanner", href: `/projects/${id}/gxp`, icon: ShieldAlert },
    { name: "Readiness", href: `/projects/${id}/readiness`, icon: Gauge },
    { name: "Decomposition", href: `/projects/${id}/decomposition`, icon: Split },
    { name: "AI Council", href: `/projects/${id}/council`, icon: Users2 },
    { name: "Roadmap", href: `/projects/${id}/roadmap`, icon: CalendarDays },
    { name: "Evidence Packs", href: `/projects/${id}/evidence`, icon: FileCheck2 },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Top Project Subheader */}
      <div className="rounded-[var(--radius-md)] p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-[var(--border)] bg-white shadow-[var(--shadow-1)]">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="p-2.5 rounded-[var(--radius-sm)] bg-white hover:bg-[var(--surface-raised)] border border-[var(--border)] text-[var(--ink-muted)] hover:text-[var(--foreground)] transition-colors"
            title="Back to Projects"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-semibold text-[var(--foreground)] tracking-tight">
                {id === "acmelims-demo" ? "AcmeLIMS (Legacy Monolith)" : id}
              </h1>
              <span className="text-[10px] px-2 py-1 rounded-[var(--radius-sm)] bg-[#edf6f0] text-[var(--success)] border border-[#cce6d5] tracking-[0.12em] uppercase">
                ACTIVE ASSESSMENT
              </span>
            </div>
            <p className="text-sm text-[var(--ink-muted)] mt-1">
              Target cloud <span className="text-[var(--foreground)]">AWS</span><span className="mx-2 text-[var(--border-strong)]">/</span>
              Scope <span className="text-[var(--foreground)]">Full monolith modernization</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-[var(--ink-muted)] bg-[var(--surface-raised)] px-3 py-2 rounded-[var(--radius-sm)] border border-[var(--border)]">
          <span className="w-2 h-2 rounded-full bg-[var(--accent)]" aria-hidden="true" />
          <span>Annex 11 / Part 11 regulated system</span>
        </div>
      </div>

      {/* Project modules */}
      <nav
        className="flex overflow-x-auto gap-5 border-b border-[var(--border)] pb-0 scrollbar-none"
        role="tablist"
        aria-label="Project Modules"
      >
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              role="tab"
              aria-selected={isActive}
              className={`relative flex items-center gap-2 px-1 py-3 min-h-[42px] text-xs font-medium whitespace-nowrap transition-colors focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
                isActive
                  ? "text-[var(--primary)] font-semibold after:absolute after:inset-x-0 after:-bottom-px after:h-0.5 after:bg-[var(--primary)]"
                  : "text-[var(--ink-muted)] hover:text-[var(--foreground)]"
              }`}
            >
              <Icon className="w-4 h-4" aria-hidden="true" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Main Tab Content */}
      <div>{children}</div>
    </div>
  );
}
