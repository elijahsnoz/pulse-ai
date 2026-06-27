/**
 * The Voice of Pulse.
 *
 * Composes Pulse's spoken lines from the deterministic signals the backend
 * already provides (emotion, phase, certainty, momentum direction, drama,
 * goals/cards/shifts). This is presentation — turning metrics into emotion —
 * not business logic. It follows the Pulse Character Bible:
 *   - present tense, short, warm, dry; names the feeling, not the number
 *   - certainty sets the strength of the verb, never the warmth
 *   - speaks rarely; earns its silence; erupts only for real peaks
 *
 * Designed so a future LLM Story Engine can replace this module behind the
 * same `Narrator` interface.
 */
import type { Meta, StoryLine, StoryTone } from "@/types/match";
import type {
  Certainty,
  MomentumDirection,
  WireSnapshot,
  WireTimeline,
} from "@/types/wire";

let counter = 0;
const nextId = () => `line-${++counter}`;

function line(text: string, tone: StoryTone, emphatic = false): StoryLine {
  return { id: nextId(), text, tone, emphatic };
}

function pick<T>(items: T[], seed: number): T {
  return items[((seed % items.length) + items.length) % items.length];
}

function teamFor(dir: MomentumDirection, meta: Meta): string {
  if (dir === "home") return meta.home;
  if (dir === "away") return meta.away;
  return "";
}

function otherTeam(dir: MomentumDirection, meta: Meta): string {
  if (dir === "home") return meta.away;
  if (dir === "away") return meta.home;
  return "";
}

/** Certainty decides how strong the verb is — never how warm the tone is. */
function controlVerb(c: Certainty, seed: number): string {
  if (c === "Confident") {
    return pick(["are taking control", "have seized this", "are running the game now"], seed);
  }
  if (c === "Measured") {
    return pick(["look the likelier side", "are starting to take over", "seem to be edging it"], seed);
  }
  return pick(["might be finding something", "are stirring", "could be turning this"], seed);
}

const BAND_GAP: Record<string, number> = {
  Frenzied: 2,
  Electric: 2,
  Heating: 4,
};

interface Ctx {
  lastSpokenMinute: number;
  lastDir: MomentumDirection | null;
  lastEmotion: string | null;
  spokeOpening: boolean;
  stoppageAnnounced: boolean;
}

export interface Narrator {
  /** A non-goal timeline event may produce a line (or stay silent). */
  onTimeline(evt: WireTimeline, snap: WireSnapshot | null, meta: Meta): StoryLine | null;
  /** Ambient narration between events, governed by cadence + silence rules. */
  onSnapshot(snap: WireSnapshot, meta: Meta): StoryLine | null;
  /** Goal beat 1 — the eruption (instant). */
  goalEruption(side: "home" | "away", meta: Meta): StoryLine;
  /** Goal beat 2 — the meaning (a breath later). */
  goalMeaning(side: "home" | "away", snap: WireSnapshot | null, meta: Meta): StoryLine;
}

