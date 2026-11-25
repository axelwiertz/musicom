# REPORT HC-101 — Kazakh Dombra Küy Composition (Programmatic Narrative Instrumental Craft)

**Date:** 2026-11-24 (nightly human-composition-research job)
**Status:** ✅ Documented
**Layer:** `human (→concrete)` — target layer when implemented: **concrete** (the küy's pitched cells, qağys rhythmic stroke patterns, and two-string drone–melody texture become concrete pitch/onset units in the UnitMatrix; the program becomes section labels + a narration voice).

---

## 1. Method name

**Kazakh Dombra Küy Composition** — "Every küy tells a story."

Full title: *Küyshi Composer-Performer Craft: Tökpe vs Shertpe Schools × Sağa-Stream Form × Two-String Drone–Melody Texture × Programmatic Narrative Lock × Oral Transmission.*

## 2. Tradition / culture

Central Asian — Kazakh dombra (dombyra) küy tradition (Turkic steppe, Kazakhstan; sibling kuy traditions on Kyrgyz komuz and Kazakh qobyz/sybyzgy):
- Classical repertoire 18th–19th c. with named küyshi composer-performers; 13th-c. roots (Ketbugha's *Aqsaq Qulan*).
- Two schools: **western tökpe** (both strings, rapid alternate strokes, dramatic/programmatic, strict tone-set order) — Kurmangazy, Dauletkerei, Qazangap, Dina; **eastern/central shertpe** (single-string fingertip plucks, lyrical/rubato) — Tattimbet, Toqa, Dairabai, Sügir.
- Oral transmission, no notation; program narrated verbally before each performance.
- UNESCO ICH Representative List 2014: "Kazakh traditional art of Dombra Kuy" (ref 00996).
- Scholarship: Zataevich, A. Zhubanov, Erzakovich, Aravin, Daukeyeva (*The Music of Central Asia*, Indiana UP 2016).

## 3. The craft procedure (how a human executes it, step by step)

1. **Apprenticeship by ear** — learn dozens–hundreds of kuy from a master; no notation; the instrument is the composition surface (Kurmangazy learned from Soqyr Eszhan, Sherkesh, Bayzhuma; teacher Uzak).
2. **Fix the program** — title/legend/event/portrait/landscape; every kuy is programmatic; the story is spoken before playing (gallop, flood, escape, lament, steppe, woman's portrait).
3. **Set the tuning** — two strings, default perfect fourth D–G; lower = drone, upper = melody; retune to 5th/octave/reverse (Tattimbet's *teris/qosaq* tunings) per kuy; 18–24 frets.
4. **Pick the school** — tökpe (western: both strings together, rapid alternate strokes, "certain sequence of tone sets on the neck", dramatic) vs shertpe (eastern/central: fingertip plucks, lyrical, free form).
5. **Fix the rhythmic cell (qağys)** — jappai/kezek/shertpe/shubyrpaly stroke patterns carry rhythm, dynamics, character ("magic secrets" never notated); meters 2/4, 4/4, 3/4, 3/8, 5/8, 6/8, sometimes changing; **the cell persists unchanged through the whole kuy**.
6. **Compose the melodic streams (sağalar)** — beginning stream states the main motif low over the drone; middle streams develop (sequence, variation, register ascent, parallel 4th/5th/3rd/2nd double stops); **climax in two branches: small sağa then large sağa** (kişi → ülken), the peak (sharyqtau) unfolding the full dombra range; close with return + cadence on the final.
7. **Forms** — single-section to 2–3-part (rarely 3-part) rondo-variational synthetic forms; long kuy reach 150–200 bars (Boğda's *Boz töbesi*, Dina's *Äsem qoñyr*).
8. **Perform, narrate, transmit** — narrate the story, play, transmit orally; performer variants harden into schools (Tattimbet's shertpe school; 1971 Almaty Conservatory shertpe class).

## 4. Practitioner examples (real)

- **Ketbugha (13th c., legendary)** — *Aqsaq Qulan* ("Lame Wild Ass"): Jochi Khan's son killed by a wild ass; the küyshi tells the news in music; molten lead poured into the dombra's soundbox. Archetypal programmatic kuy; gallop rhythm imitates the lame gait.
- **Kurmangazy Sagyrbayuly (1823–1896)** — western tökpe classic, ~60 kuy: *Sary Arqa* ("Golden Steppe"), *Adai*, *Kishkentai*, *Türmeden qashqan*, *Qairan sheshem* (slow → inspired), *Qyz Danaiyn qyrğyny* (hooves/battle/girl), *Kóbik shashqan* (foaming flood). Full-range climax (small + large sağa), locked rhythmic cell.
- **Dauletkerei Shyghaiuly (1820–1887)** — *Zhiger* (Zataevich: "overflowing the narrow throat of the small-sounding dombra"), *Topan*, lament *Salyq ölgen* (1871), portraits (*Qudasha*, *Jumabike*), genre scenes (*Zheldirme*, *Ysqyrma*); met Kurmangazy 1861/69.
- **Tattimbet Qazangapuly (1815–1862)** — shertpe founder (Sary Arka): *Sary Zhailau*, *Kókei Kesti* (two-hand vibration), *Sylqyldaq*, *Qosbasar*, *Bes Töre*; 1855 St. Petersburg coronation performance, silver medal; unusual tunings in duels.
- **Sügir Äliuly (1882–1961)** — Karatau shertpe; master of both schools; *Toğyz Tarau* ("Nine Branches"), *Aqqu*, *Telqoñyr*; qobyz timbre on dombra.
- **Dina Nurpeisova (1861–1955)** — Kurmangazy's heir; *Äsem Qoñyr*, *Bülbül*, *Qaraqasqa At*.
- **Modern** — folk-orchestra arrangements (1930s–), opera/symphony borrowings (Brusilovsky *Qyz Zhibek* uses *Aqsaq Qulan*; Tölebaev; Rakhmediyev), Tattimbet's *Bylqyldaq* in film *Zhambyl*, Sagatov trumpet piece on *Sylqyldaq*, electrodombra (Ulytau, 2010s).

## 5. UnitMatrix mapping (Musicom engine)

The method is instrument-bound craft → the matrix models **the two-string dombra as the voice skeleton** and the sağa-chain as the section architecture.

### Voices (rows)
| Voice | Role | Concrete content |
|---|---|---|
| V0 | Upper-string melody (küy spine) | Pentatonic/mode cells, sağa streams, register waves, climax figures — the composed melody proper. |
| V1 | Lower-string drone/ostinato | Open-string pedal + stopped root/5th; parallel-interval double stops with V0 (4th/5th/3rd/2nd); tokpe both-strings attack. |
| V2 | Qağys stroke/percussion layer | Soundboard taps, body slaps, stroke-pattern punctuation; jappai/kezek/shertpe/shubyrpaly selector. |
| V3 | Program/metadata voice | Title, legend text, spoken narration; section labels; tuning tag (D–G fourth or retuned variant). |
| V4 | Ensemble doubling (optional) | Modern folk-orchestra / qobyz / sybyzgy expansion. |

### Sections (columns)
- **S0_Narration** — verbal program (V3), optional in pure instrumental rendering.
- **S1_Bas** — beginning stream: main motif statement, low register, rhythmic cell established.
- **S2_Orta** — middle streams: sequence, variation, episodic figures, register ascent; optional changing-meter cell.
- **S3_Kishi_Sağa** — small climax branch (first high-register peak).
- **S4_Ulken_Sağa** — large climax branch (true peak: full range unfolded; sharyqtau).
- **S5_Qaytaru_Coda** — return/reprise of the opening figure; cadence on the final.

### Rules (encoding the craft)
1. **Two-string texture lock** — V0 on the upper-string mode/fret map; V1 open drone or stopped root/5th; tokpe double-stop interval set = parallel 4th/5th/3rd/2nd.
2. **Tuning gate** — pitch map from chosen tuning (default perfect fourth D–G; fifth/octave/reverse variants allowed).
3. **School selector (qağys)** — tökpe: both-strings density, dramatic dynamics, strict tone-set order; shertpe: single-string plucks, rubato/free rhythm, lyrical dynamics.
4. **Rhythmic-cell persistence** — one qağys cell per kuy, unchanged across all sections (no per-section groove variation).
5. **Climax architecture** — register ascent through S3 small sağa before S4 large sağa; large sağa uses the widest ambitus cell; peak at the S4/S5 seam.
6. **Program lock** — every kuy requires a title/story tag; contour must satisfy the program's affect (gallop cell, descending sigh for laments, wave-motion for floods).
7. **Meter rule** — duple/triple cells (2/4, 4/4, 3/4, 3/8, 5/8, 6/8), optional changing meters; shertpe allows unmetered recitative-like streams.
8. **Zero-drift** — all units end at section boundaries; terminal landmarks at section length.
9. **Humanization** — finger-pluck micro-timing, body-tap accents, two-hand vibration waves, ornament glides (concrete → absolute).

## 6. Table row added to human_methods_db.md

```
| **HC-101** | human (→concrete) | Kazakh Dombra Küy Composition — Programmatic Narrative Instrumental Craft (Küyshi Composer-Performer Tradition: Tökpe vs Shertpe Schools × Sağa-Stream Form × Two-String Drone–Melody Texture × Qağys Rhythmic Cell × Oral Transmission) | Central Asian — Kazakh dombra (dombyra) küy tradition (Turkic steppe, Kazakhstan; sibling kuy on Kyrgyz komuz, Kazakh qobyz/sybyzgy): classical repertoire 18th–19th c. with named küyshi composer-performers (Kurmangazy, Dauletkerei = western tökpe school; Tattimbet, Toqa, Sügir = eastern/central shertpe school); 13th-c. roots (Ketbugha 'Aqsaq Qulan'); oral transmission, programmatic narrative, verbal story before each performance; UNESCO ICH Representative List 2014 ('Kazakh traditional art of Dombra Kuy'); scholarship Zataevich, A. Zhubanov, Erzakovich, Aravin, Daukeyeva (2016) | PITCH, RHYTHM, STRUCTURE, TEXTURE (HARMONY emergent — two-string drone + parallel 4th/5th/3rd/2nd double stops) | [craft process…] | [UnitMatrix mapping…] | [practitioners…] | ✅ Documented |
```
(Full row appended verbatim in the DB; see §3–§5 for the complete text of the columns.)

## 7. Next free ID

- Highest existing: **HC-100** (transcription-based learning, 2026-11-23).
- New entry: **HC-101** (this report).
- **Next free ID: HC-102.**

## 8. Quirks & pitfalls

- **Oral transmission, no canonical text** — kuy exist in performer variants; the concrete layer fixes one legitimate realization, not "the" correct one. Don't over-normalize.
- **The program is part of the work** — a kuy without its story is half the piece; the narration voice and title tag carry the narrative lock.
- **Rhythm is the identity** — the qağys cell persists unchanged; per-section groove variation (Western habit) destroys the kuy's character.
- **Tökpe tone-set order** — western kuy follow a strict sequence of tone sets on the neck; breaking the order breaks the school's grammar (a mode-order constraint, not free invention).
- **Retuning is a compositional act** — Tattimbet's oblique/reverse tunings are part of the identity; transpose-to-12-keys does NOT apply; kuy are tuning-bound, not key-agnostic.
- **Two-string economy** — the drone is not "accompaniment": melody + drone form one texture (parallel intervals, double stops); splitting them into arranged voices changes the instrument's voice-leading logic.
- **Notation came late** (Soviet era: Zataevich, Zhubanov; Sügir first notated 1968–69) and loses the qağys "magic secrets" — annotate stroke patterns explicitly.
- **Gender history** — professional dombra performance historically predominantly male (patrilineal honor, tribal memory), with notable exceptions (Dina Nurpeisova); cultural context, not a musical rule.
- **Neighbors** — distinct from HC-002 (gamelan kotekan), HC-035 (mbira), HC-025 (kora), HC-091 (Mongolian urtiin duu vocal long-song): HC-101 is the Central Asian instrumental programmatic narrative craft on a two-string drone–melody lute.
