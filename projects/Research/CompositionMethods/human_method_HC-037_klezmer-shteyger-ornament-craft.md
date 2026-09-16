# HC-037 — Klezmer Ornament-Led Ensemble Craft (Shteyger Modes + Doina-to-Dance Wedding Set)

**Method ID:** HC-037
**Layer:** concrete (target when implemented) — human-craft knowledge; realizes material through the UnitMatrix
**Tradition:** Ashkenazi Jewish klezmer — Eastern Europe (17th c. guilds, Kraków 1595; Prague refs 1511/1533) → American immigrant big-band era (1880s–1940s) → klezmer revival (1970s–present)
**Primary Elements:** PITCH, RHYTHM, TEXTURE, STRUCTURE
**Status:** ✅ Documented

---

## 1. What it is

Klezmer = professional instrumental music of Ashkenazi Jews (Yiddish *k'lei zemer*,
"instruments of melody"), played by itinerant guild musicians (**klezmorim**) at
weddings and community functions. The craft signature for the engine: **a tune is
not a fixed melody — it is a modal shell (shteyger) + a dance-meter container +
a live ornament/variation practice that the lead voice executes on every pass**.
Ornamentation is not random decoration: Yiddish has named ornaments (krekhts,
kneytsh, kvetsh, tshok, glitshn) and their use is governed by *taste*,
self-expression, variation and restraint — a real cognitive workflow, not noise.
Ornaments imitate the **human voice / hazzan (cantor)** — sighing, laughing,
groaning — because the tradition extends vocal (cantorial + Hasidic nigun)
practice onto instruments.

Wedding-function structure drives form: **non-metrical listening pieces
(doina) precede metric dance tunes**; dance types each carry their own meter,
character and social script (freylekhs, bulgar, sher, khosidl, hora/zhok,
terkisher); processional/parting pieces (gas-nign, dobriden, zay gezunt) frame
the day. The ensemble reads the room and sequences tune-types as a **wedding
set**: rubato intro → dance block → ritual feature → dance block → closer.

Key facts anchoring this entry:

- **Modes (shteyger/nusach)** — the pitch world, shared with synagogue prayer
  modes. Beregovsky's corpus: **~25% Freygish** (Phrygian dominant, = maqam
  Hijaz), majority natural-minor-family (Mogen Ovos), ~20% major; plus **Mi
  Sheberakh** (Ukrainian Dorian, raised 4th — the doina mode), **Adonoy
  Molokh** ("Jewish major", flatted 7th ≈ Mixolydian), **Yishtabach** (Mogen
  Ovos variant flattening 2̂ and 5̂). Scales work as **pentachords, not fixed
  octatonic scales** — different parts of a melody sit in different
  mode-portions, and **modal progression** (e.g. Freygish upper pentachord →
  Mogen Ovos lower pentachord) is a compositional resource (Joshua Horowitz,
  "The Klezmer Ahava Rabboh Shteyger: Mode, Sub-mode, and Modal Progression").
- **Named ornaments** (vocal-imitative, from cantorial/Hasidic practice):
  **krekhts** ("groan" — upward pitch scoops/sob after landing on a note,
  often before a cadence), **kneytsh** ("wrinkle" — bent/pinched note),
  **kvetsh** ("pressure"), **tshok** ("laugh/cackle" — bent note, a "chromatic
  twist"), **glitshn** (glissandos), trills, grace notes, appoggiaturas,
  mordents, slides, flageolets (string harmonics), pedal notes — plus
  **typical klezmer cadences** that identify a tune as klezmer even when the
  broader structure is borrowed.
- **Function repertoire**: dance types with meters — **freylekhs** (2/4 circle
  dance; a.k.a. redl, hopke, khosid, dreydl, rikudl), **bulgar** (Moldavian
  circle dance, syncopated 2/4 or 4/4, became THE American dance type after
  Tarras "Bessarabianized" the repertoire), **sher** ("scissors", 4/4
  march-like **figure dance for four couples** in square formation — musically
  freylekhs-like but the number of sections must fit the called figures),
  **khosidl** (dignified 2/4 or 4/4, Hasidic-derived), **hora/zhok** (from
  Romanian joc, 3/8 circle dance), **terkisher** (virtuosic 4/4 Ottoman-style
  display piece), **skotshne** (elaborate freylekhs, dancing or listening).
- **Doina** = non-metrical, highly ornamented, rubato improvisation "on a more
  or less fixed pattern (usually a descending one), stretching the notes in a
  rubato-like manner... prolonged notes are the fourth or fifth above the
  floor note", adopted from Romanian lăutari (Bartók linked it to the
  Arabo-Persian makam family; klezmer doinas are influenced by Hasidic
  nigunim). Instrumental doinas usually serve **as an introduction to a dance
  tune** — the classic set pairing. Related free-form genres: taksim, fantasia
  (variations on a simple theme), volekhl.
