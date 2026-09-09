"use client";

import Link from "next/link";
import { useState } from "react";

const FAQS = [
  "Which IS code applies to my product?",
  "How does BIS certification work?",
  "Where can I find the latest BIS updates?",
];

export function FaqBubble() {
  const [open, setOpen] = useState(false);

  return (
    <div className="fixed bottom-5 right-5 z-40 sm:bottom-7 sm:right-7">
      {open && (
        <div className="mb-3 w-[min(320px,calc(100vw-2.5rem))] overflow-hidden rounded-2xl border border-line bg-paper/95 shadow-[0_18px_50px_-18px_rgba(7,21,37,0.4)] backdrop-blur-xl">
          <div className="bg-navy px-5 py-4 text-paper">
            <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-gold">Quick BIS FAQ</p>
            <p className="mt-1 font-display text-xl">What can we help with?</p>
          </div>
          <div className="p-3">
            {FAQS.map((question) => (
              <Link
                key={question}
                href={`/chat?q=${encodeURIComponent(question)}`}
                onClick={() => setOpen(false)}
                className="block rounded-xl px-3 py-2.5 text-xs leading-relaxed text-ink/75 transition hover:bg-saffron/10 hover:text-navy"
              >
                {question}
              </Link>
            ))}
            <div className="mt-2 flex gap-2 border-t border-line pt-3">
              <Link href="/helpline" onClick={() => setOpen(false)} className="flex-1 rounded-lg bg-saffron px-2 py-2 text-center text-[11px] font-bold text-white hover:bg-saffron-deep">
                BIS helpline
              </Link>
              <a href="https://www.bis.gov.in/" target="_blank" rel="noreferrer" onClick={() => setOpen(false)} className="flex-1 rounded-lg border border-line px-2 py-2 text-center text-[11px] font-bold text-navy hover:bg-navy/5">
                Official BIS site
              </a>
            </div>
          </div>
        </div>
      )}
      <button
        type="button"
        aria-label={open ? "Close FAQ" : "Open BIS FAQ"}
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        className="grid h-14 w-14 place-items-center rounded-full bg-saffron text-2xl font-semibold text-white shadow-[0_12px_28px_-8px_rgba(196,92,26,0.8)] transition hover:-translate-y-1 hover:bg-saffron-deep focus:outline-none focus:ring-4 focus:ring-saffron/25"
      >
        <span aria-hidden>{open ? "×" : "?"}</span>
      </button>
    </div>
  );
}