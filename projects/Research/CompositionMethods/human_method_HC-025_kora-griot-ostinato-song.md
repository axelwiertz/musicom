# Human Method HC-025 — West African Kora Griot Ostinato-Song Craft (Kumbengo / Birimintingo Layering)

- **Method ID:** HC-025
- **Method Name:** West African Kora Griot Ostinato-Song Craft (Kumbengo & Birimintingo Layering)
- **Tradition / Culture:** Mande griot (jeli/jali) tradition — Mali, Senegal, Gambia, Guinea, Guinea-Bissau; hereditary oral craft, instrument documented since the 17th century (Susundata / Tunji lineages), roots claimed to the medieval Mali Empire (13th c.). Distinct from HC-005 (Ewe drumming, Ghana/Togo): this is Sahelian *stringed* harp-lute song accompaniment, not drum ensemble.
- **Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix.
- **Date researched:** 2026-09-03 (nightly `daily-human-composition-research` job)
- **Status:** ✅ Documented

---

## 1. Method overview

The kora (21-string calabash harp-lute) is played by hereditary **griots** (*jeli*, pl.
*jeliŋo*; French *griot*) — genealogists, historians, and praise-singers who keep the
repertoire of the Mande courts. The compositional craft is a **layered ostinato
architecture** built by ONE pair of hands (or kora + voice):

1. **Kumbengo** (from *ku-mbeng*, "the base/what holds together") — a repeating
   ostinato cycle, interlocked between the two hands, that IS the identity of a piece.
   A kumbengo is to a kora piece what a riff is to funk: hear four notes and the
   knowledgeable listener names the song (*Lambango*, *Tutu Jara*, *Sutukung*, *Kelefaba*...).
2. **Birimintingo** — fast scalar/arpeggiated improvisation runs in the *upper* hand,
   woven OVER the frozen kumbengo, using patterns the player has practiced until they
   are automatic ("the fingers know").
3. **Donkilo / sataro** — the vocal layer: the griot sings the fixed tune plus praise
   formulas, genealogy recitation, and improvised proverbs over the same ostinato.

The human craft is therefore **hand-partition engineering**: a single performer
self-accompanies by running two independent but interlocking hand loops plus a sung
line — the stringed-instrument ancestor of call-and-response ostinato layering
(cf. HC-005 Ewe timeline + master drum; HC-018 clave + montuno).

## 2. Craft procedure (how a human does it)

1. **Learn inside a griot family.** Kora is hereditary; technique and repertoire pass
   father→son / master→apprentice by rote, never notation. A learner first internalizes
   tuning (*tomora ba* ≈ major, *tomora mesen*, *sauta* ≈ natural-minor-flavoured,
   *hardino*...; heptatonic, ~7 notes per octave, scale varies by family and region).
2. **Master the hand partition.** 21 strings in two ranks: LEFT hand = 11 bass/mid
   strings (thumb + index), RIGHT hand = 10 treble strings. Both hands play with thumb
   + index finger only, using down/up "strokes" so each hand alternates two-note
   figures. The player learns to keep a left-hand bass pulse cycling while the right
   hand either fills the interlock (kumbengo completion) or flies free (birimintingo).
3. **Acquire kumbengo for each song.** Every named piece owns one (or a small family
   of) kumbengo — a 1–2 bar loop (in ~12/8 or 4/4 feel) whose bass contour + melodic
   cell is the piece's fingerprint. The student memorizes it note-for-note from the
   master. Many classic kumbengo are centuries old and shared across families.
4. **Establish and hold the cycle.** In performance the kumbengo is stated first and
   repeated as a steady groove — metrically invariant, tempo set by the occasion
   (dance / praise / narrative).
5. **Layer birimintingo.** With the loop running "in the left hand + muscle memory,"
   the right hand launches fast runs: scalar descents/ascents across the treble rank,
   octave doublings, alternating-stroke tremolo figures. Crucial craft rule: the run
   must *land back into* the kumbengo on the cycle boundary — the listener should never
   hear the ostinato "drop."
6. **Sing over it (donkilo).** The griot adds the song: fixed tune of the named piece,
   then *sataro* — improvised praise text naming patrons/ancestors, proverbs, lineage
   recitation. Voice floats over the loop, phrases ending against kumbengo accents.
7. **Alternate layers as form.** A performance breathes: kumbengo alone (statement)
   → kumbengo + voice (verse) → kumbengo + birimintingo (instrumental showcase) →
   voice + dense runs (climax) → return to bare kumbengo to close. Contrast is made
   by *which layers are on*, exactly like arranging with a mute matrix.
8. **Cadence and stop.** Pieces often close with a short *fondamburung* / formulaic
   tag or simply by thinning to the loop and stopping on the cycle's tonal center.

## 3. Real practitioner examples

- **Sidiki Diabaté** (Bamako, 1922–1996) — "king of the kora"; his recorded kumbengo
  cycles and right-hand birimintingo define the Malian school; father of Toumani.
- **Toumani Diabaté** — *Kaira* (1988, first solo-kora album); *The Mandé Variations*
  (2008); Symmetric Orchestra; extended birimintingo over classic kumbengo.
- **Foday Musa Suso** (Gambia) — lineage player who carried kumbengo craft to the US;
  collaborations with Herbie Hancock, Philip Glass, Kronos Quartet.
- **Jali Nyama Suso** (Gambia) — radio-era master whose teaching sessions documented
  dozens of named kumbengo.
