# Report HC-038 — Sonata Form Process (Galant Exposition–Development–Recapitulation Craft)

**Job:** daily-human-composition-research
**Date:** 2026-09-17
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Primary Elements:** STRUCTURE, HARMONY, PITCH, TEXTURE
**Detail file:** `human_method_HC-038_sonata-form-process.md`
**Sources:** Wikipedia *Sonata form* (rev. 2026-09-06), *Sonata theory* (Hepokoski/Darcy), *Sentence (music)*, *Period (music)*, *Galant style* — fetched live via Wikipedia REST/API during this run.

---

## 1. Method

**Sonata form process** — the human craft of building a large instrumental
movement as a tonal argument: present material in two contrasting keys,
destabilize it (modulation, fragmentation), resolve the conflict by restating
the second group in the home key.

**Tradition:** Western Classical — Viennese Classical / galant (Haydn, Mozart,
Beethoven, Schubert), ~1750–1830; pedagogy Fux → Koch (1782–93) → Czerny
(1848) → A.B. Marx; modern systematization by Caplin (*Classical Form*, 1998)
and Hepokoski/Darcy (*Elements of Sonata Theory*, 2006; SMT Wallace Berry
Award 2008).

Distinct from **HC-009 Motivic Development** (that method = the
*transformation operators* used inside a development; this method = the
*tonal + rhetorical architecture* the operators serve). Also distinct from
HC-021 (species counterpoint) and HC-001 (partimento schemata — the 2–8 bar
surface craft that fills sonata zones).

## 2. Craft procedure (the human workflow)

1. **Fix key, Type, layout.** Type 1 sonatina (no development), Type 2
   binary-development, Type 3 textbook, Type 4 sonata-rondo, Type 5 concerto.
   Continuous vs Two-Part exposition (does TR reach a medial caesura?).
2. **P in tonic, provisionally.** Sentence (basic idea + varied repetition +
   continuation + cadence) or period (antecedent/consequent). P defines the
   key but the form requires departure; P-recall marks every rotation start.
3. **TR = energy pump.** Fortspinnung, fragmentation of P's tail, rising
   sequences; modulates (V if major; III or v if minor). Goal: the **medial
   caesura (MC)** — hammer-blow chords + gap/caesura-fill. Sonata Theory: S
   cannot begin without an MC "except in highly deformational circumstances."
4. **S in the new key.** Quieter, lyrical, piano; its job is to *delay then
   deliver* the **EEC** — "the first satisfactory perfect authentic cadence
   that proceeds onward to differing material." Delay devices: evaded
   cadences, trimodular blocks. **C zone** then reinforces the new key with
   differing material. Exposition repeated.
5. **Development = tonal instability workshop.** 1st-level default: begin
   with P in a new key; 2nd-level default: episodic new material. Sequence +
   fragment exposition themes through remote keys (HC-009 operator set lives
   here). End with the **retransition (RT)**: dominant pedal, thinning, to P
   in tonic. Optional **false recapitulation** (Haydn Op. 76/1).
6. **Recapitulation = same rotation, new tonic.** P unchanged; **TR must be
   recomposed** ("secondary development") — the original modulated away, so
   its modulation contour is flattened while keeping its rhythmic profile.
   **The crux is S in the tonic** (mode may flip — Beethoven 5/i; Mozart 40/i)
   — landing the **ESC**, which "confirms the piece's tonic as a whole,
   solidifying the tonal promise first made by P." Material heavily worked in
   the development may be trimmed/omitted (Mozart K. 457, Haydn Op. 77/1).
7. **Coda.** Post-argument reinforcement: new cadential themes, P-based
   apotheosis, or Beethoven's coda-as-second-development (Eroica; Eighth
   Symphony finale).
8. **Cadence-weighting pass.** Tovey/Rosen performance practice: cadence
   emphasis = structural rank; false cadences get real-cadence marks then are
   undercut by moving on quickly.

### Defaults ladder (decision table)

| Moment | 1st default | Lower default | Deformation example |
| :--- | :--- | :--- | :--- |
| Development opening | P-based, new key | Episodic new material | Haydn Op. 76/1 false reprise |
| S in minor movement | III or v | — | Deformational S-keys |
| MC | Half cadence in new key + fill | HC in tonic | Continuous flow to S |
| Retransition | V pedal → P in tonic | Subdominant return | Brahms Op. 1 (C-dominant); Schubert 9 (E♭) |
| Recap S | Tonic, same mode | Mode flip | "Wrong-key" recapitulations |

## 3. Practitioner examples

- **Haydn** — Op. 76 No. 1 (false recapitulation); Sym. 103 "Drumroll"
  (introduction returns in coda); monothematic expositions (S = P's shape,
  contrast by key alone).
- **Mozart** — K. 465 "Dissonance" (slow intro); Sym. 40/i (S mode-flip in
  recap); K. 457 (S-omission after tonic elaboration in development);
  trimodular blocks.
- **Beethoven** — Op. 13 "Pathétique" (grave intro recurs at development
  start and coda); Sym. 5/i (S recast in parallel major at ESC); "Eroica"
  (development + second-development coda).
