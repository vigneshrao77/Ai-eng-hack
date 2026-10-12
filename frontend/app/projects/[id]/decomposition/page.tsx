"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import {
  Split,
  TrendingDown,
  Layers,
  ShieldAlert,
  ArrowRight,
  Sliders,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { fetchDecomposition, runDecomposition } from "@/lib/api";

export default function DecompositionPage() {
  const params = useParams();
  const id = (params?.id as string) || "acmelims-demo";

  const [decompData, setDecompData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeVariant, setActiveVariant] = useState<"modernrx" | "hdbscan" | "louvain">("modernrx");
  const [recomputing, setRecomputing] = useState(false);

  const loadDecomp = useCallback(async () => {
    try {
      const data = await fetchDecomposition(id);
      setDecompData(data);
    } catch (e) {
      console.error("Failed to load decomposition data:", e);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadDecomp();
  }, [loadDecomp]);

  async function handleRecompute() {
    setRecomputing(true);
    try {
      const data = await runDecomposition(id);
      setDecompData(data);
    } catch (e) {
      alert("Failed to run decomposition algorithm.");
    } finally {
      setRecomputing(false);
    }
  }

  const headline = decompData?.headline_comparison || {
    reval_scope_naive_pct: 78.5,
    reval_scope_modernrx_pct: 44.0,
    reval_scope_reduction_pct: 34.5,
    blast_radius_naive: 14,
    blast_radius_modernrx: 7,
    modularity_modernrx: 0.62,
  };

  const variants = decompData?.variants || {};
  const currentVariantData = variants[activeVariant] || {
    name: "ModernRx Constrained",
    metrics: {
      modularity: 0.62,
      blast_radius: 7,
      reval_scope_pct: 44.0,
      services_count: 5,
      inter_cluster_call_ratio: 0.18,
    },
  };

  const clusters = decompData?.clusters || [];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Headline RevalScope Comparison Hero Cards */}
      <div className="rounded-xl p-6 border border-zinc-800 bg-black space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-800 text-xs font-mono">
              <Layers className="w-3.5 h-3.5 text-white" />
              <span>GxP-Constrained Graph Partitioning</span>
            </div>
            <h1 className="text-xl font-extrabold text-white mt-1">
              Re-validation Scope (RevalScope™) Comparison
            </h1>
            <p className="text-xs text-zinc-400">
              ModernRx enforces must-link constraints on regulated write-paths and cannot-link penalties on peripheral utilities.
            </p>
          </div>

          <button
            onClick={handleRecompute}
            disabled={recomputing}
            className="flex items-center gap-2 px-3.5 py-2 rounded bg-white hover:bg-zinc-200 text-black font-semibold text-xs disabled:opacity-50 transition-all self-start md:self-auto"
          >
            <Sliders className="w-3.5 h-3.5" />
            <span>{recomputing ? "Recomputing..." : "Recompute Partition"}</span>
          </button>
        </div>

        {/* 3 Metric Comparison Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          {/* Card 1: RevalScope */}
          <div className="bg-zinc-950 p-4 rounded-xl border border-zinc-800">
            <span className="text-[11px] text-zinc-400 font-mono uppercase block">
              RevalScope™ Reduction
            </span>
            <div className="flex items-baseline gap-2 mt-2 font-mono">
              <span className="text-3xl font-black text-white">
                {headline.reval_scope_modernrx_pct}%
              </span>
              <span className="text-xs text-zinc-500 line-through">
                {headline.reval_scope_naive_pct}% naive
              </span>
            </div>
            <div className="text-xs text-zinc-300 font-mono flex items-center gap-1 mt-1">
              <TrendingDown className="w-4 h-4 text-white" />
              <span>-{headline.reval_scope_reduction_pct}% fewer components to re-validate</span>
            </div>
          </div>

          {/* Card 2: Blast Radius */}
          <div className="bg-zinc-950 p-4 rounded-xl border border-zinc-800">
            <span className="text-[11px] text-zinc-400 font-mono uppercase block">
              Validation Blast Radius
            </span>
            <div className="flex items-baseline gap-2 mt-2 font-mono">
              <span className="text-3xl font-black text-white">
                {headline.blast_radius_modernrx}
              </span>
              <span className="text-xs text-zinc-500">
                vs {headline.blast_radius_naive} naive hops
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Constrained core isolates Part 11 side-effects
            </p>
          </div>

          {/* Card 3: Modularity */}
          <div className="bg-zinc-950 p-4 rounded-xl border border-zinc-800">
            <span className="text-[11px] text-zinc-400 font-mono uppercase block">
              Newman Modularity (Q)
            </span>
            <div className="flex items-baseline gap-2 mt-2 font-mono">
              <span className="text-3xl font-black text-white">
                {headline.modularity_modernrx}
              </span>
              <span className="text-xs text-zinc-500">/ 1.0 (Optimal Cohesion)</span>
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Low inter-cluster coupling across microservice boundaries
            </p>
          </div>
        </div>
      </div>

      {/* 3-Way Partition Switcher Tabs */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-zinc-800">
          <div>
            <h2 className="text-sm font-bold text-white">Algorithm Benchmark Comparison</h2>
            <p className="text-xs text-zinc-400">
              Evaluating clustering variants on the same AcmeLIMS dependency similarity matrix
            </p>
          </div>

          <div className="flex p-1 rounded-lg bg-zinc-950 border border-zinc-800 gap-1 self-start sm:self-auto font-mono text-xs">
            <button
              onClick={() => setActiveVariant("modernrx")}
              className={`px-3 py-1.5 rounded transition-all ${
                activeVariant === "modernrx"
                  ? "bg-white text-black font-semibold"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              ModernRx Constrained
            </button>
            <button
              onClick={() => setActiveVariant("hdbscan")}
              className={`px-3 py-1.5 rounded transition-all ${
                activeVariant === "hdbscan"
                  ? "bg-white text-black font-semibold"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              Plain HDBSCAN
            </button>
            <button
              onClick={() => setActiveVariant("louvain")}
              className={`px-3 py-1.5 rounded transition-all ${
                activeVariant === "louvain"
                  ? "bg-white text-black font-semibold"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              Baseline (Louvain)
            </button>
          </div>
        </div>

        {/* Selected Variant Metrics Banner */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 p-3.5 rounded-xl bg-zinc-950 border border-zinc-800 text-xs font-mono">
          <div>
            <span className="text-zinc-500 block text-[10px] uppercase">Variant Name</span>
            <span className="font-bold text-white">{currentVariantData.name}</span>
          </div>
          <div>
            <span className="text-zinc-500 block text-[10px] uppercase">RevalScope</span>
            <span className="font-bold text-white">
              {currentVariantData.metrics?.reval_scope_pct}%
            </span>
          </div>
          <div>
            <span className="text-zinc-500 block text-[10px] uppercase">Blast Radius</span>
            <span className="font-bold text-white">
              {currentVariantData.metrics?.blast_radius}
            </span>
          </div>
          <div>
            <span className="text-zinc-500 block text-[10px] uppercase">Services Produced</span>
            <span className="font-bold text-white">
              {currentVariantData.metrics?.services_count}
            </span>
          </div>
          <div>
            <span className="text-zinc-500 block text-[10px] uppercase">Modularity Q</span>
            <span className="font-bold text-white">
              {currentVariantData.metrics?.modularity}
            </span>
          </div>
        </div>

        {/* Clusters Breakdown Table */}
        <div className="space-y-3 pt-2">
          <h3 className="text-xs font-bold text-white uppercase font-mono">
            Derived Microservice Clusters ({clusters.length})
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {clusters.map((c: any) => (
              <div
                key={c.cluster_id}
                className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-xs text-white">{c.name}</span>
                    <span className="text-[10px] font-mono text-zinc-500">({c.cluster_id})</span>
                  </div>
                  <span
                    className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                      c.gxp_max_tier === "HIGH"
                        ? "bg-white text-black"
                        : c.gxp_max_tier === "MEDIUM"
                        ? "border border-zinc-600 bg-zinc-900 text-zinc-300"
                        : "border border-zinc-800 bg-black text-zinc-400"
                    }`}
                  >
                    {c.gxp_max_tier}
                  </span>
                </div>

                <div className="flex items-center justify-between text-[11px] text-zinc-400 font-mono">
                  <span>Components: {c.components_count}</span>
                  <span>Readiness: {c.readiness_avg}/100</span>
                </div>

                <div className="flex flex-wrap gap-1 pt-1">
                  {(c.components || []).map((comp: string) => (
                    <span
                      key={comp}
                      className="font-mono text-[10px] px-2 py-0.5 rounded bg-black text-zinc-300 border border-zinc-800"
                    >
                      {comp.split(".").pop()}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
