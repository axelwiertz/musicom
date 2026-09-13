# Report — HC-034 Choro Rondo & Baixaria Counterpoint (Roda de Choro Craft)

**Date:** 2026-09-12
**Job:** daily-human-composition-research
**Method ID:** HC-034
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Next free ID after this:** HC-035

---

## 1. Method name & tradition

**Choro Rondo & Baixaria Counterpoint (Roda de Choro Craft).**

Brazilian **choro** (diminutive *chorinho* — "little cry"), the first
characteristically Brazilian genre of urban instrumental popular music, born in
late-19th-century Rio de Janeiro. It fuses European salon dances (polka, waltz,
mazurka, schottische) with Afro-Brazilian rhythmic cells (lundu, batuque) and,
from the 1920s, jazz harmony. Its two signature craft features documented here
are the **AABBACCA rondo with fixed key-rotation** (A = principal, B = relative
mode, C = subdominant) and the **baixaria** — the improvised contrapuntal bass of
the 7-string guitar that fills the gaps of the lead melody while cavaquinho +
6-string guitar comp the harmonic grid.

**Rotation note:** Latin American pick (rotation previously: Western Classical
×12, African/Afro-diasporic ×6, East/Southeast Asian ×5, Middle/Central Asian ×3,
European folk ×3, Latin American ×2, Arctic Indigenous ×1). Choro adds the first
*Brazilian* urban-instrumental entry — distinct from cue that the existing
flamenco (HC-012) and tango (HC-030) cover Iberian and Río-de-la-Plata craft.

## 2. Layer classification

`layer: concrete (target when implemented)` — same tag as all HC-* rows. Choro is
human-craft *knowledge* with no algorithmic generator in `generator_registry` and
no ABS-* spec. When implemented it realizes the AABBACCA key-rotation rondo as
UnitMatrix sections with a frozen baixaria spine + comping layer + lead melody +
optional variation/counter-lead voices.

## 3. Craft procedure (how a human does it, step by step)

1. **Fix the rondo skeleton** — 3 sections, played `AABBACCA`.
2. **Fix the key-rotation plan** — A = principal key, B = relative mode, C = subdominant.
3. **Compose section A melody** — syncopated, virtuosic 16-bar (8+8) theme in the principal key.
4. **Compose section B** — same phrase architecture in the relative mode (contrast by mode, not rhythm).
5. **Compose section C** — subdominant "turnaround" material re-energizing back into A.
6. **Write the harmonic grid** (cavaquinho + 6-string guitar) — chord changes on strong beats, cyclical I–IV–V / ii–V–I cells, chromatic approach to dominant.
7. **Write the baixaria** (7-string guitar bass) — contrapuntal bass filling every gap of the lead with descending chromatic runs, arpeggios, anticipated chord tones; re-enters chord root on downbeats.
8. **Add the counterpoint layer** — a second lead instrument weaves an obbligato counterline through the lead's rests; two leads swap roles rather than play unison.
9. **Layer pandeiro + cavaquinho swing** — syncopated 16th-note pulse + off-beat arpeggios = continuous flow under the sparse leads.
10. **Take the roda** — musicians state the melody together, then rotate the lead improvising variations (rhythmic displacement, ornament, arpeggio fill, octave shift) over the frozen form/harmony; rhythm section never stops; end on return-to-A + coda cadence.
11. **Balance counterpoint vs. comping** — baixaria/obbligato operate only in the lead's gaps; cavaquinho hits land on the grid.

## 4. Practitioner examples

- **Pixinguinha** (Alfredo da Rocha Viana Filho, 1897–1973) — *Carinhoso*, *Lamento*, *Um a Zero* (duet with Benedito Lacerda), *Glória*.
- **Benedito Lacerda** — duet partner; lead/counter-lead texture.
- **Jacob do Bandolim** — *Noites Cariocas*, *Doce de Coco*.
- **Waldir Azevedo** — *Brasileirinho* (cavaquinho).
- **Ernesto Nazareth** — *Odeon*, *Escovado* (polca-choro/maxixe precursor).
- **Chiquinha Gonzaga** — *Corta Jaca*, *Atraente* (early female composer).
- **Dino 7 Cordas** (Horondino José da Silva) — archetypal baixaria guitarist; **Raphael Rabello** modern heir.
- **João Pernambuco** — *Magoado*.

## 5. UnitMatrix mapping (Musicom engine)

### Voices & Sections

| Voice | Role | Content | Invariance |
|---|---|---|---|
| Voice 0 | **baixaria spine** (7-string guitar) | contrapuntal bass: descending chromatic/scalar/arpeggio runs filling melody gaps, roots on downbeats | root + gap-fill re-entry invariant |
| Voice 1 | **lead melody** | syncopated virtuosic section theme; roda variation line | theme frozen in composition; free only as variation |
| Voice 2 | **harmony/comping** (cavaquinho + 6-string) | chord grid on strong beats, off-beat arpeggios | chord-grid invariance |
| Voice 3 | **counter-lead / obbligato** | decorated counterline weaving lead's gaps | gap-interlock (never overlaps lead) |
| Voice 4 | **pandeiro pulse** | syncopated 16th-note swing | continuous-pulse invariance |

