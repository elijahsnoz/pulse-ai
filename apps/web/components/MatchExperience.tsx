"use client";

/**
 * MatchExperience — the single client orchestrator.
 *
 * Opens the stream, decides loading/error/live, and lays out the experience. At
 * full time the recap rises as a LAYER over the still-living match (which blurs
 * and recedes behind it). Three graceful paths — Continue exploring, Replay,
 * Share — mean Pulse never reaches a dead end.
 */
import { AnimatePresence, motion } from "framer-motion";
import { RotateCcw, Sparkles } from "lucide-react";
import { useState } from "react";

import { ErrorState, LoadingState } from "@/components/ConnectionState";
import { DramaStars } from "@/components/drama/DramaStars";
import { AmbientField } from "@/components/effects/AmbientField";
import { GoalFlash } from "@/components/effects/GoalFlash";
import { Heartbeat } from "@/components/heartbeat/Heartbeat";
import { Intro } from "@/components/intro/Intro";
import { TugOfWar } from "@/components/momentum/TugOfWar";
import { Recap } from "@/components/recap/Recap";
import { ShareSheet } from "@/components/recap/ShareSheet";
import { ScoreBoard } from "@/components/score/ScoreBoard";
import { StoryCard } from "@/components/story/StoryCard";
import { Timeline } from "@/components/timeline/Timeline";
import { Panel } from "@/components/ui/Panel";
import { useMatchStream } from "@/hooks/useMatchStream";
import { useMatchStore } from "@/stores/matchStore";

function StatusDot() {
  const status = useMatchStore((s) => s.status);
  const live = status === "live";
  return (
    <div className="flex items-center gap-2 text-xs text-white/50">
      <span
        className={`h-2 w-2 rounded-full ${
          live ? "bg-emerald-400" : status === "ended" ? "bg-white/30" : "bg-amber-400"
        }`}
      />
      {live ? "live" : status === "ended" ? "full time" : status}
    </div>
  );
}

/** A floating, dismiss-proof way back to the recap or a replay — no dead ends. */
function EndBar({ onRecap, onReplay }: { onRecap: () => void; onReplay: () => void }) {
  return (
    <motion.div
      initial={{ y: 30, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: 30, opacity: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="fixed inset-x-0 bottom-5 z-30 flex justify-center"
    >
      <div className="flex items-center gap-1 rounded-full border border-white/10 bg-ink-700/80 p-1 shadow-xl backdrop-blur-md">
        <button
          type="button"
          onClick={onRecap}
          className="flex items-center gap-2 rounded-full bg-ember/90 px-4 py-2 text-sm font-semibold text-white transition hover:bg-ember"
        >
          <Sparkles className="h-4 w-4" /> View recap
        </button>
        <button
          type="button"
          onClick={onReplay}
          className="flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium text-white/75 transition hover:text-white"
        >
          <RotateCcw className="h-4 w-4" /> Replay
        </button>
      </div>
    </motion.div>
  );
}

export function MatchExperience() {
  const { replay } = useMatchStream();
  const status = useMatchStore((s) => s.status);
  const hasSnapshot = useMatchStore((s) => s.snapshot !== null);

  const [introDone, setIntroDone] = useState(false);
  const [recapDismissed, setRecapDismissed] = useState(false);
  const [shareOpen, setShareOpen] = useState(false);

  const ended = status === "ended";
  const recapOpen = ended && !recapDismissed && !shareOpen;
  const overlayUp = recapOpen || shareOpen;

  const showLoading = !hasSnapshot && (status === "connecting" || status === "idle");
  const showError = status === "error" && !hasSnapshot;

  // --- the three graceful paths -------------------------------------------
  const continueExploring = () => setRecapDismissed(true);
  const replayFromKickoff = () => {
    setShareOpen(false);
    setRecapDismissed(false);
    replay(); // resets + reconnects from kickoff (intro stays skipped)
  };
  const replayFromBeginning = () => {
    setShareOpen(false);
    setRecapDismissed(false);
    setIntroDone(false); // the cinematic open plays again
    replay();
  };

  return (
    <main className="relative mx-auto min-h-screen w-full max-w-6xl px-4 pb-16 pt-6 sm:px-6">
      <AmbientField />
      <GoalFlash />

      {/* The match stage. At full time it recedes behind the recap (depth). */}
      <motion.div
        animate={{
          scale: overlayUp ? 0.95 : 1,
          filter: overlayUp ? "blur(7px) brightness(0.55)" : "blur(0px) brightness(1)",
        }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        style={{ transformOrigin: "center top" }}
        className={overlayUp ? "pointer-events-none" : ""}
      >
        <header className="mb-6 flex items-center justify-between">
          <div className="text-lg font-extrabold tracking-tight text-white">
            PULSE<span className="text-ember">.</span>
            <span className="ml-2 text-xs font-medium text-white/35">AI Second Screen</span>
          </div>
          <StatusDot />
        </header>

        {showLoading ? (
          <LoadingState />
        ) : showError ? (
          <ErrorState onRetry={replayFromKickoff} />
        ) : (
          <div className="grid gap-6 lg:grid-cols-[1.45fr_1fr]">
            <section className="flex flex-col items-center gap-10">
              <ScoreBoard />
              <div className="flex min-h-[250px] w-full items-center justify-center pt-4">
                <Heartbeat />
              </div>
              <StoryCard />
              <Panel className="w-full">
                <div className="flex flex-col gap-6">
                  <TugOfWar />
                  <div className="flex justify-center">
                    <DramaStars />
                  </div>
                </div>
              </Panel>
            </section>

            <section className="lg:sticky lg:top-6 lg:h-[78vh]">
              <Panel className="h-full">
                <Timeline />
              </Panel>
            </section>
          </div>
        )}
      </motion.div>

      {/* Layers above the stage */}
      <Recap
        open={recapOpen}
        onContinue={continueExploring}
        onReplay={replayFromKickoff}
        onReplayFromStart={replayFromBeginning}
        onShare={() => setShareOpen(true)}
      />
      <ShareSheet open={shareOpen} onClose={() => setShareOpen(false)} />

      {/* After dismissing the recap, a graceful way back — never trapped. */}
      <AnimatePresence>
        {ended && recapDismissed && !shareOpen && (
          <EndBar
            onRecap={() => setRecapDismissed(false)}
            onReplay={replayFromKickoff}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {!introDone && <Intro onDone={() => setIntroDone(true)} />}
      </AnimatePresence>
    </main>
  );
}
