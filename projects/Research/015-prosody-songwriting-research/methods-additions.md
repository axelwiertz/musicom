# Proposed Musicom Method Additions

## 005: Prosodic Syntax Mapping
**Goal**: map lyric syntax to phrase and rhythm generation.

**Rules**
- Question marks -> unresolved cadence, rising final pitch, open harmony.
- Periods -> cadence, tonic landing, longer final duration.
- Commas -> light break, short rest or held note.
- Line breaks -> phrase boundary candidate.
- Stress pattern -> beat weight and velocity.

**Needed primitives**
- lyric parser
- syllable/stress extractor
- punctuation state
- phrase boundary detector

## 006: Enjambment Delay
**Goal**: prevent premature closure across line breaks.

**Rules**
- If syntax continues past line end, block cadence at that boundary.
- Continue harmony into next phrase or bar.
- Keep melodic line unfinished until syntactic completion.

**Music effect**
- delayed resolution
- longer breath arc
- stronger forward motion

## 007: Caesura Gap Control
**Goal**: model pause as structural event.

**Rules**
- Insert rest, sustain, or percussion-only slot at caesura.
- Pause length scales with emotional weight.
- Use caesura before reveal, reversal, or punch line.

**Music effect**
- breath
- emphasis
- dramatic cut

## 008: Call-Response Voice Allocation
**Goal**: distribute lyric dialogue across voices or sections.

**Rules**
- Call voice: higher activity, shorter phrase, tense contour.
- Response voice: lower activity or wider resolution contour.
- Optional antiphony between lead and backing.

**Music effect**
- dialog structure
- chant / gospel / folk / rap support

## 009: Rhyme Density and Internal Echo
**Goal**: score and place internal rhyme.

**Rules**
- Prefer internal rhyme before final cadence.
- Track rhyme pairs within line and across adjacent lines.
- Increase rhythmic density where rhyme clusters occur.

**Music effect**
- propulsion
- memorability
- phrase glue

## 010: Narrative Tension Arc
**Goal**: bind lyric story to harmony, contour, and register.

**Rules**
- Verse = low register, lower harmonic tension.
- Pre-chorus = rising contour, harmonic lift.
- Chorus = highest contour, strongest resolution or hook.
- Bridge = contrast or inversion.
- Final chorus = expanded release.

**Music effect**
- story shape
- payoff control
- section-level emotional trajectory

## Comparison to current database
Already present:
- 001 Skeleton-First Refinement
- 002 Markov Probabilistic Transitions
- 003 Genetic Genome Selection
- 004 Prosodic Narrative Coupling

Missing additions:
- syntax-level lyric parser
- caesura as explicit timing primitive
- enjambment-aware cadence blocking
- call/response voice allocator
- rhyme-density metric
- narrative arc controller

## Recommended merge path
- Keep 004 as base.
- Add 005-010 as lyric-specific extension layer.
- Store in composition-methods-database under Elements Framework plus new lyric sublayer.
- Add validation hooks in rules for stress-beat, cadence closure, and rhyme density.
