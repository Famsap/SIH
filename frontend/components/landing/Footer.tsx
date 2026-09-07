import { Logo } from "./Logo";

export function Footer() {
  return (
    <footer className="bg-navy px-5 py-12 text-paper sm:px-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <Logo inverted />
          <p className="mt-4 max-w-sm text-[13px] leading-relaxed text-paper/60">
            An AI-powered assistant for Indian Standards and BIS services.
            Built for Smart India Hackathon 2026 · problem SIH26107.
          </p>
        </div>
        <div className="flex flex-col items-start gap-2 text-[12px] text-paper/50 sm:items-end">
          <p>Not affiliated with the Bureau of Indian Standards.</p>
          <p>Answers are retrieved from public BIS documents and cited.</p>
          <p className="mt-2 font-mono uppercase tracking-[0.18em] text-gold/80">
            मानक सेतु
          </p>
        </div>
      </div>
    </footer>
  );
}
