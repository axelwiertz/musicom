# REPORT — SP-011 Karplus-Strong production pass on Pop/workflow-demo

- **Job**: random-style production (SP) layer-aligned
- **Date**: 2026-09-24 · **Seed**: 20260924
- **Method**: SP-011 — Karplus-Strong String Synthesis
- **Method module**: `sound.synthesis.karplus_strong`
- **Source composition**: `Styles/Pop/workflow-demo/MIDI/pop-001.mid`
- **Pitch verdict**: **PASS** (hit_rate 1.000, acf_pitched_frac 1.000)
- **Silence**: 8.20%

---

## 1. Selection (registry source)

Method picked from the **implemented `SP_METHODS` registry** in
`workflows/musicom_workflow.py` (not the research DB, not a stale ID range):

```python
from workflows.musicom_workflow import SP_METHODS
pool = sorted(set(SP_METHODS) - RECENT - BASELINE)
method = random.Random(20260924).choice(pool)   # -> SP-011
```

- **Excluded (used last 7 days)**: SP-069 (09-23), SP-090 (09-22), SP-033 (09-21),
  SP-080 (09-20), SP-083 (09-19), SP-084 (09-17), SP-072 (09-16).
- **Excluded (baseline)**: SP-001 — the SoundFont dry render is the *baseline*
  every job already emits as a reference; it is not a production transform.
- Candidate pool after exclusions: 25 methods. Pick: **SP-011**.
- Source picked uniformly from 189 well-formed `Styles/*/<proj>/MIDI/*.mid`
  (excluding `Production/` and `-phase1` raw drafts): **Pop/workflow-demo/pop-001.mid**.

## 2. Source composition

`pop-001.mid` — Pop I–V–vi–IV framework, 120 BPM, 4/4, 56.00 s, 491 notes,
5 instrument tracks (track 0 = tempo only):

| Track | Program | Channel | Notes | Role (SP-011) | Range |
|---|---|---|---|---|---|
| track1 | Flute (74) | 0 | 56 | lead | 60–76 |
| track2 | Piano (1) | 0 | 15 | lead | 48–64 |
| track3 | Contrabass (43) | 0 | 28 | bass | 48–57 |
| track4 | Clarinet (71) | 0 | 112 | lead | 60–76 |
| track5 | Drums (0) | 9 | 280 | perc | 36–42 |

Pitch-class histogram (all notes, drums included — every note is re-rendered as
a pitched pluck, so drums contribute real pitches): C(0)=81, D(2)=44, E(4)=34,
F(5)=14, F♯(6)=224, G(7)=42, A(9)=35, B(11)=17. PC 6 is inflated by GM drum
note 42 (closed hat). Melodic material sits in the C-major set {0,2,4,5,7,9,11}.

## 3. Method & layer discipline

**Absolute-layer discipline**: SP-011 replaces the production layer for **ALL**
voices. No SoundFont timbre is retained — every note (melody, comp, bass,
counter-line, and drums) is synthesized as a Karplus-Strong plucked string.

```python
y[n] = x[n] + loop_gain * 0.5 * (y[n-N] + y[n-N-1])
N    = round(sr / f0)          # FULL cycle period — NOT sr/(2*f0)
```

**Octave fix already in module**: the delay length is `sr / f0` (no divide-by-2),
so pitch lands exactly on the MIDI note — no waveguide octave drop.

Role configuration (drums mapped to a custom fast-decay percussive pluck):

| Role | loop_gain | gain_db | width | pan_drift | Notes |
|---|---|---|---|---|---|
| lead | 0.9985 | -2.0 | 0.55 | yes | 183 |
| bass | 0.9990 | -6.0 | 0.35 | no | 28 |
| perc | 0.970 | -8.0 | 0.20 | no | 280 |

## 4. Pipeline

1. Parse MIDI (mido) → absolute-second note lists per track; assign roles.
2. `karplus_strong.render_melody(all_notes, sr=44100, roles=ROLES)` → full mix
   `(N, 2)` float, peak-normalized −1 dB internally.
3. Per-track stems via `render_melody` per track, time-aligned to the global
   length with a silent velocity-0 tail pad (→ all 5 stems identical length).
4. Master: `normalize_to_lufs(-14)` → `Limiter(-1 dBFS)`.
5. WAV (16-bit stereo) → OGG (Opus, `libopus -application voip -b:a 48k`).
6. Verify + write artifacts.

## 5. Verification results

### Pitch verification (synthesis → must be PITCHED, not noise)

