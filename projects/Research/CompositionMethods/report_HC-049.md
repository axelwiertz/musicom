# REPORT: HC-049 — Kecak (Ramayana Monkey Chant)
## Balinese Vocal Interlocking & Dramatic Architecture

**Date**: 2026-09-28
**Next Free ID**: HC-050

---

## Method Name

Kecak (Ramayana Monkey Chant) — Balinese Vocal Interlocking & Dramatic Architecture

## Tradition / Culture

Balinese Hindu — Indonesia (Bali), 1930s–present. Roots in the Sanghyang trance-exorcism dance (pre-20th c.), adapted into a secular Ramayana dance-drama in collaboration with German artist Walter Spies and Balinese dancer I Wayan Limbak. Since the 1970s, *kecak kreasi/kontemporer* has emerged as an art form valued by Balinese audiences, distinct from the tourist-oriented *kecak ramayana*. The form is referred to as *gamelan suara* ("voice orchestra") because the chorus recreates the stratified sound of a bronze gamelan ensemble using only the human voice.

## Layer

**human (→concrete)**

This is a live, performed craft centred on oral transmission of rhythmic syllable patterns (cak telu/lima/nem/pitu), interlock timing, and dramatic scene architecture. No notation. The method is concrete in that the exact onsets of each syllable sub-pattern, the scene sequence, and the cue mechanisms can be encoded into a deterministic UnitMatrix realisation.

## The Craft Procedure in Detail

### Step 1: Internalise the invariant pulse
Every chorus member learns to maintain a steady unchanging pulse — the "cak" syllable as a continuous stream. The syllable is percussive, short, and unvoiced (glottal stop), enabling precise interlock without pitch or sustain overlap. Novices sit in the outermost ring and imitate; only senior members move to inner rings.

### Step 2: Master the named rhythmic patterns
Each chanter memorises at least four core patterns by rote imitation (months to years):

- **Cak polos**: plain unison "cak-cak-cak" on every subdivision — the ground layer.
- **Cak telu** (3-syllable): syncopated 3-count pattern creating cross-rhythmic tension against a 4/4 or 8-beat frame.
- **Cak lima** (5-syllable): asymmetric 5-count pattern.
- **Cak nem** (6-syllable): more regular 6-count pattern (two groups of 3).
- **Cak pitu** (7-syllable): 7-count shift pattern.
- **Cak lesung**: variant named after the rice-pounding mortar rhythm.

No notation exists. Transmission is entirely oral-aural, senior to junior, in pre-performance rehearsal sessions.

### Step 3: Assign specialised vocal roles
Within the chorus of 50–150+, specific senior chanters fill focused roles:

| Role | Name | Function |
|------|------|----------|
| Melodic soloist | Juru gending (pengong) | Sings pentatonic filigree ("shiiir-yang-ngger-yang-nggur-yang-nggeer") over the cak tapestry |
| Pulse keeper | Juru kawen | Chants "po-po-po-po" at beat level — bare steady anchor |
| Conductor/Leader | Juru (kecak) leader | Shouts command cues: "Diih!" (stop all), "Chiaaat!" (resume) |
| Narrator | Dalang | Recites Ramayana story in Balinese/Sanskrit between scenes |

### Step 4: Arrange concentric circles by proficiency
The spatial arrangement matches the density hierarchy:
- **Inner ring**: most complex patterns (cak telu, cak pitu, alternations between patterns)
- **Middle rings**: medium complexity (cak lima, cak nem)
- **Outer ring**: simple cak-cak-cak unison (polos, novices)

### Step 5: Interlock the patterns (vocal hocket)
The "cak" syllable has zero sustain and a sharp attack. Therefore patterns interlock like gamelan kotekan: when group A is silent, group B fills the slot. The composite rhythm sounds continuous, faster and denser than any single chanter could produce. The key constraint: **at most one voice has an onset in any given subdivision slot**.

