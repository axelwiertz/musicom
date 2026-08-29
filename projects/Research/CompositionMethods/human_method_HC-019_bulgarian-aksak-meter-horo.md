# HC-019 — Bulgarian Aksak Asymmetric-Meter Horo Construction

**Method ID:** HC-019
**Tradition / Culture:** Bulgarian folk dance music — Thrace / Shop / Macedonia ethnoregions, Bulgaria; rooted in Ottoman-Turkish *aksak* ("limping") additive-meter theory (Brăiloiu 1951). Related UNESCO element: "Bistritsa Babi, archaic polyphony, dances and rituals from the Shoplouk region" (2008).
**Primary Elements:** RHYTHM, PITCH, STRUCTURE, TEXTURE
**Status:** ✅ Documented

---

## 1. What the method is

Bulgarian aksak horo composition is the craft of building a melody (and its accompanying drone/drum layer) **inside an asymmetric additive meter** — a repeating cycle of unequal "quick" (2-unit) and "slow" (3-unit) beats, e.g. 2+3 (5), 2+2+3 (7), 2+2+2+3 (9), 2+2+3+2+2 (11), 2+2+2+2+2+3 (13), 2+2+2+2+3+2+2 (15). The name *aksak* literally means "limping" or "stumbling": to an outsider the cycle sounds like it misses a beat, but to a trained dancer it is a **regular, felt cycle of unequal pulses**, and the whole art of the composer is to make a singable modal phrase sit *naturally* inside a meter whose beats are not all the same length.

Crucially, the meter is **socially fixed by the dance**, not invented by the composer. Each horo (line dance) type has a fixed aksak grouping and a fixed footwork pattern; the composer's job is to hang a melody, drone, and drum part on that invariant skeleton so that the accents of the tune match the "long" beats where the dancers' weight lands.

## 2. Craft procedure — how a human actually does it (step by step)

1. **Fix the aksak cycle.** Choose the dance/metre type; each has a canonical long-short grouping:
   - **Paidushko** (5): 2+3
   - **Račenica** (7): 2+2+3 (also 3+2+2, 2+3+2 as *lesnoto/četvorno* variants)
   - **Daichovo** (9): 2+2+2+3 (also 2+2+3+2, 3+2+2+2)
   - **Kopanitsa / Gankino** (11): 2+2+3+2+2 (Shop vs. northern regional name)
   - **Elenino horo** (13): 2+2+2+2+2+3; **Krivo Sadovsko horo** (13): 2+2+2+3+2+2
   - **Bučimiš** (15): 2+2+2+2+3+2+2
   - Composite forms: **Jove Malaj Mome** (18) = (3+2+2)+(2+2+3+2+2); **Sandansko Horo** (22); **Sedi Donka** (25).
2. **Internalize the dance footwork.** The stepping pattern *is* the composition skeleton: the "slow" (3) beat carries the dancer's weight/accent, the "quick" (2) beats are light. The composer (usually a player who is also a dancer) knows where the weight falls and composes toward it.
3. **Fix the modal pitch set.** Bulgarian melody uses diatonic/modal scales (Dorian, Aeolian, Phrygian, Mixolydian flavours with chromatic inflections and a raised leading-tone "soft" tendency), a **narrow range**, and largely conjunct motion. There is **no functional harmony** — the pitch material is monophonic-with-drone.
4. **Lay the drone (ison) + drum spine.** A held vocal or gaida/bagpipe drone on the tonic (+5th), plus the **tapan** (large double-headed drum) marking the cycle: a low "boom" on the long beat, light "tick"/rests on the quick beats. This layer never stops and never changes.
5. **Compose the melody (pesen).** Write a short modal phrase of **one or two cycles**, placing its strongest syllable/note and any melodic accent on the long beat(s). The phrase is strophic — it repeats once per cycle so the irregularity becomes predictable and singable.
6. **Layer lead instruments.** Gaida (bagpipe: melody + drone in one), kaval (end-blown flute), gadulka (bowed fiddle), tambura (long-necked lute for rhythm-harmony). The lead states the tune; a second voice may answer in call-and-response or join in heterophony.
7. **Ornament.** Add trills, mordents, grace-note clusters, and vibrato/gadulkа slides at cadential notes and on the long beats — the ornamentation is idiomatic, not improvised invention.
8. **Set the form.** Strophic: Intro (instrumental) → strophe 1 → instrumental ritornello → strophe 2 → … → climax. Many horos are "called" dances (leader signals step changes); in fixed compositions the macro-form is a **suite of contrasting aksak cycles** (one meter per dance) or an accelerando to a fast close.
9. **Check the accent-lock.** Listen: does the tune's downbeat weight land on the long beat every cycle? If a phrase fights the grouping (e.g. the "1" falls on a quick beat), the melody is re-phrased — the cycle is never altered to fit a tune.

