"use client";

/** Loading + error states — never a blank screen. */
import { motion } from "framer-motion";

export function LoadingState() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-5 text-center">
      <motion.div
        animate={{ scale: [1, 1.15, 1], opacity: [0.6, 1, 0.6] }}
        transition={{ duration: 1.1, repeat: Infinity, ease: "easeInOut" }}
        className="text-6xl"
      >
        ❤️
      </motion.div>
      <p className="text-white/60">Tuning into the match&hellip;</p>
    </div>
  );
}

export function ErrorState({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-5 text-center">
      <div className="text-5xl opacity-60">💔</div>
      <div>
        <p className="text-lg font-semibold text-white">Lost the connection</p>
        <p className="mt-1 text-sm text-white/50">
          Make sure the Pulse backend is running on its WebSocket.
        </p>
      </div>
      <button
        onClick={onRetry}
        className="rounded-xl bg-white/10 px-5 py-2.5 font-semibold text-white ring-1 ring-white/15 transition hover:bg-white/15"
      >
        Reconnect
      </button>
    </div>
  );
}
