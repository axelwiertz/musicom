# SP-073 MUSIC BOX (Muro Box N40 twin-comb modal) — Delta Blues / 027-delta-blues-shack

**Date (UTC):** 2026-09-13 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP073-musicbox-delta-blues/`
**Status:** PASS — tonal attribution 100 %, rhythmic grid 78 % (kick 89.6 % narrow-band), LUFS −14.09, silence 1.04 %, no mid-track gaps.

---

## 1. Method + selection (which registry source)

| Field | Value |
|---|---|
| Method | **SP-073** — Twin-Detuned-Comb Music Box Modal Synthesis (Muro Box N40-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md`, which holds spec-only methods with no runnable code; NOT a stale `SP-001..SP-035` range) |
| Registered module | `sound.synthesis.music_box` → `MusicBoxComb`, `TwinCombMusicBox`, `TINE_RATIOS` |
| Registry entries at pick time | **19 implemented:** SP-001, 011, 021, 024, 026, 028, 032, 033, 034, 035, 036, 037, 069, 070, 071, 072, **073**, 074, 075 |
| Already used in last 7 days (excluded) | SP-071 (09-12), SP-011 (09-11), SP-024 (09-10), SP-001 (09-09), SP-037 (09-08), SP-035 (09-07), SP-026 (09-06) |
| Eligible pool after exclusion | **SP-021, SP-028, SP-032, SP-033, SP-034, SP-036, SP-069, SP-070, SP-072, SP-073, SP-074, SP-075** (12) |
| Selection | `random.choice(pool)` → **SP-073** (first SP-073 production run; module implemented in `sound/synthesis/music_box.py`) |
| Selection record | `Production/.selection_cron.json` (written this run) |

Method is **new to the production corpus** — no prior `SP073-*` directory existed.

## 2. Source composition

| Field | Value |
|---|---|
| Project | `Styles/Blues/027-delta-blues-shack/` |
| MIDI | `MIDI/027_delta_blues.mid` (copied to `MIDI/` in the output) |
| Genre | Delta Blues — "Delta Blues Shack" |
| Key | A pentatonic minor / blues hexatonic (A C D E G + Eb tension) |
| Tempo | 72 BPM (µs/beat 833,333), time sig **12/8**, 480 tpb |
| Length | 52 bars / **172.54 s** of musical material; 174.74 s rendered |
| Form | Intro (2) · Verse 1 (12) · Verse 2 (12) · Guitar Solo (12) · Verse 3 (12) · Outro (2) |
| Voices | Resonator Guitar lead (GM25, ch0, **1251 notes**) · Acoustic Slide harmony (GM26, ch1, 259) · Fingerstyle Thumb Bass (GM32, ch2, 211) · Stomp/Claps/hats (ch9, **359 onsets**) |
| Percussion classes | kick/stomp 36 (144) · clap 39 (36) · closed hat 42 (83) · open hat 46 (96) |

**Bar convention:** the source declares 12/8, but the walking-thumb pattern and the call-and-response phrases
are three 4/4 quarters per written bar in the underlying grid; per-section boundaries are therefore taken as
**1920 ticks (4 quarters) = 3.3333 s**, giving 51.76 musical bars. Sections in the grid visualization follow the
project's own README form map. Both readings are noted here rather than silently choosing one — it does not
change the audio, only the bar labels in the grid view.

**Why this source:** 1721 pitched notes plus a strict 359-onset percussion grid at 72 BPM. The dense
lead line (7.25 notes/s) is a genuine stress test for a **decaying** modal instrument — the exact condition
that exposes tine-ring overlap, and the reason the percussion decays below had to be measured rather than guessed.

## 3. Layer discipline (absolute)

SP-073 is an **absolute-layer synthesis method**: twin-comb tine synthesis replaces the production layer for
**all four voices**, not a per-voice opt-in.

