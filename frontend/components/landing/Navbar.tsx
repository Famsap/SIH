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
        className={`mx-auto flex h-16 max-w-6xl items-center justify-between rounded-2xl px-4 sm:px-6 transition-all duration-500 ${
          scrolled
            ? "border border-line/60 bg-paper/85 shadow-[0_12px_40px_-15px_rgba(7,21,37,0.25)] backdrop-blur-xl"
            : "border border-transparent bg-white/40 backdrop-blur-md shadow-sm"
        }`}
      >
        <Logo />

        <nav className="hidden items-center gap-1 rounded-full border border-line/40 bg-white/60 p-1 backdrop-blur-md md:flex">
          {LINKS.map((link) => {
            const isActive = activeSection === link.href;
            return (
              <a
                key={link.href}
                href={link.href}
                className={`relative rounded-full px-4 py-1.5 text-xs font-semibold tracking-wide transition-all duration-200 ${
                  isActive
                    ? "bg-navy text-white shadow-sm"
                    : "text-ink/70 hover:text-navy hover:bg-navy/5"
                }`}
              >
                {link.label}
              </a>
            );
          })}
        </nav>

        <div className="flex items-center gap-2.5">
          <span className="hidden items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-[11px] font-medium text-emerald-700 lg:flex">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            BIS Grounded
          </span>

          <Link
            href="/login"
            className="rounded-full px-3.5 py-1.5 text-xs font-semibold text-ink/80 transition hover:bg-navy/5 hover:text-navy"
          >
            Sign in
          </Link>

          <Link
            href="/chat"
            className="btn-primary hidden rounded-full px-4 py-2 text-xs font-bold text-white sm:inline-flex items-center gap-1 shadow-md hover:shadow-lg"
          >
            <span>Open assistant</span>
          </Link>

          <button
            type="button"
            aria-label="Toggle menu"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
            className="grid h-9 w-9 place-items-center rounded-xl border border-line/60 bg-white/80 text-navy md:hidden hover:bg-white transition"
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

