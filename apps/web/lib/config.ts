/** Connection configuration for the Pulse backend stream. */

export const PULSE_WS_BASE =
  process.env.NEXT_PUBLIC_PULSE_WS_URL ?? "ws://localhost:8000";

export const DEFAULT_MATCH_ID =
  process.env.NEXT_PUBLIC_PULSE_MATCH_ID ?? "demo";

/** match-minutes per real second; the backend paces the stream to this. */
export const DEFAULT_SPEED = 2.5;

export function matchSocketUrl(matchId: string, speed: number): string {
  return `${PULSE_WS_BASE}/ws/match/${encodeURIComponent(matchId)}?speed=${speed}`;
}
