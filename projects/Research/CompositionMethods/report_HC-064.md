# Report HC-064: Funk Groove Construction — The One / Chicken Scratch / Horn-Stab Interlock

## Overview

| Field | Value |
|---|---|
| **HC-ID** | HC-064 |
| **Method Name** | Funk Groove Construction — The One / Chicken Scratch / Horn-Stab Interlock |
| **Tradition / Culture** | African-American Funk (USA, ~1965–present) — James Brown & The J.B.'s, Parliament-Funkadelic, The Meters, Sly & The Family Stone, Earth Wind & Fire, Tower of Power |
| **Layer** | human (→ concrete) |
| **Primary Elements** | RHYTHM, TEXTURE, PITCH, HARMONY, STRUCTURE |
| **Craft Process** | See 9-step procedure below |
| **Real Practitioner Examples** | James Brown, Bootsy Collins, Jimmy Nolen, Clyde Stubblefield, Jabo Starks, Maceo Parker, Fred Wesley, Leo Nocentelli, Phelps "Catfish" Collins, Sly Stone, Tower of Power |
| **Status** | ✅ Documented |

---

## The Craft Procedure (9 steps — how the human does it)

### Step 1: Fix tempo, key, and harmonic cell
- Tempo: 90–125 bpm
- Key: horn-friendly (B♭, C, E♭, F, G)
- Harmonic loop: single chord vamp or 2-chord oscillation (I–IV, I–♭VII)
- Harmony is static or near-static — changes happen slowly

### Step 2: Write the bass line (pocket anchor)
- Root on The One (beat 1, strongest articulation)
- Syncopated ghost notes, 16th rests, slides, muted pops on beats 2–4
- Octave jumps and chromatic approaches
- Repeating 1–2 bar cell = piece fingerprint

### Step 3: Lock the drum pattern
- Kick syncopated (interlocks with bass, not four-on-the-floor)
- Snare crisp backbeat on 2&4
- Hi-hat 16th-note subdivision with relaxed swing
- Ghost notes between backbeats for texture

### Step 4: Write chicken-scratch guitar
- Muted staccato strums (palm/fret-hand damped)
- Rapid 16th-note motion, off-beat accents
- Bright, thin tone near bridge (or wah pedal)
- No sustained chords — it's percussion

### Step 5: Compose horn stabs
- Short staccato tutti figures (1–3 notes)
- Call-and-response: vocal or guitar calls → horns answer
- Horns play block chords (3–5 voices) or unison — no individual melodies
- Rests between stabs are composed

### Step 6: Write vocal/shout part
- Rhythmic shouts and grunts — voice as percussion
- Short call phrases (1–4 beats), syncopated
- Ad-libs cue arrangement changes ("Hit me!", "Take it to the bridge!")
- Melody secondary to rhythm

### Step 7: Add keyboard punch (optional)
- Hammond organ / electric piano
- Short chordal punches synced with horn stabs
- Sparse fills in bridge

### Step 8: Arrange macro-form as groove arc
- Single groove with dynamic states: Intro → Main Groove → Breakdown → Bridge/Solo → Climax → Outro
- No traditional AABA; variation from voice masks and intensity
- The entire track is the chorus

### Step 9: Rehearse to lock the pocket
- Fixed arrangement by ear — no charts in classic era
- The One is absolute (sub-millisecond precision)
- Fines for late/early entries (James Brown tradition)
- Danceability test: if dancers stop, groove is wrong

---

## Layer Classification

**Layer: human (→ concrete target when implemented)**

This is human-side craft knowledge — how a funk arranger/composer works. When implemented in the UnitMatrix, it becomes concrete note/riff data. The target layer is **concrete** because the method specifies exact pitch sequences, rhythmic grids, and muting patterns for each voice.

---

## Practitioner Examples

| Practitioner | Key Recordings | Specific Technique |
|---|---|---|
| **James Brown** | "Cold Sweat" (1967), "Papa's Got a Brand New Bag" (1965), "Funky Drummer" (1970) | Vocal-percussion style, The One invention, call-and-response horn arranging |
| **Bootsy Collins** | "Sex Machine", "Superbad", "Flash Light" | Funk bass pocket: octave jumps, ghost notes, chorus pedal |
| **Jimmy Nolen** | "Give It Up or Turn It Loose", "Ain't It Funky Now" | Chicken-scratch guitar originator |
| **Clyde Stubblefield / Jabo Starks** | "Funky Drummer" / "Cold Sweat" | Syncopated kick / backbeat snare drum vocabulary |
| **Maceo Parker / Fred Wesley** | "Pass the Peas", "Funky Drummer" | Horn-stab arranging & sax soloing over static groove |
| **Leo Nocentelli (The Meters)** | "Cissy Strut" (1969), "Look-Ka Py Py" | New Orleans chicken scratch + single-note syncopated riffs |
| **Parliament-Funkadelic** | "Flash Light" (1978), "One Nation Under a Groove" (1978) | Psychedelic funk: synth layers, wah-wah, group chant call-response |
| **Sly & The Family Stone** | "Thank You" (1969), "Family Affair" (1971) | Pop songwriting over funk pocket; vocal harmonies |
| **Tower of Power** | "What Is Hip?" (1973), "Oakland Stroke" (1975) | Complex horn-driven funk arrangements |
| **Earth Wind & Fire** | "September" (1978), "Shining Star" (1975), "Let's Groove" (1981) | Vocal-melody funk with horn stabs at big-band scale |

