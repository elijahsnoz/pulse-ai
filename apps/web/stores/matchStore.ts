/**
 * The single client-side mirror of the live match.
 *
 * Fed exclusively by the WebSocket stream (via `useMatchStream`). Components
 * subscribe to narrow slices so a heartbeat tick never re-renders the timeline.
 * No business logic lives here — only presentation state.
 */
import { create } from "zustand";

import type {
  ConnectionStatus,
  GoalFlash,
  Meta,
  Sample,
  StoryLine,
  TimelineEntry,
} from "@/types/match";
import type { WireSnapshot } from "@/types/wire";

interface MatchState {
  status: ConnectionStatus;
  meta: Meta | null;
  snapshot: WireSnapshot | null;
  timeline: TimelineEntry[];
  story: StoryLine | null;
  goalFlash: GoalFlash | null;
  samples: Sample[];
  peakBpm: number;
  peakBpmMinute: number;

  // actions
  setStatus: (status: ConnectionStatus) => void;
  setMeta: (meta: Meta) => void;
  applySnapshot: (snapshot: WireSnapshot) => void;
  addTimeline: (entry: TimelineEntry) => void;
  setStory: (story: StoryLine) => void;
  fireGoalFlash: (flash: GoalFlash) => void;
  clearGoalFlash: () => void;
  reset: () => void;
}

const initial = {
  status: "idle" as ConnectionStatus,
  meta: null,
  snapshot: null,
  timeline: [] as TimelineEntry[],
  story: null,
  goalFlash: null,
  samples: [] as Sample[],
  peakBpm: 0,
  peakBpmMinute: 0,
};

export const useMatchStore = create<MatchState>((set) => ({
  ...initial,

  setStatus: (status) => set({ status }),

  setMeta: (meta) => set({ meta }),

  applySnapshot: (snapshot) =>
    set((state) => {
      const bpm = snapshot.pulse.bpm;
      const isPeak = bpm > state.peakBpm;
      return {
        snapshot,
        samples: [
          ...state.samples,
          { minute: snapshot.minute, bpm, stars: snapshot.drama.stars },
        ],
        peakBpm: isPeak ? bpm : state.peakBpm,
        peakBpmMinute: isPeak ? snapshot.minute : state.peakBpmMinute,
      };
    }),

  addTimeline: (entry) =>
    set((state) => ({ timeline: [entry, ...state.timeline] })),

  setStory: (story) => set({ story }),

  fireGoalFlash: (goalFlash) => set({ goalFlash }),
  clearGoalFlash: () => set({ goalFlash: null }),

  reset: () => set({ ...initial }),
}));