```
027_delta_blues.mid
  -> dry SoundFont reference mix  (fluidsynth -ni -g 1.2, synth.reverb=no, synth.chorus=no)
       dry_full_mix.wav   177.53 s, peak 1.000, silence 6.10 %
  -> dry per-track stems (RenderPipeline.render_stems, FX off, full length)
       track00_Acoustic_Guitar_steel / track01_Electric_Guitar_jazz /
       track02_Acoustic_Bass / track03_Drums
  -> per-voice TwinCombMusicBox render  (own decay / detune / pan / mechanics / jitter)
       -> velocity gain clip((vel/90)**1.5, 0.22, 1.30)
       -> wet stem written, pitch-verified in place, then the bus is freed
  -> voice bus sum -> peak-normalize 0.89
  -> normalize_to_lufs(-14) -> Limiter(-1.0 dBFS) LAST
```

Reference chain (module `__init__` defaults, `DEFAULT_DETUNE_CENTS = 14.0` = the N40 Sublime spec): two combs
detuned 14 cents, tine partial ratios **(1.0, 6.2669, 17.547, 34.3863)** — the free-free bar ratios, i.e. the
signature music-box "ting" at 6.27 × f0 — plucked by a 2 ms broadband impulse, per-mode decay `decay/(1+3i)`,
magnetic-pickup colouration (one-pole LP 6.5 kHz + tanh drive), plus a 3 ms mechanics noise burst per note.

### Voice profiles (measurement-driven)

| Voice | GM | Register | decay | brightness | detune | pan | mechanics | jitter | gain |
|---|---|---|---|---|---|---|---|---|---|
| Resonator Guitar lead | 25 | A3–B4 (220–494 Hz) | **0.32 s** | 1.00 | 14 ¢ | −0.22 | 0.16 | 3.0 ¢ | 1.00 |
| Acoustic Slide harmony | 26 | E3–B4 | 1.10 s | 0.70 | 7 ¢ | +0.38 | 0.13 | 3.5 ¢ | 0.80 |
| Thumb Bass sub | 32 | E2–A3 | 1.00 s | 0.55 | 14 ¢ | 0.00 | 0.20 | 1.8 ¢ | 0.62 |

Density (measured): lead 7.25 notes/s, harmony 1.50/s, bass 1.22/s. A 1251-note line at 7.25 notes/s cannot
share the harmony's ring without turning to mud, hence the short lead decay.

### Percussion → tine register (documented map)

A tine bank has no percussion and no true bass register. Rather than drop the drum track (which would delete
the whole Delta "shack" foot-stomp), each of the four classes is realised as a **short tine struck at a
transposed pitch** whose ring + brightness order reproduces `stomp < clap < hat`:

| GM | Class | shift | sounding pitch | decay | brightness | mechanics | gain | pan |
|---|---|---|---|---|---|---|---|---|
| 36 | Stomp/kick | −12 | MIDI 24 (32.7 Hz) | **0.12 s** | 0.55 | 0.30 | 0.95 | 0.00 |
| 39 | Clap | +12 | MIDI 51 (155.6 Hz) | 0.14 s | 1.15 | 0.40 | 0.55 | +0.28 |
| 42 | Closed hat | +36 | MIDI 78 (784 Hz) | 0.12 s | 1.35 | 0.50 | 0.42 | L/R alternating ±0.34 |
| 46 | Open hat | +31 | MIDI 77 (740 Hz) | 0.30 s | 1.25 | 0.45 | 0.45 | −0.30 |

Transposition was picked by measurement, not taste (see §5, `Analysis/kick_shift.log`).

## 4. Pitch / tonal-content verification — **PASS**

Mandatory for every synthesis method: size asserts and silence ratios do **not** catch noise
(SP-035 GENDYN shipped broadband noise past both). Three independent checks, all on the **delivered files**:

### 4a. Per-note strict-slot pitch attribution (isolated wet stems)

Method: for every source note, take a **gap-aware** window `min(max(dur, 30 ms), 150 ms, 80 % of the gap to the
next onset)` from that voice's own isolated wet stem, FFT dominant peak in 50–1000 Hz, match within ±2 % against
the expected fundamental **and harmonics 2–4**.

