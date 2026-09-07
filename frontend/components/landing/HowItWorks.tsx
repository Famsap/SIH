const STEPS = [
  {
    n: "01",
    title: "You ask, in English or Hinglish",
    body: "“What standard applies to packaged drinking water?” No IS-number required.",
  },
  {
    n: "02",
    title: "We retrieve, not recall",
    body: "The question is embedded locally and matched against a vector index of BIS PDFs and process guides.",
  },
  {
    n: "03",
    title: "A grounded answer, with sources",
    body: "The model may only speak from retrieved clauses. Weak matches are refused. Citations render as cards.",
  },
];

export function HowItWorks() {
  return (
    <section id="how" className="relative overflow-hidden bg-navy px-5 py-20 text-paper sm:px-8 sm:py-28">
      <div className="orb -right-20 top-10 h-72 w-72 bg-teal/30" />
      <div className="orb -left-16 bottom-0 h-64 w-64 bg-saffron/20" />

      <div className="relative mx-auto max-w-6xl">
        <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-gold">
          How it works
        </p>
        <h2 className="mt-3 max-w-xl font-display text-3xl font-semibold tracking-tight sm:text-4xl">
          Retrieval first. Generation second. Hallucination never.
        </h2>

        <ol className="mt-14 grid gap-6 md:grid-cols-3">
          {STEPS.map((s) => (
            <li
              key={s.n}
              className="lift group rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
            >
              <span className="font-display text-3xl font-semibold text-saffron transition-transform duration-300 group-hover:translate-x-1">
                {s.n}
              </span>
              <h3 className="mt-4 font-display text-xl font-semibold">{s.title}</h3>
              <p className="mt-2 text-[14.5px] leading-relaxed text-paper/70">{s.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
