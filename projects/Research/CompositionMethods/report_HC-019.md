# Report — HC-019: Bulgarian Aksak Asymmetric-Meter Horo Construction

**Date:** 2026-08-28 (nightly human-composition research job)
**Method ID:** HC-019
**Next free ID:** HC-020

---

## 1. Method name & tradition

**Bulgarian Aksak Asymmetric-Meter Horo Construction**

**Tradition / Culture:** Bulgarian folk dance music (Thrace / Shop / Macedonia ethnoregions), rooted in Ottoman-Turkish *aksak* ("limping") additive-meter theory. Theoretical grounding: Constantin Brăiloiu, "Le rythme Aksak" (*Revue de Musicologie*, 1951). Related UNESCO element: "Bistritsa Babi, archaic polyphony, dances and rituals from the Shoplouk region" (2008).

**Primary Elements:** RHYTHM, PITCH, STRUCTURE, TEXTURE

**Rationale for selection:** This is a rhythm-led, drone-textured, modal-melodic method from a tradition not yet represented in the DB (no Bulgarian/Balkan/aksak entry exists). It extends the framework's "timeline / cycle-spine" family (HC-005 Ewe, HC-012 Flamenco, HC-018 Son) with a fundamentally new primitive: **unequal beat lengths within the cycle**, where the "slow" (3-unit) beat is a genuinely longer duration, not merely an accented one.

---

## 2. The craft procedure in detail

(Full version in `human_method_HC-019_bulgarian-aksak-meter-horo.md` §2.)

1. **Fix the aksak cycle** — choose the dance/metre type with its canonical long-short grouping: Paidushko (2+3), Račenica (2+2+3), Daichovo (2+2+2+3), Kopanitsa/Gankino (2+2+3+2+2), Elenino (2+2+2+2+2+3), Bučimiš (2+2+2+2+3+2+2), and composite forms (Jove Malaj Mome 18, Sandansko 22, Sedi Donka 25).
2. **Internalize the dance footwork** — the stepping pattern is the composition skeleton; the slow (3) beat carries the dancer's weight.
3. **Fix the modal pitch set** — narrow-range diatonic/modal scale, conjunct motion, no functional harmony.
4. **Lay the drone (ison) + tapan spine** — held tonic+5th drone; tapan drums mark the cycle (boom on long beat, tick on quick beats).
5. **Compose the melody (pesen)** — short strophic modal phrase (1–2 cycles), strongest note on the long beat.
6. **Layer lead instruments** — gaida/kaval/gadulka state the tune; optional heterophonic answer.
7. **Ornament** — trills/mordents/grace clusters at cadential notes and long beats.
8. **Set the form** — strophic: Intro → Strophe → Ritornello → Strophe' → Climax (accelerando) → Close.
9. **Check the accent-lock** — tune's downbeat weight must land on the long beat every cycle; the cycle is never altered to fit a tune.

---

## 3. Real practitioner examples

| Practitioner | Work / Role | Significance |
| :--- | :--- | :--- |
| Béla Bartók | *Mikrokosmos VI*, "Six Dances in Bulgarian Rhythm" (Nos. 148–153) | Abstracted aksak groupings into Western notation; proof the craft transfers across traditions. |
| Filip Kutev | State Ensemble for Folk Songs and Dances | Systematized/harmonized horo repertoire; codified drone+melody+tapan layering. |
| Le Mystère des Voix Bulgares | "Erghen Diado" (Daichovo horo), "Kaval Sviri" | World-facing proof of aksak vocal polyphony with perfect accent-lock. |
| Ivo Papazov-Ibryama | Wedding-music clarinet | Virtuosic improvisation over aksak cycles at extreme tempo. |
| Theodossi Spassov | Kaval | Idiomatic ornamentation layer over drone. |
| Kostadin Varimezov | Gaida (bagpipe) | Simultaneous melody+drone (self-contained aksak voice). |
| Petko Staynov | "Thracian Dances" | Brought aksak into Western art music (parallel to Bartók). |

---

## 4. UnitMatrix mapping (Voices & Sections)

### Musical Elements Framework

- **RHYTHM (primary):** aksak cycle = boolean accent mask over **unequal beat lengths**, encodable as a subdivision-length vector (`[2,2,3]`, `[2,2,2,3]`, `[2,2,3,2,2]`, …). Rules-Based/deterministic layer; invariant.
- **PITCH:** narrow modal pitch-class set + range window + stepwise bias; ornamentation as deterministic decoration rules.
- **HARMONY:** none functional — drone (scale degrees 0 & 7) only; vertical sonorities emergent.
- **STRUCTURE:** strophic (phrase = 1–2 cycles, repeated); Intro → Strophe → Ritornello → Strophe' → Climax → Close.
- **TEXTURE:** stratified drone + ornamented lead + tapan mark; optional heterophonic answer.

