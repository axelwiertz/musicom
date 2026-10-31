# report_HC-079 — Musique Concrète Tape-Music Composition: Studio Montage of Sound Objects

**Job:** `daily-human-composition-research` · **Date:** 2026-10-30 · **Method ID:** HC-079
**Detail file:** `human_method_HC-079_musique-concrete-tape-montage.md`

---

## 1. Header

| Field | Value |
|---|---|
| **Method name** | Musique Concrète Tape-Music Composition — Studio Montage of Sound Objects (Collect → Reduced Listening → Transform → Splice → Mix/Spatialise; Schaeffer's *faire et écouter*) |
| **Tradition** | French electroacoustic *musique concrète* — Pierre Schaeffer, Studio d'Essai / Club d'Essai (Radiodiffusion Nationale/RTF, Paris, 1942–48), GRMC (1951) → GRM/INA (1958–); Pierre Henry, Luc Ferrari, Bernard Parmegiani, François Bayle, Michel Chion; parallel lineages: Halim El-Dabh (Cairo 1944), John Cage (USA), Beatles / Pink Floyd, hip-hop sampling (Grandmaster Flash, Bomb Squad, John Oswald, Art of Noise, Matmos). |
| **Layer** | `concrete (target when implemented)` — every element is an *event on a tick timeline*: sound-object onsets/durations as cells, transposition as pitch (speed ratio → pitch shift 1:1), reversal as retrograde, looping as repetition cells, splicing as section boundaries, micromontage as subdivision-scale event clusters, filter bands as register constraints, spatialisation as diffusion tags. Realized directly as UnitMatrix voices (object streams) × sections (montage blocks) — no abstract generative layer. |
| **Primary elements** | TEXTURE (layered sound-object streams — the defining craft), STRUCTURE (montage-timeline form: exposition → transformation → intercut → accumulation → closure), RHYTHM (splicing, loops, micromontage, delay/accumulation), PITCH (transposition via playback speed; filter bands as register). HARMONY deliberately absent — no functional harmony; vertical sonorities emergent. |
| **Why human craft, not algorithm** | The object is *found, not specified* — musical value cannot be predicted before hearing (1948 Études began as "research into noises"); typology classifies after the fact, it does not generate. Transformation is *auditioned, not computed* — speed change couples pitch+duration+attack+spectrum, and the composer sweeps and chooses by ear. The form is an *editorial judgment* (Schaeffer came from radio/cinema; montage is the substrate). The *acousmatic gate* (reduced listening: does the object still carry musical value?) is a perceptual, human decision — not an objective function. Schaeffer explicitly opposed synthesis that pre-defines values because it violated "making through listening". Historically embedded in wartime radio studio equipment and its social moment. |
| **Research sources (fetched 2026-10-30)** | Wikipedia extracts (REST + action API, UA-tagged, rate-limited retries): *Musique concrète* (full article, 39 KB — Schaeffer's 1949 definition quote, Studio d'Essai 1942 / Club d'Essai 1946 / Cinq études de bruits premiered 5 Oct 1948 / GRMC 1951 / GRM 1958 / Traité des objets musicaux 1966 / Le solfège de l'objet sonore; technology: shellac players, mixing desk, mechanical reverb, filter banks; tape 1949–52, splicing axe-cut→micrometric junctions, micromontage; phonogène chromatic (Tolana) / sliding (SAREG) / universal 1963 (Springer temporal regulator, pitch/time dissociation); morphophone (10 heads, delays/filtering/feedback); three-track recorder (Timbres-durées 1952); potentiomètre d'espace / pupitre de relief (1951 Symphonie spatialisation); Coupigny synthesiser + Studio 54 desk (1970); Acousmonium (1974, Bayle, 50–100 speakers, sound diffusion); "do and listen" pedagogy; Schaeffer vs preconceived synthesis; popular-music lineage: Beatles Tomorrow Never Knows/Revolution 9, Pink Floyd Money, Kraftwerk Autobahn, hip-hop Grandmaster Flash/Bomb Squad, Oswald plunderphonics Plexure 1993, Art of Noise, Matmos, The Brutalist 2025), *Pierre Schaeffer*, *Sound object* (coined in Traité 1966), *Pierre Henry*, *Luc Ferrari*, *François Bayle* (coined "acousmatic music"), *Bernard Parmegiani*, *William Burroughs* (cut-up parallel). |
| **Distinct from existing HC methods** | See §2 (dedup) below. |

---

## 2. What the method is

**Musique concrète** = composition from *recorded sound as raw material* — locomotive brakes, voices, kitchenware, birdsong, radio fragments — captured on disc or tape, transformed, spliced, arranged into a fixed montage. Schaeffer (1949): "instead of notating musical ideas on paper with the symbols of solfege and entrusting their realization to well-known instruments, the question was to **collect concrete sounds, wherever they came from, and to abstract the musical values they were potentially containing**."

Three pillars:

1. **The sound object (*l'objet sonore*)** — the primary unit: a recorded event judged for its own sonic qualities. *Traité des objets musicaux* (1966) + *Le solfège de l'objet sonore* classify objects by **envelope morphology** (duration, attack, body, decay, iteration, "facture" — material/energetic profile): the composer's vocabulary for knowing what they hold.
2. **Acousmatic listening** — hearing a sound *without seeing its cause* (Pythagoras's curtain; Schaeffer's definition: "a sound that one hears without seeing the causes behind it"). Separation from source identity lets a train brake become a *rhythm*, a voice a *timbre*.
3. **Reduced listening (*écoute réduite*)** — judging the object *for itself* (pitch contour, envelope, grain), not for its origin. GRM pedagogy = **"do and listen"** (*faire et écouter*): practice first, theory extracted from practice.

**One-line method:** record/collect sound objects → listen acousmatically & classify (typology) → transform on the machine (speed/transposition, reversal, loop, filter, splice) → judge each result by reduced listening → montage the kept objects into a timeline (alternation, accumulation, silence) → mix & spatialise → fix the whole as a fixed-media work.

**Human method in one line (engine-friendly):** every object is an event on the timeline; every transform is a cell operation; the composer's ear is the gate at every step.

---

## 3. Craft procedure in detail

### Step 0 — Equip the studio (the human instrumentarium)
1948 radio studio: shellac record players (forward/reverse, fixed speed ratios), shellac recorder, mixing desk (rotary potentiometers), mechanical reverberation (plate/springs), third-octave + high/low-pass filter banks, microphones. 1949–52: magnetic tape (splicing, continuous speed variation). 1953+: **phonogènes** — chromatic (keyboard-controlled, short sounds only, multiple capstans), sliding (continuous speed rod; the *La voile d'Orphée* glissando), universal 1963 (Springer temporal regulator: pitch dissociated from time — time-stretch/harmonise ancestors). **Morphophone**: 50 cm loop disk, 10 movable playback heads + record/erase heads — delayed repeats, per-head filtering, feedback loops, artificial reverb, continuous sounds. **Three-track tape recorder**: three synchronised tapes (first polyphonic conception; *Timbres-durées* 1952). **Potentiomètre d'espace / pupitre de relief** (1951): hand-held coil steers a monophonic source across four loudspeakers (2 front, 1 rear, 1 overhead). 1970: **Coupigny synthesiser + Studio 54 desk** (24 tracks, modular, intermodulation-focused, no keyboard — designed so the *composer alone* could run it, against union three-operator rules). 1974: **Acousmonium** — Bayle's 50–100 loudspeaker "orchestra of loudspeakers", played live via diffusion console.

### Step 1 — Collect the material
Record whatever the ear proposes: trains (*Étude aux chemins de fer*), pots, voices, instruments, environment. In later practice (Ferrari's *Presque rien*), the microphone *is* the compositional act — a fixed, unedited frame of a real place, one sitting.

### Step 2 — Listen acousmatically; classify by typology
Hear without the cause; name envelope morphology (impulse / sustained / iterative / complex mass-form), duration class, attack/body/decay profile. The "solfège" of the material.

### Step 3 — Transform on the machine (each auditioned by reduced listening)
- **Transposition / speed change (phonogène):** speed ratio shifts pitch AND length proportionally, sharpens or dislocates the attack, re-weights spectral distribution — four coupled changes chosen by ear.
- **Reversal:** backwards playback (shellac/tape staple; Beatles' "Rain" / "Tomorrow Never Knows" vocals).
- **Looping:** skilled splices for fixed-period repeats; morphophone stacks up to ten delayed, individually-filtered repeats with feedback.
- **Filtering:** third-octave or HP/LP banks eliminate frequency regions — "keep some trace of the original sound but alter it often beyond recognition".
- **Sample extraction:** hand-held stylus reading a tiny disc segment — used throughout *Symphonie pour un homme seul*.

### Step 4 — Splice and montage
Tape: "axe-cut junctions" → **micrometric junctions**; edit fragments together; **micromontage** = very small fragments spliced into new composite sounds or large-scale structures. Cinema-style editorial heart: cut, juxtapose, intercut families, shape density and silence.

### Step 5 — Mix and spatialise
Route streams through the desk (independent gain per source), send through reverb/filters; in performance steer material across the array (potentiomètre d'espace → Acousmonium diffusion). Space as an orchestrational dimension — Bayle: "an 'orchestration' of the acoustic image".

### Step 6 — Fix the work
The composition IS the tape (fixed media). No score in the traditional sense; the work is the realised montage, reproducible by replay (later: spatialised *diffusion* concerts).

### Step 7 — (Transmission) Do and listen
GRM pedagogy: *faire et écouter*. Theory (*Traité*, 1966) extracted from two decades of studio practice, not imposed.

---

## 4. Practitioner examples

| Practitioner / work | Role in the craft |
|---|---|
| **Pierre Schaeffer** — *Cinq études de bruits* (1948; premiered 5 Oct 1948), incl. *Étude aux chemins de fer* (locomotives) & *Étude violette*; *Symphonie pour un homme seul* (1950–51, w/ Henry); *A la recherche d'une musique concrète* (1952); *Traité des objets musicaux* (1966) | Founder of the practice and theory; coined the term 1949; premiered spatialisation (pupitre de relief) 1951; opposed preconceived synthesis ("making through listening"). |
| **Pierre Henry** — *Symphonie pour un homme seul* (co-composer), *La voile d'Orphée* (1953; sliding-phonogène glissando), *Timbres-durées* (1952, w/ Messiaen, three-track), *Variations pour une porte et un soupir* (1963), *Messe pour le temps présent* (1967; "Psyché Rock") | The GRMC/GRM virtuoso; sample extraction, phonogène technique, "plastifying music"; carried concrète into theatre (Béjart) and pop awareness. |
| **Luc Ferrari** — *Presque rien n°1 — le lever du jour au bord de la mer* (1970), *Hétérozygote* (1964); GRM director 1962–63 | Founded "anecdotal music": microphone-as-frame, minimal transformation — the anti-montage pole inside the same tradition. |
| **Bernard Parmegiani** — *De natura sonorum* (1975), *Pop'electric* (1969), *Violostries* (1964) | Master of continuum/gesture; assembled pop/classical/dixieland fragments (pre-echo of plunderphonics); violin-gesture works. |
| **François Bayle** — *Expérience acoustique* (1974); coined "**acousmatic music**"; GRM director 1966–1997 | Built the **Acousmonium** (1974); institutionalised *sound diffusion* as live performance of fixed media. |
| **Halim El-Dabh** — *The Expression of Zaar* (1944, Cairo) | Earliest known wire-recorder composition (zaar ceremony processed w/ reverb, echo, re-recording); independent non-French origin. |
| **John Cage** — *Imaginary Landscape No. 1* (1939, variable-speed phonographs), *Williams Mix* (1952–53) | American branch; *Williams Mix* = chance-selected splice lengths on measured tape segments — montage hosting aleatory decisions. |
| **Messiaen / Boulez / Stockhausen / Xenakis / Varèse** — *Timbres-durées* (1952), Études I/II (1951), *Étude aux mille collants* (1952), *Déserts* tape part (1954) | The GRMC/GRM guest list; concrète technique imported into other languages; Stockhausen carried it to Cologne (concrete-vs-electronic rivalry). |
| **Beatles** — "Tomorrow Never Knows" (1966: loops, speed, reverse), "Strawberry Fields Forever" (1967), "Revolution 9" (1968) | Popularised concrète inside pop; Lennon/Ono continued (*Two Virgins* 1968). |
| **Pink Floyd** — *The Dark Side of the Moon* "Money" (1973: cash-register loop in 7/4) | The concrète loop as groove — bridge from studio montage to rock production. |
| **Hip-hop & sampling lineage** — Grandmaster Flash (turntable montage, scratching), Bomb Squad / Public Enemy (sample collage), John Oswald (*Plexure* 1993, plunderphonics), Art of Noise ("Close (to the Edit)" 1984, Fairlight), Matmos (*A Chance to Cut Is a Chance to Cure* 2001, cosmetic-surgery sounds) | Reynolds: hip-hop as "musique concrète [gone] truant from the academy" — same collect-transform-montage craft on turntables/samplers. |
| **Daniel Blumberg** — *The Brutalist* (2025, Oscar-winning score) | Contemporary film-score continuation (banknote-press sounds in the French *L'affaire Bojarski* lineage too). |

**Listening:** *Étude aux chemins de fer* (1948), *Symphonie pour un homme seul* (1950–51), *La voile d'Orphée* (1953), *Presque rien n°1* (1970), *De natura sonorum* (1975), *Williams Mix* (1952–53), "Revolution 9" (1968), "Money" (1973).

---

## 5. UnitMatrix mapping (Musicom engine)

**Layer: concrete.** Cells = events on a tick timeline (onsets, durations, pitches, velocities). Grid-quantized "perfect" export = the splice grid; humanized export = hand-spliced feel (the concrete→absolute humanizer maps perfectly onto the manual morphophone/phonogène craft). Dual-export contract applies.

### Voices (rows)
| Voice | Role |
|---|---|
| **V0 — Object stream A (identity anchor)** | One object family (e.g., "locomotive": breath/brake/whistle cells). Near-natural in S0; later cells derive from this family's transposition-set lattice. Keeps the piece's identity thread. |
| **V1 — Object stream B (contrast family)** | Second family (voice fragments / kitchen percussion). Principal intercut partner of V0; montage contrast requires ≥2 families. |
| **V2 — Object stream C (found music / noise bed, optional)** | Third family for density stacking in S3 (the "Revolution 9"/"Money" role — looped, possibly pitched-down fragment). |
| **V3 — Loop/delay layer (morphophone role)** | Delayed repeats of V0/V1 cells; fixed delay periods, filtered repeats, feedback decay (velocity fade per repeat). The rhythm engine. |
| **V4 — Metadata (non-sounding)** | Per-cell: typology tag (impulse/sustained/iterative/complex), transform log (reverse, speed ratio, filter band, loop period), reduced-listening verdict (kept/dropped); per-section: spatialisation/diffusion tags, montage-block labels. |

### Sections (columns) — montage-timeline blocks
| Section | Function |
|---|---|
| S0 Exposition | Object families presented near-natural (Schaeffer's "research into noises": objects announced as themselves) |
| S1 Transformation workshop | Phonogène workshop: transposed variants, reversals, filtered versions; identities drift toward abstraction |
| S2 Montage A | Intercut V0↔V1, splices at section landmarks; first loop layer (V3) enters |
| S3 Accumulation / climax | Max density: all streams layered, delay feedback builds, widest register spread, shortest splice units (micromontage) |
| S4 Closure | Decay: layers drop one by one, silence admitted, closing return to a near-natural object (the "Presque rien" breath) |

### Rules to encode
1. **Object-family identity** — V0 pitches belong to one family's transposition set (speed-ratio lattice: ratios {1, 2, 3, 4, ½, ⅔} → semitone shifts {0, +12, +19, +24, −12, −7}); V1 uses a disjoint family set; no cross-family pitch borrowing.
2. **Transposition coupling** — speed-ratio transform scales duration AND pitch together (ratio-proportional); universal-phonogène option (pitch/time dissociation) flagged per-cell if used.
3. **Attack-focus rule** — transformed cells keep/sharpen the attack (phonogène effect); attack-dislocated variants licensed only in S3.
4. **Reverse = retrograde** — reversed cells are retrograde event sequences; onsets mirror around cell midpoint.
5. **Loop/delay layer** — V3 repeats source cells at fixed delay periods; repeats may be band-restricted (filtered); feedback decay = velocity fade.
6. **Montage contrast** — adjacent sections differ in object-family mix; ≥2 families overall.
7. **Micromontage density cap** — S3 min event duration ≥ N ticks; density (events/bar) increases monotonically S0→S3.
8. **Silence rule** — closure admits ≥1 full section-level rest before the final object; silence is an active element.
9. **Acousmatic gate** — every cell carries a reduced-listening verdict in V4 (kept/dropped); dropped cells excluded at export; the gate is a human review pass, not an objective function.
10. **Spatialisation tags** — per-section diffusion tags (front/back/above — potentiomètre/Acousmonium geometry) in V4; pan alternation between sections.
11. **Zero-drift** — all voices end at each section's terminal landmark; `validate()` must pass; dual export (perfect splice grid + humanized hand-splice).

---

## 6. Table row added

```
| HC-079 | human (→concrete) | Musique Concrète Tape-Music Composition — Studio Montage of Sound Objects (Collect → Reduced Listening → Transform → Splice → Mix/Spatialise; Schaeffer's *faire et écouter*) | French electroacoustic *musique concrète* — Pierre Schaeffer, Studio d'Essai/Club d'Essai (RTF Paris, 1942–48), GRMC (1951) → GRM/INA (1958–); Pierre Henry, Luc Ferrari, Bernard Parmegiani, François Bayle, Michel Chion; parallel lineages: Halim El-Dabh (Cairo 1944), John Cage (USA), Beatles/Pink Floyd, hip-hop sampling (Grandmaster Flash, Bomb Squad, John Oswald, Matmos) | TEXTURE, STRUCTURE, RHYTHM, PITCH | Equip the studio (shellac players, tape, phonogènes, morphophone, mixing desk, filters, reverb) → collect recorded sound objects (train, voice, pots, field recording) → listen acousmatically (hear without the cause) & classify by envelope typology (*objet sonore*, Traité 1966) → transform on the machine, each result auditioned by reduced listening: transposition/speed change (chromatic/sliding/universal phonogène — pitch+length+attack+spectrum coupled), reversal, looping (morphophone 10-head delays/filtering/feedback), filtering (third-octave & HP/LP banks), hand-stylus sample extraction → splice & montage on tape (axe-cut → micrometric junctions; micromontage of tiny fragments) → mix & spatialise (potentiomètre d'espace 1951, Acousmonium 1974 diffusion) → fix the work as fixed media (score = the tape itself) | Voice 0 = object stream A (identity anchor: one object family, transposition-set lattice). Voice 1 = object stream B (contrast family, intercut partner). Voice 2 = object stream C / found-music loop (density stacking). Voice 3 = loop/delay layer (morphophone repeats, filtered, feedback decay). Voice 4 = metadata (typology tag, transform log, reduced-listening verdict, spatialisation tags). Sections = montage blocks (S0 Exposition near-natural → S1 Transformation workshop → S2 Montage A intercut → S3 Accumulation/climax micromontage → S4 Closure with silence). Rules: object-family identity, transposition coupling (speed ratio = pitch+duration), reverse=retrograde, loop-delay periods, montage contrast (≥2 families, adjacent-section mix differs), micromontage density cap, monotonic density arc, silence rule, acousmatic gate (kept/dropped verdict), spatialisation alternation, zero-drift validate + dual export (splice grid / hand-spliced humanized) | Pierre Schaeffer (*Cinq études de bruits* 1948, *Symphonie pour un homme seul* 1950–51), Pierre Henry (*La voile d'Orphée* 1953, *Messe pour le temps présent* 1967), Luc Ferrari (*Presque rien n°1* 1970), Bernard Parmegiani (*De natura sonorum* 1975), François Bayle (Acousmonium, *Expérience acoustique* 1974), Halim El-Dabh (*The Expression of Zaar* 1944), John Cage (*Williams Mix* 1952–53), Beatles (*Revolution 9* 1968), Pink Floyd (*Money* 1973), Daniel Blumberg (*The Brutalist* 2025) | ✅ Documented |
```

Appended as line 85 of `human_methods_db.md`. Verified: 79 rows, IDs contiguous 1–79, no duplicates.

---

## 7. Verification

- `grep HC-079 human_method_HC-079_musique-concrete-tape-montage.md` → present (title, layer, voices/sections, rules, dedup).
- `grep HC-079 human_methods_db.md` → present (line 85, one row).
- `grep HC-079 report_HC-079.md` → present.
- DB integrity: 79 unique IDs, contiguous 1–79, max 79 → **next free ID = HC-080**.

---

## 8. Quirks & pitfalls

- **Terminology trap:** "concrète" vs "elektronische Musik" (Cologne) — recorded-object vs synthesized-signal origin. The distinction blurred after the 1950s; the *craft* here is the recorded-object montage workflow, not synthesis (that is DSP/electronic generation, out of scope).
- **Harmony is absent by design.** Do not force chord frameworks — vertical sonorities are emergent; the elements that matter are TEXTURE/STRUCTURE/RHYTHM/PITCH.
- **Transposition coupling is the phonogène's whole point:** speed ratio changes pitch AND duration AND attack AND spectrum together. An engine that transposes pitch without scaling duration violates the craft (unless the universal-phonogène flag is set per cell).
- **The acousmatic gate is a human pass.** Encoding it as "dropped" cells in V4 with an export-time filter keeps the composer-in-the-loop; an objective "quality" function would be fake craft.
- **Silence is material** (radio montage heritage) — the closure section's rests are deliberate, not empty padding.
- **The Beatles' "Tomorrow Never Knows" example shows the pop crossover** — but the core craft is the 1948–75 studio practice; the hip-hop/sampling lineage is a descendant, mentionable but not the method itself.
- **"Musique concrète instrumentale"** (Lachenmann) is a *different* method — live performers producing concrete-like sounds — noted here only to avoid confusion; not folded into this entry.
- **Web fetching was rate-limited (429s)** during research; retried with backoff + UA headers. All facts above were verified against fetched Wikipedia extracts.
