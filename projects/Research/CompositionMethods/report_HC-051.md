# Report HC-051 — Ragtime Stride Piano Composition

## Method Identity

| Field | Value |
|---|---|
| **HC-ID** | HC-051 |
| **Method Name** | Ragtime Stride Piano Composition — Multi-Strain March Form & Left-Hand Oompah Craft |
| **Tradition / Culture** | African-American piano tradition — Classic Ragtime (Sedalia/St. Louis, USA, 1890s–1920s) and Harlem Stride Piano (New York, USA, 1920s–1940s) |
| **Layer** | human (→concrete) — target layer for UnitMatrix implementation: **concrete** |
| **Primary Musical Elements** | RHYTHM, PITCH, STRUCTURE, TEXTURE, HARMONY |
| **Status** | ✅ Documented |

---

## Method Description

Ragtime and stride piano represent the first distinctly African-American composed piano idioms, fusing European march multi-strain form (AABBACCDD) with West-African derived syncopation. **Classic ragtime** (Joplin, Scott, Lamb, 1897–1917) is fully notated: the left hand plays a metronomic "oompah" (bass on beats 1&3, chord on 2&4), the right hand places syncopated figures off the beat. **Harlem stride** (Johnson, Smith, Waller, Tatum, 1920s–1940s) extends this with faster tempos, wider left-hand tenths, blues harmony, and improvisatory right-hand virtuosity. Both are profoundly pianistic — designed for the human hand's physical constraints (span, finger independence, mechanical reach).

---

## Craft Procedure (Step-by-Step)

### Phase 1: Conception

1. **Choose key & modulation plan** — A in tonic → B in dominant/relative minor → A (reprise) → Trio/C in subdominant → D in same key. Joplin's *Maple Leaf Rag* template: E♭ (A) → B♭ (B) → E♭ (A) → A♭ (C) → A♭ (D). Stride pianists often favour E♭, A♭, D♭ for piano resonance.

2. **Set tempo & meter** — Classic ragtime: 2/4 or cut time, 80–120 BPM. Stride: up to 160–200 BPM (cutting contests). Never played "fast" in Joplin's school; always felt in 2.

3. **Generate motif seed** — 2–4 bar rhythmic+melodic cell. *The Entertainer* motif: E–C dyad with `♩. ♪` pattern. *Maple Leaf Rag* motif: arpeggiated eighth-sixteenth rhythm. The motif supplies unity across all strains.

### Phase 2: Left-Hand Architecture

4. **Compose oompah bass grid** — The non-negotiable spine: **bass note/octave on beats 1 & 3, chord on beats 2 & 4**. Variations: standard (root octave + root-5th chord), walking tenths (characteristic of stride), broken (root inversions), pedal (chromatic approach). **This layer never stops, never rests, never syncopates** — it is the human drum machine.

5. **Check hand-span constraint** — Maximum reach = 10th (20 semitones). Racetime composers *never* exceeded this. If the harmonic plan requires a wider bass-to-chord interval (e.g., B♭1 to D4 = 29st), the chord must be inverted or rolled.

6. **Fix harmonic grid** — I–IV–V–I and ii–V–I progressions. Classic rag: functional harmony with chromatic passing chords. Stride adds: ♭7 dominants, diminished chains, blues iii–VI–ii–V turnarounds, tritone substitutions.

### Phase 3: Right-Hand Melody

7. **Write syncopated A-strain melody** — Joplin's *School of Ragtime* rule: syncopation = `♩. ♪` or `♪ ♩. ♪` against the strict oompah. The right hand must *never* play solid eighth notes (that's a march, not a rag). ~30–50% of right-hand events should be off-beat.

8. **Apply syncopation density gradient** — A (density 0.3, moderate) → B (0.5, denser) → Trio (0.4, contrasting/simpler) → D (0.7, maximum). Monotonically increasing across the piece except the Trio which contrasts dynamically.

9. **Shape melodic contour** — Rise-and-fall arc within ≤2 octaves per phrase. Avoid random leaps: melodic skips outline chord tones or are followed by stepwise opposite-direction resolution.

### Phase 4: Form & Assembly

10. **Arrange multi-strain march form** — The blueprint: **Intro (opt, 2–4 bars) → A (16 bars, tonic) → A (repeat) → B (16 bars, dominant) → B (repeat) → A (8 or 16 bars, return) → Trio/C (16 bars, subdominant) → Trio/C (repeat) → D (16 bars, same key) → D (repeat)** = **AABBACCDD**. Each 16-bar strain = 8+8 antecedent/consequent period with half→full cadence.

