# Report — HC-036: Norwegian Hardanger Fiddle Slått Craft (Scordatura Tuning + Asymmetrical Dance-Meter Variation)

**Date:** 2026-09-14 (nightly `daily-human-composition-research`)
**Method ID:** HC-036
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Tradition:** Norwegian bygdedans village-dance folk — Telemark / Valdres / Hallingdal / Setesdal, played on the hardanger fiddle (hardingfele), 1651–present; oral slått transmission
**Primary Elements:** PITCH, RHYTHM, TEXTURE, STRUCTURE
**Status:** ✅ Documented

---

## 1. Method name & one-line definition

**Norwegian Hardanger Fiddle Slått Craft** — composition-for-tuning: a slått
(Norwegian folk tune) is written for, and inseparable from, a specific
scordatura (non-standard string tuning) which re-maps the fingerboard,
selects the drone (bordun), and — uniquely — **tunes the sympathetic
understrings that give the tune its resonant halo**. Rhythm is a dance
physics problem: the springar's three beats are *unequal*, and the fiddler's
variations track the dancers' phases, not abstract form.

---

## 2. The craft procedure (how a human does it, step by step)

1. **Choose the scordatura for the tune.** Piece and tuning are one
   decision. Standard: **A–D–A–E** (written; the instrument is a D
   transposing instrument). Understrings are retuned to match — e.g.
   **B–D–E–F♯–A** under A–D–A–E — so the resonance box is built for exactly
   this tune. Named tunings bind to tune families: **troll tuning
   A–E–A–C♯** for the *fanitullen* devil's tunes + *Kivlemøyane* suite;
   **gorrlaus** (F-string) in some regions; **E-scale** (B–E–B–F♯, Annbjørg
   Lien); **F-scale** (C–F–C–G, Knut Buen); low bass (G–D–A–E). 20+
   recorded tunings. In Valdres, ending a night in troll tuning was called
   **"greylighting"** — he'd played through his tunings until morning.
2. **Re-learn the fingerboard.** Every scordatura moves the positions; the
   fiddler re-maps hand shapes per tuning. This is why one tuning = one
   repertoire family.
3. **Learn the slått orally** from a master — phrase by phrase, sung first,
   then bowed. Notation (when used) is a memory aid. Tunes carry names,
   owners, stories (*Fanitullen* = learned from the devil under the inn
   table).
4. **Assemble the tune from gang/motif stock.** A slått is built from a
   shared regional vocabulary of short stereotypic melodic formulas —
   composition = selection + order + ornament, not free invention.
5. **Set the dance meter.**
   - **Springar**: 3/4 with *unequal beats* — Telemark longer–long–short,
     Valdres short–longer–long; beat 1 carries the dancers' weight.
   - **Gangar**: walking dance, 2/4 or 3/8; stately.
   - **Halling**: fast 2/4 or 6/8 (95–106 bpm), sharp pulse for solo
     acrobatics (nakkespretten, hodestift, the **kast** hat-kick at
     230–280 cm).
6. **Bow the double-stop composite.** The flat, wide bridge keeps the top
   strings nearly level → the normal texture is **two (sometimes three)
   strings at once**: melody on top, **bordun drone** (open tonic/fifth)
   underneath. The drone is half the melody's body, not accompaniment.
   Bowing is light and bouncy (baroque-weight bow; slimmer strings).
7. **Let the sympathetic strings ring.** The 4–5 understrings run through a
   hollow fingerboard under the bridge and resonate with every bowed note.
   The fiddler *chooses voicings so the resonance blooms*. Grieg lifted the
   understring scale **A–F♯–E–D–E–F♯** directly into "Morning" (*Peer
   Gynt*).
8. **Lay the foot-stomp grid (trapping).** For dance slått the fiddler or
   dancers stamp the weight beat — the percussive floor of the tune.
9. **Vary strophe-by-strophe across the dance phases.** First pass plain,
   then increasingly ornamented; variation intensifies with the dance:
   **figuring part → lausdans (free dancing) → samdans (closed hold)**.
   Halling variations build toward the **kast** — the music peaks exactly
   when the hat falls.
10. **Close with a vurving (turn figure).** Cadential twist that either
    re-launches the dance cycle or, for a **bruremarsj** wedding tune, ends
    the procession at the church door (playing inside was traditionally
    forbidden).

---

## 3. Practitioner examples (real humans)

- **Torkjell Haugerud** (Telemark 1876–1954) — canonical springar/gangar
  source recordings; benchmark of the Bø style.
- **Knut Buen** — whole albums in raised F-scale tuning (C–F–C–G); master of
  regional slått dialects. **Hauk Buen** — Telemark tradition bearer.
- **Leif Rygg** — Voss hardanger lineage.
- **Johannes Dahle** (Tinn) — first to play hardanger fiddle inside a church
  (1920s), breaking the centuries-old ban.
- **Knut Hamre & Benedicte Maurseth** — *Rosa i Botnen*: the oldest playable
  hardanger fiddles with Norway's oldest playable church organ.
