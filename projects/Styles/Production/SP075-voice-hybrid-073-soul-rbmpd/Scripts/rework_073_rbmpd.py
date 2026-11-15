# -*- coding: utf-8 -*-
"""Rework 073-soul-rbmpd.mid for the SP-075 production job (2026-11-15).

Pre-flight 3-rule audit of the source:
  - Zero-drift: PASS (all tracks 46080 ticks)
  - Harmony (in scale, C natural minor): PASS (0 out-of-scale)
  - Grid sync (16th = 120 ticks): FAIL — 27003 off-grid onsets, ALL in the
    Lead voice. The Lead is the raw RBMPD brownian line at 1-tick onset
    resolution (27239 notes) — never grid-quantized in the composition pass.
  - Harmony (chord tone of bar): FAIL — 4766 out-of-chord Lead notes. The
    composition's lead quantization indexed the GLOBAL progression with a
    SECTION-LOCAL bar index, so sections 2/3/5 were quantized against the
    wrong bars.

Rework (two-phase, engine-only): Lead -> snap onset to nearest 16th cell
(120 ticks), merge per-cell (keep loudest note), chord-tone quantize against
the CORRECT global per-bar chord. Other voices already clean -> preserved.
Re-export via UnitMatrixComposer (validate() zero-drift gate); original kept
as phase1 sidecar. No raw mido writing.
"""
import os
import shutil
import json
from collections import defaultdict, deque

import mido

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer

SRC = "/opt/data/repos/musicom/projects/Styles/Soul/073-soul-rbmpd/MIDI/073-soul-rbmpd.mid"
OUT = "/opt/data/repos/musicom/projects/Styles/Production/SP075-voice-hybrid-073-soul-rbmpd"
MID = os.path.join(OUT, "MIDI")
os.makedirs(MID, exist_ok=True)

BPM = 92
TPB = 480
BAR = 1920
NBARS = 24
NSEC = 6
BARS_PER_SEC = 4
SECTION = BARS_PER_SEC * BAR      # 7680
GRID = 120                        # 16th note

VOICES = [
    ("Lead", 75, 0),
    ("Horns", 61, 1),
    ("Rhodes", 4, 2),
    ("Bass", 33, 3),
    ("Drums", 0, 9),
]

SCALE_PCS = {0, 2, 3, 5, 7, 8, 10}

PROG = [60, 65, 67, 63] * 2 + [60, 67, 60, 68] + [60, 65, 67, 60] + \
       [60, 65, 67, 63] + [60, 67, 65, 60]
CHORDS = {
    60: [60, 63, 67],   # Cm  i
    65: [65, 68, 72],   # Fm  iv
    67: [67, 70, 74],   # G   V
    63: [63, 67, 70],   # Eb  III
    68: [68, 72, 75],   # Ab  VI
}
assert len(PROG) == NBARS, len(PROG)
CHORD_PCS = [{t % 12 for t in CHORDS[PROG[b]]} for b in range(NBARS)]


def snap_to_chord(pitch, bar):
    pc = pitch % 12
    tones = CHORD_PCS[min(bar, NBARS - 1)]
    if pc in tones:
        return pitch
    best, best_d = None, 999
    for ct in tones:
        delta = ((ct - pc + 6) % 12) - 6
        cand = pitch + delta
        d = abs(delta)
        if d < best_d or (d == best_d and cand < best):
            best_d, best = d, cand
    return best


def read_chan_notes():
    """FIFO-matched notes per channel: dict chan -> list of (on, off, note, vel).

    Correct for overlapping same-pitch notes (the RBMPD lead re-triggers the
    same pitch hundreds of times before a note_off).
    """
    mf = mido.MidiFile(SRC)
    by_chan = defaultdict(list)
    for tr in mf.tracks:
        t = 0
        active = defaultdict(deque)   # pitch -> deque[(on, vel)]
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0 and m.note > 0:
                active[m.note].append((t, m.velocity))
            elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
                q = active.get(m.note)
                if q:
                    on, vel = q.popleft()
                    by_chan[m.channel].append((on, t, m.note, vel))
    return by_chan


by_chan = read_chan_notes()
print("channels read:", {c: len(v) for c, v in by_chan.items()})

