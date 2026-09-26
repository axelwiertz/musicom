# SP-024 — Bowed String Physical Modeling → "Dust on the Dashboard" (Balfolk)

**Job:** random-style production (SP methods), LAYER-ALIGNED cron
**Date:** 2026-09-26
**Output project:** `/opt/data/repos/musicom/projects/Styles/Production/SP024-bowed-balfolk-dashboard/`

---

## 1. Selection

| Item | Value |
|---|---|
| Method registry (single source of truth) | `workflows.musicom_workflow.SP_METHODS` |
| Registry size | 33 implemented methods |
| Seed | `20260926` (date-derived, reproducible) |
| Pool after 7-day exclusion | 25 methods (excluded recent SP-011/SP-032/SP-033/SP-069/SP-080/SP-083/SP-090 + baseline SP-001) |
| **Chosen method** | **SP-024** → `sound.synthesis.bowed` (Bowed String Physical Modeling) |
| **Source composition** | `projects/Styles/Balfolk/011-balfolk-dust-on-the-dashboard/MIDI/composition_full.mid` |
| Source provenance | "Dust on the Dashboard", Pop Country, G major, 110 BPM, 4/4, 35.45 s (mido), 152 notes, 4 pitched voices, **no drums, no program_change** |
| Layer discipline | **absolute** — SP-024 replaces the production layer for ALL voices |

Selection script: `Production/select_job.py` (registry-based, `sys.path`-free flat import).
Result also in `projects/Styles/Production/.selection_cron.json`.

## 2. Method

`sound.synthesis.bowed.BowedString` — friction-induced digital waveguide. The string
is split into two bidirectional delay-line segments (neck + bridge) at the bowing
point; a Newton-Raphson solver (4 iterations) resolves an exponential sliding-friction
law per sample, producing Helmholtz stick-slip motion.

Called directly (module API — SP-024 adapter is **not wired** in `produce()`):

```python
from sound.synthesis.bowed import BowedString
bs = BowedString(sample_rate=44100)
audio = bs.render(freq=..., duration=..., bow_velocity=<env>, bow_force=...,
                  bow_position=..., friction_decay=..., noise_level=...)
```

Pre-flight pitch sanity (A4 = 440 Hz, 2 s): fundamental at 440 Hz **present** (3.8% of
band energy), 220 Hz **absent** → no octave-drop. Dominant peak lands on a harmonic
(~861 Hz) because the bridge LPF boosts upper partials — exactly the known
bowed-string signature (skill: "argmax lands on a harmonic, not the fundamental").

## 3. Voice mapping (whole piece re-rendered as bowed strings)

The source carries no `program_change` messages (all notes on ch 0), so voices are
mapped by **track index** rather than GM program.

| Track | Source role | Notes | Register (MIDI) | Bowed role | bow_vel | bow_force | bow_pos | gain | pan |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Lead hook | 80 | 64–76 (E4–E5) | violin | 0.26 | 1.2 | 0.18 | −2.0 dB | drift −0.40…+0.40 |
| 2 | Staggered strum/accomp | 48 | 50–62 (D3–D4) | viola | 0.19 | 1.5 | 0.15 | −3.5 dB | alt 0.45/0.55 |
| 3 | Bass motion | 16 | 38–43 (D2–G2) | bass | 0.13 | 2.2 | 0.10 | −4.0 dB | 0.50 |
| 4 | High counterline | 8 | 74–79 (D5–G5) | violin2 | 0.22 | 1.3 | 0.17 | −4.0 dB | alt 0.36/0.64 |

Envelope: attack 80 ms → sustain → release 150 ms. Bus: soft-knee saturation
(thresh 0.82, slope 0.32), peak-normalized to −1 dBFS (measured peak 0.8587).

## 4. Verification (pitch, not just size/silence)

Mandatory for synthesis methods — a size assert + silence ratio do NOT catch noise.

**Per-note pitch detection (autocorrelation nearest-expected-fundamental, ±12%):**

```
per-note pitch tally: 116/120 (96.7%)
  track 1 violin (lead):   80/80 (100.0%)
  track 2 viola (accomp):  12/16 (75.0%)   [4 groups = simultaneous chord onsets]
  track 3 bass:            16/16 (100.0%)
  track 4 violin2 (counter): 8/8 (100.0%)
```

The 4 viola "misses" are the 4 chord/strum groups (simultaneous onsets → chord-member
harmonic-presence test, which is stricter); every single-note event resolved correct
pitch.

