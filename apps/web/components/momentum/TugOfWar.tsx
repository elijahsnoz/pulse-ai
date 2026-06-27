"use client";

/**
 * Momentum as a tug-of-war — never a bar with a number.
 *
 * A rope with a knot that slides toward whoever is controlling the match.
 * The momentum *value* positions the knot internally; it is never shown.
 */
import { motion } from "framer-motion";

import { TEAM_COLORS } from "@/lib/colors";
import { useMatchStore } from "@/stores/matchStore";

export function TugOfWar() {
  const meta = useMatchStore((s) => s.meta);
  const value = useMatchStore((s) => s.snapshot?.momentum.value ?? 0);
  const direction = useMatchStore((s) => s.snapshot?.momentum.direction ?? "neutral");

  // value in [-100, 100] (+home / -away) -> knot offset across the rope.
  const clamped = Math.max(-100, Math.min(100, value));
  const knotPercent = 50 + (clamped / 100) * 42;
  const leadColor =
    direction === "home"
      ? TEAM_COLORS.home
      : direction === "away"
        ? TEAM_COLORS.away
        : "#5b6b8c";

  return (
    <div className="w-full">
      <div className="mb-3 flex items-center justify-between text-sm font-semibold">
        <span className="text-home">{meta?.home ?? "Home"}</span>
        <span className="text-[10px] uppercase tracking-[0.25em] text-white/30">
          Momentum
        </span>
        <span className="text-away">{meta?.away ?? "Away"}</span>
      </div>

      <div className="relative h-3 rounded-full bg-white/5 ring-1 ring-white/10">
        {/* the rope tension fills toward the leader */}
        <motion.div
          className="absolute top-0 bottom-0 rounded-full opacity-50"
          style={{ background: leadColor }}
          animate={
            clamped >= 0
              ? { left: "50%", right: `${100 - knotPercent}%` }
              : { left: `${knotPercent}%`, right: "50%" }
          }
          transition={{ type: "spring", stiffness: 90, damping: 20 }}
        />
        {/* the knot */}
        <motion.div
          className="absolute top-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white/30"
          style={{ background: leadColor, boxShadow: `0 0 18px ${leadColor}` }}
          animate={{ left: `${knotPercent}%` }}
          transition={{ type: "spring", stiffness: 90, damping: 18 }}
        />
        <div className="absolute left-1/2 top-1/2 h-5 w-px -translate-x-1/2 -translate-y-1/2 bg-white/15" />
      </div>
    </div>
  );
}
