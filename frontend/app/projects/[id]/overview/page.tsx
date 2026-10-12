"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Activity,
  Layers,
  ShieldAlert,
  Gauge,
  Split,
  Users2,
  CalendarDays,
  FileCheck2,
  ArrowRight,
  TrendingDown,
  CheckCircle2,
  AlertTriangle,
  Clock,
} from "lucide-react";
import { fetchReadiness, fetchGxp, fetchDecomposition, fetchRoadmap } from "@/lib/api";

export default function OverviewPage() {
  const params = useParams();
  const id = (params?.id as string) || "acmelims-demo";

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    loc: 8450,
    components: 10,
    readinessAvg: 68.4,
    highGxpCount: 4,
    p80Weeks: 18.5,
    revalScopeReduction: 44.0,
  });

  useEffect(() => {
    async function loadData() {
      try {
        const [readiness, gxp, decomp, roadmap] = await Promise.allSettled([
          fetchReadiness(id),
          fetchGxp(id),
          fetchDecomposition(id),
          fetchRoadmap(id),
        ]);

        let rAvg = 68.4;
        if (readiness.status === "fulfilled" && readiness.value?.average_readiness_score) {
          rAvg = readiness.value.average_readiness_score;
        }

        let highCount = 4;
        if (gxp.status === "fulfilled" && gxp.value?.summary?.HIGH !== undefined) {
          highCount = gxp.value.summary.HIGH;
        }

        let redPct = 44.0;
        if (decomp.status === "fulfilled" && decomp.value?.headline_comparison?.reval_scope_reduction_pct !== undefined) {
          redPct = decomp.value.headline_comparison.reval_scope_reduction_pct;
        }

        let p80 = 18.5;
        if (roadmap.status === "fulfilled" && roadmap.value?.monte_carlo?.p80_weeks) {
          p80 = roadmap.value.monte_carlo.p80_weeks;
        }

        setStats({
          loc: 8450,
          components: 10,
          readinessAvg: Math.round(rAvg * 10) / 10,
          highGxpCount: highCount,
          p80Weeks: p80,
          revalScopeReduction: redPct,
        });
      } catch (e) {
        console.error("Error loading overview data:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* KPI Cards Grid - Clean Monochromatic */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="rounded-lg p-4 border border-zinc-800 bg-zinc-950">
          <div className="text-xs text-zinc-400 font-mono">Source Size</div>
          <div className="text-2xl font-bold text-white mt-1">{stats.loc.toLocaleString()}</div>
          <div className="text-[11px] text-zinc-500 font-mono mt-1">Java &bull; SQL &bull; Config</div>
        </div>

        <div className="rounded-lg p-4 border border-zinc-800 bg-zinc-950">
          <div className="text-xs text-zinc-400 font-mono">Components</div>
          <div className="text-2xl font-bold text-white mt-1">{stats.components}</div>
          <div className="text-[11px] text-zinc-500 font-mono mt-1">Twin AST Nodes</div>
        </div>

        <div className="rounded-lg p-4 border border-zinc-800 bg-zinc-950">
          <div className="text-xs text-zinc-400 font-mono">Cloud Readiness</div>
          <div className="text-2xl font-bold text-white mt-1">{stats.readinessAvg}/100</div>
          <div className="text-[11px] text-zinc-500 font-mono mt-1">11 Deterministic Checks</div>
        </div>

        <div className="rounded-lg p-4 border border-zinc-800 bg-zinc-950">
          <div className="text-xs text-zinc-400 font-mono">HIGH GxP Critical</div>
          <div className="text-2xl font-bold text-white mt-1">{stats.highGxpCount}</div>
          <div className="text-[11px] text-zinc-500 font-mono mt-1">Part 11 Core Nodes</div>
        </div>

        <div className="rounded-lg p-4 border border-zinc-800 bg-zinc-950">
          <div className="text-xs text-zinc-400 font-mono">Blast Radius Cut</div>
          <div className="text-2xl font-bold text-white mt-1 flex items-center gap-1">
            <TrendingDown className="w-5 h-5 text-white" />
            <span>{stats.revalScopeReduction}%</span>
          </div>
          <div className="text-[11px] text-zinc-500 font-mono mt-1">vs Plain HDBSCAN</div>
        </div>

        <div className="rounded-lg p-4 border border-zinc-800 bg-zinc-950">
          <div className="text-xs text-zinc-400 font-mono">Est. Duration (P80)</div>
          <div className="text-2xl font-bold text-white mt-1 flex items-center gap-1">
            <Clock className="w-4 h-4 text-white" />
            <span>{stats.p80Weeks} wks</span>
          </div>
          <div className="text-[11px] text-zinc-500 font-mono mt-1">10,000 PERT Runs</div>
        </div>
      </div>

      {/* The 7 ModernRx Modernization Engines Section - Black & White */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-white">ModernRx 7-Engine Architecture Pipeline</h2>
            <p className="text-xs text-zinc-400 font-mono">Step-by-step audit-compliant pipeline from raw repository to verified cloud waves</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            href={`/projects/${id}/twin`}
            className="p-5 rounded-lg border border-zinc-800 bg-zinc-950 hover:border-zinc-500 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-white">
                <Layers className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-zinc-400 font-mono border border-zinc-800 px-1.5 py-0.5 rounded">ENGINE 1</span>
            </div>
            <h3 className="font-semibold text-white mt-3 text-sm">Living Architecture Twin</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Tree-sitter AST, SQL reads/writes, secret masking, and interactive Cytoscape graph.
            </p>
            <div className="mt-4 flex items-center text-xs text-white font-medium group-hover:translate-x-1 transition-transform">
              <span>Inspect Knowledge Graph</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            href={`/projects/${id}/gxp`}
            className="p-5 rounded-lg border border-zinc-800 bg-zinc-950 hover:border-zinc-500 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-white">
                <ShieldAlert className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-zinc-400 font-mono border border-zinc-800 px-1.5 py-0.5 rounded">ENGINE 2</span>
            </div>
            <h3 className="font-semibold text-white mt-3 text-sm">GxP Criticality Scanner</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              21 CFR Part 11 / EU Annex 11 rule engine with call propagation and immutable QA overrides.
            </p>
            <div className="mt-4 flex items-center text-xs text-white font-medium group-hover:translate-x-1 transition-transform">
              <span>Review Compliance Gaps</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            href={`/projects/${id}/readiness`}
            className="p-5 rounded-lg border border-zinc-800 bg-zinc-950 hover:border-zinc-500 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-white">
                <Gauge className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-zinc-400 font-mono border border-zinc-800 px-1.5 py-0.5 rounded">ENGINE 3</span>
            </div>
            <h3 className="font-semibold text-white mt-3 text-sm">Cloud Readiness Scorer</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Explainable 0–100 score across 11 architectural checks with traceable deduction nodes.
            </p>
            <div className="mt-4 flex items-center text-xs text-white font-medium group-hover:translate-x-1 transition-transform">
              <span>View Score Deductions</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            href={`/projects/${id}/decomposition`}
            className="p-5 rounded-lg border border-zinc-800 bg-zinc-950 hover:border-zinc-500 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-white">
                <Split className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-zinc-400 font-mono border border-zinc-800 px-1.5 py-0.5 rounded">ENGINE 4</span>
            </div>
            <h3 className="font-semibold text-white mt-3 text-sm">Decomposition &amp; RevalScope</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Louvain vs plain HDBSCAN vs ModernRx constrained clustering with RevalScope reduction.
            </p>
            <div className="mt-4 flex items-center text-xs text-white font-medium group-hover:translate-x-1 transition-transform">
              <span>Compare 3 Partitions</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            href={`/projects/${id}/council`}
            className="p-5 rounded-lg border border-zinc-800 bg-zinc-950 hover:border-zinc-500 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-white">
                <Users2 className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-zinc-400 font-mono border border-zinc-800 px-1.5 py-0.5 rounded">ENGINE 5</span>
            </div>
            <h3 className="font-semibold text-white mt-3 text-sm">AI Architecture Council</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Multi-agent specialist debate, rebuttal round, moderator consensus, and QA approval gate.
            </p>
            <div className="mt-4 flex items-center text-xs text-white font-medium group-hover:translate-x-1 transition-transform">
              <span>Inspect Council Debate</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            href={`/projects/${id}/roadmap`}
            className="p-5 rounded-lg border border-zinc-800 bg-zinc-950 hover:border-zinc-500 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-white">
                <CalendarDays className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-zinc-400 font-mono border border-zinc-800 px-1.5 py-0.5 rounded">ENGINE 6</span>
            </div>
            <h3 className="font-semibold text-white mt-3 text-sm">Roadmap Optimizer &amp; PERT</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              OR-Tools CP-SAT scheduler, GxP freeze windows, 10,000 PERT runs, and what-if sliders.
            </p>
            <div className="mt-4 flex items-center text-xs text-white font-medium group-hover:translate-x-1 transition-transform">
              <span>Explore Wave Gantt</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            href={`/projects/${id}/evidence`}
            className="p-5 rounded-lg border border-zinc-800 bg-zinc-950 hover:border-zinc-500 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-white">
                <FileCheck2 className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-zinc-400 font-mono border border-zinc-800 px-1.5 py-0.5 rounded">ENGINE 7</span>
            </div>
            <h3 className="font-semibold text-white mt-3 text-sm">Evidence Pack Generator</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Downloadable FDA CSA / EU Annex 11 PDF with characterization tests and traceability.
            </p>
            <div className="mt-4 flex items-center text-xs text-white font-medium group-hover:translate-x-1 transition-transform">
              <span>Download CSA PDF</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>

          <Link
            href="/audit"
            className="p-5 rounded-lg border border-zinc-800 bg-zinc-950 hover:border-zinc-500 transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="p-2 rounded bg-zinc-900 border border-zinc-800 text-white">
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-zinc-400 font-mono border border-zinc-800 px-1.5 py-0.5 rounded">AUDIT TRAIL</span>
            </div>
            <h3 className="font-semibold text-white mt-3 text-sm">SHA-256 Audit Chain</h3>
            <p className="text-xs text-zinc-400 mt-1 leading-relaxed">
              Cryptographic tamper-evident audit ledger verifying every decision and QA approval.
            </p>
            <div className="mt-4 flex items-center text-xs text-white font-medium group-hover:translate-x-1 transition-transform">
              <span>Verify Cryptographic Chain</span>
              <ArrowRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
