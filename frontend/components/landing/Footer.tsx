import Link from "next/link";
import { Logo } from "./Logo";

export function Footer() {
  return (
    <footer className="bg-[#080722] text-paper">
      <div className="border-b border-white/10 bg-white/[0.03] px-5 py-3 sm:px-8">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 text-[11px] uppercase tracking-[0.16em] text-paper/45">
          <span>Official information desk</span>
          <span className="flex items-center gap-2 text-emerald-300/80"><span className="h-1.5 w-1.5 rounded-full bg-emerald-400" /> Public BIS sources</span>
        </div>
      </div>

      <div className="mx-auto grid max-w-6xl gap-12 px-5 py-14 sm:px-8 lg:grid-cols-[1.25fr_1fr_0.8fr]">
        <div>
          <Logo inverted />
          <p className="mt-5 max-w-sm text-[13px] leading-relaxed text-paper/55">
            An AI-powered assistant for Indian Standards, BIS services, and public guidance. Built for Smart India Hackathon 2026 · problem SIH26107.
          </p>
          <Link href="/helpline" className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-gold transition hover:text-white">
            Visit the BIS help desk <span aria-hidden>-&gt;</span>
          </Link>
        </div>

        <div>
          <h2 className="font-display text-xl text-white">Bureau of Indian Standards</h2>
          <address className="mt-5 not-italic text-[13px] leading-relaxed text-paper/60">
            <p className="flex gap-3"><span className="w-5 shrink-0 text-center text-lg text-gold" aria-hidden>⌖</span><span>9 Bahadur Shah Zafar Marg,<br />New Delhi-110002, India</span></p>
            <a href="tel:+911123236236" className="mt-4 flex gap-3 transition hover:text-white"><span className="w-5 shrink-0 text-center text-lg text-gold" aria-hidden>◉</span><span>+91-11-2323 6236</span></a>
            <a href="mailto:helpdesk@bis.gov.in" className="mt-4 flex gap-3 transition hover:text-white"><span className="w-5 shrink-0 text-center text-lg text-gold" aria-hidden>@</span><span>helpdesk@bis.gov.in</span></a>
          </address>
        </div>

        <div>
          <h2 className="font-display text-xl text-white">Quick links</h2>
          <nav className="mt-5 grid gap-3 text-[13px] text-paper/60">
            <Link href="/chat" className="transition hover:text-white">Ask the assistant</Link>
            <Link href="/helpline" className="transition hover:text-white">BIS helpline</Link>
            <a href="https://www.bis.gov.in/standards/" target="_blank" rel="noreferrer" className="transition hover:text-white">Standards</a>
            <a href="https://www.bis.gov.in/consumer-overview/" target="_blank" rel="noreferrer" className="transition hover:text-white">Consumer affairs</a>
          </nav>
        </div>
      </div>

      <div className="border-t border-white/10 px-5 py-5 sm:px-8">
        <div className="mx-auto flex max-w-6xl flex-col gap-5 text-[11px] text-paper/40 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <span>Follow official updates</span>
            <a href="https://www.bis.gov.in/" target="_blank" rel="noreferrer" aria-label="BIS official website" className="grid h-8 w-8 place-items-center rounded-lg bg-white/10 text-xs font-bold text-white transition hover:bg-saffron">BIS</a>
            <a href="https://www.facebook.com/IndianStandards" target="_blank" rel="noreferrer" aria-label="BIS on Facebook" className="grid h-8 w-8 place-items-center rounded-lg bg-white/10 text-sm font-bold text-white transition hover:bg-[#1877F2]">f</a>
            <a href="https://x.com/IndianStandards" target="_blank" rel="noreferrer" aria-label="BIS on X" className="grid h-8 w-8 place-items-center rounded-lg bg-white/10 text-sm font-bold text-white transition hover:bg-black">X</a>
            <a href="https://www.youtube.com/@IndianStandard" target="_blank" rel="noreferrer" aria-label="BIS on YouTube" className="grid h-8 w-8 place-items-center rounded-lg bg-white/10 text-sm font-bold text-white transition hover:bg-[#ff0000]">▶</a>
          </div>
          <div className="flex flex-col gap-1 sm:items-end">
            <span>Not affiliated with the Bureau of Indian Standards.</span>
            <span>Answers are retrieved from public BIS documents and cited.</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
