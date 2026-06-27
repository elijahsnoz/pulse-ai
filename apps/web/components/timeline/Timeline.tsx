"use client";

/**
 * The Live Timeline — the match's memory.
 *
 * Goals and red cards are hero moments; ambient mood/phase shifts are quiet
 * texture. Importance, not recency alone, drives visual weight.
 */
import { AnimatePresence, motion } from "framer-motion";

import { useMatchStore } from "@/stores/matchStore";
import type { TimelineEntry } from "@/types/match";
import type { TimelineKind } from "@/types/wire";

const WEIGHT: Record<TimelineKind, "hero" | "notable" | "ambient"> = {
  goal: "hero",
  card: "hero",
  momentum_shift: "notable",
  pulse_moment: "notable",
  phase_changed: "ambient",
  emotion_changed: "ambient",
};

const HERO = "border-white/15 bg-white/[0.06] text-white";
const HERO_GOAL = "border-emerald-400/30 bg-emerald-400/10 text-white";
const HERO_RED = "border-away/40 bg-away/10 text-white";
const NOTABLE = "border-white/10 bg-white/[0.03] text-white/85";
const AMBIENT = "border-transparent bg-transparent text-white/40";

function classFor(entry: TimelineEntry): string {
  const weight = WEIGHT[entry.kind];
  if (weight === "hero") {
    if (entry.kind === "goal") return HERO_GOAL;
    if (entry.kind === "card" && entry.icon === "🟥") return HERO_RED;
    return HERO;
  }
  if (weight === "notable") return NOTABLE;
  return AMBIENT;
}

export function Timeline() {
  const timeline = useMatchStore((s) => s.timeline);
  const visible = timeline.slice(0, 16);

  return (
    <div className="flex h-full flex-col">
      <h3 className="mb-3 text-[10px] uppercase tracking-[0.25em] text-white/30">
        Live Timeline
      </h3>
      <div className="flex flex-col gap-2 overflow-y-auto pr-1">
        <AnimatePresence initial={false}>
          {visible.map((entry) => {
            const hero = WEIGHT[entry.kind] === "hero";
            return (
              <motion.div
                key={entry.id}
                layout
                initial={{ opacity: 0, y: -8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.35, ease: "easeOut" }}
                className={`flex items-center gap-3 rounded-xl border px-3 py-2 ${classFor(entry)}`}
              >
                <span className="w-9 shrink-0 text-xs tabular-nums text-white/40">
                  {Math.floor(entry.minute)}&rsquo;
                </span>
                <span className={hero ? "text-lg" : "text-sm"}>{entry.icon}</span>
                <span className={`${hero ? "font-semibold" : "font-normal"} truncate`}>
                  {entry.text}
                </span>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}
