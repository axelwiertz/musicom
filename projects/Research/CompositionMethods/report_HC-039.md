# Report HC-039 — Irish Traditional Dance Tune Setting & Ornamentation Craft (AABB Binary Form + Setting/Regional Dialect)

**Job:** daily-human-composition-research
**Date:** 2026-09-19
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Primary Elements:** STRUCTURE, RHYTHM, PITCH, TEXTURE
**Detail file:** `human_method_HC-039_irish-traditional-dance-tune-setting.md`
**Sources:** Breathnach (*Ceol Rince na hÉireann* 1963–1999; *Folk Music and Dance of Ireland* 1971), Francis O'Neill (*Music of Ireland* 1903), Vallely (*Companion to Irish Traditional Music* 2011), Tradschool & TU Dublin research on machine annotation of Irish traditional dance music.

---

## 1. Method

**Irish traditional dance tune setting and ornamentation craft** — the human method of creating, setting, varying, and realizing dance tunes within an invariant cyclic binary architecture (**AABB**).

**Tradition:** Irish Traditional Music (Ceol Dúchais na hÉireann) — Ireland, ~17th c.–present; oral/aural transmission within regional fiddle/piping/flute lineages (Sligo, Clare, Donegal, East Galway, Sliabh Luachra); codified by Francis O'Neill (*Music of Ireland* 1903), Breandán Breathnach (*Ceol Rince na hÉireann* 1963–1999).

Distinct from:
- **HC-012 (Flamenco Compás & Falseta):** 12-beat asymmetric compás vs strict symmetrical 32-bar AABB binary dance grid.
- **HC-026 (Scottish Pibroch Theme & Variation):** Pibroch is a slow Highland bagpipe ceremonial art form (ceòl mór); HC-039 is social dance music (ceol rince) with persistent motoric rhythmic drive.
- **HC-036 (Norwegian Hardanger Fiddle Slått):** Hardanger slått features scordatura tunings and asymmetrical 3-beat springar meters; Irish dance tunes use standard pitch references and strictly symmetrical binary meter.
- **HC-028 (Jazz Chord-Scale Improvisation):** Jazz soloists improvise new harmonic paths over functional progressions; Irish musicians vary the *setting and ornamentation* of the melodic skeleton while leaving the communal skeletal melody instantly recognizable.

---

## 2. Craft Procedure (The Human Workflow)

1. **Select Tune Type, Metric Grid & Pulse Architecture:**
   - Reel (4/4 or 2/2, 106–120 bpm, continuous 8th notes).
   - Double Jig (6/8, 110–126 bpm, triplet lilt 3+3).
   - Slip Jig (9/8, 112 bpm, 3+3+3).
   - Hornpipe (4/4, 88–96 bpm, swung dotted 8ths + cadential triplets).
   - Slide (12/8, 130–144 bpm) / Polka (2/4, 124–136 bpm).
2. **Establish Modal Center & Pitch Gamut:**
   - Grounded in uilleann pipe/tin whistle fingering: D Mixolydian, D Dorian, D Major, E Dorian, G Major.
   - Microtonal neutral thirds and sevenths inflected for expressive patos.
3. **Compose the Low Part (A-Part / "Tune Strophe"):**
   - Exactly 8 bars: Antecedent (bars 1–4, open cadence) + Consequent (bars 5–8, tonic closure).
   - Confined to lower/middle register (D4 to B4).
4. **Compose the High Part (B-Part / "The Turn"):**
   - Exactly 8 bars in upper register (A4 to G5) for acoustic contrast.
   - Bars 5–8 of part B quote/adapt the cadential turnaround from part A (cadential rhyme).
   - Full 32-bar cycle: `A (8) + A (8) + B (8) + B (8) = 32 bars`.
5. **Engineer Micro-Articulation & Ornamentation Profile:**
   - Physical acoustic interruptions articulate continuous airflow:
     - **Cut:** Rapid upper-finger grace note separating identical pitches or accenting onbeats.
     - **Strike / Tap:** Rapid lower-finger tap dipping pitch before returning.
     - **Long Roll:** 5-event composite (note → cut → note → strike → note) over a dotted quarter or half note.
     - **Short Roll:** Rapid strike + cut on a quarter note.
     - **Cran:** Piping ornament for low D (triple upper cut cascade: E cut → F cut → G cut onto D).
     - **Slide:** Portamento finger-slide upward into target pitch.
     - **Bowing Treble / Triplet:** Fiddle triple-bow pulse.
6. **Multi-Chorus Variation Arc (Pass 1 → Pass 2 → Pass 3):**
   - Pass 1: Plain ground statement (establishes tune identity).
   - Pass 2: Ornamental elaboration (rolls, crans, cuts, triplets at nodal points).
   - Pass 3: Rhythmic & registral variation (octave shifts, inverted cells, syncopated trebles, maximum drive).
7. **Set Transition (Medley Linking):**
   - Chain 2–4 tunes of identical meter with step/fifth key contrast (e.g., D maj → E dor → G maj).
   - Seamless segue on final beat of bar 32 into bar 1 of the next tune.