export function createNarrator(): Narrator {
  const ctx: Ctx = {
    lastSpokenMinute: -999,
    lastDir: null,
    lastEmotion: null,
    spokeOpening: false,
    stoppageAnnounced: false,
  };

  const markSpoken = (minute: number) => {
    ctx.lastSpokenMinute = minute;
  };

  return {
    onTimeline(evt, snap, meta) {
      const seed = evt.sequence;
      const certainty = snap?.certainty ?? "Measured";

      if (evt.kind === "card" && evt.icon === "🟥") {
        // A red card ruptures the match — Pulse always notes it.
        const team = evt.text.includes(meta.home) ? meta.home : meta.away;
        markSpoken(evt.minute);
        return line(
          pick(
            [
              `Down to ten — ${team}. This changes everything.`,
              `Red card. ${team} have it all to do now.`,
              `${team} are a man light. The shape of the match just shifted.`,
            ],
            seed,
          ),
          "rising",
        );
      }

      if (evt.kind === "momentum_shift" && snap) {
        const dir = snap.momentum.direction;
        const winner = teamFor(dir, meta);
        if (!winner) return null;
        markSpoken(evt.minute);
        ctx.lastDir = dir;
        const loser = otherTeam(dir, meta);
        return line(
          pick(
            [
              `The game's tilting. ${winner} ${controlVerb(certainty, seed)}.`,
              `${winner} ${controlVerb(certainty, seed)} — ${loser} hanging on.`,
              `Feel that shift? ${winner} have found a gear.`,
            ],
            seed,
          ),
          "rising",
        );
      }

      if (evt.kind === "phase_changed" && evt.text === "Stoppage Time" && !ctx.stoppageAnnounced) {
        ctx.stoppageAnnounced = true;
        markSpoken(evt.minute);
        return line("Into stoppage time. Hold your breath.", "peak");
      }

      // Pulse moments, emotion/phase changes are ambient texture — usually silent.
      return null;
    },

    onSnapshot(snap, meta) {
      // A warm welcome on the very first frame.
      if (!ctx.spokeOpening) {
        ctx.spokeOpening = true;
        ctx.lastDir = snap.momentum.direction;
        ctx.lastEmotion = snap.emotion;
        markSpoken(snap.minute);
        return line("Here we go. Let's feel this one out.", "calm");
      }

      const dir = snap.momentum.direction;
      const emotion = snap.emotion;
      const band = snap.drama.band;

      const gap = BAND_GAP[band];
      const dirChanged = dir !== ctx.lastDir && dir !== "neutral";
      const emotionChanged = emotion !== ctx.lastEmotion;

      // Always track, even when staying silent.
      ctx.lastDir = dir;
      ctx.lastEmotion = emotion;

      // Silence in calm passages, or too soon after the last line.
      if (gap === undefined) return null;
      if (snap.minute - ctx.lastSpokenMinute < gap) return null;
      if (!dirChanged && !emotionChanged) return null;

      const seed = Math.floor(snap.minute);
      if (dirChanged) {
        const winner = teamFor(dir, meta);
        markSpoken(snap.minute);
        return line(`${winner} ${controlVerb(snap.certainty, seed)}.`, "rising");
      }

      // Mood-led ambient line (rare).
      markSpoken(snap.minute);
      return line(
        pick(
          [
            "End to end now — anything could happen.",
            "The tempo's climbing.",
            "You can feel this one tightening.",
          ],
          seed,
        ),
        "rising",
      );
    },

    goalEruption(side, meta) {
      const team = side === "home" ? meta.home : meta.away;
      return line(`GOOOAL.  ${team}.`, "peak", true);
    },

    goalMeaning(side, snap, meta) {
      const team = side === "home" ? meta.home : meta.away;
      const minute = snap?.minute ?? 0;
      const seed = Math.floor(minute) + (side === "home" ? 0 : 1);
      if (minute >= 80) {
        return line(
          pick(
            [
              `In the ${Math.floor(minute)}th. That could be the moment of the match.`,
              "So late. That might just be the winner.",
            ],
            seed,
          ),
          "peak",
        );
      }
      return line(
        pick(
          [
            "That's the pressure finally paying off.",
            `${team} have their goal — and they earned it.`,
            "Out of a tense spell, a moment of quality.",
          ],
          seed,
        ),
        "rising",
      );
    },
  };
}

/** Recap headline — one sentence that names the whole match's identity. */
export function matchHeadline(
  meta: Meta,
  finalScore: { home: number; away: number },
): string {
  const { home, away } = meta;
  const h = finalScore.home;
  const a = finalScore.away;
  if (h === a) {
    return `${home} and ${away} couldn't be separated — a match that gave nothing away.`;
  }
  const winner = h > a ? home : away;
  const margin = Math.abs(h - a);
  if (margin === 1) {
    return `A match decided by the finest margin — ${winner} found the moment that mattered.`;
  }
  return `${winner} pulled clear in the end — a night that slowly tilted their way.`;
}

/** Recap reflection — a warm closing line. */
export function matchReflection(finalScore: { home: number; away: number }): string {
  if (finalScore.home === finalScore.away) {
    return "Some matches end level and still feel like a story.";
  }
  return "Some matches are won with brilliance. This one was won with patience.";
}
