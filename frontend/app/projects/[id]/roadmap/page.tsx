"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import {
  CalendarDays,
  Clock,
  Sliders,
  TrendingUp,
  AlertTriangle,
  Layers,
  ArrowRight,
  Shield,
  RefreshCw,
} from "lucide-react";
import { fetchRoadmap, recalculateRoadmapWhatIf } from "@/lib/api";

export default function RoadmapPage() {
  const params = useParams();
  const id = (params?.id as string) || "acmelims-demo";

  const [roadmapData, setRoadmapData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // What-If Slider State
  const [squads, setSquads] = useState<number>(2);
  const [targetWeeks, setTargetWeeks] = useState<number>(22);
  const [recalculating, setRecalculating] = useState(false);

  useEffect(() => {
    loadRoadmap();
  }, [id]);

  async function loadRoadmap() {
    try {
      const data = await fetchRoadmap(id);
      setRoadmapData(data);
      if (data?.parameters?.squads) {
        setSquads(data.parameters.squads);
      }
      if (data?.monte_carlo?.p80_weeks) {
        setTargetWeeks(Math.ceil(data.monte_carlo.p80_weeks));
      }
    } catch (e) {
      console.error("Failed to load roadmap:", e);
    } finally {
      setLoading(false);
    }
  }

  async function handleSimulateWhatIf(newSquads?: number, newTarget?: number) {
    const s = newSquads ?? squads;
    const t = newTarget ?? targetWeeks;
    setRecalculating(true);
    try {
      const res = await recalculateRoadmapWhatIf(id, {
        squads: s,
        target_weeks: t,
        freeze_windows: [[12, 14]],
      });
      setRoadmapData(res);
    } catch (e) {
      console.error("Failed to re-simulate:", e);
    } finally {
      setRecalculating(false);
    }
  }

  const schedule = roadmapData?.schedule || {};
  const waves = schedule.waves || [];
  const mc = roadmapData?.monte_carlo || {
    p50_weeks: 14.5,
    p80_weeks: 18.5,
    p95_weeks: 24.0,
    prob_meeting_target: 82.5,
    histogram: [],
    drivers_of_uncertainty: [],
  };

  const makespan = schedule.makespan_weeks || 18;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Banner & KPI Summary */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-800 text-xs font-mono">
            <CalendarDays className="w-3.5 h-3.5 text-white" />
            <span>OR-Tools CP-SAT + 10,000 PERT Monte Carlo Runs</span>
          </div>
          <h1 className="text-xl font-extrabold text-white mt-1">
            Constraint-Aware Roadmap &amp; Schedule Uncertainty
          </h1>
          <p className="text-xs text-zinc-400">
            Schedules workloads under team capacity, foundation precedence, GxP freeze windows, and risk caps.
          </p>
        </div>

        {/* Confidence Percentiles */}
        <div className="flex items-center gap-4 bg-zinc-950 px-4 py-2.5 rounded-xl border border-zinc-800 font-mono">
          <div>
            <span className="text-[10px] text-zinc-500 uppercase block">P50 (Median)</span>
            <span className="text-lg font-bold text-white">{mc.p50_weeks} wks</span>
          </div>
          <div className="h-6 w-px bg-zinc-800" />
          <div>
            <span className="text-[10px] text-zinc-400 uppercase font-bold block">
              P80 (Budget Target)
            </span>
            <span className="text-lg font-black text-white">{mc.p80_weeks} wks</span>
          </div>
          <div className="h-6 w-px bg-zinc-800" />
          <div>
            <span className="text-[10px] text-zinc-500 uppercase block">P95 (Risk Cap)</span>
            <span className="text-lg font-bold text-zinc-400">{mc.p95_weeks} wks</span>
          </div>
        </div>
      </div>

      {/* Interactive What-If Sliders Bar */}
      <div className="rounded-xl p-4 border border-zinc-800 bg-black flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2 text-xs font-bold text-white uppercase font-mono">
          <Sliders className="w-4 h-4 text-white" />
          <span>Interactive What-If Scenario Modeling</span>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-6 w-full md:w-auto">
          {/* Squads Slider */}
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <span className="text-xs text-zinc-300 whitespace-nowrap">
              Dev Squads: <b className="text-white font-mono">{squads}</b>
            </span>
            <input
              type="range"
              min="1"
              max="6"
              value={squads}
              onChange={(e) => {
                const val = parseInt(e.target.value);
                setSquads(val);
                handleSimulateWhatIf(val, targetWeeks);
              }}
              className="w-28 accent-white cursor-pointer"
            />
          </div>

          {/* Target Weeks Slider */}
          <div className="flex items-center gap-3 w-full sm:w-auto">
            <span className="text-xs text-zinc-300 whitespace-nowrap">
              Target Deadline: <b className="text-white font-mono">{targetWeeks} wks</b>
            </span>
            <input
              type="range"
              min="10"
              max="35"
              value={targetWeeks}
              onChange={(e) => {
                const val = parseInt(e.target.value);
                setTargetWeeks(val);
                handleSimulateWhatIf(squads, val);
              }}
              className="w-28 accent-white cursor-pointer"
            />
          </div>

          {/* Probability Indicator */}
          <div className="flex items-center gap-2 text-xs bg-zinc-950 px-3 py-1.5 rounded-lg border border-zinc-800 font-mono">
            <span className="text-zinc-500">On-Time Probability:</span>
            <span className="font-bold text-white">
              {mc.prob_meeting_target}%
            </span>
          </div>
        </div>
      </div>

      {/* Main Gantt Wave Schedule */}
      <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
          <div>
            <h2 className="text-sm font-bold text-white">Migration Wave Gantt Schedule</h2>
            <p className="text-xs text-zinc-400">
              Phased waves with GxP freeze windows (Weeks 12–14) and max 1 HIGH-tier cutover per wave
            </p>
          </div>
          <span className="text-xs font-mono text-white font-bold">Makespan: {makespan} Weeks</span>
        </div>

        {/* Timeline Header Scale */}
        <div className="relative border-b border-zinc-800 pb-2 text-[10px] font-mono text-zinc-500 flex justify-between px-2">
          <span>Week 0</span>
          <span>Week 5</span>
          <span>Week 10</span>
          <span className="text-white font-bold uppercase underline underline-offset-2">Freeze (W12–14)</span>
          <span>Week 15</span>
          <span>Week 20</span>
          <span>Week 25</span>
        </div>

        {/* Waves List */}
        <div className="space-y-4 pt-2">
          {waves.map((wave: any) => (
            <div key={wave.wave_number} className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white">{wave.title}</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-800 font-mono">
                    {wave.theme}
                  </span>
                </div>
                <span className="text-xs text-zinc-400 font-mono">
                  Weeks {wave.start_week}–{wave.end_week} ({wave.end_week - wave.start_week} wks)
                </span>
              </div>

              {/* Tasks within this wave */}
              <div className="space-y-1.5 pl-3 border-l-2 border-zinc-800">
                {(wave.tasks || []).map((t: any) => {
                  const isHigh = t.gxp_tier === "HIGH";
                  const startPct = Math.min(100, (t.start_week / 25) * 100);
                  const durPct = Math.max(8, ((t.end_week - t.start_week) / 25) * 100);

                  const barBg = isHigh
                    ? "bg-white text-black font-semibold border-white"
                    : t.gxp_tier === "MEDIUM"
                    ? "bg-zinc-800 text-white border-zinc-600"
                    : "bg-zinc-900 text-zinc-300 border-zinc-800";

                  return (
                    <div key={t.id} className="relative h-8 flex items-center">
                      <div
                        className={`absolute h-7 rounded border text-[11px] font-medium px-2 flex items-center justify-between shadow-sm transition-all truncate font-mono ${barBg}`}
                        style={{
                          left: `${startPct}%`,
                          width: `${durPct}%`,
                          minWidth: "120px",
                        }}
                      >
                        <span className="truncate">{t.name}</span>
                        <span className="text-[9px] font-mono opacity-80 ml-1">
                          {t.duration}w
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom Grid: Monte Carlo Histogram & Tornado Variance Drivers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Monte Carlo Distribution Histogram */}
        <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
            <span className="text-xs font-bold text-white uppercase font-mono">
              Monte Carlo Completion Distribution
            </span>
            <span className="text-[10px] text-zinc-500 font-mono">10,000 PERT RUNS</span>
          </div>

          <div className="h-40 flex items-end gap-1 pt-4 px-2">
            {(mc.histogram || []).map((bin: any, idx: number) => {
              const maxCount = Math.max(...mc.histogram.map((b: any) => b.count), 1);
              const heightPct = Math.max(5, (bin.count / maxCount) * 100);
              const isP80Near = bin.bin_start <= mc.p80_weeks && bin.bin_end >= mc.p80_weeks;

              return (
                <div
                  key={idx}
                  className="flex-1 flex flex-col items-center group relative h-full justify-end"
                >
                  <div
                    className={`w-full rounded-t transition-all ${
                      isP80Near
                        ? "bg-white"
                        : "bg-zinc-800 hover:bg-zinc-600"
                    }`}
                    style={{ height: `${heightPct}%` }}
                  />
                  <div className="absolute -top-7 hidden group-hover:block bg-black text-white text-[9px] font-mono px-1.5 py-0.5 rounded border border-zinc-800 whitespace-nowrap z-10">
                    {bin.bin_start}w: {bin.count} runs
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex justify-between text-[10px] text-zinc-500 font-mono pt-1">
            <span>Optimistic (10w)</span>
            <span className="text-white font-bold">▲ P80: {mc.p80_weeks}w</span>
            <span>Pessimistic (28w)</span>
          </div>
        </div>

        {/* Tornado Chart Variance Drivers */}
        <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
            <span className="text-xs font-bold text-white uppercase font-mono">
              Sensitivity Analysis (Tornado Drivers)
            </span>
            <span className="text-[10px] text-zinc-500 font-mono">UNCERTAINTY DRIVERS</span>
          </div>

          <div className="space-y-2 pt-1">
            {(mc.drivers_of_uncertainty || []).map((d: any, idx: number) => (
              <div key={idx} className="space-y-1 text-xs">
                <div className="flex justify-between text-[11px]">
                  <span className="text-zinc-300 font-medium truncate max-w-[220px]">
                    {d.task_name}
                  </span>
                  <span className="font-mono text-white font-bold">
                    {d.variance_contribution}% variance
                  </span>
                </div>
                <div className="w-full bg-zinc-900 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-white"
                    style={{ width: `${Math.min(100, d.variance_contribution)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
