# REPORT — HC-060: Verbunkos Composition — Lassú–Friss Recruiting-Dance Architecture

- **Method ID**: HC-060
- **Method Name**: Verbunkos Composition — Lassú–Friss Recruiting-Dance Architecture (Verbunkos-Scale Melody & Cigányzenekar Accompaniment Craft)
- **Tradition / Culture**: Hungarian — Habsburg military recruiting dance (1720s–1849); cultivated by Romani cigányzenekar bands and the "national trio" Bihari/Lavotta/Csermák (c. 1800); absorbed into Western art music as *style hongrois* (Haydn, Schubert, Beethoven, Liszt, Brahms, Erkel, Kodály, Bartók); descendant csárdás; cousin Slovácko verbuňk (Moravia, UNESCO ICH 2008)
- **Layer**: `concrete` (target) — human-craft knowledge realized through the UnitMatrix as resolved voices/sections; no generative abstraction required
- **Primary Elements** (Musical Elements Framework): STRUCTURE, RHYTHM, PITCH, TEXTURE, HARMONY
- **Date**: 2026-10-09 (nightly human-composition-research job)

---

## 1. ID resolution (dynamic)

- Scanned `human_methods_db.md` Human Composition Methods Framework table: max existing row = **HC-059** (Hawaiian Slack-Key Guitar, line 65).
- Cross-checked `human_method_HC-*.md` (59 files, max HC-059) and `report_HC-*.md` (max HC-059).
- No HC-060 anywhere (only mention found: report_HC-059.md noting "Next free ID = HC-060").
- **New ID = HC-060** (max+1). **Next free ID = HC-061.**

## 2. Why this method (gap analysis)

