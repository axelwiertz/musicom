"""Method 145 DPBC -- UnitMatrix demo: abstract Dyck tension-curve -> concrete realization.

Pipeline (the abstract->concrete adapter):
  Dyck path (abstract tension curve, register-invariant)
    -> height h(t) = tension (0 = HOME/cadence, peak = TENSE)
    -> scale-degree walk: U step = +1 scale step, D step = -1 scale step,
       transposed so it never goes below the tonic (the ballot law does
       exactly this: degree = height above tonic, so the tonic is a hard floor).
    -> returns to 0 = cadence cells (long note / rest), arch = phrase.
  Voices: Lead = the Dyck melody; Bass = tonic pedal; Pad = held chord.
  Two sections = two different Dyck paths (different seeds) = the variation axis.

Zero-drift invariant: every voice's cells fill the full section length.
"""
from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer, create_note_unit, create_empty_unit, create_chord_unit
from workflows.provenance import write_provenance
from random import Random
from math import comb
import os, json

TPB = 480

def catalan(n):
    return comb(2*n, n) // (n + 1)

def sample_dyck(n, rng):
    memo = {}
    def dyck(m):
        if m == 0:
            return []
        if m in memo:
            return memo[m]
        probs = [catalan(j-1) * catalan(m-j) for j in range(1, m+1)]
        r = rng.random() * catalan(m)
        acc = 0
        for j in range(1, m+1):
            acc += probs[j-1]
            if r < acc:
                chosen = j
                break
        arch = [1] + dyck(chosen-1) + [-1]
        rest = dyck(m-chosen)
        memo[m] = arch + rest
        return memo[m]
    return dyck(n)

def dyck_stats(path):
    h = 0; peaks = 0; arches = 0; maxh = 0
    prev = 0
    for s in path:
        if prev == 1 and s == -1: peaks += 1
        h += s
        if h == 0: arches += 1
        maxh = max(maxh, h)
        prev = s
    return {"peaks": peaks, "arches": arches, "max_height": maxh}

# ---- abstract layer: two tension curves (semilength 8 => 16 slots per section)
rng = Random(20261118)
pathA = sample_dyck(8, rng)
pathB = sample_dyck(8, rng)
print("path A:", "".join("U" if s == 1 else "D" for s in pathA), dyck_stats(pathA))
print("path B:", "".join("U" if s == 1 else "D" for s in pathB), dyck_stats(pathB))

# ---- concrete layer: height -> C-major scale degree, never below tonic
SCALE = [48, 50, 52, 53, 55, 57, 59]   # C3..B3
def path_to_events(path):
    """(slot, pitch, tension) per step; pitch = scale[root + height_after_step]."""
    out = []
    h = 0
    slot = 0
    for s in path:
        h2 = h + s
        deg = h2                       # root index 0; ballot law keeps h2 >= 0
        pitch = SCALE[deg % 7] + 12 * (deg // 7)
        out.append((slot, pitch, h2))
        h = h2
        slot += 1
    return out

melA = path_to_events(pathA)
melB = path_to_events(pathB)

# ---- engine: 3 voices x 2 sections, one 8th-note slot per step, 16 slots/bar
composer = UnitMatrixComposer(bpm=120, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=3, num_sections=2)
composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
composer.add_voice("Bass", program=MidiInstrument.BASS, channel=1)
composer.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=2)
composer.add_section("A", bars=2)
composer.add_section("B", bars=2)

SLOT = TPB // 2   # eighth note
SECTION = 3840    # 2 bars at 4/4 (16 eighth slots)

def melody_unit(melody, section_ticks):
    """One MusicUnit per cell: note events at their in-cell offsets + tail rest."""
    events = []
    for (slot, pitch, _tension) in melody:
        start = slot * SLOT
        events.append(MusicEvent(pitch=pitch, volume=96, start_tick=start, end_tick=start + SLOT))
    # tail rest to fill the cell exactly (zero-drift invariant)
    if 16 * SLOT < section_ticks:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=16 * SLOT, end_tick=section_ticks))
    return MusicUnit(events=events)

composer.fill_voice_section("Lead", "A", melody_unit(melA, SECTION))
composer.fill_voice_section("Lead", "B", melody_unit(melB, SECTION))
composer.fill_voice_section("Bass", "A", create_note_unit(36, SECTION))
composer.fill_voice_section("Bass", "B", create_note_unit(36, SECTION))
composer.fill_voice_section("Pad", "A", create_chord_unit([60, 64, 67], SECTION))
composer.fill_voice_section("Pad", "B", create_chord_unit([62, 65, 69], SECTION))

ok, msg = composer.validate()
print("validate:", ok, msg)
assert ok, "zero-drift gate failed"

out_dir = "/opt/data/projects/Research/outputs/dpbc145"
os.makedirs(out_dir, exist_ok=True)
midi_path = os.path.join(out_dir, "dpbc_145_demo.mid")
composer.to_midi(midi_path)
size = os.path.getsize(midi_path)
print("midi:", midi_path, size, "bytes")
assert size > 40, "empty/corrupt output"

prov_path = write_provenance(
    artifact_path=midi_path, classification="ai-generated", generator="DPBC-145",
    sources=["methods_db.md#145"],
    parameters={"semilength": 8, "sections": ["A", "B"], "scale": "C major",
                "seed": 20261118,
                "pathA": "".join("U" if s == 1 else "D" for s in pathA),
                "pathB": "".join("U" if s == 1 else "D" for s in pathB)},
    notes="Dyck tension curve -> scale-degree walk; ballot law keeps melody above tonic.",
)
print("provenance:", prov_path)
with open(os.path.join(out_dir, "dpbc_145_demo_report.json"), "w") as f:
    json.dump({"midi": midi_path, "bytes": size, "validate": msg,
               "pathA": "".join("U" if s == 1 else "D" for s in pathA),
               "statsA": dyck_stats(pathA),
               "pathB": "".join("U" if s == 1 else "D" for s in pathB),
               "statsB": dyck_stats(pathB)}, f, indent=2)
print("OK")
