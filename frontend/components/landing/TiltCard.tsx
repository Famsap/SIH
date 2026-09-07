"use client";

import { useRef, type ReactNode } from "react";

/** Pointer-tracking 3D tilt. Used on feature / prompt cards. */
export function TiltCard({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);

  const onMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width;
    const y = (e.clientY - r.top) / r.height;
    const rx = (0.5 - y) * 10;
    const ry = (x - 0.5) * 14;
    el.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg) translateZ(8px)`;
  };

  const onLeave = () => {
    const el = ref.current;
    if (!el) return;
    el.style.transform = "rotateX(0deg) rotateY(0deg) translateZ(0)";
  };

  return (
    <div className="perspective h-full">
      <div
        ref={ref}
        onMouseMove={onMove}
        onMouseLeave={onLeave}
        className={`preserve-3d h-full will-change-transform ${className}`}
        style={{ transition: "transform 0.18s ease-out" }}
      >
        {children}
      </div>
    </div>
  );
}
