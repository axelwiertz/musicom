---
type: instrument
family: Vocal
name: Choir
midi_program: 52
gms: "Choir Aahs"
range_min: 40
range_max: 88
solo_range: [55, 79]
sweet_spot: [48, 76]
role: [pad, harmony, melody, countermelody, anthem, texture]
synthesis: [additive, singing_voice, phase_mod]
---

# Choir (Choir Aahs)

A **mixed chorus** singing a wordless open "ah": the ensemble voice of the
orchestra/pop production, not a solo singer. It is the sound of *many* trained
voices on one part — detuned, breathing at slightly different moments, with
individual vibratos that never lock.

## MIDI / GM

- **Program**: 52 (GM1 "Choir Aahs" — the 53rd entry, 0-based). The GM chorus
  patch is a sustained ensemble "ah" sample; it is the standard stand-in
  whenever a score says *coro / choir / aahs*.
- **Channel**: melodic channel (0–9). Channel 9 with program 52 triggers the
  drum-kit map instead — never put the choir on channel 9.
- **Enum note**: `structures/instrument.py` does **not** expose a choir member.
  Use the raw GM number 52 (the registry is the full KB; only 10 instruments
  are in `MidiInstrument`).
- **FluidSynth**: `discover_soundfont()` → FluidR3_GM.sf2 preset 52 =
  **"Ahh Choir"** (verified from the phdr chunk), preset 53 = "Ohh Voices"
  (the `human_voice` stand-in). Cosmetic SF2 naming only — **no routing
  impact**: the stem is labelled from the pipeline's GM_PROGRAMS list.
- **Stem label**: `GM_PROGRAMS[52] = "Choir Aahs"` → sanitized
  `trackXX_Choir_Aahs.wav` — matches `STEM_LABEL = "Choir_Aahs"`, **no quirk**.
- **Registry**: key `choir`, `by_name('choir')` and `by_name('choir aahs')`
  both resolve; `by_program(52)` is unique (no voice_like stand-in uses 52).

### The three "voice" instruments are different things

| Instrument | What it is | Engine |
|---|---|---|
| `choir` (this, GM52) | sampled/rendered **section** of many voices on one part, wordless "ah" | additive formant stack / FluidSynth |
| `human_voice` (GM53 stand-in) | **solo** synthetic singer — source–filter vocal-tract model, vowels, vibrato, jitter | `singing_voice` |
| `voice_like` family (GM20/59/80/81/106) | non-vocal instruments (kazoo, jaw harp, singing saw…) that merely *read* as vocal | `voice_like` |

Do not cross-register them: a choir is a pad/anchor, a solo voice is a lead.

## Range

A real mixed chorus (SATB) spans roughly E2 (bass bottom) to C6 (soprano top).
The GM chorus patch plays the whole keyboard but thins and loses its "section"
character at the extremes.

| Zone | MIDI | Pitches | Section / use |
|---|---|---|---|
| Full range | 40–88 | E2–E6 | writing band (patch span is wider; extremes thin out) |
| Bass | 40–55 | E2–G3 | bass section — roots, pedal tones, low "ah" bed |
| Tenor | 48–64 | C3–E4 | tenor line — inner voice, melody at pitch in pop keys |
| Alto | 53–72 | F3–C5 | alto — the body of the chord, most stable blend zone |
| Soprano | 60–88 | C4–E6 | soprano — top line, descant, anthem climax |

Empirical FluidR3 pitch sweep (RMS, velocity 74, held one bar): note 24 = 964,
36 = 988, 40 = 904, 48 = 1065, 60 = 1015, 72 = 1167, 84 = 1360, 88 = 1363,
96 = 1388. **Audible at every tested note, no gaps** — the chorus patch never
clips a composition. RMS *rises* with pitch (the sample is brighter and more
present up high), so a soprano line at the same velocity will read louder than
the bass: balance by lowering upper-voice velocity ~8–12 or by voicing more
basses (the classic SATB balance problem).

## Articulations

| Technique | Velocity | Duration | Timbre |
|---|---|---|---|
| Ah | 68–78 | full | sustained open vowel — the default choral gesture |
| Legato | 66–74 | full | seamless join; the choir never re-attacks inside a phrase |
| Swell | 58–78 | full | crescendo on a held chord (organ-like build) |
| Decrescendo | 60–52 | full | phrase-end taper — extremely idiomatic |
| Staccato | 72–78 | 0.3× | short "ah" — rhythmic choral stabs (needs a rhythmic double) |
| Marcato | 85–92 | 0.85× | hard "HAH" anthem hit on the downbeat |
| Hum | 48–56 | full | closed-mouth bed — low velocity reads as a hummed pad |

