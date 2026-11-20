# HC-097 — Nashville Number System (NNS) Charting & Arrangement Craft

**Method ID:** HC-097
**Layer:** concrete (target when implemented) — human-craft knowledge; the NNS chart is an abstract harmonic/structural skeleton that realizes material through the UnitMatrix.
**Tradition:** American — Nashville country/studio session craft (Tennessee, late 1950s → present). Invented by Jordanaires vocal arranger **Neal Matthews Jr.** with **Charlie McCoy**; roots in shape-note / gospel-quartet movable-do practice (Matthews' own stated inspiration, per Chas Williams' history); spread from Nashville to Muscle Shoals and other Southern recording centers, then into pop, church worship bands, and jazz pedagogy. Codified in Chas Williams, *The Nashville Number System* (1988) and Mike McAdam, *The Nashville Number System: The Definitive Guide* (2017).
**Primary Elements:** HARMONY, STRUCTURE, RHYTHM, TEXTURE (PITCH enters via the key mapping — the numbers themselves are key-independent).

---

## What It Is

The Nashville Number System is a **key-independent shorthand for the harmonic and structural framework of a song**. Chords are written as Arabic numerals standing for scale degrees of the song's key (tonic = 1, supertonic = 2, …), with quality suffixes and slash-chord bass notation; the form is drawn as a "road map" of labeled sections with repeats, pushes, and feel tags. It is a *practical performance/arrangement notation*, not harmonic analysis: it deliberately leaves melody, voicings, and parts unspecified. The same one-page chart works in any key — the whole band transposes by reading the numbers.

It is the 20th-century American session-musician descendant of the same idea as figured bass / partimento (HC-001): a compact numeric code for harmony that a skilled musician realizes in real time. Difference: partimento is 18th-c. Neapolitan keyboard improvisation pedagogy over a bass; NNS is a mid-20th-c. studio/band communication grid where the *whole rhythm section* improvises from the numbers, and the chart is edited live as the arrangement changes ("head sessions").

---

## The Craft Procedure (step by step, how a human does it)

1. **Learn the song by ear (head-session norm).** In the Nashville studio of the 1950s–70s, a demo was played repeatedly until the musicians had the song memorized and could improvise their parts by ear; the arrangement was often created *collectively* in the room. The chart is written to *capture* that arrangement almost as fast as it is made — not to create it from scratch on paper.

2. **Fix the key (mentally, never on the chart).** The chart carries no key signature. The player announces or knows the key ("number 4, key of D"); numbers express relationships to the tonic, so the identical chart serves every key. Transposition on the fly = changing one parameter.

3. **Assign Arabic numerals to scale degrees.** 1 2 3 4 5 6 7 = the seven degrees of the (usually major) scale; 1 is tonic. All chords are read as **major by default** until a quality is applied — this is the core NNS convention (no diatonic-theory assumptions baked in).

4. **Apply chord-quality suffixes.** Minor = `m` or minus sign (`2m`, `6m`, `3m`); dominant seventh = `7` (so `5 7` = V7); major seventh = `Δ` or `maj7`; diminished = `°`/`dim`; half-diminished = `ø`/`m7♭5`; suspended = `sus`/`sus4`; augmented = `aug`/`+`; added tones = `add9`, `6`, etc. Secondary dominants and borrowed chords are just written as numbers outside the scale (e.g., `♭7`, `5 7 of 2m`).

5. **Write slash chords for the bass.** `1/5` = the 1 chord over a 5 bass note (second inversion); `4/1` = IV chord over the 1 bass (pedal); `5/♭7` etc. This is how inversions, pedal points, and walking-bass contours are encoded without staff notation.

6. **Lay the hashmark beat grid.** Each beat is a slash; chord numbers are written *above the beat they hit*. Underlining a measure = split measure (two chords in one bar); boxing a measure = complex measure; a dash/arrow before a chord = **push** (anticipated chord change, landing early). This is the rhythm layer of the chart — chord duration, articulation, rests, and pushes are all conveyable.

7. **Build the road map (form).** Sections are labeled (Intro, Verse 1, Chorus, Bridge, Instrumental, Tag, Outro) with repeat signs, `×2`/`×4`, D.S./D.C./Coda, "2nd time to Bridge" instructions, and per-section feel/dynamic tags ("half-time feel", "shuffle", "ballad", "build"). First-time/second-time cells with different chords are written as two stacked rows. This is where STRUCTURE lives.

