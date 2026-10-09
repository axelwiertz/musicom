#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SP-085 job: inspect environment + source MIDI (2026-10-09)."""
import mido
from utilities.env import repo_root, python_bin, fluidsynth_bin, soundfont_path

print("repo_root", repo_root)
print("python_bin", python_bin)
print("fluidsynth_bin", fluidsynth_bin)
print("soundfont_path", soundfont_path)

from sound.render.fluidsynth import discover_soundfont
print("discover_soundfont ->", discover_soundfont())

SRC = "/opt/data/repos/musicom/projects/Styles/Blues/blues-delta-daily-2026-06-24/MIDI/blues-delta-daily-2026-06-24.mid"
mf = mido.MidiFile(SRC)
print("tpb", mf.ticks_per_beat, "length_s", round(mf.length, 2))
for i, tr in enumerate(mf.tracks):
    pcs = [m for m in tr if m.type == "program_change"]
    notes = [m for m in tr if m.type == "note_on" and m.velocity > 0]
    chans = sorted(set(m.channel for m in tr if m.type in ("note_on", "program_change")))
    print(f"track{i}: notes={len(notes)} prog={[m.program for m in pcs]} chans={chans} name={tr.name!r}")
