---
name: musicom-onboarding
description: Use when adding a new human composer to the musicom framework project. Standardizes environment setup, repository access, and the first DNA-centric composition run.
version: 1.0.0
author: Musicom Agent
license: MIT
metadata:
  hermes:
    tags: [musicom, onboarding, setup, composer, workflow]
    related_skills: [musicom-composer, music-project-workflow]
---

# Musicom Onboarding — Composer Setup

Welcome to the **White Box** music composition framework. This skill guides the initial setup for human composers joining the `musicom` project.

## Overview
Musicom is not a "black box" generator. It is a systematic composition environment where you control the **Musical DNA** (Pitch/Rhythm matrices) and the **Synthesis Stack** (Logic/Rules/VST).

## Initial Setup Checklist

### 1. Repository Access
Ensure you have access to the canonical repositories:
- **Core Library**: `axelwiertz/musicom` (The logic)
- **Portfolio**: `musicom-agent/music-projects` (The creative output)

### 2. Environment Verification
Run the validation script to ensure your local or containerized environment has the necessary audio stack:
```bash
python3 /opt/data/repos/musicom/skills/music/musicom-onboarding/scripts/validate_env.py
```
**Required stack:**
- `music21`, `musicpy`, `mido` (Symbolic logic)
- `Pedalboard`, `numpy` (Audio/VST logic)
- `FluidSynth` + `FluidR3_GM.sf2` (High-fidelity fallback rendering)

### 3. Project Initialization
Always start from the template to ensure your metrics and dashboards are auto-generated.
```bash
cp -r /opt/data/projects/000-project-template /opt/data/projects/NNN-my-first-project
```

## Your First Composition (DNA-First)

Musicom works by defining **MusicUnits** within a **UnitMatrix**.

1.  **Define Pitch DNA**: Open `src/composition.py` and define your scale/set.
    ```python
    scale = [0, 2, 4, 7, 9] # A Major Pentatonic
    ```
2.  **Define Rhythm DNA**: Set your Euclidean pattern.
    ```python
    rhythm = E(5, 8) # 5 hits in 8 pulses
    ```
3.  **Apply Rules**: Choice between Hindemith (Tension/Resolution) or Schoenberg (Variation).
4.  **Render**: Running the script generates `.mid`, `.wav`, and the `index.html` dashboard.

## Common Pitfalls
- **Relative Paths**: Always use absolute paths (e.g., `/opt/data/projects/...`) to avoid script failures.
- **WAV Delivery**: When sharing via Telegram, always use OGG/Opus for instant playback. RAW WAV is for archive/high-fidelity only.
- **DNA drift**: Ensure your `theory.md` matches the code. Use `musicom-agent` to audit the harmonic accuracy.

## Verification Checklist
- [ ] Repositories cloned to `/opt/data/repos/`
- [ ] `validate_env.py` returns all checks as PASSED
- [ ] First test render produces a playable `.wav` and an `index.html` with ASCII visualizations.
