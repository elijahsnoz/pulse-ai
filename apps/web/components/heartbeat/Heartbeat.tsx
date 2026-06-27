"use client";

/**
 * The Heartbeat — Pulse's logo.
 *
 * A living heart: organic lub-dub, a slow breath, a glow that deepens with
 * drama, and a hard spike the instant a goal lands. The one thing judges
 * remember.
 */
import { motion, useReducedMotion } from "framer-motion";

import { bandIntensity, bandTheme } from "@/lib/colors";
import { BEAT_KEYFRAMES, BEAT_TIMES, HEART_PATH } from "@/lib/heart";
import { useMatchStore } from "@/stores/matchStore";

export function Heartbeat() {
  const reduce = useReducedMotion();
  const rawBpm = useMatchStore((s) => s.snapshot?.pulse.bpm ?? 64);
  const rawBand = useMatchStore((s) => s.snapshot?.pulse.band ?? "Dormant");
  const dramaBand = useMatchStore((s) => s.snapshot?.drama.band ?? "Dormant");
  const spiking = useMatchStore((s) => s.goalFlash !== null);
  const ended = useMatchStore((s) => s.status === "ended");

  // At full time the tension releases — the heart eases to a calm resting beat.
  const bpm = ended ? 56 : rawBpm;
  const band = ended ? "Dormant" : rawBand;
  const theme = bandTheme(band);
  const beat = Math.min(1.15, Math.max(0.36, 60 / Math.max(bpm, 1)));
  const drama = ended ? 0 : bandIntensity(dramaBand);
  const scale = (1 + drama * 0.3) * (spiking ? 1.28 : 1);
  const glowSize = 220 + drama * 80;

  return (
    <div className="relative flex items-center justify-center" aria-hidden>
      {/* breath — a slow outer swell independent of the beat */}
      <motion.div
        className="absolute rounded-full blur-3xl"
        style={{ width: glowSize, height: glowSize, background: theme.glow }}
        animate={reduce ? undefined : { opacity: [0.45, 0.8, 0.45], scale: [1, 1.08, 1] }}
        transition={{ duration: spiking ? beat : 5, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* two staggered pulse rings for a richer beat */}
      {!reduce &&
        [0, beat * 0.4].map((delay, i) => (
          <motion.div
            key={i}
            className="absolute rounded-full"
            style={{ width: 150, height: 150, border: `2px solid ${theme.color}` }}
            animate={{ scale: [0.8, 2.1], opacity: [0.5, 0] }}
            transition={{ duration: beat, repeat: Infinity, ease: "easeOut", delay }}
          />
        ))}

      <motion.div
        animate={{ scale }}
        transition={{ type: "spring", stiffness: 140, damping: 14 }}
      >
        <motion.svg
          width={172}
          height={172}
          viewBox="0 0 100 100"
          animate={reduce ? undefined : BEAT_KEYFRAMES}
          transition={
            reduce
              ? undefined
              : { duration: beat, repeat: Infinity, ease: "easeInOut", times: BEAT_TIMES }
          }
          style={{ filter: `drop-shadow(0 0 ${spiking ? 48 : 28}px ${theme.glow})` }}
        >
          <defs>
            <radialGradient id="heartFill" cx="50%" cy="34%" r="78%">
              <stop offset="0%" stopColor="#ffffff" stopOpacity="0.4" />
              <stop offset="38%" stopColor={theme.color} />
              <stop offset="100%" stopColor={theme.color} />
            </radialGradient>
          </defs>
          <path d={HEART_PATH} fill="url(#heartFill)" />
        </motion.svg>
      </motion.div>

      <div className="absolute -bottom-10 flex items-baseline gap-1.5 text-white/70">
        <motion.span
          key={Math.round(bpm)}
          initial={{ opacity: 0.4, y: 2 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-2xl font-bold tabular-nums tracking-tight"
        >
          {Math.round(bpm)}
        </motion.span>
        <span className="text-[11px] uppercase tracking-[0.3em] text-white/35">bpm</span>
      </div>
    </div>
  );
}