---

## UnitMatrix Mapping

### Voices

| Voice | Role | Section Behavior |
|---|---|---|
| V0 | **Bass Spine** — root on The One + syncopated ghost notes | Always on; muted in breakdown |
| V1 | **Drum Grid** — kick syncopated, snare 2&4, hi-hat 16th | Invariant; snare rolls in climax |
| V2 | **Chicken-Scratch Guitar** — muted staccato off-beat stabs | Always on; sparser in breakdown |
| V3 | **Horn Stabs** — 3–5 voice block-chord punctuation | Active main groove & climax; tacet in breakdown |
| V4 | **Vocal Shout** — rhythmic call phrases, percussion voice | Solo in verse sections; call-response with V3 |
| V5 | **Keyboard/Organ** — short chordal punches, sparse fills | Optional; active main groove, solo in bridge |
| V6 | **Percussion Shimmer** — tambourine/shaker, continuous 8th/16th | Enters main groove; loudest climax; tacet breakdown |

### Sections

| Section | Bars | Active Voices | Description |
|---|---|---|---|
| S0 Intro | 4–8 | V1→V0→V2→V4 | Tiered entry, establish groove |
| S1 Main Groove | 16–32 | All (V3 enters later) | Locked pocket, call-response active |
| S2 Breakdown | 4–8 | V0+V1+V2 sparse | Thin texture, bass/drums/guitar only |
| S3 Bridge/Solo | 16–32 | V0+V1+V2+V5+V6 | Instrumental solo over same groove |
| S4 Climax | 8–16 | Full tutti + V3 max | Max density, overlapping calls |
| S5 Outro | 4–8 | V0+V1+V2 | Tagged riff repeat, hard stop or fade |

### Rules (8 constraints)

1. **The-One invariance** — all voices must hit beat 1 every bar. Bass plays root on beat 1.
2. **Call-response interlock mask** — V4 call and V3 answer never overlap (≥1 beat gap).
3. **Chicken-scratch muting** — V2 events: velocity < 100, duration < 60 ticks, chord root+3rd+5th muted.
4. **Horn block-chord rule** — V3 events: ≥3 simultaneous pitches, short duration, same onset.
5. **Bass ghost-note vocabulary** — muted ghost notes (velocity < 40) on 16th subdivisions between roots.
6. **Static harmony** — chord changes ≤ every 4 bars. Preferred loops: I–I, I–IV, I–♭VII, i–♭VII.
7. **Density progression** — voices add monotonically S0→S4. No drops until S2 (selective) or S5.
8. **Section uniformity** — all cells must end at section's terminal landmark tick; repeat identical cells.

---

## Table Row Added to human_methods_db.md

```
| HC-064 | human (→concrete) | Funk Groove Construction — The One / Chicken Scratch / Horn-Stab Interlock | African-American Funk (USA, ~1965–present) — James Brown, Parliament, The Meters, Tower of Power | RHYTHM, TEXTURE, PITCH, HARMONY, STRUCTURE | Fix harmonic cell & tempo → write bass root on The One with syncopated ghost notes → set drum grid (kick-snare interlock + 16th hi-hat) → compose chicken-scratch guitar (muted staccato off-beat stabs) → write horn stabs (block-chord punctuation in call-and-response with vocal) → write vocal shout (percussive short calls) → add keyboard punch (optional) → arrange as groove-arc form (Intro→Main Groove→Breakdown→Solo Bridge→Climax→Outro) → rehearse to millisecond The-One precision | V0=Bass spine (root on beat1 + ghost notes). V1=Drum grid (kick syncopated, snare 2&4, hi-hat 16th). V2=Chicken-scratch guitar (muted staccato off-beat). V3=Horn stabs (≥3-voice block chords). V4=Vocal shout (percussive call phrases). V5=Keyboard punch (optional). V6=Percussion shimmer (tambourine/shaker) | James Brown (*Cold Sweat*, *Funky Drummer*, *The Payback*), Bootsy Collins (bass pocket), Jimmy Nolen (chicken-scratch guitar), Clyde Stubblefield & Jabo Starks (funk drums), Maceo Parker & Fred Wesley (horn stabs), Leo Nocentelli/The Meters (*Cissy Strut*), Parliament-Funkadelic (*Flash Light*), Tower of Power (*What Is Hip?*), Sly Stone, Earth Wind & Fire | ✅ Documented |
```

---

## Verification

| Check | Result |
|---|---|
| Detail file exists | `/opt/data/projects/Research/CompositionMethods/human_method_HC-064_funk-groove-construction.md` |
| Report file exists | `/opt/data/projects/Research/CompositionMethods/report_HC-064.md` |
| `grep HC-064` in detail file | ✅ Present (title, sections, references) |
| `grep HC-064` in DB file | ✅ Row added (line with HC-064 in table) |
| **Next free ID** | **HC-065** |

---

## Quirks & Pitfalls

1. **The One is played slightly ahead** — MIDI offset of −5 to −15 ticks on beat 1 events captures the feel.
2. **Groove is the composition** — reducing funk to a lead sheet loses its essence.
3. **Static harmony ≠ static arrangement** — interest comes from voice masks and dynamics, not chord changes.
4. **Kick and bass must interlock, not double** — simultaneous kick+bass on beat 1 = plodding.
5. **No written charts in classic tradition** — oral transmission; notation should be sparse rhythmic grid + chord symbols.