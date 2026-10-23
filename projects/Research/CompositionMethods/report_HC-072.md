# report_HC-072 — Tabla Solo Composition: Gharana Theme-and-Variation Architecture

**Job:** `daily-human-composition-research` · **Date:** 2026-10-22 · **Method ID:** HC-072
**Detail file:** `human_method_HC-072_tabla-solo-gharana-variation-architecture.md`

---

## 1. Header

| Field | Value |
|---|---|
| **Method name** | Tabla Solo Composition — Gharana Theme-and-Variation Architecture (Peshkar → Kayda → Rela → Gat/Tukra, with Tihai & Chakradar Cadence Math) |
| **Tradition** | Hindustani (North Indian) classical percussion — tabla solo. Six gharanas: Delhi (oldest; birthplace of the kayda), Ajrada, Farrukhabad, Lucknow, Benares (Purbi baj), Punjab. 18th c.–present. Oral guru–shishya transmission; **bol** (mnemonic syllables) serve as the notation. |
| **Layer** | `concrete (target when implemented)` — the craft emits stroke-level events per hand per drum straight into UnitMatrix cells. No abstract/theory layer is needed: a matra is a cell, an avartana is a section, a bol is an event with (daya, baya) components. |
| **Primary elements** | RHYTHM, STRUCTURE, TEXTURE, PITCH |
| **Why human craft, not algorithm** | The rule system is a *grammar of prohibitions* ("use only the theme's bols", "keep the stress pattern", "retain the character"). It selects an alphabet; it never generates the sentence. Peshkar deliberately breaks the theme rule. "Character" is an ear judgement the tradition refuses to formalise. Cadence arithmetic is exact, but what fills the arithmetic is free. |

**Distinct from existing HC methods:**
- HC-004 (raga-tala improvisation) — melodic improvisation framed by tala; HC-072 is purely percussive and *composition*-centred (a repertoire plus a variation system, not an improvisation arc).
- HC-017 (Korean sanjo jangdan) — same slow→fast emotional-register ladder idea, different cycle set and a melodic instrument.
- HC-005 (Ewe drumming) — timeline + ensemble call-response with a master drummer; HC-072 is a *solo* form with a fixed variation grammar.
- HC-070 (Carnatic kriti / sangati) — also progressive variation with a fixed landing point, but texted, melodic, strophic.

---

## 2. What the method is

Tabla solo is a **composed repertoire plus a rule-governed variation practice**, not improvised drumming. The player opens with a slow semi-improvised **peshkar**, establishes a **kayda** (or **rela**) theme, generates a chain of variations that must obey the theme's own stroke vocabulary and the tala's stress pattern, and punctuates with cadential forms (**tihai**, **tukra**, **chakradar**, **gat**, **paran**) whose final stroke lands exactly on **sam** (beat 1 of the cycle).

Two axes govern the whole thing:
- **Horizontal — systematic variation:** same bols, new arrangement, developed large unit → small unit.
- **Vertical — laya / layakari:** speed doubling, and subdivision climbing barabar (2:1, 4:1, 8:1) → aralay (3:1, 6:1, 12:1).
- **Cadential axis:** periodically abandon the cycle and drive to sam, then resume.

The name is the thesis: **kayda means "rule" / "system of rules"**. A kayda is simultaneously a composition, a technique exercise, and a method for learning to improvise — DigiTabla calls it classical tabla's greatest pedagogical achievement.

---

## 3. Craft procedure in detail

### Step 0 — Fix the frame
Choose **tala** (tintal 16 = 4+4+4+4 default; jhaptal 10 = 2+3+2+3; rupak 7 = 3+2+2; dhamar 14 = 5+2+3+4), **laya** (vilambit / madhya / drut), **theka** (the bare cycle used as reference), and **gharana idiom** (which forms and bols are native). Tune the dayan (right drum) to Sa.

### Step 1 — Compose the main bol (parent composition)
Write the **fully open** (tali) version first: 2–4 **main phrases**, each 2–8 bols, each making a percussive "statement" that complements the next. The main bol is always made from **at least two main phrases**. Each half must end with a **main-bol ending phrase**:

