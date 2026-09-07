const FEATURES = [
  {
    kicker: "01",
    title: "Find the right IS code",
    body: "Describe the product in plain language. Retrieval looks through indexed BIS documents and returns the matching standard — with the clause, not a guess.",
  },
  {
    kicker: "02",
    title: "Certification, demystified",
    body: "ISI mark, hallmarking, CRS, FMCS. What to file, which lab, how long it typically takes — pulled from official process guides.",
  },
  {
    kicker: "03",
    title: "Cited, or silent",
    body: "If the index has nothing relevant, ManakSetu says so. Every factual sentence carries a source card you can open.",
  },
  {
    kicker: "04",
    title: "Built for follow-ups",
    body: "Ask “what documents for that?” and it remembers the standard from the last turn. Multi-turn, MSME-speed.",
  },
];

export function Features() {
  return (
    <section id="standards" className="relative px-5 py-20 sm:px-8 sm:py-28">
      <div className="mx-auto max-w-6xl">
        <div className="max-w-xl">
          <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-saffron-deep">
            What it does
          </p>
          <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-navy sm:text-4xl">
            A compliance officer that fits in a browser tab.
          </h2>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-2">
          {FEATURES.map((f) => (
            <article
              key={f.kicker}
              className="lift group rounded-2xl border border-line bg-white/50 p-6 sm:p-7"
            >
              <span className="font-mono text-[11px] text-mist transition-colors duration-300 group-hover:text-saffron">
                {f.kicker}
              </span>
              <h3 className="mt-3 font-display text-xl font-semibold text-navy">
                {f.title}
              </h3>
              <p className="mt-2 text-[14.5px] leading-relaxed text-ink/70">{f.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
