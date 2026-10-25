# 265 — Baroque Counter Duet

**Axis combo** (from `COMPOSITION_DESIGN_SPACE.md`, user pick "2-lead counter"):

| axis | pick |
|---|---|
| layer path | concrete-only |
| paradigm | Stochastic — **Markov 002** (scale-degree walk) |
| lead count | **1 lead + 1 counter** |
| percussion | none |
| harmonization | harpsichord continuo (sustained triads) |
| voice count | 4 — Violin · Viola · Harpsichord · Cello |
| register | non-crossing: cello 36–55 → harp 48–72 → viola 55–72 → violin 67–96 |
| density | lead 8ths w/ rests, counter fills the free 8ths |
| form | binary A A2 B B2 (4×4 = 16 bars) |
| humanization | classical (7 ms σ) |

## The counter (the point of this piece)

The second melodic voice is the engine's canonical **`HarmonyWriter.counterline()`**
(Phase 3 P2, commit `c5c73d7`), hard-enforcing both counter constraints:

- **contrast** — never sounds the lead's pitch class at the same time;
- **complementary density** — onsets only on grid slots the lead leaves free.

Viola (ch1) answers the violin lead (ch0) on the gaps. Verified 0 onset
collisions + 0 pitch-class doublings.

## Method

**Markov 002** — first-order walk over the 7 scale degrees with stepwise-biased
transition weights (leading tone resolves to I/V). Tiered pitch (P1): strong
beats snap to chord tones, weak stay in-scale.

## Files

- `MIDI/*-phase1.mid` — raw Markov draft (chromatic, off-grid)
- `MIDI/*-perfect.mid` — grid-locked rules-processed
- `MIDI/*-humanized.mid` — classical profile jitter
- `Audio/*.ogg` / `*.wav` — mastered −18 LUFS (classical target)

## Verify (real numbers)

Zero-drift 30720 × 4 voices · perfect off-grid **0** · humanized off-grid
**200** · harmony 0/0/0 on all 4 voices · counter 40 notes, 0 collisions,
0 pc-doublings. See `Analysis/verify.json`.