---

## 3. Real Practitioner Examples

- **Paddy Fahey (1916–2019, East Galway):** Composer of legendary un-named reels and jigs with subtle modal shifts and elegant asymmetric phrasing.
- **Ed Reavy (1897–1988, Cavan / Philadelphia):** Composed over 100 classic tunes ("The Hunter's House") featuring wide melodic arcs and structural unity between A and B parts.
- **Willie Clancy (1918–1973, Clare):** Master uilleann piper; defined Clare style with deep low-D crans and percussive regulator chords.
- **Michael Coleman (1891–1945, Sligo):** 1920s 78rpm recordings established the virtuosic, roll-heavy Sligo style globally.
- **Liz Carroll (Chicago, contemporary):** All-Ireland champion fiddler and composer ("The Musical Priest", "Lost in the Loop") pushing rhythmic syncopation within traditional bounds.

---

## 4. UnitMatrix Mapping (Voices & Sections)

**Layer:** `concrete (target when implemented)`

### Matrix Allocation:
- **Voice 0 (Skeletal Melody Spine):** Core unornamented tune melody. Invariant structural spine and pitch reference.
- **Voice 1 (Ornamented Solo / Lead Fiddle/Flute):** Realized acoustic surface with micro-ornament expansions (rolls, crans, cuts, slides, triplets) varying across section passes.
- **Voice 2 (Drone / Pipes Foundation):** Root + Fifth sustained pedal ({D2, A2} or {D3, A3}). Emulates uilleann pipe bass/tenor drones. Invariant harmonic floor.
- **Voice 3 (Bodhrán / Percussive Pulse):** Motoric rhythmic driver; syncopated tipper strokes (4/4 reels or 6/8 jigs) with triplet roll accents at section transitions.
- **Voice 4 (Harmonic Comping / Bouzouki DADGAD):** Sparse modal chord strikes; emphasizes open fifths and flat-seventh step changes (I–♭VII).

### Sections (One 32-Bar Chorus):
- **Section 0 (`A1`):** Bars 1–8. Low register statement, straight phrasing, minimal ornaments.
- **Section 1 (`A2`):** Bars 9–16. Low register repeat, rolls and cuts introduced.
- **Section 2 (`B1`):** Bars 17–24. "The Turn" (high register ascent), melodic contrast.
- **Section 3 (`B2`):** Bars 25–32. High register repeat + cadential turnaround rhyming with Section 1. Peak ornamental density.

---

## 5. Table Row Added to `human_methods_db.md`

```markdown
| **HC-039** | human (→concrete) | Irish Traditional Dance Tune Setting & Ornamentation Craft (AABB Binary Form + Regional Dialect) | Irish Traditional Music (Ceol Dúchais na hÉireann) — Ireland, ~17th c.–present (Sligo, Clare, Donegal, East Galway lineages) | STRUCTURE, RHYTHM, PITCH, TEXTURE | Select tune type (reel 4/4, jig 6/8, hornpipe swung 4/4) → fix modal center (D mixolydian/dorian/major, pipe gamut) → compose low 8-bar A-part (antecedent + consequent to open/closed cadences) → compose high 8-bar B-part "the turn" (contrasting leap + cadential rhyme with A-part tail) → repeat each to form 32-bar AABB cycle → articulate continuous air stream using acoustic micro-ornaments (cuts, strikes, 5-event long rolls, piping crans on low D, slides, fiddle trebles) → execute 3-pass variation arc (plain ground → ornamental elaboration → syncopated variation) → link 2–4 tunes into medley set with key shifts | Voice 0 = skeletal melody spine (unornamented core tune, invariant pitch anchor). Voice 1 = ornamented lead fiddle/flute (realized acoustic surface with roll/cran/cut expansions, density rises per pass). Voice 2 = pipe drone foundation (sustained root+fifth pedal, invariant harmonic floor). Voice 3 = bodhrán pulse (motoric 4/4 or 6/8 tipper groove, barrúl roll at section turns). Voice 4 = modal comping (bouzouki DADGAD open-fifth vamps, I–♭VII modal shifts). Sections = A1 (bars 1–8 plain low) → A2 (bars 9–16 ornamented low) → B1 (bars 17–24 high turn) → B2 (bars 25–32 high + cadential rhyme). Rules: AABB metric grid (8 bars/section, 32 bars/chorus zero-drift), modal scale constraint (mixolydian/dorian/ionian), roll-expansion formula, cut-separation between identical notes, register partition (A low vs B high), cadential rhyme, drone invariance. | Paddy Fahey (un-named master reels/jigs), Ed Reavy ("The Hunter's House"), Willie Clancy (Clare piping & crans), Michael Coleman (Sligo fiddle virtuosity), Liz Carroll (contemporary tune craft) | ✅ Documented |
```

---

## 6. Next Free ID
- **Next Free ID:** `HC-040`
