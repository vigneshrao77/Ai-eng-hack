"use client";

import React, { useState } from "react";
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
  Menu,
  X,
} from "lucide-react";

export function Navbar({ projectId }: { projectId?: string }) {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
          <Link
            href="/"
            className="flex items-center space-x-2.5 group focus-visible:ring-2 focus-visible:ring-white rounded py-1 px-1.5"
            aria-label="ModernRx Home"
          >
            <div className="w-7 h-7 rounded bg-white text-black flex items-center justify-center font-black text-xs">
              M
            </div>
            <div>
              <span className="text-base font-bold tracking-tight text-white flex items-center gap-2">
                ModernRx
                <span className="text-[10px] uppercase font-mono font-medium px-1.5 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-700">
                  GxP
                </span>
              </span>
            </div>
          </Link>
        </div>

        {/* Desktop Navigation items */}
        <nav className="hidden md:flex items-center space-x-1" aria-label="Main Navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            const isDisabled = item.href === "#";

            return (
              <Link
                key={item.name}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={`px-2.5 py-1.5 min-h-[36px] rounded text-xs font-medium flex items-center gap-1.5 transition-colors focus-visible:ring-2 focus-visible:ring-white ${
                  isActive
                    ? "bg-white text-black font-semibold"
                    : isDisabled
                    ? "text-zinc-600 cursor-not-allowed"
                    : "text-zinc-400 hover:text-white hover:bg-zinc-900"
                }`}
              >
                <Icon className="w-3.5 h-3.5" aria-hidden="true" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Status, User & Mobile Menu Toggle */}
        <div className="flex items-center space-x-2.5">
          <div
            className="hidden sm:flex items-center space-x-1.5 px-2 py-0.5 rounded border border-zinc-800 bg-zinc-950 text-[11px] text-zinc-300 font-mono"
            role="status"
            aria-label="Validation Status"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-white" aria-hidden="true" />
            <span>Standalone Validated</span>
          </div>
          <div
            className="hidden sm:block px-2 py-0.5 rounded bg-zinc-900 text-zinc-300 text-[11px] font-mono border border-zinc-800"
            role="status"
            aria-label="User Role"
          >
            Role: <span className="text-white font-bold">QA Approver</span>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded text-zinc-400 hover:text-white hover:bg-zinc-900 focus-visible:ring-2 focus-visible:ring-white border border-zinc-800 min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-expanded={mobileMenuOpen}
            aria-controls="mobile-navigation"
            aria-label={mobileMenuOpen ? "Close navigation menu" : "Open navigation menu"}
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div
          id="mobile-navigation"
          className="md:hidden border-t border-zinc-800 bg-black/98 px-4 pt-2 pb-4 space-y-1"
          role="navigation"
          aria-label="Mobile Navigation"
        >
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            const isDisabled = item.href === "#";

            return (
              <Link
                key={item.name}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                aria-current={isActive ? "page" : undefined}
                className={`flex items-center gap-2.5 px-3 py-2.5 min-h-[44px] rounded text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-white text-black font-semibold"
                    : isDisabled
                    ? "text-zinc-600 cursor-not-allowed"
                    : "text-zinc-300 hover:text-white hover:bg-zinc-900"
                }`}
              >
                <Icon className="w-4 h-4" aria-hidden="true" />
                <span>{item.name}</span>
              </Link>
            );
          })}
          <div className="pt-2 border-t border-zinc-900 flex items-center justify-between text-xs font-mono text-zinc-400 px-1">
            <span>Validated: Standalone</span>
            <span>Role: QA Approver</span>
          </div>
        </div>
      )}
    </header>
  );
}

