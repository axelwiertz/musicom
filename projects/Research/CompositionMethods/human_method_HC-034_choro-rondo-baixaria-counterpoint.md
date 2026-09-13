# HC-034 — Choro Rondo & Baixaria Counterpoint (Roda de Choro Craft)

**Method ID:** HC-034
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Tradition:** Brazilian Choro (chorinho) — Rio de Janeiro, late 19th c.–present
**Primary Elements:** STRUCTURE, HARMONY, PITCH, RHYTHM, TEXTURE
**Status:** ✅ Documented

---

## 1. What it is

**Choro** (Portuguese "cry"/"lament", diminutive *chorinho* "little cry") is the
first characteristically Brazilian genre of *urban instrumental* popular music,
born in late-19th-century Rio de Janeiro. Despite the name it is usually fast
and bright. Musically it fuses European salon dances (polka, waltz, mazurka,
schottische) with Afro-Brazilian rhythmic cells (lundu, batuque) and, from the
1920s, jazz harmony. Its two signature *craft* features — the ones this entry
documents — are:

1. **The rondo form** with a fixed key-rotation plan: three sections played
   `AABBACCA`, each section in a different key (principal → relative mode →
   subdominant).
2. **The baixaria** — the improvised *contrapuntal bass* played by the 7-string
   guitar, which weaves descending/arpeggiated counterlines through the gaps of
   the lead melody while the cavaquinho and 6-string guitar supply the harmonic
   rhythm.

Choro is learned and played in the **roda de choro** ("choro circle"): musicians
gather, state the piece's melody together, then take turns leading
improvised variations over the frozen rondo — the bass/comping layer never
stops, so the texture remains continuously flowing despite the virtuosic,
syncopated, gap-filled lead lines.

---

## 2. Layer classification

`layer: concrete (target when implemented)` — same tag as all HC-* rows. Choro
is human-craft *knowledge* with no algorithmic generator in the registry; when
implemented it would realize the AABBACCA key-rotation rondo as UnitMatrix
sections with a frozen baixaria spine + comping layer + lead melody + optional
variation voices.

---

## 3. Craft procedure (how a human does it, step by step)

1. **Fix the rondo skeleton.** Decide the piece is a 3-section rondo played
   `AABBACCA` (A twice, B twice, A once, C twice, C once, A once). This binary
   rondo is the canonical choro macro-form, notated or agreed by ear in the roda.
2. **Fix the key-rotation plan.** Set section A in the principal key, section B
   in the relative mode (relative minor if A is major, relative major if minor),
   section C in the subdominant key. The modulations between sections are
   "subtle" (Claude — often via ii–V pivots or direct common-tone shifts), not
   abrupt.
3. **Compose the lead melody (section A).** Write a syncopated, virtuosic 16-bar
   (or 8+8) theme in the principal key — heavily off-beat, with anticipations
   and chromatic passing notes. This becomes the piece's identity.
4. **Compose section B** in the relative mode — same phrase architecture, new
   tonal colour (contrast by mode, not by rhythm).
5. **Compose section C** in the subdominant — often the "turnaround" material
   that re-energizes the cycle back into A.
6. **Write the harmonic grid (cavaquinho + 6-string guitar).** Chord changes
   typically land on strong beats in a cyclical pattern (frequent I–IV–V and
   ii–V–I cells, with chromatic approach to the dominant). This grid is the
   *frozen* harmonic spine every player agrees to.
7. **Write the baixaria (7-string guitar bass line).** The *contrapuntal*
   signature: an improvised bass that fills every gap of the lead melody with
   descending chromatic lines, scalar/arpeggio runs, and anticipated chord tones,
   re-entering the chord root on downbeats. In old trios the 7-string's low
   B/C strings extend the bass register; this is the "counterpoint" of choro.
8. **Add the counterpoint layer (a second melody instrument).** In the classic
   duet texture (e.g. Pixinguinha on flute/sax + Benedito Lacerda on flute), two
   lead instruments *weave counterlines* — one states the melody while the other
   plays a decorated obbligato, then they swap; never both simply playing unison.
9. **Layer the pandeiro + cavaquinho swing.** Light percussion (pandeiro, atabaque
   in some styles) supplies the syncopated 16th-note pulse; cavaquinho strums
   or arpeggiates the chords on off-beats. This continuous layer keeps the
   texture flowing under the sparse virtuosic leads.
10. **Take the roda.** Musicians assemble in a circle; the melody is stated in
    unison/octaves; then players rotate the lead, each improvising variations
    (rhythmic displacement, added ornament, arpeggio fills, octave jumps) over
    the frozen form and harmonic grid while the rhythm section never stops. The
    piece ends with a return to the A melody and a final "coda" cadence.
11. **Balance counterpoint vs. comping.** The arranger checks that the baixaria
    and any obbligato never collide with the *lead* phrase's active notes (call
    operates on the gaps), and that the cavaquinho chord hits land on the grid —
    this is what separates choro from free improvisation: the form and the bass
    are governed; only the lead *variation* is free.

---

## 4. Practitioner examples

- **Pixinguinha** (Alfredo da Rocha Viana Filho, 1897–1973) — the towering choro
  composer/arranger; merged 19th-c. salon dance forms with jazz harmony and
  Afro-Brazilian rhythm. Signature pieces: *Carinhoso*, *Lamento*, *Um a Zero*
  (with Benedito Lacerda), *Glória*.
- **Benedito Lacerda** — Pixinguinha's duet partner on flute; the classic
  lead/counter-lead texture is documented in their *1 x 0* recordings.
- **Jacob do Bandolim** — bandolim (mandolin) virtuoso who codified the modern
  choro revival repertoire (*Noites Cariocas*, *Doce de Coco*).
