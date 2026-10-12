"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import {
  FileCheck2,
  Download,
  FileText,
  Shield,
  Layers,
  CheckCircle2,
  Clock,
  ArrowRight,
  Plus,
  RefreshCw,
} from "lucide-react";
import { fetchEvidencePacks, generateEvidencePack, getEvidenceDownloadUrl } from "@/lib/api";

export default function EvidencePacksPage() {
  const params = useParams();
  const id = (params?.id as string) || "acmelims-demo";

  const [packs, setPacks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [generatingWave, setGeneratingWave] = useState<number | null>(null);
  const [selectedWaveToGen, setSelectedWaveToGen] = useState<number>(1);

  const loadPacks = useCallback(async () => {
    try {
      const data = await fetchEvidencePacks(id);
      if (data && data.evidence_packs) {
        setPacks(data.evidence_packs);
      }
    } catch (e) {
      console.error("Failed to load evidence packs:", e);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadPacks();
  }, [loadPacks]);

  async function handleGeneratePack(waveNum: number) {
    setGeneratingWave(waveNum);
    try {
      await generateEvidencePack(id, waveNum);
      await loadPacks();
    } catch (e) {
      alert("Failed to generate Evidence Pack PDF.");
    } finally {
      setGeneratingWave(null);
    }
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-800 text-xs font-mono">
            <FileText className="w-3.5 h-3.5 text-white" />
            <span>FDA CSA &amp; EU Annex 11 Dossier Engine</span>
          </div>
          <h1 className="text-xl font-extrabold text-white mt-1">
            Computer Software Assurance (CSA) Evidence Packs
          </h1>
          <p className="text-xs text-zinc-400">
            Auto-compiles audit-ready assurance dossiers with characterization test harnesses, differential verification, and traceability matrices.
          </p>
        </div>

        {/* Generate Pack Action */}
        <div className="flex items-center gap-2 self-start md:self-auto font-mono">
          <select
            value={selectedWaveToGen}
            onChange={(e) => setSelectedWaveToGen(parseInt(e.target.value))}
            className="bg-zinc-950 border border-zinc-800 text-white text-xs py-2 px-3 rounded focus:outline-none focus:border-white font-medium"
          >
            <option value={0}>Wave 0 — Cloud Foundation</option>
            <option value={1}>Wave 1 — Quick Wins</option>
            <option value={2}>Wave 2 — Core Modernization</option>
            <option value={3}>Wave 3 — Regulated Core</option>
          </select>

          <button
            onClick={() => handleGeneratePack(selectedWaveToGen)}
            disabled={generatingWave !== null}
            className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-zinc-200 text-black rounded text-xs font-bold disabled:opacity-50 transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>
              {generatingWave !== null ? "Compiling..." : "Generate Wave PDF"}
            </span>
          </button>
        </div>
      </div>

      {/* Generated Evidence Packs List */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
          <div className="flex items-center gap-2">
            <FileCheck2 className="w-4 h-4 text-white" />
            <h2 className="text-sm font-bold text-white">Compiled Wave Evidence Dossiers</h2>
          </div>
          <span className="text-xs font-mono text-zinc-500">{packs.length} Dossiers Registered</span>
        </div>

        {packs.length === 0 ? (
          <div className="text-center py-12 space-y-3">
            <FileText className="w-10 h-10 text-zinc-700 mx-auto" />
            <p className="text-xs text-zinc-400">
              No evidence packs generated yet for this project. Select a wave above and click &quot;Generate Wave PDF&quot;.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {packs.map((pack) => {
              const downloadUrl = getEvidenceDownloadUrl(id, pack.wave);

              return (
                <div
                  key={pack.id}
                  className="p-4 rounded-xl bg-zinc-950 border border-zinc-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-2.5 rounded bg-zinc-900 text-white border border-zinc-800">
                      <FileText className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-xs font-bold text-white">{pack.file_name}</h3>
                        <span className="text-[10px] px-2 py-0.5 rounded font-mono font-bold bg-zinc-900 text-white border border-zinc-700">
                          {pack.wave}
                        </span>
                      </div>
                      <p className="text-[11px] text-zinc-400 mt-0.5 font-mono">
                        SHA-256:{" "}
                        <span className="text-zinc-300 text-[10px]">
                          {pack.sha256_hash}
                        </span>
                      </p>
                      <span className="text-[10px] text-zinc-500 font-mono block mt-1">
                        Compiled: {new Date(pack.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>

                  <a
                    href={downloadUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-2 px-4 py-2 rounded bg-white hover:bg-zinc-200 text-black font-bold text-xs transition-all self-end md:self-center font-mono"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download CSA PDF</span>
                  </a>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* CSA Dossier Contents Blueprint Breakdown */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
        <div>
          <h2 className="text-sm font-bold text-white">Compliance Dossier Section Architecture</h2>
          <p className="text-xs text-zinc-400">
            Every ModernRx PDF evidence pack satisfies GAMP 5 (2nd Ed) &amp; FDA CSA risk-based assurance:
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
            <span className="font-bold text-white">1. System Description</span>
            <p className="text-[11px] text-zinc-400">
              C4 container architecture, component count, and intended regulatory use.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
            <span className="font-bold text-white">2. GxP Criticality Breakdown</span>
            <p className="text-[11px] text-zinc-400">
              Part 11/Annex 11 tiering (HIGH/MED/LOW) and write-path propagation.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
            <span className="font-bold text-white">3. Risk-Based Testing Rigor</span>
            <p className="text-[11px] text-zinc-400">
              Scripted testing for critical functions; unscripted exploratory testing for peripheral tools.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
            <span className="font-bold text-white">4. Characterization Invariants</span>
            <p className="text-[11px] text-zinc-400">
              Pre-captured test harnesses verifying baseline behavior parity.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
            <span className="font-bold text-white">5. Differential Shadow Testing</span>
            <p className="text-[11px] text-zinc-400">
              Live request dual-routing, comparison tolerance, and rollback thresholds.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
            <span className="font-bold text-white">6. Data &amp; Audit Continuity</span>
            <p className="text-[11px] text-zinc-400">
              Table row counts, SHA-256 table checksums, and unbroken audit trail checks.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
            <span className="font-bold text-white">7. Traceability Matrix</span>
            <p className="text-[11px] text-zinc-400">
              End-to-end 21 CFR §11 clause ➔ component ➔ test ➔ knowledge graph evidence node ID.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
            <span className="font-bold text-white">8. Supplier &amp; Rollback Governance</span>
            <p className="text-[11px] text-zinc-400">
              Cloud shared responsibility qualification and 15-minute emergency rollback switches.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800 space-y-1">
            <span className="font-bold text-white">9. Human QA Signoff Block</span>
            <p className="text-[11px] text-zinc-400">
              Formal signature endorsement lines for CSV Lead, Security Officer, and Regulatory Director.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
