# 053 — Euclidean Binaural

**Style:** Experimental | **Method 012:** Euclidean Groove Locking | **SP-021:** Binaural Spatialization

## Concept
Four Euclidean rhythm patterns (tresillo, latin, khaling, samba) mapped to D Dorian scale.
Binaural spatialization via Woodworth-Schlosberg ITD/ILD model creates a slowly sweeping stereo image.

## DNA
- **Key:** D Dorian
- **Tempo:** 110 BPM
- **Form:** AABA (8 bars)
- **Pitch:** Dorian scale degrees mapped to Euclidean onset positions
- **Rhythm:** E(3,8), E(5,16), E(2,5), E(7,16)
- **Harmony:** Dm - G - Am - F cycle
- **Space:** Binaural azimuth sweep +/-60deg at 0.15Hz

## Files
- `MIDI/053-euclidean-binaural.mid` — DAW-editable MIDI
- `Audio/053-euclidean-binaural.ogg` — Binaural Opus render
- `Analysis/grid_visualization.txt` — Rhythm DNA grid
- `Analysis/euclidean_patterns.txt` — Pattern analysis

## Run
```bash
/opt/data/micromamba/envs/musicom/bin/python src/compose.py
/opt/data/micromamba/envs/musicom/bin/python src/apply_binaural.py
ffmpeg -y -i Audio/053-euclidean-binaural_binaural.wav -codec:a libopus -b:a 48k Audio/053-euclidean-binaural.ogg
```
