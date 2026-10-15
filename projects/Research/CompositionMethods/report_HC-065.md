# Report HC-065: Thai Piphat Thang Elaboration — One Melody, Many Paths (Luk Khong / Thamnong Lak + Stratified Heterophony)

## Overview

| Field | Value |
|---|---|
| **HC-ID** | HC-065 |
| **Method Name** | Thai Piphat Thang Elaboration — One Melody, Many Paths (Luk Khong / Thamnong Lak + Stratified Heterophony) |
| **Tradition / Culture** | Thai Classical — Central Thai court & temple *piphat* tradition (Ayutthaya 1351–1767 → Rattanakosin, Fine Arts Department canon); the ensemble of khon/lakhon theatre, ritual music, and the sacred *phleng rueang* suites |
| **Layer** | human (→ concrete) — target layer **concrete** when implemented |
| **Primary Elements** | TEXTURE, PITCH, STRUCTURE, RHYTHM, HARMONY |
| **Craft Process** | See 10-step procedure below |
| **Real Practitioner Examples** | Luang Pradit Phairoh, Montri Tramote, Prince Narisara Nuwattiwong, Mom Luang Tuan, Somsak Ketukaenchan, Bussakorn Binson-Sumrongthong, Fong Naam (Bruce Gaston/Boonrung Songchroa), Kru Yan Songmuangkean, David Morton (scholar) |
| **Status** | ✅ Documented |

---

## The Craft Procedure (10 steps — how the human does it)