- **Waldir Azevedo** — cavaquinho master (*Brasileirinho*, a "Brazilian tango"
  classic).
- **Ernesto Nazareth** — the piano precursor whose *polca-choro*/maxixe hybrids
  (e.g. *Odeon*, *Escovado*) set the syncopated, modulatory choro idiom.
- **Chiquinha Gonzaga** — early female composer (*Corta Jaca*, *Atraente*) of
  polca-choro and maxixe.
- **Dino 7 Cordas (Horondino José da Silva)** — the archetypal 7-string guitarist
  whose improvised baixarias made the instrument's contrapuntal bass role famous;
  **Raphael Rabello** his modern heir.
- **João Pernambuco** — guitarist of the choro golden age (*Magoado*).

---

## 5. UnitMatrix mapping (Musicom engine)

### Voices & Sections

| Voice | Role | Content | Invariance |
|---|---|---|---|
| Voice 0 | **baixaria spine** (7-string guitar) | improvised contrapuntal bass: descending chromatic runs, arpeggios, anticipated chord tones filling melody gaps, roots on downbeats | harmonic-root + re-entry rule invariant (fills gaps, lands on grid) |
| Voice 1 | **lead melody** (flute/bandolim/clarinet) | syncopated virtuosic theme of section A/B/C; in roda becomes the variation line | section theme identity frozen (in composition); free only in roda variation |
| Voice 2 | **harmony/comping** (cavaquinho + 6-string guitar) | chord grid on strong beats, strummed/arpeggiated off-beats | chord-grid invariance (shared by all players) |
| Voice 3 | **counter-lead / obbligato** (second flute/sax) | decorated counterline weaving the lead's gaps when lead rests | call-gap interlock (never overlaps lead's active notes) |
| Voice 4 | **pandeiro pulse** | syncopated 16th-note swing, light percussion | continuous-pulse invariance (never stops) |

**Sections** = the rondo modules: `A → A → B → B → A → C → C → A` (canonical
`AABBACCA`). Each section = 16 bars (8+8) in its key. The key plan maps directly
to section-tonality tags: A = tonic, B = relative mode, C = subdominant. A roda
"second pass" can be modeled as an additional rotation of the A section with a
variation mask applied to Voice 1.

### Rules to encode

- **Rondo invariance**: section order locked to `AABBACCA` (or its ABC
  rotation); no section skipped.
- **Key-rotation plan**: tonality(A) = principal; tonality(B) = relative mode;
  tonality(C) = subdominant. Modulation pivots chosen from {ii–V, direct
  common-tone/stepwise} — no abrupt jumps.
- **Baixaria gap-fill rule**: bass onsets occur where the lead voice is *inactive*
  (fill the lead's rests; re-enter chord root on downbeats; prefer descending
  chromatic/scalar/arpeggio motion). This is the contrapuntal "counterpoint"
  constraint.
- **Lead/counter-lead interlock**: Voice 3 (obbligato) and Voice 1 (lead) never
  both sustain active pitch simultaneously at phrase peaks — one states, the other
  decorates the gaps (swap roles).
- **Syncopation + anticipation**: melody and baixaria onsets bias toward off-beats
  and anticipations (characteristic syncopation).
- **Harmonic-grid invariance**: chord changes on the metric grid, cyclical
  I–IV–V / ii–V–I cells, chromatic approach to dominant; shared by all voices.
- **Continuous-fill layer**: pandeiro pulse + cavaquinho off-beat arpeggios =
  always-on texture under the sparse virtuosic leads (see hybridization rule:
  sparse lead + continuous comping = flowing).
- **Variation-not-invention** (roda): lead variation = rhythmic displacement,
  ornament, arpeggio fill, octave shift over frozen form/harmony — no re-harmonizing.
- **Return-to-A closure**: piece ends on restatement of the A melody + cadence
  (coda) rather than fading.

### Element mapping

- **STRUCTURE** — the `AABBACCA` rondo + key-rotation plan (primary).
- **HARMONY** — cyclical grid, ii–V pivots, subdominant section-C colour (primary).
- **PITCH** — syncopated chromatic lead + descending baixaria counterpoint (primary).
- **RHYTHM** — pandeiro 16th-note swing, anticipation/off-beat bias (secondary).
- **TEXTURE** — lead/counter-lead + frozen bass + continuous comping layering (secondary).

---

## 6. Quirks / pitfalls

- **"Choro" ≠ sad** — the name means "cry" but the music is typically bright and
  fast; a mood-based generator steer would be wrong.
- **Baixaria is improvised but constrained** — it is the *contrapuntal* glue,
  not a free solo: encode it as gap-fill + root-reentry, not random bass. Naive
  stepwise bass with no regard to the lead's active notes collapses the counterpoint.
- **Key rotation is the form's engine** — a generator that keeps all sections in
  one key loses the defining "subtle modulation" character. Encode
  {A→tonic, B→relative, C→subdominant} as a hard constraint.
- **The roda is variation, not recomposition** — freeze the harmonic grid + form,
  vary only the lead (and freely exchange lead/obbligato roles). Treat the roda
  as a "variation mask" applied to Voice 1, never a new progression.
- **Two-lead counterpoint ≠ doubling** — the classic duet texture requires
  interlocked gap-fill between two lead instruments, not unison doubling
  (distinguish from the single-lead + comping trio).
- **Continuous texture despite sparse leads** — choro lead lines are syncopated and
  gap-heavy, but the cavaquinho + pandeiro + baixaria keep it flowing; this is
  the canonical "sparse method + continuous fill" hybrid pattern.