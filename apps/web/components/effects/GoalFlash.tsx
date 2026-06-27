"use client";

/**
 * GoalFlash — the screen briefly erupts in the scoring team's colour.
 * Paired with the heartbeat spike and the "GOOOAL." line in the story card.
 */
import { AnimatePresence, motion } from "framer-motion";

import { TEAM_COLORS } from "@/lib/colors";
import { useMatchStore } from "@/stores/matchStore";

export function GoalFlash() {
  const flash = useMatchStore((s) => s.goalFlash);

  return (
    <AnimatePresence>
      {flash && (
        <motion.div
          key={flash.key}
          className="pointer-events-none fixed inset-0 z-40"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0.55, 0] }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.1, ease: "easeOut", times: [0, 0.25, 1] }}
          style={{
            background: `radial-gradient(circle at center, ${
              TEAM_COLORS[flash.side]
            }55, transparent 70%)`,
          }}
        />
      )}
    </AnimatePresence>
  );
}
