# SP-090 ORBITAL STEREO SCULPTOR (3-Band Orbital Stereo Sculptor / AutoPanner) — 097-jazz-bebop-changes

**Date (UTC):** 2026-09-22 (nightly autonomous production job)
**Output root:** `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/`
**Status:** PASS — mix FFT 89/89 (1.0000), harmonic energy 0.5389, silence 7.58%, LUFS -14.00, peak 0.8913, mono correlation 0.4287.

---

## 1. Method + Selection (Which Registry Source)

| Field | Value |
|---|---|
| Method | **SP-090** — 3-Band Orbital Stereo Sculptor / AutoPanner (SoundGhost Orbit-style) |
| Registry source | `workflows.musicom_workflow.SP_METHODS` — the **implemented** dict (NOT `methods_db.md` spec-only, NOT stale ranges) |
| Registered module | `sound.effects.orbit_sculptor` → `OrbitalStereoSculptor`, `OrbitalBandProcessor`, `LinkwitzRiley4Crossover`, `ModulatorConfig`, `BandConfig` |
| Registry entries at pick time | **32 implemented:** SP-001, 011, 021, 024, 026, 028, 032–037, 069–086, 090–091 |
| Already used last 7d (excluded) | SP-033 (09-21), SP-080 (09-20), SP-083 (09-19), SP-084 (09-17), SP-072 (09-16), SP-074 (09-15), SP-036 (09-14) |
| Eligible pool | **25 implemented methods** |
| Selection | `random.Random(20260922).choice(eligible)` → **SP-090** (first SP-090 production run in current cycle) |
| MIDI pool | 227 usable candidates (>500 B, excl. `Production`, `phase1`, `candidates`, `evolution`); deterministic seeded pick → `Styles/Jazz/097-jazz-bebop-changes/MIDI/097-jazz-bebop-changes.mid` |
| Selection record | `Analysis/select_20260922.json` and `.selection_cron.json` |

---

## 2. Source Composition

| Field | Value |
|---|---|
| Project | `Styles/Jazz/097-jazz-bebop-changes/` (Jazz Bebop Changes with 12TET subset network walk over G major diatonic seventh anchors) |
| MIDI | `097-jazz-bebop-changes.mid` (copied to output `MIDI/`; 7,085 B) |
| Tempo / grid | 132 BPM (454,545 µs/beat), tpb 480; 47.77 s duration, 46,080 ticks (24 bars: 6 sections × 4 bars) |
| Form | Intro / Head / Solo / Bridge / Head2 / Outro (24 bars), G Major walked seventh cadence (`I - IV - I - IV - ii - iii | IV - I - ii - I - iii - IV | IV7 - vi7 - IV7 - I7 | vi7 - ii7 - vi7 - IV7 - ii7 | IV - V7 - I`) |
| Voices | Trumpet (lead, GM 56) · Trombone (counterline, GM 57) · Bright Acoustic Piano (comping, GM 1) · Contrabass (walking, GM 43) · Drums (ch9, spang-a-lang ride) |
| Texture | Fast swing bebop quintet: intricate chromatic approach bebop soloing, walking bass line, syncopated piano stabs, rich horn harmonies |
| Why this source | Multiband orbital auto-panning and stereo sculpting expands the classic jazz quintet into an immersive, rotating 3D acoustic stage without smearing the low-end walking bass or drum kick punch. |

Grid (`Analysis/grid_visualization.txt`): 5 voices × 6 sections, 24 bars total, bebop swing groove.

---

## 3. Layer Discipline (Absolute)

SP-090 is an **absolute-layer multiband stereo sculpting and auto-panning method**: `OrbitalStereoSculptor` splits audio into Low (<250 Hz), Mid (250 Hz - 3500 Hz), and High (>3500 Hz) bands using 4th-order Linkwitz-Riley (24 dB/oct) crossover filters. Each band applies tempo-synced LFO modulators, pan law compensation, mid/side stereo widening, and gentle harmonic drive across all instrument voices.

```
097-jazz-bebop-changes.mid
 -> dry reference: fluidsynth -ni -g 1.2 (reverb OFF, chorus OFF, FluidR3_GM.sf2)
      dry_full_mix_sp001_reference.wav (8.43 MB)
 -> dry stems (RenderPipeline extraction, FX off):
      track00_Trumpet / track01_Trombone / track02_Bright_Acoustic_Piano / track03_Contrabass / track04_Drums
 -> SP-090 Orbital Stereo Sculptor processing:
      Trumpet: 1/4-note tempo-synced sine autopan + saturated mod in mids, 1/8-note orbital width in highs
      Trombone: 1/2-note triangle counter-pan in mids, subtle high-frequency air dispersion
      Piano: 1/2-note triangle pan across mid-band with 1.4 width, 1/4-note S&H random walk on upper register
      Contrabass: Lows mono-locked (0.0 width), warm mid presence with subtle drift, high-frequency clutter clamped
      Drums: Low end centered & punchy, 1/8-note orbital auto-pan on ride cymbals & hi-hat shimmer
      per-stem peak-norm 0.89 -> trackXX_*_ORBIT.wav
 -> master bus sum -> master cohesion orbital sculptor (mono sub <200 Hz, 1.15x mid width, 1.35x high width)
 -> AlgorithmicReverb (jazz club acoustics, room_size 0.5, wet_dry 0.12)
 -> normalize_to_lufs(-14.0) -> Limiter(-1.0 dBFS) LAST
 -> SP090-orbit-jazz-bebop-changes.wav + .ogg (Opus 48k voip)
```