- **Edvard Grieg** — *Slåtter* Op. 72 (17 peasant dances, written down via
  **Johan Halvorsen**'s arrangement); "Morning" opening derived from the
  understring tuning A–F♯–E–D–E–F♯; *Peer Gynt* no. 2 fiddle music.
- **Arne Bjørndal & Eivind Groven** — collectors/systematizers; Groven built
  his just-intonation (renstemt) organ to render slått microtonality.
- **Annbjørg Lien** — E-scale tunings, crossover work with organist Iver
  Kleive. **Nils Økland / Erlend Apneseth** — contemporary/experimental
  hardanger voices.
- **Liza Lim** — *Philtre* (1997), solo hardanger commission; *Winding
  Bodies: 3 Knots* (2013–14); *The Weaver's Knot* quartet inspired by it.
- Canonical tunes: *Fanitullen* (devil's tune, troll tuning), *Kivlemøyane*
  suite (hulder association), *Fykerudens gångar/springar*, Valdres
  hallingar, bruremarsj repertoire.

---

## 4. UnitMatrix mapping (Musicom engine)

### Voices & Sections

| Voice | Role | Content | Invariance |
|---|---|---|---|
| Voice 0 | **melody double-stop lead** | top-string melody built from gang/motif stock; ornaments accrue per pass | gang formula identity, fixed per slått |
| Voice 1 | **bordun/drone partner** | lower double-stop voice (open-string tonic/5th pedal under the melody) | drone-locked to the tuning's open strings |
| Voice 2 | **sympathetic understrings** | sustained ghost layer ⊂ understring pitch set of the active scordatura; rings with, never doubles, the melody | subset of tuning set, low velocity |
| Voice 3 | **foot-stomp (trapping)** | dance weight on beat 1 (springar), drive pulse in halling | continuous, invariant |

**Sections** = dance phases, not abstract blocks:
- Springar/gangar: **Figuring → Lausdans → Samdans** per dance cycle.
- Halling: **build → Kast climax → close**.
- Bridal context: **Bruremarsj processional → stop at church door**.

Ornament/variation index rises with each section (plain → ornamented →
drive). For the engine: one section per dance phase; equal-length rows;
zero-drift padding at section end (terminal landmark at `section_len`).

### Rules to encode

- **Scordatura-per-tune lock** — one tuning per piece; melody + drone +
  sympathetic layer all derive from that tuning's pitch set (understrings
  ⊂ tuned resonance set; e.g. A–D–A–E ↔ B–D–E–F♯–A).
- **Unequal-beat grid** — springar 3/4 realized with explicit beat
  tick-lengths (Telemark longer–long–short; Valdres short–longer–long);
  never uniform 3/4 quantization. At 480 tpq: e.g. Telemark springar ≈
  {960, 600, 300} or another ratio-tuned set; encode as a beat-template,
  not a tempo.
- **Double-stop composite bias** — Voices 0+1 sound together by default; a
  monophonic render is a degraded case, not the target.
- **Sympathetic-set constraint** — Voice 2 pitches must lie in the
  understring set of the active tuning; onsets ride melody events, velocity
  low (ring, not line).
- **Motif-stock composition** — melodic material assembled from a finite
  formula vocabulary + sequence/ornament operators; no freely invented
  material (variation-not-invention).
- **Dance-phase form** — section order and variation intensity track
  figuring → lausdans → samdans; halling peaks at kast.
- **Foot-stomp invariance** — weight beat never disappears while dancing.
- **Cadential vurving** — section closes with the turn figure; re-launch
  (dance continues) or stop (processional ends at the door).
- **Range constraint** — 4 bowed strings, melody on top two; ~1.5-octave
  typical melodic range.
- **HARMONY** emergent only — drone + melody imply open I/5 sonorities; no
  functional progression.

### Element mapping

**PITCH** (scordatura pitch set + drone/sympathetic derivation, primary),
**RHYTHM** (unequal dance-beat grids + halling drive + stomp weight,
primary), **TEXTURE** (double-stop composite + sympathetic ring, primary),
**STRUCTURE** (dance-phase form + variation passes, secondary).

---

## 5. Table row added (human_methods_db.md)

```
| HC-036 | human (→concrete) | Norwegian Hardanger Fiddle Slått Craft (Scordatura Tuning + Asymmetrical Dance-Meter Variation) | Norwegian bygdedans folk — Telemark/Valdres/Hallingdal/Setesdal on the hardanger fiddle (hardingfele), 1651–present; oral slått transmission; UNESCO-listed tradition | PITCH, RHYTHM, TEXTURE, STRUCTURE | Choose scordatura for the tune (20+ tunings: A–D–A–E standard + understrings B–D–E–F♯–A; troll A–E–A–C♯ = fanitullen/Kivlemøyane; gorrlaus; E/F-scale raised tunings) → re-learn fingerboard per tuning → learn slått orally from master (named tunes, lineage "dialect") → assemble tune from shared gang/motif stock (selection + order + ornament, not invention) → set dance meter (springar 3/4 unequal beats: Telemark longer–long–short, Valdres short–longer–long; gangar 2/4 or 3/8; halling fast 2/4·6/8 95–106 bpm) → bow flat-bridge double-stop composite (melody + bordun drone always together) → let sympathetic understrings ring (choose voicings so resonance blooms; Grieg lifted A–F♯–E–D–E–F♯ into "Morning") → lay foot-stomp weight beat → vary per dance phase (figuring → lausdans → samdans; halling peaks at kast hat-kick) → close with vurving turn (re-launch or bruremarsj stop at church door) | Voice 0 = melody double-stop lead (top strings, gang/motif stock). Voice 1 = bordun/drone partner (open-string tonic/5th under melody, tuning-locked). Voice 2 = sympathetic understrings (sustained ghost layer ⊂ understring set of active tuning, low velocity, rings with melody). Voice 3 = foot-stomp trapping (dance weight beat 1, invariant). Sections = dance phases (Figuring→Lausdans→Samdans; Halling build→Kast climax; Bruremarsj→stop at church door), ornament/variation index rises per section. Rules: scordatura-per-tune lock, unequal-beat grid (explicit tick spans, never uniform 3/4), double-stop composite bias, sympathetic-set constraint (Voice 2 ⊂ understring set), motif-stock composition (finite formula vocabulary), dance-phase form, stomp invariance, vurving cadence, ~1.5-octave range on top two strings | Torkjell Haugerud (Telemark springar/gangar source), Knut Buen (F-scale albums), Hauk Buen, Johannes Dahle (first church performance 1920s), Knut Hamre & Benedicte Maurseth (Rosa i Botnen), Edvard Grieg (Slåtter Op. 72; "Morning" Peer Gynt from understring tuning), Johan Halvorsen, Arne Bjørndal & Eivind Groven (just-intonation systematizers), Annbjørg Lien (E-scale), Nils Økland, Erlend Apneseth, Liza Lim (Philtre 1997); tunes: Fanitullen, Kivlemøyane, Fykerudens gångar, bruremarsj repertoire | ✅ Documented |
```

---

## 6. Verification

- Detail file: `human_method_HC-036_hardanger-fiddle-slatt.md` — 2 × `HC-036` hits (title + ID line).
- Table: `human_methods_db.md` — 36 HC rows, `HC-036` present, all rows well-formed (9 columns), file ends with newline.
- **Next free ID: HC-037.**

---

## 7. Quirks / pitfalls

- **Uniform 3/4 kills the springar** — the genre's core information is beat
  asymmetry; encode beat lengths as explicit tick spans, not a global tempo.
- **Tuning is the piece, not a knob** — wrong scordatura changes fingerings,
  drones AND the sympathetic bloom; treat tuning as an immutable
  piece-level parameter (Valdres "greylighting" shows how strongly tunings
  structure a whole playing night).
- **Transposing instrument** — written C sounds D; store absolute concert
  pitches in the engine, keep the scordatura as a named preset, never
  hand-shift by ear.
- **Sympathetic layer is a ghost, not a voice** — if Voice 2 reads as a
  played line, the render is wrong: low velocity, sustained, subset of
  understrings only.
- **Double-stops are the default** — single-line-only output loses the
  bordun, which is half the instrument's identity (the flat bridge exists
  for this).
