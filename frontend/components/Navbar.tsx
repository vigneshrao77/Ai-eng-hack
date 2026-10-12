"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Layers,
  ShieldCheck,
  Cloud,
  GitFork,
  Users,
  Calendar,
  FileText,
  Lock,
  Cpu,
} from "lucide-react";

export function Navbar({ projectId }: { projectId?: string }) {
  const pathname = usePathname();

  const navItems = [
    { name: "Overview", href: projectId ? `/projects/${projectId}/overview` : "/", icon: Activity },
    { name: "Living Twin", href: projectId ? `/projects/${projectId}/twin` : "#", icon: Layers },
    { name: "GxP Scanner", href: projectId ? `/projects/${projectId}/gxp` : "#", icon: ShieldCheck },
    { name: "Cloud Readiness", href: projectId ? `/projects/${projectId}/readiness` : "#", icon: Cloud },
    { name: "Decomposition", href: projectId ? `/projects/${projectId}/decomposition` : "#", icon: GitFork },
    { name: "AI Council", href: projectId ? `/projects/${projectId}/council` : "#", icon: Users },
    { name: "Roadmap", href: projectId ? `/projects/${projectId}/roadmap` : "#", icon: Calendar },
    { name: "Evidence Pack", href: projectId ? `/projects/${projectId}/evidence` : "#", icon: FileText },
    { name: "Audit Trail", href: "/audit", icon: Lock },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-zinc-800 bg-black/95 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="w-7 h-7 rounded bg-white text-black flex items-center justify-center font-black text-xs">
              M
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-white flex items-center gap-2">
                ModernRx
                <span className="text-[10px] uppercase font-mono font-medium px-1.5 py-0.2 rounded bg-zinc-900 text-zinc-300 border border-zinc-700">
                  GxP
                </span>
              </span>
            </div>
          </Link>
        </div>

        {/* Navigation items */}
        <nav className="hidden md:flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            const isDisabled = item.href === "#";

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`px-2.5 py-1.5 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
                  isActive
                    ? "bg-white text-black font-semibold"
                    : isDisabled
                    ? "text-zinc-600 cursor-not-allowed"
                    : "text-zinc-400 hover:text-white hover:bg-zinc-900"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Status & User */}
        <div className="flex items-center space-x-2.5">
          <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded border border-zinc-800 bg-zinc-950 text-[11px] text-zinc-300 font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-white" />
            <span>Standalone Validated</span>
          </div>
          <div className="px-2 py-0.5 rounded bg-zinc-900 text-zinc-300 text-[11px] font-mono border border-zinc-800">
            Role: <span className="text-white font-bold">QA Approver</span>
          </div>
        </div>
      </div>
    </header>
  );
}