- **Schubert** — Sym. 9 finale (retransition lands the theme in flat
  mediant E♭ — deformational RT).
- **Brahms** — Piano Sonata No. 1 (retransition over the *tonic's* dominant
  seventh, theme arrives in C major — documented exception).
- **Hepokoski/Darcy** — codified P–TR–'–S–C action spaces, EEC/ESC,
  Types 1–5, dialogic defaults/deformations.

## 4. UnitMatrix mapping (Voices & Sections)

Layer: **concrete (target when implemented)**.

- **Voice 0 — P-theme spine:** P at every rotation start (Expo-P, Dev-P,
  Recap-P, Coda-P fragment). Invariant identity anchor.
- **Voice 1 — TR/S melodic voice:** TR = energy build (fragmentation of V0
  tail, rising sequence); S = lyrical contrast (dynamic ≤ piano, slower
  harmonic rhythm). In recap, V1's S-material transposed to tonic — the most
  rule-governed edit in the whole matrix.
- **Voice 2 — accompaniment texture:** Alberti bass/pads; density tracks
  zone (sparse under S, driving in TR, max in C).
- **Voice 3 — bass/tonal-gravity voice:** carries the key plan
  I→X→remote→V-pedal→I; owns the PAC targets at EEC/ESC.
- **Voice 4 — MC punctuation + caesura-fill + C tutti** (doubles as
  solo/tutti alternation for Type 5).

**Sections** = the tonal plot:

```
(Intro) → P(T) → TR(→V/III) ' MC → S(V/III/v) → C(EEC) → [expo repeat]
→ DEV(P-entry new key → fragments/remote → RT V-pedal)
→ P(T) → TR'(secondary development) → S'(T) → C(ESC) → Coda
```

**Rules (engine-encodable):**

1. Key-plan lock per Type (Expo T→X; X = V if major else III/v; Recap all-T).
2. EEC/ESC cadence-goal predicate: first satisfactory PAC followed by
   differing material; evasion budget in S.
3. MC-gates-S: caesura event required before S (deformation flag to bypass).
4. Rotation rule: P-recall starts a rotation; recap replays zone order.
5. Energy-gradient: TR monotonic rise to MC; RT monotonic decay to P.
6. S-contrast gate: onset-density + interval-variance drop vs TR.
7. Default/deformation ladder per zone boundary (determinism picks default;
   `deformations=[...]` injects surprises).
8. Secondary-development rule: recap-TR modulation flattened.
9. Mode-vs-key separation: S' may flip mode, never key.
10. Zero-drift tail padding at exposition repeat (`total_section_ticks − 1`
    silent event per the MIDI tail-truncation pitfall).

**Hybrids:** HC-009 operators inside the development; HC-001 partimento
schemata generate the zone surfaces (Prinner in TR, Fonte in S, Fenaroli in
RT); ABS-001 tension curve ≈ sonata tension profile; ABS-002 subset walker can
drive the development's key walk with an RT return gate.

## 5. Table row added (human_methods_db.md)

`| HC-038 | human (→concrete) | Sonata Form Process (Galant Exposition–Development–Recapitulation Craft) | Western Classical — Viennese Classical / galant (Haydn, Mozart, Beethoven, Schubert), ~1750–1830; pedagogy Koch→Czerny→Marx; systematized by Caplin (1998) & Hepokoski/Darcy Sonata Theory (2006) | STRUCTURE, HARMONY, PITCH, TEXTURE | ... | ... | ... | ✅ Documented |`

(One row appended after HC-037; full text in the DB.)

## 6. Next free ID

Max existing = HC-038 → **next free ID = HC-039**.

## 7. Quirks / pitfalls

- **Recap-TR is the failure point:** naive exposition replay re-modulates and
  never returns home — must recompose TR (flatten modulation).
- **EEC ≠ any PAC:** first S-PAC is often evaded/repeated ("S tries again");
  predicate requires *proceeding onward to differing material*.
- **Mode vs key:** recap S may flip mode but never key — encode as
  pitch-class center + scale-set toggle.
- **Continuous expositions** have no MC — P|TR S|C segmentation assumptions
  mis-split them (common in concertos).
- **False recapitulation** fools theme-match P-detectors; detect via the
  subsequent modulation-away.
- **Monothematic expositions** (Haydn) reuse P for S — contrast-by-key only;
  a contrast-scored gate would reject Haydn.
- **No duration gates:** development length spans tiny (Eine kleine
  Nachtmusik) → colossal (Eroica); gate on cadential landmarks, not
  proportional length.
- **Dedup check done:** no prior sonata-form entry (HC-009 is motive
  operators, verified distinct).

## 8. Verification log

- `grep -oE '\*\*HC-[0-9]+\*\*'` on human_methods_db.md before write: max
  HC-037 (table rows scanned + human_method_HC-*.md + report_HC-*.md cross-checked).
- Detail file written: `human_method_HC-038_sonata-form-process.md` (15.8 KB).
- DB row appended via targeted patch (HC-038 row after HC-037; no other rows touched).
- Post-write grep: HC-038 present in both files (1 detail file + 1 table row).
- Next free ID: **HC-039**.