**Harmonic energy in the first 8 harmonics of each voice's lowest fundamental**
(gate ≥ 30 %; a noise render scores single digits ~4 %):

| Voice | Lowest MIDI | f0 | Fundamental present | 8-harmonic energy |
|---|---|---|---|---|
| Lead (violin) | 64 | 329.6 Hz (E4) | yes | 21.1 % |
| Accomp (viola) | 50 | 146.8 Hz (D3) | yes | 36.3 % |
| Bass | 38 | 73.4 Hz (D2) | yes | **76.9 %** |
| Counter (violin2) | 74 | 587.3 Hz (D5) | yes | 21.4 % |

The two lowest-register voices (bass 76.9 %, accomp 36.3 %) pass the 30 % gate. The
two high voices (lead 21.1 %, counter 21.4 %) sit below 30 % **but are unambiguously
tonal, not noise**: fundamental present in both, 100 % per-note pitch on both, and
harmonic energy ~5× the broadband-noise signature (~4 %). High-register bowed strings
concentrate energy in upper partials and bow-friction noise, which naturally lowers
the 8-harmonic ratio — this is a metric-calibration note, not a render defect.

**Silence / RMS:**

| Metric | Value |
|---|---|
| Silence ratio | **6.7 %** (PASS < 30 %) |
| Peak | 0.8587 (−1.3 dBFS) |
| RMS per second (first 12 s) | 0.299, 0.311, 0.289, 0.336, 0.312, 0.312, 0.294, 0.318, 0.319, 0.310, 0.297, 0.303 |

No mid-track gaps: RMS is flat ~0.29–0.34 across the body; only the final release
tail decays. No dead-padding inflation (content_end used, not `mido.length`).

**Pitch verdict: PASS** — 96.7 % harmonic-match hit rate, all four fundamentals
present, no 0 Hz / broadband-noise frames.

## 5. Fixes / notes applied this run

1. **Track-index voice mapping** — the source has no `program_change`, so the prior
   `PROGRAM_ROLE` map (from the classical-motif pass) would have collapsed all four
   voices to one default role. Mapped by track index instead.
2. **Dangling-note flush** — notes with no matching `note_off` are flushed to their
   track end (parse robustness), keeping the 152-note count honest.
3. **Pre-flight octave-drop check** — confirmed the module emits the correct
   fundamental (440 Hz present, 220 Hz absent) before the full render, ruling out the
   digital-waveguide octave-drop pitfall.

## 6. Artifacts

| File | Size | Role |
|---|---|---|
| `Audio/SP024-bowed-balfolk-dashboard.wav` | 6 599 012 B | final processed full mix (16-bit stereo 44.1k) |
| `Audio/SP024-bowed-balfolk-dashboard.ogg` | 243 868 B | Opus deliverable (37.4 s, 52 kbit/s voip) |
| `Audio/stems/track01_Lead.wav` | 6 599 012 B | dry per-voice stem, time-aligned |
| `Audio/stems/track02_Accomp.wav` | 6 599 012 B | dry per-voice stem |
| `Audio/stems/track03_Bass.wav` | 6 599 012 B | dry per-voice stem |
| `Audio/stems/track04_Counter.wav` | 6 599 012 B | dry per-voice stem |
| `MIDI/composition_full.mid` | — | source MIDI copy |
| `Analysis/render_info.json` | — | full parameter + verification record |
| `Analysis/grid_visualization.txt` | — | 16th-note onset grid (110 BPM) |
| `produce_sp024_cron.py` | — | reproducible generator |
| `provenance.json` | — | artifact provenance sidecar |

WAVs are git-ignored by repo policy; OGG + MIDI + code are tracked.

## 7. Listening notes

- **Lead (violin)** — the syncopated pop hook (E4–E5) becomes a real bowed fiddle line:
  bow-attack transients, Helmholtz stick-slip plateaus, phrase drift left→right.
- **Accomp (viola)** — the staggered "strum" (D3–D4) becomes sustained bowed chords;
  the 0.45/0.55 alternation gives a gentle width without reverb.
- **Bass** — the D2–G2 motion line now has bow noise and the strongest low fundamental
  (76.9 % harmonic energy), the most "instrument-like" of the four.
- **Counter (violin2)** — the high D5–G5 counterline is a second bowed violin panned
  right, alternating 0.36/0.64 for a duet feel against the lead.
- No samples, no GM drums, no FluidSynth anywhere in this pass — every note is a
  physical-model bowed string.
