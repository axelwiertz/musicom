# Sound Production Methods Registry

Catalog of researched sound production methods (SP-xxx). The Hermes agent's
production pipeline picks from this registry. Keep one entry per method;
update status when implementation lands in `sound/`.

Status: `implemented` = in sound/ package · `partial` = some pieces exist · `research` = documented only

## Synthesis Engines

| ID | Method | Status | Location |
|----|--------|--------|----------|
| SP-010 | FM Synthesizer Voicing | partial | sound/synthesis/phase_mod.py |
| SP-013 | Aperiodic Granular Synthesis | implemented | sound/synthesis/granular.py |
| SP-022 | Wave Terrain Synthesis (WTS) | research | — (2D terrain scan) |
| SP-032 | FDTD Physical Modeling | research | — (see methods KB; distinct from SP-003) |
| SP-003 | Modal Physical Modeling (Plate/Bar) | implemented | sound/synthesis/modal.py |
| SP-004 | Formant Vocal Synthesis | implemented | sound/synthesis/vocal.py |
| — | Additive Synthesis (SoundWave) | implemented | sound/synthesis/additive.py |

## Post-Processing / DSP

| ID | Method | Status | Location |
|----|--------|--------|----------|
| SP-001 | Multi-timbral SoundFont (SF2) | implemented | sound/render/fluidsynth.py |
| SP-002 | VST3 Polyphonic Stacking | implemented | sound/render/vst.py |
| SP-005 | Headless DAW/MTC Sync | implemented | sound/sync/clock.py |
| SP-006 | Zero-Drift Humanization | implemented | workflows/unitmatrix_composer.py |
| SP-007 | Spectral Masking EQ | partial | sound/effects/filter.py (DynamicEQ) |
| SP-008 | Dynamic Range Compression (DRC) | partial | sound/effects/mastering.py (Limiter) |
| SP-009 | Convolutive Reverberation | implemented | sound/effects/reverb.py (algorithmic) |
| SP-021 | Binaural Woodworth-Schlosberg Spatialization | research | — (HRTF ITD/ILD) |

## Mastering (from MusicTech workflow)

| Method | Status | Location |
|--------|--------|----------|
| LUFS Metering (ITU-R BS.1770-4) | implemented | sound/effects/mastering.py |
| Dynamic EQ (resonance control) | implemented | sound/effects/mastering.py |
| Stereo Imaging (mono-safe) | implemented | sound/effects/mastering.py |
| Peak Limiter | implemented | sound/effects/mastering.py |

## Generative Event Cores (Karst-style)

| Core | Status | Location |
|------|--------|----------|
| MarkovCore | implemented | sound/generators/event_core.py |
| StochasticCore (tendency mask) | implemented | sound/generators/event_core.py |
| EuclideanCore (Bjorklund) | implemented | sound/generators/event_core.py |
| LSystemCore | implemented | sound/generators/event_core.py |
| WeightedRandomCore | implemented | sound/generators/event_core.py |

## Planned (from surveillance, see surveillance.md)

| Method | Priority | Notes |
|--------|----------|-------|
| Spectral processing (STFT + demucs) | medium | effects/spectral.py planned |
| Mass-spring physical modeling | low | synthesis/physical.py, JAX optional |
| Guitar Pro / tab export | future | transcription pipeline |
| Flat.io integration | future | integrations/flat_io.py |
