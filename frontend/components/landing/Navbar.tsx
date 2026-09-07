"use client";

import { useEffect, useState } from "react";
import { Logo } from "./Logo";

const LINKS = [
  { href: "#standards", label: "Standards" },
  { href: "#how", label: "How it works" },
  { href: "#who", label: "Who it's for" },
  { href: "#ask", label: "Try a question" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-40 transition-all duration-500 ${
        scrolled
          ? "border-b border-line bg-paper/80 shadow-[0_8px_30px_-18px_rgba(7,21,37,0.35)] backdrop-blur-xl"
          : "bg-transparent"
      }`}
    >
      <div className="mx-auto flex h-[72px] max-w-6xl items-center justify-between px-5 sm:px-8">
        <Logo />

        <nav className="hidden items-center gap-8 md:flex">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="nav-link text-[13px] font-medium tracking-wide text-ink/70 hover:text-navy"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <a
            href="/chat"
            className="btn-primary hidden rounded-full px-4 py-2 text-[13px] font-semibold text-white sm:inline-flex"
          >
            Open assistant
          </a>
          <button
            type="button"
            aria-label="Toggle menu"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
            className="grid h-10 w-10 place-items-center rounded-full border border-line bg-white/60 md:hidden"
          >
            <span className="flex w-4 flex-col gap-1.5">
              <span
                className={`h-px w-full bg-navy transition-transform duration-300 ${
                  open ? "translate-y-[4px] rotate-45" : ""
                }`}
              />
              <span
                className={`h-px w-full bg-navy transition-transform duration-300 ${
                  open ? "-translate-y-[3px] -rotate-45" : ""
                }`}
              />
            </span>
          </button>
        </div>
      </div>

      <div
        className={`overflow-hidden border-t border-line bg-paper/95 backdrop-blur-xl transition-[max-height,opacity] duration-400 md:hidden ${
          open ? "max-h-80 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <nav className="flex flex-col gap-1 px-5 py-4">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="rounded-lg px-3 py-2.5 text-sm font-medium text-ink/80 hover:bg-navy/5 hover:text-navy"
            >
              {link.label}
            </a>
          ))}
          <a
            href="/chat"
            onClick={() => setOpen(false)}
            className="btn-primary mt-2 rounded-full px-4 py-2.5 text-center text-sm font-semibold text-white"
          >
            Open assistant
          </a>
        </nav>
      </div>
    </header>
  );
}
