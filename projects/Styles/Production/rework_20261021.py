# -*- coding: utf-8 -*-
"""Pre-flight rework for 012-country-country-uke (2026-10-21).

Three-rule gate FAILED on the source:
  - Grid sync:   192 off-grid onsets (acoustic-guitar strum rolls at 14/28-tick
                  micro-offsets from the 0/960/1920 grid base).
  - Chord-tone:  576 out-of-chord notes (melodic passing tones across lead /
                  harmony / e-guitar / fiddle / pedal-steel; fully diatonic
                  G major, 0 out-of-scale, but not chord tones of their bar).
  - Zero-drift:  note tracks end at 8 distinct ticks (final-note durations).

Fix (two-phase rework, source preserved):
  1. Snap every note onset to the 16th grid (nearest multiple of 120); keep
     duration (end = snapped_start + original_dur).
  2. Chord-tone quantize every pitched (non-drum) note to the nearest chord
     tone of its bar (signed circular delta, tie -> downward).
  3. Clamp note ends to 48 bars (92160) and pad every note track to 92160.
Written to the production folder; source MIDI is never modified.
"""
import mido
from pathlib import Path

SRC = Path("/opt/data/repos/musicom/projects/Styles/Country/012-country-country-uke/MIDI/v2_country_unitmatrix.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP090-orbit-sculptor-012-country-uke")
MIDIDIR = OUT / "MIDI"
MIDIDIR.mkdir(parents=True, exist_ok=True)

BAR = 1920
GRID = 120
TARGET = 48 * BAR  # 92160

CHORD_TONES = {
    "G": {7, 11, 2},
    "D": {2, 6, 9},
    "Em": {4, 7, 11},
    "C": {0, 4, 7},
}
PROG = []
PROG += ["G", "D", "Em", "C"]
PROG += ["G", "D", "Em", "C", "G", "D", "C", "D"]
PROG += ["G", "D", "Em", "C", "G", "D", "C", "D"]
PROG += ["G", "D", "Em", "C", "G", "D", "C", "D"]
PROG += ["G", "D", "Em", "C", "G", "D", "C", "D"]
PROG += ["Em", "C", "G", "D"]
PROG += ["G", "D", "C", "D"]
PROG += ["G", "C", "G", "G"]
assert len(PROG) == 48


def chord_pcs(bar):
    return CHORD_TONES[PROG[min(bar, 47)]]


def nearest_chord_delta(note, bar):
    pc = note % 12
    best = None
    for tp in chord_pcs(bar):
        d = tp - pc
        if d > 6:
            d -= 12
        elif d < -6:
            d += 12
        if best is None or abs(d) < abs(best) or (abs(d) == abs(best) and d < best):
            best = d
    return best


def snap(t):
    return int(round(t / GRID)) * GRID


mf = mido.MidiFile(str(SRC))
print("input:", mf.type, "tpb:", mf.ticks_per_beat, "tracks:", len(mf.tracks))

n_grid_snap = 0
n_chord_snap = 0

for ti, tr in enumerate(mf.tracks):
    # channel of this track
    track_channel = None
    for m in tr:
        if m.type in ("note_on", "note_off"):
            track_channel = m.channel
            break
    is_drum = (track_channel == 9)

    has_notes = any(m.type == "note_on" and m.velocity > 0 for m in tr)
    if not has_notes:
        # conductor/meta track — leave unchanged
        continue

    # absolute-time events
    abs_events = []
    t = 0
    for m in tr:
        t += m.time
        abs_events.append((t, m))

    pending = {}   # (channel, note) -> list of (orig_start, new_start, new_note)
    new_events = []  # (abs_time, order_idx, message)

    for order, (t, m) in enumerate(abs_events):
        if m.type == "note_on" and m.velocity > 0:
            key = (m.channel, m.note)
            ns = snap(t)
            if ns != t:
                n_grid_snap += 1
            nn = m.note
            if not is_drum:
                d = nearest_chord_delta(m.note, t // BAR)
                if d != 0:
                    nn = m.note + d
                    n_chord_snap += 1
            if ns < TARGET:
                pending.setdefault(key, []).append((t, ns, nn))
                new_events.append((ns, order, m.copy(note=nn)))
        elif m.type == "note_off" or (m.type == "note_on" and m.velocity == 0):
            key = (m.channel, m.note)
            if pending.get(key):
                orig_start, ns, nn = pending[key].pop(0)
                ne = ns + (t - orig_start)
                ne = min(ne, TARGET)
                if ne > ns:
                    new_events.append((ne, order, m.copy(note=nn)))
            # orphan note_off (shouldn't happen) -> drop
        elif m.type == "end_of_track":
            continue  # handled below
        else:
            new_events.append((t, order, m))

    # sort by absolute time (stable by order)
    new_events.sort(key=lambda e: (e[0], e[1]))

    # rebuild track with delta times + padded end_of_track
    new_tr = mido.MidiTrack()
    last = 0
    for t, order, m in new_events:
        m.time = t - last
        last = t
        new_tr.append(m)
    pad = TARGET - last
    if pad < 0:
        pad = 0
    new_tr.append(mido.MetaMessage("end_of_track", time=pad))
    mf.tracks[ti] = new_tr

dst = MIDIDIR / "composition.mid"
mf.save(str(dst))
print(f"grid snaps: {n_grid_snap}, chord snaps: {n_chord_snap}")
print("wrote:", dst, dst.stat().st_size, "bytes")
