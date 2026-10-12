"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  Lock,
  RefreshCw,
  Search,
  ArrowLeft,
  FileText,
  X,
} from "lucide-react";
import { fetchAuditLogs, verifyAuditChain } from "@/lib/api";

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState<any | null>(null);
  const [selectedPayload, setSelectedPayload] = useState<any | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadAudit();
  }, []);

  async function loadAudit() {
    try {
      const data = await fetchAuditLogs();
      setLogs(data || []);
    } catch (e) {
      console.error("Failed to load audit logs:", e);
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyChain() {
    setVerifying(true);
    try {
      const res = await verifyAuditChain();
      setVerificationResult(res);
    } catch (e) {
      alert("Failed to verify audit hash chain.");
    } finally {
      setVerifying(false);
    }
  }

  const filteredLogs = logs.filter(
    (l) =>
      (l.action || "").toLowerCase().includes(search.toLowerCase()) ||
      (l.actor || "").toLowerCase().includes(search.toLowerCase()) ||
      (l.entity || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-800 text-xs font-mono">
            <Lock className="w-3.5 h-3.5 text-white" />
            <span>Self-Compliance Layer (Annex 22 / Part 11)</span>
          </div>
          <h1 className="text-xl font-extrabold text-white mt-1">
            Tamper-Evident SHA-256 Audit Trail
          </h1>
          <p className="text-xs text-zinc-400">
            Append-only cryptographic hash chain recording all AI decisions, GxP tier overrides, and human QA authorizations.
          </p>
        </div>

        <button
          onClick={handleVerifyChain}
          disabled={verifying}
          className="flex items-center gap-2 px-4 py-2.5 bg-white hover:bg-zinc-200 text-black font-semibold text-xs rounded disabled:opacity-50 transition-all self-start md:self-auto font-mono"
        >
          <ShieldCheck className="w-4 h-4" />
          <span>{verifying ? "Verifying Genesis to Tip..." : "Verify Hash Chain ✓"}</span>
        </button>
      </div>

      {/* Verification Result Banner */}
      {verificationResult && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between text-xs animate-fadeIn font-mono ${
            verificationResult.valid
              ? "bg-zinc-950 border-white text-white"
              : "bg-zinc-950 border-zinc-600 text-zinc-300"
          }`}
        >
          <div className="flex items-center gap-3">
            {verificationResult.valid ? (
              <CheckCircle2 className="w-5 h-5 text-white flex-shrink-0" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-white flex-shrink-0" />
            )}
            <div>
              <span className="font-bold text-sm block">
                {verificationResult.valid
                  ? "Cryptographic Integrity Verified Authentic"
                  : "Cryptographic Tampering Detected"}
              </span>
              <p className="text-xs text-zinc-400 mt-0.5">{verificationResult.message}</p>
            </div>
          </div>

          <button
            onClick={() => setVerificationResult(null)}
            className="text-zinc-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Logs Table Card */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pb-3 border-b border-zinc-800">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
            <input
              type="text"
              placeholder="Filter by action, actor, entity..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-zinc-950 rounded text-xs text-white border border-zinc-800 focus:outline-none focus:border-white placeholder:text-zinc-600 font-mono"
            />
          </div>

          <span className="text-xs text-zinc-500 font-mono">
            {filteredLogs.length} Cryptographic Blocks Recorded
          </span>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-zinc-950 text-zinc-400 uppercase font-mono text-[10px] border-b border-zinc-800">
              <tr>
                <th className="py-2.5 px-3"># Block</th>
                <th className="py-2.5 px-3">Timestamp (UTC)</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Actor</th>
                <th className="py-2.5 px-3">Target Entity</th>
                <th className="py-2.5 px-3">Previous Hash</th>
                <th className="py-2.5 px-3">SHA-256 Digest</th>
                <th className="py-2.5 px-3 text-right">Payload</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800 font-mono text-[11px]">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-zinc-900/40 transition-colors">
                  <td className="py-3 px-3 font-bold text-white">#{log.id}</td>
                  <td className="py-3 px-3 text-zinc-400 text-[10px]">
                    {new Date(log.ts).toLocaleString()}
                  </td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-zinc-900 text-white border border-zinc-700">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-zinc-300 font-sans text-xs">{log.actor}</td>
                  <td className="py-3 px-3 text-zinc-400">
                    {log.entity}:{log.entity_id}
                  </td>
                  <td className="py-3 px-3 text-zinc-500 text-[10px]" title={log.prev_hash}>
                    {log.prev_hash.slice(0, 10)}...
                  </td>
                  <td className="py-3 px-3 text-white text-[10px]" title={log.hash}>
                    {log.hash.slice(0, 10)}...
                  </td>
                  <td className="py-3 px-3 text-right font-sans">
                    <button
                      onClick={() => setSelectedPayload(log)}
                      className="px-2 py-1 rounded bg-black hover:bg-zinc-900 text-zinc-300 hover:text-white text-[10px] border border-zinc-800"
                    >
                      View Payload
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Payload Modal */}
      {selectedPayload && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn">
          <div className="bg-black border border-zinc-800 rounded-xl max-w-lg w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-white" />
                <h3 className="font-bold text-white text-sm font-mono">
                  Block #{selectedPayload.id} Payload Inspection
                </h3>
              </div>
              <button
                onClick={() => setSelectedPayload(null)}
                className="text-zinc-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex justify-between text-[11px] font-mono text-zinc-400 bg-zinc-950 p-2 rounded border border-zinc-800">
                <span>Action: <b className="text-white">{selectedPayload.action}</b></span>
                <span>Actor: <b className="text-white">{selectedPayload.actor}</b></span>
              </div>

              <div>
                <span className="text-[10px] font-mono uppercase text-zinc-500 block mb-1">
                  Canonical Serialized JSON:
                </span>
                <pre className="p-3 bg-zinc-950 rounded text-zinc-300 font-mono text-[11px] overflow-x-auto max-h-60 border border-zinc-800">
                  {JSON.stringify(selectedPayload.payload_json, null, 2)}
                </pre>
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-zinc-800">
              <button
                onClick={() => setSelectedPayload(null)}
                className="px-4 py-1.5 rounded bg-white hover:bg-zinc-200 text-black text-xs font-bold font-mono"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
