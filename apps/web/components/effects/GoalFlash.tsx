"use client";

/**
 * GoalFlash — a goal interrupts everything.
 *
 * The screen erupts in the scoring team's colour with a bright bloom, paired
 * with the heartbeat spike and the "GOOOAL." line. Brief, then it clears so the
 * meaning can land.
 */
import { AnimatePresence, motion } from "framer-motion";

import { TEAM_COLORS } from "@/lib/colors";
import { useMatchStore } from "@/stores/matchStore";

export function GoalFlash() {
  const flash = useMatchStore((s) => s.goalFlash);

  return (
    <AnimatePresence>
      {flash && (
        <motion.div key={flash.key} className="pointer-events-none fixed inset-0 z-40">
          {/* full-field colour wash */}
          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.6, 0] }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.1, ease: "easeOut", times: [0, 0.2, 1] }}
            style={{
              background: `radial-gradient(circle at center, ${TEAM_COLORS[flash.side]}66, transparent 70%)`,
            }}
          />
          {/* a quick bright bloom at the very start */}
          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.35, 0] }}
            transition={{ duration: 0.5, ease: "easeOut", times: [0, 0.3, 1] }}
            style={{ background: "white" }}
          />
          {/* edge vignette in team colour */}
          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.7, 0] }}
            transition={{ duration: 1.1, ease: "easeOut" }}
            style={{
              boxShadow: `inset 0 0 220px 40px ${TEAM_COLORS[flash.side]}`,
            }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