### Step 6: Layer character-dancers and dramatic scenes
Costumed dancer-actors perform in the circle centre. The Ramayana unfolds in a fixed sequence of scenes. The chanting circle shifts pattern, intensity, and tempo to match dramatic mood:
- Gentle scenes (forest exile): soft dynamics, slow cak pulse, juru gending sings melodic phrases
- Tension (golden deer, abduction): gradual tempo increase, syncopated patterns enter
- Battle (Rama vs Ravana, Hanuman's army): maximum tempo, all cak layers active, arm movements agitated
- Fire scene (Hanuman's tail burns Lanka): dancer enters trance, fire-kicking, chorus at peak intensity

### Step 7: Escalate through the performance arc (~1 hour)
1. **Pembukaan (Opening)**: slow cak-cak-cak, swaying body movements, establishing pulse (~5 min)
2. **Golden Deer**: tempo rises, cak telu enters (~3 min)
3. **Abduction of Sita**: cak telu + cak nem, heightened tension (~3 min)
4. **Jatayu Battle**: all patterns active, loudest dynamic (~5 min)
5. **Hanuman Search**: Hanuman solo, subdued chorus, re-escalation (~5 min)
6. **Burning of Lanka / Fire Trance**: climax — max tempo, full interlock, fire-kicking, trance state (~7 min)
7. **Final Battle**: sustained peak, Rama defeats Ravana (~5 min)
8. **Penutup (Closing)**: resolution, tempo decelerates, chorus dissolves

### Step 8: Cue transitions by ear
No conductor. The juru leader shouts "Diih!" (stop) and "Chiaaat!" (start/resume). Senior chanters signal tempo modulations by shifting their pattern slightly ahead of the chorus. The entire ensemble follows by ear.

## Practitioner Examples

| Practitioner | Role | Contribution |
|-------------|------|-------------|
| **I Wayan Limbak** (1913–2003) | Dancer, choreographer | Co-created Kecak Ramayana with Spies (1930s). International tours spread the form. |
| **I Wayan Dibia** (b. 1950) | Scholar-practitioner | Author of *Kecak: the Vocal Chant of Bali* (1996). Codified named patterns (cak telu/lima/nem/pitu) and performance structure. |
| **Walter Spies** (1895–1942) | German artist, ethnographer | Collaborated with Limbak to adapt Sanghyang ritual into Ramayana dance-drama for tourist audiences. |
| **Kendra Stepputat** | Ethnomusicologist | Documented *kecak kreasi* (contemporary art kecak) evolution. Distinguished tourist vs. Balinese-audience kecak. |
| **Uluwatu Kecak Groups** | Performance ensemble | Daily sunset performances at Pura Uluwatu. The most internationally visible kecak venue. |
| **Contemporary kecak kreasi choreographers** | Choreographers | Expanding form with new compositions, non-Ramayana stories, female performers (since 2006). |

## UnitMatrix Integration

### Voices (8 voices)

| Voice | Role | Parameterisation |
|-------|------|-----------------|
| **V0** | Cak pulse grid | Continuous 8th-note onsets at tempo × 2. Invariant backbone. No pitch — drum-sound mapping. |
| **V1** | Cak telu/lima cross-rhythm | Syncopated 3-count and 5-count patterns. Onsets occupy specific subdivision slots of the 8th-note grid. |
| **V2** | Cak nem/pitu filler | 6- and 7-count patterns. Interlock constraint: rests of V1 = onsets of V2 (complementary hocket). |
| **V3** | Juru gending melody | Pentatonic (pelog/slendro) melodic line. Sparser entries, longer sustain. |
| **V4** | Juru kawen pulse marker | "po-po-po-po" on every beat. Steady quarter-note anchor. |
| **V5** | Character-dancer impacts | MIDI percussion events at scene climax points (fire stomps, battle hits). Not musical pitches — impact markers. |
| **V6** | Juru leader cues | One-tick marker events. "Diih!" = clear all voices for 1 beat (rest). "Chiaaat!" = re-entry synchronisation event. |
| **V7** | Dalang narration | Text events only (metadata layer). Not rendered as audio. |

### Sections (8 sections)

| S | Name | Bars | Tempo | Active V1/V2 | V3 (gending) | Character |
|---|------|------|-------|-------------|-------------|-----------|
| S0 | Pembukaan (Opening) | ~64 | 60–80 | polos only | Melodic | Slow swaying, forest exile |
| S1 | Golden Deer | ~32 | 80–90 | V1 (cak telu) | Tacet | Tension entry |
| S2 | Abduction | ~32 | 90–100 | V1+V2 | Tacet | Heightened drama |
| S3 | Jatayu Battle | ~48 | 100–110 | V1+V2+V1 | Tacet | Loudest battle |
| S4 | Hanuman Search | ~48 | 100 | V1 polos only | Melodic | Solo introspective |
| S5 | Burning of Lanka | ~64 | 110–130 | V1+V2 full | Tacet | Maximum, trance, fire |
| S6 | Final Battle | ~48 | 120–130 | V1+V2 full | Tacet | Sustained peak |
| S7 | Penutup (Closing) | ~32 | 120→60 decel | polos only | Melodic | Resolution, dissolve |

### Rules (Encodeable Constraints)

1. **Cak syllable mask**: each event = 1 tick (at 480ppqn: ~60–240 ticks), zero sustain, no pitch (single attack class).
2. **Hocket interlock**: for any subdivision slot t, at most one voice among {V1, V2} may have an onset. Rests of V1 = onsets of V2.
3. **Pulse invariance**: V0 (cak grid) and V4 (po marker) maintain constant tempo except at leader-cued acceleration points.
4. **Cross-rhythmic multiplicity**: composite grid must produce ≥2 simultaneous periodicity layers (e.g. 3-against-4, 5-against-8).
5. **Pattern locking per scene**: each V1/V2 pattern (telu/lima/nem/pitu) is fixed for the duration of the current section. No mid-section pattern mutation.
6. **Leader cue mask**: V6 "Diih!" event = clear all voices for exactly 1 beat (all rests). "Chiaaat!" = all voices resume simultaneously.
7. **Pentatonic constraint**: V3 pitch set ⊆ {D,F,G,A,C} (pelog/slendro subset). No chromatic pitches.
8. **Density monotonic increase S0→S5**: number of active voices increases monotonically from 2 (V0+V4 only) to 6 (all except V3+V7). S6→S7 reverses.
9. **Scene boundary integrity**: V7 text markers (dalang narration) placed between sections only.
10. **Zero-drift**: all 8 voice rows must have equal total tick duration. Section lengths predetermined, events padded to section end.
11. **Trance/fire escalation at S5**: density floor override — all voices minimum-active at peak. V6 triggers density override state.
12. **Unison refrain**: at the end of S7, all voices converge on simultaneous "cak" unison for 2 bars → final stroke → silence.

## Table Row Added

```
| HC-049 | human (→concrete) | Kecak (Ramayana Monkey Chant) — Balinese Vocal Interlocking & Dramatic Architecture | Balinese Hindu — Indonesia (Bali), 1930s–present; roots in Sanghyang trance ritual | RHYTHM, TEXTURE, STRUCTURE, PITCH | Internalize pulse → learn named patterns (cak telu/lima/nem/pitu) by rote → assign concentric circle positions (complex patterns inner) → interlock syllable-slot hocket → layer juru gending melody + juru kawen pulse marker → juru leader cues transitions via shouts → character dancers act Ramayana scenes in center → escalate through 7-scene arc (opening → deer → abduction → battle → search → fire → resolution) → dissolve climax with trance/fire section | Voice 0 = cak pulse grid (invariant 8th-note backbone). Voice 1 = cak telu/lima cross-rhythm (syncopated patterns). Voice 2 = cak nem/pitu filler (interlock complement, no overlap with V1). Voice 3 = juru gending (pentatonic melodic line). Voice 4 = juru kawen pulse marker (po-po-po-po). Voice 5 = character-dancer impact events. Voice 6 = juru leader cues (Diih!/Chiaaat!). Voice 7 = dalang narration text events. Sections = S0 Pembukaan → S1 Golden Deer → S2 Abduction → S3 Jatayu Battle → S4 Hanuman Search → S5 Burning of Lanka → S6 Final Battle → S7 Penutup. Rules: cak zero-sustain syllable, hocket interlock (≤1 voice per subdivision slot), pulse invariance, cross-rhythmic multiplicity (≥2 periodicity layers), pattern locked per scene, leader cue mask (clear all for 1 beat), pentatonic pitch set for V3, density monotonic increase S0→S5 and decrease S6→S7, zero-drift | I Wayan Limbak (co-creator, 1913–2003), I Wayan Dibia (scholar-practitioner, *Kecak: the Vocal Chant of Bali* 1996), Walter Spies (1930s collaborator), Kendra Stepputat (kecak kreasi ethnographer), Uluwatu/Tanah Lot/Ratu Boko performance groups | ✅ Documented |
```

## Verification

- `grep "HC-049" human_method_HC-049_kecak-monkey-chant.md` → found (detail file)
- `grep "HC-049" human_methods_db.md` → found (database table)
- Next free ID: HC-050

## Quirks & Pitfalls

1. **No pitch = no traditional melody**: The cak syllable is unpitched percussion. The "music" is purely rhythmic. The only pitched element is the juru gending line. A UnitMatrix realisation should use a percussion channel (MIDI ch10) for the cak layers and a pitched instrument for V3.
2. **Oral transmission is the ONLY method**: Notation does not exist and pattern names vary by village group. Any "notation" is a scholarly reconstruction (Dibia 1996).
3. **Tourist vs. art kecak**: The standardized kecak ramayana (tourist version) is shorter and louder than kecak kreasi (contemporary). The research here describes the standard tourist-dramatic form; kecak kreasi is more experimental.
4. **No conductor means no downbeat sync**: The leader cue "Diih!" clears the texture completely for 1 beat, creating a break that paradoxically re-syncs the entire ensemble. This is the only synchronisation mechanism.
5. **Trance is NOT fake in source tradition**: The Sanghyang fire trance is genuine — the dancer enters an altered state and does not feel fire. In tourist kecak, this is staged. The report describes the staged version.
6. **Distinct from Gamelan Kotekan (HC-002)**: HC-002 covers instrumental gangsa interlocking in Gamelan Bali. HC-049 covers the purely vocal Kecak with its dramatic narrative structure, large chorus, lack of instruments, and Ramayana story arc. They share the interlock principle but are fundamentally different performance traditions.
7. **High vocal count**: 50–150 voices is hard to map directly to a UnitMatrix. Solution: treat each voice in the matrix as a *group* (one pattern per group) rather than individual choristers. The pattern-precision matters, not the number of bodies.