```
tuna / dhinna
tinna / dhinna
tuna kata / dhinna kata
tinna kata / dhinna kata
tinna kina / dhinna gina        ← the most common Dilli ending
tina taka / dinna taka
tin-na-kitataka / dhin-na-kitataka
```
Every one of these is a **tali–khali counterpart pair**: closed (`tu`, `tin`) for the first half, open (`dhin`) for the second. (Delhi kaydas almost always end `tinna kina / dhinna gina`.)

Beginner example: main bol `dhadha tete | dhadha dhinna` = phrases `dhadha tete` + `dhadha dhinna`.

### Step 2 — Split into tali and khali halves
Generate two versions of each half by changing **only the baya (bass) pattern on the counterpart strokes**. The **dayan (treble) strokes stay byte-identical**.

```
parent : dha dha  te te  dha dha  dhin na
half 1 : dha dha  te te  dha dha  tu   na     (khali — closed bass)
half 2 : ta  ta   te te  dha dha  dhin na     (tali — open bass)
```
Theme = half 1 + half 2. The resulting vibhag stress pattern is **tali–tali–khali–tali**, mirroring tintal's own clap/wave pattern (vibhag 3 is khali — a *timbre* change, not a dynamic one).

### Step 3 — Rules-check the theme
- Length = **16 matras at some laya** (16 at 1x, 8 at 2x, 4 at 4x). There is no "real" length.
- Vibhag 3 contains **no open baya**; vibhags 1, 2, 4 each contain at least one.
- Phrase division may be uneven (3–3–2 is legal) provided the overall stress melody still reads tali-tali-khali-tali.
- Phrase 1 and phrase 2 must contrast in density / register / bol family — not merely transpose.

### Step 4 — Generate variations systematically (largest unit first)
Order (DigiTabla / Chhotelal Misra):
1. **Dohra** ("doubled") — first quarter ×2, then the main bol; second half = khali quarter ×2 + main bol with fully open baya. Doubles the length, preserves the stress pattern.
2. Variations from the **first main phrase** (stress `dhadha`; then stress `tete`; then rearrange so neither dominates).
3. Variations from the **second main phrase** (e.g. `dhadha tuna` ×3; or a fresh `dhate tedha dhinna` cell + the second phrase only).
4. Variations **with gaps** (silence inserted between bols — texture variation, no new vocabulary).
5. **New main bol** — take a sub-phrase that "sounds complete on its own", re-fit it to the cyclic shape (its 3rd quarter becomes khali, the ending-phrase pair restored), then vary *that*.

Five permitted operations on the theme's bols: **repeat · rearrange · substitute (within the set) · invert · add gaps**.
Four standing guidelines: use only theme bols; keep the tali–khali structure; develop systematically; retain the theme's character.

### Step 5 — Climb the layakari ladder
Monotonic, integer-divisible into the matra:
- **barabar lay** — 2:1 (dugun), 4:1 (chaugun), 8:1 (atugun)
- **aralay** — 3:1, 6:1, 12:1 (the "three against four" feel; Ajrada's signature, e.g. peshkars in 3:1 / 6:1)

Never skip a rung on the way up. The climb *is* the form.

### Step 6 — Compose the cadence backward from sam
- **Tihai** — a phrase played three times, with two equal rests (dumdaar) or none (bedum).
  `3p + 2r = 16n` → tintal solutions p=4,r=2 (4-2-4-2-4) and p=2,r=5 (2-5-2-5-2); bedum requires `3p = 16n` (e.g. p=16 → three avartanas). The three statements may start **anywhere** in the cycle — hence the "time distortion, then snap to sam" effect. Jhaptal: 6-1-6-1-6-1 = 21 = 10×2+1.
- **Anagat** — same shape, landing one matra before sam.
- **Chakradar** — a tukra (mukhra + tihai) played **three times**: tintal `3 × (3×7) + 2 = 65 = 64 + 1`, i.e. three palle of 21 matras + 2 rests, last `dha` on sam.
- **Tukra / gat / paran** — fixed cadential pieces (paran often pakhawaj-derived), closing a section abruptly to reset.

### Step 7 — Assemble the solo arc
```
uthan (optional) → peshkar → kayda theme → dohra → phrase-1 variations → phrase-2 variations
  → gaps → new main bol → its variations → rela → its variations
  → gat / tukra / paran → chakradar → final tihai on sam
```
**Peshkar** is the loosest form and the tabla's *alap*: state a theme (or a "blueprint" — it may never be clearly stated at all) → improvise with gaps and off-beat/on-beat stress contrast → use **incomplete tihais** (the final `dha` replaced by the theme's first bol, e.g. `dhi`) → introduce non-theme bols in faster divisions → morph into a related rela or kayda → final tihai. It is simultaneously a warm-up, a technique display and a mood-setter. Benares does not perform peshkar (it uses uthan, theka prakar, fard instead).

