"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Layers,
  Database,
  Lock,
  ArrowRight,
  FileSignature,
  FileSpreadsheet,
  X,
  FileText,
} from "lucide-react";
import { fetchGxp, overrideGxp } from "@/lib/api";

export default function GxpHeatmapPage() {
  const params = useParams();
  const id = (params?.id as string) || "acmelims-demo";

  const [gxpData, setGxpData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTierFilter, setSelectedTierFilter] = useState<string>("ALL");

  // Override Modal
  const [overrideModalOpen, setOverrideModalOpen] = useState(false);
  const [targetNode, setTargetNode] = useState<any | null>(null);
  const [newTier, setNewTier] = useState("MEDIUM");
  const [overrideReason, setOverrideReason] = useState("");
  const [savingOverride, setSavingOverride] = useState(false);
  const [overrideSuccessMsg, setOverrideSuccessMsg] = useState("");

  const loadGxp = useCallback(async () => {
    try {
      const data = await fetchGxp(id);
      setGxpData(data);
    } catch (e) {
      console.error("Failed to load GxP scan data:", e);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadGxp();
  }, [loadGxp]);

  async function handleApplyOverride() {
    if (!targetNode || !overrideReason.trim()) return;
    setSavingOverride(true);
    try {
      await overrideGxp(id, targetNode.node_id, newTier, overrideReason);
      setOverrideSuccessMsg(`Override recorded in cryptographic audit log for ${targetNode.node_id}`);
      setOverrideModalOpen(false);
      setOverrideReason("");
      await loadGxp();
      setTimeout(() => setOverrideSuccessMsg(""), 4000);
    } catch (e) {
      alert("Failed to record QA override. Please ensure backend is reachable.");
    } finally {
      setSavingOverride(false);
    }
  }

  const items = gxpData?.classifications || [];
  const filteredItems = items.filter((item: any) =>
    selectedTierFilter === "ALL" ? true : item.tier === selectedTierFilter
  );

  const gaps = gxpData?.gaps || [];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner & Heatmap Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="rounded-xl p-4 border border-zinc-800 bg-black">
          <div className="flex items-center justify-between">
            <span className="text-xs text-white font-mono font-medium">HIGH Criticality</span>
            <ShieldAlert className="w-4 h-4 text-white" />
          </div>
          <div className="text-2xl font-bold text-white mt-1 font-mono">
            {gxpData?.summary?.HIGH ?? 4}
          </div>
          <div className="text-[11px] text-zinc-400 mt-1 font-mono">Direct Batch Release / Part 11</div>
        </div>

        <div className="rounded-xl p-4 border border-zinc-800 bg-black">
          <div className="flex items-center justify-between">
            <span className="text-xs text-zinc-300 font-mono font-medium">MEDIUM Criticality</span>
            <AlertTriangle className="w-4 h-4 text-zinc-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-1 font-mono">
            {gxpData?.summary?.MEDIUM ?? 3}
          </div>
          <div className="text-[11px] text-zinc-400 mt-1 font-mono">Read-only Records / Security IAM</div>
        </div>

        <div className="rounded-xl p-4 border border-zinc-800 bg-black">
          <div className="flex items-center justify-between">
            <span className="text-xs text-zinc-400 font-mono font-medium">LOW Criticality</span>
            <CheckCircle2 className="w-4 h-4 text-zinc-500" />
          </div>
          <div className="text-2xl font-bold text-white mt-1 font-mono">
            {gxpData?.summary?.LOW ?? 3}
          </div>
          <div className="text-[11px] text-zinc-500 mt-1 font-mono">Reporting / Utilities</div>
        </div>

        <div className="rounded-xl p-4 border border-zinc-800 bg-black">
          <div className="flex items-center justify-between">
            <span className="text-xs text-zinc-300 font-mono font-medium">Compliance Gaps</span>
            <FileText className="w-4 h-4 text-white" />
          </div>
          <div className="text-2xl font-bold text-white mt-1 font-mono">{gaps.length || 5}</div>
          <div className="text-[11px] text-zinc-400 mt-1 font-mono">Requires Remediation</div>
        </div>
      </div>

      {overrideSuccessMsg && (
        <div className="p-3 rounded-lg bg-zinc-950 border border-white text-white text-xs flex items-center justify-between font-mono">
          <span>✓ {overrideSuccessMsg}</span>
          <button onClick={() => setOverrideSuccessMsg("")} className="text-zinc-400 hover:text-white">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Compliance Gap Detection Alert Table */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-white" />
            <h2 className="text-sm font-bold text-white">Regulatory Smells &amp; Compliance Gaps</h2>
          </div>
          <span className="text-xs text-zinc-500 font-mono">AUTOMATIC DETECTIONS</span>
        </div>

        <div className="space-y-2">
          {gaps.map((gap: any, idx: number) => (
            <div
              key={idx}
              className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2"
            >
              <div className="flex items-start gap-3">
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-zinc-900 text-white border border-zinc-700">
                  {gap.code || `GAP-0${idx + 1}`}
                </span>
                <div>
                  <h4 className="text-xs font-semibold text-white">{gap.title || gap.name}</h4>
                  <p className="text-[11px] text-zinc-400 mt-0.5">{gap.description || gap.detail}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 self-end sm:self-center">
                <span className="text-[10px] font-mono text-zinc-500">
                  Impact: <span className="text-white font-bold">{gap.severity || "HIGH"}</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* GxP Heatmap Component List with QA Override */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-bold text-white">Component GxP Criticality Heatmap</h2>
            <p className="text-xs text-zinc-400">Deterministic Part 11 / Annex 11 classification with write-path propagation</p>
          </div>

          {/* Tier Filters */}
          <div className="flex gap-1.5">
            {["ALL", "HIGH", "MEDIUM", "LOW"].map((tier) => (
              <button
                key={tier}
                onClick={() => setSelectedTierFilter(tier)}
                className={`px-3 py-1 rounded text-xs font-medium font-mono transition-all ${
                  selectedTierFilter === tier
                    ? "bg-white text-black font-semibold"
                    : "bg-black text-zinc-400 border border-zinc-800 hover:text-white hover:border-zinc-700"
                }`}
              >
                {tier}
              </button>
            ))}
          </div>
        </div>

        {/* Components Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-zinc-950 text-zinc-400 uppercase font-mono text-[10px] border-b border-zinc-800">
              <tr>
                <th className="py-2.5 px-3">Component / Class</th>
                <th className="py-2.5 px-3">GxP Criticality Tier</th>
                <th className="py-2.5 px-3">Regulatory Dimensions</th>
                <th className="py-2.5 px-3">Propagation &amp; Evidence</th>
                <th className="py-2.5 px-3 text-right">Human QA Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {filteredItems.map((item: any) => (
                <tr key={item.node_id} className="hover:bg-zinc-900/40 transition-colors">
                  <td className="py-3 px-3">
                    <span className="font-semibold text-white block">
                      {item.node_id.split(".").pop()}
                    </span>
                    <span className="font-mono text-[10px] text-zinc-500">{item.node_id}</span>
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                        item.tier === "HIGH"
                          ? "bg-white text-black"
                          : item.tier === "MEDIUM"
                          ? "border border-zinc-600 bg-zinc-900 text-zinc-300"
                          : "border border-zinc-800 bg-black text-zinc-400"
                      }`}
                    >
                      {item.tier}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex flex-wrap gap-1">
                      {(item.tags || []).map((tag: string) => (
                        <span
                          key={tag}
                          className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-zinc-900 text-zinc-300 border border-zinc-800"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="py-3 px-3 text-zinc-400 text-[11px] max-w-xs">
                    {item.rationale || "Propagated via write-path to regulated schema table"}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <button
                      onClick={() => {
                        setTargetNode(item);
                        setNewTier(item.tier === "HIGH" ? "MEDIUM" : "HIGH");
                        setOverrideModalOpen(true);
                      }}
                      className="px-2.5 py-1 rounded bg-black hover:bg-zinc-900 text-zinc-300 hover:text-white border border-zinc-750 text-[11px] font-medium transition-all"
                    >
                      Override Tier
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* QA Override Modal */}
      {overrideModalOpen && targetNode && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
          role="dialog"
          aria-modal="true"
          aria-labelledby="gxp-override-title"
        >
          <div className="bg-black border border-zinc-700 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
              <div className="flex items-center gap-2">
                <FileSignature className="w-4 h-4 text-white" aria-hidden="true" />
                <h3 id="gxp-override-title" className="font-bold text-white text-base">
                  Regulatory QA Tier Override
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setOverrideModalOpen(false)}
                className="text-zinc-400 hover:text-white p-1 rounded focus-visible:ring-2 focus-visible:ring-white"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-zinc-400">Target Component:</span>
                <div className="font-mono text-white text-xs mt-1 p-2 bg-zinc-950 rounded border border-zinc-800 break-all">
                  {targetNode.node_id}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <span className="text-zinc-400 block mb-1">Current Detected Tier:</span>
                  <div className="font-bold text-white mt-1 font-mono p-1.5 bg-zinc-950 rounded border border-zinc-800">
                    {targetNode.tier}
                  </div>
                </div>
                <div>
                  <label htmlFor="new-qa-tier-select" className="text-zinc-400 block mb-1">
                    New QA Tier:
                  </label>
                  <select
                    id="new-qa-tier-select"
                    value={newTier}
                    onChange={(e) => setNewTier(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 text-white p-2 rounded font-medium focus:outline-none focus:border-white focus-visible:ring-2 focus-visible:ring-white font-mono"
                  >
                    <option value="HIGH">HIGH (Part 11 Core)</option>
                    <option value="MEDIUM">MEDIUM (CSA Exploratory)</option>
                    <option value="LOW">LOW (Peripheral / Utility)</option>
                  </select>
                </div>
              </div>

              <div>
                <label htmlFor="override-reason-textarea" className="text-zinc-400 block mb-1">
                  Mandatory QA Regulatory Justification:
                </label>
                <textarea
                  id="override-reason-textarea"
                  rows={3}
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  placeholder="State the formal CSV/CSA rationale for re-tiering (e.g., component is isolated by read-only API facade with zero batch release impact)..."
                  className="w-full bg-zinc-950 border border-zinc-800 text-white p-2.5 rounded text-xs focus:outline-none focus:border-white focus-visible:ring-2 focus-visible:ring-white placeholder:text-zinc-600"
                />
              </div>

              <div className="p-2.5 rounded bg-zinc-950 border border-zinc-800 text-zinc-400 text-[11px] leading-relaxed font-mono">
                Notice: All manual overrides are cryptographically timestamped and committed to the
                tamper-evident SHA-256 audit ledger with your user identity.
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => setOverrideModalOpen(false)}
                className="px-3.5 py-2 min-h-[38px] rounded bg-black hover:bg-zinc-900 border border-zinc-800 text-zinc-300 text-xs focus-visible:ring-2 focus-visible:ring-white"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleApplyOverride}
                disabled={savingOverride || !overrideReason.trim()}
                className="px-4 py-2 min-h-[38px] rounded bg-white hover:bg-zinc-200 text-black font-bold text-xs disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-white"
              >
                {savingOverride ? "Recording..." : "Authorize & Sign Override"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
