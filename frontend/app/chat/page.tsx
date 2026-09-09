"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { postChatQuestion, ChatMessage } from "@/lib/api";

const SUGGESTIONS = [
  "What is IS 4082 for stacking of materials?",
  "What standard applies to wind turbine tower design?",
  "How does BIS ISI mark certification work?",
  "What are the requirements for Gold Hallmarking?",
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "w-1",
      role: "assistant",
      content:
        "Namaste! I am ManakSetu (मानकसेतु), your AI assistant for Indian Standards (IS Codes), BIS Conformity Assessment, and Hallmarking. How can I help you?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async (qText?: string) => {
    const q = (qText || input).trim();
    if (!q || isLoading) return;

    setMessages((p) => [...p, { id: `u-${Date.now()}`, role: "user", content: q }]);
    setInput("");
    setIsLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await postChatQuestion(q, history);
      setMessages((p) => [
        ...p,
        { id: `a-${Date.now()}`, role: "assistant", content: res.response, citations: res.citations, grounded: res.grounded },
      ]);
    } catch (err: any) {
      setMessages((p) => [
        ...p,
        { id: `err-${Date.now()}`, role: "assistant", content: `⚠️ Failed to connect to backend (${err.message}).` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen flex-col bg-[#FDFBF7] text-slate-800">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6 shadow-sm">
        <Link href="/" className="flex items-center gap-2 font-display font-bold text-navy text-lg">
          <span className="flex h-8 w-8 items-center justify-center rounded bg-[#FF9933] text-white">M</span>
          ManakSetu
        </Link>
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 text-xs text-emerald-700 font-medium">
            ● RAG Grounded
          </span>
          <Link href="/" className="text-xs text-slate-500 hover:text-slate-800">Home</Link>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-4 max-w-4xl mx-auto w-full">
        {messages.map((m) => (
          <div key={m.id} className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-2xl p-4 text-sm leading-relaxed ${m.role === "user" ? "bg-[#FF9933] text-white rounded-br-none" : "bg-white border border-slate-200 rounded-bl-none shadow-sm"}`}>
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.citations && m.citations.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-100 flex flex-wrap gap-1">
                  {m.citations.map((c, i) => (
                    <span key={i} className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600 font-mono" title={c.snippet}>
                      📄 {c.standard_number && c.clause ? `${c.standard_number}, ${c.clause}` : c.source_file}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && <div className="text-xs text-slate-400 animate-pulse">Retrieving Indian Standards...</div>}
        <div ref={bottomRef} />
      </div>

      {messages.length === 1 && (
        <div className="max-w-4xl mx-auto w-full px-4 pb-2 grid grid-cols-1 sm:grid-cols-2 gap-2">
          {SUGGESTIONS.map((s, i) => (
            <button key={i} onClick={() => handleSend(s)} className="text-left rounded-lg border border-slate-200 bg-white p-2 text-xs text-slate-700 hover:bg-orange-50/50">
              {s}
            </button>
          ))}
        </div>
      )}

      <footer className="border-t border-slate-200 bg-white p-4">
        <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="max-w-4xl mx-auto flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about Indian Standards (e.g. IS 4082)..."
            className="flex-1 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm focus:outline-none focus:ring-1 focus:ring-[#FF9933]"
            disabled={isLoading}
          />
          <button type="submit" disabled={!input.trim() || isLoading} className="rounded-xl bg-[#000080] px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-50">
            Send
          </button>
        </form>
      </footer>
    </div>
  );
}