**Rela** is the fast sibling: composed to be played fast, phrases smooth and flowing, boundaries interwoven ("an unbroken chain" — Naimpalli), few cadential gaps; typical bols `tirakita`, `ghere naga`, `dheradhera`, `dhina gina`, `dhara gina`.

### Step 8 — Recite, then play
Speak the bols (padhant) before/while playing — the mnemonic *is* the notation and the memory medium. Teachers correct the recitation first, the hands second; the chain is then reproduced from memory at rising speeds. That is the tradition's actual test of a composition.

---

## 4. Practitioner examples

| Player | Gharana | Contribution to the craft |
|---|---|---|
| **Pandit Ram Sahai** (1780–1826) | Benares (founder) | Withdrew six months to redesign fingering (`na` with curved ring finger for maximum dayan resonance), then **composed new forms**: uthan, Benarsi theka, fard, plus gats/tukras/parans. A player composing a *form*, not a piece. |
| **Ustad Ahmedjan Thirakwa** (c. 1892–1976) | Farrukhabad | The modern **peshkar**; credited with the **incomplete tihai**; documented alternation of theme and non-theme bols in 12:1. |
| **Pandit Chhotelal Misra** | Benares | The **"new main bol"** technique — extract a complete-sounding sub-phrase, re-fit it to the cycle, build a new variation family (*Tal Prabandh*, 2006). 1978 BHU solo follows the classical peshkar outline. |
| **Pandit Kishan Maharaj** (1923–2008) | Benares | Cross-rhythm calculation and **tihai/chakradar** architecture in live solo; Taal Vadya Kacheri with mridangam player Palghat R. Raghu. |
| **Ustad Alla Rakha** (1919–2000) / **Ustad Zakir Hussain** (1951–2025) | Punjab | Punjab peshkar + layakari (esp. aralay), pakhawaj-derived relas, globalisation of the solo format; their peshkar layakari now audible in every gharana. |
| **Ustad Mian Shaukat Hussain Khan** (1930–1996) | Punjab | Self-composed **qaydas on the tite-dhete subject**, regarded as the best of their kind; low-tuned bayan worked with the wrist for melodic bass variation. |
| **Ustad Habibuddin Khan** | Ajrada | Ajrada kayda with an **extra third line** in a four-line division; `gheghe tit kit` composites; 3:1 / 6:1 divisions; heavy bayan work (thumb on the bass face). |
| **Anokhelal Mishra, Samta Prasad, Kumar Bose, Anindo Chatterjee (Farrukhabad), Swapan Chaudhuri (Lucknow)** | — | The 20th-c. recital canon in which the peshkar → kayda → rela → cadential arc became fixed repertoire. |

**Documenting scholarship:** Rebecca Stewart, *The Tabla in Perspective* (UCLA diss. 1974) — cyclic vs. cadential classification, peshkar as blueprint; James Kippen, *The Tabla of Lucknow* (1988) — "pseudo-tihai"; Gert-Matthias Wegner, *Vintage Tabla Repertory* (2004) — the Dilli/Farrukhabad peshkar classification problem; Sadanand Naimpalli (2005/2009) — peshkar as "offspring of the theka", rela as "unbroken chain"; Sudhir Kumar Saxena (2006); David R. Courtney, *Focus on the Kaidas of Tabla* (2002); Robert S. Gottlieb (1977, 1993).

---

## 5. UnitMatrix mapping

### Resolution
`ticks_per_beat=480`, `beats_per_bar=4` → bar = 1920 ticks. **1 matra = 1 beat = 480 ticks**. **Tintal avartana = 16 matras = 4 bars = 7680 ticks.** Jhaptal = 10 matras = 4800 ticks (2.5 bars — the cycle, not the bar, must be the section unit).

### Voices & Sections

