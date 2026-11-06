"""compose_chc136_demo.py — Collatz Hailstone Composition (CHC), method 136 demo.

4 voices = hailstone trajectories of record-holder seeds (27, 54, 73, 97).
Each step = one grid slot; parity = gesture; bit-length = register/velocity;
the universal 4-2-1 tail = HOME cadence (looped as an ostinato after each
row's trajectory ends, preserving the equal-length / zero-drift invariant).

Sanctioned spine: create_matrix -> add_voice -> add_section ->
fill_voice_section (unit built from events via _unit_from_events) ->
validate -> to_midi (musicom engine).
"""
import os

from structures import MidiInstrument, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.musicom_workflow import _unit_from_events
from workflows.provenance import write_provenance

# ---- Collatz machinery (pure, no MIDI) ----
def T(n):  # shortcut map: even -> n/2, odd -> (3n+1)/2
    return (3 * n + 1) // 2 if n % 2 else n // 2

def trajectory(seed):
    out = []
    while seed != 1:
        out.append(seed)
        seed = T(seed)
    out.append(1)
    return out

# ---- musical folding ----
DEGREES = [0, 2, 4, 5, 7, 9, 11]  # C major
def fold(a_n, base=36):
    """Register from bit-length (altitude), degree from residue mod 7. Clamped to MIDI range."""
    octave = (a_n.bit_length() - 1) // 3
    degree = DEGREES[a_n % 7]
    return min(120, base + 12 * octave + degree)

def velocity(a_n):
    return min(120, 32 + 8 * (a_n.bit_length() - 1))

# ---- matrix geometry ----
SEEDS = [27, 54, 73, 97]          # record holders: 111/112/115/118 steps (shortcut)
STEP_TICKS = 480                  # one slot = one beat
SLOTS_PER_SECTION = 20
NUM_SECTIONS = 6
SECTION_TICKS = STEP_TICKS * SLOTS_PER_SECTION

trajs = [trajectory(s) for s in SEEDS]
LONGEST = max(len(t) for t in trajs)                 # 118 steps for seed 97
assert LONGEST <= NUM_SECTIONS * SLOTS_PER_SECTION   # fits the 120-slot grid

composer = UnitMatrixComposer(bpm=120, ticks_per_beat=480, beats_per_bar=4)
composer.create_matrix(num_voices=len(SEEDS), num_sections=NUM_SECTIONS)
INSTS = [MidiInstrument.STRING_ENSEMBLE, MidiInstrument.PIANO,
         MidiInstrument.VIOLIN, MidiInstrument.FLUTE]
for v, seed in enumerate(SEEDS):
    composer.add_voice(f"Hail{v}-{seed}", program=INSTS[v], channel=v)
for s in range(NUM_SECTIONS):
    composer.add_section(f"S{s}", bars=SECTION_TICKS // 1920)

for v, (seed, traj) in enumerate(zip(SEEDS, trajs)):
    base = 36 + 12 * v
    # per-section event lists; each section must END exactly at SECTION_TICKS
    sec_events = {s: [] for s in range(NUM_SECTIONS)}
    slot = 0
    for a in traj:
        section = slot // SLOTS_PER_SECTION
        if section >= NUM_SECTIONS:
            break
        dur = STEP_TICKS * (2 if a % 2 else 1)       # odd steps = longer cells
        start = (slot % SLOTS_PER_SECTION) * STEP_TICKS
        if start + dur > SECTION_TICKS:
            dur = SECTION_TICKS - start
        sec_events[section].append(MusicEvent(fold(a, base), velocity(a), start, start + dur))
        slot += dur // STEP_TICKS
    # rows that finished their trajectory pad remaining slots with the
    # 4-2-1 tail ostinato (HOME) — equal-length invariant preserved
    while slot < NUM_SECTIONS * SLOTS_PER_SECTION:
        section = slot // SLOTS_PER_SECTION
        start = (slot % SLOTS_PER_SECTION) * STEP_TICKS
        dur = STEP_TICKS * 2
        if start + dur > SECTION_TICKS:
            dur = SECTION_TICKS - start
        sec_events[section].append(MusicEvent(fold(4, base), velocity(4), start, start + dur))
        slot += dur // STEP_TICKS
    for s in range(NUM_SECTIONS):
        unit = _unit_from_events(sec_events[s], section_len=SECTION_TICKS)
        composer.fill_voice_section(f"Hail{v}-{seed}", f"S{s}", unit)

ok, msg = composer.validate()
assert ok, f"validate failed: {msg}"

out_dir = "/opt/data/repos/musicom/projects/Research/outputs/chc136_demo"
os.makedirs(out_dir, exist_ok=True)
midi_path = os.path.join(out_dir, "chc136_demo.mid")
composer.to_midi(midi_path)
assert os.path.getsize(midi_path) > 40, "empty/corrupt output"

write_provenance(
    midi_path,
    classification="ai-generated",
    generator="compose_chc136_demo.py (method 136, Collatz Hailstone Composition)",
    sources=["Wikipedia 'Collatz conjecture' (rev. 2026-11-05)",
             "OEIS A006877 record-holder seeds",
             "_web137/verify_136_CHC.py (12 fact-checks)"],
    parameters={
        "method": "136", "name": "Collatz Hailstone Composition (CHC)",
        "seeds": SEEDS, "steps": [len(t) for t in trajs],
        "slots_per_section": SLOTS_PER_SECTION, "num_sections": NUM_SECTIONS,
        "fold": "register=bit_length//3, degree=residue mod 7, clamp 120",
        "tail_ostinato": "4-2-1 loop after trajectory end (zero-drift padding)",
    },
    notes=f"validate()={ok}; longest row {LONGEST} steps (seed {SEEDS[trajs.index(max(trajs, key=len))]})",
)

print(f"validate: {msg}")
print(f"rows: {[len(t) for t in trajs]} steps; longest = {LONGEST} (seed {SEEDS[trajs.index(max(trajs, key=len))]})")
print(f"MIDI: {midi_path} ({os.path.getsize(midi_path)} bytes)")