**Sections** = rondo modules `A → A → B → B → A → C → C → A` (`AABBACCA`), each
16 bars (8+8). Key plan = section tonality tags: A = tonic, B = relative mode,
C = subdominant. A roda "second pass" = extra A rotation with variation mask on
Voice 1.

### Rules to encode

- **Rondo invariance** — section order locked to `AABBACCA`.
- **Key-rotation plan** — A = principal, B = relative mode, C = subdominant; pivots ∈ {ii–V, common-tone/stepwise}.
- **Baixaria gap-fill** — bass onsets where lead is inactive; root on downbeat; descending chromatic/scalar/arpeggio preference.
- **Lead/counter-lead interlock** — Voice 3 decorates Voice 1's gaps; roles swap; no unison doubling.
- **Syncopation + anticipation** — melody/baixaria off-beat bias.
- **Harmonic-grid invariance** — changes on grid, cyclical I–IV–V / ii–V–I, chromatic approach to dominant.
- **Continuous-fill layer** — pandeiro + off-beat cavaquinho always-on under sparse leads.
- **Variation-not-invention** (roda) — lead variation only (displacement/ornament/arpeggio/octave).
- **Return-to-A closure** — coda restates A melody + cadence.

### Element mapping

**STRUCTURE** (rondo + key rotation, primary), **HARMONY** (cyclical grid + ii–V pivots + subdominant C, primary), **PITCH** (syncopated chromatic lead + descending baixaria counterpoint, primary), **RHYTHM** (pandeiro 16th swing + anticipation, secondary), **TEXTURE** (lead/counter-lead + frozen bass + continuous comping, secondary).

## 6. Table row added (human_methods_db.md)

```
| HC-034 | human (→concrete) | Choro Rondo & Baixaria Counterpoint (Roda de Choro Craft) | Brazilian Choro (chorinho) — Rio de Janeiro, late 19th c.–present; fuses European salon dances (polka/waltz/mazurka/schottische) + Afro-Brazilian lundu/batuque + jazz harmony; roda = improvised circle | STRUCTURE, HARMONY, PITCH, RHYTHM, TEXTURE | Fix rondo skeleton AABBACCA (3 sections) → fix key-rotation plan (A=principal, B=relative mode, C=subdominant) → compose syncopated virtuosic 16-bar lead theme (A) → compose B (same phrase, relative mode, contrast by mode) → compose C (subdominant turnaround) → write harmonic grid (cavaquinho+6-str guitar: strong-beat changes, I–IV–V/ii–V–I, chromatic approach to dominant) → write baixaria (7-str guitar contrapuntal bass fills lead gaps with descending runs/arpeggios, root on downbeat) → add counter-lead obbligato (2nd instrument weaves lead gaps, roles swap) → layer pandeiro+cavaquinho swing (continuous 16th pulse) → roda: state melody, rotate lead variations over frozen form/harmony → return to A + coda | Voice 0 = baixaria spine (7-str guitar contrapuntal bass, gap-fill + root-reentry invariant). Voice 1 = lead melody (syncopated theme, frozen in composition, free as roda variation). Voice 2 = harmony/comping (cavaquinho+6-str chord grid + off-beat arpeggios). Voice 3 = counter-lead/obbligato (decorated counterline, never overlaps Voice 1). Voice 4 = pandeiro pulse (continuous 16th swing). Sections = AABBACCA rondo modules (16-bar 8+8 each; A=tonic, B=relative, C=subdominant). Rules: rondo-invariance, key-rotation-plan, baixaria gap-fill, lead/counter-lead interlock, syncopation+anticipation bias, harmonic-grid invariance, continuous-fill layer, variation-not-invention, return-to-A closure | Pixinguinha (Carinhoso, Lamento, Um a Zero), Benedito Lacerda (duet), Jacob do Bandolim (Noites Cariocas), Waldir Azevedo (Brasileirinho), Ernesto Nazareth (Odeon), Chiquinha Gonzaga (Corta Jaca), Dino 7 Cordas & Raphael Rabello (baixaria), João Pernambuco (Magoado) | ✅ Documented |
```

## 7. Verification

- `HC-034` present in detail file `human_method_HC-034_choro-rondo-baixaria-counterpoint.md` ✓
- `HC-034` present in `human_methods_db.md` framework table ✓
- Highest ID = **HC-034**; next free ID = **HC-035** ✓
- No duplicate HC-034 in table ✓

## 8. Quirks / pitfalls

- **"Choro" ≠ sad** — the name means "cry" but the music is typically bright/fast; a mood-based steer would be wrong.
- **Baixaria is improvised but constrained** — encode as gap-fill + root-reentry, not random bass; naive stepwise bass collapses the counterpoint.
- **Key rotation is the form's engine** — keep {A→tonic, B→relative, C→subdominant} as a hard constraint or lose the "subtle modulation" character.
- **The roda is variation, not recomposition** — freeze grid + form, vary lead only; model roda as a variation mask on Voice 1.
- **Two-lead counterpoint ≠ doubling** — interlocked gap-fill between two lead instruments, not unison doubling.
- **Continuous texture despite sparse leads** — cavaquinho + pandeiro + baixaria keep it flowing; canonical "sparse method + continuous fill" hybrid.