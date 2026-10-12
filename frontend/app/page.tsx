"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Activity,
  Layers,
  ShieldAlert,
  Cloud,
  ArrowRight,
  Plus,
  Play,
  FileCheck2,
  Clock,
  Database,
  Lock,
} from "lucide-react";

export default function HomePage() {
  const [projects, setProjects] = useState<any[]>([
    {
      id: "acmelims-demo",
      name: "AcmeLIMS (Legacy Monolith)",
      repo_url: "com.acme.lims:v2.4",
      target_cloud: "AWS",
      status: "ANALYZED",
      loc: "8,450",
      components: "24",
      gxp_high_ratio: "42%",
      readiness_score: "64/100",
      reval_scope_reduction: "-44%",
      created_at: "2026-10-12",
    },
  ]);

  const [assessmentModalOpen, setAssessmentModalOpen] = useState(false);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Banner - Black & White Enterprise */}
      <div className="rounded-xl p-8 border border-zinc-800 bg-zinc-950">
        <div className="max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-zinc-900 border border-zinc-700 text-zinc-300 text-xs font-mono">
            <span>FDA CSA (2025/2026) &bull; EU Annex 11/22 Regulatory Assurance</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
            Application Modernization Advisor for Regulated Pharma IT
          </h1>
          <p className="text-zinc-400 text-sm sm:text-base leading-relaxed">
            Standard AI rewrites code without regulatory context. ModernRx converts legacy pharma monoliths into a
            Living Architecture Twin, scores GxP criticality, minimizes validation blast radius,
            convenes an Architecture Council, and compiles audit-ready CSA Evidence Packs.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              href="/projects/acmelims-demo/overview"
              className="px-5 py-2.5 rounded bg-white hover:bg-zinc-200 text-black font-semibold text-sm flex items-center gap-2 transition-colors"
            >
              <Play className="w-4 h-4 fill-black text-black" />
              <span>Explore AcmeLIMS Assessment</span>
            </Link>
            <button
              onClick={() => setAssessmentModalOpen(true)}
              className="px-5 py-2.5 rounded bg-black hover:bg-zinc-900 text-white font-medium text-sm flex items-center gap-2 border border-zinc-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>New Repository Assessment</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Row - Monochromatic Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-lg bg-zinc-950 border border-zinc-800">
          <div className="flex items-center justify-between text-zinc-400 text-xs font-mono">
            <span>MODERNIZATION ENGINE</span>
            <Activity className="w-4 h-4 text-zinc-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">7 Engines</div>
          <p className="mt-1 text-xs text-zinc-500">Twin &bull; GxP &bull; Readiness &bull; Decomp &bull; Council &bull; Roadmap &bull; Evidence</p>
        </div>

        <div className="p-5 rounded-lg bg-zinc-950 border border-zinc-800">
          <div className="flex items-center justify-between text-zinc-400 text-xs font-mono">
            <span>REGULATORY MOAT</span>
            <ShieldAlert className="w-4 h-4 text-zinc-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">21 CFR Part 11</div>
          <p className="mt-1 text-xs text-zinc-500">Audit Trail, E-Signature, Batch Release &amp; ALCOA+ Gap Detection</p>
        </div>

        <div className="p-5 rounded-lg bg-zinc-950 border border-zinc-800">
          <div className="flex items-center justify-between text-zinc-400 text-xs font-mono">
            <span>REVALUATION BLAST RADIUS</span>
            <Layers className="w-4 h-4 text-zinc-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">-50.0% Reduction</div>
          <p className="mt-1 text-xs text-zinc-500">ModernRx Constrained vs Naive HDBSCAN Re-validation Footprint</p>
        </div>

        <div className="p-5 rounded-lg bg-zinc-950 border border-zinc-800">
          <div className="flex items-center justify-between text-zinc-400 text-xs font-mono">
            <span>SELF-COMPLIANCE</span>
            <Lock className="w-4 h-4 text-zinc-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-white">SHA-256 Ledger</div>
          <p className="mt-1 text-xs text-zinc-500">EU Annex 22 Tamper-Evident Hash Chain &amp; Mandatory QA Sign-off</p>
        </div>
      </div>

      {/* Projects List Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <span>Active Assessment Projects</span>
            <span className="text-xs px-2 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800 font-mono">
              {projects.length}
            </span>
          </h2>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {projects.map((proj) => (
            <div
              key={proj.id}
              className="p-6 rounded-lg bg-zinc-950 border border-zinc-800 hover:border-zinc-600 transition-colors group"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-bold text-white">
                      {proj.name}
                    </h3>
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-zinc-900 text-zinc-300 border border-zinc-700">
                      {proj.status}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-zinc-900 text-zinc-400 border border-zinc-800">
                      Target: {proj.target_cloud}
                    </span>
                  </div>
                  <p className="text-xs text-zinc-500 flex items-center gap-4 font-mono">
                    <span>Artifact: {proj.repo_url}</span>
                    <span>&bull;</span>
                    <span>LOC: {proj.loc}</span>
                    <span>&bull;</span>
                    <span>Components: {proj.components}</span>
                    <span>&bull;</span>
                    <span>Assessed: {proj.created_at}</span>
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right hidden sm:block">
                    <div className="text-xs text-zinc-500 font-mono">Readiness Score</div>
                    <div className="text-base font-bold text-white">{proj.readiness_score}</div>
                  </div>
                  <div className="text-right hidden sm:block">
                    <div className="text-xs text-zinc-500 font-mono">Blast Radius Cut</div>
                    <div className="text-base font-bold text-white">{proj.reval_scope_reduction}</div>
                  </div>
                  <Link
                    href={`/projects/${proj.id}/overview`}
                    className="px-4 py-2 rounded bg-white hover:bg-zinc-200 text-black text-xs font-semibold flex items-center gap-1.5 transition-colors"
                  >
                    <span>View Assessment</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              {/* Module Quick Jump Grid - Black & White */}
              <div className="mt-5 pt-4 border-t border-zinc-850 border-zinc-900 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 text-xs font-mono">
                <Link
                  href={`/projects/${proj.id}/twin`}
                  className="px-3 py-2 rounded bg-black hover:bg-zinc-900 border border-zinc-900 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center gap-1.5 transition-colors"
                >
                  <Layers className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Living Twin</span>
                </Link>
                <Link
                  href={`/projects/${proj.id}/gxp`}
                  className="px-3 py-2 rounded bg-black hover:bg-zinc-900 border border-zinc-900 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center gap-1.5 transition-colors"
                >
                  <ShieldAlert className="w-3.5 h-3.5 text-zinc-400" />
                  <span>GxP Heatmap</span>
                </Link>
                <Link
                  href={`/projects/${proj.id}/readiness`}
                  className="px-3 py-2 rounded bg-black hover:bg-zinc-900 border border-zinc-900 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center gap-1.5 transition-colors"
                >
                  <Cloud className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Readiness</span>
                </Link>
                <Link
                  href={`/projects/${proj.id}/decomposition`}
                  className="px-3 py-2 rounded bg-black hover:bg-zinc-900 border border-zinc-900 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center gap-1.5 transition-colors"
                >
                  <Layers className="w-3.5 h-3.5 text-zinc-400" />
                  <span>RevalScope</span>
                </Link>
                <Link
                  href={`/projects/${proj.id}/council`}
                  className="px-3 py-2 rounded bg-black hover:bg-zinc-900 border border-zinc-900 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center gap-1.5 transition-colors"
                >
                  <Activity className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Council</span>
                </Link>
                <Link
                  href={`/projects/${proj.id}/roadmap`}
                  className="px-3 py-2 rounded bg-black hover:bg-zinc-900 border border-zinc-900 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center gap-1.5 transition-colors"
                >
                  <Clock className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Roadmap</span>
                </Link>
                <Link
                  href={`/projects/${proj.id}/evidence`}
                  className="px-3 py-2 rounded bg-black hover:bg-zinc-900 border border-zinc-900 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center gap-1.5 transition-colors"
                >
                  <FileCheck2 className="w-3.5 h-3.5 text-zinc-400" />
                  <span>Evidence Pack</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Assessment Modal */}
      {assessmentModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="assessment-modal-title"
        >
          <div className="bg-zinc-950 max-w-lg w-full p-6 space-y-4 border border-zinc-700 rounded-lg shadow-2xl">
            <h3 id="assessment-modal-title" className="text-lg font-bold text-white">
              Create Repository Assessment
            </h3>
            <p className="text-xs text-zinc-400">
              Upload a source archive (ZIP) or provide repository metadata. ModernRx will ingest the
              source code, SQL models, configs, and traces to generate the Living Twin.
            </p>
            <div className="space-y-3">
              <div>
                <label htmlFor="app-name-input" className="text-xs font-mono text-zinc-400 block">
                  Application Name
                </label>
                <input
                  id="app-name-input"
                  type="text"
                  defaultValue="EnterpriseLIMS-v2"
                  className="mt-1 w-full px-3 py-2 rounded bg-black border border-zinc-800 text-sm text-white focus:outline-none focus:border-white focus-visible:ring-2 focus-visible:ring-white font-mono"
                />
              </div>
              <div>
                <label htmlFor="target-cloud-select" className="text-xs font-mono text-zinc-400 block">
                  Target Cloud
                </label>
                <select
                  id="target-cloud-select"
                  className="mt-1 w-full px-3 py-2 rounded bg-black border border-zinc-800 text-sm text-white focus:outline-none focus:border-white focus-visible:ring-2 focus-visible:ring-white font-mono"
                >
                  <option>AWS (Amazon Web Services)</option>
                  <option>Azure (Microsoft Azure)</option>
                  <option>GCP (Google Cloud Platform)</option>
                </select>
              </div>
              <div className="p-4 rounded border border-dashed border-zinc-800 bg-black text-center">
                <p className="text-xs text-zinc-400">Select or drop AcmeLIMS repository ZIP</p>
                <button
                  type="button"
                  className="mt-2 px-3 py-1.5 rounded bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-xs text-zinc-200 focus-visible:ring-2 focus-visible:ring-white"
                >
                  Use Built-in AcmeLIMS Monolith
                </button>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setAssessmentModalOpen(false)}
                className="px-4 py-2 min-h-[38px] rounded bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 hover:bg-zinc-800 focus-visible:ring-2 focus-visible:ring-white"
              >
                Cancel
              </button>
              <Link
                href="/projects/acmelims-demo/overview"
                className="px-4 py-2 min-h-[38px] rounded bg-white text-xs text-black font-semibold hover:bg-zinc-200 focus-visible:ring-2 focus-visible:ring-white flex items-center justify-center"
              >
                Start Assessment
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