## 3. Real practitioner examples

| Practitioner | Work / Role | Craft significance |
| :--- | :--- | :--- |
| **Béla Bartók** | *Mikrokosmos Vol. VI*, "Six Dances in Bulgarian Rhythm" (Nos. 148–153, 1926–39) | Abstracted the aksak groupings (4+2+3, 2+2+3, 2+3, 3+2+3, 2+2+2+3, 3+3+2) into Western bar notation while preserving the long-short accent pattern — the canonical "outsider" proof that aksak is transferable craft, not a local accident. |
| **Filip Kutev** | Founder, State Ensemble for Folk Songs and Dances (Philip Kutev Ensemble) | Systematized and harmonized (light polyphonic arrangement) the regional horo repertoire for concert stage; codified the drone + melody + tapan layering. |
| **Le Mystère des Voix Bulgares** | Bulgarian State Television Female Vocal Choir — "Polegnala e Todora", "Erghen Diado" (Daichovo horo), "Kaval Sviri" | The world-facing proof of asymmetric-meter vocal polyphony: open-voiced drone + ornamented lead, sung in aksak cycles with perfect accent-lock. |
| **Ivo Papazov-Ibryama** | Bulgarian wedding-music clarinetist (*orchestar*) | Pushed aksak horo metres into virtuosic improvisation at extreme tempos; demonstrated the meter's elasticity under fast ornament. |
| **Theodossi Spassov** | Kaval player | Contemporary kaval master; the idiomatic ornamentation layer (trills, overblown harmonics) over the drone. |
| **Kostadin Varimezov** | Gaida (bagpipe) | Master of simultaneous melody + drone on one instrument — the self-contained aksak voice. |
| **Petko Staynov** | Symphonic composer ("Thracian Dances") | Brought aksak rhythm into Western art music (parallel to Bartók), arranging horo tunes for orchestra. |

## 4. Mapping to the Musicom engine (Musical Elements Framework)

### RHYTHM (primary element)
- The aksak cycle is a **boolean accent mask over unequal beat lengths** — encodable as a per-beat subdivision-length vector, e.g. Račenica = `[2,2,3]`, Daichovo = `[2,2,2,3]`, Kopanitsa = `[2,2,3,2,2]`. This is a **Rules-Based (deterministic)** layer: the vector is invariant and every other voice aligns to it.
- Engine note: this requires **per-beat subdivision lengths**, not a single fixed `ticks_per_beat`. The "slow" beat must be a *genuinely longer duration* (e.g. 3 subdivisions), not 2 subdivisions with an accent — otherwise the groove is destroyed.

### PITCH
- Narrow-range modal set (Dorian/Aeolian/Phrygian/Mixolydian with inflection), conjunct motion, no chromaticism beyond idiom. Encodable as a **pitch-class constraint set** + range window + stepwise-motion bias.
- Ornamentation = grace-note/trill/mordent events at cadential points (deterministic decoration rules, not random).

### HARMONY
- **None (functional).** A single drone (tonic + 5th) is the only vertical constant. Encodable as a **drone voice** holding scale degrees 0 and 7; any incidental vertical sonority is emergent, never a progression.

### STRUCTURE
- Strophic: the melody phrase = 1–2 aksak cycles, repeated; macro-form = Intro → Strophe → Ritornello → Strophe' → Climax (accelerando) → Close. Bartók's suite alternative: one aksak cycle per movement.
- "Called dance" variant: section changes are triggered by a leader signal, not by bar count.

