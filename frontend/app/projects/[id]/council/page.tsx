"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import {
  Users2,
  Cloud,
  ShieldAlert,
  Lock,
  DollarSign,
  Scale,
  CheckCircle2,
  XCircle,
  MessageSquare,
  AlertTriangle,
  Play,
  ArrowRight,
  Clock,
  X,
} from "lucide-react";
import { runCouncil, fetchCouncilDecisions, approveDecision, rejectDecision } from "@/lib/api";

const AGENT_ICONS: Record<string, any> = {
  "Cloud Architect": Cloud,
  "Validation & QA Lead": ShieldAlert,
  "Security Officer": Lock,
  "FinOps Analyst": DollarSign,
  "Regulatory Affairs": Scale,
  "Moderator (Chair)": Users2,
};

const AGENT_COLORS: Record<string, string> = {
  "Cloud Architect": "text-white bg-zinc-900 border-zinc-700",
  "Validation & QA Lead": "text-white bg-zinc-900 border-zinc-700",
  "Security Officer": "text-white bg-zinc-900 border-zinc-700",
  "FinOps Analyst": "text-white bg-zinc-900 border-zinc-700",
  "Regulatory Affairs": "text-white bg-zinc-900 border-zinc-700",
  "Moderator (Chair)": "text-white bg-zinc-900 border-zinc-700",
};

