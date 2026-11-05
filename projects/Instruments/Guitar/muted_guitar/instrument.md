---
type: instrument
family: Guitar
name: Muted Guitar
midi_program: 28
gms: "Electric Guitar (muted)"
range_min: 28
range_max: 84
solo_range: [40, 76]
role: [rhythm, comp, groove, accent, texture, melody]
synthesis: [karplus-strong, modal, phase-mod]
---

# Muted Guitar

## MIDI / GM

- **Program**: 28 (GM1 Electric Guitar (muted) — palm-muted / fret-hand-damped solid-body electric guitar)
- **Channel**: any melodic channel; polyphonic (6 strings, but the idiom is 2–4 note chops and single-note chugs)
- **Pipeline stem label**: `GM_PROGRAMS[28] = "Electric Guitar (muted)"` → `trackXX_Electric_Guitar_muted.wav`
- **FluidR3 SF2 preset**: 28 = **"Palm Muted Guitar"** (SF2 uses the playing-technique name; pipeline uses the GM2 spec spelling — cosmetic only, **no routing impact**)

## Range

| Zone | MIDI | Pitches | Register |
|------|------|---------|----------|
| Full range | 28–84 | E1–C6 (GM patch span; real 22-fret guitar = E2–E6 = 40–76) | |
| Low chug | 28–47 | E1–B2 — palm-muted low-E/A chugs, the metal riff atom; fundamental thump, no ring | |
| Middle | 48–64 | C3–E4 — **THE muted-guitar zone**: 16th chord chops, single-note funk lines, double stops, scratches | |
| High | 65–84 | F4–C6 — short muted stabs, dead-string fills, top-note accents; thin and clicky above ~E5 | |

Empirical FluidR3 pitch sweep (notes 28/33/38/40/43/45/48/52/55/59/62/64/67/71/74/76/79/84, velocity 100) confirms the patch is audible across the whole 28–84 span with **no gaps**; RMS rolls off from 0.12 at E1 to 0.0055 at C6, so the top octave is present but weak — write it sparingly. Idiomatic writing zone is 40–76 (E2–E6, the real neck); the funk/metal money zone is 40–55 (E2–G3).

## Timbre DNA

The muted guitar is defined by **one technique applied to an ordinary electric guitar** — the strings are prevented from ringing:

- **Palm mute** (picking hand): the fleshy edge of the picking hand rests on the strings immediately in front of the bridge saddles. The pick still strikes, so there is a full pick transient, but the palm damps the string — the note speaks and dies in ~50–250 ms. Low strings produce a pitched *thump* with a strong fundamental and almost no upper-harmonic sustain.
- **Fret-hand mute** (fretting hand): fingers release pressure just enough to kill the pitch while staying on the strings — the "scratch"/"chika" with no defined note. This is the pure-rhythm texture layer.
- **Combination**: funk comping alternates fretted chops (pitched) with dead-string scratches (unpitched) in a 16th-note stream. Metal riffing uses palm-muted chugs (low E/A) alternated with open accents — the mute/open contrast *is* the riff.
- **Pickup**: usually bridge humbucker or single-coil — the bridge position gives the click and the midrange cut; the neck position turns the mute into mud and is rarely used.
- **Body**: irrelevant compared to an acoustic — the sound is dominated by the string's first 100 ms and the pickup, not by a resonating body.

In the ideal:
- **Low E (E2 = 82 Hz)**: the chug — full fundamental, tight thump, dead stop
- **A string (A2 = 110 Hz)**: second chug string, the "gallop" alternation
- **D string (D3 = 147 Hz)**: chop root — funk chord bottoms
- **G string (G3 = 196 Hz)**: the chop's top voice, cuts through the mix
- **B/E strings (B3/E4)**: short stabs only — the mute leaves nothing to sustain

Attack type:
- **Pick, palm muted**: hard transient + dead tail — the default
- **Pick, fret-hand muted**: no pitch, pure percussive scratch
- **Pick, palm released**: a normal electric attack that rings — used as the *contrast* accent, never as the base texture

## Articulations

| Technique | Velocity | Duration factor | Description |
|-----------|----------|----------------|-------------|
| palm_mute | 82 | 0.18 | Default: pick stroke with palm edge at the bridge — pitched attack, fast decay, no ring |
| chug | 92 | 0.08 | Low-E/A 16th chug — hardest pick, dead stop; the metal riff atom |
| funk_chop | 78 | 0.12 | 16th-note chord chop — short percussive stab on the upbeats (the "chick"); 3–4 note voicings only |
| muted_strum | 72 | 0.10 | Full-strum rake, fully damped — a "shhk" texture, not a chord |
| scratch | 38 | 0.05 | Fret-hand dead-string scratch — no defined pitch, pure rhythm texture |
| staccato | 80 | 0.22 | Single-note muted lead — pitch defined, just short |
| open_accent | 90 | 0.60 | Momentary palm release — chord rings out; the contrast that makes mutes read |
| double_stop | 76 | 0.15 | Two-note muted double stop (root+5th or root+octave) — riff punctuation |
| octave | 74 | 0.30 | Octave funk line — single-note hook, muted articulation |
| slide | 70 | 0.25 | Muted slide up/down — fret-hand drag, short travel |
| bend | 78 | 0.40 | Short bluesy bend — pitch rise, then damped |
| ghost_note | 30 | 0.04 | Near-inaudible 16th filler — grid texture between real notes |
| accent | 90 | 0.12 | Hard dig — cutting muted hit on the "1" |

## Synthesis

### Primary: Karplus-Strong (sound/synthesis/karplus_strong.py)

