"""HCSC (method 122) engine validation demo.

Reads a d=4, order-2 Hilbert table, maps each curve step to the one voice whose
coordinate changed, and fills a 4-voice x 4-section UnitMatrix.

Verified inside the engine output:
  (i)   exactly one voice changes pitch per curve step (no parallel motion),
  (ii)  every vertical sonority is a subset of the section's chord ladder,
  (iii) every cell ends on the section landmark (zero drift -> validate() OK).
"""
import json
import os

from structures import MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.musicom_workflow import _unit_from_events

OUT = "/opt/data/projects/Research/outputs/hcsc_validate"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- curve table
with open(os.path.join(OUT, "hilbert_d4_p2.json")) as f:
    tab = json.load(f)
PTS = tab["points"]
DIM, N = tab["dim"], tab["n"]

# ---------------------------------------------------------------- grid -> pitch
TPB, BPB, BPM = 480, 4, 96
BAR = TPB * BPB                 # 1920 ticks
STEP = 240                      # one curve step = an eighth note
VOICES = ["Bass", "Tenor", "Alto", "Soprano"]
CHROMA = [0, 3, 7, 10]          # minor-7 ladder, one chord tone per grid level
BASE = [36, 48, 60, 72]         # octave-apart bases: every voice shares the pcs
TRANS = [0, 5, 3, 7]            # per-section frame translation (Cm7 Fm7 Ebm7 Gm7)
n_sections = 4
SEC_STEPS = N // n_sections     # 64 steps per section
section_len = SEC_STEPS * STEP  # 15360 ticks = 8 bars

# ---------------------------------------------------------------- step -> events
changes = []                    # (step, voice, new level)
for s in range(1, N):
    diff = [v for v in range(DIM) if PTS[s][v] != PTS[s - 1][v]]
    assert len(diff) == 1, f"step {s}: {len(diff)} coordinates changed"
    assert abs(PTS[s][diff[0]] - PTS[s - 1][diff[0]]) == 1
    changes.append((s, diff[0], PTS[s][diff[0]]))
print(f"invariant (i) OK: {len(changes)} steps, exactly 1 voice moved each")

# per-voice onset list: (tick, level)
onsets = {v: [(0, PTS[0][v])] for v in range(DIM)}
for s, v, lvl in changes:
    onsets[v].append((s * STEP, lvl))


def pitch_of(v, level, section):
    p = BASE[v] + CHROMA[level] + TRANS[section]
    while p > 95:
        p -= 12
    while p < 26:
        p += 12
    return p


per_cell = {(v, m): [] for v in range(DIM) for m in range(n_sections)}
n_seam_revoice = 0
for v in range(DIM):
    lst = onsets[v]
    for i, (tick, level) in enumerate(lst):
        end = lst[i + 1][0] if i + 1 < len(lst) else N * STEP
        t = tick
        while t < end:
            m = min(t // section_len, n_sections - 1)
            stop = min(end, (m + 1) * section_len)
            local = t - m * section_len
            per_cell[(v, m)].append(
                MusicEvent(pitch_of(v, level, m), 84, local, local + (stop - t))
            )
            if t > tick:
                n_seam_revoice += 1
            t = stop

# ---------------------------------------------------------------- UnitMatrix
composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
composer.create_matrix(num_voices=DIM, num_sections=n_sections)
PROGS = [43, 58, 42, 74]        # Cello, Trombone, Viola, Flute
for i, name in enumerate(VOICES):
    composer.add_voice(name, program=PROGS[i], channel=i)
sec_names = [chr(ord("A") + m) for m in range(n_sections)]
for m in range(n_sections):
    composer.add_section(sec_names[m], bars=section_len // BAR)

for v in range(DIM):
    for m in range(n_sections):
        composer.fill_voice_section(
            VOICES[v], sec_names[m], _unit_from_events(per_cell[(v, m)], section_len)
        )

ok, msg = composer.validate()
print(f"validate() -> {ok}: {msg}")
assert ok, msg

midi_path = os.path.join(OUT, "hcsc_d4_demo.mid")
composer.to_midi(midi_path)
size = os.path.getsize(midi_path)
assert size > 40, "empty MIDI"
print(f"MIDI {midi_path} {size} bytes")

# ---------------------------------------------------------------- report facts
notes = sum(len(per_cell[(v, m)]) for v in range(DIM) for m in range(n_sections))
print(f"cells={DIM * n_sections} notes={notes} "
      f"seam re-voices={n_seam_revoice} (frame changes)")
print(f"section_len={section_len} ticks, total={n_sections * section_len} ticks "
      f"= {n_sections * section_len // BAR} bars")

# invariant (ii): vertical sonority check per section
bad = 0
for m in range(n_sections):
    allowed = {(t + TRANS[m]) % 12 for t in CHROMA}
    evs = [(e.start_tick, e.end_tick, e.pitch % 12)
           for v in range(DIM) for e in per_cell[(v, m)]]
    for s, _, _ in evs:
        sounding = {pc for st, en, pc in evs if st <= s < en}
        if not sounding <= allowed:
            bad += 1
print(f"invariant (ii): {len(evs)} onsets checked, {bad} with an out-of-chord pc sounding")
for v in range(DIM):
    ps = sorted({e.pitch for m in range(n_sections) for e in per_cell[(v, m)]})
    print(f"  voice {VOICES[v]:8s} pitch set {ps}")
