# HC-008 — Minimalist Phase & Additive Process Composition

**Tradition / Culture:** American Minimalism (USA, 1960s–1970s) — Steve Reich, Terry Riley, Philip Glass, La Monte Young.
**Primary Elements:** RHYTHM, TEXTURE, STRUCTURE, PITCH.
**Status:** ✅ Documented

---

## Description

A human composition method in which a **small, fixed musical cell** (a short melodic/rhythmic pattern) is subjected to **audible, gradual processes** — phase shifting, additive growth, or modular repetition — and the musical interest arises from the **emergent composite patterns** produced when multiple copies of the cell interlock. The composer does not write a narrative melody; instead they design a *process* and let the resulting texture be the piece.

Reich's famous dictum: *"I am interested in perceptible processes. I want to be able to hear the process happening throughout the sounding music."* The craft is in choosing a cell whose interlocking copies produce rich "result patterns" (sub-melodies the ear picks out of the composite), and in pacing the process so the transformation is always audible.

No functional harmony. Harmony is **emergent** — the vertical sonorities are whatever the pitch content of the cell happens to stack into at each moment. Pitch material is usually diatonic or pentatonic to keep the result patterns consonant.

---

## Craft Steps (how the human executes it)

1. **Compose the cell.** Write a short pattern (8–16 notes), often pentatonic or diatonic, with a clear rhythmic profile. The cell must be *self-sufficient* — it is the entire melodic material of the piece. (Reich: "Piano Phase" cell = 12-note figure; Riley: "In C" = 53 short phrases.)

2. **Choose the process.**
   - **Phase shifting** — two (or more) identical voices play the cell; one voice gradually accelerates (or shifts by a fixed subdivision) so the two copies drift out of and back into alignment. (Reich: *Piano Phase*, *Violin Phase*, *Clapping Music*.)
   - **Additive process** — the cell is built note-by-note: start with one note, add a second, then a third, until the full pattern emerges; then subtract notes back down. (Glass: *Music in 12 Parts*, *Music in Fifths*.)
   - **Modular repetition** — a set of short phrases; each player repeats a phrase as many times as they wish before moving to the next, creating staggered, ever-shifting vertical combinations. (Riley: *In C*.)

3. **Map the phase/step grid.** Decide the exact offset increments (e.g. shift by one 16th-note every N repetitions) so the drift is *audible and gradual*, not random. In *Clapping Music*, Reich shifts the second clapper by one 8th-note every 8 bars through all 12 positions.

4. **Listen for result patterns.** Play the interlocked copies and identify the emergent composite melodies (e.g. the "resulting pattern" that appears when two phased voices align at a certain offset). These emergent figures become the perceived "melody" even though no single player plays them.

5. **Layer texture.** Add a steady pulse (drumming, marimba, clapping) and/or sustained tones (strings, voices, organ) beneath the phased cells. Minimalism is built on an **invariant pulse** — the process rides on top of an unbroken rhythmic foundation.

6. **Pace the macro-form.** Structure the piece as a sequence of process states: phase positions (0°→90°→180°→270°→re-alignment) or additive stages (1 note→full cell→1 note). Section changes are *process milestones*, not thematic events.

7. **Notate the process, not the result.** The score describes the rule ("shift by one 8th-note every 8 bars"), not the fully written-out composite. In *In C*, the score is one page of 53 phrases plus the instruction "repeat each phrase as long as you like."

---

## UnitMatrix Integration

**Voices (4):**
- **Voice 0 — Base cell (invariant spine).** The fixed pattern, played continuously, never changes. This is the human-authored core.
- **Voice 1 — Phased copy.** Identical cell content, offset by a phase increment that advances over time (drift → re-alignment).
- **Voice 2 — Additive layer.** The cell built note-by-note (grows from 1 note to full pattern and back), or a second phased copy at a different offset.
- **Voice 3 — Pulse/drone (invariant foundation).** Steady rhythmic pulse (claps, marimba, shaker) and/or sustained tones (strings, organ, voices) that never stop.

**Sections = process states:**
- Phase-shift piece: `Phase 0 → Phase 1 → Phase 2 → … → Phase N → Re-alignment (return to 0)`.
- Additive piece: `1-note → 2-note → … → full cell → subtract → 1-note`.
- Modular piece: `Entry 1 → Entry 2 → … → Full ensemble → Decay`.

**Rules to encode:**
- **Cell invariance** — Voice 0 pitch/rhythm content is constant across all sections.
- **Phase-offset progression** — Voice 1 offset advances by a fixed subdivision (e.g. +1 16th per section), monotonic, never random.
- **Additive growth** — Voice 2 note count increases by exactly 1 per section (then decreases).
- **Result-pattern emergence** — the composite (sum of voices) is the audible melody; no single voice carries a "lead."
- **No functional harmony** — pitch set constrained to diatonic/pentatonic; vertical sonorities are emergent, not authored.
- **Pulse invariance** — Voice 3 never stops; it is the grid the process rides on.
- **Gradual process** — every transformation is audible and stepwise (no hidden/sudden changes).

**Musicom mapping note:** This is the *human-side* origin of the engine's **026 DPSM (Phase-Shift Minimalism)** nature-led method. The human method defines *what the composer chooses* (the cell, the offset increments, the pacing); DPSM is the *emergent polyrhythm* that results. The two are complementary — human cell design + phase-offset grid → DPSM output.

---

## Real Practitioner Examples

- **Steve Reich — *Piano Phase* (1967):** Two pianos play the same 12-note cell; one gradually accelerates until the two are exactly one note out of phase, then two, then three… through all 12 positions and back to unison. The "melody" is the emergent result pattern heard at each offset.
- **Steve Reich — *Clapping Music* (1972):** Two clappers, one fixed, one shifting by one 8th-note every 8 bars through all 12 positions. Pure phase process with no pitch at all.
- **Steve Reich — *Drumming* (1971) & *Music for 18 Musicians* (1976):** Additive construction — patterns built one note at a time, layered over a steady pulse, with result patterns arising from interlocking marimbas/voices.
- **Terry Riley — *In C* (1964):** 53 short phrases on one page; any number of players repeat each phrase as long as they like before moving on. Staggered entries produce a constantly shifting, never-repeating vertical texture — the archetype of modular repetition.
- **Philip Glass — *Music in 12 Parts* (1971–74) & *Music in Fifths* (1969):** Additive process — a figure grows by one note per cycle, then subtracts, creating audible build-and-decay structure.
- **La Monte Young — *The Well-Tuned Piano* (1964–):** Drone/just-intonation minimalism — sustained tones held for long durations, harmony as a static, slowly-shifting field rather than progression.