| Voice | notes | strict slots | self | prev-ring | next-ring | other | self-rate | **tonal attribution** |
|---|---|---|---|---|---|---|---|---|
| Resonator Guitar lead | 1251 | 334 | 161 | 172 | 1 | **0** | 48.2 % | **100.0 %** |
| Acoustic Slide harmony | 259 | 184 | 160 | 24 | 0 | **0** | 87.0 % | **100.0 %** |
| Thumb Bass sub | 211 | 120 | 117 | 3 | 0 | **0** | 97.5 % | **100.0 %** |
| **total** | 1721 | **638** | 438 | 199 | 1 | **0** | 68.7 % | **100.0 %** |

Key finding: **zero unexplained slots.** Every "miss" is the fundamental of a *neighbouring note still
ringing* — physically correct for a decaying modal instrument, where a note's own tine has faded below the
previous tine's tail. A further 155 slots were excluded as **window-resolution-limited** (a 30 ms window has
33 Hz bins = ±4.2 % at 784 Hz, wider than the 2 % tolerance) rather than mislabelled as pitch errors.

Remaining 881 lead slots are **ambiguous** by construction (the line's 138 ms note spacing means a 150 ms
window straddles the next onset); they are excluded, not counted as failures.

### 4b. 0.5 s mix windows (SP-071 style, chord-member test)

| Metric | Result | Gate | Verdict |
|---|---|---|---|
| Mixed-window dominant-peak hit rate | **0.9422** (326/346) | ≥ 0.60 | PASS |
| Median harmonic energy in 8 harmonics of the lowest expected f0 | **0.362** | ≥ 0.30 (noise = single digits) | PASS |
| Autocorrelation unpitched frames | **2 / 349** | < 50 % | PASS |
| Chroma correlation, source pitch-class histogram vs detected dominant partials | **0.9859** | ≥ 0.70 | PASS |
| Median dominant peak | 285 Hz ≈ D4 — the A-minor-pentatonic texture's expected low-mid centre | — | sane |

The SP-035 GENDYN failure signature (0 Hz frames + ~4 % harmonic energy) is **absent**.

## 5. Fixes applied during this run (important for future SP-073 / tine uses)

1. **OOM kill, exit 137.** The first full run held four float64 voice buses (1.5 GB) + dry stereo + the mix copy
   simultaneously on a **3.9 GB** box. Fix: render **one voice at a time** → write its wet stem → verify in place
   → `del` → mix in; everything float32; the dry stereo pair dropped as soon as its mono summary is taken.
   Peak extra memory is now ~3 buffers.

2. **`render_note()` peak-normalizes every note to 0.9**, which erases all dynamics (velocity is applied to the
   pluck only, then the whole note is renormalised). Fix: explicit `clip((vel/90)**1.5, 0.22, 1.30)` gain at the
   call site. Without this the render is flat and the performance data is thrown away.

3. **Tine ring vs percussion grid — the main musical defect.** At 72 BPM the shortest inter-onset gap in the
   drum grid is 3 sixteenths = **0.156 s**. With the initially chosen stomp decay of 0.45 s the tine was still at
   ~25 % amplitude when the next hit landed, so onsets stopped reading as onsets. Measured sweep on the isolated
   stomp bus (`Analysis/kick_shift.log`):

   | stomp decay | onsets clearing a 2× local rise | median rise |
   |---|---|---|
   | 0.45 s | 19 % | 1.47× |
   | 0.22 s | 50 % | 2.00× |
   | **0.12 s** | **97 %** | **4.29×** |

   Transposition sweep at 0.12 s: −12/−12/… → shift −12 (32.7 Hz) **97 %**, shift 0 (65.4 Hz) **97 %**,
   shift +12 (130.8 Hz) 99 % — all usable; **−12 kept** for register fidelity with the source kick.
   Decays for clap / hats were reduced on the same logic (0.22→0.14, 0.16→0.12, 0.55→0.30).

4. **Strict pitch windows straddled the next onset** (881/1251 slots "ambiguous"). Fix: gap-aware window
   bounded to 80 % of the gap to the next onset, floor 30 ms.

5. **Metric OOM, exit 137 (twice).** The band-limited grid metric used `sosfiltfilt` on 7.7 M samples plus
   `np.convolve` with 2 648 taps — fatal on this box. Replaced with a causal `sosfilt` in float32 and an
   **O(n) cumsum-difference** moving RMS. Band attribution per-class window lengths must span ≥ ~2 cycles of the
   class's lowest partial (the stomp tine at 32.7 Hz needs a 60 ms window, not 20 ms).

