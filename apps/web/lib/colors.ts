/** Emotion-driven color language. Bands become heat, not numbers. */
import type { Band } from "@/types/wire";

export interface BandTheme {
  /** Core color of the heartbeat at this intensity. */
  color: string;
  /** Soft glow color (rgba). */
  glow: string;
  /** Human label kept for accessibility only. */
  label: Band;
}

const BANDS: Record<Band, BandTheme> = {
  Dormant: { color: "#5b7cff", glow: "rgba(91,124,255,0.45)", label: "Dormant" },
  Simmering: { color: "#33d98b", glow: "rgba(51,217,139,0.45)", label: "Simmering" },
  Heating: { color: "#ffd166", glow: "rgba(255,209,102,0.50)", label: "Heating" },
  Electric: { color: "#ff9f1c", glow: "rgba(255,159,28,0.55)", label: "Electric" },
  Frenzied: { color: "#ff3b6b", glow: "rgba(255,59,107,0.65)", label: "Frenzied" },
};

export function bandTheme(band: Band): BandTheme {
  return BANDS[band] ?? BANDS.Dormant;
}

const ORDER: Band[] = ["Dormant", "Simmering", "Heating", "Electric", "Frenzied"];

/** 0..1 intensity for scaling the heartbeat size, derived from the band. */
export function bandIntensity(band: Band): number {
  const i = ORDER.indexOf(band);
  return i < 0 ? 0 : i / (ORDER.length - 1);
}

export const TEAM_COLORS = {
  home: "#52b1ff",
  away: "#ff5d73",
} as const;
