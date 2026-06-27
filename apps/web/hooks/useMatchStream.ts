"use client";

/**
 * useMatchStream — the bridge between the backend WebSocket and the store.
 *
 * Owns the socket lifecycle, parses the frozen wire contract, runs the Voice
 * narrator, and orchestrates the two-beat goal moment (eruption -> flash ->
 * meaning). Components never touch the socket; they read the store.
 */
import { useCallback, useEffect, useRef, useState } from "react";

import { DEFAULT_MATCH_ID, DEFAULT_SPEED, matchSocketUrl } from "@/lib/config";
import { createNarrator, type Narrator } from "@/lib/voice";
import { useMatchStore } from "@/stores/matchStore";
import type { Side } from "@/types/match";
import type { WireMessage, WireSnapshot } from "@/types/wire";

interface Options {
  matchId?: string;
  speed?: number;
}

export function useMatchStream({ matchId = DEFAULT_MATCH_ID, speed = DEFAULT_SPEED }: Options = {}) {
  const socketRef = useRef<WebSocket | null>(null);
  const narratorRef = useRef<Narrator>(createNarrator());
  const latestSnapshot = useRef<WireSnapshot | null>(null);
  const timers = useRef<ReturnType<typeof setTimeout>[]>([]);
  const seqRef = useRef(0);
  const [nonce, setNonce] = useState(0);

  const store = useMatchStore;

  const clearTimers = () => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
  };

  const replay = useCallback(() => {
    store.getState().reset();
    narratorRef.current = createNarrator();
    latestSnapshot.current = null;
    setNonce((n) => n + 1);
  }, [store]);

  useEffect(() => {
    const s = store.getState();
    s.setStatus("connecting");

    let closedByUs = false;
    const ws = new WebSocket(matchSocketUrl(matchId, speed));
    socketRef.current = ws;

    ws.onopen = () => store.getState().setStatus("live");

    ws.onmessage = (event) => {
      let msg: WireMessage;
      try {
        msg = JSON.parse(event.data as string) as WireMessage;
      } catch {
        return;
      }
      handleMessage(msg);
    };

    ws.onerror = () => {
      if (!closedByUs) store.getState().setStatus("error");
    };

    ws.onclose = () => {
      const st = store.getState().status;
      if (!closedByUs && st !== "ended") store.getState().setStatus("error");
    };

    function handleMessage(msg: WireMessage) {
      const api = store.getState();
      const narrator = narratorRef.current;
      const meta = () => store.getState().meta;

      if (msg.type === "meta") {
        api.setMeta({ home: msg.home, away: msg.away, matchId: msg.match_id });
        return;
      }

      if (msg.type === "snapshot") {
        latestSnapshot.current = msg;
        api.applySnapshot(msg);
        const m = meta();
        if (m) {
          const ambient = narrator.onSnapshot(msg, m);
          if (ambient) api.setStory(ambient);
        }
        return;
      }

      if (msg.type === "timeline") {
        const id = `tl-${msg.sequence}-${seqRef.current++}`;
        api.addTimeline({ ...msg, id });
        const m = meta();
        if (!m) return;

        if (msg.kind === "goal") {
          const side: Side = msg.text.includes(m.home) ? "home" : "away";
          // Beat 1: eruption + flash, instantly.
          api.setStory(narrator.goalEruption(side, m));
          api.fireGoalFlash({ side, key: msg.sequence });
          const t1 = setTimeout(() => store.getState().clearGoalFlash(), 1100);
          // Beat 2: the meaning, a breath later.
          const t2 = setTimeout(() => {
            store.getState().setStory(
              narrator.goalMeaning(side, latestSnapshot.current, m),
            );
          }, 1700);
          timers.current.push(t1, t2);
          return;
        }

        const reaction = narrator.onTimeline(msg, latestSnapshot.current, m);
        if (reaction) api.setStory(reaction);
        return;
      }

      if (msg.type === "end") {
        store.getState().setStatus("ended");
      }
    }

    return () => {
      closedByUs = true;
      clearTimers();
      ws.onopen = ws.onmessage = ws.onerror = ws.onclose = null;
      ws.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [matchId, speed, nonce]);

  return { replay };
}