| Voice | Role | Content |
|---|---|---|
| **V0 — Daya (treble)** | **spine** | Bol stream on the right drum: `dha, dhin, ta/na, tin, tete, tirakita, dhati, dhagina, tinna, kina, tuna, kata`. Carries phrase identity. **Invariant across tali/khali halves** — the structural rule that makes the two halves "the same composition played two ways". |
| **V1 — Baya (bass)** | **form / stress layer** | Open (`ghe`, `ga`) vs. closed (`ka/kat`, or absent). Encodes tali vs. khali. **The form literally lives in this voice** — not in velocities. |
| **V2 — Padhant (recited bol)** | memory / surface layer | The same syllables in a speech-like timbre; doubles V0 at 1:1. Optional but authentic — the medium the composer actually works in. |
| **V3 — Theka** | reference grid | Bare cycle (tintal: `dha dhin dhin dha / dha dhin dhin dha / dha tin tin ta / ta dhin dhin dha`). Muted in true solo; alignment oracle for validation and for accompaniment. |
| **V4 — Sam/tali markers** | colotomic | Clap / wave / sam markers at vibhag boundaries. |
| **V5 — Nagma/lehera** | context (optional) | Harmonium/sarangi melodic loop; gives sam a pitch identity (Sa on beat 1). |

### Sections = one composition unit each
```
S0  Uthan (optional, cadential, ends on sam)
S1  Peshkar theme            (1 avartana, blueprint)
S2  Peshkar improvisation    (n avartanas; incomplete tihais in the last 4 matras)
S3  Kayda theme              (1 avartana; tali/khali split at the half)
S4  Dohra                    (2 avartanas)
S5–S8   phrase-1 variations
S9–S12  phrase-2 variations
S13 Gaps variation
S14 New main bol + its variations
S15 Rela theme + variations  (drut laya, flowing, low contrast)
S16 Gat / Tukra / Paran      (cadential, fixed)
S17 Chakradar                (3 palle: 3 × 21 matras + 2 rests in tintal)
S18 Final tihai              (last stroke on sam; end)
```
**Cells** = one matra (480 ticks), subdivided by bol density (4:1 → 4 events, 12:1 → 12 events per cell). Cell content is a *pair* (daya bol, baya state); compound bols (`dha` = `na`+`ghe`, `dhin` = `tin`+`ghe`) write to V0 and V1 in the same tick window as one logical event. Zero-drift is structural: every section is exactly `k × avartana_ticks` (k ∈ {1/2, 1, 2, 4}); silence is real rests, not padding.

### Rules to encode
1. **Avartana lock** — section length ≡ 0 (mod `avartana_ticks`); nothing straddles sam.
2. **Vibhag stress gate** — tintal: vibhags 1/2/4 ≥ 1 open-baya event, vibhag 3 exactly 0. Generalises via the tala's tali/khali map.
3. **Tali–khali counterpart transform** — `khali(phrase)` replaces designated open strokes with closed ones (`dha→ta`, `dhin→tin`, `dhinna→tuna`, `dha kata→ta kata`), **asserting V0 stroke sequence identical** to the parent.
4. **Main-bol ending whitelist** — each half terminates in a member of the ending-phrase set; first half closed form, second half its open counterpart.
5. **Vocabulary closure (kayda)** — every variation bol ∈ bol-set(theme). **Peshkar exemption:** non-theme bols allowed from the peshkar pool (`tirakita`, `tetegheraidha`, `tet-dhagedha`, `gheranaga`, `dhagina`) and must return within one avartana.
6. **Systematic development order** — no skipped rung: largest phrase → sub-phrase → sub-bol; new main bol re-fitted to rules 2/3/4 before variation.
7. **Layakari ladder** — factor ∈ {2,3,4,6,8,12} per matra, non-decreasing across the chain, each dividing the matra evenly (12:1 over 480 ticks = 40 ticks/bol).
8. **Tihai arithmetic** — `3p + 2r = N × avartana` (dumdaar) or `3p = N × avartana` (bedum); three identical statements; `start_phase` free; final stroke ≡ 0 (mod avartana).
9. **Anagat flag** — land at `avartana − matra`; next section resolves on sam.
10. **Chakradar** — `3 × (mukhra + tihai)`, each palle internally terminated; total ≡ 0 (mod avartana).
11. **Peshkar rules** — theme may be stated once or never; incomplete tihai allowed; bol pool may widen mid-section; must hand off to a rela/kayda cell, not close.
12. **Rela profile** — flowing composites, interwoven phrase boundaries, tempo ≥ 2× the kayda's, low contrast.
13. **Tempo map** — non-decreasing; doubling only at section seams (never mid-avartana).
14. **Sam convergence** — cadential sections end on sam (or the anagat offset); coda's final stroke is an open `dha` on sam.
15. **Validate** — `composer.validate()` → True per section; equal-length rows, terminal landmarks at section length.