### Voice Profiles (Orbital Parameter Design)

| Voice Stem | Role | Low-Mid Crossover | Mid-High Crossover | Low Band (Pan/Width) | Mid Band Modulation | High Band Modulation | Mono Correlation |
|---|---|---|---|---|---|---|---|
| `track00_Trumpet` | Solo Lead | 300 Hz | 3200 Hz | Center / 0.0 Mono | 1/4 Sine, Sat=True, Depth 0.6 | 1/8 Sine, Width 1.5, Depth 0.5 | 0.758 |
| `track01_Trombone` | Counterline | 250 Hz | 2800 Hz | Center / 0.1 Width | 1/2 Triangle, Depth 0.45 | 1/4 Sine, Width 1.3, Depth 0.3 | 0.877 |
| `track02_Bright_Acoustic_Piano` | Comping | 250 Hz | 3500 Hz | Center / 0.2 Width | 1/2 Triangle, Width 1.4, Depth 0.5 | 1/4 Random S&H, Width 1.6, Depth 0.4 | -0.472 (Wide Out of Phase) |
| `track03_Contrabass` | Walking Bass | 220 Hz | 2500 Hz | Center / 0.0 Mono | 1/1 Sine subtle wander, Depth 0.15 | Width 0.6, Gain -2.0 dB | 0.655 |
| `track04_Drums` | Swing Ride & Kit | 180 Hz | 4000 Hz | Center / 0.0 Mono | 1/4 Random S&H, Depth 0.25 | 1/8 Sine, Width 1.8, Depth 0.7 | 0.827 |

---

## 4. Pitch / Tonal-Content Verification — **PASS**

Checked on delivered wet mix audio:

| Metric | Wet Mix | Gate | Verdict |
|---|---|---|---|
| Mix FFT hit (0.5 s windows, 50–1000 Hz, ±4.5% vs fund ×1/×2/×3/×4//2) | **89/89 = 1.0000** | ≥ 0.60 | PASS |
| Harmonic energy (8 harmonics of lowest fund) | **0.5389** | ≥ 0.30 | PASS |
| Valid pitched windows | **89 / 95 (93.7%)** | > 50% | PASS |
| Dominant pitch range | 65.4 Hz (C2) to 784 Hz (G5) (G Major / Bebop scale tones) | — | Aligned |
| Median dominant peak | 492.0 Hz (B4 / diatonic 3rd) | — | Clean |

The SP-035 failure signature (0 Hz frames + broadband noise) is **absent**. Tonal gravity and pitch integrity of the G major bebop walk are completely preserved with 0.5389 harmonic ratio.

---

## 5. Silence / RMS Profile + Level

| Metric | Wet | Note |
|---|---|---|
| Silence (<0.001) | **7.58%** | Excellent continuous musical flow with brief phrase pauses |
| Peak / LUFS | **0.8913 / -14.00 LUFS** | Limiter(-1 dBFS) ceiling strictly enforced |
| Mono Correlation | **0.4287** | Expansive stereo image while maintaining robust mono compatibility |
| RMS profile | ~0.11–0.19 active | Dynamic bebop intensity across all 6 sections |

---

## 6. Fixes & Discoveries During Run

1. **Biquad Vectorization Speedup**: The standard recursive Python sample loop in `Biquad.process` within `sound/effects/orbit_sculptor.py` required >180s for 48s multi-track buffers. Vectorized using `scipy.signal.lfilter`, bringing processing time down to <2.5 seconds per track while keeping exact mathematical filter response.
2. **Mastering Array Orientation**: `LUFSMeter` and `AlgorithmicReverb` expect time-major shape `(N, 2)` while raw audio synthesis pipelines use channel-major `(2, N)`. Managed transposition transitions cleanly so LUFS measurement and Limiter operate with 100% precision.
3. **Low-End Phase Safety**: In multiband spatialization, auto-panning frequencies below 200 Hz creates phase cancellation on subwoofers. Strictly zeroed low-frequency pan and width across Contrabass, Drums, and master bus, locking the fundamental groove to the center.

---

## 7. Artifact Manifest

| Type | Path | Size |
|---|---|---|
| Master WAV | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/SP090-orbit-jazz-bebop-changes.wav` | 8,426,796 B |
| Master OGG | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/SP090-orbit-jazz-bebop-changes.ogg` | 353,062 B |
| Dry Reference | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/dry_full_mix_sp001_reference.wav` | 8,426,796 B |
| Source MIDI | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/MIDI/097-jazz-bebop-changes.mid` | 7,085 B |
| Dry Stems | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/Audio/stems_dry/` (5 stems) | ~42.1 MB total |
| Wet Stems | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/Audio/stems_wet/` (5 stems) | ~42.1 MB total |
| Script | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/Scripts/produce_sp090_cron.py` | 15.6 KB |
| Provenance | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/provenance.json` | 910 B |
| Selection Record | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/Analysis/select_20260922.json` | 642 B |
| Report | `/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-jazz-bebop-changes/REPORT.md` | this file |
