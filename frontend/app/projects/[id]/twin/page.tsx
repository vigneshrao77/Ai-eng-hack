"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import {
  Layers,
  Search,
  MessageSquare,
  Send,
  Database,
  Code,
  Shield,
  FileCode,
  Info,
  ChevronRight,
  X,
} from "lucide-react";
import { fetchTwinGraph, askTwin } from "@/lib/api";

export default function TwinGraphPage() {
  const params = useParams();
  const id = (params?.id as string) || "acmelims-demo";

  const [graphData, setGraphData] = useState<{ nodes: any[]; edges: any[] }>({
    nodes: [],
    edges: [],
  });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedNode, setSelectedNode] = useState<any | null>(null);

  // Ask-the-Twin Drawer State
  const [chatOpen, setChatOpen] = useState(false);
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string; evidence?: string[] }>>([
    {
      role: "assistant",
      content:
        "Hello! I am your Living Architecture Twin AI assistant. Ask me questions about component dependencies, blast radius, or who writes to regulated tables.",
    },
  ]);
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    async function loadGraph() {
      try {
        const data = await fetchTwinGraph(id);
        if (data && data.nodes) {
          setGraphData(data);
          if (data.nodes.length > 0) {
            setSelectedNode(data.nodes[0]);
          }
        }
      } catch (e) {
        console.error("Failed to load twin graph:", e);
      } finally {
        setLoading(false);
      }
    }
    loadGraph();
  }, [id]);

  const filteredNodes = graphData.nodes.filter((n) =>
    (n.name || n.id || "").toLowerCase().includes(search.toLowerCase())
  );

  async function handleSendQuestion(q?: string) {
    const questionText = q || chatQuestion;
    if (!questionText.trim()) return;

    setChatMessages((prev) => [...prev, { role: "user", content: questionText }]);
    setChatQuestion("");
    setAsking(true);

    try {
      const res = await askTwin(id, questionText);
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.answer || "No response received.",
          evidence: res.evidence_ids || [],
        },
      ]);
    } catch (e: any) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I could not query the Architecture Twin. Please check backend connectivity.",
        },
      ]);
    } finally {
      setAsking(false);
    }
  }

  const sampleQuestions = [
    "Who writes to the regulated RESULT table?",
    "What is the blast radius of changing SampleService?",
    "Which components have local filesystem dependencies?",
  ];

  return (
    <div className="space-y-4 animate-fadeIn">
      {/* Top Controls Bar */}
      <div className="rounded-lg p-3 flex flex-col sm:flex-row items-center justify-between gap-3 border border-zinc-800 bg-zinc-950">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" />
          <input
            type="text"
            placeholder="Search classes, tables, endpoints..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-black rounded text-xs text-zinc-200 border border-zinc-800 focus:outline-none focus:border-zinc-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          <button
            onClick={() => setChatOpen(true)}
            className="flex items-center gap-2 px-3.5 py-2 bg-white hover:bg-zinc-200 text-black rounded text-xs font-semibold transition-colors"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Ask the Twin</span>
          </button>
        </div>
      </div>

      {/* Main Two-Column Graph & Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Graph / Node Explorer Canvas */}
        <div className="lg:col-span-2 rounded-lg p-5 border border-zinc-800 bg-zinc-950 min-h-[500px] flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800 mb-4">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-white" />
                <span className="text-sm font-semibold text-white">Architecture Twin Component Map</span>
              </div>
              <span className="text-xs text-zinc-400 font-mono">
                {filteredNodes.length} Nodes &nbsp;|&nbsp; {graphData.edges.length} Edges
              </span>
            </div>

            {/* Visual Node Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[420px] overflow-y-auto pr-1">
              {filteredNodes.map((node) => {
                const isSelected = selectedNode?.id === node.id;
                const tierBorder =
                  node.gxp_tier === "HIGH"
                    ? "border-zinc-500 bg-zinc-950 text-white"
                    : node.gxp_tier === "MEDIUM"
                    ? "border-zinc-700 bg-zinc-950 text-zinc-300"
                    : "border-zinc-800 bg-black text-zinc-400";

                return (
                  <div
                    key={node.id}
                    onClick={() => setSelectedNode(node)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? "border-white bg-zinc-900 text-white ring-1 ring-white"
                        : `${tierBorder} hover:border-zinc-500`
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-xs text-white truncate max-w-[180px]">
                        {node.name || node.id.split(".").pop()}
                      </span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                          node.gxp_tier === "HIGH"
                            ? "bg-white text-black font-bold"
                            : node.gxp_tier === "MEDIUM"
                            ? "border border-zinc-600 bg-zinc-900 text-zinc-300"
                            : "border border-zinc-800 bg-black text-zinc-400"
                        }`}
                      >
                        {node.gxp_tier || "LOW"}
                      </span>
                    </div>

                    <div className="text-[11px] text-zinc-400 truncate mt-1">{node.id}</div>

                    <div className="flex items-center gap-3 mt-2 text-[10px] text-zinc-500 font-mono">
                      <span>LOC: {node.loc || 150}</span>
                      <span>Fan-In: {node.fan_in || 1}</span>
                      <span>Readiness: {node.readiness || 75}/100</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="text-xs text-zinc-500 pt-3 border-t border-zinc-800 flex items-center justify-between">
            <span>Click any component node to inspect full AST metrics, GxP tags, and evidence.</span>
            <span className="font-mono text-zinc-400 text-[10px]">● GRAPH SYNCED</span>
          </div>
        </div>

        {/* Component Inspector Panel */}
        <div className="rounded-xl p-5 border border-zinc-800 bg-black space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-white" />
              <span className="text-sm font-semibold text-white">Component Inspector</span>
            </div>
            {selectedNode && (
              <span className="text-xs px-2 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-800 font-mono">
                {selectedNode.type || "Class"}
              </span>
            )}
          </div>

          {selectedNode ? (
            <div className="space-y-4">
              <div>
                <div className="text-xs text-zinc-400 font-medium">Fully Qualified Name (FQN)</div>
                <div className="text-sm font-mono text-white break-all bg-zinc-950 p-2 rounded-lg mt-1 border border-zinc-800">
                  {selectedNode.id}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-zinc-950 p-2.5 rounded-lg border border-zinc-800">
                  <span className="text-zinc-400">GxP Risk Tier</span>
                  <div
                    className={`font-bold mt-1 text-sm font-mono ${
                      selectedNode.gxp_tier === "HIGH"
                        ? "text-white underline underline-offset-2"
                        : selectedNode.gxp_tier === "MEDIUM"
                        ? "text-zinc-300"
                        : "text-zinc-400"
                    }`}
                  >
                    {selectedNode.gxp_tier || "LOW"}
                  </div>
                </div>

                <div className="bg-zinc-950 p-2.5 rounded-lg border border-zinc-800">
                  <span className="text-zinc-400">Cloud Readiness</span>
                  <div className="font-bold text-white mt-1 text-sm font-mono">
                    {selectedNode.readiness || 80}/100
                  </div>
                </div>

                <div className="bg-zinc-950 p-2.5 rounded-lg border border-zinc-800">
                  <span className="text-zinc-400">Lines of Code (LOC)</span>
                  <div className="font-bold text-white mt-1 text-sm font-mono">{selectedNode.loc || 280}</div>
                </div>

                <div className="bg-zinc-950 p-2.5 rounded-lg border border-zinc-800">
                  <span className="text-zinc-400">Cyclomatic Complexity</span>
                  <div className="font-bold text-white mt-1 text-sm font-mono">
                    {selectedNode.complexity || 8}
                  </div>
                </div>
              </div>

              {/* Regulatory Criticality Tags */}
              <div>
                <div className="text-xs text-zinc-400 font-medium mb-1.5">Detected GxP Tags</div>
                <div className="flex flex-wrap gap-1.5">
                  {(selectedNode.gxp_tags || ["DATA_INTEGRITY"]).map((tag: string) => (
                    <span
                      key={tag}
                      className="text-[11px] px-2 py-0.5 rounded bg-zinc-900 text-zinc-200 border border-zinc-700 font-mono"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Connected Relationships */}
              <div>
                <div className="text-xs text-zinc-400 font-medium mb-1.5">Graph Relationships</div>
                <div className="text-xs text-zinc-300 bg-zinc-950 p-2.5 rounded-lg border border-zinc-800 space-y-1">
                  <div className="flex justify-between">
                    <span className="text-zinc-400">Inbound Callers (Fan-In):</span>
                    <span className="font-mono text-white">{selectedNode.fan_in || 2}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-400">Outbound Calls (Fan-Out):</span>
                    <span className="font-mono text-white">{selectedNode.fan_out || 3}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-400">Cluster Partition:</span>
                    <span className="font-mono text-white">
                      {selectedNode.cluster_id || "Core Service"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-zinc-500 text-sm">
              Select a component from the map to inspect properties.
            </div>
          )}
        </div>
      </div>

      {/* Ask the Twin Slide-Over Chat Modal */}
      {chatOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex justify-end animate-fadeIn">
          <div className="w-full max-w-md bg-black border-l border-zinc-800 h-full flex flex-col shadow-2xl">
            {/* Header */}
            <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-950">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-white" />
                <h3 className="font-bold text-white text-sm">Architecture Knowledge Query</h3>
              </div>
              <button
                onClick={() => setChatOpen(false)}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-900"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Suggested Prompts */}
            <div className="p-3 bg-zinc-950 border-b border-zinc-800">
              <span className="text-[10px] text-zinc-400 uppercase font-semibold">Suggested Queries:</span>
              <div className="flex flex-col gap-1.5 mt-2">
                {sampleQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSendQuestion(q)}
                    className="text-left text-xs text-zinc-300 hover:text-black hover:bg-white px-2.5 py-1.5 rounded border border-zinc-800 hover:border-white transition-all truncate"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Chat Body */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-black">
              {chatMessages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col ${
                    m.role === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-lg p-3 text-xs leading-relaxed ${
                      m.role === "user"
                        ? "bg-white text-black font-medium"
                        : "bg-zinc-900 text-zinc-200 border border-zinc-800"
                    }`}
                  >
                    {m.content}
                    {m.evidence && m.evidence.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-zinc-800">
                        <span className="text-[10px] text-zinc-400 font-mono block mb-1">
                          CITED EVIDENCE NODES:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {m.evidence.map((ev, i) => (
                            <span
                              key={i}
                              className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black text-zinc-200 border border-zinc-700"
                            >
                              {ev.split(".").pop()}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {asking && (
                <div className="flex items-center gap-2 text-xs text-zinc-400 p-2">
                  <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
                  <span>Traversing Architecture Graph...</span>
                </div>
              )}
            </div>

            {/* Input Footer */}
            <div className="p-3 border-t border-zinc-800 bg-zinc-950 flex gap-2">
              <input
                type="text"
                placeholder="Ask about blast radius, tables, dependencies..."
                value={chatQuestion}
                onChange={(e) => setChatQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendQuestion()}
                className="flex-1 px-3 py-2 bg-black rounded-lg text-xs text-white border border-zinc-800 focus:outline-none focus:border-white placeholder:text-zinc-600"
              />
              <button
                onClick={() => handleSendQuestion()}
                disabled={asking}
                className="p-2 bg-white hover:bg-zinc-200 text-black rounded-lg disabled:opacity-50 font-bold"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
