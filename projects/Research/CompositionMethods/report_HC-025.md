# Report — HC-025: West African Kora Griot Ostinato-Song Craft (Kumbengo & Birimintingo Layering)

- **Method ID:** HC-025
- **Method Name:** West African Kora Griot Ostinato-Song Craft (Kumbengo & Birimintingo Layering)
- **Tradition / Culture:** Mande griot (jeli/jali) tradition — Mali, Senegal, Gambia, Guinea, Guinea-Bissau; hereditary oral craft; Sahelian 21-string harp-lute (kora), documented since the 17th c. (Susundata / Tunji lineages), roots claimed to the medieval Mali Empire (13th c.).
- **Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix.
- **Date researched:** 2026-09-03 (nightly `daily-human-composition-research` job)
- **Status:** ✅ Documented

---

## 1. Method overview

The kora is a 21-string calabash harp-lute played by hereditary **griots** (*jeli*) —
genealogists, historians, and praise-singers of the Mande courts. Its compositional
craft is a **layered ostinato architecture** run by a single performer (kora + voice):

1. **Kumbengo** (from *ku-mbeng*, "the base / what holds together") — a repeating
   ostinato loop, interlocked between the two hands, that IS the identity of a piece.
   Four notes of a kumbengo name the song for a knowledgeable listener (*Lambango*,
   *Tutu Jara*, *Sutukung*, *Kelefaba*...).
2. **Birimintingo** — fast scalar/arpeggiated runs in the upper hand, woven OVER the
   frozen kumbengo, built from patterns practiced until automatic ("the fingers know").
3. **Donkilo / sataro** — the vocal layer: fixed tune plus praise formulas, genealogy
   recitation, and improvised proverbs over the same ostinato.

The human craft is **hand-partition engineering**: one performer self-accompanies by
running two independent but interlocking hand loops plus a sung line — the stringed
ancestor of call-and-response ostinato layering (cf. HC-005 Ewe timeline + master
drum; HC-018 clave + montuno). It is distinct from those: identity lives in a *named
melodic ostinato played by one pair of hands*, not a bell/clave pattern.

## 2. Craft procedure (how a human does it)

1. **Learn inside a griot family.** Kora is hereditary; technique and repertoire pass
   master→apprentice by rote, never notation. First internalize tuning (*tomora ba* ≈
   major, *tomora mesen*, *sauta* ≈ natural-minor-flavoured, *hardino*...; heptatonic,
   ~7 notes/octave, varies by family and region).
2. **Master the hand partition.** 21 strings in two ranks: LEFT = 11 bass/mid strings
   (thumb + index), RIGHT = 10 treble. Both hands use thumb + index only, down/up
   "strokes," so each hand alternates two-note figures. Keep the left-hand bass pulse
   cycling while the right hand fills the interlock or flies free.
3. **Acquire the kumbengo for each song.** Every named piece owns one (or a small
   family of) kumbengo — a 1–2 bar loop (12/8 or 4/4 feel) whose bass contour +
   melodic cell is the fingerprint. Memorized note-for-note; many are centuries old.
4. **Establish and hold the cycle.** The kumbengo is stated first and repeated as a
   steady groove — metrically invariant, tempo set by occasion (dance/praise/narrative).
5. **Layer birimintingo.** With the loop running, the right hand launches runs: scalar
   descents/ascents, octave doublings, alternating-stroke tremolo figures. The run must
   *land back into* the kumbengo on the cycle boundary — the ostinato never "drops."
6. **Sing over it (donkilo/sataro).** Fixed tune first, then sataro — improvised praise
   naming patrons/ancestors, proverbs, lineage. Voice floats over the loop, phrase
   endings aligned to kumbengo accents.
7. **Alternate layers as form.** Kumbengo alone → +voice → +birimintingo → all layers
   (climax) → bare kumbengo + tag (close). Contrast = which layers are switched on,
   exactly like a mute-matrix arrangement.
