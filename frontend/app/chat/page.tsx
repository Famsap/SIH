"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  postChatQuestion,
  fetchHealth,
  ChatMessage,
  ChatTurn,
  Citation,
  HealthReport,
} from "@/lib/api";
import { DocumentAttachment } from "@/components/chat/DocumentAttachment";

const STORAGE_KEY = "manaksetu:chat:v1";
const WELCOME_ID = "welcome";

const WELCOME_MESSAGE: ChatMessage = {
  id: WELCOME_ID,
  role: "assistant",
  content:
    "Namaste! I am ManakSetu (मानकसेतु), your AI assistant for Indian Standards (IS Codes), BIS Conformity Assessment, and Hallmarking. How can I help you?",
};

const SUGGESTIONS = [
  "What is IS 4082 for stacking of materials?",
  "What standard applies to wind turbine tower design?",
  "How does BIS ISI mark certification work?",
  "What are the requirements for Gold Hallmarking?",
];

function createId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function loadMessages(): ChatMessage[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as ChatMessage[];
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch {
    /* corrupt storage — fall through to a fresh chat */
  }
  return [WELCOME_MESSAGE];
}

/** Messages -> backend history turns (excludes the welcome + error rows). */
function buildHistory(msgs: ChatMessage[]): ChatTurn[] {
  return msgs
    .filter((m) => !m.error && m.id !== WELCOME_ID)
    .map((m) => ({ role: m.role, content: m.content }));
}

