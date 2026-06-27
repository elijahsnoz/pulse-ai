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
    <div className="relative h-[66px] w-[50px] overflow-hidden sm:h-[88px] sm:w-[66px]">
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={value}
          initial={{ y: side === "home" ? 46 : -46, opacity: 0, scale: 1.35 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          exit={{ y: side === "home" ? -46 : 46, opacity: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 22 }}
          className="absolute inset-0 flex items-center justify-center text-6xl font-black tabular-nums tracking-tight sm:text-7xl"
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
        <span className="min-w-[110px] text-right text-xl font-bold tracking-tight text-home sm:min-w-[170px] sm:text-3xl">
          {meta?.home ?? "Home"}
        </span>

        <div className="flex items-center gap-1.5 text-white">
          <ScoreDigit value={home} side="home" />
          <span className="pb-1 text-4xl font-thin text-white/30">:</span>
          <ScoreDigit value={away} side="away" />
        </div>

        <span className="min-w-[110px] text-left text-xl font-bold tracking-tight text-away sm:min-w-[170px] sm:text-3xl">
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
