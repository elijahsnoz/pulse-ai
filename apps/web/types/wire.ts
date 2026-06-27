/**
 * Wire types — the FROZEN backend WebSocket contract.
 *
 * These mirror `pulse.presentation.serialization` exactly. The frontend never
 * sees raw engineering internals; it receives fan-facing values + bands.
 */

export type Band = "Dormant" | "Simmering" | "Heating" | "Electric" | "Frenzied";
export type MomentumDirection = "home" | "away" | "neutral";
export type Certainty = "Tentative" | "Measured" | "Confident";

export type TimelineKind =
  | "goal"
  | "card"
  | "momentum_shift"
  | "pulse_moment"
  | "phase_changed"
  | "emotion_changed";

export interface WireMeta {
  type: "meta";
  match_id: string;
  home: string;
  away: string;
}

export interface WireSnapshot {
  type: "snapshot";
  minute: number;
  score: { home: number; away: number };
  pulse: { value: number; band: Band; bpm: number };
  drama: { value: number; band: Band; stars: number };
  momentum: { value: number; direction: MomentumDirection; band: Band };
  pressure: { home: number; away: number };
  phase: string;
  emotion: string;
  certainty: Certainty;
}

export interface WireTimeline {
  type: "timeline";
  kind: TimelineKind;
  sequence: number;
  minute: number;
  icon: string;
  text: string;
}

export interface WireEnd {
  type: "end";
}

export type WireMessage = WireMeta | WireSnapshot | WireTimeline | WireEnd;
