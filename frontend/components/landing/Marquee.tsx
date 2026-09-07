const ITEMS = [
  "IS 14543 Packaged Drinking Water",
  "ISI Mark · Product Certification",
  "CRS · Compulsory Registration",
  "Hallmarking · Gold & Silver",
  "IS 1786 TMT Bars",
  "IS 16046 Lithium Cells",
  "FMCS · Foreign Manufacturers",
  "IS 302 Household Appliances",
  "ECO Mark",
  "IS 13428 Packaged Natural Mineral Water",
];

export function Marquee() {
  const row = [...ITEMS, ...ITEMS];
  return (
    <div className="relative overflow-hidden border-y border-line bg-navy py-3.5">
      <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-16 bg-gradient-to-r from-navy to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-16 bg-gradient-to-l from-navy to-transparent" />
      <div className="marquee flex w-max gap-10">
        {row.map((item, i) => (
          <span
            key={`${item}-${i}`}
            className="flex items-center gap-10 whitespace-nowrap font-mono text-[11px] uppercase tracking-[0.22em] text-paper/80"
          >
            {item}
            <span className="h-1 w-1 rounded-full bg-saffron" />
          </span>
        ))}
      </div>
    </div>
  );
}