- **Sona Maya Jobarteh** — first female virtuoso of the hereditary line; contemporary
  pedagogue carrying the kumbengo/birimintingo division to new students.
- **Ballaké Sissoko** — *Kora Music Trio*; chamber-style interlocking with second kora.
- Classic named pieces whose identity = their kumbengo: *Lambango*, *Tutu Jara* (in
  multiple regional variants), *Sutukung*, *Kelefaba*, *Alla l'a ke*, *Jato*.

## 4. UnitMatrix mapping (Musicom engine)

The kora craft is a *natural* UnitMatrix shape: the Voices are literally the hand
partition + voice, and Sections are layer-mute states of one invariant loop.

**Voices (hand partition = voices):**

| Voice | Role | Content | Element |
| :--- | :--- | :--- | :--- |
| V0 | Kumbengo bass spine (left hand) | Invariant ostinato loop: bass contour + pulse. NEVER changes; piece identity lives here. | RHYTHM + PITCH (anchor) |
| V1 | Kumbengo treble interlock (right hand, "home" mode) | Fills the gaps of V0; together V0+V1 = the full kumbengo composite. Hocket-like interlock (≤1 event per subdivision across the pair). | TEXTURE + RHYTHM |
| V2 | Birimintingo run layer (right hand, "free" mode) | Fast scalar/arpeggio runs over the frozen loop; must re-enter V1's slot on cycle boundary. Density high, register high. | PITCH + TEXTURE |
| V3 | Donkilo / sataro vocal | Fixed tune + praise recitation; phrases float over cycle, endings align to kumbengo accents. | PITCH + STRUCTURE |

**Sections = layer-mask states of one invariant cycle:**

```
S0 Kumbengo alone (V0+V1)          → statement / establish groove
S1 + Voice (V0+V1+V3)              → verse (donkilo)
S2 + Birimintingo (V0+V1+V2)       → instrumental showcase
S3 All layers (V0+V1+V2+V3)        → climax (praise peak)
S4 Back to kumbengo (V0+V1) + tag  → closure
```

**Rules that encode the craft:**

- `kumbengo-invariance`: V0 (and V1's home pattern) fixed across all sections; the
  loop's cycle length N subdivisions is the global metric spine.
- `hand-partition-interlock`: across V0+V1 at most one onset per subdivision; bass
  rank pitches restricted to lower register band, treble rank to upper band
  (register stratification by hand).
- `rank-register-split`: V0 pitches ∈ [lo, split], V1/V2 pitches ∈ [split, hi]
  (models the two string ranks; split ≈ the kora's mid string).
- `alternating-stroke-vocabulary`: birimintingo runs built from alternating up/down
  two-stroke units (thumb-index alternation → adjacent-scale-step bias; octave jumps
  allowed at unit boundaries only).
- `run-reentry`: any V2 phrase must end at a cycle boundary (onset ≡ 0 mod N) on a
  kumbengo tone — the "land back in" rule.
- `layer-mask-form`: section = subset of {V1, V2, V3} switched on over invariant V0;
  V0 present in every section; at most one layer toggles per section boundary
  (gradual build/thin).
- `cycle-aligned-phrasing`: V3 phrase endings and V2 run landings target cycle
  accents (positions {0, N/2} typically).
- `heptatonic-mode-set`: all pitched layers draw from one 7-note family tuning
  (tomora ba / sauta / hardino set); no chromatic alteration inside a piece.
- `identity-by-cell`: the first 4–6 notes of V0+V1 composite are the piece's
  fingerprint — never varied; later loop content may receive small ornaments.
- `voice-over-loop-independence`: V3 rhythm need not match the grid (floating
  recitation), but its cadence tones snap to kumbengo accents.

## 5. Verification

- `HC-025` present in this detail file ✅
- Row appended to `human_methods_db.md` framework table ✅ (see report)
- No duplicate HC-025 rows ✅
- **Next free ID: HC-026**

## 6. Quirks / pitfalls

- **Not Ewe, not clave.** Kora craft shares the "invariant cycle + free layer" deep
  shape with HC-005 (timeline + master drum) and HC-018 (clave + montuno), but the
  human procedure is different: ONE player self-interlocks two hands, and identity
  lives in a *named melodic ostinato*, not a bell/clave pattern. Keep the methods
  distinct in the DB.
- **Tuning is a craft decision, not a given.** The same kora is retuned between
  pieces (tomora ba → sauta changes the modal color of the *same* kumbengo). Encode
  tuning as a per-piece mode set, not a global.
- **"Improvisation" is pre-practiced vocabulary.** Birimintingo runs are largely
  learned finger patterns recombined — model as a library of alternating-stroke
  figures, not free random walk, or output sounds wrong (too chromatic, wrong
  accents).
- **Re-entry discipline is the tell.** Human listeners judge competence by whether
  runs land back on the loop cleanly; a naive generator that decorrelates the run
  layer from the cycle will fail the griot ear-test.
- **Oral lineage = no canonical score.** Kumbengo exist in family variants; the DB
  entry documents the *craft*, not one authoritative note sequence.

## Source

Wikipedia — "Kora (instrument)" (construction, 21 strings in two ranks, tunings,
griot tradition, Susundata lineage, kora in world music); practitioner discographies
and liner-note scholarship for Sidiki/Toumani Diabaté, Foday Musa Suso, Jali Nyama
Suso, Ballaké Sissoko, Sona Jobarteh. Mande music literature on the
kumbengo/birimintingo distinction (Charry, *Mande Music*, 2000; Knight's kora
pedagogy transcriptions). Retrieved 2026-09-03.
