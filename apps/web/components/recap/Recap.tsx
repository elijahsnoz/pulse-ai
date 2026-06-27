"use client";

/**
 * The Recap — a cinematic sheet that rises OVER the completed match.
 *
 * Not a terminal screen: the finished match still lives underneath (blurred,
 * dimmed, gently scaled). The recap is a layer, never a destination. It offers
 * three graceful paths — Continue exploring (primary), Replay, Share — so Pulse
 * never reaches a dead end.
 */
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, RotateCcw, Share2 } from "lucide-react";

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
  return timeline.find((e) => e.kind === "goal") ?? null;
}

function mostEmotionalMinute(samples: Sample[]): Sample | null {
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
    initial={{ opacity: 0, y: 14 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
    className="border-t border-white/10 py-3.5"
  >
    <div className="text-[10px] uppercase tracking-[0.25em] text-white/35">{label}</div>
    <div className="mt-1 text-base font-semibold text-white sm:text-lg">{children}</div>
  </motion.div>
);

export interface RecapProps {
  open: boolean;
  onContinue: () => void;
  onReplay: () => void;
  onReplayFromStart: () => void;
  onShare: () => void;
}

export function Recap({ open, onContinue, onReplay, onReplayFromStart, onShare }: RecapProps) {
  const meta = useMatchStore((s) => s.meta);
  const snapshot = useMatchStore((s) => s.snapshot);
  const samples = useMatchStore((s) => s.samples);
  const timeline = useMatchStore((s) => s.timeline);
  const peakBpm = useMatchStore((s) => s.peakBpm);
  const peakBpmMinute = useMatchStore((s) => s.peakBpmMinute);

  const ready = open && !!meta && !!snapshot;

  return (
    <AnimatePresence>
      {ready && meta && snapshot && (
        <div className="fixed inset-0 z-50">
          {/* backdrop — tap to continue exploring (the match shows through) */}
          <motion.div
            className="absolute inset-0"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            onClick={onContinue}
          />

          {/* the rising sheet */}
          <div className="absolute inset-0 flex items-end justify-center sm:items-center">
            <motion.div
              role="dialog"
              aria-label="Match recap"
              onClick={(e) => e.stopPropagation()}
              initial={{ y: 80, opacity: 0, scale: 0.98 }}
              animate={{ y: 0, opacity: 1, scale: 1 }}
              exit={{ y: 60, opacity: 0 }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="max-h-[92vh] w-full max-w-lg overflow-y-auto rounded-t-[28px] border border-white/10 bg-gradient-to-b from-ink-600/95 to-ink-800/98 p-6 shadow-2xl backdrop-blur-2xl sm:mb-6 sm:rounded-[28px] sm:p-7"
            >
              {/* grab handle — the bottom-sheet feel */}
              <div className="mx-auto mb-5 h-1.5 w-10 rounded-full bg-white/15" />

              <div className="text-[11px] uppercase tracking-[0.35em] text-ember">
                Full time &middot; Pulse Recap
              </div>

              <motion.h2
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.12, duration: 0.7 }}
                className="mt-3 text-2xl font-extrabold leading-snug tracking-tight text-white sm:text-3xl"
              >
                {matchHeadline(meta, snapshot.score)}
              </motion.h2>

              <div className="mt-2 text-sm font-semibold text-white/60">
                {meta.home} {snapshot.score.home}&ndash;{snapshot.score.away} {meta.away}
              </div>

              {/* heartbeat curve */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.28, duration: 0.8 }}
                className="mt-5"
              >
                <div className="text-[10px] uppercase tracking-[0.25em] text-white/35">
                  The match&rsquo;s heartbeat
                </div>
                <svg viewBox="0 0 320 64" className="mt-2 h-16 w-full" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="curve" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ff3b6b" stopOpacity="0.5" />
                      <stop offset="100%" stopColor="#ff3b6b" stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  {samples.length > 1 && (
                    <>
                      <polyline
                        points={curvePoints(samples, 320, 64)}
                        fill="none"
                        stroke="#ff3b6b"
                        strokeWidth="2"
                        strokeLinejoin="round"
                      />
                      <polygon
                        points={`0,64 ${curvePoints(samples, 320, 64)} 320,64`}
                        fill="url(#curve)"
                      />
                    </>
                  )}
                </svg>
              </motion.div>

              <Row delay={0.4} label="Turning point">
                {(() => {
                  const tp = turningPoint(timeline);
                  return tp ? `${Math.floor(tp.minute)}' — ${tp.text}` : "A slow, even battle";
                })()}
              </Row>
              <Row delay={0.48} label="Most emotional moment">
                {(() => {
                  const m = mostEmotionalMinute(samples);
                  return m
                    ? `${Math.floor(m.minute)}' — ${"★".repeat(m.stars)}${"☆".repeat(5 - m.stars)}`
                    : "A slow burn throughout";
                })()}
              </Row>
              <Row delay={0.56} label="Peak heart rate">
                {Math.round(peakBpm)} bpm at {Math.floor(peakBpmMinute)}&rsquo;
              </Row>
              <Row delay={0.64} label="Pulse reflection">
                <span className="font-medium italic text-white/85">
                  {matchReflection(snapshot.score)}
                </span>
              </Row>

              {/* CTAs — three meaningful, graceful paths forward */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.78 }}
                className="mt-6 space-y-3"
              >
                <button
                  type="button"
                  onClick={onContinue}
                  className="group flex w-full items-center justify-center gap-2 rounded-2xl bg-ember py-3.5 font-semibold text-white transition hover:brightness-110"
                >
                  Continue exploring
                  <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
                </button>

                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={onReplay}
                    className="flex items-center justify-center gap-2 rounded-2xl bg-white/[0.06] py-3 font-medium text-white/85 ring-1 ring-white/10 transition hover:bg-white/10"
                  >
                    <RotateCcw className="h-4 w-4" />
                    Replay
                  </button>
                  <button
                    type="button"
                    onClick={onShare}
                    className="flex items-center justify-center gap-2 rounded-2xl bg-white/[0.06] py-3 font-medium text-white/85 ring-1 ring-white/10 transition hover:bg-white/10"
                  >
                    <Share2 className="h-4 w-4" />
                    Share recap
                  </button>
                </div>

                <button
                  type="button"
                  onClick={onReplayFromStart}
                  className="w-full pt-1 text-center text-xs text-white/40 transition hover:text-white/70"
                >
                  Replay from the beginning
                </button>
              </motion.div>
            </motion.div>
          </div>
        </div>
      )}
    </AnimatePresence>
  );
}