### Schematic (invented illustration, not a transcription)
Tintal, matra = 480 ticks, avartana = 7680 ticks.

| Section | Matras | V0 daya | V1 baya | Stress |
|---|---|---|---|---|
| S3 theme 1–4 | 4 | dha dha · te te | open open · – – | tali |
| S3 theme 5–8 | 4 | dha dha · dhin na | open open · open – | tali |
| S3 theme 9–12 | 4 | ta ta · te te | – – · – – | **khali** |
| S3 theme 13–16 | 4 | dha dha · dhin na | open open · open – | tali |
| S18 tihai p=4, r=2 | 16 | X X X X ·· X X X X ·· X X X X | open throughout | lands on sam |

---

## 6. Table row added to `human_methods_db.md`

Appended verbatim (9 columns, matching the existing table):

```
| HC-072 | human (→concrete) | Tabla Solo Composition — Gharana Theme-and-Variation Architecture (Peshkar → Kayda → Rela → Gat/Tukra with Tihai & Chakradar Cadence Math) | Hindustani (North Indian) classical tabla solo — six gharanas (Delhi, Ajrada, Farrukhabad, Lucknow, Benares/Purbi, Punjab), 18th c.–present; oral guru–shishya transmission with bol mnemonics as the notation | RHYTHM, STRUCTURE, TEXTURE, PITCH | Fix frame (tala + vibhag tali/khali map, laya, theka, gharana idiom) → compose the main bol / parent composition (2–4 main phrases, each half ending in a main-bol ending phrase: tuna/dhinna, tinna/dhinna, tuna kata/dhinna kata, tinna kina/dhinna gina) → split into tali + khali halves by changing ONLY the baya stroke on counterpart bols (dayan strokes identical) → check the vibhag stress pattern tali-tali-khali-tali and that the theme is 16 matras AT SOME LAYA (16 at 1x, 8 at 2x, 4 at 4x) → generate variations systematically, largest unit first (dohra = first quarter ×2 + main bol → first-phrase variations → second-phrase variations → gap variations → new main bol from a sub-phrase), using only repeat / rearrange / substitute / invert / add-gaps on the theme's bols → climb the layakari ladder monotonically: barabar (2:1, 4:1, 8:1) → aralay (3:1, 6:1, 12:1) → compose the cadence backward from sam: tihai (3p+2r = 16n dumdaar; 3p = 16n bedum; start phase free, e.g. 4-2-4-2-4 or 2-5-2-5-2), anagat (same shape landing one matra early), chakradar (3 × (mukhra + tihai), tintal 3×21+2 = 65 = 64+1) → assemble the solo arc: uthan → peshkar (blueprint not theme, non-theme bols allowed, incomplete tihai where the final dha is replaced by the theme's first bol) → kayda → rela (flowing unbroken chain, no cadential gaps) → gat/tukra/paran → final tihai on sam → recite the bols aloud (padhant) and only then play the chain from memory, doubling laya at section seams | V0 = Daya treble bol stream (spine: the phrase identity; strokes invariant between tali and khali halves). V1 = Baya open/closed strokes (form layer: open = tali, closed = khali — the stress/form is literally in this voice, not in velocity). V2 = Padhant recited bol (memory/surface layer, speech-like timbre, doubles V0 1:1). V3 = Theka reference grid (alignment oracle; muted in true solo). V4 = Sam/tali markers (colotomic, one event per vibhag). V5 = Nagma/lehera pitch bed (optional, Sa on sam). Sections = one composition unit each: S0 Uthan → S1 Peshkar theme → S2 Peshkar improvisation → S3 Kayda theme → S4 Dohra → S5–S8 phrase-1 variations → S9–S12 phrase-2 variations → S13 gap variations → S14 new main bol + its variations → S15 rela theme + variations → S16 gat/tukra/paran → S17 chakradar → S18 final tihai. Cells = one matra (480 ticks at 4/4); tintal avartana = 16 matras = 4 bars = 7680 ticks; cells subdivide by bol density (4:1 = 4 events, 12:1 = 12 events per matra). Rules: avartana lock (section length ≡ 0 mod avartana_ticks), vibhag stress gate (tintal vibhag 3 = zero open-baya events; vibhags 1, 2, 4 ≥ 1), tali-khali counterpart transform (dha→ta, dhin→tin, dhinna→tuna with V0 asserted identical), main-bol ending-phrase whitelist (closed form on the first half, its open counterpart on the second), kayda vocabulary closure + explicit peshkar exemption, systematic development order with no skipped rung, layakari ladder monotonic over {2,3,4,6,8,12} dividing the matra evenly, tihai/anagat/chakradar arithmetic gates, sam convergence (cadential final stroke ≡ 0 mod avartana), tempo doubling only at section seams, zero-drift validate per section | Pandit Ram Sahai (Benares founder, 1780–1826: six months' seclusion to redesign fingering — na with curved ring finger — then composed new forms uthan, Benarsi theka, fard, plus gats/tukras/parans), Ustad Ahmedjan Thirakwa (Farrukhabad peshkar; credited with the incomplete tihai; theme ↔ non-theme bols in 12:1), Pandit Chhotelal Misra (new main bol technique; Tal Prabandh 2006; 1978 BHU peshkar solo following the classical outline), Pandit Kishan Maharaj (tihai and chakradar calculation in live solo; Taal Vadya Kacheri with Palghat R. Raghu), Ustad Alla Rakha & Ustad Zakir Hussain (Punjab peshkar layakari, pakhawaj-derived relas, globalised solo format), Ustad Mian Shaukat Hussain Khan (self-composed tite-dhete qaydas, low-tuned wrist-worked bayan), Ustad Habibuddin Khan (Ajrada: gheghe tit kit composites, 3:1/6:1 divisions, extra third line, bayan work), Anokhelal Mishra, Samta Prasad, Anindo Chatterjee, Swapan Chaudhuri; scholars Rebecca Stewart (The Tabla in Perspective 1974, cyclic vs cadential), James Kippen (The Tabla of Lucknow 1988, pseudo-tihai), Gert-Matthias Wegner (Vintage Tabla Repertory 2004), Sadanand Naimpalli (2005/2009), Sudhir Kumar Saxena (2006), David R. Courtney (2002), Robert S. Gottlieb (1977/1993) | ✅ Documented |
```

