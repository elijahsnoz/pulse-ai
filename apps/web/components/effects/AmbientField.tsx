"use client";

/**
 * AmbientField — the room changes color with the match.
 *
 * A slow background wash whose hue tracks the drama band: cool when calm, warm
 * as it builds, electric and critical at the peaks, settling at release. Bands
 * change infrequently, so each shift crossfades over ~1.6s — felt, not noticed.
 */
import { AnimatePresence, motion } from "framer-motion";

import { bandTheme } from "@/lib/colors";
import { useMatchStore } from "@/stores/matchStore";

export function AmbientField() {
  const band = useMatchStore((s) => s.snapshot?.drama.band ?? "Dormant");
  const glow = bandTheme(band).glow;

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <AnimatePresence>
        <motion.div
          key={band}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.6, ease: "easeInOut" }}
          className="absolute inset-0"
          style={{
            background: `radial-gradient(1100px 760px at 50% -8%, ${glow}, transparent 62%)`,
          }}
        />
      </AnimatePresence>
    </div>
  );
}