function llmStatusPill(health: HealthReport | null): {
  label: string;
  dot: string;
  pulse: boolean;
} {
  if (!health) {
    return { label: "Backend offline", dot: "bg-rose-500", pulse: true };
  }
  if (health.services?.groq?.status === "configured") {
    return { label: "Groq LLM ready", dot: "bg-emerald-500", pulse: false };
  }
  if (health.services?.ollama?.status === "ok") {
    return { label: "Ollama ready", dot: "bg-amber-500", pulse: false };
  }
  return { label: "LLM not configured", dot: "bg-rose-500", pulse: true };
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [storageReady, setStorageReady] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [health, setHealth] = useState<HealthReport | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [openCitation, setOpenCitation] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const llmStatus = llmStatusPill(health);
  const ragReady = Boolean(
    health?.services?.chroma?.status === "ok" &&
      (health.services.chroma.vectors ?? 0) > 0
  );

  // Restore saved conversation after mount so SSR HTML matches the first
  // client render (localStorage is unavailable on the server).
  useEffect(() => {
    setMessages(loadMessages());
    setStorageReady(true);
  }, []);

  // Auto-scroll to the latest message.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Persist conversation across reloads — skip until storage has been read
  // so we never overwrite a saved chat with the default welcome message.
  useEffect(() => {
    if (!storageReady) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch {
      /* storage full / private browsing — degrading gracefully */
    }
  }, [messages, storageReady]);

  // Poll backend health so the status pills stay truthful.
  useEffect(() => {
    let alive = true;
    const check = () =>
      fetchHealth()
        .then((h) => alive && setHealth(h))
        .catch(() => alive && setHealth(null));
    check();
    const timer = setInterval(check, 30000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  const resetChat = useCallback(() => {
    setMessages([WELCOME_MESSAGE]);
    setInput("");
    setOpenCitation(null);
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    textareaRef.current?.focus();
  }, []);

  const sendQuestion = useCallback(
    async (qText: string, appendUser = true) => {
      const q = (qText ?? "").trim();
      if (!q || isLoading) return;

      if (appendUser) {
        setMessages((prev) => [
          ...prev,
          { id: createId("user"), role: "user", content: q },
        ]);
        setInput("");
      }
      setOpenCitation(null);
      setIsLoading(true);

      try {
        const res = await postChatQuestion(q, buildHistory(messages));
        setMessages((prev) => [
          ...prev,
          {
            id: createId("assistant"),
            role: "assistant",
            content: res.response,
            citations: res.citations,
            grounded: res.grounded,
            source: res.source,
          },
        ]);
      } catch (err: unknown) {
        const detail =
          err instanceof Error ? err.message : "Unknown connection error";
        setMessages((prev) => [
          ...prev,
          {
            id: createId("error"),
            role: "assistant",
            content: `⚠️ Could not reach the backend: ${detail}`,
            error: true,
            retryOf: q,
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, messages]
  );

  const copyMessage = useCallback(async (m: ChatMessage) => {
    try {
      await navigator.clipboard.writeText(m.content);
      setCopiedId(m.id);
      setTimeout(() => setCopiedId(null), 1500);
    } catch {
      /* clipboard permission denied — non-blocking */
    }
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    void sendQuestion(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void sendQuestion(input);
    }
  };

  const autoResize = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "0px";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  };

  const citationLabel = (c: Citation) =>
    [c.standard_number, c.clause].filter(Boolean).join(", ") || c.source_file;

  return (
    <div className="flex h-screen flex-col bg-[#FDFBF7] text-slate-800">
      <header className="flex h-14 shrink-0 items-center justify-between gap-3 border-b border-slate-200 bg-white px-4 shadow-sm sm:px-6">
        <Link
          href="/"
          className="flex items-center gap-2 font-display text-lg font-bold text-navy"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded bg-[#FF9933] text-white">
            M
          </span>
          ManakSetu
        </Link>

        <div className="flex items-center gap-2">
          <span
            className={`hidden items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium sm:inline-flex ${
              ragReady
                ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                : "border-amber-200 bg-amber-50 text-amber-700"
            }`}
            title={
              ragReady
                ? `RAG corpus ready (${health?.services?.chroma?.vectors ?? 0} chunks)`
                : "RAG corpus not ready"
            }
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                ragReady ? "bg-emerald-500" : "bg-amber-500"
              }`}
            />
            RAG
          </span>

          <span
            className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-medium text-slate-600"
            title="LLM provider currently powering answers"
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${llmStatus.dot} ${
                llmStatus.pulse ? "animate-pulse" : ""
              }`}
            />
            {llmStatus.label}
          </span>

          <button
            type="button"
            onClick={resetChat}
            className="rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs font-medium text-slate-600 transition hover:border-[#FF9933] hover:text-[#c45c1a]"
          >
            New chat
          </button>

          <Link
            href="/"
            className="text-xs text-slate-500 hover:text-slate-800"
          >
            Home
          </Link>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-4 max-w-4xl mx-auto w-full">
        {messages.map((m) => (
          <div key={m.id} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed shadow-sm md:max-w-[75%] ${
                m.role === "user"
                  ? "rounded-br-none bg-[#FF9933] text-white"
                  : m.error
                    ? "rounded-bl-none border border-red-200 bg-red-50 text-red-800"
                    : "rounded-bl-none border border-slate-200 bg-white"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>

              {!m.error && m.source && m.source !== "unknown" && (
                <p className="mt-1 text-[10px] uppercase tracking-wide text-slate-400">
                  via {m.source}
                </p>
              )}

              {m.role === "assistant" &&
                !m.error &&
                m.grounded === false &&
                (!m.citations || m.citations.length === 0) && (
                  <p className="mt-2 rounded-lg bg-amber-50 px-2.5 py-1.5 text-xs text-amber-800">
                    No grounded information found in the ingested BIS corpus for
                    this question.
                  </p>
                )}

              {m.citations && m.citations.length > 0 && (
                <div className="mt-3 space-y-1.5">
                  <p className="text-[11px] font-bold uppercase tracking-wider text-teal">
                    📚 Citations ({m.citations.length}) · grounded ✓
                  </p>
                  {m.citations.map((c, i) => {
                    const key = `${m.id}-${i}`;
                    const open = openCitation === key;
                    return (
                      <div
                        key={key}
                        className="overflow-hidden rounded-xl border border-slate-200 bg-slate-50/80 text-xs text-slate-600"
                      >
                        <button
                          type="button"
                          onClick={() => setOpenCitation(open ? null : key)}
                          className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left"
                        >
                          <span className="truncate font-mono text-xs">
                            📄 {citationLabel(c)}
                          </span>
                          <span className="shrink-0 text-slate-400">
                            {open ? "▾" : "▸"}
                          </span>
                        </button>
                        {open && (
                          <div className="space-y-1.5 border-t border-slate-200 px-3 py-2">
                            <p className="text-xs leading-relaxed">
                              {c.snippet}
                            </p>
                            <p className="text-[11px] text-slate-500">
                              {c.source_file}
                              {c.page_number != null
                                ? ` · page ${c.page_number}`
                                : ""}
                            </p>
                            {c.source_url && (
                              <a
                                href={c.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex text-xs font-semibold text-[#c45c1a] hover:underline"
                              >
                                Open BIS source ↗
                              </a>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {!m.error && (
                <button
                  type="button"
                  onClick={() => void copyMessage(m)}
                  className="mt-2 text-[11px] text-slate-400 transition hover:text-slate-700"
                >
                  {copiedId === m.id ? "✓ Copied" : "⧉ Copy answer"}
                </button>
              )}

              {m.error && m.retryOf && (
                <button
                  type="button"
                  onClick={() => void sendQuestion(m.retryOf!, false)}
                  disabled={isLoading}
                  className="mt-2 rounded-lg border border-red-200 bg-white px-3 py-1.5 text-xs font-semibold text-red-700 transition hover:bg-red-100 disabled:opacity-50"
                >
                  ↻ Retry
                </button>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-2xl rounded-bl-none border border-slate-200 bg-white px-4 py-3 shadow-sm">
              <span className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <span
                    key={i}
                    className="pulse-dot h-1.5 w-1.5 rounded-full bg-slate-400"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </span>
              <span className="text-xs text-slate-500">
                Searching Indian Standards…
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {messages.length === 1 && !isLoading && (
        <div className="mx-auto grid w-full max-w-4xl grid-cols-1 gap-2 px-4 pb-2 sm:grid-cols-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => void sendQuestion(s)}
              className="rounded-lg border border-slate-200 bg-white p-2 text-left text-xs text-slate-700 transition hover:bg-orange-50/70"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      <footer className="border-t border-slate-200 bg-white p-4">
        <form
          onSubmit={handleSubmit}
          className="mx-auto flex max-w-4xl items-end gap-2"
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              autoResize();
            }}
            onKeyDown={handleKeyDown}
            placeholder="Ask about Indian Standards (e.g. IS 4082)… (Enter to send, Shift+Enter for newline)"
            disabled={isLoading}
            className="max-h-[160px] min-h-[46px] flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-[#FF9933] disabled:opacity-60"
          />
          <DocumentAttachment />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="rounded-xl bg-[#000080] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#000066] disabled:opacity-50"
          >
            Send ↵
          </button>
        </form>
      </footer>
    </div>
  );
}

