#!/usr/bin/env bash
# 094-african-hierarchical-diffusion - full reproducible run
set -euo pipefail
PY="${MUSICOM_PYTHON:-/opt/data/micromamba/envs/musicom/bin/python}"
cd "$(dirname "$0")"
echo "== compose (phase 1 + phase 2 MIDI) =="; "$PY" compose.py
echo "== audit (grid / harmony / range / zero-drift) =="; "$PY" audit.py
echo "== render (FluidSynth -> WAV -> OGG) =="; "$PY" render_audio.py
echo "== audio stats (silence / RMS) =="; "$PY" audio_stats.py
echo "== tonal check (pitch ground truth) =="; "$PY" tonal_check.py
echo "== summarize + provenance =="; "$PY" summarize.py
echo "== preflight =="; "$PY" "$MUSICOM_ROOT/projects/Research/preflight_check.py" "$(dirname "$0")/.."
echo "DONE"
