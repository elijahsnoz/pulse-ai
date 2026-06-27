"use client";

/**
 * ScoreBoard — "what is happening": teams, score, minute, and the match's
 * current chapter (phase) and mood (emotion) as words, never numbers.
 */
import { AnimatePresence, motion } from "framer-motion";

import { minuteLabel } from "@/lib/format";
import { useMatchStore } from "@/stores/matchStore";

function ScoreDigit({ value, side }: { value: number; side: "home" | "away" }) {
  return (
    <div className="relative h-[58px] w-[44px] overflow-hidden sm:h-[72px] sm:w-[56px]">
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={value}
          initial={{ y: side === "home" ? 40 : -40, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: side === "home" ? -40 : 40, opacity: 0 }}
          transition={{ type: "spring", stiffness: 320, damping: 26 }}
          className="absolute inset-0 flex items-center justify-center text-5xl font-extrabold tabular-nums sm:text-6xl"
        >
          {value}
        </motion.span>
      </AnimatePresence>
    </div>
  );
}

export function ScoreBoard() {
  const meta = useMatchStore((s) => s.meta);
  const home = useMatchStore((s) => s.snapshot?.score.home ?? 0);
  const away = useMatchStore((s) => s.snapshot?.score.away ?? 0);
  const minute = useMatchStore((s) => s.snapshot?.minute ?? 0);
  const phase = useMatchStore((s) => s.snapshot?.phase ?? "");
  const emotion = useMatchStore((s) => s.snapshot?.emotion ?? "");

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="text-[11px] uppercase tracking-[0.3em] text-white/35">
        FIFA World Cup
      </div>

      <div className="flex items-center justify-center gap-5 sm:gap-8">
        <span className="min-w-[110px] text-right text-lg font-bold text-home sm:min-w-[160px] sm:text-2xl">
          {meta?.home ?? "Home"}
        </span>

        <div className="flex items-center gap-1 text-white">
          <ScoreDigit value={home} side="home" />
          <span className="pb-1 text-3xl font-light text-white/40">:</span>
          <ScoreDigit value={away} side="away" />
        </div>

        <span className="min-w-[110px] text-left text-lg font-bold text-away sm:min-w-[160px] sm:text-2xl">
          {meta?.away ?? "Away"}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-semibold tabular-nums text-white/80 ring-1 ring-white/10">
          {minuteLabel(minute)}
        </span>
        {phase && (
          <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-medium text-white/55 ring-1 ring-white/10">
            {phase}
          </span>
        )}
        {emotion && (
          <span className="rounded-full bg-ember/10 px-3 py-1 text-xs font-semibold text-ember ring-1 ring-ember/20">
            {emotion}
          </span>
        )}
      </div>
    </div>
  );
}
