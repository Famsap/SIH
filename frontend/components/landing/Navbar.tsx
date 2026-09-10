"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Logo } from "./Logo";

const LINKS = [
  { href: "#standards", label: "Standards" },
  { href: "#how", label: "How it works" },
  { href: "#who", label: "Who it is for" },
  { href: "#ask", label: "Try a question" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 20);
      const sections = LINKS.map((l) => l.href.substring(1));
      for (const section of sections.reverse()) {
        const el = document.getElementById(section);
        if (el && window.scrollY >= el.offsetTop - 120) {
          setActiveSection("#" + section);
          break;
        }
      }
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className="fixed inset-x-0 top-0 z-50 px-4 pt-4 sm:px-6 lg:px-8 animate-nav-drop">
      <div
        className={`relative mx-auto flex items-center justify-between overflow-hidden rounded-2xl border px-3 transition-all duration-500 sm:px-4 ${
          scrolled
            ? "h-14 border-white/15 bg-navy/[0.96] shadow-[0_24px_60px_-20px_rgba(7,21,37,0.7)] backdrop-blur-2xl sm:h-16"
            : "h-16 border-white/10 bg-navy/[0.88] shadow-[0_12px_36px_-16px_rgba(7,21,37,0.55)] backdrop-blur-xl sm:h-[72px]"
        }`}
      >
        <span
          aria-hidden
          className="pointer-events-none absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-white/25 to-transparent"
        />
        <span
          aria-hidden
          className="pointer-events-none absolute -bottom-10 left-1/2 h-20 w-2/3 -translate-x-1/2 rounded-full bg-saffron/20 blur-3xl"
        />
        <div className="relative flex items-center gap-3">
          <Logo inverted />
          <span className="hidden h-8 w-px bg-white/15 sm:block" />
          <span className="hidden max-w-[86px] font-mono text-[9px] uppercase leading-tight tracking-[0.16em] text-white/40 sm:block">
            Public knowledge, clearly explained
          </span>
        </div>

        <nav className="hidden items-center gap-1 md:flex">
          {LINKS.map((link, index) => {
            const isActive = activeSection === link.href;
            return (
              <a
                key={link.href}
                href={link.href}
                className={`nav-link group relative flex items-center gap-1.5 rounded-lg px-3 py-2 text-[11px] font-semibold tracking-[0.06em] transition-all duration-200 ${
                  isActive
                    ? "bg-white/[0.08] text-white ring-1 ring-inset ring-white/10"
                    : "text-white/55 hover:bg-white/[0.05] hover:text-white"
                }`}
              >
                <span
                  className={`font-mono text-[9px] transition-colors duration-200 ${
                    isActive
                      ? "text-saffron"
                      : "text-white/30 group-hover:text-saffron"
                  }`}
                >
                  0{index + 1}
                </span>
                {link.label}
              </a>
            );
          })}
        </nav>
        <div className="relative flex items-center gap-1.5 sm:gap-2.5">
          <span className="hidden items-center gap-2 rounded-lg border border-white/10 bg-white/[0.04] px-2.5 py-2 text-[9px] font-bold uppercase tracking-[0.12em] text-white/55 lg:flex">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-teal/50" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-teal ring-2 ring-teal/20" />
            </span>
            Live index
          </span>

          <Link
            href="/login"
            className="hidden rounded-lg px-3 py-2 text-[11px] font-semibold text-white/65 transition hover:bg-white/10 hover:text-white sm:inline-flex"
          >
            Sign in
          </Link>

          <Link
            href="/helpline"
            className="hidden rounded-lg px-3 py-2 text-[11px] font-semibold text-white/65 transition hover:bg-white/10 hover:text-white lg:inline-flex"
          >
            BIS helpline
          </Link>

          <Link
            href="/chat"
            className="btn-primary btn-shine hidden items-center gap-1.5 rounded-lg px-4 py-2.5 text-[11px] font-bold text-white shadow-md transition hover:shadow-lg sm:inline-flex"
          >
            <span>Open assistant</span>
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden>
              <path d="M2 6h7M6 2.5 9.5 6 6 9.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </Link>
          <button
            type="button"
            aria-label="Toggle menu"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
            className="grid h-11 w-11 place-items-center rounded-xl border border-white/15 bg-white/[0.06] text-white transition hover:bg-white/15 md:hidden"
          >
            <span className="flex w-4 flex-col gap-1">
              <span
                className={`h-[1.5px] w-full rounded bg-white transition-transform duration-300 ${
                  open ? "translate-y-[5.5px] rotate-45" : ""
                }`}
              />
              <span
                className={`h-[1.5px] w-full rounded bg-white transition-opacity duration-300 ${
                  open ? "opacity-0" : ""
                }`}
              />
              <span
                className={`h-[1.5px] w-full rounded bg-white transition-transform duration-300 ${
                  open ? "-translate-y-[6.5px] -rotate-45" : ""
                }`}
              />
            </span>
          </button>
        </div>
      </div>
      <div
        className={`mx-auto mt-2 max-w-6xl overflow-hidden rounded-2xl border border-white/10 bg-navy/[0.96] shadow-[0_24px_60px_-24px_rgba(7,21,37,0.8)] backdrop-blur-2xl transition-all duration-300 md:hidden ${
          open
            ? "max-h-[440px] opacity-100 p-3"
            : "max-h-0 border-transparent p-0 opacity-0"
        }`}
      >
        <nav className="flex flex-col gap-1">
          {LINKS.map((link, index) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className={`flex items-center gap-2.5 rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-colors duration-300 ${
                activeSection === link.href
                  ? "bg-white/[0.08] text-white"
                  : "text-white/70 hover:bg-white/[0.06] hover:text-white"
              }`}
              style={{ transitionDelay: 30 * index + "ms" }}
            >
              <span className="font-mono text-[9px] text-saffron">0{index + 1}</span>
              {link.label}
            </a>
          ))}
          <div className="my-2 border-t border-white/10" />
          <div className="grid grid-cols-2 gap-1.5">
            <Link
              href="/login"
              onClick={() => setOpen(false)}
              className="rounded-xl border border-white/10 px-3.5 py-2.5 text-sm font-semibold text-white/70 transition hover:bg-white/[0.06] hover:text-white"
            >
              Sign in
            </Link>
            <Link
              href="/helpline"
              onClick={() => setOpen(false)}
              className="rounded-xl border border-white/10 px-3.5 py-2.5 text-sm font-semibold text-white/70 transition hover:bg-white/[0.06] hover:text-white"
            >
              Helpline
            </Link>
          </div>
          <Link
            href="/chat"
            onClick={() => setOpen(false)}
            className="btn-primary mt-1.5 rounded-xl px-4 py-3 text-center text-sm font-bold text-white shadow-md"
          >
            Open assistant →
          </Link>
        </nav>
      </div>
    </header>
  );
}
