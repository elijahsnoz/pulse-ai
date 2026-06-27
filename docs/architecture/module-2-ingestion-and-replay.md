# Module 2 — Event Ingestion & Replay (Architecture)

> **Governing principle (v1, non-negotiable):**
> **Replay is a first-class feature, not a debugging tool.**
> Every event entering the pipeline must be **recordable, serializable,
> replayable, verifiable, and reproducible**. The replay path must produce
> **byte-for-byte identical `MatchSnapshot`s** to the live path. There is exactly
> **one pipeline** — there is no separate "live logic" and "replay logic."

This principle is an *architectural invariant*. Every component below is shaped by
it. If a design choice would create two code paths, it is wrong by definition.

---

## 1. The One-Pipeline Model

Live TxLINE and Replay are **two sources behind one identical pipeline**. They
differ only in (a) where frames come from and (b) the pacing of emission — never
in how a frame becomes a snapshot.

```
            ┌─────────────────── SOURCE (SportsDataProvider port) ───────────────────┐
   LIVE  →  │  TxLineProvider     poll TxLINE → normalize → assign sequence → dedupe   │
            │                                                                          │ ── emits canonical
   REPLAY → │  RecordedProvider   read tape (ordered frames)                           │    MatchFrames
            └──────────────────────────────────────────────────────────────────────────┘
                                            │
                                            ▼  (identical from here down — the ONE pipeline)
                          ┌─────────────────────────────────────────┐
                          │  Recorder (tee)   append frame → tape     │  ← recording is a
                          ├─────────────────────────────────────────┤     cross-cutting tee,
                          │  MatchReducer     fold frame → snapshot   │     not separate logic
                          │     uses Module 1 MetricEngine (pure)     │
                          ├─────────────────────────────────────────┤
                          │  Fingerprint      hash snapshot content   │
                          ├─────────────────────────────────────────┤
                          │  SnapshotSink     persist snapshot+hash   │
                          ├─────────────────────────────────────────┤
                          │  EventPublisher   emit downstream (WS)     │  ← port; Module 3 impl
                          └─────────────────────────────────────────┘
```

**The only differences between live and replay:**

| Aspect | Live | Replay |
| --- | --- | --- |
| Frame source | `TxLineProvider` (network) | `RecordedProvider` (storage) |
| Recording | Recorder **writes** the tape | Recorder is a **no-op / idempotent** |
| Pacing | real arrival | chosen speed (1×, 4×, instant) |
| Frame → snapshot | **identical reducer** | **identical reducer** |

Everything from the Recorder down is byte-identical because it is *the same code
running over the same inputs*.

---

## 2. The Determinism Contract

> Let **T** = an ordered tape of canonical frames, **C** = a `MetricConfig`
> version, **V** = the engine/normalizer code version.
> `reduce(T, C, V) → [MatchSnapshot]` is a **pure, total function**.
> For any execution on any machine with the same (T, C, V), the output is
> **bit-identical**.

Because the live path *produces* T while reducing it, and the replay path *reads*
the same T and reduces it with the same (C, V), their snapshot streams are
identical by construction. The fingerprint (§6) is how we cheaply *prove* it.

This is only possible if **every input to `reduce` lives inside T**, and **no
hidden input** (wall clock, RNG, DB key, network timing) can leak in. §4 is the
firewall that guarantees that.

---

## 3. The Canonical Unit: `MatchFrame`

A **`MatchFrame`** is the atomic thing that enters the pipeline and the atomic
thing we record. It is the seam where "an event enters the pipeline."

A frame is one of:
- **EventFrame** — wraps a Module 1 domain `MatchEvent` (goal, shot, card …).
- **TickFrame** — a clock advance carrying only a `match_minute` (lets the
  heartbeat evolve via time-decay between events; see §5).

Every frame carries:
```
sequence       monotonic, gap-free order key within a match (assigned at ingest)
match_minute   the canonical clock position (NEVER wall-clock; see §5)
kind           event | tick
provider_event_id   (event frames) for idempotent dedupe — nullable for ticks
payload        the serialized domain event (event frames only)
```

The frame is the contract for all five required capabilities:

| Capability | Mechanism |
| --- | --- |
| **Recorded** | Recorder tee appends every frame to the tape (append-only), in sequence order |
| **Serialized** | Versioned canonical encoding: stable key order, integer `sequence`, fixed-precision `match_minute`, `schema_version` stamped |
| **Replayed** | `RecordedProvider` reads frames and feeds the *same* pipeline |
| **Verified** | `ReplayVerifier` re-reduces the tape and compares snapshot fingerprints to those stored (§6, §8) |
| **Reproduced** | Pure `reduce(T,C,V)` + fully-captured inputs → anyone re-runs and gets the same result |

---

## 4. The Non-Determinism Firewall

Reproducibility fails the instant a hidden, run-varying input reaches `reduce`.
Each such source is **quarantined to one place, upstream of the tape**, so the
recorded frames already bake in the resolved value.

| Hazard | Where it is allowed to exist | How it is neutralised |
| --- | --- | --- |
| **Wall clock** | only in the live `MatchClock` | clock maps real time → `match_minute` *once*, bakes it into the frame; pipeline reads `frame.match_minute`, never `now()` |
| **Out-of-order / duplicate events** | only in `TxLineProvider` normalization | dedupe on `provider_event_id`; assign deterministic `sequence`; tape stores the canonical, deduped order |
| **Score lag/disagreement** | normalization | scoreline is **derived by folding goal events** in the tape (single source of truth); TxLINE's score field is used only to *validate* at ingest |
| **DB surrogate keys / `recorded_at`** | persistence | stored as **sidecar** columns; **excluded** from the snapshot and its fingerprint |
| **Replay speed / pacing** | replay driver | changes *when* frames emit, not *what* they are — snapshot values depend on `match_minute` (data), not elapsed real time |
| **Randomness** | nowhere | forbidden in the pipeline (Module 1 already has none) |
| **Config drift** | `MetricConfig` | tape header pins `config_version`; reproduction guaranteed within a pinned version (§7) |

**Module 1 stays frozen.** The pipeline calls `MetricEngine.evaluate(events,
minute, scoreline, previous)` exactly as v1.0 defines it. `match_minute` and the
folded scoreline come from frames; `TickFrame` is a Module-2 concept, so **no
change to the v1.0 domain contract is required.**

---

## 5. Clock & Ticks (quarantining wall-time)

The heartbeat must evolve between events (momentum time-decays). That requires
evaluations at minutes where no event occurred — i.e. **TickFrames**.

- **Live:** a `MatchClock` converts wall-time-since-kickoff into `match_minute`
  and emits a `TickFrame` at a fixed **match-minute cadence** (proposed: every
  0.25 match-minute / 15s). Each emitted tick is recorded into the tape.
- **Replay:** the recorded TickFrames are replayed like any other frame.

Because ticks are *recorded frames*, the evaluation schedule is captured in the
tape and reproduced exactly — the live↔replay snapshot streams line up 1:1. (A
storage-lighter alternative — regenerating ticks from a recorded grid policy
instead of storing them — is noted as a future optimization in §11; explicit
recording is chosen first for robustness against non-linear clocks like halftime
and stoppage.)

---

## 6. Snapshot Fingerprint (the proof of identity)

Each `MatchSnapshot` is stored with a **fingerprint**: a SHA-256 over a canonical
serialization of its *semantic content only* —

```
metric values (fixed precision), enum values (phase, emotion, bands),
fan_read fields, ordered explanation contributors, match_minute, scoreline
```

Explicitly **excluded**: DB ids, `recorded_at`, any storage metadata.

Within a pinned (code, config) version, snapshots are bit-identical, so the
fingerprint is a cheap, total equality check. Verification = recompute the
fingerprint from a re-reduce and assert it equals the stored one.

---

## 7. Data Model (refines Module 1's storage plan)

```
match_tape            -- the authoritative, append-only frame log (the "tape")
  id (sidecar)        match_id   sequence   kind   provider_event_id
  match_minute        event_type payload(JSONB)   recorded_at (sidecar)
  UNIQUE(match_id, sequence)            -- gap-free order
  UNIQUE(match_id, provider_event_id)   -- idempotent dedupe (event frames)

match_snapshots       -- derived outputs of reduce()
  id (sidecar)        match_id   frame_sequence   match_minute
  content(JSONB)      fingerprint(text)   recorded_at (sidecar)

match_tape_header     -- reproduction pinning
  match_id   kickoff_anchor   tick_cadence
  engine_version   config_version   normalizer_version   schema_version
```

