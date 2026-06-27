# Module 1 — Tracked Technical Debt

These are **known, accepted** items recorded at the Module 1 v1.0 freeze. None are
correctness bugs or freeze blockers. They are documented so they are not
rediscovered as surprises, and so a future module can address them deliberately.

| # | Item | Risk | Proposed direction | Severity |
|---|------|------|--------------------|----------|
| TD-1 | **Unknown event handling is silent.** `MetricConfig.weight_for` returns `0.0` for any unrecognised event `kind`. A typo'd or unregistered `kind` on a future event contributes nothing with no error. | A new event type could silently fail to influence the metrics. | Introduce a registered-kinds set and/or a strict mode (used in tests/CI) that raises on an unknown `kind`. Keep lenient `0.0` behaviour in production. | Low |
| TD-2 | **Duplicated value storage.** Each branded metric value object stores both `.value` and `.explanation.value` — the same number in two places, kept equal by construction/convention rather than enforced. | A future edit could let them diverge. | Either derive one from the other, or add a lightweight post-init equality assertion on the metric value objects. | Low |

## Notes
- Both items are contained within the domain layer and do not affect the public
  contract; addressing either is a backward-compatible, additive change.
- Revisit when Module 2 (ingestion) introduces new event kinds — that is the
  natural moment to land TD-1.
