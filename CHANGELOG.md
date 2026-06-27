# Changelog — Pulse

All notable changes to the Pulse experience. Backend contracts (metric engine,
WebSocket, replay) are frozen; frontend changes never alter them.

## [Unreleased] — Experience Continuity Sprint

### Changed — the recap is no longer a dead end
- **Recap is now a cinematic layer, not a terminal screen.** It rises as a sheet
  over the *still-living* completed match, which blurs, dims, and recedes behind
  it (depth + parallax + subtle scaling). The match underneath is preserved.
- **Replaced "Watch it again"** with three meaningful, graceful paths:
  - **Continue exploring (primary)** — dismisses the recap and returns to the
    final match state, fully interactive: timeline, heartbeat, AI story, momentum
    and final score remain explorable.
  - **Replay** — resets to kickoff and re-streams immediately (intro skipped).
  - **Replay from the beginning** — replays the cinematic intro, then kickoff.
- **Added Share recap** — a designed, portrait, share-ready card (branding, final
  score, headline, heartbeat curve, peak rate). Copy-link works today; image
  export for X / Instagram / WhatsApp is signposted as next.

### Added — no screen ever traps the user
- **EndBar** — after Continue exploring, a floating pill offers "View recap" and
  "Replay", so the recap is always one tap away and exploring never dead-ends.

### Added — emotional release at full time
- The **heartbeat slows** to a calm resting beat and cools to blue.
- The **AmbientField cools** the whole interface to its calmest hue.
- The recap typography **breathes** (generous spacing, staggered reveal).

### Notes
- No backend, WebSocket, or replay-architecture changes.
- `next build` compiles clean (~153 kB first load); reduced-motion respected.

---

## [0.3.0] — Demo Day Polish Sprint
- Cinematic intro (black → heartbeat → "Pulse is watching." → match).
- AmbientField: interface colour evolves with the drama band.
- Heartbeat reborn as the logo: organic lub-dub, breath, rings, drama glow,
  hard goal spike.
- Goals erupt: bloom + white flash + edge vignette + score punch.
- Warmer voice lines; stronger recap ("Most emotional moment"); Apple-grade type.

## [0.2.0] — Production Frontend
- Next.js 15 + React 19 + TS + Tailwind + Framer Motion + Zustand companion UI
  consuming the frozen WebSocket stream. Heartbeat, AI story card, tug-of-war
  momentum, drama stars, prioritised timeline, cinematic recap, goal moments.
- `lib/voice`: deterministic Pulse voice (Character Bible), swappable for the
  future LLM Story Engine.

## [0.1.0] — Backend (Modules 1–2)
- Module 1: deterministic domain & metric engine (frozen `v1.0`).
- Module 2: ingestion + replay pipeline, reducer, timeline events, VerifyReplay,
  TxLINE provider, FastAPI + WebSocket demo.
