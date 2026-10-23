# HC-072 — Tabla Solo Composition: Gharana Theme-and-Variation Architecture (Peshkar → Kayda → Rela → Gat/Tukra, with Tihai & Chakradar Cadence Math)

**Method ID:** HC-072
**Layer:** `concrete (target when implemented)` — the craft emits stroke-level events (bol stream per hand, per drum) directly into UnitMatrix cells; each cell is one matra or one bol phrase, each section is one avartana (cycle) or one composition. No abstract layer is required between the human procedure and the grid.
**Tradition:** Hindustani (North Indian) classical percussion — tabla solo, 18th c.–present. Six canonical gharanas: Delhi (oldest, birthplace of the kayda), Ajrada, Farrukhabad, Lucknow, Benares (Purbi baj), Punjab. Oral transmission, guru–shishya, no primary notation (bol = mnemonic syllable = the notation).
**Primary elements:** RHYTHM, STRUCTURE, TEXTURE, PITCH.
**Related but distinct methods:** HC-004 (raga-tala improvisation — *melodic* improvisation framed by a tala; HC-072 is purely percussive and *composition*-centred), HC-017 (Korean sanjo jangdan — analogous slow→fast cycle ladder, but melodic instrument and different cycle set), HC-005 (Ewe drumming — timeline + call-response ensemble; HC-072 is a *solo* form with a written-in-stone variation system), HC-070 (Carnatic kriti sangati — also a progressive-variation architecture, but texted/melodic and strophic). HC-072 is the canonical **percussion composition-as-rule-system** craft: the qayda literally means "rule".

---

## 1. What the method is

Tabla solo is not "improvising a drum part". It is a **composed repertoire plus a rule-governed variation practice**. The player opens with a slow, semi-improvised *peshkar*, establishes a *kayda* (or *rela*) theme, then generates a chain of variations that must obey the theme's own stroke vocabulary and the tala's stress pattern, and punctuates the whole with cadential forms (*tihai*, *tukra*, *chakradar*, *gat*, *paran*) whose last stroke lands exactly on *sam* (beat 1 of the cycle).

Two things make this a genuine **human composition method** and not a rhythmic randomizer:

1. **The theme is a generative grammar.** A kayda theme is 16 matras (in tintal) built from 2–4 "main phrases" made of 3–5 bols. Variations may use *only* the bols of the theme (the classic rule), must keep the theme's **tali/khali stress pattern** (stressed-stressed-unstressed-stressed, produced by open vs. closed bass-drum strokes), and must retain the theme's "character" — a deliberately subjective criterion the tradition insists on.
2. **Every phrase is measured backward from a landing point.** Cadences are *composed to fit*: a tihai is a phrase played three times so that the final stroke falls on sam. The arithmetic is done by the player, in the head, in performance tempo.

The whole solo is therefore a **two-axis system**: a horizontal axis of *systematic variation* (same bols, new arrangement) and a vertical axis of *speed* (barabar 2:1/4:1/8:1 → aralay 3:1/6:1/12:1), with a cadential axis that periodically abandons the cycle and drives to sam.

---

## 2. Why this is not an algorithm

