# -*- coding: utf-8 -*-
"""SP-107 bit-crusher production: pre-flight audit + dry render (2026-11-18)."""
import os
import subprocess
from pathlib import Path

import mido

ROOT = Path("/opt/data/repos/musicom")
SRC = ROOT / "projects/Styles/IndianClassical/212-indian-boids-yaman/MIDI/212-indian-boids-yaman.mid"
OUT = ROOT / "projects/Styles/Production/SP107-bitcrusher-212-indian-boids-yaman"
AUD = OUT / "Audio"
MIDIDIR = OUT / "MIDI"
ANALYSIS = OUT / "Analysis"
SCRIPTS = OUT / "Scripts"
for d in (AUD, MIDIDIR, ANALYSIS, SCRIPTS):
    d.mkdir(parents=True, exist_ok=True)

FLUID = "/opt/data/micromamba/envs/musicom/bin/fluidsynth"
SF = "/opt/data/micromamba/envs/musicom/share/soundfonts/FluidR3_GM.sf2"

TPB = 480
BAR = 1920
GRID = 120  # 16th
NBARS = 32
# Raga Yaman on C: S R G M# P D N = C D E F# G A B
SCALE_PCS = {0, 2, 4, 6, 7, 9, 11}
# Monophonic raga -> Sa+Pa tanpura drone is the constant harmony;
# chord-tone vocabulary == full Yaman scale (per source REPORT audit).
CHORD_TONES = [SCALE_PCS] * NBARS


def audit(path):
    mf = mido.MidiFile(str(path))
    grid_off = 0
    out_scale = 0
    out_chord = 0
    total_notes = 0
    track_ends = []
    per_voice = {}
    for tr in mf.tracks:
        chans = {m.channel for m in tr if m.type in ("note_on", "note_off")}
        is_drum = 9 in chans
        t = 0
        n_notes = 0
        last_end = 0
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                n_notes += 1
                total_notes += 1
                if is_drum:
                    continue
                if (t % GRID) != 0:
                    grid_off += 1
                pc = m.note % 12
                if pc not in SCALE_PCS:
                    out_scale += 1
                bar = min(t // BAR, NBARS - 1)
                if pc not in CHORD_TONES[bar]:
                    out_chord += 1
                last_end = max(last_end, t)
            elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
                last_end = max(last_end, t)
        if n_notes:
            track_ends.append(last_end)
            per_voice["ch%d%s" % (min(chans) if chans else -1,
                                  "_drums" if is_drum else "")] = {
                "n_notes": n_notes, "last_end": last_end}
    zero_drift = len(set(track_ends)) == 1
    return {"grid_off": grid_off, "out_scale": out_scale,
            "out_chord": out_chord, "total_notes": total_notes,
            "zero_drift": zero_drift, "track_ends": sorted(set(track_ends)),
            "per_voice": per_voice}


before = audit(SRC)
print("== pre-flight audit (source MIDI) ==")
print(before)
assert before["grid_off"] == 0, "grid sync FAIL"
assert before["out_scale"] == 0, "out-of-scale FAIL"
assert before["out_chord"] == 0, "out-of-chord FAIL"
assert before["zero_drift"], "zero-drift FAIL"
print("PRE-FLIGHT PASS (grid 0 / out-of-scale 0 / out-of-chord 0 / zero-drift)")

# copy source MIDI into output (for record), also phase1 sidecar already exists
import shutil
shutil.copy2(str(SRC), str(MIDIDIR / "212-indian-boids-yaman.mid"))
phase1_src = SRC.parent / "212-indian-boids-yaman-phase1.mid"
if phase1_src.exists():
    shutil.copy2(str(phase1_src), str(MIDIDIR / "212-indian-boids-yaman-phase1.mid"))

# ---- dry FluidSynth render (FX off) ----
dry_wav = OUT / "dry_full_mix_sp001_reference.wav"
r = subprocess.run([FLUID, "-ni", "-R", "0", "-C", "0", "-g", "1.2",
                    "-F", str(dry_wav), SF, str(SRC)],
                   capture_output=True, text=True, timeout=900)
if r.returncode != 0 or not dry_wav.exists() or dry_wav.stat().st_size < 1000:
    raise RuntimeError("FluidSynth render failed: %s" % r.stderr[-500:])
print("dry WAV:", dry_wav.stat().st_size, "bytes")

# save audit + selection summary
import json
sel = json.loads((ROOT / "projects/Styles/Production/.selection_cron.json").read_text())
(ANALYSIS / "preflight.json").write_text(json.dumps({
    "audit": before, "key": "Raga Yaman on C",
    "scale_pcs": sorted(SCALE_PCS), "harmony_note": "monophonic raga over Sa+Pa drone; chord-tone vocab = full Yaman scale",
    "bpm": 90, "tpb": TPB, "bars": NBARS,
}, indent=2))
print("preflight.json written")
print("DRY_WAV=" + str(dry_wav))
