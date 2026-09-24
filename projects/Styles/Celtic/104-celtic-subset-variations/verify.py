#!/opt/data/micromamba/envs/musicom/bin/python
# -*- coding: utf-8 -*-
"""Read-only verification for 104-celtic-subset-variations.

mido used READING ONLY (analysis). Re-derives the deterministic subset walk to
compute per-bar chord pitch-classes for the chord-violation audit.
"""
import os, json, random
import mido  # READING ONLY (analysis)
from rules.subset_network import PatternNetwork, standard_patterns

PROJ = "/opt/data/projects/Styles/Celtic/104-celtic-subset-variations"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")

BAR = 1920
KEY_PCS = {8, 10, 0, 1, 3, 5, 7}      # Ab major
TONIC_OFF = 8

# re-derive walk (deterministic)
_ANCHOR_IDS = ["maj0", "min2", "min4", "maj5", "maj7", "min9",
               "maj70", "dom77", "min72"]
_lib = PatternNetwork(standard_patterns())
_NET = PatternNetwork([_lib.patterns[i] for i in _ANCHOR_IDS])
BAR_TENSION = [
    2.0, 2.0, 2.0, 2.0, 2.5, 2.5, 3.0, 3.0, 3.5, 3.5, 4.0, 4.0,
    4.5, 5.0, 5.5, 4.5, 3.5, 3.0, 3.0, 3.5, 3.0, 2.5, 2.0, 2.0,
    3.5, 4.0, 4.0, 3.5, 2.0, 1.5, 1.2, 1.0]
_rng = random.Random(7)
_WALK = _NET.walk("maj0", 32, rng=_rng, tension_curve=BAR_TENSION, home="maj0")
_WALK[-1] = "maj0"
if _WALK[30] not in ("dom77", "maj7"):
    _WALK[30] = "dom77"


def chord_pcs(bar):
    pid = _WALK[bar]
    subset = _lib.patterns[pid].subset
    return set((pc + TONIC_OFF) % 12 for pc in subset)


def track_channel(track):
    for m in track:
        if m.type in ("note_on", "note_off", "program_change"):
            return m.channel
    return None


def audit(mid_path):
    mid = mido.MidiFile(mid_path)
    voice_tracks = mid.tracks[1:]
    lengths = []
    for t in voice_tracks:
        lengths.append(sum(m.time for m in t))
    zero_drift = len(set(lengths)) == 1

    channels = [track_channel(t) for t in voice_tracks]
    off_grid = 0
    scale_viol = 0
    chord_viol = 0
    pitched = 0
    for ti, t in enumerate(voice_tracks):
        is_drums = channels[ti] == 9
        abs_tick = 0
        for m in t:
            abs_tick += m.time
            if m.type == "note_on" and m.velocity > 0 and not is_drums:
                pitched += 1
                if not (abs_tick % 120 == 0 or abs_tick % 240 == 0):
                    off_grid += 1
                if m.note % 12 not in KEY_PCS:
                    scale_viol += 1
                bar = abs_tick // BAR
                if bar >= 32:
                    bar = 31
                if m.note % 12 not in chord_pcs(bar):
                    chord_viol += 1
    return {
        "n_tracks": len(voice_tracks),
        "lengths": lengths,
        "channels": channels,
        "zero_drift": zero_drift,
        "pitched_onsets": pitched,
        "off_grid": off_grid,
        "scale_viol": scale_viol,
        "chord_viol": chord_viol,
    }


res = {"phase1": audit(os.path.join(MIDI_DIR, "104-celtic-subset-variations-phase1.mid")),
       "phase2": audit(os.path.join(MIDI_DIR, "104-celtic-subset-variations.mid"))}

# size asserts
sizes = {}
for p in [os.path.join(MIDI_DIR, "104-celtic-subset-variations.mid"),
          os.path.join(MIDI_DIR, "104-celtic-subset-variations-phase1.mid")]:
    sizes[os.path.basename(p)] = os.path.getsize(p)
    assert os.path.getsize(p) > 40, p
for f in sorted(os.listdir(AUDIO_DIR)):
    fp = os.path.join(AUDIO_DIR, f)
    if os.path.isfile(fp):
        sizes[f] = os.path.getsize(fp)
        if f.endswith((".wav", ".ogg", ".mid")):
            assert os.path.getsize(fp) > 40, fp

out = {"project": "104-celtic-subset-variations", "audit": res, "sizes": sizes}
with open(os.path.join(PROJ, "Analysis", "verify.json"), "w") as f:
    json.dump(out, f, indent=2)

print(json.dumps(res, indent=2))
print("\nSIZES:", sizes)
p2 = res["phase2"]
print("\nPHASE2: tracks=%d len=%s zero_drift=%s pitched=%d off_grid=%d scale_viol=%d chord_viol=%d"
      % (p2["n_tracks"], p2["lengths"], p2["zero_drift"], p2["pitched_onsets"],
         p2["off_grid"], p2["scale_viol"], p2["chord_viol"]))
p1 = res["phase1"]
print("PHASE1: tracks=%d len=%s zero_drift=%s pitched=%d off_grid=%d"
      % (p1["n_tracks"], p1["lengths"], p1["zero_drift"], p1["pitched_onsets"], p1["off_grid"]))
