"use client";

/**
 * MatchExperience — the single client orchestrator.
 *
 * Opens the stream, decides loading/error/live, and lays out the experience in
 * the priority order of the design: heartbeat & story at the heart, score above,
 * supporting visuals around, timeline alongside, recap at the end.
 */
import { AnimatePresence } from "framer-motion";
import { useState } from "react";

import { ErrorState, LoadingState } from "@/components/ConnectionState";
import { DramaStars } from "@/components/drama/DramaStars";
import { AmbientField } from "@/components/effects/AmbientField";
import { GoalFlash } from "@/components/effects/GoalFlash";
import { Heartbeat } from "@/components/heartbeat/Heartbeat";
import { Intro } from "@/components/intro/Intro";
import { TugOfWar } from "@/components/momentum/TugOfWar";
import { Recap } from "@/components/recap/Recap";
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

export function MatchExperience() {
  const { replay } = useMatchStream();
  const status = useMatchStore((s) => s.status);
  const hasSnapshot = useMatchStore((s) => s.snapshot !== null);
  const [introDone, setIntroDone] = useState(false);

  const showLoading = !hasSnapshot && (status === "connecting" || status === "idle");
  const showError = status === "error" && !hasSnapshot;

  return (
    <main className="relative mx-auto min-h-screen w-full max-w-6xl px-4 pb-16 pt-6 sm:px-6">
      <AmbientField />
      <GoalFlash />
      <Recap onReplay={replay} />
      <AnimatePresence>
        {!introDone && <Intro onDone={() => setIntroDone(true)} />}
      </AnimatePresence>

      <header className="mb-6 flex items-center justify-between">
        <div className="text-lg font-extrabold tracking-tight text-white">
          PULSE<span className="text-ember">.</span>
          <span className="ml-2 text-xs font-medium text-white/35">
            AI Second Screen
          </span>
        </div>
        <StatusDot />
      </header>

      {showLoading ? (
        <LoadingState />
      ) : showError ? (
        <ErrorState onRetry={replay} />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[1.45fr_1fr]">
          {/* Hero column */}
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

          {/* Timeline column */}
          <section className="lg:sticky lg:top-6 lg:h-[78vh]">
            <Panel className="h-full">
              <Timeline />
            </Panel>
          </section>
        </div>
      )}
    </main>
  );
}
