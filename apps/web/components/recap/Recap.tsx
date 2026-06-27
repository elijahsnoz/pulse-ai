"use client";

/**
 * The Recap — Pulse's Spotify-Wrapped moment.
 *
 * Not "the match stopped" but "here's the story you just lived": a headline, the
 * heartbeat curve of the whole match, its turning point, peak heart rate, most
 * dramatic moment, and a warm closing reflection. Built to be screenshotted.
 */
import { AnimatePresence, motion } from "framer-motion";

import { matchHeadline, matchReflection } from "@/lib/voice";
import { useMatchStore } from "@/stores/matchStore";
import type { Sample, TimelineEntry } from "@/types/match";

function curvePoints(samples: Sample[], w: number, h: number): string {
  if (samples.length < 2) return "";
  const minutes = samples.map((s) => s.minute);
  const bpms = samples.map((s) => s.bpm);
  const minM = Math.min(...minutes);
  const maxM = Math.max(...minutes);
  const minB = Math.min(...bpms);
  const maxB = Math.max(...bpms);
  const spanM = Math.max(1, maxM - minM);
  const spanB = Math.max(1, maxB - minB);
  return samples
    .map((s) => {
      const x = ((s.minute - minM) / spanM) * w;
      const y = h - ((s.bpm - minB) / spanB) * (h - 8) - 4;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function turningPoint(timeline: TimelineEntry[]): TimelineEntry | null {
  const red = timeline.find((e) => e.kind === "card" && e.icon === "🟥");
  if (red) return red;
  const goal = timeline.find((e) => e.kind === "goal");
  return goal ?? null;
}

function mostEmotionalMinute(samples: Sample[]): { minute: number; stars: number } | null {
  if (!samples.length) return null;
  return samples.reduce((best, s) => (s.stars >= best.stars ? s : best), samples[0]);
}

const Row = ({
  delay,
  label,
  children,
}: {
  delay: number;
  label: string;
  children: React.ReactNode;
}) => (
  <motion.div
    initial={{ opacity: 0, y: 16 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
    className="border-t border-white/10 py-4"
  >
    <div className="text-[10px] uppercase tracking-[0.25em] text-white/35">{label}</div>
    <div className="mt-1 text-lg font-semibold text-white">{children}</div>
  </motion.div>
);

export function Recap({ onReplay }: { onReplay: () => void }) {
  const status = useMatchStore((s) => s.status);
  const meta = useMatchStore((s) => s.meta);
  const snapshot = useMatchStore((s) => s.snapshot);
  const samples = useMatchStore((s) => s.samples);
  const timeline = useMatchStore((s) => s.timeline);
  const peakBpm = useMatchStore((s) => s.peakBpm);
  const peakBpmMinute = useMatchStore((s) => s.peakBpmMinute);

  const open = status === "ended" && !!meta && !!snapshot;

  return (
    <AnimatePresence>
      {open && meta && snapshot && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/95 p-5 backdrop-blur-md"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            initial={{ scale: 0.96, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
            className="w-full max-w-lg rounded-3xl border border-white/10 bg-gradient-to-b from-ink-600 to-ink-800 p-7 shadow-2xl"
          >
            <div className="text-[11px] uppercase tracking-[0.35em] text-ember">
              Pulse Recap
            </div>

            <motion.h2
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15, duration: 0.7 }}
              className="mt-3 text-2xl font-extrabold leading-snug text-white sm:text-3xl"
            >
              {matchHeadline(meta, snapshot.score)}
            </motion.h2>

            <div className="mt-2 text-sm font-semibold text-white/60">
              {meta.home} {snapshot.score.home}&ndash;{snapshot.score.away} {meta.away}
            </div>

            {/* Heartbeat curve */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="mt-5"
            >
              <div className="text-[10px] uppercase tracking-[0.25em] text-white/35">
                The match&rsquo;s heartbeat
              </div>
              <svg viewBox="0 0 320 70" className="mt-2 h-20 w-full" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="curve" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ff3b6b" stopOpacity="0.5" />
                    <stop offset="100%" stopColor="#ff3b6b" stopOpacity="0" />
                  </linearGradient>
                </defs>
                {samples.length > 1 && (
                  <>
                    <polyline
                      points={curvePoints(samples, 320, 70)}
                      fill="none"
                      stroke="#ff3b6b"
                      strokeWidth="2"
                      strokeLinejoin="round"
                    />
                    <polygon
                      points={`0,70 ${curvePoints(samples, 320, 70)} 320,70`}
                      fill="url(#curve)"
                    />
                  </>
                )}
              </svg>
            </motion.div>

            <Row delay={0.45} label="Turning point">
              {(() => {
                const tp = turningPoint(timeline);
                return tp ? `${Math.floor(tp.minute)}' — ${tp.text}` : "A slow, even battle";
              })()}
            </Row>
            <Row delay={0.55} label="Most emotional moment">
              {(() => {
                const m = mostEmotionalMinute(samples);
                return m
                  ? `${Math.floor(m.minute)}' — ${"★".repeat(m.stars)}${"☆".repeat(5 - m.stars)}`
                  : "A slow burn throughout";
              })()}
            </Row>
            <Row delay={0.65} label="Peak heart rate">
              {Math.round(peakBpm)} bpm at {Math.floor(peakBpmMinute)}&rsquo;
            </Row>
            <Row delay={0.75} label="Pulse reflection">
              <span className="font-medium italic text-white/85">
                {matchReflection(snapshot.score)}
              </span>
            </Row>

            <motion.button
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.95 }}
              onClick={onReplay}
              className="mt-6 w-full rounded-xl bg-ember py-3 font-semibold text-white transition hover:brightness-110"
            >
              Watch it again
            </motion.button>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
