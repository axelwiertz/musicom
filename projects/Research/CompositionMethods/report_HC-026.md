# Report — HC-026: Scottish Pibroch Theme-and-Variation (Ceòl Mór — Ùrlar + Movement Ornamentation)

- **Method ID:** HC-026
- **Method Name:** Scottish Pibroch Theme-and-Variation (Ceòl Mór — Ùrlar + Movement Ornamentation)
- **Tradition / Culture:** Scottish Highlands — *piobaireachd* / *ceòl mór* ("the great music") of the Great Highland Bagpipe, descending from the earlier wire-strung Gaelic harp (*clàrsach*) and Scottish fiddle traditions; hereditary piping dynasties (MacCrimmons of Dunvegan/Skye, MacArthurs of Sleat), ~16th c.–present; orally transmitted via *canntaireachd* (chanted vocables).
- **Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix.
- **Date researched:** 2026-09-04 (nightly `daily-human-composition-research` job)
- **Status:** ✅ Documented

---

## 1. Method overview

Pibroch (Gaelic *piobaireachd*, literally "piping"; the art-music form is *ceòl mór*,
"great music", as against *ceòl beag* — reels, marches, strathspeys) is the extended
**theme-and-variation** art music of the Scottish Highlands. A single melodic line
(the chanter, a 9-note scale over a fixed three-pipe drone) carries an entire extended
composition through a fixed sequence of **movements**, each of which is the *same
theme* re-decorated with a progressively more elaborate set of gracenote ornaments.

The core human insight: because the bagpipe **cannot rest and cannot change dynamics**,
all musical development must happen through **embellishment density and tempo**, not
silence or loudness. The piper composes by fixing an **ùrlar** (ground/theme), then
re-stating it through a rising ladder of ornament-masks (siubhal → dithis → leumluath
→ taorluath → crùnluath), each played as singling then doubling, then returning to the
ground. The skeleton never changes; the craft is entirely in how it is dressed. This is
the oral-tradition counterpart to Classical theme-and-variation, but variation is a
*pure ornament-ramp* — the same notes successively "crowned" with gracenote clusters.

## 2. Craft procedure (how a human does it)

1. **Learn by ear via canntaireachd.** Sung before played. The Nether Lorn canntaireachd
   (from Campbell Canntaireachd MSS 1797/1814) encodes each gracenote movement as a
   syllable ("hin-darid-hio-din…"). The learner internalizes exact durations/tempo by
   singing, which staff notation flattens. Staff notation (MacKay 1845, Kilberry 1969,
   Piobaireachd Society books) is simplified shorthand, not the truth.
2. **Fix drone + scale.** Fixed drone (bass A + two tenor As); fixed 9-note chanter
   scale (~G-mixolydian, flattened 7th). No dynamics, no rests, no chromaticism.
3. **Compose the ùrlar (ground).** Slow stylised theme with connecting notes and
   embellishments; internal phrase order is Primary (AAB ABB AB), Secondary (ABCD CBAD
   CD), Tertiary (AB ABB AB C), or Irregular.
4. **State the ground** first, slow, with expressive timing.
5. **Run the movement ladder** — siubhal (gracenote before each theme note), dithis
   (cut note after), leumluath/taorluath/crùnluath (gracenote grips of increasing
   cluster size), each as singling then doubling with slightly increased tempo.
6. **Return to the ground** — an arch form after the crùnluath peak.
7. **Pass on orally** through performance lineages (Cameron = rounded; MacPherson =
   clipped).

## 3. Real practitioner examples

- **MacCrimmon dynasty** (Skye) — Donald Mor (c.1570–1640) and Patrick Mor (c.1595–1670),
  hereditary pipers to the MacLeods of Dunvegan.
- **MacArthur dynasty** (Sleat) — pipers to the MacDonalds; "college" of ceòl mór
  instruction continuing the Irish bardic model.
- **Angus MacKay** — *A Collection of Ancient Piobaireachd* (1845).
- **Archibald Campbell** — *The Kilberry Book of Ceòl Mór* (1969).
- **Donald MacLeod, William McCallum, Roderick MacLeod, Allan MacDonald** — modern
  masters; MacDonald, Barnaby Brown, William Donaldson led recovery of pre-1845 settings.
- **Cameron / MacPherson styles** — the two dominant performance lineages.
- **Simon Fraser** (1845–1934, Melbourne) — preserved ~140 ornate pibroch outside the
  Society standardization.
- Classic titles: *Lament for Patrick Og MacCrimmon*, *Lament for the Harp Tree*, *Too
  Long in This Condition*, *The Piper's Warning to His Master*, *The Big Spree*.

## 4. UnitMatrix mapping (Musicom engine)

Single chanter over a drone, but the craft decomposes into theme skeleton + per-movement
ornament layer — the UnitMatrix shape:

**Voices:**

| Voice | Role | Content | Element |
| :--- | :--- | :--- | :--- |
| V0 | Drone (invariant) | Fixed bass A + two tenor As — continuous, never changes, no rest. | HARMONY (pedal) |
| V1 | Ùrlar theme skeleton | The ground's structural melody notes — piece identity. Same sequence in every movement. | PITCH + STRUCTURE (anchor) |
| V2 | Ornament/embellishment layer | Movement-specific gracenotes: siubhal pair-notes, dithis cut-notes, taorluath/crùnluath grips. Density ramps per movement. | TEXTURE + RHYTHM |

**Sections = the movement ladder (arch form):**