8. **Cadence/stop.** Close with a short formulaic tag (*fondamburung*-type figure) or
   thin to the loop and stop on the cycle's tonal center.

## 3. Real practitioner examples

- **Sidiki Diabaté** (Bamako, 1922–1996) — "king of the kora"; his recorded kumbengo
  cycles and birimintingo define the Malian school; father of Toumani.
- **Toumani Diabaté** — *Kaira* (1988, first solo-kora album); *The Mandé Variations*
  (2008); Symmetric Orchestra; extended birimintingo over classic kumbengo.
- **Foday Musa Suso** (Gambia) — lineage player who carried kumbengo craft to the US;
  collaborations with Herbie Hancock, Philip Glass, Kronos Quartet.
- **Jali Nyama Suso** (Gambia) — radio-era master; teaching sessions documented dozens
  of named kumbengo.
- **Sona Maya Jobarteh** — first female virtuoso of the hereditary line; contemporary
  pedagogue carrying kumbengo/birimintingo to new students.
- **Ballaké Sissoko** — *Kora Music Trio*; chamber-style interlocking with second kora.
- Classic named pieces whose identity = their kumbengo: *Lambango*, *Tutu Jara*,
  *Sutukung*, *Kelefaba*, *Alla l'a ke*, *Jato*.

## 4. UnitMatrix mapping (Musicom engine)

The kora craft is a *natural* UnitMatrix shape: Voices = hand partition + voice;
Sections = layer-mute states of one invariant loop.

**Voices (hand partition = voices):**

| Voice | Role | Content | Element |
| :--- | :--- | :--- | :--- |
| V0 | Kumbengo bass spine (left hand) | Invariant ostinato loop: bass contour + pulse. NEVER changes; piece identity lives here. | RHYTHM + PITCH (anchor) |
| V1 | Kumbengo treble interlock (right hand, "home" mode) | Fills gaps of V0; together V0+V1 = full kumbengo composite. Hocket-like interlock. | TEXTURE + RHYTHM |
| V2 | Birimintingo run layer (right hand, "free" mode) | Fast scalar/arpeggio runs over the frozen loop; re-enters V1's slot on cycle boundary. | PITCH + TEXTURE |
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