# ---- Lead (ch 0): grid-quantize + merge + chord-quantize -------------------
before_off = 0
before_ooc = 0
cells = defaultdict(list)
for (on, off, note, vel) in by_chan.get(0, []):
    if on % GRID != 0:
        before_off += 1
    if (note % 12) not in CHORD_PCS[min(on // BAR, NBARS - 1)]:
        before_ooc += 1
    cell = int(round(on / GRID)) * GRID
    cells[cell].append((note, vel))

lead_events = []
for cell in sorted(cells):
    note, vel = max(cells[cell], key=lambda x: (x[1], x[0]))
    pitch = snap_to_chord(note, cell // BAR)
    lead_events.append(MusicEvent(
        pitch=int(pitch), volume=int(vel),
        start_tick=int(cell), end_tick=int(min(cell + GRID, NBARS * BAR))))
print("lead: before off-grid=%d out-of-chord=%d -> cells=%d"
      % (before_off, before_ooc, len(lead_events)))


def ev_for_chan(chan):
    out = []
    for (on, off, note, vel) in by_chan.get(chan, []):
        out.append(MusicEvent(pitch=int(note), volume=int(vel),
                              start_tick=int(on),
                              end_tick=int(min(off, NBARS * BAR))))
    return out


voice_abs = {
    "Lead": lead_events,
    "Horns": ev_for_chan(1),
    "Rhodes": ev_for_chan(2),
    "Bass": ev_for_chan(3),
    "Drums": ev_for_chan(9),
}
for v in voice_abs:
    print("  voice", v, "events", len(voice_abs[v]))

# ---- build via engine ------------------------------------------------------
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=5, num_sections=NSEC)
for name, prog, ch in VOICES:
    composer.add_voice(name, program=prog, channel=ch)
for s in range(NSEC):
    composer.add_section(f"Sec{s+1}", bars=BARS_PER_SEC)

for vi, (name, prog, ch) in enumerate(VOICES):
    for s in range(NSEC):
        lo = s * SECTION
        hi = lo + SECTION
        evs = []
        for e in voice_abs[name]:
            if lo <= e.start_tick < hi:
                evs.append(MusicEvent(
                    pitch=e.pitch, volume=e.volume,
                    start_tick=e.start_tick - lo,
                    end_tick=min(e.end_tick - lo, SECTION)))
        if not any(e.pitch == 0 and e.end_tick == SECTION for e in evs):
            evs.append(MusicEvent(pitch=0, volume=0,
                                  start_tick=SECTION - 1, end_tick=SECTION))
        composer.fill_voice_section(name, f"Sec{s+1}", MusicUnit(events=evs))

ok, msg = composer.validate()
print("validate:", ok, msg)
assert ok, msg

out_midi = os.path.join(MID, "073-soul-rbmpd.mid")
composer.to_midi(out_midi)
print("reworked MIDI:", out_midi, os.path.getsize(out_midi), "bytes")

phase1 = os.path.join(MID, "073-soul-rbmpd-phase1.mid")
shutil.copyfile(SRC, phase1)
print("phase1 sidecar:", phase1, os.path.getsize(phase1), "bytes")

# ---- re-audit (skip drums for grid/scale/chord; zero-drift over all) ------
mf = mido.MidiFile(out_midi)
off_grid = out_scale = out_chord = total = 0
spans = set()
for tr in mf.tracks:
    t = 0
    notes = []
    chans = set()
    for m in tr:
        t += m.time
        if m.type in ("note_on", "note_off"):
            chans.add(m.channel)
        if m.type == "note_on" and m.velocity > 0 and m.note > 0:
            notes.append({"note": m.note, "on": t})
    if not notes:
        continue
    spans.add(t)
    is_drum = 9 in chans
    for n in notes:
        total += 1
        if is_drum:
            continue
        if n["on"] % GRID != 0:
            off_grid += 1
        pc = n["note"] % 12
        bar = min(n["on"] // BAR, NBARS - 1)
        if pc not in SCALE_PCS:
            out_scale += 1
        if pc not in CHORD_PCS[bar]:
            out_chord += 1

audit = {
    "off_grid": off_grid, "out_scale": out_scale, "out_chord": out_chord,
    "total_onsets": total, "track_spans": sorted(spans),
    "zero_drift": len(spans) == 1,
}
print("re-audit:", json.dumps(audit))
print("before: off_grid=%d out_chord=%d -> after: off_grid=%d out_chord=%d"
      % (before_off, before_ooc, off_grid, out_chord))

with open(os.path.join(MID, "rework_audit.json"), "w") as f:
    json.dump({"before_off_grid": before_off, "before_out_of_chord": before_ooc,
               "after": audit}, f, indent=2)

assert off_grid == 0, "grid rework did not reach 0"
assert out_scale == 0, "scale violated after rework"
assert out_chord == 0, "chord rework did not reach 0"
assert len(spans) == 1, "zero-drift violated after rework"
print("REWORK CLEAN")