```
S0 Ùrlar (V0+V1, bare ground)          → statement, slow
S1 Siubhal (V0+V1+V2[siubhal mask])    → single gracenote before each theme note
S2 Dithis  (V0+V1+V2[dithis mask])     → cut note after each theme note
S3 Leumluath → Taorluath               → gracenote grips, increasing cluster size
S4 Crùnluath singling → doubling        → densest grip, climax
S5 Return to Ùrlar (V0+V1)             → recapitulation, close
```

**Rules that encode the craft:**

- `drone-invariance`: V0 constant single pitch, present in every section, no rests/dynamics.
- `theme-invariance`: V1 note sequence fixed across all sections; the ùrlar IS the piece identity.
- `ornament-mask`: each section selects one ornament formula; V2 notes are gracenotes
  (short, sub-beat, register-neighbouring) attached to V1's notes, never new material.
- `movement-progression`: ornament density monotonically increases ùrlar → siubhal →
  dithis → leumluath → taorluath → crùnluath.
- `singling-doubling`: each movement twice; doubling denser + slightly faster.
- `return-to-ground`: arch form — bare ùrlar recapitulates after crùnluath peak.
- `chanter-scale-constraint`: all V1/V2 pitches from fixed 9-note set (~G-mixolydian);
  no chromatic alteration, no rests.
- `phrase-order-structure`: ùrlar phrase order follows Primary/Secondary/Tertiary/Irregular.
- `continuous-sound`: no silence anywhere; development via ornament density only.
- `canntaireachd-vocable-map`: each ornament movement ↔ chanted vocable sequence.

## 5. Table row added

```
| HC-026 | human (→concrete) | Scottish Pibroch Theme-and-Variation (Ceòl Mór — Ùrlar + Movement Ornamentation) | Scottish Highlands — ceòl mór / piobaireachd of the Great Highland Bagpipe, descending from wire-strung clàrsach harp & fiddle; hereditary dynasties (MacCrimmon, MacArthur), ~16th c.–present; oral via canntaireachd vocables | STRUCTURE, TEXTURE, PITCH, RHYTHM | Learn by ear via canntaireachd (chanted vocables = true notation) → fix drone + 9-note chanter scale (no rests/dynamics) → compose ùrlar ground (Primary AAB ABB AB / Secondary ABCD CBAD CD / Tertiary phrase order) → state ground slow → run movement ladder (siubhal gracenote-before → dithis cut-after → leumluath/taorluath/crùnluath grips, each singling then doubling, faster) → return to ground to close | Voice 0 = drone (fixed A, invariant). Voice 1 = ùrlar theme skeleton (fixed note sequence = piece identity). Voice 2 = ornament layer (movement-specific gracenotes, density ramps). Sections = movement ladder (Ùrlar→Siubhal→Dithis→Leumluath→Taorluath→Crùnluath doubling→return Ùrlar). Rules: drone-invariance, theme-invariance, ornament-mask, monotonic ornament-density ramp, singling-doubling, return-to-ground arch, chanter-scale-constraint (9-note mixolydian, no chromaticism/rests), phrase-order-structure, continuous-sound (no silence — vary by ornament only), canntaireachd-vocable-map | MacCrimmon dynasty (Donald Mor, Patrick Mor), MacArthur dynasty, Angus MacKay (1845), Archibald Campbell (Kilberry 1969), Donald MacLeod / William McCallum / Roderick MacLeod / Allan MacDonald, Cameron & MacPherson lineages, Simon Fraser (Melbourne); titles: Lament for Patrick Og MacCrimmon, Lament for the Harp Tree, Too Long in This Condition, The Big Spree | ✅ Documented |
```

## 6. Verification

- `HC-026` present in detail file `human_method_HC-026_scottish-pibroch-theme-variation.md` ✅
- `HC-026` present in `human_methods_db.md` framework table (exactly 1 row) ✅
- No duplicate HC-026 rows ✅
- Highest existing ID confirmed HC-025 before write; new ID = 026 (max+1) ✅
- **Next free ID: HC-027**

## 7. Quirks / pitfalls

- **No rests, no dynamics.** The pipe physically cannot stop or crescendo. A generator
  that varies by adding silence or velocity swells will not sound like pibroch — vary by
  ornament density and tempo only. Most important encoding constraint.
- **The theme never changes, only its dress.** Contrast with HC-009 motivic development
  (theme transformed): in pibroch the skeleton is frozen, only the gracenote layer mutates.
- **Notation is a flattened shorthand.** MacKay 1845 onward was simplified for competition
  judging; real durations/tempo live in canntaireachd vocables. Encode the vocable→ornament
  map, not the printed notes.
- **Scale is fixed and modal.** 9 notes, mixolydian-flavoured, no chromaticism; harmony is
  the single drone against melody — vertical sonorities incidental, not functional.
- **Arch form, not ladder-only.** Many tunes return to the ground after the crùnluath; a
  generator that only ascends in complexity misses the signature shape.
- **Lineage variance = no single canonical text.** Cameron vs MacPherson styles and the
  Simon Fraser body give divergent settings of the same tune; entry documents craft, not
  one authoritative sequence.

## Source

Wikipedia — "Pibroch" (structure: ùrlar/ground, siubhal, dithis, leumluath, taorluath,
crùnluath; singling/doubling; Primary/Secondary/Tertiary phrase-orderings; canntaireachd
vocable system and Campbell Canntaireachd MSS 1797/1814; notation history MacKay 1845 →
Kilberry 1969 → Piobaireachd Society books; MacCrimmon/MacArthur dynasties; Cameron vs
MacPherson lineages; Roderick Cannon title taxonomy; harp/fiddle precedents and
contemporary revival). Retrieved 2026-09-04.
