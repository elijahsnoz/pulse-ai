# Pulse — Web (Production Frontend)

> Pulse lets fans **feel** a football match, not just follow it.

The AI second-screen companion UI. It consumes the **frozen** FastAPI WebSocket
contract and turns deterministic metrics into emotion: a living heartbeat, a
single warm AI sentence, a tug-of-war for momentum, drama in stars, an animated
timeline, goal eruptions, and a Spotify-Wrapped-style recap.

## Stack
Next.js 15 (App Router) · React 19 · TypeScript · Tailwind CSS · Framer Motion ·
Zustand · Lucide.

## Run it

The backend must be streaming first (from `apps/api`):
```bash
cd ../api && PYTHONPATH=src ./.venv/bin/python -m uvicorn pulse.presentation.app:app
```

Then the frontend:
```bash
cp .env.local.example .env.local   # defaults to ws://localhost:8000
npm install
npm run dev        # http://localhost:3000
```

Production build: `npm run build && npm run start`.

## Architecture

```
app/                 App Router shell (layout, page, globals)
components/
  heartbeat/         the identity — a living, tempo-driven heart
  story/             the AI voice card (visual centre)
  score/             score, minute, phase & mood
  momentum/          tug-of-war (no numbers)
  drama/             drama as stars
  timeline/          prioritised event feed (goals dominate)
  recap/             cinematic end-of-match recap
  effects/           goal flash
  ui/                shared surfaces
hooks/useMatchStream WebSocket lifecycle + goal two-beat orchestration
stores/matchStore    Zustand mirror of the live match (narrow selectors)
lib/voice            Pulse's personality (Character Bible) — composes lines from
                     the signals; swappable for the LLM Story Engine later
types/               the frozen wire contract + UI types
```

### The Voice layer
The backend provides *signals* (emotion, phase, certainty, momentum direction,
drama, goals). `lib/voice` composes Pulse's spoken lines from those — present
tense, short, warm; certainty sets the strength of the verb; it erupts for goals
and stays silent in calm passages. This is presentation, not business logic, and
is designed so an LLM Story Engine can replace it behind the same interface.

### What is never shown
Raw Pulse/Pressure/Momentum values, the Confidence number, and any internal
explanations. Everything is visual or emotional.