- **Ensemble**: small 3–5 players (18th–early 19th c.: lead violin, second
  violin, cello, cimbalom — like Hungarian bands); clarinet joins mid-19th c.;
  Ukrainian orchestras grew to 7–12 with brass; **tsimbl/cimbalom, bass
  (baran), poyk drum with cymbal on top**; early-20th-c. recordings = minimal
  percussion (wood block/snare). Lead instrument = violin (19th c. virtuosos
  Pedotser, Stempenyu) then **clarinet** (Brandwein, Tarras). Repertoire
  transmitted orally through klezmer dynasties and apprenticeship; each
  musician had his own idea of correct style; ornament usage governed by
  taste/restraint. The **badkhn** (wedding poet/jester) sang to the bride over
  free-form accompaniment; **Kale-bazetsn** (seating of the bride) pieces are
  freeform; **broygez-tants** (anger-and-reconciliation dance) pantomime.
- **Rhythm/texture facts**: bulgar's syncopated 2/4 pickup-driven lift;
  secondary melody instruments play **countermelody/seconding**: 2nd violin
  and tsimbl **double-time elaboration** (emphasizing off-beats —
  "fakēng" the beat), clarinet at lower volume "sneaks in with ornamented
  secondings" of the violin lead — a real heterophonic seconding practice,
  not chordal comping.

---

## 2. Layer classification

`layer: concrete (target when implemented)` — same tag as all HC-* rows. The
klezmer craft is human-craft knowledge: no generator in `generator_registry`
and no ABS-* spec. When implemented it realizes a **modal (shteyger) tune set**
as UnitMatrix rows (lead + seconding voice + bass + drum), with the shteyger
choice as the per-piece pitch-world parameter and the doina→dance pair as the
section arc.

---

## 3. Craft procedure (how a human does it, step by step)

1. **Pick the function and dance type** — wedding script decides form: circle
   dance (freylekhs/bulgar), figure dance (sher: 4 couples, figures called,
   sections must fit the dance figures), dignified feature (khosidl), listening
   intro (doina), processional/parting (gas-nign, dobriden, zay gezunt —
   Beregovski: gas-nign always 3/4), ritual dance (kosher-tants/mitsve-tants,
   broygez-tants). Music serves the event, not the reverse.
