"use client";

/**
 * ShareSheet — the shareable recap, designed now.
 *
 * Presents the recap as a portrait card built for X / Instagram / WhatsApp:
 * branding, final score, headline, the heartbeat curve, peak rate. Copy-link
 * works today; image export is the next step (placeholder, clearly signposted).
 */
import { AnimatePresence, motion } from "framer-motion";
import { Check, Link2, X } from "lucide-react";
import { useState } from "react";

import { matchHeadline } from "@/lib/voice";
import { useMatchStore } from "@/stores/matchStore";
import type { Sample } from "@/types/match";

function miniCurve(samples: Sample[], w: number, h: number): string {
  if (samples.length < 2) return "";
  const ms = samples.map((s) => s.minute);
  const bs = samples.map((s) => s.bpm);
  const minM = Math.min(...ms);
  const maxM = Math.max(...ms);
  const minB = Math.min(...bs);
  const maxB = Math.max(...bs);
  const spanM = Math.max(1, maxM - minM);
  const spanB = Math.max(1, maxB - minB);
  return samples
    .map((s) => {
      const x = ((s.minute - minM) / spanM) * w;
      const y = h - ((s.bpm - minB) / spanB) * (h - 6) - 3;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

export function ShareSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const meta = useMatchStore((s) => s.meta);
  const snapshot = useMatchStore((s) => s.snapshot);
  const samples = useMatchStore((s) => s.samples);
  const peakBpm = useMatchStore((s) => s.peakBpm);
  const [copied, setCopied] = useState(false);

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* clipboard unavailable — no-op */
    }
  };

  const ready = open && !!meta && !!snapshot;

  return (
    <AnimatePresence>
      {ready && meta && snapshot && (
        <motion.div
          className="fixed inset-0 z-[55] flex items-center justify-center bg-ink-900/70 p-5 backdrop-blur-xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            onClick={(e) => e.stopPropagation()}
            initial={{ y: 30, opacity: 0, scale: 0.97 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 20, opacity: 0 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            className="w-full max-w-sm"
          >
            <div className="mb-3 flex items-center justify-between">
              <span className="text-[11px] uppercase tracking-[0.3em] text-white/45">
                Share recap
              </span>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close"
                className="rounded-full bg-white/10 p-1.5 text-white/70 transition hover:bg-white/15"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* the shareable card artifact (9:16-ish) */}
            <div className="overflow-hidden rounded-[26px] border border-white/10 bg-[radial-gradient(700px_400px_at_50%_-10%,#2a1430,#0a0e1a_60%)] p-6 shadow-2xl">
              <div className="flex items-center gap-2 text-sm font-extrabold tracking-tight text-white">
                PULSE<span className="text-ember">.</span>
                <span className="text-[10px] font-medium text-white/35">AI Second Screen</span>
              </div>

              <div className="mt-7 text-center">
                <div className="text-xs font-semibold uppercase tracking-[0.25em] text-white/45">
                  Full time
                </div>
                <div className="mt-2 flex items-center justify-center gap-3 text-white">
                  <span className="text-sm font-bold text-home">{meta.home}</span>
                  <span className="text-4xl font-black tabular-nums tracking-tight">
                    {snapshot.score.home}&ndash;{snapshot.score.away}
                  </span>
                  <span className="text-sm font-bold text-away">{meta.away}</span>
                </div>
              </div>

              <p className="mt-6 text-center text-base font-semibold leading-snug text-white/90">
                {matchHeadline(meta, snapshot.score)}
              </p>

              <svg viewBox="0 0 300 50" className="mt-6 h-12 w-full" preserveAspectRatio="none">
                {samples.length > 1 && (
                  <polyline
                    points={miniCurve(samples, 300, 50)}
                    fill="none"
                    stroke="#ff3b6b"
                    strokeWidth="2"
                    strokeLinejoin="round"
                  />
                )}
              </svg>

              <div className="mt-4 flex items-center justify-between text-[11px] text-white/40">
                <span>Peak {Math.round(peakBpm)} bpm</span>
                <span>made with Pulse &middot; pulse.ai</span>
              </div>
            </div>

            {/* actions */}
            <div className="mt-4 space-y-2">
              <button
                type="button"
                onClick={copyLink}
                className="flex w-full items-center justify-center gap-2 rounded-2xl bg-ember py-3 font-semibold text-white transition hover:brightness-110"
              >
                {copied ? <Check className="h-4 w-4" /> : <Link2 className="h-4 w-4" />}
                {copied ? "Link copied" : "Copy link"}
              </button>
              <p className="text-center text-xs text-white/35">
                Image export for X, Instagram &amp; WhatsApp is coming next.
              </p>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