11. **Engineer trio transition** — New key (subdominant), new tonal centre, new texture — but retaining at least one motivic fragment from the A strain. The trio is the "musical heart." In stride, the trio is where improvisation flourishes.

12. **Add dynamics & markings** — A = *mf*, B = *f*, Trio = *p* (contrast), D = *ff*. Provide phrase markings, staccato/legato, and pedal indications. Ragtime scores are explicit performance instructions.

### Phase 5: Stride Variant (optional, when `is_stride = True`)

- Replace single-note bass on beats 1/3 with 10th intervals
- Add chromatic/diatonic walking 10th motion
- Right-hand may improvise ornamentation on each pass (repeats = different syncopation surface over frozen grid)
- Tempo ≥ 140 BPM
- Swing eighth feel (long-short)
- Blues notes (♭3, ♭5, ♭7) permitted
- Cutting contest mentality: each chorus = virtuosic escalation

---

## Practitioner Examples

### Classic Ragtime Composers
- **Scott Joplin** (1868–1917) — The definitive ragtime composer. *Maple Leaf Rag* (1899): AABBACCDD, E♭→A♭, perfect multi-strain architecture. *The Entertainer* (1902): highly symmetrical form. *School of Ragtime* (1908): self-published syncopation manual. *Magnetic Rag* (1914): most harmonically advanced, 14/10 internal asymmetry.
- **James Scott** (1885–1938) — *Frog Legs Rag* (1906), *Grace and Beauty* (1909). More chromatic harmony, elaborate bass lines.
- **Joseph Lamb** (1887–1959) — *American Beauty Rag* (1913): exceptional motivic coherence. *Ragtime Nightingale* (1914). Only white composer in Joplin–Scott circle.
- **Artie Matthews** — *Pastime Rags No. 1–5* (1913–1917): advanced syncopation.

### Harlem Stride Pianists
- **James P. Johnson** (1894–1955) — "Father of Stride." *Carolina Shout* (1921): first recorded stride solo, modelled on ring-shout rhythm. *The Harlem Strut* (1917). Integrated blues notes, swing eighths, call-and-response hands.
- **Willie "The Lion" Smith** (1897–1973) — *Finger Buster* (1921), *Echoes of Spring* (1936). Dynamic contrasts, abrupt stops-and-starts, "trick" piano effects.
- **Fats Waller** (1904–1943) — *Handful of Keys* (1929): stride tour-de-force. *Honeysuckle Rose* (1929). Walking 10ths in every phrase, "stride-breaks" (two-handed upward runs). Bridged stride to swing.
- **Art Tatum** (1909–1956) — *Tiger Rag* (1932), *Body and Soul* (1940). Pushed stride to harmonic extreme: reharmonized stride (altered dominants, tritone substitutions, diminished chains). Left hand used 10th–12th with rolled chords. Fastest and most virtuosic stride pianist.

### Contemporary Practitioners
- **William Bolcom** — *Poltergeist*, *Graceful Ghost Rag*. Concert ragtime composer, Pulitzer winner.
- **Bill Edwards** — Ragtime composer, *Blood on the Keys*, *Hanon Rag*. Author of the comprehensive Rhapsody in Ragtime composition guide.
- **Marcus Roberts**, **Dick Hyman** — Contemporary stride/ragtime performers and educators.

---

## UnitMatrix Mapping

### Voice Architecture

| Voice # | Role | Instrument (MIDI Program) | Craft Function |
|---|---|---|---|
| **Voice 0** | Left-hand bass spine — oompah foundation | Acoustic Grand Piano (ch 0, pg 0) | Invariant bass/chord alternation on beats 1–3 (bass) and 2–4 (chord). The mechanical engine — never stops, never rests, never syncopates. Serves as the metronomic grid the right hand syncopates against. |
| **Voice 1** | Right-hand melody — syncopated lead | Acoustic Grand Piano (ch 0, pg 0) | All melodic material: motif statement, syncopated figures, runs, breaks. Plays exclusively in RH register (C4–C7). Syncopation density varies per strain. |
| **Voice 2** | Right-hand harmony/break layer | Acoustic Grand Piano (ch 0, pg 0) | Second RH layer in stride: two-handed chords, arpeggiated break figures, tremolos, and "stride-break" runs. Typically an octave below V1, filling the gap between V0's chord and V1's melody. Classic rag: may be empty. |
| **Voice 3** | Bass tenth extension — walking tenth layer | Acoustic Grand Piano (ch 0, pg 0) | Active only in stride variant (`is_stride = True`). Replaces V0's single-note bass on 1/3 with 10th intervals (e.g., C3–E4). Chromatic/diatonic approach 10ths between harmony changes. In classic rag: keep empty. |
| **Voice 4** | Percussion backbeat — optional | Side Stick / Snare (ch 9, perc) | Optional groove reinforcement: accents on beats 2 & 4. Keeps the lock during fast stride passages. Classic rag: empty. |