### TEXTURE
- **Drone + ornamented lead + tapan mark** = a three-layer stratified texture: invariant drone (Voice), invariant cycle-mark (tapan), and the lead's ornamented strophic phrase. Optional heterophonic doubling/call-response second voice.

## 5. UnitMatrix fill (Voices & Sections)

**Voices (4-voice matrix, small ensemble template):**

| Voice | Role | Content | Rules |
| :--- | :--- | :--- | :--- |
| Voice 0 | **Tapan (drum)** | Marks the aksak cycle: low "boom" on the long (3) beat, light tick/rest on quick (2) beats | Never varies; boolean cycle mask = the meter spine |
| Voice 1 | **Lead melody (gaida/kaval/gadulka)** | Strophic modal phrase, 1–2 cycles long, accent on long beats | Mode-constrained; conjunct; onsets/accents target long beats; repeats per cycle |
| Voice 2 | **Vocal / heterophonic answer** | Doubles or answers Voice 1 (call-response, parallel/heterophony) | Never contradicts the cycle; ornamentation idiomatic; joins on cadential notes |
| Voice 3 | **Drone (ison) + tambura** | Held tonic + 5th (and rhythmic strum on tambura) | Invariant pedal; no harmonic function |

**Sections (5-section matrix):**

| Section | Content | Density |
| :--- | :--- | :--- |
| S0 Intro | Instrumental statement of the tune + drone + tapan | medium |
| S1 Strophe 1 | Full vocal/lead melody over drone + tapan | medium |
| S2 Ritornello | Instrumental interlude (lead + ornament) | medium |
| S3 Strophe 2 (climax) | Repeated melody, higher ornament, accelerando | rising → high |
| S4 Close | Cadence on the long beat, drone resolves to tonic | resolves |

**Encodable rule set (summary):**
1. `aksak_cycle_invariant`: Voice 0's subdivision-length vector is constant across all sections; never altered to fit a tune.
2. `long_beat_accent`: melodic onsets/accents in Voices 1–2 target the "slow" (3) beats of the cycle.
3. `mode_constraint`: Voice 1 pitch classes ∈ modal set, range ≤ ~octave, stepwise-biased motion.
4. `drone_invariant`: Voice 3 holds scale degrees 0 (and 7) throughout; no harmonic progression.
5. `phrase_cycle_alignment`: phrase length ∈ {1, 2} cycles (strophic repetition).
6. `ornamentation`: grace/trill/mordent events allowed only at cadential notes and long beats.
7. `accelerando_climax`: tempo + ornament density increase monotonically into the coda.
8. `no_functional_harmony`: vertical sonorities are emergent (drone + passing notes), never treated as chord syntax.

## 6. Quirks / pitfalls

- **"Limping" is the point.** Outsiders hear aksak as a mistake (a dropped beat); trained dancers feel it as a *regular* cycle of unequal beats. A composer who "corrects" the meter to even subdivisions has destroyed the dance.
- **The grouping order matters, not just the total.** 7/8 = 2+2+3 (Račenica) is a *different dance* from 3+2+2 and from 2+3+2. Copying the time signature without the internal long-short order produces the wrong groove. In the engine this means the **subdivision-length vector** is the ground truth, not a bare numerator.
- **Never quantize the slow beat away.** Rendering aksak on an even MIDI grid turns 3 into "2+accent", which kills the groove. The "slow" beat must be a genuinely longer duration (see UnitMatrix note on per-beat subdivision lengths).
- **The dance fixes the meter, not the composer.** Unlike Western art music where the composer chooses a meter freely, in horo the meter is socially bound to the dance type — the composer composes *into* a fixed cycle.
- **No harmony to hide behind.** There is no chord progression; the whole piece is melody + drone + drum. Melodic quality and accent-lock carry 100% of the musical interest.
- **Accelerando ≠ free tempo.** The climax accelerando happens *within* the fixed cycle grouping — the beats speed up together but keep their 2:3 internal ratios.
