"use client";

import { useEffect, useRef } from "react";

/**
 * 3D scroll stage — documents tilt, recede, and rotate as the user scrolls.
 * Pure CSS 3D + rAF. Honours prefers-reduced-motion.
 */
export function ScrollStage() {
  const stageRef = useRef<HTMLDivElement>(null);
  const stackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stage = stageRef.current;
    const stack = stackRef.current;
    if (!stage || !stack) return;

    const cards = Array.from(stack.querySelectorAll<HTMLElement>("[data-card]"));
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) return;

    let raf = 0;
    const onScroll = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const rect = stage.getBoundingClientRect();
        const vh = window.innerHeight;
        // 0 when the stage enters, 1 when it leaves
        const progress = Math.min(
          1,
          Math.max(0, (vh * 0.85 - rect.top) / (rect.height + vh * 0.4)),
        );

        stack.style.transform = `rotateX(${18 - progress * 26}deg) rotateY(${
          -22 + progress * 38
        }deg) rotateZ(${progress * -4}deg) translateZ(${progress * 80}px)`;

        cards.forEach((card, i) => {
          const dir = i % 2 === 0 ? 1 : -1;
          const depth = (i - 1) * 70;
          const y = (i - 1) * 18 - progress * 40;
          const rot = dir * (8 - progress * 14);
          card.style.transform = `translate3d(${dir * (30 - progress * 48)}px, ${y}px, ${
            depth + progress * 40
          }px) rotateY(${rot}deg)`;
        });
      });
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <div
      ref={stageRef}
      className="perspective relative mx-auto h-[420px] w-full max-w-[560px] sm:h-[500px]"
    >
      <div
        ref={stackRef}
        className="preserve-3d absolute inset-0 flex items-center justify-center transition-transform duration-75"
        style={{ transform: "rotateX(18deg) rotateY(-22deg)" }}
      >
        <DocCard
          index={0}
          stamp="IS 14543"
          title="Packaged Drinking Water"
          clause="4.2 · Microbiological limits"
          body="Coliforms shall be absent in 250 ml. Test as per IS 15185."
          offset="-translate-x-8 -translate-y-6"
        />
        <DocCard
          index={1}
          stamp="CRS"
          title="LED Lamps — Compulsory Registration"
          clause="Scheme II · Series guidelines"
          body="Submit test reports from a BIS-recognised lab. Factory inspection follows grant."
          offset="translate-y-4"
          featured
        />
        <DocCard
          index={2}
          stamp="IS 1786"
          title="High Strength Deformed Steel"
          clause="6.3 · Chemical composition"
          body="Maximum phosphorus 0.040%. Heat analysis to be furnished with each cast."
          offset="translate-x-10 -translate-y-2"
        />
      </div>
    </div>
  );
}

function DocCard({
  stamp,
  title,
  clause,
  body,
  offset,
  featured,
  index,
}: {
  stamp: string;
  title: string;
  clause: string;
  body: string;
  offset: string;
  featured?: boolean;
  index: number;
}) {
  return (
    <article
      data-card
      className={`doc-edge preserve-3d absolute w-[230px] rounded-xl p-5 sm:w-[260px] ${offset} ${
        featured ? "z-20 scale-105" : "z-10"
      }`}
      style={{ transform: `translateZ(${(index - 1) * 70}px)` }}
    >
      <div className="mb-4 flex items-center justify-between">
        <span className="rounded-full bg-navy px-2.5 py-0.5 font-mono text-[10px] font-medium tracking-wider text-paper">
          {stamp}
        </span>
        <span className="h-2 w-2 rounded-full bg-saffron/80" />
      </div>
      <h3 className="font-display text-[17px] font-semibold leading-snug text-navy">
        {title}
      </h3>
      <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.14em] text-teal">
        {clause}
      </p>
      <p className="mt-3 text-[12.5px] leading-relaxed text-ink/70">{body}</p>
      <div className="mt-4 h-px w-full bg-line" />
      <p className="mt-3 text-[10px] uppercase tracking-[0.16em] text-mist">
        Bureau of Indian Standards
      </p>
    </article>
  );
}
