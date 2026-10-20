# -*- coding: utf-8 -*-
"""Zero-drift normalization rework (2026-10-20).

Source: Styles/Latin/bossa-nova-daily-2026-06-15/composition.mid (raw-mido
"daily pattern" file, pre-UnitMatrixComposer).

Finding: note-bearing tracks end at 3840 / 3720 / 3660 ticks (final-note
durations differ by design).  Content is all within the 2-bar span (3840 ticks)
and 0 off-grid / 0 out-of-scale / 0 out-of-chord, but the strict zero-drift
gate ("all note tracks equal length") reads NOT equal.

Fix: pad each note-bearing track's end_of_track delta so the track spans exactly
3840 ticks (2 bars x 1920).  This is the musicom terminal-landmark convention
(silent tail pad) — NO note is moved, NO duration changed, audio is byte-identical
to the source render.  Written into the production folder (never overwrites source).
"""
import mido
from pathlib import Path

SRC = Path("/opt/data/repos/musicom/projects/Styles/Latin/bossa-nova-daily-2026-06-15/composition.mid")
OUT = Path("/opt/data/repos/musicom/projects/Styles/Production/SP111-odd1-granular-bossa-nova-daily")
MIDIDIR = OUT / "MIDI"
MIDIDIR.mkdir(parents=True, exist_ok=True)

TARGET = 3840   # 2 bars * 1920 ticks at TPB 480

mf = mido.MidiFile(str(SRC))
print("input type:", mf.type, "tpb:", mf.ticks_per_beat)

for ti, tr in enumerate(mf.tracks):
    total = 0
    eot_idx = None
    n_notes = 0
    for i, m in enumerate(tr):
        total += m.time
        if m.type == "note_on" and m.velocity > 0:
            n_notes += 1
        if m.type == "end_of_track":
            eot_idx = i
            break
    if eot_idx is None or n_notes == 0:
        # conductor/meta track (no notes) — leave as-is
        print(f"track {ti}: no notes (length {total}) — leave")
        continue
    if total < TARGET:
        pad = TARGET - total
        tr[eot_idx].time += pad
        print(f"track {ti}: notes={n_notes} length {total} -> {total + pad} (pad {pad})")
    else:
        print(f"track {ti}: notes={n_notes} length {total} (no pad needed)")

dst = MIDIDIR / "composition.mid"
mf.save(str(dst))
print("wrote:", dst, dst.stat().st_size, "bytes")

# ---- re-audit (zero-drift only) ----
check = mido.MidiFile(str(dst))
lens = []
for tr in check.tracks:
    t = 0
    notes = 0
    for m in tr:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            notes += 1
    lens.append((notes, t))
print("re-audit (notes, length):", lens)
note_lens = [t for n, t in lens if n > 0]
print("note-track lengths:", note_lens)
print("ZERO-DRIFT:", "PASS" if len(set(note_lens)) == 1 else "FAIL")