8. **Rehearse/record from the chart.** Call the key, count off, and the band realizes the grid: bass player reads numbers/slashes, guitar/piano comp voicings from the quality grammar, drummer plays the feel tag, soloists improvise over the sections. The arranger can shout a change ("make bar 12 a 4/1") and everyone adjusts instantly — the chart keeps pace with the session.

9. **Revise and preserve.** The final chart is the durable artifact of a session; the same numbers serve for a different artist, a different key, a live band, or a string-section date. The melody is assumed known — the chart never carries it (a lead-sheet melody line is a separate, optional artifact).

---

## Practitioner Examples

- **Neal Matthews Jr. (Jordanaires)** — vocal arranger who developed the system in the late 1950s to write vocal parts quickly; the Jordanaires backed Elvis Presley and worked several sessions a day, so speed was the motive. The Country Music Hall of Fame and Museum credits Matthews with popularizing the system.
- **Charlie McCoy** — adapted Matthews' numerical approach into chord charts for bass, drums, piano, and guitar; a legendary Nashville session musician (harmonica/bass) whose charts made the system the studio standard.
- **Nashville "A-Team" session players** — Bob Moore (bass), Harold Bradley, Grady Martin, Pig Robbins, et al.; the head-session culture where arrangements were improvised collectively and captured in numbers (recordings across classic country and pop hits from the 1960s–70s).
- **Muscle Shoals rhythm section** — the system spread to the Alabama studios (Aretha Franklin, Wilson Pickett sessions) as the lingua franca of Southern session work.
- **Chas Williams** — codified and taught the system in his 1988 book, preserving its history (including the shape-note link).
- **Mike McAdam** — contemporary authority; *The Nashville Number System: The Definitive Guide* (2017) formalizes quality notation, road maps, and pedagogy.
- **Contemporary practice** — church worship bands and jazz/pop covers read NNS charts for instant key changes; songwriters use the numbers to audition progressions across keys.

---

## UnitMatrix Integration (Musicom engine)

The NNS chart **is already a grid** — sections (rows of the road map) × beats/bars (columns of the hashmark grid) — so it maps onto the UnitMatrix almost directly. The chart is the *framework*; the matrix voices are the *realizations* the session musicians would improvise.

**Voices:**
- **Voice 0 — Degree-grid spine (the chart):** one cell per section holding the chord-degree sequence (e.g., `1 6m 4 5` per bar, or `1 1/5 4 4/1`). Realized as sustained/chordal units (pad or block chords). This is the harmonic DNA and the identity anchor — like the partimento bass, everything derives from it.
- **Voice 1 — Bass realization:** root notes from the degree numbers, slash-bass note from the `/n` suffix; walking/ostinato pattern chosen from the section's feel tag.
- **Voice 2 — Comping realization:** guitar/piano voicings generated from the quality grammar (m, 7, Δ, sus, °, ø); rhythm from hashmarks and pushes; sparse in verses, fuller in choruses per feel tags.
- **Voice 3 — Melody/lead:** off-chart by design (known by ear); optional human-authored lead-sheet voice when the matrix must carry the tune (e.g., a songwriting demo).
- **Voice 4 — Rhythm/feel layer:** meter, groove tag, tempo, push positions (where chords anticipate the beat).
- **Voice 5 — Metadata:** road-map labels, repeat/2nd-time operators, solo and dynamic cues.

**Sections:** road-map blocks — Intro → Verse 1 → Chorus → Verse 2 → Bridge → Chorus (2nd-time cell) → Tag/Outro — each an integer number of bars (zero-drift invariant).

**Rules to encode:**
1. **Degree→pitch mapping from key** — one key parameter re-pitches the entire matrix; the numbers never change (transposition invariance).
2. **Quality grammar** — default major; `m/−` minor, `7` dominant, `Δ`/`maj7`, `°`, `ø`, `sus`, `aug`, `add9`; each maps to a chord-tone set for the realization voices.
3. **Slash-bass rule** — `/n` fixes the bass scale degree under the chord (inversion/pedal).
4. **Beat-grid hashmarks** — chord cells align to integer beats; split measures (underline) get two chords per bar; boxed measures get complex/chromatic spellings.
5. **Push rule** — anticipated chords shift onset earlier by the marked offset (an absolute-tick displacement at realization time, still zero-drift-safe because the cell length is unchanged).
6. **Form-repeat operators** — `×2`/`×4`, D.S./D.C./Coda, and **2nd-time substitution cells** (first-pass vs second-pass chords in the same section slot).
7. **Feel tags per section** — groove (shuffle/swing/half-time), tempo, dynamics; drives the rhythm/feel voice and the humanize profile.
8. **Collective realization** — Voices 1–2 are improvised from the grid (rule-generated here), never fully specified; the chart stays abstract, exactly like a real session.
9. **Zero-drift** — every section cell = integer bars; `validate()` must pass before `to_midi()`.