Recent entries: HC-055 fugue (Western Classical), HC-056 qawwali (South Asia), HC-057 fado (Portugal), HC-058 samba batucada (Brazil), HC-059 slack key (Hawai'i). East-Central Europe was covered only by Bulgarian aksak (HC-019) and Ashkenazi klezmer (HC-037). **Nothing covered Hungary or the Habsburg civilizational sphere.** Verbunkos fills that gap with a strongly *architectural* human craft: a tempo-arc form (lassú→friss), a distinctive scale system (Hungarian minor with raised 4th), a fixed ensemble accompaniment lock (bőgő/kontra/cimbalom), and a named cadential formula (bokázó) — all highly encodable as UnitMatrix rules, plus a deep practitioner lineage from folk-ritual to Liszt/Brahms/Kodály/Bartók.

## 3. The craft procedure (how a human does it)

The verbunkos is choreographed social ritual translated into music: a dozen hussars recruited recruits by dancing in rank order — sergeant slow and dignified first, officers livelier, youngest soldiers finishing with jumps and spur-clicking — while a Romani band played music of steadily *increasing speed and brilliance*. The composer's procedure:

1. **Fix strictly duple meter** (2/4 or 4/4; march step). No asymmetric meters.
2. **Choose the verbunkos scale** — Hungarian minor / "Gypsy scale": 1–2–♭3–♯4–5–♭6–7 (harmonic minor with raised 4th). The two augmented seconds (♭3–♯4, ♭6–7) are the identity markers. Variants: verbunkos-dorian, verbunkos-phrygian, verbunkos-lydian, major-with-augmented-second (Loya's taxonomy). Plan a parallel-major finale.
3. **Compose the hallgató** — "melody without words": free, rubato/parlando, rhapsodic, ornament-dense, no dance pulse. The prímás's cadenza-like prelude.
4. **Compose the lassú** — majestic slow dance in dotted rhythm (♩.♪ dotted-quarter+eighth); fingerprint cell = "verbunkos rhythm" (♪.♫ dotted-eighth+sixteenth). Wide-arched melody with single climax; ends with the **bokázó figure** (cambiata-type turn, from heel-clicking) over the cadence.
5. **Lay the accompaniment lock** (cigányzenekar: prímás violin, kontra viola, bőgő bass, later cimbalom, optionally clarinet/tárogató): bőgő dűvő strokes (root/5th on beats, invariant, never rests); kontra 3-voice chordal strokes in off-beat gaps; cimbalom percussive punctuation + tremolo at cadences.
6. **Compose the first friss** — fast, *giusto*: triplet girdles, 16th-note runs, strict accents, syncopation.
7. **Add further friss sections, each faster** — the ritual's escalation: monotonic accelerando across sections, cifra (ornamented) virtuoso figuration, higher register.
8. **Resolve the final friska to the parallel major** — Liszt/Kodály convention: cimbalom-like resonant figuration, "stable major-mode resolutions".
9. **Close with the bokázó cadence** — rapid figure + heel-click V–I cadential formula, often over trill/pedal.
10. **Optional**: alternate lassú/friss pairs at greater length — the csárdás lineage.

The melody is composed (fixed skeleton); the surface is improvised (prímás ornaments: trills, double stops, pizzicato, runs — *extempore ornamentations and paraphrases*, per Szabolcsi). Sections carry the form via tempo and density, NOT via thematic transformation.

## 4. Real practitioner examples

- **János Bihari (1764–1827)** — "father of verbunkos"; Romani violinist; ~84 compositions; Pest band from 1801; played through the Congress of Vienna (1814); Rákóczi March attribution (legendary); Liszt heard him.
- **János Lavotta (1764–1820)** — *Nota insurrectionalis hungarica* (1797), first verbunkos programme music; theatre conductor at Pest-Buda.
- **Antal Csermák (1774–1822)** — first Hungarian chamber dance sets; Viennese-influenced.
- **József Kossovits (d. c. 1819)** — 12 *Danses Hongroises* (c. 1800); **Ignác Ruzitska** — *Magyar nóták Veszprém Vármegyéből* (1823–32); **Márk Rózsavölgyi (1789–1848)** — late verbunkos → csárdás transition.
- **Ferenc Erkel** — national opera (*Hunyadi László* 1844, *Bánk bán* 1861) in verbunkos idiom.
- **Style hongrois**: Haydn *"Gypsy Rondo"* (Piano Trio Hob. XV:25, 1795); Schubert *Divertissement à la hongroise* D. 818 (1824); Brahms *Hungarian Dances* (on Bihari/Lavotta/Csermák/Ruzitska material); **Liszt** *Hungarian Rhapsody No. 2* — canonical lassú→friska (unmetered cadenza opening, dotted lassú theme, accelerating friska to major climax); **Kodály** *Dances of Galanta* (1933); **Bartók** *Contrasts* (1938) mvmt. I "Verbunkos", Violin Concerto No. 2.
- **Living practice**: táncház (dance-house) revival 1970s–present (Muzsikás et al.); Slovácko verbuňk (Czech/Moravian) UNESCO-listed 2008 — three-part song→slow→fast form.

## 5. UnitMatrix mapping

### Voices (rows)

| Voice | Instrument/role | Content role |
|---|---|---|
| V0 | Bőgő (double bass) | Dűvő strokes: root/5th on beats, invariant pulse, never rests (silent only in S0) |
| V1 | Prímás (lead violin) | Composed melody skeleton — hallgató, lassú, all friss themes; piece identity |
| V2 | Kontra (3-string viola) | Chordal strokes in off-beat gaps; harmony rhythm; fills |
| V3 | Cimbalom | Percussive chordal punctuation; tremolo at cadences/holds |
| V4 | Ornament/cifra layer | Surface only: trills, double-stops, pizzicato, 16th/triplet runs; sparse lassú, dense friss; no new pitch classes in lassú |
| V5 | Clarinet/tárogató (optional) | Counter-melody / doubling, urban bands |

### Sections (columns)

`S0 Hallgató` (free rubato) → `S1 Lassú I` (dotted, minor) → `S2 Lassú II` (contrasting strain) → `S3 Friss I` (giusto, runs) → `S4 Friss II` (faster, cifra) → `S5 Friska climax` (max tempo, parallel-major) → `S6 Closing tag` (trill/pedal + bokázó V–I).

### Rules (what would encode it in the engine)

1. **Verbunkos-scale lock** — pitch set 1–2–♭3–♯4–5–♭6–7; ♯4 structural; augmented-2nd contour fences.
2. **Lassú dotted profile** — ♩.♪ and ♪.♫ dominance; no even-note monotony.
3. **Friss giusto profile** — triplets + 16ths; strict accents; off-beat syncopation.
4. **Monotonic tempo map** — lassú 50–70 bpm → friss 120–160+; each successive friss faster; accelerando at transitions.
5. **Bőgő dűvő invariance** — V0 never rests (except hallgató gate).
6. **Kontra interlock** — V2 onsets never coincide with V0 onsets (off-beat slot; mirrors HC-053 hand-partition).
7. **Bokázó cadence formula** — cambiata-type figure over V–I at every section end.
8. **Ornament-skeleton separation** — V1 pitches invariant; V4 surface only.
9. **Major-resolution gate** — final friss in parallel major.
10. **Hallgató gate** — S0 exempt from tempo map and V0 pulse.
11. **Zero-drift** — equal-length sections (UnitMatrix invariant).

Engine realization note: 2/4 meter via `beats_per_bar=2` (or 4/4 hypermeter); alternate lassú/friss sections as repeated column groups (S1/S2 ↔ S3/S4) for the csárdás-style extended form; V0/V2 onset-separation enforced at fill time; bpm changes modeled per-section (tempo meta events at section boundaries).

## 6. Table row appended to `human_methods_db.md`

```
| HC-060 | human (→concrete) | Verbunkos Composition — Lassú–Friss Recruiting-Dance Architecture (Verbunkos-Scale Melody & Cigányzenekar Accompaniment Craft) | Hungarian — Habsburg recruiting dance (1720s–1849), cultivated by Romani cigányzenekar bands & the Bihari/Lavotta/Csermák "national trio" (c. 1800); style hongrois in Haydn/Schubert/Liszt/Brahms/Erkel/Kodály/Bartók; descendant csárdás; cousin Slovácko verbuňk (Moravia, UNESCO ICH 2008) | STRUCTURE, RHYTHM, PITCH, TEXTURE, HARMONY | <craft steps — see detail file> | <UnitMatrix mapping — see detail file> | <practitioners — see detail file> | ✅ Documented |
```

(Appended as line 66, directly after the HC-059 row.)

## 7. Verification

- ✅ `grep HC-060` in detail file `human_method_HC-060_verbunkos-lassu-friss.md` → found (title + body, 12,862 bytes).
- ✅ `grep HC-060` in `human_methods_db.md` → exactly 1 table row (line 66, after HC-059).
- ✅ No duplicate HC-060 row pre-existed; no `human_method_HC-060*` / `report_HC-060*` files pre-existed.
- ✅ Prior max confirmed HC-059 before write; new ID = 060 = max+1.
- **Next free ID: HC-061.**

## 8. Quirks & pitfalls

1. **Not klezmer (HC-037)**: same East-Central European string-band orbit, but klezmer = shteyger modes with neutral seconds, wedding script of distinct dance types, no intra-piece slow→fast ramp; verbunkos = one piece, tempo-arc form, augmented-2nd scale. Keep distinct.
2. **♯4 is structural**: encoding verbunkos as plain harmonic minor + occasional raised 4th misses the identity; the augmented seconds are contour-grammar fences, and the scale family (minor/dorian/phrygian/lydian versions, per Loya) is the mode system.
3. **"Gypsy" is a style label**: melodies are Hungarian; Romani bands were carriers/performers. Do not equate performer ethnicity with musical origin (Bellman).
4. **Bihari was not a Viennese-style composer**: self-taught, largely improvised, orally transmitted; the surviving 84 pieces were written down by others; Rákóczi March attribution is legendary.
5. **Hallgató vs lassú blur** in early sources: model them as separate stages (S0 free prelude vs S1 slow dance).
6. **Friss sections are not variations** (≠ HC-026 pibroch, ≠ HC-039 Irish setting): new figuration and often new material; density + tempo carry the arc.
7. **Spelling of notes**: dialect spellings (verbunkos/verbunko/werbunkos; lassú/lassan; friss/friska; csárdás/czardas) all denote the same lineage — grep-friendly canonical forms chosen above.

## 9. Files

| Artifact | Path | Status |
|---|---|---|
| Detail file | `human_method_HC-060_verbunkos-lassu-friss.md` | ✅ 12,862 bytes |
| DB row | `human_methods_db.md` line 66 | ✅ appended |
| This report | `report_HC-060.md` | ✅ primary record |
| Next free ID | **HC-061** | — |