# HC-079 — Musique Concrète Tape-Music Composition: Studio Montage of Sound Objects (Collect → Reduced Listening → Transform → Splice → Mix / Spatialise)

**Method ID:** HC-079
**Layer:** `concrete (target when implemented)` — every element is an *event placed on a tick timeline*: sound-object onsets/durations as cells, transposition as pitch (speed ratio maps 1:1 to pitch shift), looping as repetition cells, reversal as retrograde, splicing as section boundaries, micromontage as event clusters at subdivision scale, filter bands as register constraints, spatialisation as diffusion tags. Realized directly as UnitMatrix voices (object streams) × sections (montage blocks) — no abstract generative layer.
**Tradition:** French electroacoustic *musique concrète* — Pierre Schaeffer's Studio d'Essai / Club d'Essai (Radiodiffusion Nationale/RTF, Paris, 1942–48), GRMC (1951) → GRM (1958) at ORTF/INA; Schaeffer, Pierre Henry, Luc Ferrari, Bernard Parmegiani, François Bayle, Michel Chion; parallel global lineages — Halim El-Dabh (Cairo, 1944), John Cage (USA), and the pop/hip-hop sampling descendants (Beatles, Pink Floyd, Grandmaster Flash, Bomb Squad, John Oswald, Art of Noise, Matmos).
**Primary elements:** TEXTURE (layered sound-object streams — the defining craft), STRUCTURE (montage-timeline form: exposition → transformation → intercut → accumulation → closure), RHYTHM (splicing, loops, micromontage, delay/accumulation), PITCH (transposition via playback speed, filter bands as register); HARMONY is deliberately absent — no functional harmony, vertical sonorities are emergent.

---

## 1. What the method is

**Musique concrète** ("concrete music") is composition from *recorded sound as raw material*: locomotive brakes, voices, pots and pans, bird song, radio fragments — captured on disc or tape, transformed, spliced, and arranged into a fixed montage. Schaeffer's own definition (1949): instead of "notating musical ideas on paper with the symbols of solfege and entrusting their realization to well-known instruments, the question was to **collect concrete sounds, wherever they came from, and to abstract the musical values they were potentially containing**."

The method has three pillars:

