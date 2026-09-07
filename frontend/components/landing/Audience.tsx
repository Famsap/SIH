const PEOPLE = [
  {
    role: "MSME manufacturers",
    need: "Which mark, which lab, which form — without a consultant on retainer.",
  },
  {
    role: "Exporters & importers",
    need: "Confirm the IS code a buyer named, and whether CRS applies before the shipment.",
  },
  {
    role: "QC / compliance",
    need: "Jump to the clause, not the 80-page PDF. Keep a trail of cited answers.",
  },
  {
    role: "Students & consultants",
    need: "A faster way into the standards corpus, with the source still attached.",
  },
];

export function Audience() {
  return (
    <section id="who" className="px-5 py-20 sm:px-8 sm:py-28">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="max-w-xl">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-saffron-deep">
              Who it's for
            </p>
            <h2 className="mt-3 font-display text-3xl font-semibold tracking-tight text-navy sm:text-4xl">
              Built for the people who actually have to comply.
            </h2>
          </div>
          <p className="max-w-sm text-sm leading-relaxed text-ink/60">
            BIS already published the rules. We make them askable.
          </p>
        </div>

        <ul className="mt-12 divide-y divide-line border-y border-line">
          {PEOPLE.map((p) => (
            <li
              key={p.role}
              className="group grid gap-2 py-6 transition-colors duration-300 hover:bg-white/40 sm:grid-cols-[280px_1fr] sm:items-baseline sm:gap-10 sm:px-3"
            >
              <h3 className="font-display text-lg font-semibold text-navy transition-transform duration-300 group-hover:translate-x-1">
                {p.role}
              </h3>
              <p className="text-[14.5px] leading-relaxed text-ink/70">{p.need}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
