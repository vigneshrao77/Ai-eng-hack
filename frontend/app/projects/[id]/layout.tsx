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
    <div className="space-y-6 animate-fadeIn">
      {/* Top Project Subheader */}
      <div className="rounded-xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 border border-zinc-800 bg-zinc-950">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="p-2 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 hover:text-white transition-colors"
            title="Back to Projects"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-white tracking-tight">
                {id === "acmelims-demo" ? "AcmeLIMS (Legacy Monolith)" : id}
              </h1>
              <span className="text-[11px] px-2 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-700 font-mono">
                ACTIVE ASSESSMENT
              </span>
            </div>
            <p className="text-xs text-zinc-400 font-mono mt-0.5">
              Target Cloud: <span className="text-zinc-200">AWS</span> &nbsp;|&nbsp; 
              Scope: <span className="text-zinc-200">Full Monolith Modernization</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-zinc-300 bg-zinc-900 px-3 py-1.5 rounded border border-zinc-800 font-mono">
          <span>Annex 11 / Part 11 Regulated System</span>
        </div>
      </div>

      {/* Modern Horizontal Navigation Tabs - Black & White */}
      <div className="flex overflow-x-auto gap-1 border-b border-zinc-800 pb-2 scrollbar-none">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2 px-3.5 py-2 rounded text-xs font-medium whitespace-nowrap transition-colors ${
                isActive
                  ? "bg-white text-black font-semibold"
                  : "text-zinc-400 hover:text-white hover:bg-zinc-900"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Main Tab Content */}
      <div>{children}</div>
    </div>
  );
}
