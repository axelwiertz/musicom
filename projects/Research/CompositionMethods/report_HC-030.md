# Report — HC-030 Argentine Tango Arrangement & Marcato Counterpoint (Orquesta Típica Craft)

**Job:** daily-human-composition-research
**Date:** 2026-09-08
**Method ID:** HC-030
**Layer:** human → `concrete` (target when implemented)
**Tradition / Culture:** Argentine/Uruguayan **tango** — Río de la Plata (Buenos Aires, Argentina & Montevideo, Uruguay), ~1880s–present. Lineage: *Guardia Vieja* (1890s–1920s, habanera/milonga roots) → *Guardia Nueva* (1920s–30s, Decarean school — Julio de Caro's sextet refines tango from dance music into composed counterpoint) → *Golden Age* (1940s–50s) → *Tango Nuevo* (Piazzolla). UNESCO Intangible Cultural Heritage (2009).

---

## 1. Method Name

Argentine Tango Arrangement & Marcato Counterpoint — arranging/composing for the
**orquesta típica** (bandoneón-led tango sextet) around a shared rhythmic
*compás tanguero* and a contrapuntal dialogue between a cantabile melody
(violin) and a marcato counter-melody (bandoneón).

## 2. Tradition

Tango grew in the port cities of the Río de la Plata from a fusion of habanera
(Cuba), milonga (rural gaucho song/dance), candombe (Afro-Uruguayan drumming),
and European immigrant music (Italian/Spanish). Three stages matter for the
craft:

- **Guardia Vieja** — tango as dance music; simple 2/4, habanera-derived bass.
- **Guardia Nueva / decarismo** — **Julio de Caro** (violinist) led the sextet
  that made tango a *composed, contrapuntal* art form: two equal melodic voices
  (violin + bandoneón) instead of melody-over-accompaniment.
- **Golden Age** — Troilo, Pugliese, Salgán, Di Sarli, D'Arienzo: the classic
  orquesta típica lineup (2 bandoneones, 2 violins, piano, contrabajo) with
  idiomatic marcato rhythms, *fraseo* phrasing, and arrangement arcs.
- **Tango Nuevo** — Piazzolla extends harmony/form (chromatic lament, fugue,
  concert forms) while keeping the compás spine.

The craft is learned by apprenticeship inside orchestras and transmitted via
the *arreglo* (arrangement score) — not an academic treatise. UNESCO inscribed
tango (Argentina & Uruguay) in 2009.

## 3. Layer

`concrete` (target). Human-craft knowledge — realizes material through the
UnitMatrix into playable voices/events. Not a generator; not routed by the
SCALE selector. Target layer stated per job contract.

## 4. Craft Procedure (how the human does it, step by step)

1. **Fix the rhythmic spine (compás tanguero).** Three core cells, all
   syncopated against a 2/4 or 4/4 grid:
   - **marcato en 4** — strong staccato accent on all four beats (bandoneón +
     piano chop; "el Rey del Compás" D'Arienzo pushed this hardest);
   - **habanera / milonga 3-3-2** — the dotted `♪· ♪· ♪♪` figure (ta-dum ta-dum
     ta-dum), the tango/milonga bass fingerprint;
   - **yumba** — Pugliese's heavy accent *on the off-beat* (syncopated, dragged,
     almost late). Plus **arrastre** (bass "drag"/gliss into the downbeat) and
     **síncopa** (anticipations).
2. **Fix tonality.** Tango leans minor (A/D/G minor) with a **chromatic
   descending bass** (the "lament" line: i → ♭7 → ♭6 → ♭5 etc. under a static
   melody — cf. Piazzolla "Adiós Nonino"), ii–V–I, harmonic/melodic minor,
   dominant 7♭9/9, diminished passing chords. Milonga = faster 2/4 habanera;
   tango-vals = 3/4.
3. **Choose the form.** Instrumental tango = 2–3 sections (A-B-A or A-B-C), each
   **16 bars** (8 antecedent + 8 consequent), plus a short intro and coda.
   Tango-canción (song) = intro → estrofa (verse) → estribillo (refrain) →
   estrofa' → estribillo' → coda.
4. **Write the cantabile melody with fraseo.** Pick-up (anacrusis) start,
   syncopated off-beat accents, rubato, chromatic neighbor tones, lyricism;
   phrases resolve onto the downbeat. The violin carries this "singing" line.
5. **Write the bandoneón counter-melody.** Bandoneón alternates **left-hand
   marcato chord stabs** with a **right-hand second melodic line** that answers
   and weaves around the violin melody — the Decarean core idea: *two equal
   melodic voices in dialogue*, not melody + accompaniment.
6. **Voice the rhythm section.** Double bass: root/5th, anticipated or yumba
   off-beats, or arrastre slides. Piano: marcato chords on the beats + syncopated
   fill runs ("yeites"). Second violin: parallel 3rds/6ths with the lead or a
   third contrapuntal voice.
7. **Build the arrangement arc.** State the melody (violin) → bandoneón solo
   (ornamented, more chromatic variation) → piano solo → **tutti** (melody +
   counter-melody + full marcato together = climax) → coda.
8. **Close with idiomatic gestures (yeites).** Arrastre drag into the final
   chord, chicharra (bandoneón scrape), rubato "fraseo" rallentando, and a
   final marcato stinger ("chan-chan" cadence).

## 5. Practitioner Examples

- **Julio de Caro** (violinist, "decarismo") — Sexteto Julio de Caro, "Boedo"
  (1928): refined tango from dance music into composed counterpoint; two equal
  melodic voices.
- **Carlos Gardel** — the tango-canción voice ("Mi Buenos Aires querido",
  "Volver"); defined the singing tango.
- **Aníbal Troilo** ("Pichuco") — bandoneón, "Sur", "Responso"; lyrical fraseo.
- **Osvaldo Pugliese** — "La Yumba" (1946), namesake of the yumba off-beat
  accent; "Negracha".
- **Astor Piazzolla** — tango nuevo, "Adiós Nonino", "Libertango", "Oblivion",
  "Estaciones Porteñas"; extended harmony, bandoneón as lead, chromatic lament.
- **Horacio Salgán** — "A fuego lento"; most sophisticated arrangement/counterpoint.
- **Juan D'Arienzo** — "el Rey del Compás" (the King of the Beat), driving marcato.
- **Mariano Mores** — "Taquito militar".

## 6. UnitMatrix Mapping (Voices & Sections)

### Voices
- **Voice 0 = contrabajo bass spine** — habanera/milonga 3-3-2 cell, root/5th,
  chromatic-descending "lament" line; the invariant rhythmic-harmonic floor.
- **Voice 1 = violin cantabile lead** — the singing melody, fraseo (pick-ups,
  off-beat accents, rubato), chromatic neighbor decoration.
- **Voice 2 = bandoneón counter-melody + marcato** — second independent melodic
  line (right hand) weaving around Voice 1, alternating with left-hand staccato
  marcato chord stabs.
- **Voice 3 = piano marcato + yeites** — chords on the beats, syncopated fill
  runs between phrases.
- **Voice 4 (optional) = second violin** — parallel 3rds/6ths or a third
  contrapuntal voice.

### Sections
Instrumental tango: **Intro → A (16) → B (16) → A' (16) → Coda** (or A-B-C),
each section 8+8. Tango-canción: **Intro → Estrofa → Estribillo → Estrofa' →
Estribillo' → Coda**. The arrangement arc maps one solo-feature voice per
section, reserving the tutti for the climax.

### Rules (what would encode it)
- **Compás invariance** — Voice 0 groove (habanera 3-3-2 / marcato / yumba)
  never stops; other voices decorate around it.
- **3-3-2 cell + marcato en 4** — onsets snap to the dotted habanera cell or the
  four marcato beats; yumba = off-beat accent.
- **Minor-key + chromatic-descending bass** — lament line under static/stepwise
  melody; harmonic/melodic minor palette + dominant 7♭9/9 + diminished passing.
- **Counterpoint rule** — Voice 1 & Voice 2 are independent melodic lines
  (contrary/oblique motion, no unison doubling); one cantabile (legato,
  rubato), one marcato (staccato, metronomic).
- **Fraseo rule** — melody pick-ups, off-beat accents, phrase resolves on the
  downbeat; rubato = durational freedom at phrase ends.
- **Section = 16 bars** — 8+8 antecedent/consequent; intro/coda short.
- **Arrangement-arc rule** — one solo-feature voice per section, monotonic
  density rise to the tutti climax, coda with arrastre + final stinger.

## 7. Table Row Added

Appended to the 'Human Composition Methods Framework' table in
`human_methods_db.md` (kept aligned with the 9-column schema):

| HC-030 | human (→concrete) | Argentine Tango Arrangement & Marcato Counterpoint (Orquesta Típica Craft) | Argentine/Uruguayan tango — Río de la Plata (Buenos Aires & Montevideo), ~1880s–present; Guardia Vieja → Decarean school → Golden Age → Tango Nuevo; UNESCO Intangible Heritage (2009) | RHYTHM, HARMONY, PITCH, STRUCTURE, TEXTURE | ... | Voice 0 = contrabajo bass spine ... Voice 1 = violin cantabile lead ... Voice 2 = bandoneón counter-melody + marcato ... | Julio de Caro ... Piazzolla ... | ✅ Documented |

(Full aligned row in the DB; full text in the detail file.)

## 8. Next Free ID

**HC-031** (highest existing = HC-030, this job's new ID; next = max+1).

## 9. Quirks / Pitfalls (engine-fit notes for the implementer)

1. **Marcato vs legato = two simultaneous feel-layers.** Voice 2 (bandoneón)
   must switch between staccato chord stabs and a legato counter-line; needs a
   per-event articulation flag (or two sub-voices), not one global "style".
2. **Rubato vs fixed grid.** Fraseo bends phrase-end durations; UnitMatrix's
   absolute-tick grid will quantize it. Encode rubato as a post-pass durational
   offset on phrase-terminal events, gated to keep track-length symmetry (the
   zero-drift invariant).
3. **3-3-2 vs straight 4.** The habanera cell is a 2-beat dotted figure, not
   swing 8ths; if rendered as straight 16ths it sounds like a march, not tango.
   The accent mask `{0, 1.5, 2}` per 2-beat cell is the fix.
4. **Chromatic bass under static melody** (lament) can produce vertical
   dissonances a naive scale-filter would reject — the descending line is the
   *harmonic identity*; validation must allow chromatic passing chords over it.
5. **Counter-melody ≠ harmony pad.** The bandoneón line is an independent
   melody (Decarean), not chordal filling — scoring it as block chords loses the
   entire method. Keep it a Voice-1-like contour with its own register/fraseo.

## 10. Files

- Detail: `/opt/data/projects/Research/CompositionMethods/human_method_HC-030_argentine-tango-marcato-counterpoint.md`
- DB: `/opt/data/projects/Research/CompositionMethods/human_methods_db.md`
- Report (this file): `/opt/data/projects/Research/CompositionMethods/report_HC-030.md`
