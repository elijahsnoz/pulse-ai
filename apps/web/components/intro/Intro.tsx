"use client";

/**
 * The cinematic opening — Pulse never drops you into a dashboard.
 *
 * Black. A heart fades in and starts to beat. Its rate climbs. Pulse says it's
 * watching. Then the curtain lifts onto the match. Like opening Apple TV+, not a
 * web page. Tap anywhere to skip.
 */
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";

import { BEAT_KEYFRAMES, BEAT_TIMES, HEART_PATH } from "@/lib/heart";

const TARGET_BPM = 72;

export function Intro({ onDone }: { onDone: () => void }) {
  const reduce = useReducedMotion();
  const [stage, setStage] = useState(0);
  const [bpm, setBpm] = useState(44);
  const [leaving, setLeaving] = useState(false);

  const finish = () => {
    if (leaving) return;
    setLeaving(true);
    setTimeout(onDone, 850);
  };

  useEffect(() => {
    const timers = [
      setTimeout(() => setStage(1), 400),
      setTimeout(() => setStage(2), 2400),
      setTimeout(() => setStage(3), 4100),
      setTimeout(finish, 5600),
    ];
    return () => timers.forEach(clearTimeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (stage < 1) return;
    let current = 44;
    const id = setInterval(() => {
      current += 2;
      if (current >= TARGET_BPM) {
        current = TARGET_BPM;
        clearInterval(id);
      }
      setBpm(current);
    }, 55);
    return () => clearInterval(id);
  }, [stage]);

  const beat = 60 / bpm;

  return (
    <motion.div
      onClick={finish}
      className="fixed inset-0 z-[60] flex cursor-pointer flex-col items-center justify-center bg-ink-900"
      initial={{ opacity: 1 }}
      animate={{ opacity: leaving ? 0 : 1 }}
      transition={{ duration: 0.85, ease: "easeInOut" }}
    >
      <AnimatePresence>
        {stage >= 1 && (
          <motion.div
            key="heart"
            initial={{ opacity: 0, scale: 0.6 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
            className="relative flex items-center justify-center"
          >
            <motion.div
              className="absolute rounded-full blur-3xl"
              style={{ width: 220, height: 220, background: "rgba(255,59,107,0.45)" }}
              animate={reduce ? undefined : { opacity: [0.4, 0.8, 0.4] }}
              transition={{ duration: beat, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.svg
              width={150}
              height={150}
              viewBox="0 0 100 100"
              animate={reduce ? undefined : BEAT_KEYFRAMES}
              transition={
                reduce
                  ? undefined
                  : { duration: beat, repeat: Infinity, ease: "easeInOut", times: BEAT_TIMES }
              }
              style={{ filter: "drop-shadow(0 0 30px rgba(255,59,107,0.6))" }}
            >
              <path d={HEART_PATH} fill="#ff3b6b" />
            </motion.svg>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mt-8 flex h-7 items-baseline gap-1.5 text-white">
        {stage >= 1 && (
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-3xl font-bold tabular-nums tracking-tight"
          >
            {bpm}
          </motion.span>
        )}
        {stage >= 1 && (
          <span className="text-xs uppercase tracking-[0.3em] text-white/40">bpm</span>
        )}
      </div>

      <div className="mt-10 h-16 text-center">
        <AnimatePresence mode="wait">
          {stage === 2 && (
            <motion.p
              key="watching"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.8 }}
              className="text-2xl font-medium tracking-tight text-white/90"
            >
              Pulse is watching.
            </motion.p>
          )}
          {stage >= 3 && (
            <motion.p
              key="tagline"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1 }}
              className="text-xl font-light tracking-tight text-white/70"
            >
              Every match has a pulse. This is how it feels.
            </motion.p>
          )}
        </AnimatePresence>
      </div>

      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: stage >= 1 && !leaving ? 0.4 : 0 }}
        transition={{ delay: 1.5 }}
        className="absolute bottom-8 text-xs tracking-wide text-white/40"
      >
        tap to skip
      </motion.span>
    </motion.div>
  );
}