- **The rule is a prohibition, not a generator.** "Use only the theme's bols" tells you the alphabet, never the sentence. Two players from the same gharana produce different, equally correct variation chains.
- **Gharana is a style prior, not a grammar.** Delhi, Ajrada, Farrukhabad, Lucknow, Benares and Punjab share the kayda skeleton but differ in bol preference, bayan (bass) usage, phrase division, and which forms they cultivate. The tradition itself acknowledges definitions are inconsistent across lineages (DigiTabla's own caution; Kippen 1988).
- **Peshkar deliberately violates the theme rule.** It is a "blueprint" (Stewart 1974) rather than a theme — non-theme bols are introduced freely, and the theme may never be clearly stated at all.
- **"Character" is an ear judgment.** Variations must "sound right" for that kayda; this is not encodable as a constraint set, only as a similarity bias.
- **Cadence arithmetic is exact but the phrase inside it is free.** The tihai sum fixes *how many matras*, nothing about which bols fill them.
- **Speed is expressive, not notational.** A kayda "is 16 matras at some speed" — the same composition is 16, 8, or 4 matras long depending on laya. The notation is relative to the cycle, not absolute.

---

## 3. The craft procedure, step by step

### Step 0 — Fix the frame
Choose **tala** (tintal 16 = 4+4+4+4 is the default; jhaptal 10 = 2+3+2+3; rupak 7 = 3+2+2; dhamar 14 = 5+2+3+4; ada-chautal 14), **laya** (vilambit / madhya / drut), **theka** (the bare cycle pattern that will be the reference), and **gharana idiom** (which forms and bols are native to the lineage). Tune the dayan to Sa.

### Step 1 — Compose the **main bol** (parent composition)
Write the *fully open* (tali) version first: 2–4 **main phrases**, each 2–8 bols, each phrase making a percussive "statement" and complementing the next. Every kayda main bol ends its half with a **main-bol ending phrase** — `tuna/dhinna`, `tinna/dhinna`, `tuna kata/dhinna kata`, `tinna kina/dhinna gina`, `tina taka/dinna taka`, `tin-na-kitataka/dhin-na-kitataka`. These are *tali–khali counterpart pairs*: closed (`tu/tin`) for the first half, open (`dhin`) for the second.

Example (beginner kayda): main bol `dhadha tete | dhadha dhinna`, two main phrases `dhadha tete` + `dhadha dhinna`.

### Step 2 — Split into **tali and khali halves** (the parallel-halves rule)
Take the parent and generate two versions of each half by changing **only the baya (bass) pattern on the counterpart strokes**; the **dayan (treble) strokes stay identical**.

```
parent : dha dha  te te  dha dha  dhin na
half 1 : dha dha  te te  dha dha  tu   na      (khali — closed bass)
half 2 : ta  ta   te te  dha dha  dhin na      (tali — open bass)
```
Theme = half 1 + half 2. Resulting vibhag stress pattern = **tali–tali–khali–tali** (matches tintal's own 4-vibhag clap/wave pattern).

### Step 3 — Rules-check the theme
- Length = 16 matras **at some laya** (16 at 1x, 8 at 2x, 4 at 4x).
- Vibhag 3 must contain **no open baya** (khali); vibhags 1, 2, 4 each contain at least one.
- Phrase division may be uneven (3–3–2 is legal) but the *overall* stress melody must still read tali-tali-khali-tali.
- Inter-phrase contrast: phrase 1 and phrase 2 should differ in density/register/bol family, not just transpose.

### Step 4 — Generate variations **systematically**, largest unit first
Traditional development order (DigiTabla / Chhotelal Misra):
1. **Dohra** ("doubled") — the first quarter played twice, then the main bol; second half = khali quarter twice + main bol open. Doubles the length, preserves the stress pattern.
2. Variations from the **first main phrase** (e.g. stress `dhadha`; then stress `tete`; then rearrange so neither dominates).
3. Variations from the **second main phrase** (e.g. `dhadha tuna` ×3; or a new `dhate tedha dhinna` cell + the second phrase only).
4. Variations **with gaps** (silence inserted between bols — a texture variation, not a new vocabulary).
5. **New main bol** — take one sub-phrase that "sounds complete on its own", re-fit it to the cyclic shape (make its 3rd quarter khali, restore the ending-phrase pair), then vary *that*.

Five permitted operations on the theme's bols: **repeat, rearrange, substitute (within the set), invert (swap phrase order), add gaps**.

### Step 5 — Lay the **layakari ladder**
Climb subdivisions monotonically, and keep every subdivision integer-divisible into the matra:
- **barabar lay** — 2:1 (dugun), 4:1 (chaugun), 8:1 (atugun)
- **aralay** — 3:1, 6:1, 12:1 (the "3 against 4" feel; Ajrada's signature, e.g. peshkars in 3:1/6:1)
Never drop a rung on the way up; the climb *is* the form.

### Step 6 — Compose the **cadence**
Pick the cadential form and solve its arithmetic *backward from sam*:
- **Tihai** — phrase ×3, with 2 equal rests (dumdaar) or none (bedum). Constraint: `3p + 2r = 16n` (dumdaar) or `3p = 16n` (bedum). Tintal solutions: p=4,r=2 → 4-2-4-2-4; p=2,r=5 → 2-5-2-5-2. The three statements need not start on a vibhag — they may start anywhere in the cycle, which is what produces the "time-distortion then snap-to-sam" effect.
- **Anagat** — same shape but landing one matra **before** sam.
- **Chakradar** — a *tukra* (mukhra + tihai) played **three times**, i.e. a tihai of tihais. Tintal: `3 × (3×7) + 2 = 65 = 64 + 1` — three palle of 21 matras + 2 rests, last `dha` on sam.
- **Tukra / gat / paran** — fixed cadential pieces, frequently pakhawaj-derived (paran), used to close a section abruptly and reset.

### Step 7 — Assemble the **solo arc**
```
uthan (opening, optional) → peshkar (slow, improvised, incomplete tihais)
  → kayda theme → dohra → phrase-1 variations → phrase-2 variations
  → gaps → new main bol → its variations
  → rela (fast, flowing, "unbroken chain") → its variations
  → gat / tukra / paran (cadential) → chakradar → final tihai on sam
```
Peshkar's own outline (the loosest form): state theme → improvise with gaps/stress and **incomplete tihais** (the last `dha` replaced by the theme's first bol, e.g. `dhi`) → introduce non-theme bols in faster divisions → morph into a related rela or kayda → final tihai. It is the tabla's *alap*: a warm-up, a technique display, and a mood-setter, in that order.

### Step 8 — Speak it (padhant), then play it
Recite the bols aloud before/while playing. The mnemonic *is* the notation and the memory medium; teachers correct the recitation first, the hands second. Then practise the variation chain at increasing speeds until the whole chain is reproducible from memory — the tradition's actual test of composition.

---

## 4. Practitioner examples

- **Pandit Ram Sahai (1780–1826), Benares** — withdrew for six months and redesigned the instrument's fingering (notably `na` played with a curved ring finger for maximum dayan resonance), then composed new forms: **uthan**, **Benarsi theka**, **fard**, and a large body of gats, tukras and parans. The clearest historical case of a player *composing a form* rather than a piece.
- **Ustad Ahmedjan Thirakwa (c. 1892–1976), Farrukhabad** — the modern **peshkar** style, and the player usually credited with the **incomplete tihai** (final `dha` replaced by the theme's opening bol). His peshkar recordings are the reference for theme→non-theme bol alternation in 12:1.
- **Pandit Chhotelal Misra (Benares)** — theorist-practitioner of the "**new main bol**" technique: extract a sub-phrase that sounds complete, re-fit it to the cycle, then build a fresh variation family from it (*Tal Prabandh*, 2006). A 1978 BHU solo recording is the standard documented peshkar performance following the classical outline.
- **Pandit Kishan Maharaj (1923–2008), Benares** — famed for cross-rhythm calculation and **tihai/chakradar** architecture in live solo; also the Taal Vadya Kacheri dialogues with mridangam player Palghat R. Raghu.
- **Ustad Alla Rakha (1919–2000) & Ustad Zakir Hussain (1951–2025), Punjab** — Punjab gharana peshkar and layakari (especially aralay), pakhawaj-derived relas, and the globalisation of the solo format. Zakir Hussain's cross-gharana layakari is now audible in players of every lineage.
- **Ustad Mian Shaukat Hussain Khan (1930–1996), Punjab** — self-composed **qaydas** on the `tite-dhete` subject regarded as the best of their kind, plus a low-tuned bayan worked with the wrist for melodic bass variation.
- **Ustad Habibuddin Khan, Ajrada** — the Ajrada kayda with its **extra third line** in a four-line division, `gheghe tit kit`-type composite bols, and 3:1 / 6:1 divisions.
- **Pandit Anokhelal Mishra (1914–58), Samta Prasad (1921–94), Kumar Bose, Swapan Chaudhuri (Lucknow), Anindo Chatterjee (Farrukhabad)** — the 20th-c. solo-recital canon in which the peshkar → kayda → rela → cadential arc is fixed repertoire.
- **Scholarship that documents the craft:** Rebecca Stewart, *The Tabla in Perspective* (UCLA diss., 1974) — the cyclic vs. cadential classification; James Kippen, *The Tabla of Lucknow* (1988) — "pseudo-tihai"; Gert-Matthias Wegner, *Vintage Tabla Repertory* (2004); Sadanand Naimpalli, *Theory and Practice of Tabla* (2005); Sudhir Kumar Saxena, *The Art of Tabla Rhythm* (2006); David R. Courtney, *Focus on the Kaidas of Tabla* (2002); Robert S. Gottlieb, *The Major Traditions of North Indian Tabla Drumming* (1977) and *Solo Tabla Drumming of North India* (1993).

---

## 5. UnitMatrix integration

### Resolution
`ticks_per_beat=480`, `beats_per_bar=4` → bar = 1920 ticks. **1 matra = 1 beat = 480 ticks** (at 4/4, one matra per beat). **Tintal avartana = 16 matras = 4 bars = 7680 ticks.** Jhaptal = 10 matras = 4800 ticks (2.5 bars — set `beats_per_bar` to the vibhag or use 10-beat bars).

### Voices & Sections

| Voice | Role | Content |
|---|---|---|
| **Voice 0 — Daya (treble)** | **spine** | The bol stream struck on the right drum: `dha, dhin, ta/na, tin, tete, tirakita, dhati, dhagina, tinna, kina, tuna, kata`. Carries the phrase identity. **Invariant between tali and khali halves** — this is the structural rule that makes the two halves "the same composition played two ways". |
| **Voice 1 — Baya (bass)** | **stress / form layer** | Open (`ghe`, `ga`) vs. closed (`ka/kat`, or silent). One event per bol that has a bass component. Encodes tali (open) vs. khali (closed) — i.e. the *form* is literally in this voice. |
| **Voice 2 — Padhant (recited bol)** | **surface / memory layer** | The same bol syllables rendered as a speech-like timbre (spoken or pitched-on-Sa). Optional but authentic: it is the medium in which the composer actually works and the way the variation chain is memorised. Doubles V0 at 1:1 with a different instrument program. |
| **Voice 3 — Theka** | **reference grid** | The bare cycle (`dha dhin dhin dha / dha dhin dhin dha / dha tin tin ta / ta dhin dhin dha` for tintal). Muted or absent in true solo; present in accompaniment and in practice, and used as the alignment oracle for validation. |
| **Voice 4 — Sam/tali markers** | **colotomic** | Clap (tali) / wave (khali) / sam markers at vibhag boundaries — a one-event-per-vibhag structural layer for validation and for the "landing" check. |
| **Voice 5 — Nagma/harmonic bed (optional)** | **context** | Lehera/harmonium or sarangi melodic loop for practice and for pitched solo contexts; gives the sam a pitch identity (Sa on beat 1). |

### Sections = one composition unit each
```
S0  Uthan (optional opening, cadential, ends on sam)
S1  Peshkar theme            (1 avartana, blueprint)
S2  Peshkar improvisation    (n avartanas; incomplete tihais in last 4 matras)
S3  Kayda theme              (1 avartana, tali-khali split at half)
S4  Dohra                    (2 avartanas: first quarter ×2 + main bol, per half)
S5..S8  Phrase-1 variations  (1–2 avartanas each; systematic order)
S9..S12 Phrase-2 variations
S13 Gaps variation
S14 New main bol + variations
S15 Rela theme + variations  (drut laya; flowing, low-contrast bols)
S16 Gat / Tukra / Paran      (cadential, fixed)
S17 Chakradar                (3 palle = 3 × 21 matras + 2 rests in tintal)
S18 Final tihai              (last stroke on sam; end)
```
**Cells** = one matra (480 ticks) each, subdivided by bol density: at 4:1 a cell holds 4 bol events, at 12:1 twelve. Cell content is a *pair* (daya bol, baya state); a bol with both drums (`dha`, `dhin`) writes to V0 and V1 in the same tick window. Zero-drift is structural: every section is exactly `k × avartana_ticks` (k ∈ {1/2, 1, 2, 4}), padding is silence-not-padding.

### Rules to encode
1. **Avartana lock** — section length ≡ 0 (mod `avartana_ticks`); a theme of `p` bols at laya `L` occupies `p × matra/L` ticks. Nothing may straddle sam.
2. **Vibhag stress pattern** — for tintal: vibhags 1, 2, 4 contain ≥1 open-baya event; vibhag 3 contains **0** open-baya events. Generalizes per tala's tali/khali map.
3. **Tali–khali counterpart transform** — `khali(phrase)` = replace designated open strokes with their closed counterparts (`dha→ta`, `dhin→tin`, `dhinna→tuna`, `dha kata→ta kata`), **asserting V0 stroke sequence is byte-identical** to the parent. Each half of a theme/variation is produced by this one operator.
4. **Main-bol ending vocabulary** — each half must terminate in a member of the ending-phrase set (`tuna/dhinna`, `tinna/dhinna`, `tuna kata/dhinna kata`, `tinna kina/dhinna gina`, `tina taka/dinna taka`); first half uses the closed form, second half the open form (its tali counterpart).
5. **Vocabulary closure (kayda)** — every bol in a variation ∈ bol-set(theme). *Peshkar exemption:* non-theme bols allowed, but must be drawn from the peshkar phrase pool (`tirakita`, `tetegheraidha`, `tet-dhagedha`, `gheranaga`, `dhagina`) and returned from within one avartana.
6. **Systematic development order** — variation index must not skip a rung: (a) largest phrase, (b) sub-phrase, (c) sub-bol; each new main bol re-fitted to rules 2/3/4 before variation begins.
7. **Layakari ladder** — subdivision factor ∈ {2, 3, 4, 6, 8, 12} per matra; the sequence of factors across sections is non-decreasing; each factor divides the matra evenly (12:1 over a 480-tick matra = 40 ticks/bol).
8. **Tihai arithmetic** — `3p + 2r = N × avartana` (dumdaar) or `3p = N × avartana` (bedum); all three statements identical in bol content; `start_phase` free; final stroke tick ≡ 0 (mod avartana).
9. **Anagat flag** — land at `avartana − matra` instead of `0`; the following section then begins *on* sam with the resolution stroke.
10. **Chakradar** — `3 × (mukhra + tihai)` with each palla terminated by its own internal tihai; total ≡ 0 (mod avartana) with the last `dha` at sam.
11. **Peshkar rules** — theme may be stated once or never; **incomplete tihai** allowed (last `dha` of the tihai replaced by the theme's first bol); section may modulate its bol pool mid-avartana; must hand off to a rela/kayda cell rather than close.
12. **Rela profile** — bol set biased to flowing composites (`tirakita`, `ghere naga`, `dheradhera`, `dhina gina`, `dhara gina`), phrase boundaries interwoven (no cadential silence), tempo ≥ 2× the kayda's, low contrast.
13. **Tempo map** — non-decreasing across sections; doubling allowed at section seams only (never mid-avartana), because a tempo change inside a cycle breaks the sam grid.
14. **Sam convergence** — every cadential section's last event is on sam (or the anagat offset); the coda's final stroke must be an open `dha` on sam.
15. **Validate** — `composer.validate()` → True after each section; all rows equal length, all terminal landmarks at section length.

### Schematic (invented illustration, not a transcription)
Tintal, matra = 480 ticks, one avartana = 7680 ticks. Theme = `dhadha tete | dhadha dhinna` halves.

| Section | Matras | V0 daya (per matra) | V1 baya | Stress |
|---|---|---|---|---|
| S3 theme 1–4 | 4 | dha dha · te te | open open · – – | tali |
| S3 theme 5–8 | 4 | dha dha · dhin na | open open · open – | tali |
| S3 theme 9–12 | 4 | ta ta · te te | – – · – – | **khali** |
| S3 theme 13–16 | 4 | dha dha · dhin na | open open · open – | tali |
| S4 dohra 1–4 | 4 | dha dha te te (×? first quarter twice) | open… | tali |
| … | | | | |
| S18 tihai p=4,r=2 | 16 | X X X X ·· X X X X ·· X X X X | open throughout | tutti, lands on sam |

---

## 6. Pitfalls and quirks

1. **Matra ≠ bar.** Tintal is 4 bars of 4 only if you set `beats_per_bar=4`; jhaptal (10) and rupak (7) do not tile 4/4 bars. Model the *cycle* as the section unit and derive bars, or the sam drifts every avartana.
2. **The stress pattern lives in the bass voice, not in accents.** Encoding "loud on beat 1" is wrong: khali is *timbre* (closed/damped bass), not dynamic. A velocity-based model will not reproduce the form.
3. **Tali–khali is a substitution, not a transpose.** The dayan strokes are identical; only the baya changes on *designated* strokes. If the dayan stream differs between halves, it is no longer the same composition.
4. **"16 matras" is laya-relative.** The same theme is 16, 8, or 4 matras at 1x/2x/4x. A validator that demands exactly 16 will reject correct performances; store length as (bols, laya) and derive matras.
5. **Tihai rests must be *equal*.** Unequal rests make it a different figure; and a tihai whose last stroke lands one matra early is an **anagat**, not a mistake — flag, don't correct.
6. **Chakradar nests two levels of three.** `3 × (mukhra + 3p)` — conflating the inner tihai's triple with the outer triple gives 9 or 27 statements and a missed sam. Sum-check every palle.
7. **Composite bols are single events with two hands.** `dha` = `na`+`ghe`, `dhin` = `tin`+`ghe`. Splitting them into two independent voices breaks the tali/khali transform (the dayan half must stay put while the bass half flips).
8. **Gharana definitions conflict.** The same Thirakwa peshkar is called "Farrukhabad" by some and "Dilli" by others (Wegner 2004 vs. Stewart 1974). Do not hard-code a gharana→form table; store gharana as a *style prior* over bol choice and division preference.
9. **Benares has 20+ forms and no peshkar tradition.** A generic "solo arc" preset will misrepresent Benares (uthan + theka prakar + fard instead) and Punjab (rela-dominant, pakhawaj-derived parans).
10. **Peshkar's rule violation is the point.** Enforcing kayda vocabulary closure on peshkar destroys the form; it needs its own, looser validator.
11. **Recitation layer is not decoration.** Padhant is how the material is composed, checked and memorised; a system that only emits MIDI loses the actual human workflow. Keep V2 as a first-class voice.
12. **Cadential forms are fixed repertoire, not generated.** Tukra, gat, paran and traditional chakradar are *composed pieces* owned by a lineage; treat them as library assets with provenance, not as rule output.

---

## 7. Sources

- DigiTabla.com reference — *Compositional Forms Overview*, *Kayda*, *The Structure of Kaydas*, *Kayda Phrases*, *Kayda Variations 1–2*, *Peshkar*, *Rela*, *Tihai*, *Chakradar*, *Gat*, *Tukra*, *Uthan* (accessed 2026-10-22). Primary technical source for: parallel halves and tali–khali counterparts; the tali-tali-khali-tali vibhag stress rule; main-bol ending phrase set; the systematic variation guidelines and the five operations (repeat/rearrange/substitute/invert/gaps); the "new main bol"; peshkar outline, incomplete tihai, layakari progression barabar→aralay; rela's "unbroken chain" profile.
- Wikipedia — *Tabla* (kayda structure: mukh, dohara, adha dohara, vishram, adha vishram, palta, tihai; bol tables; tala/vibhag/tali/khali/sam; gharana list), *Tihai* (dumdaar/bedumdaar, anagat, 4-2-4-2-4 and 2-5-2-5-2 in tintal, 6-1 pattern in jhaptal, chakradar expansion 3×(7×3)+2 = 65 = 64+1), *Benares gharana* (Ram Sahai, uthan/fard/Benarsi theka, `na` fingering, 20+ forms), *Ajrada gharana* (3:1/6:1 divisions, `gheghe tit kit`, extra third line, bayan work, thumb on bass face), *Punjab gharana* (pakhawaj influence, Shaukat Hussain's tite-dhete qaydas, Alla Rakha, Zakir Hussain), *Lucknow gharana*, *Pakhawaj* (paran/rela ancestry, padhant recitation vs. konnakol).
- Rebecca Marie Stewart, *The Tabla in Perspective* (Ph.D. diss., UCLA, 1974) — cyclic vs. cadential classification; peshkar as "blueprint".
- James Kippen, *The Tabla of Lucknow: A Cultural Analysis of a Musical Tradition* (Cambridge UP, 1988) — "pseudo/incomplete tihai".
- Gert-Matthias Wegner, *Vintage Tabla Repertory* (Munshiram Manoharlal, 2004) — the Dilli/Farrukhabad peshkar classification problem.
- Chhote Lal Misra, *Tal Prabandh* (Kanishka, 2006) and *Tal Prasoon* (2004) — "new main bol", rela typology (swatantra rela vs. kayda-derived).
- Sadanand Naimpalli, *Theory and Practice of Tabla* (2005) / *Tabla for Advanced Students* (2009) — peshkar as "offspring of the theka"; rela as "unbroken chain".
- Sudhir Kumar Saxena, *The Art of Tabla Rhythm* (2006); David R. Courtney, *Focus on the Kaidas of Tabla* (2002); Robert S. Gottlieb, *The Major Traditions of North Indian Tabla Drumming* (1977) and *Solo Tabla Drumming of North India* (1993).
- Source-quality note: DigiTabla is a scholarly practitioner-run reference and is the most detailed public description of the variation system; Wikipedia used for repertoire/lineage facts and the tihai arithmetic examples; the step sequence in §3 is my synthesis of these, not a quotation from any single text.

---

## 8. Registry status

- Detail file: `human_method_HC-072_tabla-solo-gharana-variation-architecture.md`
- DB row: appended to `human_methods_db.md` → Human Composition Methods Framework
- Report: `report_HC-072.md`
- **Next free ID: HC-073**