---

## Quirks & Pitfalls

- **Not analysis, not lead sheet.** NNS intentionally omits melody, voicings, and arrangement detail. Encoding it as a *complete* composition misses the point — the chart is a skeleton the players complete. In the engine, keep Voices 1–2 rule-realized (generative), not hand-notated.
- **Default-major convention.** A bare `6` means the major VI chord, not diatonic vi — the system deliberately ignores diatonic theory until the suffix says otherwise. Encoding must not "correct" bare numbers to diatonic qualities.
- **No fixed key on the chart.** The matrix must treat key as an external parameter, not a per-cell property; re-keying = one parameter change, matrix re-pitches.
- **Numbering dialect drift.** Minor as `m` vs `−`, major-7 as `Δ` vs `maj7`, diminished as `°` vs `dim` vary by community (churches, jazz, studio). Pick one grammar and state it in provenance.
- **Road-map ambiguity.** "2nd time to…" cells and push dashes are hand-drawn conventions; they must be normalized to explicit repeat/substitution operators for machine encoding.
- **Head-session ethos.** The value is speed and collective improvisation; over-specifying the chart (writing every voicing) destroys the craft. Keep the realization layer rule-driven and minimal.

---

## Table Row Added

`| **HC-097** | human (→concrete) | Nashville Number System (NNS) Charting & Arrangement Craft — Key-Independent Degree-Grid "Road Map" (Arabic-Numeral Chord Shorthand × Slash-Chord Bass × Hashmark Rhythm Grid × Form-Repeat Operators; Head-Session Realization) | American — Nashville country/studio session craft (Jordanaires/Neal Matthews Jr. & Charlie McCoy, late 1950s → present); roots in shape-note/gospel-quartet movable-do; spread to Muscle Shoals, pop, church & jazz pedagogy; Chas Williams (1988), Mike McAdam (2017) | HARMONY, STRUCTURE, RHYTHM, TEXTURE | Learn the song by ear (head session: demo looped until memorized, arrangement improvised collectively) → fix key (numbers relative, key never on chart) → assign Arabic numerals to scale degrees (1=tonic; default major; m/−=minor, 7=dominant, Δ/maj7, °/dim, ø, sus, aug, add9) → write slash chords (1/5 = I over 5 bass; 4/1 = IV over 1) → lay hashmark beat grid (slash per beat, chord above its beat; underline=split measure, box=complex, dash=push/anticipated chord) → build road map (label Intro/Verse/Chorus/Bridge/Instrumental/Tag; repeats ×2/×4, D.S./D.C./Coda, 2nd-time substitution cells; feel/dynamic tags) → call key & count off ("number 4, key of D") → band realizes grid by ear (bass reads numbers/slashes, compers voice from quality grammar, drummer plays feel tag) → arranger shouts changes, chart keeps pace → final chart = durable artifact, re-usable in any key/ensemble | Voice 0 = degree-grid spine (chord-degree+quality+slash-bass per cell, realized as chordal units; harmonic DNA). Voice 1 = bass realization (root/slash-bass, walking/ostinato per feel). Voice 2 = comping realization (voicings from quality grammar, rhythm from hashmarks/pushes). Voice 3 = melody/lead (off-chart by design; optional human-authored). Voice 4 = rhythm/feel layer (meter, groove tag, tempo, push positions). Voice 5 = metadata (road-map labels, repeat/2nd-time operators, cues). Sections = road-map blocks (Intro→V1→Chorus→V2→Bridge→Chorus2nd→Tag). Rules: degree→pitch mapping from key (transposition invariance), default-major quality grammar, slash-bass rule, beat-grid hashmarks, push anticipation, split/boxed measure, form-repeat operators with 2nd-time cells, feel tags per section, integer-bar zero-drift cells, collective realization (V1–V2 rule-generated, never fully specified). | Neal Matthews Jr. & the Jordanaires (Elvis sessions; invented late 1950s), Charlie McCoy (bass/drums/piano/guitar charts), Nashville "A-Team" head sessions (Bob Moore, Harold Bradley, Grady Martin, Pig Robbins), Muscle Shoals rhythm section, Chas Williams (*The Nashville Number System* 1988), Mike McAdam (*The Nashville Number System: The Definitive Guide* 2017), contemporary church/jazz NNS readers | ✅ Documented |`

**Next free ID:** HC-098