---

## 7. Verification

| Check | Result |
|---|---|
| `grep -c 'HC-072' human_methods_db.md` | 1 (single row, no duplicate) |
| `grep -c 'HC-072' human_method_HC-072_*.md` | 5 (header, title, registry block) |
| Table columns in new row vs. header | 9 vs. 9 (field count 11 with leading/trailing pipes) → aligned |
| Total `HC-NNN` rows in table after append | 72 (001–072, no gaps, no duplicates) |
| Highest existing ID before this run | HC-071 |
| **Next free ID** | **HC-073** |

---

## 8. Quirks and pitfalls (implementation warnings)

1. **Matra ≠ bar.** Tintal tiles 4/4 bars; jhaptal (10) and rupak (7) do not. Model the **cycle** as the section unit and derive bars, or sam drifts every avartana.
2. **The stress pattern lives in the bass voice, not in accents.** Khali is a *timbre* (closed/damped bass), not a dynamic. A velocity-based model will not reproduce the form.
3. **Tali–khali is a substitution, not a transpose.** Dayan strokes identical; only designated baya strokes flip. If the dayan stream differs, it is a different composition.
4. **"16 matras" is laya-relative.** Store `(bols, laya)` and derive matras; a validator demanding exactly 16 rejects correct performances.
5. **Tihai rests must be equal.** Unequal rests make a different figure; a tihai landing one matra early is an **anagat** — flag, don't "fix".
6. **Chakradar nests two levels of three.** `3 × (mukhra + 3p)`; conflating the inner and outer triple gives 9 or 27 statements and a missed sam. Sum-check every palle (tintal: 3×21+2 = 65 = 64+1).
7. **Compound bols are single events with two hands.** `dha` = `na`+`ghe`, `dhin` = `tin`+`ghe`. Splitting them breaks the tali/khali transform (the dayan half must stay put while the bass half flips).
8. **Gharana definitions conflict.** The same Thirakwa peshkar is called "Farrukhabad" by Wegner (2004) and "Dilli" by Stewart (1974). Store gharana as a *style prior* over bol choice and division preference — never a hard gharana→form table.
9. **Benares has 20+ forms and no peshkar.** A generic solo-arc preset misrepresents Benares (uthan + theka prakar + fard) and Punjab (rela-dominant, pakhawaj-derived parans).
10. **Peshkar's rule violation is the point.** Enforcing kayda vocabulary closure on peshkar destroys the form; it needs its own looser validator.
11. **Padhant is not decoration.** Recitation is how the material is composed, checked and memorised; a system that only emits MIDI loses the actual human workflow. Keep V2 first-class.
12. **Cadential forms are fixed repertoire.** Tukra, gat, paran and traditional chakradar are composed pieces owned by a lineage — library assets with provenance, not rule output.
13. **Tempo changes must land on section seams.** A doubling inside an avartana breaks the sam grid; the ladder is stepped, never continuous within a cycle.

