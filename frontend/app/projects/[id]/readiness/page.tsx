"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import {
  Gauge,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Zap,
  Trash2,
  FileCode,
  ArrowRight,
  TrendingUp,
} from "lucide-react";
import { fetchReadiness } from "@/lib/api";

export default function ReadinessPage() {
  const params = useParams();
  const id = (params?.id as string) || "acmelims-demo";

  const [readinessData, setReadinessData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedComp, setSelectedComp] = useState<any | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchReadiness(id);
        setReadinessData(data);
        if (data?.components && data.components.length > 0) {
          setSelectedComp(data.components[0]);
        }
      } catch (e) {
        console.error("Failed to load readiness data:", e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [id]);

  const components = readinessData?.components || [];
  const deadCode = readinessData?.dead_code_candidates || readinessData?.dead_code || [];
  const quickWins = readinessData?.quick_win_candidates || readinessData?.quick_wins || [];
  const avgScore = readinessData?.average_readiness_score ?? readinessData?.average_readiness ?? 68.4;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Gauge className="w-5 h-5 text-white" />
            <h1 className="text-lg font-bold text-white">Cloud Readiness Assessment Engine</h1>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Explainable 0–100 score computed via 11 deterministic checks with traceable deductions
          </p>
        </div>

        <div className="flex items-center gap-6 bg-zinc-950 px-4 py-3 rounded-xl border border-zinc-800">
          <div>
            <span className="text-[10px] text-zinc-400 uppercase font-mono block">Average Score</span>
            <span className="text-2xl font-black text-white font-mono">
              {avgScore}/100
            </span>
          </div>
          <div className="h-8 w-px bg-zinc-800" />
          <div>
            <span className="text-[10px] text-zinc-400 uppercase font-mono block">Components Evaluated</span>
            <span className="text-2xl font-black text-white font-mono">{components.length || 10}</span>
          </div>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Components Score List */}
        <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-3">
          <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
            <span className="text-xs font-bold text-white uppercase font-mono">Component Scores</span>
            <span className="text-[11px] text-zinc-500 font-mono">0..100 Index</span>
          </div>

          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {components.map((comp: any, idx: number) => {
              const compId = comp.id || comp.node_id || `comp-${idx}`;
              const selectedId = selectedComp?.id || selectedComp?.node_id;
              const isSelected = selectedId === compId;
              const score = comp.score ?? 75;
              const displayName =
                comp.name ||
                comp.class_name ||
                (typeof compId === "string" ? compId.split(".").pop() : "") ||
                `Component ${idx + 1}`;

              return (
                <div
                  key={compId}
                  onClick={() => setSelectedComp(comp)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    isSelected
                      ? "border-white bg-zinc-900 ring-1 ring-white"
                      : "border-zinc-800 bg-zinc-950 hover:border-zinc-600"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-xs text-white truncate max-w-[170px]">
                      {displayName}
                    </span>
                    <span className="font-mono font-bold text-xs text-white">{score}/100</span>
                  </div>

                  <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden mt-2">
                    <div className="h-full bg-white" style={{ width: `${score}%` }} />
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-zinc-400 font-mono mt-2">
                    <span>GxP: {comp.gxp_tier || "LOW"}</span>
                    <span>{comp.deductions?.length || 0} Deductions</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Deductions Breakdown Panel */}
        <div className="lg:col-span-2 rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
            <div>
              <span className="text-xs font-bold text-white uppercase font-mono">
                Deduction Audit Trail &amp; Evidence
              </span>
              <p className="text-[11px] text-zinc-400">
                Target: <span className="text-white font-mono">{selectedComp?.id || selectedComp?.node_id || selectedComp?.name || "None"}</span>
              </p>
            </div>
            {selectedComp && (
              <span className="text-xs px-2.5 py-1 rounded bg-zinc-900 text-white border border-zinc-700 font-bold font-mono">
                Score: {selectedComp.score}/100
              </span>
            )}
          </div>

          {selectedComp ? (
            <div className="space-y-3">
              {(!selectedComp.deductions || selectedComp.deductions.length === 0) ? (
                <div className="p-8 text-center text-zinc-500 text-xs">
                  Zero architectural deductions. This component is cloud-ready.
                </div>
              ) : (
                selectedComp.deductions.map((ded: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 flex flex-col gap-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-white flex-shrink-0" />
                        <span className="font-semibold text-xs text-white">{ded.check_name}</span>
                      </div>
                      <span className="font-mono text-xs font-bold text-white bg-zinc-900 px-2 py-0.5 rounded border border-zinc-700">
                        -{ded.points_deducted} pts
                      </span>
                    </div>

                    <p className="text-xs text-zinc-300 leading-relaxed pl-6">{ded.reason}</p>

                    {ded.evidence_node_ids && ded.evidence_node_ids.length > 0 && (
                      <div className="pl-6 pt-1 flex items-center gap-1.5 flex-wrap">
                        <span className="text-[10px] text-zinc-500 uppercase font-mono">
                          Evidence Nodes:
                        </span>
                        {ded.evidence_node_ids.map((nid: string, i: number) => (
                          <span
                            key={i}
                            className="font-mono text-[10px] px-2 py-0.5 rounded bg-black text-zinc-300 border border-zinc-800"
                          >
                            {typeof nid === "string" ? nid.split(".").pop() : String(nid)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          ) : (
            <div className="text-center py-12 text-zinc-500 text-xs">
              Select a component to inspect deductions.
            </div>
          )}
        </div>
      </div>

      {/* Dead Code & Quick Win Opportunities Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Dead Code Candidates */}
        <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
            <div className="flex items-center gap-2 text-white">
              <Trash2 className="w-4 h-4" />
              <h3 className="text-xs font-bold text-white uppercase font-mono">
                Dead Code Candidates (Retire)
              </h3>
            </div>
            <span className="text-[10px] text-zinc-500 font-mono">FAN-IN = 0</span>
          </div>

          <div className="space-y-2">
            {deadCode.length === 0 ? (
              <p className="text-xs text-zinc-500 py-4 text-center">No uncalled dead code detected.</p>
            ) : (
              deadCode.map((dc: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-center justify-between text-xs"
                >
                  <div>
                    <span className="font-semibold text-white block">
                      {dc.name || dc.class_name || dc.node_id || dc.id || "Dead Code Candidate"}
                    </span>
                    <span className="text-[10px] text-zinc-500 font-mono">
                      {dc.reason || "Zero caller fan-in; candidate for immediate retirement"}
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-white text-black font-mono text-[10px] font-bold">
                    RETIRE
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Quick Win Rehost Candidates */}
        <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
            <div className="flex items-center gap-2 text-white">
              <Zap className="w-4 h-4" />
              <h3 className="text-xs font-bold text-white uppercase font-mono">
                Quick-Win Rehost Candidates
              </h3>
            </div>
            <span className="text-[10px] text-zinc-500 font-mono">LOW GXP / ISOLATED</span>
          </div>

          <div className="space-y-2">
            {quickWins.length === 0 ? (
              <p className="text-xs text-zinc-500 py-4 text-center">No peripheral quick wins found.</p>
            ) : (
              quickWins.map((qw: any, idx: number) => (
                <div
                  key={idx}
                  className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex items-center justify-between text-xs"
                >
                  <div>
                    <span className="font-semibold text-white block">
                      {qw.name || qw.class_name || qw.node_id || qw.id || "Quick-Win Candidate"}
                    </span>
                    <span className="text-[10px] text-zinc-500 font-mono">
                      {qw.reason || "Read-only reporting service with zero batch release impact"}
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded border border-zinc-700 bg-zinc-900 text-zinc-300 font-mono text-[10px] font-bold">
                    REHOST (WAVE 1)
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
