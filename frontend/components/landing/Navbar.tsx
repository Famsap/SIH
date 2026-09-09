"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Logo } from "./Logo";

const LINKS = [
  { href: "#standards", label: "Standards" },
  { href: "#how", label: "How it works" },
  { href: "#who", label: "Who it's for" },
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
          setActiveSection(`#${section}`);
          break;
        }
      }
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className="fixed inset-x-0 top-0 z-50 px-4 pt-3 sm:px-8 transition-all duration-300">
      <div
        className={`mx-auto flex h-[72px] max-w-6xl items-center justify-between rounded-[18px] px-3 sm:px-4 transition-all duration-500 ${
          scrolled
            ? "border border-navy/80 bg-navy/[0.97] shadow-[0_20px_50px_-18px_rgba(7,21,37,0.5)] backdrop-blur-xl"
            : "border border-white/70 bg-navy/[0.92] shadow-[0_12px_32px_-14px_rgba(7,21,37,0.45)] backdrop-blur-md"
        }`}
      >
        <div className="flex items-center gap-3">
          <Logo inverted />
          <span className="hidden h-8 w-px bg-white/15 sm:block" />
          <span className="hidden max-w-[82px] font-mono text-[9px] uppercase leading-tight tracking-[0.14em] text-white/40 sm:block">
            Public knowledge, clearly explained
          </span>
        </div>

        <nav className="hidden items-center gap-6 md:flex lg:gap-8">
          {LINKS.map((link, index) => {
            const isActive = activeSection === link.href;
            return (
              <a
                key={link.href}
                href={link.href}
                className={`group relative flex items-center gap-1.5 py-2 text-[11px] font-semibold tracking-wide transition-all duration-200 ${
                  isActive
                    ? "text-white"
                    : "text-white/55 hover:text-white"
                }`}
              >
                <span className={`font-mono text-[9px] ${isActive ? "text-saffron" : "text-white/30 group-hover:text-saffron"}`}>0{index + 1}</span>
                {link.label}
                {isActive && <span className="absolute -bottom-1 left-0 h-0.5 w-full bg-saffron" />}
              </a>
            );
          })}
        </nav>

        <div className="flex items-center gap-1.5 sm:gap-2.5">
          <span className="hidden items-center gap-2 rounded-lg border border-white/10 px-2.5 py-2 text-[9px] font-bold uppercase tracking-[0.12em] text-white/55 lg:flex">
            <span className="relative flex h-2 w-2"><span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-teal/50" /><span className="relative inline-flex h-2 w-2 rounded-full bg-teal" /></span>
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
            className="btn-primary hidden rounded-lg px-4 py-2.5 text-[11px] font-bold text-white shadow-md hover:shadow-lg sm:inline-flex items-center gap-1"
          >
            <span>Open assistant</span>
          </Link>

          <button
            type="button"
            aria-label="Toggle menu"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
            className="grid h-10 w-10 place-items-center rounded-xl border border-white/15 bg-white/10 text-white transition hover:bg-white/20 md:hidden"
          >
            <span className="flex w-4 flex-col gap-1">
              <span
                className={`h-0.5 w-full bg-navy transition-transform duration-300 ${
                  open ? "translate-y-[5px] rotate-45" : ""
                }`}
              />
              <span
                className={`h-0.5 w-full bg-navy transition-opacity duration-300 ${
                  open ? "opacity-0" : ""
                }`}
              />
              <span
                className={`h-0.5 w-full bg-navy transition-transform duration-300 ${
                  open ? "-translate-y-[7px] -rotate-45" : ""
                }`}
              />
            </span>
          </button>
        </div>
      </div>

      <div
        className={`mx-auto mt-2 max-w-6xl overflow-hidden rounded-2xl border border-line/60 bg-paper/95 backdrop-blur-xl transition-all duration-300 md:hidden ${
          open ? "max-h-96 opacity-100 p-4 shadow-xl" : "max-h-0 opacity-0 p-0"
        }`}
      >
        <nav className="flex flex-col gap-1.5">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="rounded-xl px-4 py-2.5 text-sm font-semibold text-ink/80 hover:bg-navy/5 hover:text-navy transition"
            >
              {link.label}
            </a>
          ))}
          <div className="my-2 border-t border-line/40" />
          <Link
            href="/login"
            onClick={() => setOpen(false)}
            className="rounded-xl px-4 py-2 text-sm font-semibold text-ink/80 hover:bg-navy/5"
          >
            Sign in
          </Link>
          <Link
            href="/helpline"
            onClick={() => setOpen(false)}
            className="rounded-xl px-4 py-2 text-sm font-semibold text-ink/80 hover:bg-navy/5"
          >
            BIS helpline
          </Link>
          <Link
            href="/chat"
            onClick={() => setOpen(false)}
            className="btn-primary mt-1 rounded-xl px-4 py-2.5 text-center text-sm font-bold text-white shadow-md"
          >
            Open assistant
          </Link>
        </nav>
      </div>
    </header>
  );
}

