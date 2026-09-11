#!/usr/bin/env bash
# Full pipeline for 093-rock-euclidean (rerun-safe, in order).
set -euo pipefail
PY=/opt/data/micromamba/envs/musicom/bin/python
P=/opt/data/repos/musicom/projects/Styles/Rock/093-rock-euclidean
cd /opt/data/repos/musicom
$PY $P/Scripts/compose.py        2>&1 | grep -v ALSA | grep -v RuntimeWarning | grep -v "soprano_motion\|motion2\|motion1"
$PY $P/Scripts/audit.py          2>&1 | grep -v ALSA
$PY $P/Scripts/render_audio.py   2>&1 | grep -v ALSA
$PY $P/Scripts/audio_stats.py    2>&1 | grep -v ALSA
$PY $P/Scripts/tonal_check.py    2>&1 | grep -v ALSA
$PY $P/Scripts/summarize.py      2>&1 | grep -v ALSA | tail -3
$PY $P/Scripts/audio_provenance.py 2>&1 | grep -v ALSA
