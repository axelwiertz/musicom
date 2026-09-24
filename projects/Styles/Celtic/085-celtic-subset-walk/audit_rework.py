#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""Rework audit for 085-celtic-subset-walk. mido used READING ONLY (analysis)."""
import os, json, datetime
import mido  # READING ONLY (analysis)

PROJ = "/opt/data/projects/Styles/Celtic/085-celtic-subset-walk"
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
os.makedirs(ANALYSIS_DIR, exist_ok=True)

PRIMARY = os.path.join(MIDI_DIR, "085-celtic-subset-walk.mid")
PHASE1 = os.path.join(MIDI_DIR, "085-celtic-subset-walk-phase1.mid")

failures = []

# --- Standard 1: engine vs hand-rolled
compose_src = open(os.path.join(PROJ, "compose.py")).read()
uses_engine = ("from workflows.unitmatrix_composer import" in compose_src
               or "from workflows.musicom_workflow import compose" in compose_src)
hand_rolled = ("mido.MidiTrack(" in compose_src or "mido.MidiFile(" in compose_src
               and "note_on" in compose_src)
if not uses_engine:
    failures.append("std1_engine: compose.py does not import UnitMatrixComposer/musicom_workflow")
if hand_rolled:
    failures.append("std1_engine: compose.py authors MIDI with raw mido (note_on/MidiTrack)")

# --- Parse primary MIDI read-only
mid = mido.MidiFile(PRIMARY)
voice_tracks = mid.tracks[1:]  # skip track 0 conductor/tempo

# --- Standard 2: zero-drift (all voice tracks equal length)
lengths = []
for t in voice_tracks:
    total = 0
    for m in t:
        total += m.time
    lengths.append(total)
zero_drift_ok = len(set(lengths)) == 1
if not zero_drift_ok:
    failures.append(f"std2_zero_drift: voice track lengths differ {lengths}")

# --- Standard 3: rhythm-grid sync (pitched onsets, exclude ch9 drums)
# --- Standard 4: valid track setup (>= 4 voice tracks)
# Determine channel per track (from program_change or first note)
def track_channel(track):
    for m in track:
        if m.type in ("note_on", "note_off", "program_change"):
            return m.channel
    return None

channels = [track_channel(t) for t in voice_tracks]
n_voice = len(voice_tracks)
if n_voice < 4:
    failures.append(f"std4_tracks: only {n_voice} voice tracks (<4)")

# Collect pitched onsets
off_grid = []
pitched_onsets = []
for ti, t in enumerate(voice_tracks):
    ch = channels[ti]
    is_drums = (ch == 9)
    abs_tick = 0
    for m in t:
        abs_tick += m.time
        if m.type == "note_on" and m.velocity > 0:
            if is_drums:
                continue
            pitched_onsets.append((ti, m.note, abs_tick, ch))
            if not (abs_tick % 120 == 0 or abs_tick % 240 == 0):
                off_grid.append((ti, m.note, abs_tick))

if off_grid:
    failures.append(f"std3_grid: {len(off_grid)} pitched onsets off-grid")

# --- Standard 5: two-phase artifacts
if not os.path.exists(PHASE1):
    failures.append("std5_phase1: -phase1.mid missing")

# --- Standard 6: provenance + index.html
prov_p2 = PRIMARY + ".provenance.json"
prov_p1 = PHASE1 + ".provenance.json"
if not (os.path.exists(prov_p2) and os.path.exists(prov_p1)):
    failures.append("std6_provenance: provenance.json missing")
if not os.path.exists(os.path.join(PROJ, "index.html")):
    failures.append("std6_index: index.html missing")

# --- scale/chord check on source (informational, Ab major)
KEY_PCS = {8, 10, 0, 1, 3, 5, 7}
scale_viol = []
for ti, note, tick, ch in pitched_onsets:
    if note % 12 not in KEY_PCS:
        scale_viol.append((ti, note, tick, ch))

result = {
    "chosen": PROJ,
    "genre": "Celtic",
    "primary_midi": PRIMARY,
    "standard_failures": failures,
    "redesign_required": len(failures) > 0,
    "source_identity": {
        "key": "Ab major",
        "bpm": 96,
        "form": "6 sections x 4 bars = 24 bars",
        "sections": ["Intro", "ReelA", "ReelB", "Lift", "ReelA2", "Outro"],
        "method": "ABS-002 Subset Walker + ABS-001 tension curve + method-006 cadence close",
        "voices": ["Marimba", "French Horn", "Cello", "Violin", "Bassoon", "Double Bass", "Drums"],
    },
    "audit_numbers": {
        "n_voice_tracks": n_voice,
        "track_lengths": lengths,
        "channels": channels,
        "pitched_onsets": len(pitched_onsets),
        "off_grid_count": len(off_grid),
        "scale_violations": len(scale_viol),
    },
    "audit_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}

out = os.path.join(ANALYSIS_DIR, "rework_audit.json")
with open(out, "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
print("\nAUDIT FAILURES:", failures if failures else "none (all pass)")
print("REDESIGN REQUIRED:", result["redesign_required"])
