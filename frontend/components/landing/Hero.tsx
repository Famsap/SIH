import { ScrollStage } from "./ScrollStage";

export function Hero() {
  return (
    <section
      id="top"
      className="relative overflow-hidden px-5 pb-20 pt-28 sm:px-8 sm:pb-28 sm:pt-36"
    >
      <div className="orb -left-24 top-10 h-72 w-72 bg-saffron/25" />
      <div className="orb right-[-80px] top-40 h-80 w-80 bg-teal/20" />
      <div className="orb bottom-0 left-1/3 h-56 w-56 bg-gold/20" />

      <div className="relative mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:gap-8">
        <div>
          <p className="inline-flex items-center gap-2 rounded-full border border-line bg-white/50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-navy/70 backdrop-blur-sm">
            <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-teal" />
            Smart India Hackathon · SIH26107
          </p>

          <h1 className="mt-6 max-w-xl font-display text-[42px] font-semibold leading-[1.08] tracking-tight text-navy sm:text-[56px] lg:text-[62px]">
            Indian Standards,
            <span className="italic text-saffron-deep"> without the PDF hunt.</span>
          </h1>

          <p className="mt-5 max-w-lg text-[16px] leading-relaxed text-ink/70 sm:text-[17.5px]">
            ManakSetu is an AI assistant for BIS. Ask which IS code applies, how
            ISI marking or CRS works, and what to file — answers are retrieved
            from official text and cited, never invented.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
            <a
              href="/chat"
              className="btn-primary inline-flex items-center justify-center rounded-full px-6 py-3 text-[14px] font-semibold text-white"
            >
              Ask a question
              <ArrowIcon />
            </a>
            <a
              href="#how"
              className="btn-ghost inline-flex items-center justify-center rounded-full border border-line bg-white/40 px-6 py-3 text-[14px] font-semibold text-navy"
            >
              See how it works
            </a>
          </div>

          <dl className="mt-10 grid max-w-md grid-cols-3 gap-4 border-t border-line pt-6">
            {[
              ["20,000+", "IS codes in scope"],
              ["Cited", "every answer"],
              ["MSME", "first design"],
            ].map(([k, v]) => (
              <div key={k}>
                <dt className="font-display text-xl font-semibold text-navy sm:text-2xl">
                  {k}
                </dt>
                <dd className="mt-0.5 text-[11px] leading-snug text-mist">{v}</dd>
              </div>
            ))}
          </dl>
        </div>

        <ScrollStage />
      </div>
    </section>
  );
}

function ArrowIcon() {
  return (
    <svg
      className="ml-2 h-4 w-4 transition-transform duration-300 group-hover:translate-x-0.5"
      viewBox="0 0 16 16"
      fill="none"
      aria-hidden
    >
      <path
        d="M3 8h10M9 4l4 4-4 4"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
