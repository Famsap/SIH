export function Logo({ inverted = false }: { inverted?: boolean }) {
  return (
    <a href="#top" className="group flex items-center gap-2.5">
      <span
        className={`relative grid h-9 w-9 place-items-center overflow-hidden rounded-lg transition-transform duration-300 group-hover:rotate-6 group-hover:scale-105 ${
          inverted ? "bg-white/10 ring-1 ring-white/15" : "bg-navy"
        }`}
      >
        <span className="absolute inset-0 bg-[conic-gradient(from_210deg,#e07a2f_0deg,#c9a227_120deg,#1a7a74_240deg,#e07a2f_360deg)] opacity-90" />
        <span
          className={`relative font-display text-[15px] font-semibold leading-none ${
            inverted ? "text-white" : "text-paper"
          }`}
        >
          म
        </span>
      </span>
      <span className="flex flex-col leading-none">
        <span
          className={`font-display text-[17px] font-semibold tracking-tight ${
            inverted ? "text-white" : "text-navy"
          }`}
        >
          ManakSetu
        </span>
        <span
          className={`mt-0.5 text-[10px] font-medium uppercase tracking-[0.18em] ${
            inverted ? "text-white/55" : "text-mist"
          }`}
        >
          BIS · IS codes
        </span>
      </span>
    </a>
  );
}