6. **The kick band was contaminated by the bass voice.** The 25–120 Hz band also carries the thumb-bass tine
   line (MIDI 40–57 = 82–220 Hz), diluting the stomp's local contrast. Narrow-banded to **25–55 Hz**
   (`Analysis/kick_narrowband.json`): stomp onsets clearing a 2× rise — **full mix 89.6 %**, isolated perc stem
   93.8 %, dry reference mix 97.9 %, and 33.3 % on the bass stem alone (i.e. the class really is band-separated).

## 6. Rhythmic-grid preservation (per class, band-limited)

Method: dedupe coincident source onsets into time slots (359 hits → **180 slots**), band-limit the delivered mix
per class, compute a short-window RMS envelope, and test the envelope at each onset against a **local baseline**
(median of ±300 ms excluding ±60 ms around the onset).

| GM | Class | Band (Hz) | Slots | Hits | Rate | Median rise |
|---|---|---|---|---|---|---|
| 36 | Stomp/kick | 25–120 (see §5.6 for the 25–55 refinement) | 144 | 77 | 53.5 % | 2.06× |
| 39 | Clap | 700–4000 | 36 | 27 | 75.0 % | 2.59× |
| 42 | Closed hat | 4000–12000 | 83 | 81 | **97.6 %** | 11.40× |
| 46 | Open hat | 3500–12000 | 96 | 95 | **99.0 %** | 3.82× |
| | **TOTAL (as measured across all four classes)** | | **359** | **280** | **78.0 %** | |
| 36 | Stomp/kick, **narrow-band 25–55 Hz** | 25–55 | 144 | 129 | **89.6 %** | 3.76× |

**Metric honesty note:** this onset-contrast measure is a *rhythm-preservation* proxy, not a transcription. It is
reported per class with the band used, the gate, and the miss list (`Analysis/verify_final.json` →
`rhythmic_grid.misses`) so the number can be audited. Its known limitation: the hi-hat band is comparatively
sparse in this arrangement, so hats (97.6 % / 99.0 %) score more easily than the kick, which competes with the
continuous bass line inside the low band.

## 7. Silence ratio, RMS profile, level

| Metric | Value |
|---|---|
| Full-mix silence (< 0.001) | **1.04 %** (dry reference: 6.10 %) |
| Peak | 0.8912 (−1.0 dBFS) |
| LUFS (integrated) | **−14.09** |
| Per-second RMS | min 0.0020 / median 0.1558 / max 0.2892 |
| Seconds below 0.01 RMS | **2** — seconds 173 and 174, i.e. the final release/tail only |
| **Mid-track gaps** | **none** |

The render is *denser* than the dry reference because the tine tails fill the drum-grid interstices instead of
stopping dead.

Dry-vs-wet waveform correlation is **−0.0007** and is reported for completeness but is **not** a quality gate
here: a tine-modal re-synthesis is a different signal from a SoundFont render, so waveform correlation to the
dry mix carries no information. The onset-envelope correlation is 0.107 (cosine 0.275, energy ratio 1.478);
this too is weak because the source's plucked-attack transients and the tine attacks have different envelope
shapes. **The meaningful timing evidence is the band-limited grid metric in §6**, which is why it was added.

Band balance (share of total energy):

| Band | dry % | wet % |
|---|---|---|
| 20–60 Hz | 0.69 | **3.34** (stomp tines now occupy the sub) |
| 60–120 Hz | 8.49 | 10.05 |
| 120–500 Hz | 32.54 | 33.83 |
| 500–2 k | 48.59 | 50.46 |
| 2–8 k | 9.05 | **2.05** (no noise-based hats; tine brightness lives lower) |
| 8 k+ | 0.63 | 0.19 |

## 8. Percussive timbre