export default function CouncilPage() {
  const params = useParams();
  const id = (params?.id as string) || "acmelims-demo";

  const [debates, setDebates] = useState<any[]>([]);
  const [decisions, setDecisions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningCouncil, setRunningCouncil] = useState(false);
  const [selectedClusterIdx, setSelectedClusterIdx] = useState<number>(0);

  // Approval / Rejection Dialog State
  const [actionModalOpen, setActionModalOpen] = useState(false);
  const [modalAction, setModalAction] = useState<"APPROVE" | "REJECT">("APPROVE");
  const [targetDecision, setTargetDecision] = useState<any | null>(null);
  const [actionComment, setActionComment] = useState("");
  const [actionLoading, setActionLoading] = useState(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState("");

  const loadCouncilData = useCallback(async () => {
    try {
      const resDec = await fetchCouncilDecisions(id);
      if (resDec && resDec.decisions) {
        setDecisions(resDec.decisions);
      }
    } catch (e) {
      console.error("Failed to load council decisions:", e);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadCouncilData();
  }, [loadCouncilData]);

  async function handleRunCouncil() {
    setRunningCouncil(true);
    try {
      const res = await runCouncil(id);
      if (res && res.debates) {
        setDebates(res.debates);
      }
      await loadCouncilData();
    } catch (e) {
      alert("Failed to run Council debate. Ensure backend is running.");
    } finally {
      setRunningCouncil(false);
    }
  }

  async function handleConfirmAction() {
    if (!targetDecision) return;
    setActionLoading(true);
    try {
      if (modalAction === "APPROVE") {
        await approveDecision(targetDecision.id, actionComment || "Approved by QA Lead");
        setActionSuccessMsg(`Decision for ${targetDecision.cluster_id} approved.`);
      } else {
        if (!actionComment.trim()) {
          alert("Rejection requires a mandatory explanation.");
          setActionLoading(false);
          return;
        }
        await rejectDecision(targetDecision.id, actionComment);
        setActionSuccessMsg(`Decision for ${targetDecision.cluster_id} rejected.`);
      }
      setActionModalOpen(false);
      setActionComment("");
      await loadCouncilData();
      setTimeout(() => setActionSuccessMsg(""), 4000);
    } catch (e) {
      alert("Failed to process approval action.");
    } finally {
      setActionLoading(false);
    }
  }

  const activeDebate = debates.length > 0 ? debates[selectedClusterIdx] : null;
  const currentDecision =
    decisions.length > 0 ? decisions[selectedClusterIdx] || decisions[0] : null;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner & Control */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-800 text-xs font-mono">
            <Users2 className="w-3.5 h-3.5 text-white" />
            <span>Architecture Governance Council</span>
          </div>
          <h1 className="text-xl font-extrabold text-white mt-1">
            Specialist Deliberation, Rebuttal &amp; Human QA Gate
          </h1>
          <p className="text-xs text-zinc-400">
            Cloud Architect, Validation Lead, Security Officer, FinOps, and Regulatory Director debate modernization strategies.
          </p>
        </div>

        <button
          onClick={handleRunCouncil}
          disabled={runningCouncil}
          className="flex items-center gap-2 px-4 py-2.5 rounded bg-white hover:bg-zinc-200 text-black font-semibold text-xs disabled:opacity-50 transition-all self-start md:self-auto font-mono"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>{runningCouncil ? "Council In Session..." : "Run AI Council Debate"}</span>
        </button>
      </div>

      {actionSuccessMsg && (
        <div className="p-3 rounded-lg bg-zinc-950 border border-white text-white text-xs flex items-center justify-between font-mono">
          <span>✓ {actionSuccessMsg}</span>
          <button onClick={() => setActionSuccessMsg("")} className="text-zinc-400 hover:text-white">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Cluster Decision Switcher */}
      {decisions.length > 0 && (
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none font-mono text-xs">
          {decisions.map((dec, idx) => (
            <button
              key={dec.id}
              onClick={() => setSelectedClusterIdx(idx)}
              className={`px-3 py-2 rounded text-xs font-medium whitespace-nowrap transition-all border ${
                selectedClusterIdx === idx
                  ? "bg-white border-white text-black font-semibold"
                  : "bg-black border-zinc-800 text-zinc-400 hover:text-white hover:border-zinc-700"
              }`}
            >
              <span>{dec.cluster_id.replace("modernrx_", "").replace("_", " ").toUpperCase()}</span>
              <span className="ml-2 font-mono text-[10px] opacity-80">[{dec.status}]</span>
            </button>
          ))}
        </div>
      )}

      {/* Main Grid: Live Multi-Agent Debate on Left, Synthesized Decision & QA Gate on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Debate Transcript */}
        <div className="lg:col-span-2 rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-white" />
              <h2 className="text-sm font-bold text-white">Deliberation Transcript</h2>
            </div>
            <span className="text-[11px] font-mono text-zinc-500">5 SPECIALISTS + 1 MODERATOR</span>
          </div>

          {activeDebate ? (
            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
              {/* Specialist Opinions */}
              <div className="space-y-3">
                <span className="text-[10px] font-mono text-zinc-500 uppercase font-bold block">
                  ROUND 1 — SPECIALIST OPENING OPINIONS
                </span>
                {activeDebate.opinions.map((op: any, i: number) => {
                  const Icon = AGENT_ICONS[op.agent] || MessageSquare;
                  const colorClass = AGENT_COLORS[op.agent] || "text-zinc-300 bg-zinc-900 border-zinc-700";

                  return (
                    <div key={i} className="p-3.5 rounded-xl bg-zinc-950 border border-zinc-800 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className={`p-1.5 rounded-lg border ${colorClass}`}>
                            <Icon className="w-3.5 h-3.5" />
                          </div>
                          <span className="font-bold text-xs text-white">{op.agent}</span>
                        </div>
                        <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-zinc-900 text-white border border-zinc-700">
                          {op.strategy}
                        </span>
                      </div>

                      <p className="text-xs text-zinc-300 leading-relaxed pl-7">{op.rationale}</p>

                      <div className="flex items-center gap-4 text-[10px] text-zinc-500 font-mono pl-7 pt-1">
                        <span>Effort: {op.effort_weeks?.[1] || 3} wks</span>
                        <span>
                          Target: {(op.target_pattern || []).join(", ") || "Containerized"}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Rebuttal Round */}
              {activeDebate.rebuttals && activeDebate.rebuttals.length > 0 && (
                <div className="space-y-3 pt-2">
                  <span className="text-[10px] font-mono text-zinc-400 uppercase font-bold block">
                    ROUND 2 — MODERATOR-CHAIRED REBUTTAL &amp; COUNTER-PROPOSALS
                  </span>
                  {activeDebate.rebuttals.map((reb: any, i: number) => (
                    <div
                      key={i}
                      className="p-3 rounded-xl bg-zinc-950 border border-zinc-800 space-y-1.5"
                    >
                      <div className="flex items-center justify-between text-[11px] font-mono">
                        <span className="font-semibold text-white">
                          {reb.from} ➔ {reb.to}
                        </span>
                        <span className="text-[10px] text-zinc-500">REBUTTAL</span>
                      </div>
                      <p className="text-xs text-zinc-300 italic leading-relaxed">{reb.text}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-16 space-y-3">
              <Users2 className="w-10 h-10 text-zinc-600 mx-auto" />
              <p className="text-xs text-zinc-400">
                Click &quot;Run AI Council Debate&quot; to convene the 5 specialist agents and view their deliberations.
              </p>
            </div>
          )}
        </div>

        {/* Right Column: Synthesized Council Decision & QA Approval Gate */}
        <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
            <span className="text-xs font-bold text-white uppercase font-mono">
              Consensus Recommendation
            </span>
            {currentDecision && (
              <span
                className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                  currentDecision.status === "APPROVED"
                    ? "bg-white text-black"
                    : currentDecision.status === "REJECTED"
                    ? "border border-zinc-600 bg-zinc-900 text-zinc-300"
                    : "border border-zinc-800 bg-black text-zinc-400"
                }`}
              >
                {currentDecision.status}
              </span>
            )}
          </div>

          {currentDecision ? (
            <div className="space-y-4 text-xs">
              <div>
                <span className="text-[10px] text-zinc-400 uppercase font-mono">Recommended 7R Strategy</span>
                <div className="text-2xl font-black text-white mt-0.5 font-mono">
                  {currentDecision.strategy}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 font-mono">
                <div className="bg-zinc-950 p-2.5 rounded-lg border border-zinc-800">
                  <span className="text-zinc-500 text-[10px] block uppercase">Confidence</span>
                  <span className="font-bold text-white text-sm">
                    {Math.round((currentDecision.confidence || 0.88) * 100)}%
                  </span>
                </div>
                <div className="bg-zinc-950 p-2.5 rounded-lg border border-zinc-800">
                  <span className="text-zinc-500 text-[10px] block uppercase">Likely Effort</span>
                  <span className="font-bold text-white text-sm">
                    {currentDecision.effort_weeks?.[1] || 4} wks
                  </span>
                </div>
              </div>

              <div>
                <span className="text-[10px] text-zinc-400 uppercase font-mono">Target Patterns</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {(currentDecision.target_pattern || ["StranglerFig", "Containerized"]).map(
                    (p: string) => (
                      <span
                        key={p}
                        className="px-2 py-0.5 rounded bg-zinc-900 text-zinc-200 border border-zinc-700 text-[10px] font-mono font-semibold"
                      >
                        {p}
                      </span>
                    )
                  )}
                </div>
              </div>

              <div>
                <span className="text-[10px] text-zinc-400 uppercase font-mono">Target Cloud Services</span>
                <div className="text-[11px] text-zinc-300 font-mono bg-zinc-950 p-2 rounded-lg border border-zinc-800 mt-1">
                  {(currentDecision.target_services || ["AWS ECS", "Amazon RDS"]).join(", ")}
                </div>
              </div>

              <div>
                <span className="text-[10px] text-zinc-400 uppercase font-mono">Consensus Rationale</span>
                <p className="text-[11px] text-zinc-300 mt-1 bg-zinc-950 p-2.5 rounded-lg border border-zinc-800 leading-relaxed">
                  {currentDecision.rationale}
                </p>
              </div>

              {/* Recorded Dissent */}
              {currentDecision.dissent && currentDecision.dissent.length > 0 && (
                <div>
                  <span className="text-[10px] text-zinc-400 uppercase font-mono font-bold block mb-1">
                    Recorded Specialist Dissent
                  </span>
                  <div className="space-y-1.5">
                    {currentDecision.dissent.map((d: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-2 rounded bg-zinc-950 border border-zinc-800 text-[11px]"
                      >
                        <span className="font-bold text-white font-mono">{d.agent}:</span>{" "}
                        <span className="text-zinc-300">{d.reason}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Human QA Approval Gate Buttons */}
              <div className="pt-2 border-t border-zinc-800 space-y-2">
                <span className="text-[10px] text-zinc-400 uppercase font-mono block">
                  Mandatory Human QA Approval Gate
                </span>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => {
                      setTargetDecision(currentDecision);
                      setModalAction("APPROVE");
                      setActionModalOpen(true);
                    }}
                    className="flex items-center justify-center gap-1.5 px-3 py-2 rounded bg-white hover:bg-zinc-200 text-black font-bold text-xs transition-all"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Approve Strategy</span>
                  </button>

                  <button
                    onClick={() => {
                      setTargetDecision(currentDecision);
                      setModalAction("REJECT");
                      setActionModalOpen(true);
                    }}
                    className="flex items-center justify-center gap-1.5 px-3 py-2 rounded bg-black hover:bg-zinc-900 border border-zinc-700 text-zinc-300 hover:text-white font-medium text-xs transition-all"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Reject Strategy</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-zinc-500 text-xs">
              No decisions loaded. Run Council to generate strategies.
            </div>
          )}
        </div>
      </div>

      {/* Approve / Reject Dialog Modal */}
      {actionModalOpen && targetDecision && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
          role="dialog"
          aria-modal="true"
          aria-labelledby="council-action-title"
        >
          <div className="bg-black border border-zinc-800 rounded-xl max-w-md w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
              <h3 id="council-action-title" className="font-bold text-white text-sm">
                {modalAction === "APPROVE" ? "Authorize Council Decision" : "Reject Council Decision"}
              </h3>
              <button
                type="button"
                onClick={() => setActionModalOpen(false)}
                className="text-zinc-400 hover:text-white p-1 rounded focus-visible:ring-2 focus-visible:ring-white"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="bg-zinc-950 p-2.5 rounded border border-zinc-800 space-y-1 font-mono text-[11px]">
                <div>
                  <span className="text-zinc-500">Cluster:</span>
                  <span className="font-bold text-white ml-2">{targetDecision.cluster_id}</span>
                </div>
                <div>
                  <span className="text-zinc-500">Proposed Strategy:</span>
                  <span className="font-bold text-white ml-2">{targetDecision.strategy}</span>
                </div>
              </div>

              <div>
                <label htmlFor="council-action-notes" className="text-zinc-400 block mb-1">
                  {modalAction === "APPROVE"
                    ? "QA Approval Endorsement / Review Notes:"
                    : "Mandatory Rejection Explanation:"}
                </label>
                <textarea
                  id="council-action-notes"
                  rows={3}
                  value={actionComment}
                  onChange={(e) => setActionComment(e.target.value)}
                  placeholder={
                    modalAction === "APPROVE"
                      ? "Approved following CSA risk categorization and characterization harness review..."
                      : "State why this strategy fails compliance or architectural standards..."
                  }
                  className="w-full bg-zinc-950 border border-zinc-800 text-white p-2.5 rounded text-xs focus:outline-none focus:border-white focus-visible:ring-2 focus-visible:ring-white placeholder:text-zinc-600"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => setActionModalOpen(false)}
                className="px-3.5 py-2 min-h-[36px] rounded bg-black hover:bg-zinc-900 border border-zinc-800 text-zinc-300 text-xs focus-visible:ring-2 focus-visible:ring-white"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmAction}
                disabled={actionLoading}
                className={`px-4 py-2 min-h-[36px] rounded font-bold text-xs focus-visible:ring-2 focus-visible:ring-white ${
                  modalAction === "APPROVE"
                    ? "bg-white hover:bg-zinc-200 text-black"
                    : "bg-zinc-900 hover:bg-zinc-800 text-white border border-zinc-700"
                }`}
              >
                {actionLoading ? "Processing..." : `Confirm ${modalAction}`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
