/** A soft glass panel — the resting surface for supporting visuals. */
import type { ReactNode } from "react";

export function Panel({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-2xl border border-white/10 bg-gradient-to-b from-ink-600/70 to-ink-700/70 p-5 backdrop-blur-sm ${className}`}
    >
      {children}
    </div>
  );
}