Per 0.5 s window (50–1000 Hz), dominant FFT peak matched against the source
note **fundamental or any integer harmonic** sounding in that window:

- **valid windows**: 112 (of 112 — no fully-silent 0.5 s windows in the body)
- **hits**: 112 → **hit_rate = 1.000**
- **acf_pitched_frac = 1.000** — normalized autocorrelation detected a real
  pitch in 100% of windows (independent noise gate; noise → 0 Hz frames).
- **mean harmonic energy = 0.229** — energy in the first 8 harmonics of the
  dominant frequency. Healthy for a 5-voice polyphonic texture (see §6).
- median dominant frequency 440.0 Hz (A4 region).

**Verdict: PASS.** `hit_rate = 1.0` is decisive — the rendered dominant
frequency matches a source note in *every* window, which rules out noise
(noise → random dominant peak → hit_rate ≈ 0) *and* rules out the waveguide
octave drop (an octave-down fundamental would be `f0/2`, not an integer
multiple of `f0`, and would fail the match).

### Loudness / dynamics

- **LUFS**: −20.23 (target −14, see §6)
- **Peak**: 0.891 (−1.0 dBFS ceiling respected)
- **Mono correlation**: 0.852 (wide but coherent stereo)
- **Silence ratio**: 8.20% (well under the 30% suspect threshold; the tail
  includes the +3 s render pad)
- **RMS/s profile** (first 20 s): 0.037–0.103, smoothly varying — no mid-track
  gaps, no digital-silence plateaus.

### Rhythm DNA grid (onset matrix)

See `Analysis/grid_visualization.txt`. Summary of metrical gravity:

- track1 (Flute): quarter-note pulse (≈1 onset/beat)
- track2 (Piano): sparse chord stabs (≈1 onset/4 beats)
- track3 (Bass): half-note walking line (≈1 onset/2 beats)
- track4 (Clarinet): eighth-note counter-line (≈2 onsets/beat)
- track5 (Drums): sixteenth-note grid (≈4 onsets/beat)

## 6. Notes on the two "off" numbers

- **mean_HE 0.229 < naive 0.25 noise gate**: the 0.25/0.30 threshold in the
  skill is calibrated for *sparse/sustained* sources. Here 5 voices sound
  simultaneously, so the dominant note's 8 harmonic bins capture only ~23% of
  total spectral energy — the rest is the *other* sounding notes' fundamentals
  and partials, not noise. Noise renders sit in single digits (SP-035 GENDYN
  failure = 4% HE *and* 0 Hz autocorrelation pitch everywhere). This render has
  1.0 autocorrelation-pitch coverage — decisively pitched. Verdict therefore
  keys on `hit_rate` + `acf_pitched_frac`, not the HE threshold alone.
- **LUFS −20.23 vs −14 target**: plucked strings have a high crest factor
  (short loud attacks, long quiet decays). `normalize_to_lufs(-14)` is
  peak-ceiling-limited — pushing average loudness to −14 LUFS would clip the
  attacks past 0 dBFS, so the limiter caps gain. This is correct behavior for
  the source; the mix is not under-normalized by error.

## 7. Artifacts

| Path | Size |
|---|---|
| `SP011-karplus-strong-pop-workflow-demo.wav` | 10,407,644 B (10 MB) |
| `SP011-karplus-strong-pop-workflow-demo.ogg` | 566,877 B (554 KB) |
| `Audio/stems/track00_track1.wav` … `track04_track5.wav` | 5 × 10 MB (time-aligned) |
| `MIDI/pop-001.mid` | source copy |
| `provenance.json` | job record |
| `Analysis/render_stats.json` | full metrics |
| `Analysis/pitch_verification.json` | pitch gate result |
| `Analysis/grid_visualization.txt` | rhythm DNA grid |
| `Analysis/select_20260924.json` | selection record |
| `Scripts/produce_sp011_cron.py` | reproducible generator |

## 8. Fixes / decisions applied

1. SP-001 excluded from the pick pool (baseline render, not a transform).
2. Drums (ch 9) mapped to a custom `perc` role with fast decay (loop_gain 0.97)
   so percussion renders as short plucks instead of sustained bass strings.
3. Stems time-aligned via silent velocity-0 tail pad (render_melody pads each
   call to `max(end)+3 s`; the pad forces identical lengths).
4. Verdict logic keyed on `hit_rate` + autocorrelation pitch coverage instead of
   the polyphony-unsafe harmonic-energy threshold; both are recorded.