2. **Choose the shteyger (mode)** — the pitch-world decision: Freygish
   (identity mode, ~25% of corpus), Mogen Ovos (natural minor, greeting/parting
   + dances), Mi Sheberakh (doina mode, raised 4th), Adonoy Molokh ("Jewish
   major"), Yishtabach; modal progression between pentachord regions is
   compositional (Freygish upper → Mogen Ovos lower shares the same pitch
   pool). Tune and mode are one decision — "Hava Nagila" (Freygish), doinas
   lean Mi Sheberakh.
3. **Learn the tune orally** — rote from family/lineage/teacher (klezmer
   dynasties, apprenticeship); tune rarely attributed to a composer; each
   player owns his version; notation is a memory aid, not the source
   (Brandwein could not read sheet music at all).
4. **Assemble the tune's skeleton from cadence + formula stock** — phrases
   built around **typical klezmer cadences** (cadence type identifies the
   genre even in borrowed structures) and stereotypic turns; freylekhs/sher
   tunes are two-reel-style **AABB** section pairs (often 8 bars, ending
   distantly then home); composition = selection + order + ornament, as in
   slått craft (cf. HC-036).
5. **Compose the seconding plan** — who seconds whom: 2nd violin/tsimbl play
   **double-time elaboration with off-beat emphasis** under the lead;
   clarinet (in violin-led bands) "sneaks in" with ornamented seconding of
   the lead; roles swap when the clarinet leads (American-era standard:
   clarinet lead, violin seconds).
6. **Lay the bass/drum floor** — bass (baran) on strong beats; **poyk
   (bass drum + cymbal) marks the dance weight**; early recordings keep
   percussion minimal (wood block/snare) — the percussion is the dance's
   floor, not a kit.
7. **Ornament by taste, not by density** — apply named ornaments as *vocal
   imitation*: krekhts (sob/groan after landing on a note, esp. before
   cadences), kneytsh/kvetsh (pinched/bent notes), tshok (cackled bent note),
   glitshn (glissando into a note), trills/grace notes/mordents, flageolets;
   govern with taste, variation and restraint — the same phrase is never
   ornamented identically twice; ornaments cluster at cadences and phrase
   ends, rarely at the very start of a section.
8. **Doina intro (when the function calls for one)** — free-rhythm rubato
   improvisation on a fixed descending pattern; stretch the notes that are a
   4th/5th above the floor note; accompany sparsely (held chords/drone) so
   the soloist breathes; modulate inside the doina (Mi Sheberakh ↔ Freygish
   upper-pentachord sharing) and **land the doina's final phrase directly
   into the dance tune's opening** — the classic doina→bulgar/freylekhs
   segue (recorded practice: taksim/doina intro replacing taksim, both
   lăutari and klezmer practice).
9. **Play the dance block with repetition + variation** — AABB cycles; each
   pass ornaments more (plain statement → ornamented → virtuosic double-time
   seconding), exactly the strophe-variation arc of other oral traditions.
10. **Follow the dancers/room** — sher sections must fit called figures
    (cut/extend a section to fit the figure); master drummer/leader watches
    the dance floor; close the set with a parting piece (dobriden/zay gezunt)
    or walk the party onward with a gas-nign/march.
11. **Badkhn/ritual features** — under the badkhn's sung couplets
    (kale-bazetsn), play held, free-form chords/drone; broygez-tants mirrors
    the pantomime (angry music → reconciliation music) — music follows the
    social script.

---

## 4. Practitioner examples

- **Naftule Brandwein** (1884–1963, Galicia→NY) — the archetypal
  ornament-first player: virtuosic **doinas and dance pieces** on Victor
  (1923–27), krekhts-laden cantorial style, self-promoting light-bulb suit,
  **could not read music** — pure oral-craft carrier; run of Victor sessions
  ended 1927; late return 1941 under own label.
- **Dave Tarras** (c. 1895–1989, Podolia→NY) — the smooth counter-pole:
  ~500 recordings, read music, military-band training; "smooth and dignified,
  with deliberate and rhythmical phrasing"; **"Bessarabianized" Jewish dance
  music and replaced the freylekh with the bulgar** as the dominant American
  dance type (Zev Feldman); *Tanz!* (1956, with son-in-law Sam Musiker)
  fused jazz + klezmer; mentored **Andy Statman**; 1984 NEA National Heritage
  Fellowship.
- **Pedotser** (Aron-Moyshe Kholodenko) & **Stempenyu** (Yosef Drucker) —
  19th-c. klezmer **violin virtuosos** combining classical technique
  (Khandoshkin) with Bessarabian folk violin; their dance/display pieces
  spread anonymously after their deaths — repertoire without named composers.
- **Moisei Beregovsky** (1892–1961) — Soviet ethnomusicologist who collected
  the corpus (~25% Freygish, ~⅕ major, majority minor-family); used the
  Yiddish term **gust ("taste")** for mode — taste as analytic category.
- **Michael Alpert** (Brave Old World) — describes the **sher** as figure
  dance "similar to the American square dance... richest venues for social
  interaction" (Kraków 1994 presentation on Pessl's Sher).
- **Joshua Horowitz** — "The Klezmer Ahava Rabboh Shteyger: Mode, Sub-mode,
  and Modal Progression" — the systematic account of shteyger pentachords and
  modal progression; basis for the engine's mode rules below.
- **Walter Zev Feldman** — 1979 LP with Andy Statman popularized the word
  "klezmer" as genre name; scholarship on klezmer dance structure.
- **Andy Statman**, **Max Epstein, Sid Beckerman, Ray Musiker** —
  Tarras-lineage revival; 1970s revival bands (The Klezmatics, Klezmer
  Conservatory Band, Brave Old World, Budowitz) carried the craft to Europe.
- Canonical pieces: **"Hava Nagila"** (Freygish), **"Ma yofus"** (Freygish),
  Brandwein's **"Odessa Bulgar"** / doina-labelled Victor sides, Tarras
  *Tanz!* (1956), *Sher #1 (Pessl's Sher)*.

---

## 5. UnitMatrix mapping (Musicom engine)

### Voices & Sections

| Voice | Role | Content | Invariance |
|---|---|---|---|
| Voice 0 | **lead (clarinet/violin)** | modal tune from cadence+formula stock; ornament profile (krekhts/tshok/glitshn) thickens per pass | shteyger pitch-set lock; AABB cycle lock |
| Voice 1 | **seconding voice** (2nd violin/tsimbl/2nd clarinet) | double-time elaboration, off-beat emphasis, ornamented echo of lead tail | gap-fill complement; never collides with lead onsets |
| Voice 2 | **bass (baran)** | root-fifth on strong beats, floor-note anchor of the shteyger | beat-locked, root-bias |
| Voice 3 | **poyk (bass drum + cymbal)** | dance-weight pulse + cymbal accents at section turns | continuous, invariant |
| Voice 4 | **doina solo layer** (lead instrument, free-rhythm) | rubato stretch on 4̂/5̂ above floor note; sparse held-chord support from V2 | free rhythm, desc.-pattern constraint |

**Sections** = wedding-set script, not abstract blocks: **Doina (rubato intro)
→ Dance A (freylekhs/bulgar AABB, plain) → Dance A' (ornamented pass) →
Dance A'' (virtuosic double-time pass) → Sher/feature (figure-length
sections) → Parting piece (Mogen Ovos, cadential close)**. Doina's final
phrase lands into the dance's first bar (segue invariant). Badkhn/ritual
section = free-form over held chords (Kale-bazetsn) when scripted.

### Rules to encode

- **Shteyger pitch-set lock** — one mode per piece: Freygish
  (0,1,4,5,7,8,10), Mi Sheberakh (0,2,3,6,7,9,10), Mogen Ovos (0,2,3,5,7,8,10),
  Adonoy Molokh (0,2,4,5,7,9,10), Yishtabach (Mogen Ovos with flatted 2̂ & 5̂
  as variants). Melody voices restricted to the mode; **modal progression**
  = section-level move between shared-pitch pentachord regions (Freygish
  upper ↔ Mogen Ovos lower).
- **Cadence-formula constraint** — phrase endings drawn from a small stock of
  typical klezmer cadences; genre identification rides the cadences, not the
  structural provenance of the tune.
- **Ornament profile** — named ornament set (krekhts = short pitch-bend scoop
  after note onset, esp. pre-cadential; tshok = quick chromatic bend-release;
  glitshn = pre-onset glissando; trill/grace/mordent pool). Ornament density
  rises with pass number; **never on every note** (taste/restraint gate);
  clusters at cadences/phrase tails; krekhts reserved for cadential approach.
- **Seconding interlock** — Voice 1 fills lead gaps: double-time subdivision,
  off-beat emphasis, echo-ornament of the lead's last group; ≤1 onset per
  subdivision; no unison collision with Voice 0.
- **Double-time elaboration gate** — Voice 1 density ≤ 2× Voice 0; off-beat
  emphasis bias in 2/4/4/4 dances.
- **Bass floor-note anchor** — Voice 2 emphasizes the mode's floor note
  (finalis) and 5th on strong beats; Freygish/Mi Sheberakh floor logic follows
  the descending-pattern practice.
- **Poyk dance-weight invariance** — Voice 3 never drops while the dance runs;
  cymbal accent on section entry.
- **Doina rubato rule** — Voice 4 section uses explicit non-uniform event
  spacing (stretched notes = long tick spans on 4̂/5̂ above floor note,
  descending fixed-pattern frame); other voices hold sparse pedal/held chords.
  Segue: doina's last phrase = dance's first phrase (pitch-locked handoff).
- **Dance-meter containers** — freylekhs/bulgar 2/4 (bulgar with syncopated
  pickup bias), sher 4/4 march (section count flexible to fit figures),
  khosidl 2/4 or 4/4 dignified, hora/zhok 3/8, terkisher 4/4 virtuosic,
  gas-nign 3/4.
- **Pass-variation arc** — each AABB cycle re-orchestrates: plain → ornamented
  → double-time seconding → feature (sher) → parting. Material varies, the
  cycle structure never does (variation-not-invention, cf. HC-035/HC-036).
- **Zero-drift padding** — terminal landmark at `section_len` per voice so
  rubato doina cells and dance cells stay equal-length (MIDI tail truncation
  pitfall).

### Element mapping

**PITCH** (shteyger modes + cadence stock + ornaments, primary),
**RHYTHM** (dance-meter containers + rubato doina + seconding double-time,
primary),
**TEXTURE** (lead/second heterophonic interlock, primary),
**STRUCTURE** (wedding-set script: doina → dance passes → feature → parting;
AABB cycle invariance, primary),
**HARMONY** is emergent (root-fifth bass under a modal melody; American-era
arrangements add chord-based writing — a later stratum, not the core craft).

---

## 6. Quirks / pitfalls

- **Scales are pentachords, not octave scales** — encoding shteygers as fixed
  8-note scales breaks modal progression (Freygish upper ↔ Mogen Ovos lower
  share pitch classes but flip function); represent mode as stacked
  pentachord regions with a floor note, per Horowitz.
- **Ornament without restraint = parody** — the tradition's own category is
  *taste/gust*; cap ornament density, cluster at cadences, reserve krekhts
  for pre-cadential spots. Ornamenting every note reads as off-style
  instantly.
- **Krekhts is a bend, not a note** — implement as pitch-bend-like offset on
  the ornamented note (or a grace-note pair), never a scale-tone ornament;
  it imitates a sob, which lives between pitches.
- **Doina rubato ≠ free timing everywhere** — only the solo layer is rubato;
  bass/drum drop to sparse pedal or tacet; rubato must be encoded as explicit
  tick spans (non-uniform), then padded to `section_len` or the zero-drift
  gate fails.
- **The segue is the form** — a doina that doesn't land into the dance tune
  is a taksim; the doina→dance handoff (last doina phrase = dance's first
  phrase, pitch-locked) is the identifying move. Encode as a section
  boundary rule, not two unrelated cells.
- **Sher section count serves the dance figures** — cut or extend sections
  to fit the called figure; a fixed AABBCC that ignores the figure script
  is off-function.
- **Don't chromaticize the mode** — American big-band klezmer added chords
  and chromatic passing tones; the pre-war craft core is modal + diatonic
  within the shteyger, with ornaments living *between* pitches (bends), not
  as passing chromatics.
- **Second ≠ harmony part** — the seconding voice heterophonically elaborates
  the lead (double-time, off-beats, echo), it does not sing 3rds/6ths; a
  chordal harmony-part render is a revival-era stratum, not the craft core.
- **Lead instrument era** — 19th c. = violin lead (Pedotser/Stempenyu);
  post-1900 American = clarinet lead (Brandwein/Tarras); pick era when
  assigning GM programs (violin vs clarinet) so the seconding plan matches.

---

## 7. Sources

- Wikipedia: *Klezmer* (style, named ornaments krekhts/kneytsh/kvetsh/tshok/glitshn, cadences, vocal-imitation principle, shteyger/nusach/gust terminology, Beregovsky mode statistics, mode descriptions Freygish/Mi Sheberakh/Adonoy Molokh/Mogen Ovos/Yishtabach, dance types freylekhs/bulgar/sher/khosidl/hora-zhok/terkisher/skotshne, doina/taksim/fantasia/volekhl listening genres, gas-nign 3/4, kosher-tants/broygez-tants, badkhn/kale-bazetsn, ensemble history 3–5 → 7–12, poyk/baran percussion, Pedotser/Stempenyu, Brandwein/Tarras, Tarras NEA 1984, Horowitz citation, Feldman 1979 LP naming credit).
- Wikipedia: *Doina* (free-rhythm, highly ornamented melismatic improvisation on a descending fixed pattern; prolonged notes = 4th/5th above floor note; Bartók Arabo-Persian linkage; taksim→doina intro-to-dance practice; klezmer doinas influenced by Hasidic nigunim).
- Wikipedia: *Sher (dance)* (4/4 march-like set dance, four couples, square formation, scissors figure; Michael Alpert description).
- Wikipedia: *Hora (dance)* (circle-dance family incl. Ashkenazi hore; 3-step-forward-1-back figure; instruments incl. cimbalom/accordion).
- Wikipedia: *Dave Tarras*, *Naftule Brandwein* (career facts, recording practice, doina recordings, Tarras's bulgar shift per Zev Feldman, Brandwein's non-reading of notation, Tarras mentoring Andy Statman, *Tanz!* 1956).
- Wikipedia: *Nigun* (non-lexical vocables, Hasidic group-singing context feeding klezmer's vocal aesthetic).
- Scholarship context: Joshua Horowitz, "The Klezmer Ahava Rabboh Shteyger: Mode, Sub-mode, and Modal Progression"; Moisei Beregovsky corpus statistics (via Wikipedia *Klezmer*).