`match_tape` supersedes Module 1's sketch of `match_events` (now including ticks).
`match_snapshots` gains `fingerprint` + a pointer to the producing `frame_sequence`.

---

## 8. Ports, Components & Clean-Architecture placement

**application/ (Module 2 — new):**
- `ports/SportsDataProvider` — `frames(match_id) -> Iterator[MatchFrame]`
- `ports/TapeStore` — append/read frames; `ports/SnapshotSink` — persist snapshots;
  `ports/EventPublisher` — emit downstream (impl in Module 3)
- `dto/MatchFrame` (+ canonical serialization & `schema_version`)
- `services/MatchReducer` — folds frames → snapshots via Module 1 `MetricEngine`
  (accumulates event list + derived scoreline + previous snapshot; deterministic)
- `services/Fingerprint` — canonical hash
- `use_cases/IngestLiveMatch`, `ReplayMatch`, `VerifyReplay`

**infrastructure/ (Module 2 — new):**
- `txline/TxLineProvider` (live; implements the port) — the **only** home of
  network, retries, dedupe, wall-clock
- `replay/RecordedProvider` (reads tape; implements the **same** port)
- `recording/Recorder` (tee decorator around any provider)
- `clock/MatchClock` (wall→match-minute; live only)
- `persistence/` (TapeStore + SnapshotSink: file/JSON tapes first, Postgres later
  behind the same ports)

**domain/ (Module 1):** untouched, frozen at v1.0.

The pipeline depends only on **ports**, so swapping live↔replay, or file↔Postgres,
is an adapter change — never a logic change. This is the structural enforcement of
"one pipeline."

---

## 9. Verification Strategy (the principle, as tests)

1. **Golden tape:** commit a recorded match tape + its expected snapshot
   fingerprints. Test asserts `reduce(tape)` reproduces them exactly.
2. **Round-trip:** drive a synthetic live source → capture the tape → replay it →
   assert the replayed snapshots are byte-identical to the live ones.
3. **Idempotency:** inject duplicate / out-of-order provider events → assert the
   canonical tape (and thus snapshots) is unchanged.
4. **Serialization round-trip:** `frame → serialize → deserialize → frame` is
   identity; fingerprints are stable across processes.
5. **`VerifyReplay` as a guard:** the same check is runnable in CI on every tape,
   not just in unit tests — replay fidelity is a continuously-enforced invariant.

---

## 10. Pacing ≠ Determinism (why replay can be fast *and* faithful)

Snapshot values are a function of `match_minute` (recorded data), not of real
elapsed time. So the replay driver may emit frames at 1×, 4×, or instantly: the
*timing* of client updates changes, the *content* does not. This is what lets a
judge scrub/fast-forward a match while every number stays exactly what it was
live.

---

## 11. Versioning, caveats & future optimizations

- **"Byte-for-byte forever" is scoped to a pinned (engine, config, normalizer,
  schema) version.** The tape header records all four. Changing any of them is an
  explicit, versioned migration — reproduction is guaranteed *within* a version,
  and `VerifyReplay` flags drift across versions.
- **Future optimization:** regenerate ticks from a recorded grid policy instead of
  storing every TickFrame (storage-light), once the live clock model (halftime,
  stoppage) is settled.
- **Future:** archive raw TxLINE payloads in cold storage for forensic
  re-normalization — *off* the deterministic path; the canonical tape remains the
  authority.

---

## 12. MVP build order (recorded-first, judge-safe)

Mirrors the locked decision *"recorded match first, live TxLINE as fallback."*

1. `MatchFrame` + canonical serialization + `schema_version`.
2. `MatchReducer` over Module 1 engine + `Fingerprint`.
3. `RecordedProvider` + file/JSON `TapeStore` + a committed **golden tape**.
4. `ReplayMatch` use case + `VerifyReplay` + the verification test suite (proves
   the principle end-to-end before any network code exists).
5. `Recorder` tee + `IngestLiveMatch` wiring.
6. `TxLineProvider` skeleton implementing the **same** port (live creds wired when
   available) — demonstrating one-pipeline parity even pre-live.

Reaching step 4 already *demonstrates the governing principle* with zero TxLINE
dependency — the safest possible position for a hackathon demo.
```
