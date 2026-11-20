# Report HC-097 — Nashville Number System (NNS) Charting & Arrangement Craft

**Job:** daily-human-composition-research · **Date:** 2026-11-19
**Method ID:** HC-097 (resolved dynamically: max existing = HC-096 → next = HC-097)
**Layer:** concrete (target when implemented) — human-craft knowledge realized through the UnitMatrix.
**Tradition:** American — Nashville country/studio session craft (Tennessee, late 1950s → present).

---

## 1. Method Name & Tradition

**Nashville Number System (NNS) Charting & Arrangement Craft** — key-independent Arabic-numeral chord shorthand + "road map" form notation, used by session musicians to capture an arrangement fast and re-realize it in any key.

- **Who:** developed in the late 1950s by **Neal Matthews Jr.**, vocal arranger of the **Jordanaires** (Elvis's backing group), and adapted into bass/drums/piano/guitar charts by **Charlie McCoy**; popularized through Nashville "A-Team" head sessions; spread to **Muscle Shoals** and other Southern studios, then to pop, church worship bands, and jazz pedagogy.
- **Lineage:** Matthews explicitly drew on his **shape-note / gospel-quartet movable-do** background (per Chas Williams' history) — degree-relative thinking, same as solfège and figured bass. NNS is the 20th-century American session descendant of the figured-bass/partimento idea (cf. HC-001): a numeric harmonic code realized by skilled musicians in real time.
- **Codification:** Chas Williams, *The Nashville Number System* (1988); Mike McAdam, *The Nashville Number System: The Definitive Guide* (2017).

## 2. Layer

`concrete` (target when implemented). The NNS chart is an abstract harmonic/structural skeleton (framework-level knowledge); the UnitMatrix realizes it as concrete material (chords, bass, comping, feel). Same layer contract as all HC methods: human craft → concrete realization.

## 3. Craft Procedure (how the human does it)

1. **Learn the song by ear** — "head session" norm: demo looped until memorized; arrangement improvised collectively in the room; the chart captures the arrangement almost as fast as it is made.
2. **Fix the key mentally** — numbers are relative; the key is never written on the chart.
3. **Assign Arabic numerals to scale degrees** — 1 = tonic … 7; **all chords major by default** until a quality suffix is applied (deliberately ignoring diatonic theory).
4. **Apply quality suffixes** — `m`/`−` minor, `7` dominant, `Δ`/`maj7`, `°`/`dim`, `ø`, `sus`, `aug`, `add9`, `6`; non-scale chords as flat/accidental numbers (`♭7`, "5 of 2m").
5. **Write slash chords for bass** — `1/5` = I over 5 bass; `4/1` = IV over 1 (pedal); encodes inversions/pedals/walking-bass contours.
6. **Lay the hashmark beat grid** — slash per beat; chord number above the beat it hits; underline = split measure (2 chords/bar); box = complex measure; dash = **push** (anticipated chord). Rhythm, duration, rests, articulation all conveyable.
7. **Build the road map (form)** — labeled sections (Intro/Verse/Chorus/Bridge/Instrumental/Tag), repeats `×2`/`×4`, D.S./D.C./Coda, "2nd time to…" cells, per-section feel/dynamic tags ("shuffle", "half-time", "build").
8. **Call the key, count off, play** — "number 4, key of D"; band realizes the grid by ear: bass reads numbers/slashes, compers voice from quality grammar, drummer plays the feel tag, soloists improvise.
9. **Revise live** — arranger shouts a change; everyone adjusts instantly; the chart keeps pace. The final chart is the durable, reusable artifact (any key, any ensemble). Melody is never on the chart (assumed known).

## 4. Practitioner Examples

- **Neal Matthews Jr. & the Jordanaires** — invented the system (late 1950s) for fast vocal-part charts; several sessions per day with Elvis et al.; Country Music Hall of Fame credits Matthews with popularizing it.
- **Charlie McCoy** — adapted numerals into multi-instrument chord charts (bass/drums/piano/guitar); made the system the studio standard.
- **Nashville "A-Team"** — Bob Moore, Harold Bradley, Grady Martin, Pig Robbins: head-session collective arranging captured in numbers (classic country/pop hits, 1960s–70s).
- **Muscle Shoals rhythm section** — the system as Southern session lingua franca (Aretha Franklin, Wilson Pickett dates).
- **Chas Williams** — 1988 book: history + pedagogy (documented the shape-note link).
- **Mike McAdam** — 2017 definitive guide: quality notation, road maps, pedagogy.
- **Contemporary** — church worship bands transpose NNS charts on the fly; songwriters audition progressions as numbers across keys; jazz/pop cover bands read "number charts".

## 5. UnitMatrix Mapping (Voices & Sections, Rules)

The NNS chart *is* a grid (road-map rows × beat-grid columns), so it maps almost directly onto the UnitMatrix: chart = framework, voices = the realizations session players improvise.

**Voices:**
- **Voice 0 — Degree-grid spine (the chart):** chord-degree + quality + slash-bass per cell, realized as chordal units; the harmonic DNA / identity anchor.
- **Voice 1 — Bass realization:** root from degree number, bass note from `/n` suffix; walking/ostinato per feel tag.
- **Voice 2 — Comping realization:** voicings generated from quality grammar; rhythm from hashmarks and pushes; density per section feel.
- **Voice 3 — Melody/lead:** off-chart by design (known by ear); optional human-authored lead-sheet voice for demos.
- **Voice 4 — Rhythm/feel layer:** meter, groove tag, tempo, push positions.
- **Voice 5 — Metadata:** road-map labels, repeat/2nd-time operators, solo/dynamic cues.

**Sections:** road-map blocks — Intro → Verse 1 → Chorus → Verse 2 → Bridge → Chorus (2nd-time cell) → Tag/Outro; each = integer bars (zero-drift).

**Rules:**
1. Degree→pitch mapping from key (transposition invariance: one key parameter re-pitches the whole matrix; numbers never change).
2. Default-major quality grammar (m/−, 7, Δ/maj7, °, ø, sus, aug, add9 → chord-tone sets for realization voices).
3. Slash-bass rule (`/n` fixes bass scale degree).
4. Beat-grid hashmarks (chord cells on integer beats; underline = split measure; box = complex).
5. Push rule (anticipated chord: onset shifted early at realization time; cell length unchanged → zero-drift safe).
6. Form-repeat operators (×2/×4, D.S./D.C./Coda) + 2nd-time substitution cells (first-pass vs second-pass chords in the same slot).
7. Feel tags per section (groove/tempo/dynamics → rhythm voice + humanize profile).
8. Collective realization (Voices 1–2 rule-generated, never fully specified — preserves the head-session ethos).
9. Zero-drift gate: `validate()` must pass before `to_midi()`; all rows equal length.

## 6. Table Row Added (human_methods_db.md, after HC-096)

```
| **HC-097** | human (→concrete) | Nashville Number System (NNS) Charting & Arrangement Craft — Key-Independent Degree-Grid "Road Map" (Arabic-Numeral Chord Shorthand × Slash-Chord Bass × Hashmark Rhythm Grid × Form-Repeat Operators; Head-Session Realization) | American — Nashville country/studio session craft (Jordanaires/Neal Matthews Jr. & Charlie McCoy, late 1950s → present); roots in shape-note/gospel-quartet movable-do; spread to Muscle Shoals, pop, church & jazz pedagogy; Chas Williams (1988), Mike McAdam (2017) | HARMONY, STRUCTURE, RHYTHM, TEXTURE | Learn the song by ear (head session: demo looped until memorized, arrangement improvised collectively) → fix key (numbers relative, key never on chart) → assign Arabic numerals to scale degrees (1=tonic; default major; m/−=minor, 7=dominant, Δ/maj7, °/dim, ø, sus, aug, add9) → write slash chords (1/5 = I over 5 bass; 4/1 = IV over 1) → lay hashmark beat grid (slash per beat, chord above its beat; underline=split measure, box=complex, dash=push/anticipated chord) → build road map (label Intro/Verse/Chorus/Bridge/Instrumental/Tag; repeats ×2/×4, D.S./D.C./Coda, 2nd-time substitution cells; feel/dynamic tags) → call key & count off ("number 4, key of D") → band realizes grid by ear (bass reads numbers/slashes, compers voice from quality grammar, drummer plays feel tag) → arranger shouts changes, chart keeps pace → final chart = durable artifact, re-usable in any key/ensemble | Voice 0 = degree-grid spine (chord-degree+quality+slash-bass per cell, realized as chordal units; harmonic DNA). Voice 1 = bass realization (root/slash-bass, walking/ostinato per feel). Voice 2 = comping realization (voicings from quality grammar, rhythm from hashmarks/pushes). Voice 3 = melody/lead (off-chart by design; optional human-authored). Voice 4 = rhythm/feel layer (meter, groove tag, tempo, push positions). Voice 5 = metadata (road-map labels, repeat/2nd-time operators, cues). Sections = road-map blocks (Intro→V1→Chorus→V2→Bridge→Chorus2nd→Tag). Rules: degree→pitch mapping from key (transposition invariance), default-major quality grammar, slash-bass rule, beat-grid hashmarks, push anticipation, split/boxed measure, form-repeat operators with 2nd-time cells, feel tags per section, integer-bar zero-drift cells, collective realization (V1–V2 rule-generated, never fully specified). | Neal Matthews Jr. & the Jordanaires (Elvis sessions; invented late 1950s), Charlie McCoy (bass/drums/piano/guitar charts), Nashville "A-Team" head sessions (Bob Moore, Harold Bradley, Grady Martin, Pig Robbins), Muscle Shoals rhythm section, Chas Williams (*The Nashville Number System* 1988), Mike McAdam (*The Nashville Number System: The Definitive Guide* 2017), contemporary church/jazz NNS readers | ✅ Documented |
```

## 7. Next Free ID

**HC-098** (max existing = HC-097 after this entry; no HC-098 detail/report files exist).

## 8. Quirks & Pitfalls

- **Not analysis, not a lead sheet** — NNS omits melody/voicings by design; over-specifying the chart destroys the craft. Realization voices must stay rule-generated.
- **Default-major convention** — a bare `6` is the major VI chord, not diatonic vi; encoders must not "correct" bare numbers to diatonic qualities.
- **Key is an external parameter** — never a per-cell property; re-keying = one parameter change.
- **Dialect drift** — `m` vs `−`, `Δ` vs `maj7`, `°` vs `dim` vary by community; pick one grammar, state it in provenance.
- **Hand-drawn road-map conventions** (2nd-time arrows, push dashes) must be normalized to explicit operators for machine encoding.
- **Head-session ethos** — the value is speed + collective improvisation; keep the realization layer minimal and rule-driven.

## 9. Files

- Detail: `/opt/data/projects/Research/CompositionMethods/human_method_HC-097_nashville-number-system-charting.md`
- DB: `/opt/data/projects/Research/CompositionMethods/human_methods_db.md` (row HC-097 appended)
- This report: `/opt/data/projects/Research/CompositionMethods/report_HC-097.md`