---

## 9. Sources (accessed 2026-10-22)

- **DigiTabla.com** reference — *Compositional Forms Overview*, *Kayda*, *The Structure of Kaydas*, *Kayda Phrases*, *Kayda Variations 1–2*, *Peshkar*, *Rela*, *Tihai*, *Chakradar*, *Gat*, *Tukra*, *Uthan*. Primary technical source for: parallel halves and tali–khali counterparts; tali-tali-khali-tali vibhag stress rule; main-bol ending-phrase set; systematic variation guidelines + five operations; "new main bol"; peshkar outline, incomplete tihai, barabar→aralay progression; rela's "unbroken chain" profile.
- **Wikipedia** — *Tabla* (kayda structure: mukh, dohara, adha dohara, vishram, adha vishram, palta, tihai; bol tables; tala/vibhag/tali/khali/sam; gharana list), *Tihai* (dumdaar/bedumdaar, anagat, 4-2-4-2-4 and 2-5-2-5-2 in tintal, 6-1 in jhaptal, chakradar 3×(7×3)+2 = 65 = 64+1), *Benares gharana* (Ram Sahai, uthan/fard/Benarsi theka, `na` fingering, 20+ forms), *Ajrada gharana* (3:1/6:1, `gheghe tit kit`, extra third line, bayan work), *Punjab gharana* (pakhawaj influence, Shaukat Hussain's tite-dhete qaydas, Alla Rakha, Zakir Hussain), *Lucknow gharana*, *Pakhawaj* (paran/rela ancestry, padhant vs. konnakol).
- Rebecca Marie Stewart, *The Tabla in Perspective* (Ph.D. diss., UCLA, 1974).
- James Kippen, *The Tabla of Lucknow: A Cultural Analysis of a Musical Tradition* (Cambridge UP, 1988).
- Gert-Matthias Wegner, *Vintage Tabla Repertory* (Munshiram Manoharlal, 2004).
- Chhote Lal Misra, *Tal Prabandh* (Kanishka, 2006); *Tal Prasoon* (2004).
- Sadanand Naimpalli, *Theory and Practice of Tabla* (2005); *Tabla for Advanced Students* (2009).
- Sudhir Kumar Saxena, *The Art of Tabla Rhythm* (2006); David R. Courtney, *Focus on the Kaidas of Tabla* (2002); Robert S. Gottlieb, *The Major Traditions of North Indian Tabla Drumming* (1977), *Solo Tabla Drumming of North India* (1993).
- **Source-quality note:** DigiTabla is a scholarly, practitioner-run reference and the most detailed public description of the variation system; Wikipedia supplies repertoire/lineage facts and the tihai arithmetic examples. The step sequence in §3 is my synthesis across these, not a quotation from any single text.

---

## 10. Registry status

- Detail file: `human_method_HC-072_tabla-solo-gharana-variation-architecture.md`
- DB row: appended to the **Human Composition Methods Framework** table in `human_methods_db.md` (row count 72, columns aligned)
- Report: `report_HC-072.md` (this file — primary record)
- **Next free ID: HC-073**