### Voices (4-voice matrix)

| Voice | Role | Content | Rules |
| :--- | :--- | :--- | :--- |
| 0 | Tapan (drum) | Cycle mask (boom on long beat, tick on quick) | invariant |
| 1 | Lead melody | Strophic modal phrase, accent on long beats | mode-constrained, conjunct |
| 2 | Heterophonic answer | Doubles/answers lead | never contradicts cycle |
| 3 | Drone + tambura | Held tonic+5th | invariant pedal |

### Sections (5-section matrix)

S0 Intro → S1 Strophe 1 → S2 Ritornello → S3 Strophe 2 (climax/accelerando) → S4 Close (cadence on long beat).

### Encodable rules (summary)

1. `aksak_cycle_invariant` — Voice 0 vector constant, never altered.
2. `long_beat_accent` — melodic onsets/accents target slow (3) beats.
3. `mode_constraint` — modal set + range ≤ octave + stepwise bias.
4. `drone_invariant` — scale degrees 0 & 7 held; no progression.
5. `phrase_cycle_alignment` — phrase length ∈ {1,2} cycles.
6. `ornamentation` — grace/trill/mordent only at cadential notes & long beats.
7. `accelerando_climax` — tempo + ornament density rise into coda.
8. `no_functional_harmony` — vertical sonorities emergent.

---

## 5. Table row added

Appended to the "Human Composition Methods Framework" table in `human_methods_db.md`:

```
| HC-019 | Bulgarian Aksak Asymmetric-Meter Horo Construction | Bulgarian folk dance music (Thrace/Shop/Macedonia) — Ottoman-Turkish aksak additive meter; UNESCO Shoplouk/Bistritsa Babi (2008) | RHYTHM, PITCH, STRUCTURE, TEXTURE | Fix aksak cycle (2+3/2+2+3/2+2+2+3/2+2+3+2+2/…, long=3-unit beat) → internalize dance footwork (slow beat = weight) → fix modal pitch set (narrow, conjunct, no functional harmony) → lay drone (ison) + tapan spine (boom on long beat) → compose strophic modal melody (1–2 cycles, accent on long beat) → layer lead instruments + heterophonic answer → ornament (trills/mordents at cadences) → set strophic form (Intro→Strophe→Ritornello→Strophe'→Climax/accelerando) → check accent-lock | Voice 0 = tapan (cycle mask, boom on long beat). Voice 1 = lead melody (strophic modal phrase). Voice 2 = heterophonic answer. Voice 3 = drone (tonic+5th). Sections = Intro→Strophe→Ritornello→Strophe'→Close. Rules: aksak cycle invariance, long-beat accent, modal constraint, drone invariant, phrase=1–2 cycles, cadential ornamentation, accelerando climax, no functional harmony | Béla Bartók (Mikrokosmos VI "Six Dances in Bulgarian Rhythm"), Filip Kutev (State Ensemble), Le Mystère des Voix Bulgares ("Erghen Diado"), Ivo Papazov-Ibryama, Theodossi Spassov, Petko Staynov ("Thracian Dances") | ✅ Documented |
```

---

## 6. Quirks / pitfalls

- **"Limping" is the point** — aksak is a *regular* cycle of unequal beats, not a dropped-beat error.
- **Grouping order ≠ total** — 7/8 as 2+2+3 (Račenica) is a different dance from 3+2+2 or 2+3+2. The subdivision-length vector is ground truth, not the bare numerator.
- **Never quantize the slow beat away** — rendering 3 as "2+accent" kills the groove; the slow beat must be a genuinely longer duration.
- **Dance fixes the meter** — the composer composes *into* a socially fixed cycle, not a freely chosen meter.
- **No harmony to hide behind** — melody + drone + drum carry 100% of the interest.
- **Engine implication** — the Musicom UnitMatrix needs per-beat subdivision lengths (non-uniform `ticks_per_beat`), since `beats_per_bar` alone cannot express aksak.

---

## 7. Verification

- Detail file: `human_method_HC-019_bulgarian-aksak-meter-horo.md` — contains `HC-019`.
- DB table: `human_methods_db.md` — contains `HC-019`.
- Next free ID: **HC-020**.