### Section Architecture

| Section | Bars | Key | Function | Syncopation Density |
|---|---|---|---|---|
| **Intro** (opt.) | 0–4 | Tonic | Establish key, tempo, and motif. Raked chord or V7–I fanfare. Johnson's *Carolina Shout* uses a 2-bar raked chord. | — |
| **A** | 1–16 | Tonic (I) | Main theme, stated twice (repeat). 8+8 antecedent/consequent. Moderate syncopation, clear motif presentation. | 0.3 |
| **B** | 17–32 | Dominant (V) or rel. minor (vi) | Contrasting theme, repeated. Denser syncopation, octave melody, upper register climax near cadence. | 0.5 |
| **A repr.** | 33–40 (or 48) | Tonic (I) | Brief return, often 8 bars (not full 16), leading into trio. | 0.3 |
| **Trio/C** | 41–56 | Subdominant (IV) | New key, fresh thematic material. Retains at least one motivic fragment from A. Dynamic contrast (*p* vs A's *mf*). In stride: improvisation zone. | 0.4 |
| **D** | 57–72 | Subdominant (IV) | Final strain, repeated. Most virtuosic, highest register, densest syncopation. Often recycles B's melodic shape with IV-key harmony. | 0.7 |
| **Coda** (opt.) | 73–80 | Tonic (I) | Closing tag: ii–V–I chain, register rise, final tonic chord with fermata. Common in stride. | — |

### Rules (Constraint Set)

1. **Oompah invariance**: V0 plays bass/octave on beats 1&3, chord on beats 2&4, every bar, no rests, no syncopation. `[onset ∈ {0, 0.5, 1.0, 1.5} bar] ∧ [V0.beats(1,3) ∈ {root_octave, root}] ∧ [V0.beats(2,4) ∈ {chord_tones}]`
2. **Hand-span filter**: No bass-to-chord interval > 10th (20 semitones). If harmonic plan exceeds this, invert or roll the chord. `V0.chord_pitches - V0.bass_pitch ≤ 20`
3. **Syncopation density gradient**: A=0.3 → B=0.5 → Trio=0.4 → D=0.7 (proportion of RH onsets off the beat-grid). Joplin's rule: ≥1 tied note across a beat per phrase.
4. **Strain period division**: Each 16-bar strain = 8+8 antecedent/consequent. Antecedent ends on half cadence (V); consequent ends on full cadence (I). Cadential rhyme: the last 2 bars of each half share harmonic/rhythmic material.
5. **Key modulation plan**: A=tonic → B=dominant or rel.minor → A return=tonic → Trio=subdominant → D=subdominant or V/IV. Modulations are abrupt (double-bar), no developmental bridge.
6. **Motivic coherence**: ≥1 motif from A strain must reappear (inverted, augmented, diminished, or interval-expanded) in the Trio. Without this, the rag sounds like 4 separate pieces.
7. **No internal modulation**: Each strain stays in its local key for its entire duration — no modulation inside a strain.
8. **Playability gate**: Every chord must be playable by human hands. Chords >10th span across both hands simultaneously = illegal.
9. **Stride variant gate** (when `is_stride = True`): V0 bass on 1/3 → 10th intervals; walking 10th bass (chromatic approach); right-hand improvisatory variation on repeats (different syncopation each pass over frozen harmony); tempo ≥ 140 BPM; blue notes permitted.

---

## Table Row Added

The following row was appended to the Human Composition Methods Framework table in `human_methods_db.md`:

```
| HC-051 | human (→concrete) | Ragtime Stride Piano Composition — Multi-Strain March Form & Left-Hand Oompah Craft | African-American piano tradition — Classic Ragtime (USA, 1890s–1920s) & Harlem Stride (USA, 1920s–1940s) | RHYTHM, PITCH, STRUCTURE, TEXTURE, HARMONY | Choose key & key scheme (I→V→I→IV) → generate motif seed (2–4 bar rhythmic+melodic cell) → write left-hand oompah (bass/octave on 1&3, chord on 2&4, never stops) → check hand-span (no bass-to-chord > 10th) → write right-hand syncopated melody against oompah grid → shape syncopation gradient per strain (A moderate → B denser → Trio contrasting → D maximum) → arrange AABB(AC)CDD multi-strain march form (16-bar sections, 8+8 antecedent/consequent, half→full cadence) → modulate keys per strain (A=tonic, B=dominant/relative minor, Trio=subdominant, D=subdominant) → ensure motivic coherence (one A-motif reappears transformed in Trio) → in stride variant: 10th bass, swing feel, improvisatory ornament on repeats, tempo ≥140 | Voice 0 = left-hand bass spine (oompah grid: bass on 1/3, chord on 2/4, invariant metronomic foundation). Voice 1 = right-hand melody (syncopated lead, off-beat bias, density gradient per strain). Voice 2 = right-hand harmony/break layer (two-handed chords, arpeggiated runs — stride only). Voice 3 = bass 10th extension (active in stride: chromatic/diatonic 10ths replacing single-note bass). Voice 4 = optional percussion backbeat (side stick on 2&4, groove lock). Sections = Intro (optional, 0–4 bars) → A (bars 1–16, tonic, moderate syncopation) → B (bars 17–32, dominant, denser syncopation) → A reprise (bars 33–40/48, tonic) → Trio/C (bars 41–56, subdominant, new key+motif) → D (bars 57–72, subdominant, max density+register) → optional Coda (ii–V–I tag). Rules: oompah invariance (V0 always playing, never a rest), hand-span filter (interval ≤ 10th, 20st), syncopation density per strain (0.3→0.5→0.4→0.7), strain period division (16=8+8, half cadence→full cadence), key modulation plan (I→V→I→IV), motivic coherence (≥1 motif reappears in Trio), no internal modulation (each strain self-contained), playability validation, stride variant conditions (10th bass, tempo≥140, improvisatory repeats) | Scott Joplin (*Maple Leaf Rag* AABBACCDD archetype, *The Entertainer* symmetric syncopation, *School of Ragtime* syncopation rules), James Scott (*Frog Legs Rag*, *Grace and Beauty*), Joseph Lamb (*American Beauty Rag*), James P. Johnson (*Carolina Shout* first stride solo, ring-shout integration), Willie "The Lion" Smith (*Finger Buster*), Fats Waller (*Handful of Keys*, 10th walking bass), Art Tatum (*Tiger Rag*, reharmonized stride), Bill Edwards (ragtime composer) | ✅ Documented |
```

---

## Next Free ID

After HC-051, the next free ID is **HC-052**.

---

## Verification

- ✅ `human_method_HC-051_ragtime-stride-piano-composition.md` — detail file written (16,194 bytes)
- ✅ `human_methods_db.md` — row HC-051 appended on line 57
- ✅ `report_HC-051.md` — this report file
- ✅ `grep HC-051` in detail file: found
- ✅ `grep HC-051` in human_methods_db.md: found on line 57
- ✅ No conflicting HC-051 files existed before creation

---

## Quirks & Pitfalls

- **The ragtime paradox**: The left hand MUST be metronomically stiff while the right hand plays "ragged." Beginners let the left hand speed up with right-hand syncopation — destroys the feel. The left hand is a human drum machine.
- **The "not a rag" risk**: Syncopation density <10% = march/cakewalk, not rag. Syncopation density >70% = mechanical stagger, not syncopation. The sweet spot is ~30–50% off-beat RH events.
- **Hand-stretch injury**: 10th in C (C–E) = maximum safe static span. 10th on black keys (B♭–D, A♭–C) is tighter. Stride pianists (Waller, Tatum) frequently practiced themselves into injury. Compose within safe human limits.
- **Readability trap**: Ragtime notation with complex beam breaks is notoriously hard to sight-read. Joplin wrote exact syncopation; modern composers recommend using tenuto/tie marks for readability.
- **Cutting contest trap**: Speed alone is empty. *Carolina Shout* works because it swings AND has clear motivic logic. Entertain without technique = boring. Technique without melody = empty.

---

## Sources

- Bill Edwards, "Ragtime Composition" (RagPiano.com, 2004/2015/2024)
- Scott Joplin, *School of Ragtime* (1908)
- Gunther Schuller, *Early Jazz: Its Roots and Musical Development* (1986)
- David Schiff, "A Pianist With Harlem on His Mind," *New York Times* (1992)
- Songtive, "Maple Leaf Rag Form Analysis: AABBACCDD Explained" (2024)
- Jazz History Tree, "Harlem Stride / Stride: 1925"
- Syncopated Times, Scott E. Brown on James P. Johnson's *The Harlem Strut* (2024)