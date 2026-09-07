const PROMPTS = [
  "What standard applies to packaged drinking water?",
  "How do I get an ISI mark for LED bulbs?",
  "Documents required for CRS registration of a laptop?",
  "Is hallmarking mandatory for silver jewellery?",
];

export function AskPreview() {
  return (
    <section id="ask" className="px-5 pb-20 sm:px-8 sm:pb-28">
      <div className="relative mx-auto max-w-6xl overflow-hidden rounded-[28px] border border-line bg-white/60 p-6 sm:p-10">
        <div className="orb -right-10 -top-10 h-56 w-56 bg-saffron/20" />
        <div className="relative grid items-center gap-10 lg:grid-cols-[1fr_1.05fr]">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-saffron-deep">
              Try it
            </p>
            <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-navy sm:text-[40px]">
              Start with a question you would have called the helpline for.
            </h2>
            <p className="mt-3 max-w-md text-[15px] leading-relaxed text-ink/70">
              The assistant is grounded in indexed BIS documents. If we don’t
              have the page, we will say so — we will not invent an IS number.
            </p>
            <a
              href="/chat"
              className="btn-primary mt-7 inline-flex rounded-full px-6 py-3 text-[14px] font-semibold text-white"
            >
              Open the assistant
            </a>
          </div>

          <ul className="flex flex-col gap-3">
            {PROMPTS.map((q) => (
              <li key={q}>
                <a
                  href={`/chat?q=${encodeURIComponent(q)}`}
                  className="lift flex items-center justify-between gap-4 rounded-2xl border border-line bg-paper/80 px-4 py-3.5 text-left"
                >
                  <span className="text-[14px] text-ink/80">{q}</span>
                  <span className="shrink-0 font-mono text-[11px] uppercase tracking-widest text-saffron-deep">
                    Ask →
                  </span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