- **Motif stock ≠ laziness** — slått composition is selection and order from
  a shared formula vocabulary; "inventing" novel themes per generation is
  off-craft. Constrain the pitch/rhythm generator to the stock.
- **Dance function gates form** — halling peaks at the kast, springar tracks
  lausdans/samdans, bruremarsj stops at the church door; use the dance's
  social script, not abstract ABA.

---

## 8. Sources

- Wikipedia: *Hardanger fiddle* — instrument history (Jaastad 1651), 8–9
  strings / understrings, D transposition, 20+ tunings incl. troll/gorrlaus/
  E-scale/F-scale, understring sets per tuning, flat-bridge double-stop
  technique, church ban + Johannes Dahle, Grieg "Morning" derivation
  (A–F♯–E–D–E–F♯), Liza Lim *Philtre*.
- Wikipedia: *Bygdedans* — gangar/springar definitions, regional unequal
  pulses (Telemark longer–long–short, Valdres short–longer–long), three-part
  dance sequence (figuring / lausdans / samdans), gangar survival only in
  Telemark/Setesdal, rull/rudl in the west.
- Wikipedia: *Halling (dance)* — 2/4·6/8, 95–106 bpm, solo laus character,
  kast hat-kick 230–280 cm, nakkespretten/hodestift, Olav Thorshaug.
- Wikipedia: *Springar* — uneven 3/4 couple dance.
- Context: Grieg *Slåtter* Op. 72 / Halvorsen; Eivind Groven just-intonation
  organ; practitioner canon (Buen brothers, Haugerud, Rygg, Økland,
  Apneseth).