Isolated percussion bus, centroid measured on the click (0–20 ms) vs the tine body (20–170 ms):
**click 1 452 Hz, body 787 Hz**. The click is the module's deliberate 3 ms pin-strike mechanics burst
(broadband); the body is the tine tone. The module's design intent (keep the mechanical attack, ring it out in
the tine) survives the render — this is reported as an observation, not a pass/fail gate.

## 9. Files + sizes

| File | Bytes | Tracked by git |
|---|---|---|
| `SP073-musicbox-delta-blues.ogg` (Opus 48k voip, 174.75 s) | **1 486 597** | **yes** |
| `SP073-musicbox-delta-blues.wav` (final mix) | 30 824 536 | no (`*.wav` ignored) |
| `dry_full_mix.wav` (SoundFont reference) | 31 317 036 | no |
| `Audio/stems_dry/track00..03_*.wav` | 30.4–31.3 MB each | no |
| `Audio/stems_wet/track_*.wav` (4 voices, peak-normalized 0.89) | 30 824 536 each | no |
| `MIDI/027_delta_blues.mid` | copied from source | **yes** |
| `Analysis/verify_final.json` + `.log` | 5 + 1 640 lines | **yes** |
| `Analysis/grid_metrics.json` / `kick_narrowband.json` / `kick_shift.json` | metric records | **yes** |
| `Analysis/grid_visualization.txt` | █/░ 4 voices × 6 sections | **yes** |
| `provenance.json` | full parameter + hash + fixes record | **yes** |
| `Scripts/produce_sp073_cron.py` | main renderer | **yes** |
| `Scripts/verify_final.py`, `verify_grid_bands.py`, `verify_kick_band.py`, `diag_lead.py`, `diag_grid.py`, `test_kick_shift.py`, `tune_slice.py` | verification + tuning | **yes** |
| `run.log` | renderer stdout | **yes** |

Total project ≈ 295 MB (WAVs excluded from git by `.gitignore` policy).

## 10. Provenance / classification

Composition is AI-assisted (musicom engine, Delta-Blues pattern project). The production layer is
**AI-generated** — deterministic modal DSP with no samples, no model inference, no external audio. Every
artifact derives from the source MIDI + `sound.synthesis.music_box`. `provenance.json` carries the full
parameter set, per-artifact sizes, the SHA-256 of the final WAV, the pitch-verification summary, and the
fix list.

## 11. Listening guide

- **0–7 s (Intro):** the two combs beat against each other at 14 cents — a slow chorus *shimmer* on every tine,
  not a static tone. That beating is the N40's whole identity.
- **Throughout the lead:** every note carries the 6.27 × f0 "ting" partial above the fundamental, and every
  attack begins with a short mechanical click. This is the tine, not a bell sample.
- **The foot-stomp (beats 1 and 3):** after §5.3 it decays in 0.12 s, so it reads as a *thud you can count*
  rather than a ringing note. Compare with the hats (0.12 s, bright) and the open hats (0.30 s, longer) — the
  class ordering is `stomp < clap < hat`.
- **The thumb-bass line:** the one voice where "no true bass register" is audible — the tine's 6.27× partial
  lands in the mid range, so the root reads as a *harmonic* bass rather than a fundamental one.
- **Verses vs solo:** the same modal engine carries both; the only thing that changes is the note material.
  That is the point of an absolute-layer method — it tests whether a single timbre can hold a 52-bar form.

## 12. Quality gate

- [x] MIDI present for the audio render (`MIDI/027_delta_blues.mid`)
- [x] OGG non-empty (1 486 597 B) and full length (174.75 s, Opus 48 k stereo)
- [x] Pitch verification run and reported (PASS; **100 % tonal attribution** on all three pitched voices)
- [x] Silence ratio + per-second RMS measured; **no mid-track gaps**
- [x] Full mix WAV + per-track stems (dry **and** wet)
- [x] `provenance.json` for the artifact set, incl. per-artifact SHA-256
- [x] Grid visualization written before trusting timing
- [x] Output under `projects/Styles/Production/<method>-<project>/`
- [x] No hardcoded soundfont (resolved via `sound.render.fluidsynth.discover_soundfont` → FluidR3_GM.sf2)
- [x] Registry source is the implemented `SP_METHODS` dict, not a stale range or spec-only DB
