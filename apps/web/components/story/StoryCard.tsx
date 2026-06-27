"use client";

/**
 * The AI Story Card — Pulse's voice, in the visual centre.
 *
 * A single warm sentence that breathes, fades, and never looks like a
 * notification. Goal eruptions get the loudest treatment; ambient lines stay
 * quiet. When Pulse has nothing to add, this rests (the heartbeat speaks on).
 */
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";

import { useMatchStore } from "@/stores/matchStore";
import type { StoryTone } from "@/types/match";

const TONE_CLASS: Record<StoryTone, string> = {
  calm: "text-white/80",
  rising: "text-white",
  peak: "text-white",
  reflective: "text-white/85",
};

export function StoryCard() {
  const reduce = useReducedMotion();
  const story = useMatchStore((s) => s.story);

  return (
    <div className="flex min-h-[150px] items-center justify-center px-4 text-center sm:min-h-[170px]">
      <AnimatePresence mode="wait">
        {story && (
          <motion.div
            key={story.id}
            initial={reduce ? { opacity: 0 } : { opacity: 0, y: 14, filter: "blur(6px)" }}
            animate={reduce ? { opacity: 1 } : { opacity: 1, y: 0, filter: "blur(0px)" }}
            exit={reduce ? { opacity: 0 } : { opacity: 0, y: -10, filter: "blur(6px)" }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="max-w-xl"
          >
            <p
              className={`${TONE_CLASS[story.tone]} ${
                story.emphatic
                  ? "text-4xl font-extrabold tracking-tight sm:text-6xl"
                  : "text-xl font-medium leading-relaxed sm:text-3xl sm:leading-relaxed"
              }`}
            >
              {story.text}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
