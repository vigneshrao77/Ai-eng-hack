"use client";

import React from "react";
import Link from "next/link";

export function Navbar(_props: { projectId?: string }) {

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-white">
      <div className="max-w-[1440px] mx-auto px-8 h-[72px] flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <Link
            href="/"
            className="flex items-center space-x-2.5 group focus-visible:ring-2 focus-visible:ring-[var(--accent)] rounded py-1 px-1.5"
            aria-label="ModernRx Home"
          >
            <div className="w-9 h-9 rounded-[var(--radius-sm)] bg-[var(--primary)] text-[var(--primary-ink)] flex items-center justify-center font-bold text-sm">
              <span className="leading-none">M<span className="text-[var(--accent)]">/</span>R</span>
            </div>
            <div>
              <span className="text-[17px] font-semibold tracking-tight text-[var(--foreground)] flex items-center gap-2">
                ModernRx
                <span className="text-[10px] uppercase tracking-[0.16em] font-semibold px-2 py-1 rounded-[var(--radius-sm)] bg-[var(--surface-raised)] text-[var(--accent)] border border-[var(--border)]">GxP</span>
              </span>
            </div>
          </Link>
        </div>

        {/* Status and User */}
        <div className="flex items-center space-x-2.5">
          <div
            className="hidden sm:flex items-center space-x-1.5 px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface-raised)] text-[11px] text-[var(--ink-muted)] font-mono"
            role="status"
            aria-label="Validation Status"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[var(--success)]" aria-hidden="true" />
            <span>Standalone Validated</span>
          </div>
          <div
            className="hidden sm:block px-2 py-1 rounded bg-white text-[var(--ink-muted)] text-[11px] font-mono border border-[var(--border)]"
            role="status"
            aria-label="User Role"
          >
            Role: <span className="text-[var(--foreground)] font-bold">QA Approver</span>
          </div>
        </div>
      </div>
    </header>
  );
}
