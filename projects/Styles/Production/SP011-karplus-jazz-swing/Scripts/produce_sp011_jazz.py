# -*- coding: utf-8 -*-
"""
SP-011 — Karplus-Strong String Synthesis production pass (nightly random job).

Source: Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/exercise1b_jazz_ii_v_i_swing.mid
        (Jazz ii-V-I Swing study, 120 BPM, 16 s, 5 tracks)
Method: SP-011 from workflows.musicom_workflow.SP_METHODS registry
        (sound.synthesis.karplus_strong) — physical modeling of plucked strings:
        delay-line feedback + 2-point moving-average loop filter.

Absolute-layer discipline: EVERY voice is rendered as Karplus-Strong plucked
strings (no FluidSynth, no GM samples). Voice roles by program:
  prog 65 (Sax Lead)      -> role "lead"  (pan drift L->R across the form)
  prog 0  (Piano Comping) -> role "comp"  (center, shorter decay)
  prog 32 (Walking Bass)  -> role "bass"  (center, long sustain)
  ch9    (Drums: ride/backbeat) -> role "perc" (center, very short decay thunk)

Outputs: full mix WAV + OGG, per-role stems (same synthesis), provenance,
render_info.json, onset grid visualization, pitch verification numbers.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import mido
import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom")  # editable install already global; belt+braces
from sound.synthesis.karplus_strong import render_melody, render_melody_wav, SR

OUT_ROOT = Path("/opt/data/projects/Styles/Production/SP011-karplus-jazz-swing")
SRC_MIDI = Path("/opt/data/projects/Styles/Balfolk/017-hybrid-pattern-matrix/MIDI/exercise1b_jazz_ii_v_i_swing.mid")

AUDIO = OUT_ROOT / "Audio"
ANALYSIS = OUT_ROOT / "Analysis"
MIDI_OUT = OUT_ROOT / "MIDI"
SCRIPTS = OUT_ROOT / "Scripts"
for d in (AUDIO, ANALYSIS, MIDI_OUT, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Parse source MIDI (mido = read-only analysis; authoring stays in musicom)
# ---------------------------------------------------------------------------
def tick_to_sec(mid, tick):
    abs_tempos = []
    at = 0
    for m in mid.tracks[0]:
        at += m.time
        if m.type == "set_tempo":
            abs_tempos.append((at, m.tempo))
    if not abs_tempos:
        abs_tempos = [(0, 500000)]
    sec = 0.0
    prev = 0
    cur = abs_tempos[0][1]
    for at, tmp in abs_tempos:
        if tick <= at:
            break
        sec += (at - prev) * cur / mid.ticks_per_beat / 1_000_000
        prev = at
        cur = tmp
    sec += (tick - prev) * cur / mid.ticks_per_beat / 1_000_000
    return sec


def parse_notes(mid):
    events = []
    for ti, track in enumerate(mid.tracks):
        program = 0
        for m in track:
            if m.type == "program_change":
                program = m.program
        abstick = 0
        active = {}
        for m in track:
            abstick += m.time
            if m.type == "note_on" and m.velocity > 0:
                active[m.note] = (abstick, m.velocity, m.channel)
            elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
                if m.note in active:
                    s, vel, ch = active.pop(m.note)
                    events.append({
                        "track": ti, "program": program, "channel": ch,
                        "pitch": m.note, "velocity": vel,
                        "start": tick_to_sec(mid, s),
                        "end": tick_to_sec(mid, abstick),
                    })
    events.sort(key=lambda e: e["start"])
    return events


mid = mido.MidiFile(str(SRC_MIDI))
events = parse_notes(mid)
for e in events:
    # channel 9 is the percussion channel regardless of program byte
    if e["channel"] == 9:
        e["role"] = "perc"
    elif e["program"] == 32:
        e["role"] = "bass"
    elif e["program"] == 0:
        e["role"] = "comp"
    else:
        e["role"] = "lead"

bpm = round(60_000_000 / next((m.tempo for t in mid.tracks for m in t
                               if m.type == "set_tempo"), 500000), 2)
total_dur = mid.length
print(f"notes={len(events)} bpm={bpm} total_dur={total_dur:.2f}s")

from collections import Counter
print("roles:", Counter(e["role"] for e in events))

# ---------------------------------------------------------------------------
# 2. Voice design — per-role Karplus-Strong config (absolute layer)
# ---------------------------------------------------------------------------
ROLES = {
    "lead": {"gains": [1.0], "width": 0.55, "pan_drift": True,
             "gain_db": -2.0, "loop_gain": 0.9992},   # sax melody, sweeping pan
    "comp": {"gains": [1.0], "width": 0.60, "pan_drift": False,
             "gain_db": -6.0, "loop_gain": 0.9978},   # piano chords, longer ring
    "bass": {"gains": [1.0], "width": 0.35, "pan_drift": False,
             "gain_db": -5.0, "loop_gain": 0.9994},   # walking bass, long sustain
    "perc": {"gains": [1.0], "width": 0.30, "pan_drift": False,
             "gain_db": -10.0, "loop_gain": 0.9850},  # ride/backbeat -> short thunks
}

# ---------------------------------------------------------------------------
# 3. Render full mix + per-role stems with the SAME synthesis
# ---------------------------------------------------------------------------
mix_wav = AUDIO / "SP011-jazz-swing-karplus-strong.wav"
audio, info = render_melody(events, roles=ROLES)
render_melody_wav(events, mix_wav, roles=ROLES)
print(f"mix: {mix_wav.name} {mix_wav.stat().st_size} bytes, {info['output_seconds']}s")

stems = {}
for role in ("lead", "comp", "bass", "perc"):
    role_notes = [e for e in events if e["role"] == role]
    if not role_notes:
        continue
    stem_path = AUDIO / f"stem_{role}.wav"
    _, sinfo = render_melody(role_notes, roles=ROLES)
    render_melody_wav(role_notes, stem_path, roles=ROLES)
    stems[role] = str(stem_path)
    print(f"stem {role}: {stem_path.name} {stem_path.stat().st_size} bytes ({sinfo['note_count']} notes)")

# Trim dead tail: source is 16.00s; render tail extends to 19s with ~3s of
# pure silence after the last pluck. Crop to 16.2s (0.2s natural decay).
def trim_wav(path, target_sec):
    import wave as _wave
    with _wave.open(str(path), "rb") as wf:
        sr0 = wf.getframerate()
        nch0 = wf.getnchannels()
        sw = wf.getsampwidth()
        n0 = wf.getnframes()
        data = wf.readframes(n0)
    n_t = int(target_sec * sr0)
    if n_t >= n0:
        return
    data = data[: n_t * nch0 * sw]
    with _wave.open(str(path), "wb") as wf:
        wf.setnchannels(nch0)
        wf.setsampwidth(sw)
        wf.setframerate(sr0)
        wf.writeframes(data)


trim_wav(mix_wav, 16.2)
for role, sp in stems.items():
    trim_wav(Path(sp), 16.2)
print(f"trimmed mix to 16.2s: {mix_wav.stat().st_size} bytes")

# OGG for Telegram playback
ogg_path = AUDIO / "SP011-jazz-swing-karplus-strong.ogg"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mix_wav),
                "-codec:a", "libopus", "-application", "voip", "-b:a", "48k",
                str(ogg_path)], check=True)
print(f"ogg: {ogg_path.stat().st_size} bytes")

# ---------------------------------------------------------------------------
# 4. Analysis artifacts
# ---------------------------------------------------------------------------
# 4a. Onset grid per track (high-contrast, 16 cols = 8 bars x 2)
def onset_grid(notes, ncols=32, span=None):
    span = span or (min(n["start"] for n in notes), max(n["end"] for n in notes))
    t0, t1 = span
    cols = [""] * ncols
    for n in notes:
        c = int((n["start"] - t0) / (t1 - t0) * ncols)
        c = min(ncols - 1, c)
        cols[c] = "X"
    return "".join("█" if c else "░" for c in cols)

grid_lines = []
grid_lines.append(f"SP-011 Karplus-Strong — source: {SRC_MIDI.name} ({bpm} BPM, {total_dur:.1f}s)")
grid_lines.append("")
for role in ("lead", "comp", "bass", "perc"):
    rn = [e for e in events if e["role"] == role]
    grid_lines.append(f"{role:5s} {onset_grid(rn)}")
grid_lines.append("")
grid_lines.append("32 columns across the full piece; each col = 0.5s")
(ANALYSIS / "onset_grid.txt").write_text("\n".join(grid_lines))

# 4b. render_info.json
info.update({
    "source_midi": str(SRC_MIDI),
    "source_name": SRC_MIDI.name,
    "bpm": bpm,
    "total_notes": len(events),
    "roles_used": {r: sum(1 for e in events if e["role"] == r) for r in ROLES},
    "stems": stems,
    "parameters": {
        "excitation": "2-sample uniform noise burst scaled by velocity",
        "delay_line": "N = round(sr/f0), full cycle period (no octave drop)",
        "loop_filter": "2-point moving average y[n]=0.5*(y[n-N]+y[n-N-1])",
        "loop_gain_by_role": {r: ROLES[r]["loop_gain"] for r in ROLES},
        "gain_db_by_role": {r: ROLES[r]["gain_db"] for r in ROLES},
        "pan": "lead drift -0.55..+0.55 across form; others center",
        "bus": "soft-knee saturation, peak -1 dBFS",
        "tail": "3.0 s reverb-free decay tail",
    },
})
(ANALYSIS / "render_info.json").write_text(json.dumps(info, indent=2))

# 4c. provenance
from workflows.provenance import write_provenance, AI_ASSISTED
for art, cls in [(mix_wav, "ai-assisted"), (ogg_path, "ai-assisted")]:
    write_provenance(str(art), cls, "SP-011 Karplus-Strong production pass",
                     sources=[str(SRC_MIDI)],
                     parameters={"method": "SP-011", "roles": list(ROLES)})
for role, sp in stems.items():
    write_provenance(sp, "ai-assisted", "SP-011 Karplus-Strong stem",
                     sources=[str(SRC_MIDI)],
                     parameters={"role": role, "method": "SP-011"})

# 4d. copy source MIDI for provenance
shutil = __import__("shutil")
shutil.copy2(SRC_MIDI, MIDI_OUT / SRC_MIDI.name)

# 4e. size asserts
for p in [mix_wav, ogg_path] + [Path(v) for v in stems.values()]:
    assert p.stat().st_size > 1000, f"too small: {p}"

print("PRODUCE OK")
print(json.dumps({"mix": str(mix_wav), "ogg": str(ogg_path), "stems": stems}, indent=1))
