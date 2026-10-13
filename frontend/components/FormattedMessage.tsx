"use client";

import React, { useState } from "react";
import { Copy, Check, Bot, Sparkles, Terminal, FileCode, CheckCircle2 } from "lucide-react";

interface FormattedMessageProps {
  role: "user" | "assistant";
  content: string;
  evidence?: string[];
  source?: string;
  onSelectNode?: (nodeId: string) => void;
}

// Inline renderer for bold, italic, code, and links
function renderFormattedInlineText(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  // Matches ***bold italic***, **bold**, *italic*, `code`, and [link](url)
  const regex = /(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*[^*]+?\*|`[^`]+?`|\[[^\]]+?\]\([^)]+?\))/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }
    const token = match[0];

    if (token.startsWith("***") && token.endsWith("***")) {
      parts.push(
        <strong key={match.index} className="font-semibold italic text-white">
          {token.slice(3, -3)}
        </strong>
      );
    } else if (token.startsWith("**") && token.endsWith("**")) {
      parts.push(
        <strong key={match.index} className="font-semibold text-white">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith("*") && token.endsWith("*")) {
      parts.push(
        <em key={match.index} className="italic text-zinc-300">
          {token.slice(1, -1)}
        </em>
      );
    } else if (token.startsWith("`") && token.endsWith("`")) {
      parts.push(
        <code
          key={match.index}
          className="px-1.5 py-0.5 rounded bg-zinc-950 text-zinc-200 font-mono text-[11px] border border-zinc-800"
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith("[") && token.includes("](")) {
      const linkMatch = token.match(/\[([^\]]+)\]\(([^)]+)\)/);
      if (linkMatch) {
        parts.push(
          <a
            key={match.index}
            href={linkMatch[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="text-white underline hover:text-zinc-300 transition-colors"
          >
            {linkMatch[1]}
          </a>
        );
      } else {
        parts.push(token);
      }
    }
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}

// Sub-component for code blocks with dedicated copy button
function CodeBlock({ code, language }: { code: string; language?: string }) {
  const [copied, setCopied] = useState(false);

  function copyCode() {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="my-2.5 rounded-lg border border-zinc-800 bg-zinc-950 overflow-hidden shadow-sm">
      <div className="flex items-center justify-between px-3 py-1.5 bg-zinc-900 border-b border-zinc-800 text-[10px] font-mono text-zinc-400">
        <div className="flex items-center gap-1.5">
          <Terminal className="w-3 h-3 text-zinc-400" />
          <span className="uppercase font-semibold tracking-wider">{language || "CODE"}</span>
        </div>
        <button
          onClick={copyCode}
          className="flex items-center gap-1 hover:text-white transition-colors px-1.5 py-0.5 rounded hover:bg-zinc-800"
          title="Copy code snippet"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-green-400" />
              <span className="text-green-400">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <pre className="p-3.5 overflow-x-auto font-mono text-[11px] leading-relaxed text-zinc-200 bg-zinc-950">
        <code>{code}</code>
      </pre>
    </div>
  );
}

// Sub-component for markdown tables
function MarkdownTable({ rawRows }: { rawRows: string[] }) {
  if (rawRows.length < 2) return null;

  const parseCells = (row: string) =>
    row
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((c) => c.trim());

  const headers = parseCells(rawRows[0]);
  // Row 1 is divider (|---|---|)
  const dataRows = rawRows.slice(2).map(parseCells);

  return (
    <div className="my-2.5 overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-950">
      <table className="w-full text-left text-xs border-collapse">
        <thead>
          <tr className="border-b border-zinc-800 bg-zinc-900/90 text-white font-mono text-[11px]">
            {headers.map((h, i) => (
              <th key={i} className="px-3 py-2 font-semibold">
                {renderFormattedInlineText(h)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800/60 text-zinc-300">
          {dataRows.map((row, rIdx) => (
            <tr key={rIdx} className="hover:bg-zinc-900/50 transition-colors">
              {row.map((cell, cIdx) => (
                <td key={cIdx} className="px-3 py-2 font-mono text-[11px]">
                  {renderFormattedInlineText(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function FormattedMessage({
  role,
  content,
  evidence,
  source,
  onSelectNode,
}: FormattedMessageProps) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (role === "user") {
    return (
      <div className="flex flex-col items-end">
        <div className="max-w-[85%] rounded-2xl px-4 py-2.5 text-xs bg-white text-black font-medium shadow-sm leading-relaxed">
          {content}
        </div>
      </div>
    );
  }

  // Parse assistant content into structured markdown blocks
  const rawLines = content.split("\n");
  const blocks: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeBuffer: string[] = [];
  let codeLang = "";
  let tableBuffer: string[] = [];

  const flushTable = (keyPrefix: string) => {
    if (tableBuffer.length >= 2) {
      blocks.push(<MarkdownTable key={`${keyPrefix}-table`} rawRows={[...tableBuffer]} />);
    } else if (tableBuffer.length > 0) {
      // Not a full table, render as lines
      tableBuffer.forEach((line, idx) => {
        blocks.push(
          <p key={`${keyPrefix}-tblfallback-${idx}`} className="text-xs text-zinc-300 leading-relaxed font-mono">
            {line}
          </p>
        );
      });
    }
    tableBuffer = [];
  };

  for (let i = 0; i < rawLines.length; i++) {
    const line = rawLines[i];
    const trimmed = line.trim();

    // Check code fence
    if (trimmed.startsWith("```")) {
      flushTable(`pre-code-${i}`);
      if (inCodeBlock) {
        blocks.push(
          <CodeBlock
            key={`code-${i}`}
            code={codeBuffer.join("\n")}
            language={codeLang}
          />
        );
        codeBuffer = [];
        codeLang = "";
        inCodeBlock = false;
      } else {
        inCodeBlock = true;
        codeLang = trimmed.replace(/^```/, "").trim();
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      continue;
    }

    // Check table rows (| cell | cell |)
    const isTableRow = trimmed.startsWith("|") && trimmed.endsWith("|") && trimmed.includes("|");
    if (isTableRow) {
      tableBuffer.push(trimmed);
      continue;
    } else if (tableBuffer.length > 0) {
      flushTable(`row-${i}`);
    }

    if (!trimmed) {
      blocks.push(<div key={`empty-${i}`} className="h-2" />);
      continue;
    }

    // Markdown Headings (# Heading, ## Heading, ### Heading, #### Heading)
    const mdHeadingMatch = trimmed.match(/^(#{1,4})\s+(.+)$/);
    // Bold Section Heading on its own line: **Heading:** or **Heading**
    const boldHeadingMatch = trimmed.match(/^\*\*([^*]+)\*\*[:\s]*$/);

    if (mdHeadingMatch || boldHeadingMatch) {
      const headingText = mdHeadingMatch ? mdHeadingMatch[2] : boldHeadingMatch![1];
      const level = mdHeadingMatch ? mdHeadingMatch[1].length : 3;

      blocks.push(
        <div key={`h-${i}`} className="pt-2.5 pb-1">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-800/90 text-white font-bold text-xs font-mono border border-zinc-700 shadow-sm">
            <Sparkles className="w-3 h-3 text-zinc-200" />
            <span>{headingText}</span>
          </div>
        </div>
      );
      continue;
    }

    // Blockquote (> Quote)
    if (trimmed.startsWith(">")) {
      const quoteText = trimmed.replace(/^>\s*/, "");
      blocks.push(
        <div
          key={`quote-${i}`}
          className="my-1.5 pl-3 py-1.5 border-l-2 border-zinc-600 bg-zinc-950/70 rounded-r-md text-xs text-zinc-300 italic leading-relaxed"
        >
          {renderFormattedInlineText(quoteText)}
        </div>
      );
      continue;
    }

    // Detect indentation for nested lists
    const indentMatch = line.match(/^(\s+)/);
    const indentSpaces = indentMatch ? indentMatch[1].length : 0;
    const isNested = indentSpaces >= 2;
    const indentPadding = isNested ? "pl-5" : "pl-1";

    // Bullet list (*, -, +, •)
    const bulletMatch = trimmed.match(/^[\*\-+\•]\s+(.*)$/);
    if (bulletMatch) {
      const itemText = bulletMatch[1];
      blocks.push(
        <div key={`bullet-${i}`} className={`flex items-start gap-2.5 text-xs text-zinc-200 leading-relaxed ${indentPadding}`}>
          <span
            className={`rounded-full mt-1.5 shrink-0 ${
              isNested
                ? "w-1 h-1 bg-zinc-500 border border-zinc-400"
                : "w-1.5 h-1.5 bg-zinc-300"
            }`}
          />
          <div className="flex-1">{renderFormattedInlineText(itemText)}</div>
        </div>
      );
      continue;
    }

    // Numbered list (1. Item, 2. Item)
    const numMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (numMatch) {
      const num = numMatch[1];
      const itemText = numMatch[2];
      blocks.push(
        <div key={`num-${i}`} className={`flex items-start gap-2 text-xs text-zinc-200 leading-relaxed ${indentPadding}`}>
          <span className="px-1.5 py-0.5 rounded-full bg-zinc-800 text-[10px] font-mono font-bold text-zinc-300 border border-zinc-700 shrink-0 leading-none mt-0.5">
            {num}
          </span>
          <div className="flex-1">{renderFormattedInlineText(itemText)}</div>
        </div>
      );
      continue;
    }

    // Standard paragraph line
    blocks.push(
      <p key={`p-${i}`} className="text-xs text-zinc-300 leading-relaxed">
        {renderFormattedInlineText(trimmed)}
      </p>
    );
  }

  // Flush any remaining table at the end
  if (tableBuffer.length > 0) {
    flushTable("final");
  }

  // Handle open code block at the end if truncated
  if (inCodeBlock && codeBuffer.length > 0) {
    blocks.push(
      <CodeBlock
        key="code-final"
        code={codeBuffer.join("\n")}
        language={codeLang}
      />
    );
  }

  return (
    <div className="flex flex-col items-start w-full">
      <div className="w-full rounded-2xl p-4 bg-zinc-900/95 border border-zinc-800/90 shadow-md space-y-3">
        {/* Assistant Header */}
        <div className="flex items-center justify-between pb-2 border-b border-zinc-800/80">
          <div className="flex items-center gap-2">
            <div className="p-1 rounded-md bg-white text-black">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <span className="text-xs font-bold text-white">AI Architecture Advisor</span>
            {source && (
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-950 text-zinc-400 border border-zinc-800">
                {source.split("&")[0].trim()}
              </span>
            )}
          </div>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 text-[11px] text-zinc-400 hover:text-white px-2.5 py-1 rounded-md bg-zinc-950 border border-zinc-800 hover:border-zinc-700 transition-colors"
            title="Copy entire answer"
          >
            {copied ? (
              <>
                <Check className="w-3 h-3 text-green-400" />
                <span className="text-green-400 text-[10px]">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3 h-3" />
                <span className="text-[10px]">Copy</span>
              </>
            )}
          </button>
        </div>

        {/* Structured Body Content */}
        <div className="space-y-1.5 py-0.5">{blocks}</div>

        {/* Cited Evidence Nodes */}
        {evidence && evidence.length > 0 && (
          <div className="mt-3 pt-2.5 border-t border-zinc-800/80 space-y-1.5">
            <span className="text-[10px] text-zinc-400 uppercase font-mono font-semibold block">
              Referenced Architecture Components (Click to Inspect):
            </span>
            <div className="flex flex-wrap gap-1.5">
              {evidence.map((ev, i) => {
                const cleanName = typeof ev === "string" ? ev.split(".").pop() : String(ev);
                return (
                  <button
                    key={i}
                    onClick={() => onSelectNode && onSelectNode(String(ev))}
                    className="text-[10px] font-mono px-2.5 py-1 rounded-md bg-zinc-950 hover:bg-white text-zinc-300 hover:text-black border border-zinc-800 hover:border-white transition-all cursor-pointer font-medium flex items-center gap-1 shadow-sm"
                  >
                    <span>🔍</span>
                    <span>{cleanName}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
