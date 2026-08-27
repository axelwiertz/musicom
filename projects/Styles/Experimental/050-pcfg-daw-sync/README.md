# Project 050: PCFG & DAW Sync

Autonomous daily production piece using the **musicom** engine.

## Methods Used
- **Composition Method:** `Method 034` - Probabilistic Context-Free Grammar (PCFG) Recursion
- **Sound Production Method:** `SP-005` - Headless DAW/MTC Sync

## Concept & DNA
- **Key/Mode:** D Dorian (D, E, F, G, A, B, C, D)
- **Tempo:** 100 BPM (4/4 meter)
- **Progression:** Dm7 - G7 - Cmaj7 - Am7 (8 bars total)
- **Stems Exported:** Lead (Flute), Pad (Synth Pad), Bass (Acoustic Bass)
- **Notation Export:** Full MusicXML score in `Scores/`

## Run
```bash
/opt/data/micromamba/envs/musicom/bin/python compose.py
/opt/data/micromamba/envs/musicom/bin/python /opt/data/projects/Research/preflight_check.py .
```
