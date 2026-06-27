/** UI-facing types derived from the wire contract. */
import type { WireTimeline } from "@/types/wire";

export type Side = "home" | "away";

export type ConnectionStatus =
  | "idle"
  | "connecting"
  | "live"
  | "ended"
  | "error";

/** The mood of a Pulse line — drives typography and motion, not content. */
export type StoryTone = "calm" | "rising" | "peak" | "reflective";

export interface StoryLine {
  id: string;
  text: string;
  tone: StoryTone;
  /** Eruption lines (goals) get the loudest treatment. */
  emphatic?: boolean;
}

export interface TimelineEntry extends WireTimeline {
  id: string;
}

export interface GoalFlash {
  side: Side;
  key: number;
}

/** One captured frame for the recap heartbeat curve. */
export interface Sample {
  minute: number;
  bpm: number;
  stars: number;
}

export interface Meta {
  home: string;
  away: string;
  matchId: string;
}
