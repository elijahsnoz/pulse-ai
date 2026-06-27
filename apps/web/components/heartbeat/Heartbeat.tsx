"use client";

/**
 * The Heartbeat — Pulse's identity.
 *
 * An organic, living heart whose tempo follows the match BPM, whose size swells
 * in drama, and whose colour is the heat of the moment. Users should remember
 * this more than any chart.
 */
import { motion, useReducedMotion } from "framer-motion";

import { bandIntensity, bandTheme } from "@/lib/colors";
import { useMatchStore } from "@/stores/matchStore";

const HEART_PATH =
  "M50 88 C 18 64, 4 44, 4 28 C 4 14, 15 6, 27 6 C 37 6, 45 12, 50 22 C 55 12, 63 6, 73 6 C 85 6, 96 14, 96 28 C 96 44, 82 64, 50 88 Z";

export function Heartbeat() {
  const reduce = useReducedMotion();
  const bpm = useMatchStore((s) => s.snapshot?.pulse.bpm ?? 64);
  const band = useMatchStore((s) => s.snapshot?.pulse.band ?? "Dormant");
  const dramaBand = useMatchStore((s) => s.snapshot?.drama.band ?? "Dormant");

  const theme = bandTheme(band);
  const beat = Math.min(1.15, Math.max(0.36, 60 / Math.max(bpm, 1)));
  const scale = 1 + bandIntensity(dramaBand) * 0.32;

  const beatKeyframes = reduce ? undefined : { scale: [1, 1.14, 1, 1.05, 1] };

  return (
    <div className="relative flex items-center justify-center" aria-hidden>
      {/* soft ambient glow */}
      <motion.div
        className="absolute rounded-full blur-3xl"
        style={{ width: 240, height: 240, background: theme.glow }}
        animate={reduce ? undefined : { opacity: [0.5, 0.85, 0.5] }}
        transition={{ duration: beat, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* expanding pulse ring on each beat */}
      {!reduce && (
        <motion.div
          className="absolute rounded-full"
          style={{ width: 150, height: 150, border: `2px solid ${theme.color}` }}
          animate={{ scale: [0.8, 2], opacity: [0.55, 0] }}
          transition={{ duration: beat, repeat: Infinity, ease: "easeOut" }}
        />
      )}

      {/* the heart */}
      <motion.div
        style={{ scale }}
        transition={{ type: "spring", stiffness: 60, damping: 16 }}
      >
        <motion.svg
          width={170}
          height={170}
          viewBox="0 0 100 100"
          animate={beatKeyframes}
          transition={
            reduce
              ? undefined
              : {
                  duration: beat,
                  repeat: Infinity,
                  ease: "easeInOut",
                  times: [0, 0.14, 0.3, 0.44, 1],
                }
          }
          style={{ filter: `drop-shadow(0 0 26px ${theme.glow})` }}
        >
          <defs>
            <radialGradient id="heartFill" cx="50%" cy="35%" r="75%">
              <stop offset="0%" stopColor="#ffffff" stopOpacity="0.35" />
              <stop offset="35%" stopColor={theme.color} />
              <stop offset="100%" stopColor={theme.color} />
            </radialGradient>
          </defs>
          <path d={HEART_PATH} fill="url(#heartFill)" />
        </motion.svg>
      </motion.div>

      {/* subtle BPM flavour — the pulse, not a metric */}
      <div className="absolute -bottom-9 flex items-baseline gap-1 text-white/70">
        <span className="text-2xl font-bold tabular-nums">{Math.round(bpm)}</span>
        <span className="text-[11px] uppercase tracking-widest text-white/40">bpm</span>
      </div>
    </div>
  );
}