1. **The sound object (*l'objet sonore*)** — the primary unit. Not a written note, but a *recorded event* judged for its own sonic qualities. Schaeffer's *Traité des objets musicaux* (1966) + the companion *Le solfège de l'objet sonore* records classify objects by **envelope morphology** (duration, attack, body, decay, iteration, "facture" — the material/energetic profile) — a typology the composer uses to *know what they are working with* before arranging it.
2. **Acousmatic listening** — hearing a sound *without seeing its cause* (Schaeffer borrowed the term from Pythagoras, whose pupils listened from behind a curtain). Separating the object from its source identity is what lets a train brake become a *rhythm*, a voice become a *timbre*.
3. **Reduced listening (*écoute réduite*)** — the composer's evaluative habit: listen to the object *for itself* (its pitch contour, its envelope, its grain), not for what made it. Schaeffer's "do and listen" (*faire et écouter*) was the GRM pedagogy — practice first, theory extracted from practice.

The human method in one line: **record/collect sound objects → listen acousmatically and classify them (typology) → transform them on the machine (speed/transposition, reversal, loop, filter, splice) → judge each result by reduced listening → montage the kept objects into a timeline (alternation, accumulation, silence) → mix and spatialise → fix the whole thing as a work of fixed media.**

Why this is *craft*, not DSP or algorithm: the machines are *instruments played by hand* — a stylus held over a groove to extract a sample ("delicate manipulation"), a razor blade cutting tape at "micrometric junctions", a slider sweeping the sliding phonogène. Every transform is auditioned by ear and kept or rejected on musical grounds. Schaeffer explicitly *opposed* the synthesiser that pre-defines values, because it violated his principle of "**making through listening**" — the material must be discovered, not preconceived.

---

## 2. Why this is not an algorithm

- **The object is found, not specified.** The composer cannot predict the musical value of a recording until they *hear it* (the 1948 Études began as "research into noises"). The typology classifies *after the fact*; it does not generate.
- **Transformation is auditioned, not computed.** The phonogène changes pitch *and* duration *and* attack character *and* spectral distribution together (speed ratio affects all four) — the composer sweeps through speeds and *chooses by ear* which version "works" in context. The 1963 universal phonogène dissociated pitch from time (Springer temporal regulator) — an option, not a default.
- **The form is a montage judgment.** Where to splice, how long to hold an object, when to let silence in — these are editorial decisions (Schaeffer came from radio and cinema; montage is the substrate). Two composers given the same tape library produce unrelated pieces.
- **The acousmatic gate is a perceptual decision.** Whether an object still "carries" after heavy filtering, or whether a transformed sound has *lost* its musical identity, is decided by the composer's ear — the reduced-listening test is a human gate, not a measurable objective function.
- **It is a historical, socially-embedded practice.** Born of wartime radio studio equipment (shellac players, mixing desks, mechanical reverb), formalized in *A la recherche d'une musique concrète* (1952) and the *Traité* (1966), diffused into popular music via the Beatles' tape experiments and hip-hop's turntable/sampler lineage. The craft is inseparable from its tools and its moment.

---

## 3. Craft procedure, step by step

### Step 0 — Equip the studio (the human instrumentarium)
The 1948 radio studio: shellac record players (forward/reverse, fixed speed ratios), a shellac recorder, a mixing desk with rotary potentiometers, mechanical reverberation (metal plate/springs), third-octave and high/low-pass filter banks, microphones. From 1949–52: magnetic tape (splicing, continuous speed variation). From 1953: the **phonogènes** (chromatic keyboard-controlled; sliding/continuous; 1963 universal with pitch/time dissociation), the **morphophone** (a 50 cm loop disk with ten playback heads — delays, filtering, feedback, reverberation, continuous sounds), the **three-track tape recorder** (three synchronised tapes — first polyphonic conception), the **potentiomètre d'espace** (hand-held coil steering a sound across four loudspeakers, 1951), later the Coupigny modular synthesiser + Studio 54 mixing desk (1970) and the **Acousmonium** (1974 — 50–100 loudspeakers played live like an orchestra, "sound diffusion").

### Step 1 — Collect the material
Record whatever the ear proposes: trains (*Étude aux chemins de fer*), pots and pans, voices, instruments, environmental sound. In later practice (Ferrari's *Presque rien*), the microphone itself becomes the compositional act — a fixed, unedited *frame* of a real place recorded at one sitting.

### Step 2 — Listen acousmatically; classify by typology
Hear the object without its cause; name its envelope morphology (impulse? sustained? iterative? complex mass-form?), its duration class, its attack/body/decay profile. This is the "solfège" of the material — the composer's vocabulary for knowing what they hold.

### Step 3 — Transform on the machine (each auditioned by reduced listening)
- **Transposition / speed change** (phonogène): reading faster or slower shifts pitch and length together (ratio-proportional), sharpens or dislocates the attack, re-weights the spectrum. *La voile d'Orphée* (Henry, 1953) opens with a long sliding-phonogène glissando symbolising Orpheus's veil descending into hell.
- **Reversal**: playing backwards (a shellac/tape staple; later the Beatles' "Rain"/"Tomorrow Never Knows" vocal).
- **Looping**: skilled splices create fixed-period repeats; the morphophone stacks up to ten delayed, individually-filtered repeats with feedback.
- **Filtering**: third-octave or HP/LP banks eliminate frequency regions, keeping "some trace of the original" while altering it "often beyond recognition".
- **Sample extraction**: the hand-held stylus letting a disc play only a tiny segment — used throughout *Symphonie pour un homme seul*.

### Step 4 — Splice and montage
With tape, "axe-cut junctions" give way to **micrometric junctions**; the composer edits fragments together, including **micromontage** — very small fragments spliced into new composite sounds or large-scale structures. This is the cinema-style editorial heart of the method: cutting, juxtaposing, intercutting object families, shaping density and silence.

### Step 5 — Mix and spatialise
Route object streams through the desk (gain control per source), send through reverb/filters, and — in performance — steer material across the loudspeaker array (potentiomètre d'espace, then the Acousmonium diffusion console). Space becomes an orchestrational dimension: "an orchestration of the acoustic image" (Bayle).

### Step 6 — Fix the work
The composition is the *tape itself* — fixed media. No score in the traditional sense; the work is the realised montage, reproducible by replaying it (later: spatialised *diffusion* concerts).

### Step 7 — (Transmission) Do and listen
GRM pedagogy: *faire et écouter*. Young composers learned by doing in the studio under listening-based critique; the theory (*Traité des objets musicaux*, 1966) was extracted from two decades of this practice, not imposed on it.

---

## 4. Practitioner examples

| Practitioner / work | Role in the craft |
|---|---|
| **Pierre Schaeffer** — *Cinq études de bruits* (1948; premiered 5 Oct 1948, Paris), incl. *Étude aux chemins de fer* (locomotives) and *Étude violette*; *Symphonie pour un homme seul* (1950–51, with Henry) | Founder. Invented the practice at the Studio/Club d'Essai (RTF), coined "musique concrète" (1949), wrote the theory (*A la recherche d'une musique concrète* 1952; *Traité des objets musicaux* 1966; *Le solfège de l'objet sonore* recordings). The 1951 *Symphonie* premiered with the *pupitre de relief* spatialisation system. |
| **Pierre Henry** — *Symphonie pour un homme seul* (co-composer), *La voile d'Orphée* (1953), *Timbres-durées* (1952, with Messiaen, on the three-track recorder), *Messe pour le temps présent* (1967, incl. "Psyché Rock"), *Variations pour une porte et un soupir* (1963) | The virtuoso of the GRMC/GRM studio: sample extraction, sliding phonogène glissandi, door-and-sigh sound theatre. Called the work "plastifying music — rendering it plastic like sculpture"; his 1950s–60s output (with Béjart's choreography) carried concrète into theatre and popular awareness. |
| **Luc Ferrari** — *Presque rien n°1 — le lever du jour au bord de la mer* (1970), *Hétérozygote* (1964) | Founded "anecdotal music": the microphone as compositional frame, recording a real place over time with minimal transformation — the *opposite pole* of studio montage within the same tradition. GRM director 1962–63. |
| **Bernard Parmegiani** — *De natura sonorum* (1975), *Pop'electric* (1969), *Violostries* (1964) | Master of *continuum* and gesture; assembled pieces from pop/classical/dixieland fragments (pre-echo of plunderphonics) and from violin gestures (GRM, from 1958). |
| **François Bayle** — *Expérience acoustique* (1974), *L'Expérience acoustique* cycle; coined "**acousmatic music**" | GRM director 1966–1997; built the **Acousmonium** (1974) — the loudspeaker orchestra — and institutionalised *sound diffusion* as a live performance art of fixed media. |
| **Halim El-Dabh** — *The Expression of Zaar* (1944, Cairo) | The earliest known tape/wire-recorded composition (a zaar ceremony processed with reverb, echo, re-recording at Middle East Radio); later at Columbia-Princeton. An independent, non-French origin of the same craft. |
| **John Cage** — *Imaginary Landscape No. 1* (1939, variable-speed phonographs), *Williams Mix* (1952–53) | American branch: phonograph speeds as instruments; *Williams Mix* = tape montage whose splice lengths were chosen by chance operations (measured tape segments), showing montage as an *editorial* art that can host aleatory decisions. |
| **Olivier Messiaen / Pierre Boulez / Karlheinz Stockhausen / Iannis Xenakis / Edgard Varèse** — *Timbres-durées* (1952), Études I/II (1951), *Étude aux mille collants* (1952), *Déserts* (tape part, 1954) | The GRMC/GRM guest list — established composers importing concrète technique into their own languages (and, in Stockhausen's case, taking it back to the Cologne electronic studio, sparking the concrete/electronic rivalry). |
| **Beatles** — "Tomorrow Never Knows" (1966: tape loops, speed manipulation, reverse), "Strawberry Fields Forever", "Revolution 9" (1968) | Popularised concrète techniques inside pop; Lennon/Ono continued in *Two Virgins* (1968). |
| **Pink Floyd** — *The Dark Side of the Moon* "Money" (1973: cash-register loop in 7/4) | The concrète loop as a groove — the bridge from studio montage to rock production. |
| **Hip-hop & sampling lineage** — Grandmaster Flash (turntable montage, scratching), Bomb Squad / Public Enemy (sample collage), John Oswald (*Plexure* 1993, "plunderphonics"), Art of Noise ("Close (to the Edit)", 1984, Fairlight), Matmos (*A Chance to Cut Is a Chance to Cure*, 2001 — cosmetic-surgery sounds) | Reynolds: hip-hop as "musique concrète [gone] truant from the academy" — the same collect-transform-montage craft executed on turntables and samplers. |
| **Daniel Blumberg** — *The Brutalist* (2025, Oscar-winning score) | Contemporary film-score continuation: concrète style as dramatic material. |

**Listening:** *Étude aux chemins de fer* (1948), *Symphonie pour un homme seul* (1950–51), *La voile d'Orphée* (1953), *Presque rien n°1* (1970), *De natura sonorum* (1975), *Williams Mix* (1952–53), "Revolution 9" (1968), "Money" (1973).

---

## 5. UnitMatrix integration (Musicom engine)

**Layer:** concrete. Cells are *events on a tick timeline*: onsets, durations, pitches (transposition), velocities (mixing gains). Object identity, transform history, and spatialisation ride as cell/section attributes. The grid-quantized "perfect" export is the splice grid; the humanized export (timing/velocity jitter) carries the "hand-controlled" tape-splice feel — the engine's concrete→absolute humanizer is exactly the right tool (the morphophone and phonogène were *manual* instruments).

**Voices (rows):** each voice = one **sound-object stream** (one tape track / one object family):
- **V0 — Object stream A (identity anchor).** One object family (e.g., "locomotive": breath/brake/whistle cells) presented near-natural in the exposition; all later cells in V0 derive from this family's transposition set (speed ratios → pitch set). Anchor voice: keeps the piece's identity thread.
- **V1 — Object stream B (contrast family).** A second family (e.g., "voice fragments" or "percussion/kitchen") — montage contrast requires ≥2 families; V1 is the principal *intercut* partner of V0.
- **V2 — Object stream C (found music / noise bed, optional).** Third family for density stacking in the accumulation section (the "Revolution 9"/"Money" role — a looped, possibly pitched-down fragment).
- **V3 — Loop/delay layer.** Morphophone role: delayed repeats of V0/V1 cells (fixed delay periods, filtered repeats, feedback decay) — rhythm engine of the piece.
- **V4 — Metadata (non-sounding).** Per-cell: object-type tag (typology: impulse/sustained/iterative/complex), transform log (reverse, speed ratio, filter band, loop period), reduced-listening verdict (kept/dropped); per-section: spatialisation/diffusion tags, montage block labels.

**Sections (columns):** montage-timeline blocks:
| Section | Function |
|---|---|
| S0 Exposition | Present object families near-natural state (Schaeffer's "research into noises": objects announced as themselves) |
| S1 Transformation workshop | Phonogène workshop: transposed variants, reversals, filtered versions auditioned; object identities drift toward abstraction |
| S2 Montage A | Intercut: V0↔V1 alternation, splices at section landmarks, first loop layer (V3) enters |
| S3 Accumulation / climax | Max density: all streams layered, delay feedback builds, register spread widest, shortest splice units (micromontage) |
| S4 Closure | Decay: layers drop one by one, silence admitted, closing return to a near-natural object (the "Presque rien" breath) |

**Rules to encode:**
1. **Object-family identity** — V0 cell pitches belong to one family's transposition set (speed-ratio lattice: e.g., ratios {1, 2, 3, 4, ½, ⅔} → pitch shifts {0, +12, +19, +24, −12, −7} semitones); V1 uses a disjoint family set. No cross-family pitch borrowing.
2. **Transposition coupling** — speed-ratio transform scales duration AND pitch together (ratio-proportional); the universal-phonogène option (pitch/time dissociation) must be flagged per-cell if used.
3. **Attack-focus rule** — transformed cells keep or sharpen the attack (phonogène effect); attack-dislocated variants are licensed only in S3 (micromontage).
4. **Reverse = retrograde** — reversed cells are retrograde event sequences within the cell; onsets mirror around the cell midpoint.
5. **Loop/delay layer** — V3 repeats a source cell at fixed delay periods (morphophone delays), each repeat may be filtered (band-restricted); feedback decay = velocity fade per repeat.
6. **Montage contrast** — adjacent sections must differ in object-family mix (no two consecutive sections with identical V0/V1 weighting); ≥2 families present overall.
7. **Micromontage density cap** — in S3, minimum event duration ≥ N ticks (subdivision-scale splice limit); density (events per bar) increases monotonically from S0→S3.
8. **Silence rule** — closure admits ≥1 full section-level rest before the final object; silence is an active element (Schaeffer/radio montage).
9. **Acousmatic gate (metadata)** — every cell carries a reduced-listening verdict (kept/dropped) in V4; dropped cells are excluded at export. The gate is the composer's ear — encoded as a human review pass, not an objective function.
10. **Spatialisation tags** — per-section diffusion tags (front/back/above; the potentiomètre d'espace / Acousmonium geometry) recorded in V4 for the renderer; pan alternation between sections.
11. **Zero-drift** — all voices end at each section's terminal landmark; `validate()` must pass; grid export = splice grid, humanized export = hand-splice feel (dual-export contract).

**Distinct in engine terms:** HC-023 (spectral listening) analyses a *performed* sound to derive orchestration for *live instruments*; HC-079 composes *with recorded objects* by montage. HC-024 (graphic score) is indeterminate notation for live performers; HC-079 is fixed media realized in the studio. HC-063 (improvisation-to-notation) captures a live gesture to paper; HC-079's "performance" is the tape machine and the diffusion desk. HC-008 (minimalism) uses *composed* pitch cells with phase/additive process; HC-079 uses *found* sound objects with splice/loop/transposition operators — process is editorial, not generative.

---

## 6. Deduplication note

Checked the neighbours: HC-023 (spectral listening — analysis of instrumental sound for orchestration), HC-024 (graphic score — indeterminate live notation), HC-063 (improvisation-to-notation — gesture capture), HC-008 (minimalist phase/additive — composed cells + process), HC-062 (twelve-tone serialism — pitch-row organization). None covers the **studio montage of recorded sound objects** as a compositional method: Schaeffer's collect → reduced-listen/classify → transform (phonogène/morphophone) → splice (micromontage) → mix/spatialise workflow, and its fixed-media craft tradition. This entry is the Electronic-tradition slot in the rotation and is kept strictly on that human studio craft.
