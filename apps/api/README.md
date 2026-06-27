# Pulse Domain & Metric Engine

> Module 1 of Pulse — *The AI Second Screen for Every Football Match.*

A **standalone, dependency-free** Python library that turns a stream of match
events into branded, explainable, **deterministic** match intelligence. No ML, no
LLMs, no randomness — replaying the same match always produces identical output.

## Why it's built this way

This is the product's intellectual property and the foundation every later
subsystem (WebSocket, Story Engine, Recap, Replay) depends on. It is therefore
written like an open-source library: Clean-Architecture domain layer, full
docstrings, near-100% test coverage, and **zero magic numbers** (everything lives
in `MetricConfig`).

## The branded metrics

| Metric | Range | Meaning |
| --- | --- | --- |
| **Pulse Score** | 0–100 | Overall match intensity (drives the heartbeat) |
| **Pressure Index** | 0–100 | One side's sustained attacking pressure (per team) |
| **Momentum Vector** | −100–100 | Who's on top now (+home / −away), with direction |
| **Drama Index** | 0–100 | Intensity amplified by stakes (lateness, margin, red cards) |
| **Confidence Score** | 0–100 | Trust in the deterministic *signal* (not AI confidence) |
| **Match Phase** | enum | Narrative chapter (Opening … Critical Phase … Stoppage) |
| **Emotional State** | enum | How it *feels* (Calm … Explosive … Desperate) |

Every metric returns an **additive `Explanation`** — its contributors sum to the
value — so the Story Engine can verbalise *why*, not just *what*.

## Quick start

```python
from pulse.domain import MetricEngine, Scoreline
from pulse.domain.events.football import ShotEvent, GoalEvent
from pulse.domain.value_objects.side import Side

engine = MetricEngine()  # uses DEFAULT_CONFIG; pass MetricConfig(...) to tune
events = [
    ShotEvent(event_id="e1", sequence=1, minute=82.0, side=Side.HOME, on_target=True),
    GoalEvent(event_id="e2", sequence=2, minute=83.0, side=Side.HOME),
]
state = engine.evaluate(events=events, minute=84.0, scoreline=Scoreline(home=1, away=1))

print(state.pulse.value, state.emotion.label, state.phase.label)
print(state.momentum.explanation.top_contributors())
```

## Design guarantees

- **Deterministic** — pure functions of `(events, minute, scoreline, config)`.
- **Sport-agnostic core** — `MatchEvent` has zero football assumptions; football
  lives in subclasses and is detected via `kind` (weights) and `tags` (semantics).
- **Explainable** — additive contributor breakdown on every metric.
- **Configurable** — tune feel via `MetricConfig`, never by editing logic.

## Tests

```bash
cd apps/api
pip install -e ".[test]"
pytest
```

Table-driven tests target near-100% coverage of the domain layer, including a
determinism suite that asserts shuffled-input and repeated evaluation produce
byte-identical results.
