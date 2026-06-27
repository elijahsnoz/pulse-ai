/** The Pulse heart silhouette — shared by the intro and the live heartbeat. */
export const HEART_PATH =
  "M50 88 C 18 64, 4 44, 4 28 C 4 14, 15 6, 27 6 C 37 6, 45 12, 50 22 C 55 12, 63 6, 73 6 C 85 6, 96 14, 96 28 C 96 44, 82 64, 50 88 Z";

/** The organic lub-dub: a strong beat, a quick second, then rest. */
export const BEAT_KEYFRAMES = { scale: [1, 1.16, 1.0, 1.07, 1] };
export const BEAT_TIMES = [0, 0.12, 0.26, 0.4, 1];