- `kumbengo-invariance`: V0 (and V1's home pattern) fixed across all sections; cycle
  length N subdivisions = global metric spine.
- `hand-partition-interlock`: across V0+V1 at most one onset per subdivision; bass rank
  restricted to lower register band, treble rank to upper band.
- `rank-register-split`: V0 pitches ∈ [lo, split], V1/V2 ∈ [split, hi] (models the two
  string ranks; split ≈ the kora's mid string).
- `alternating-stroke-vocabulary`: birimintingo runs built from alternating up/down
  two-stroke units (thumb-index alternation → adjacent-scale-step bias; octave jumps at
  unit boundaries only).
- `run-reentry`: any V2 phrase must end at a cycle boundary (onset ≡ 0 mod N) on a
  kumbengo tone — the "land back in" rule.
- `layer-mask-form`: section = subset of {V1, V2, V3} on over invariant V0; V0 present
  in every section; at most one layer toggles per section boundary (gradual build/thin).
- `cycle-aligned-phrasing`: V3 phrase endings and V2 run landings target cycle accents
  (typically positions {0, N/2}).
- `heptatonic-mode-set`: all pitched layers draw from one 7-note family tuning (tomora
  ba / sauta / hardino set); no chromatic alteration inside a piece.
- `identity-by-cell`: first 4–6 notes of the V0+V1 composite = fingerprint, never
  varied; later loop content may receive small ornaments.
- `voice-over-loop-independence`: V3 rhythm need not match the grid (floating
  recitation), but cadence tones snap to kumbengo accents.

## 5. Table row added

```
| HC-025 | human (→concrete) | West African Kora Griot Ostinato-Song Craft (Kumbengo & Birimintingo Layering) | Mande griot (jeli) tradition — Mali/Senegal/Gambia/Guinea, hereditary oral craft; Sahelian 21-string harp-lute (kora), roots in the Mali Empire (13th c.) | RHYTHM, PITCH, TEXTURE, STRUCTURE | Learn inside a griot family (rote, no notation) → master hand partition (left = 11 bass strings, right = 10 treble; thumb+index two-stroke alternation) → acquire the named kumbengo ostinato loop (piece fingerprint) → hold the invariant cycle → layer birimintingo (fast practiced runs that re-enter the loop on the boundary) → sing donkilo/sataro over the loop → alternate layer masks as form → close by thinning to bare kumbengo + tag | Voice 0 = kumbengo bass spine (left-hand invariant loop, piece identity). Voice 1 = kumbengo treble interlock (right-hand home pattern filling V0's gaps, hocket-like). Voice 2 = birimintingo run layer (fast scalar/arpeggio runs, re-enters loop on cycle boundary). Voice 3 = donkilo/sataro vocal (fixed tune + praise recitation, phrases snap to cycle accents). Sections = layer-mask states (kumbengo alone → +voice → +runs → all layers → back to kumbengo). Rules: kumbengo-invariance, hand-partition-interlock (≤1 onset/subdivision across V0+V1), rank-register-split, alternating-stroke-vocabulary, run-reentry (V2 ends ≡ 0 mod N), layer-mask-form, cycle-aligned-phrasing, heptatonic-mode-set, identity-by-cell | Sidiki Diabaté (king of the kora), Toumani Diabaté (Kaira 1988; The Mandé Variations 2008), Foday Musa Suso (Gambia → Kronos/Glass/Hancock), Jali Nyama Suso, Sona Jobarteh, Ballaké Sissoko; named kumbengo: Lambango, Tutu Jara, Sutukung, Kelefaba, Alla l'a ke, Jato | ✅ Documented |
```

## 6. Verification

- `HC-025` present in detail file `human_method_HC-025_kora-griot-ostinato-song.md` ✅
- `HC-025` present in `human_methods_db.md` framework table (exactly 1 row) ✅
- No duplicate HC-025 rows ✅
- Highest existing ID confirmed HC-024 before write; new ID = 025 (max+1) ✅
- **Next free ID: HC-026**

## 7. Quirks / pitfalls

- **Not Ewe, not clave.** Shares the "invariant cycle + free layer" deep shape with
  HC-005 (timeline + master drum) and HC-018 (clave + montuno), but the human procedure
  differs: ONE player self-interlocks two hands, and identity lives in a *named melodic
  ostinato*, not a bell/clave pattern. Keep distinct in the DB.
- **Tuning is a craft decision, not a given.** Same kora retuned between pieces (tomora
  ba → sauta changes the modal color of the *same* kumbengo). Encode tuning as a
  per-piece mode set, not a global.
- **"Improvisation" is pre-practiced vocabulary.** Birimintingo runs are largely learned
  finger patterns recombined — model as a library of alternating-stroke figures, not a
  free random walk, or output sounds wrong (too chromatic, wrong accents).
- **Re-entry discipline is the tell.** Listeners judge competence by whether runs land
  back on the loop cleanly; a generator that decorrelates the run layer from the cycle
  will fail the griot ear-test.
- **Oral lineage = no canonical score.** Kumbengo exist in family variants; the entry
  documents the *craft*, not one authoritative note sequence.

## Source

Wikipedia — "Kora (instrument)" (construction, 21 strings in two ranks, tunings, griot
tradition, Susundata lineage, kora in world music); practitioner discographies and
liner-note scholarship for Sidiki/Toumani Diabaté, Foday Musa Suso, Jali Nyama Suso,
Ballaké Sissoko, Sona Jobarteh. Mande music literature on the kumbengo/birimintingo
distinction (Charry, *Mande Music*, 2000; Knight's kora pedagogy transcriptions).
Retrieved 2026-09-03.
