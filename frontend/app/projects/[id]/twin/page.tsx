"use client";

import React, { useState, useEffect, useRef } from "react";
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
  Trash2,
  Sparkles,
} from "lucide-react";
import { fetchTwinGraph, askTwin } from "@/lib/api";
import { FormattedMessage } from "@/components/FormattedMessage";

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
  const [chatMessages, setChatMessages] = useState<
    Array<{ role: string; content: string; evidence?: string[]; source?: string }>
  >([
    {
      role: "assistant",
      content:
        "Hello! I am your AI Architecture Advisor. Ask me anything about your project in plain English—like what each component does, how data flows, or the easiest way to modernize it into the cloud.",
      source: "Architecture Twin Advisor",
    },
  ]);
  const [asking, setAsking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (chatOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      inputRef.current?.focus();
    }
  }, [chatMessages, asking, chatOpen]);

  useEffect(() => {
    async function loadGraph() {
      try {
        const data = await fetchTwinGraph(id);
        const rawNodes =
          data?.nodes ||
          (data?.elements?.nodes ? data.elements.nodes.map((n: any) => n.data || n) : []) ||
          [];
        const rawEdges =
          data?.edges ||
          (data?.elements?.edges ? data.elements.edges.map((e: any) => e.data || e) : []) ||
          [];

        setGraphData({ nodes: rawNodes, edges: rawEdges });
        if (rawNodes.length > 0) {
          setSelectedNode(rawNodes[0]);
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
          evidence: res.evidence_node_ids || res.evidence_ids || [],
          source: res.source || "Architecture Twin Advisor",
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
    "What does this application do in plain English?",
    "Which components are highest risk and why?",
    "What are the best steps to modernize this into the cloud?",
    "Who connects to the database or external services?",
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
                        {node.name || (typeof node.id === "string" ? node.id.split(".").pop() : "") || "Component"}
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
          <div className="w-full max-w-xl md:max-w-2xl bg-black border-l border-zinc-800 h-full flex flex-col shadow-2xl">
            {/* Header */}
            <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-950">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-lg bg-white text-black font-bold">
                  <MessageSquare className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-sm">Architecture AI Advisor</h3>
                  <p className="text-[10px] text-zinc-400 font-mono">Living Twin Graph Knowledge Query</p>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                {chatMessages.length > 1 && (
                  <button
                    onClick={() =>
                      setChatMessages([
                        {
                          role: "assistant",
                          content:
                            "Hello! I am your AI Architecture Advisor. Ask me anything about your project in plain English—like what each component does, how data flows, or the easiest way to modernize it into the cloud.",
                          source: "Architecture Twin Advisor",
                        },
                      ])
                    }
                    className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-900 transition-colors"
                    title="Clear chat history"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => setChatOpen(false)}
                  className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-900 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Suggested Prompts */}
            <div className="p-3 bg-zinc-950 border-b border-zinc-800">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[10px] text-zinc-400 uppercase font-mono font-semibold">
                  Suggested Questions (Click to Ask):
                </span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                {sampleQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSendQuestion(q)}
                    className="text-left text-[11px] text-zinc-300 hover:text-black hover:bg-white px-2.5 py-1.5 rounded-md border border-zinc-800 hover:border-white transition-all truncate"
                    title={q}
                  >
                    💬 {q}
                  </button>
                ))}
              </div>
            </div>

            {/* Chat Body */}
            <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-black">
              {chatMessages.map((m, idx) => (
                <FormattedMessage
                  key={idx}
                  role={m.role as "user" | "assistant"}
                  content={m.content}
                  evidence={m.evidence}
                  source={m.source}
                  onSelectNode={(nodeId) => {
                    const found = graphData.nodes.find(
                      (n) =>
                        n.id === nodeId ||
                        n.name === nodeId ||
                        (typeof n.id === "string" && n.id.endsWith(nodeId))
                    );
                    if (found) {
                      setSelectedNode(found);
                    }
                  }}
                />
              ))}

              {asking && (
                <div className="flex items-center gap-2.5 text-xs text-zinc-300 p-3.5 rounded-2xl bg-zinc-900 border border-zinc-800 animate-pulse">
                  <Sparkles className="w-4 h-4 text-white animate-spin" />
                  <span>Traversing architecture graph and analyzing with AI model...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Footer */}
            <div className="p-3 border-t border-zinc-800 bg-zinc-950 flex gap-2">
              <input
                ref={inputRef}
                type="text"
                placeholder="Ask anything about components, data flows, blast radius, cloud..."
                value={chatQuestion}
                onChange={(e) => setChatQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendQuestion()}
                className="flex-1 px-3 py-2 bg-black rounded-lg text-xs text-white border border-zinc-800 focus:outline-none focus:border-white placeholder:text-zinc-600 font-sans"
              />
              <button
                onClick={() => handleSendQuestion()}
                disabled={asking || !chatQuestion.trim()}
                className="px-3 py-2 bg-white hover:bg-zinc-200 text-black rounded-lg disabled:opacity-40 font-bold flex items-center gap-1.5 text-xs transition-all"
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