Muted guitar is still a plucked string — Karplus-Strong is the exact physical model, with the damping term turned up hard (a very lossy waveguide loop). This is the one guitar voice where the loop gain drops into the 0.98x range:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| loop_gain | 0.9850 | Palm mute kills the ring — ~0.2–0.4 s decay vs 0.9970+ for open strings; the lowest loop gain in the guitar family |
| excitation | "pick" | Hard plectrum attack — the click IS the funk/metal articulation |
| width | 0.30 | Narrow pulse = bright pick transient, then the damping eats the tail |
| lowpass_hz | 2200 | Palm flesh + bridge-pickup rolloff — darker than jazz (3500) because the muted string has almost no upper-harmonic sustain |
| noise_component | 0.030 | Moderate: pick scrape + palm slap are part of the sound (vs thumb 0.015) |

### Secondary: ModalSynth (sound/synthesis/modal.py)

Stock `'string'` preset, impulse excitation, with very fast decay rates (roughly 12/26/44/66/90 — several times faster than the jazz guitar's 4/10/18/28/40). The modal bank still gives the pitched thump on low chugs, which is what a mute is: a fundamental with almost no overtones left.

### Tertiary: PhaseModSynth (sound/synthesis/phase_mod.py — SP-012)

FM approximation — a saw carrier with more modulation edge than the jazz patch, and a near-instant release that models the mute:

| Parameter | Value |
|-----------|-------|
| carrier_shape | saw (even+odd harmonics) |
| mod_freq_ratio | 1.0 (octave doubling) |
| mod_depth | 2.0 — more edge than jazz (1.5), less than distortion |
| attack | 0.004 s — near-instant pick transient |
| release | 0.08 s — the mute itself |

## Production defaults

| Parameter | Value | Notes |
|-----------|-------|-------|
| REVERB_TAIL | 0.9 s | Tight, dry amp/room — the articulation is 16th-note detail; long tails blur it |
| EQ_BODY | (220, -1.5) | Peaking cut at 220 Hz — trim the palm-mute thump so chugs don't fight the bass |
| EQ_PRESENCE | (3200, +2.5) | Peaking boost at 3.2 kHz — pick-attack click and chop definition; the muted guitar has no sustained energy, so this is what makes it audible |
| EQ_AIR | (8000, +0.5) | High shelf at 8 kHz — very little air: damping and palm flesh remove the top by design |
| PAN | -0.25 | Centre-left guitar seat; double hard L/R at ±0.6 for funk/metal rhythm |

## RenderPipeline stem-label quirk

**Name quirk (cosmetic).** `GM_PROGRAMS[28] = "Electric Guitar (muted)"` → sanitized filename `Electric_Guitar_muted`. FluidR3 preset 28 = **"Palm Muted Guitar"** — the SF2 names the *technique*, the pipeline names the GM2 *program*. `STEM_LABEL = "Electric_Guitar_muted"` **matches the pipeline's real label** so stem-file lookups work (same discipline as the "Bag pipe"/"Shanai" and "Jazz Guitar" quirks). No routing impact.

## FluidSynth / SF2 notes

FluidR3_GM.sf2 preset 28 = "Palm Muted Guitar" — a dedicated muted sample set, not the clean guitar with a filter. It is audible across the full 28–84 range with no gaps, but the patch is a **one-shot**: the sample itself decays fast regardless of note length, so a long MIDI note does NOT produce a long sound. That is correct behaviour — write note lengths ≤ 0.25 beats for chops, and use `open_accent` (longer, higher velocity) when you want the patch to ring. Below 40 (E2) the patch plays the lowest sample looped and gets muddy — keep real writing ≥ 40.

## Identity

GM 28 = Electric Guitar (muted) — the palm-muted electric guitar. Archetypal sounds: Nile Rodgers' 16th-note "chick" on a Strat (Chic, "Le Freak"), Jimmy Nolen's funk chops with James Brown, Catfish Collins, and the palm-muted low-string chug of metal riffing (Metallica, Pantera) — plus the muted ska/reggae upstroke.

The muted guitar is a **rhythm instrument first**:
1. **Comp / groove** — a continuous 16th-note stream of chops and scratches; the guitar becomes part of the percussion section, defining the groove's subdivision rather than its harmony.
2. **Riff** — palm-muted chugs on the low strings alternating with open accents; the mute/open dynamic contour is the riff.
3. **Melody** — short staccato single-note lines and octave hooks; never a sustaining lead (use clean/jazz/distortion for that).

Line-instrument quirks:
- NOT a sustain voice — every note is an attack plus a decay. Write rhythmic density, not tied notes. If a phrase needs sustain, this is the wrong patch.
- Chords must stay SMALL: 2–4 notes (double stops, three-note chops). Six-string barre chords through a mute are a percussive smear, not harmony.
- The mute duration is the groove: alternate `funk_chop` (0.12) with `scratch` (0.05) and `ghost_note` (0.04) to get the hand-motion feel; all-identical durations sound like a machine.
- Velocity IS the dynamic: 30–40 ghosts, 75–82 normal chops, 90+ accents. The patch has little natural sustain, so a flat velocity layer disappears in a mix.
- Doubling quirk: double hard left/right with the SAME part (two takes) is the funk/metal standard — that is a stereo production technique, not unison doubling of two *different* patches. Never stack another melodic patch on the same pitches (2026-09-01 comb-filter rule).
- EQ: the muted guitar occupies roughly 150 Hz–4 kHz after damping; keep the bass below 150 Hz and let cymbals/keys own 4 kHz+.