1. **Learn the canon orally.** Thai classical music is transmitted by rote; 12–24 musicians perform from memory, no notation on stage. The composer's apprenticeship = years of absorbing the standard repertoire (sathukan invocation, phleng rueang suites, na phat theatre pieces, phleng khab rong singing tunes) and building a mental library of *thang* per instrument, per teacher (*kru*).
2. **Fix the luk khong** (structural melody, *neya phleng* = "the meat of the song"). Two-, four- or eight-phrase melody; phrase-end *luk tok* ("falling/pillar notes") define the piece. Most composition starts from an existing luk khong (canon, songs, drum melodies); brand-new luk khong are rare, new *phleng rueang* suites rarer still.
3. **Set thang (key) + na thap (drum pattern).** Seven equidistant transpositions (thang phiang o lang, nai, klang, phiang o bon, nok, klang haeb, chawa); ensembles pair two thangs for male/female vocal registers. The na thap (prop kai / song mai / phiset) on taphon+klong that repeats continuously; one cycle = one *jang hwa*; piece length measured in whole cycles.
4. **Set attra (density).** chan diao (1×, fast) / song chan (2×, medium) / sam chan (4×, slow). Extension craft: expand each structural note while keeping every luk tok aligned to drum-pattern cycle ends.
5. **Compose the vocal layer first where present** (phleng khab rong singing tunes, flexible) — action tunes (phleng prakop kiriya) are fixed and unchangeable. Pi nai shadows the singer; so u must anticipate and echo vocal variations.
6. **Distribute the thang.** Translate the luk khong into each instrument's idiom: ranat ek *keb* fast octave figuration (leader), pi nai sustained vibrato song-line, ranat thum low resonant echo, khong wong lek treble doubling. Each voice's *klon* (phrase style) is its player/teacher's fingerprint.
7. **Classify freedom (luk khong type gate).** *isara* (free variations, luk tok may even shift) / *bang khap* (strict — ceremonial like sathukan; kro roll sustains long notes, nothing altered) / *kueng bang khap kueng isara* (mixed — phrase-end pillars fixed, interior free).
8. **Assemble the macro-form.** Phleng Rueang suite: Cha (slow) → Song Mai (medium) → Rew (fast) → La (coda); or thao attra-cycling. Standard techniques: oad/phan modulation, tat thorn phrase-shortening, luk thao pitch emphasis, graded interval dissonance (koo kradang / kueng kradang / sanoh).
9. **Rehearse by ear under Rule 6** (Montri Tramote's 12 principles): individual variations must NEVER interfere with another instrument's function; the skeleton must stay audible.
10. **Perform — realization IS the composition.** No single player (except khong wong yai's reference) sounds the complete melody; the heard music = the stratification, re-created at every performance within the piece's freedom class. Thai musicians resist the word "improvisation" — the thang are memorized paths.

---

## Layer Classification

**Layer: human (→ concrete target when implemented)**

This is human craft knowledge — how a Thai piphat master realizes one structural melody into a stratified heterophonic texture. When implemented in the UnitMatrix, every thang layer becomes concrete note data (fixed pitch/duration sequences plus ornament profiles). Target layer = **concrete**: the khong wong yai spine is a literal pitch/duration sequence, and each elaboration voice is a concrete transformation of it.

---

## UnitMatrix Mapping (Voices & Sections, Rules)

**Voices:**

| Voice | Instrument | Role |
|---|---|---|
| V0 | Khong wong yai (16 gongs) | **Luk khong spine** — invariant structural melody, pitch reference; every section's cells derive from it. One pitch per structural slot. |
| V1 | Ranat ek (21–22 keys) | **Keb elaboration + leadership** — highest-density figuration around V0's pitches (octave fills); cue events at section transitions; extends/shortens phrases (leader function). |
| V2 | Pi nai | **Sustained song-like thang** — long-duration events, vibrato/bends on held tones; shadows vocal (V6) where present. |
| V3 | Ranat thum | **Low-resonant elaboration** — slower deeper counter-figuration; freest variation budget ("joker"); optional V3b = khong wong lek treble echo. |
| V4 | Ching/Chap | **Timekeeper grid** — open ching / closed chap alternating; chap = accented, phrase-TERMINAL (Thai stress at unit end, not downbeat). |
| V5 | Taphon + klong that | **Na thap colotomic grid** — repeating drum pattern cells; section length = integer na-thap cycles; luk tok alignment target. |
| V6 | Vocal (phleng khab rong) / so u | Optional singing layer on same luk khong; so u echoes vocal variations; silent in instrumental (phleng rueang) sections. |

**Sections:**
- Phleng Rueang movements: S0 Cha (slow, stately) → S1 Song Mai (medium) → S2 Rew (fast) → S3 La (farewell coda) — tempo/density escalates across the suite.
- OR thao attra levels: sam chan (4×) → song chan (2×) → chan diao (1×) — same melody, halving density each section.
- Each section spans an integer number of na-thap (jang hwa) cycles → natural zero-drift section length.

**Rules (encode in the realize layer):**
- **Luk khong invariance** — V0 frozen per piece; all voices derive from it.
- **Luk tok convergence** — phrase ends land on pillar pitch, aligned with chap stroke + na-thap boundary.
- **Thang-idiom mask per voice** — run-length/density windows: V1 fastest, V2 longest sustains, V3 lowest register; ornament vocabulary per instrument.
- **Luk-khong-type gate** — per piece/section flag ∈ {isara, bang khap, kueng-bang-khap}: strict pieces mirror V0 exactly in V1–V3 (kro sustain), mixed pieces lock phrase-end pillars only.
- **Seven-thang key lock** — global transposition offset; paired-thang pivot between sections for vocal register.
- **Attra density multiplier** — chan level sets uniform subdivision factor (1×/2×/4×) across all voices.
- **Na-thap count divisibility** — section lengths = whole na-thap cycles; validate gate enforces equal-length tracks.
- **Thai phrase-end stress** — accent/velocity maxima at unit ENDS; group/pad per Thai two-bar unit (= one Western 2/4 bar).
- **Variation-restraint (Rule 6)** — interference guard: no elaboration voice may obscure V0's skeleton or collide at luk-tok points.
- **Pentatonic skeleton set** — pitch pool from the working thang's five core tones (equidistant-7 scale idealized; Rahn 2019 'strict propriety' in practice → realize as pentatonic subset in 12-TET).

**Engine path:** `UnitMatrixComposer` (bpm/ticks_per_beat=480/beats_per_bar=4) → `create_matrix(7 voices, N sections)` → `add_voice` per instrument (`MidiInstrument.XYLOPHONE`, `OBOE`, `MARIMBA`, `TAIKO`-class percussion via channel 9, etc.) → `add_section` per Phleng Rueang movement / attra level → V0 cells = authored luk khong, V1/V3 = elaboration filter over V0, V4/V5 = fixed pattern cells, V2 = sustained transform → `validate()` (zero-drift gate MUST pass) → `to_midi()`. Artifacts → `projects/Research/outputs/<project>/`; provenance sidecar; preflight check.

---

## Table Row Added

```
| HC-065 | human (→concrete) | Thai Piphat Thang Elaboration — One Melody, Many Paths (Luk Khong / Thamnong Lak + Stratified Heterophony) | Thai Classical — Central Thai court & temple piphat (Ayutthaya 1351–1767 → Rattanakosin, Fine Arts Dept. canon); ensemble of khon/lakhon theatre & sacred phleng rueang | TEXTURE, PITCH, STRUCTURE, RHYTHM, HARMONY | Learn canon orally (perform from memory, no notation) → fix luk khong (neya phleng "meat of the song" = structural melody) on khong wong yai (16-gong reference voice) → set thang (key: one of seven transpositions for ensemble/vocal register) → set attra (chan diao/song chan/sam chan = 1×/2×/4× density) + na thap (repeating taphon drum pattern; piece length = integer cycles) → plae (translate) luk khong into each instrument's idiomatic thang: ranat ek keb rapid octave figuration (leader, cues), pi nai sustained song-like vibrato line, ranat thum low resonant echo → classify freedom (luk khong isara free / bang khap strict-ceremonial / kueng-bang-khap mixed, phrase-end pillars fixed) → anchor phrase ends to luk tok (pillar pitch on chap stroke = accent at phrase END, not downbeat) → assemble Phleng Rueang suite (Cha slow → Song Mai → Rew fast → La coda) or thao attra-cycling; modulate oad/phan, shorten tat thorn, emphasize luk thao → rehearse by ear under Tramote Rule 6 (variations never obscure the skeleton) | Voice 0 = khong wong yai (luk khong spine, invariant structural melody, pitch reference). Voice 1 = ranat ek (keb elaboration, highest density, ensemble leader + cue layer). Voice 2 = pi nai (sustained song-like thang, closest to vocal, vibrato). Voice 3 = ranat thum (low resonant elaboration, freer "joker" variation; opt. khong wong lek treble echo). Voice 4 = ching/chap (timekeeper: open ching + closed chap alternating; chap = phrase-terminal accent). Voice 5 = taphon + klong that (na thap colotomic grid; luk tok lands at pattern end). Voice 6 = optional vocal (phleng khab rong) / so u echo. Sections = Phleng Rueang movements (S0 Cha → S1 Song Mai → S2 Rew → S3 La) or thao attra levels (sam chan→song chan→chan diao); each section = integer na-thap (jang hwa) cycles. Rules: luk khong invariance, luk tok convergence (pillar pitch on chap at phrase end), thang-idiom mask per voice, luk-khong-type gate (isara/bang khap/mixed per piece & section), kro sustain rule in strict pieces, seven-thang key lock + paired-thang pivot, attra density multiplier, pentatonic skeleton set (equidistant-7 in theory, Rahn 'strict propriety' in practice), Thai phrase-end stress (zero-drift pad per Thai 2-bar unit), na-thap count divisibility, variation-restraint interference guard | Luang Pradit Phairoh (Sorn Silapabanleng, court master, canon-fixing director), Montri Tramote (National Artist 1985, 200+ pieces, theory systematizer), Prince Narisara Nuwattiwong (piphat duek dam ban), Mom Luang Tuan (Phra Lo music, lakhon phanthang), Somsak Ketukaenchan (thang khong/ranat ek dissertation), Bussakorn Binson-Sumrongthong (ranat ek keb improvisation), Fong Naam (Bruce Gaston/Boonrung Songchroa, phleng rueang revival), Kru Yan Songmuangkean (Nan Puja drum → piphat translation), David Morton (polyphonic stratification 1976) | ✅ Documented |
```

Appended after the HC-064 row (line 70 → 71) in `human_methods_db.md`. Table remains clean: HC-001…HC-065 sequential, one row per ID.

---

## Next Free ID

**HC-066** (max existing = HC-065; no HC-066 anywhere in table, detail files, or reports).

---

## Quirks & Pitfalls

1. **Accent polarity inverted vs. Western practice** — the Thai strong beat (chap) CLOSES the phrase; a downbeat-centric realization sounds wrong. Encode stress at phrase end.
2. **"Improvisation" is a misnomer** — Thai elaboration = constrained re-elaboration of memorized thang paths, never free generation; the engine's variation layer must be derivation-from-spine, not stochastic fill.
3. **Strict pieces allow ZERO variation** — sathukan and action tunes (luk khong bang khap) must be realized verbatim (kro sustain for long notes); a blanket ornamentation rule destroys ceremonial correctness.
4. **Equidistant-7 scale is an ideal, not a measurement** — Rahn (2019) showed 'strict propriety' (ordered, unequal steps). Realize as a pentatonic subset in 12-TET; do not attempt microtonal quantization in the UnitMatrix.
5. **Lineage variance is legitimate** — thang differ by teacher/school; the rules encode constraints, not one canonical output. Documenting a "reference" ranat ek version is an abstraction.
6. **Oral canon** — the living practice exceeds the notated record; verified core melodies live in Fine Arts Department notation volumes (Tramot's series) and modern transcriptions (Ketukaenchan, Phonron).
7. **Na-thap grid is the zero-drift anchor** — treating the na thap cycle (not the Western bar) as the section unit is what keeps all seven voices aligned; the Thai two-bar unit ≈ one Western 2/4 bar for padding math.

---

## Sources

- Artit Phonron, *Making Music in Thai Music Theatre: the interaction between music, narrative and dance in Lakhon Phanthang* (PhD, Goldsmiths, Univ. of London, 2025) — thamnong lak & luk khong types, ching/na thap mechanics, seven thangs, attra levels, ranat ek leadership, Tramote's principles, so u "joker" role
- Pattara Komkhum & Kumkom Pornprasit, "Thai Classical Music Composition: Pleng Ruang Puja Nakhon Nan," *Journal of Urban Culture Research* 10 (2015) — neya phleng, thang khong translation method, Pleng Ruang four-movement structure, oad/phan/tat thorn/luk thao techniques
- Bussakorn Sumrongthong, "The Improvisation of Thai Xylophone or Ranaat Eek," *Manusya* 1(1) (1998) — keb technique
- Somsak Ketukaenchan, *The Thang of the Khong Wong Yai and Ranat Ek: A Transcription and Analysis of Performance Practice in Thai Music* (PhD) — primary thang-comparison documentation
- David Morton, *The Traditional Music of Thailand* (1976) — "polyphonic stratification"
- Jay Rahn, tuning study of 28 Thai ensembles (2019) — "strict propriety"
- D. Swangviboonpong, *Thai Court Singing* (2000) — luk tok significance on ching beats
- Montri Tramote, *Duriyasan* / *Khambanyai wicha duriyangkhasat Thai* (1995/2002) — musician hierarchy, 12 principles, theory canon