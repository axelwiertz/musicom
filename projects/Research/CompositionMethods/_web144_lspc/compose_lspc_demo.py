"""Method 144 (LSPC) — concrete demo: a Langford L(2,8) piece rendered through the
musicom engine (UnitMatrix).  8 voices x 4 sections, 16 slots (quarter notes).

Every slot is occupied exactly once (perfect cover).  Voice k speaks twice, at
distance k+1 slots.  Zero drift by construction.
"""
import json, os, sys

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_empty_unit,
)

OUT = os.path.dirname(os.path.abspath(__file__))

# --- the sequence (Langford L(2,8), found by the verifier) --------------------
SEQ = (8, 3, 7, 2, 6, 3, 2, 4, 5, 8, 7, 6, 4, 1, 5, 1)
N = 8
assert len(SEQ) == 2 * N

TPB, BPB = 480, 4
SLOT = TPB                 # one slot = one quarter note
BARS = len(SEQ) // BPB     # 16 slots / 4 per bar = 4 bars
SEC_TICKS = BPB * TPB      # 1920 ticks per section

# symbol k -> C-major scale degree (weak tonal gravity, registral ladder)
SCALE = [0, 2, 4, 5, 7, 9, 11, 12]
def pitch_of(k: int) -> int:
    return 48 + SCALE[k - 1]

# ---------------------------------------------------------------- compose ----
composer = UnitMatrixComposer(bpm=120, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=N, num_sections=BARS)

GM_MARIMBA = 12            # GM program 13 (1-based) = Marimba; engine is 0-based
for k in range(1, N + 1):
    composer.add_voice(f"V{k}", program=GM_MARIMBA, channel=k - 1)

for b in range(BARS):
    composer.add_section(chr(ord("A") + b), bars=1)

# slot -> (voice, offset in section)
slots = []
for pos, sym in enumerate(SEQ):
    sec = pos // BPB
    off = (pos % BPB) * SLOT
    slots.append((sym, sec, off))

# build per-voice-per-section event lists
cell_events = {(k, b): [] for k in range(1, N + 1) for b in range(BARS)}
for sym, sec, off in slots:
    cell_events[(sym, sec)].append((off, pitch_of(sym)))

for k in range(1, N + 1):
    for b in range(BARS):
        evs = sorted(cell_events[(k, b)])
        if not evs:
            unit = create_empty_unit(SEC_TICKS)
        else:
            events = []
            for off, pitch in evs:
                end = min(off + SLOT, SEC_TICKS)          # no note crosses the seam
                events.append(MusicEvent(pitch=pitch, volume=96,
                                         start_tick=off, end_tick=end))
            # terminal landmark -> cell spans the whole section (zero drift)
            last_end = max(e.end_tick for e in events)
            if last_end < SEC_TICKS:
                events.append(MusicEvent(pitch=0, volume=0,
                                         start_tick=last_end, end_tick=SEC_TICKS))
            unit = MusicUnit(events=events)
        composer.fill_voice_section(f"V{k}", chr(ord("A") + b), unit)

ok, msg = composer.validate()
print("validate:", ok, msg)
assert ok, msg

mid = os.path.join(OUT, "lspc_144_langford8.mid")
composer.to_midi(mid)
size = os.path.getsize(mid)
print("midi bytes:", size)
assert size > 40

# ---------------------------------------------------------------- audit ------
from collections import Counter
per_section = Counter(s for _, s, _ in slots)
lags = {}
for pos, sym in enumerate(SEQ):
    lags.setdefault(sym, []).append(pos)
lag_list = sorted(v[1] - v[0] for v in lags.values())
report = dict(
    sequence=list(SEQ), n=N, slots=len(SEQ), bars=BARS, voices=N,
    events=sum(len(v) for v in cell_events.values()),
    events_per_voice={k: len(lags[k]) for k in sorted(lags)},
    events_per_section=dict(sorted(per_section.items())),
    lag_spectrum=lag_list,
    lag_spectrum_complete=(lag_list == list(range(2, N + 2))),
    pitches=[pitch_of(k) for k in range(1, N + 1)],
    midi=mid, midi_bytes=size,
)
print(json.dumps(report, indent=2))
with open(os.path.join(OUT, "lspc_144_demo_report.json"), "w") as f:
    json.dump(report, f, indent=2)