Soft-attack quirk: every onset is a *breath*, not a click. Attack is
~100–300 ms even at high velocity, so 16th-note choral stabs blur. If a line
needs punch, put the rhythm in the drums/piano and let the choir sustain — do
not try to make the chorus articulate fast figures.

## Timbre DNA

- **Ensemble unison (the defining trait)** — several voices per part, detuned
  by roughly ±5–20 cents (professional blend <10 cents, community choir 20–30).
  The result is slow amplitude beating (1–5 Hz ripple) and a wide, "soft" unison
  rather than the sharp single pitch of a soloist.
- **Vowel formants** — the open "ah": F1 ≈ 730 Hz, F2 ≈ 1090 Hz, F3 ≈ 2440 Hz
  (Peterson & Barney 1952). Partials sitting on F1/F2 carry the vowel; that is
  why the additive recipe boosts partials 2–4 (`choir_ah` = [1.0, 0.72, 0.55,
  0.60, 0.34, 0.22, 0.14, 0.09]).
- **Singer's formant / ring** — a 2.8–3.2 kHz energy cluster (Sundberg 1974)
  that lets a voice cut an orchestra. In a *section* the individual rings smear
  into a broad band: presence, not bite.
- **Breath / aspiration** — shaped noise around 1–5 kHz mixed at ~10%. Each
  singer's breath onset is staggered, which is what makes a choral attack feel
  soft and "wide" instead of synchronized.
- **Unsynchronized vibrato** — 4.5–6 Hz per voice with different phases and
  depths; the section average is a shimmer, not a wobble. Never modulate a
  whole choir with one LFO at full depth (that reads as a synth pad, not voices).
- **No consonants** — the GM patch is pure vowel. Words are impossible without
  a TTS/formant path; write wordless "aah/ooh" lines or use `human_voice`.
- **Dynamic range by mass** — a choir gets louder by singing harder *and* by
  adding voices; its ff is dense, not distorted. Velocity 50–60 already reads
  as a full soft chord.

## Role in Arrangement

- **Pad / harmony bed** — the warmest sustained pad in the KB (strings 2.6 s
  reverb vs choir 2.8 s): R&B/gospel organ replacement, cinematic beds.
- **Anthem / hook** — sustained "aah" hook over a drop or final chorus; the
  classic epic-pop/cinematic lift.
- **Melody** — works for slow, sustained melodies (hymns, ballads, folk
  anthems). Not for melisma or fast runs — that is `human_voice` territory.
- **Countermelody** — long-note line against a busy lead; its soft attack sits
  under a plucked/percussive lead without masking it.
- **Texture / tension** — low cluster "ah" under a scene; dissonant minor-second
  clusters are a film-score staple (keep them above C3 or they turn to mud).
- **NOT** a bass instrument below E2, **not** a rhythmic comping voice, **not**
  a solo improviser.

## Synthesis Engines (musicom)

1. **Additive** (`sound/synthesis/additive.py`, SoundWave) — **primary**. A
   chorus *is* a formant-shaped harmonic stack, N detuned voices wide: use
   `ADDITIVE_HARMONICS["choir_ah"]` (open vowel) or `["choir_hum"]` (dark hum
   bed), attack 0.18 s, detune ±0.009, stack 5, release 0.45 s, sustain 0.88,
   vowel "a" with formants (730, 1090, 2440) Hz, breath 0.10.
   **Engine quirk (inherited from synth_pad, 2026-10-12)**:
   `apply_overtones` leaves `self.frequency` at the TOP partial, so the ADSR
   grid interval ≈ 1/(duration × top_partial) s and the decay values are
   PER-GRID-STEP — use `decay_S ≈ 1e-4` to hold a 2 s chord. Verified: late
   sustain weight 0.718 (gate ≥ 0.45). Length proportions passed to
   `get_adsr_weights` MUST sum to exactly 1.0 (asserted in the engine) —
   e.g. [0.18, 0.07, 0.65, 0.10].
