"use client";

/**
 * Drama as stars — cinematic intensity, no percentages, no decimals.
 */
import { motion, useReducedMotion } from "framer-motion";

import { useMatchStore } from "@/stores/matchStore";

const STARS = [0, 1, 2, 3, 4];

export function DramaStars() {
  const reduce = useReducedMotion();
  const stars = useMatchStore((s) => s.snapshot?.drama.stars ?? 0);

  return (
    <div className="flex flex-col items-center gap-2">
      <span className="text-[10px] uppercase tracking-[0.25em] text-white/30">
        Drama
      </span>
      <div className="flex items-center gap-1.5">
        {STARS.map((i) => {
          const filled = i < stars;
          return (
            <motion.span
              key={i}
              animate={
                filled && !reduce
                  ? { scale: stars >= 4 ? [1, 1.18, 1] : 1 }
                  : { scale: 1 }
              }
              transition={{ duration: 1.4, repeat: stars >= 4 ? Infinity : 0, ease: "easeInOut" }}
              className={`text-2xl ${filled ? "text-gold" : "text-white/15"}`}
              style={filled ? { filter: "drop-shadow(0 0 8px rgba(255,209,102,0.6))" } : undefined}
            >
              ★
            </motion.span>
          );
        })}
      </div>
    </div>
  );
}