2. **SingingVoice** (`sound/synthesis/singing_voice.py`) — **secondary**, the
   "real section" route: render 4–5 voices with `voice_type="alto"`, vibrato
   5.2 Hz ±0.28 semitones (narrower than a soloist's ±0.45), aspiration 0.22,
   shimmer 0.05, per-voice seeds, detuned by ±0.9%. Verified: single voice
   peak 0.800, sustain/peak 0.290; 5-voice stack rms 0.0878 — **normalize the
   stack** (sum ÷ N or ÷ √N) because the raw sum peaks at 1.72 and would clip.
3. **PhaseModSynth** (`sound/synthesis/phase_mod.py`) — tertiary "vocal pad":
   sine carrier, ratio 2.0, depth 1.6, attack 0.2 s, release 0.45 s, sustain
   0.85 (FM_DEFAULTS). Cheaper, glassier; good under a busy mix.
4. **FluidSynth** (default production path) — preset 52 "Ahh Choir". The patch
   has a built-in slow swell and chorus; that is why REVERB_TAIL is shorter
   than a synth pad's (the sample already carries some space).

## Production

- **Reverb**: hall/church 2.8 s (string ensemble 2.6, synth pad 3.2). A choir
  is *always* in a room — dry choir sounds like a Mellotron. Pre-delay 20–30 ms
  keeps the vowel intelligible.
- **EQ**: cut ~350 Hz −2.5 dB (stacked "ah" formants pile up in the low-mid);
  boost ~3 kHz +2 dB (vowel presence); highshelf +7 kHz +1 dB only — a choir is
  not a cymbal, too much air turns it into a synth pad.
- **Pan**: center for the composed stem; ±0.35 for a wide double-tracked
  chorus (slightly narrower than the synth pad's ±0.4 — voices need a coherent
  centre).
- **Layering**: idiomatic doubling is **octaves** (choir + choir 8vb) or
  **thirds/sixths** with a different patch. NEVER unison with another melodic
  patch on the same pitches — the 2026-09-01 comb-filter lesson applies exactly
  here (choir + string ensemble unison = buzz). Drums or a low bass an octave+
  below are fine.
- **Balance**: velocity is not loudness only — it is *how many voices* are
  singing. 50–58 = small ensemble/hum, 68–76 = full chorus, 84–92 = tutta
  forza anthem. Keep the soprano 8–12 velocity units under the bass for a
  blended chord.

## Verification

Pattern: `_test/verify_choir.py` (solo render — one voice, one track).

- Zero-drift: 5-note SATB chord (43/48/55/60/64) held to BAR, `validate()`
  → True (OK)
- MIDI: `_test/choir_test.mid` (81 bytes)
- WAV (solo, FluidR3 via `discover_soundfont()`): `_test/choir_test.wav`
  (1,077,292 bytes), spectral buzz check 4–8 kHz = **2.0%** (gate < 20%)
- Stems: `track00_Choir_Aahs.wav` (1,077,292 bytes) from the real
  `RenderPipeline.render_stems`
- Pitch sweep: preset 52 audible at 24/36/40/48/60/72/84/88/96, no gaps
- Registration: `by_name('choir')` → Choir Aahs, `by_name('choir aahs')` →
  Choir Aahs, `by_program(52)` → Choir Aahs, `by_program(53)` → Human Voice
  (distinct), `in_sweet_spot(64)` = True, `in_sweet_spot(24)` = False
- Additive envelope: late-sustain 0.718 (collapse gate ≥ 0.45)
- SingingVoice stack: rms 0.0878, no phase cancellation

## Stem label / quirks

- `GM_PROGRAMS[52] = "Choir Aahs"` → stem `trackXX_Choir_Aahs.wav`; FluidR3
  preset 52 spells it "Ahh Choir" — cosmetic only, **no routing impact**
- Program 52 has **no collision**: 53 (human_voice), 54 (Synth Voice, unused),
  80 (talkbox), 81 (singing_saw) are all distinct entries. (Lesson learned
  while picking this instrument: GM80 AND GM81 are both claimed by voice_like
  stand-ins, so a new "saw lead" registration there would fail `by_program`
  uniqueness and share the `Lead_2_sawtooth` stem filename.)
- Channel quirk: melodic channel (0–9); channel 9 triggers the drum map and the
  stem comes out `Drums`
- Choir sections in the registry table sort under **Vocal** (family), not
  Woodwind/Keys — do not "fix" the family
- The `voice_like` umbrella still renders two duplicate "Vox Humana" rows in
  `registry_table()` (pre-existing: umbrella + FAMILY member both map to the
  same label) — cosmetic table noise, unrelated to this entry
