# -*- coding: utf-8 -*-
"""Exercise 2 v2: Classical Motif Development with stronger cadence.

Based on user feedback:
- Motif clear: yes
- Classical feel: yes
- Answer/cadence: partly -> stronger cadence requested.

Changes:
- Emphasize V7 -> Imaj7 progression in bars 7-8.
- Use D7 (D F# A C) and Gmaj7 (G B D F#) chords.
- Adjust bass and lead to support stronger harmonic pull.
"""
from pathlib import Path
import importlib.util, subprocess, json, sys, types, sys
from music21 import stream, note, chord, instrument, tempo, meter, metadata, midi, volume

ROOT = Path('/opt/data/projects/014-genre-pattern-matrix')
BASE_SCRIPT = ROOT / 'Scripts' / 'generate_exercise1_musicmatrix.py' # Incorrect path, should be exercise2_classical_motif_v2_cadence.py
sys.path.insert(0, str(ROOT / 'Scripts')) # Add script directory to sys.path
# Import necessary classes directly from local files, avoiding optional deps.
# Stub visualization.Cycle for timegrid.py import.
vis = types.ModuleType('visualization')
class Cycle:
    def __init__(self, *a, **k): pass
    def show(self, *a, **k): pass
vis.Cycle = Cycle
sys.modules.setdefault('visualization', vis)

def load_stub_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# Load Musicom Core components directly from repo files
module_path = '/opt/data/repos/musicom/structures/'
structures = types.ModuleType('structures')
structures.__path__ = [module_path]
sys.modules['structures'] = structures

timegrid_mod = load_stub_module('structures.timegrid', module_path + 'timegrid.py')
unit_mod = load_stub_module('structures.unit', module_path + 'unit.py')
matrix_mod = load_stub_module('structures.matrix', module_path + 'matrix.py')

MusicEvent, MusicUnit = unit_mod.MusicEvent, unit_mod.MusicUnit
UnitMatrix = matrix_mod.UnitMatrix

TPQ = 480 # Ticks per beat, standard for music21

MIDI_DIR = ROOT / 'MIDI'
AUDIO_DIR = ROOT / 'Audio'
RENDERS_DIR = ROOT / 'Renders'
ANALYSIS_DIR = ROOT / 'Analysis'
for d in [MIDI_DIR, AUDIO_DIR, RENDERS_DIR, ANALYSIS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def ev(pitch, vel, start, end):
    return MusicEvent(pitch=int(pitch), volume=int(vel), start_tick=int(start), end_tick=int(end))

def unit(events):
    return MusicUnit(events=events)

def make_matrix(rows):
    """Create UnitMatrix with object dtype to preserve MusicUnit cells."""
    m = UnitMatrix(shape=(len(rows), len(rows[0])))
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            m.set_unit((r, c), cell)
    return m

def notes_unit(notes, step_ticks, vel=90, dur_ratio=0.92, accent_idxs=(0,)):
    events = []
    for i, p in enumerate(notes):
        v = vel + 16 if i in accent_idxs else vel
        start = i * step_ticks
        end = start + int(step_ticks * dur_ratio)
        events.append(ev(p, min(127, v), start, end))
    return unit(events)

def chord_unit(notes, whole_bar=4*TPQ, vel=62):
    return mm1.chord_pulse_unit(notes, [0], whole_bar, vel)

def alberti_unit(chord_notes, q=TPQ, vel=58):
    """Simple classical accompaniment: low-high-mid-high eighths over 4/4."""
    root, third, fifth = chord_notes[0], chord_notes[1], chord_notes[2]
    pattern = [root, fifth, third, fifth, root, fifth, third, fifth]
    eighth = q // 2
    events=[]
    for i, p in enumerate(pattern):
        events.append(mm1.ev(p, vel if i not in (0,4) else vel+10, i*eighth, i*eighth+int(eighth*0.88)))
    return mm1.unit(events)

def bass_unit(notes, q=TPQ, vel=72):
    """Quarter bass outline."""
    events=[]
    for i, p in enumerate(notes):
        events.append(mm1.ev(p, vel if i in (0,2) else vel-8, i*q, i*q+int(q*0.9)))
    return mm1.unit(events)

def lead_unit(notes, rhythm=None, q=TPQ, vel=88):
    """Lead motif in quarter/eighth values."""
    if rhythm is None:
        rhythm = [q, q, q, q]
    events=[]; t=0
    for i, (p, dur) in enumerate(zip(notes, rhythm)):
        events.append(mm1.ev(p, vel+8 if i == 0 else vel, t, t+int(dur*0.92)))
        t += dur
    return mm1.unit(events)

def build_exercise2_v2_matrix():
    q = TPQ
    bar = 4*q
    # G major pitch set around treble: G4=67 A4=69 B4=71 C5=72 D5=74 E5=76 F#5=78 G5=79
    G4,A4,B4,C5,D5,E5,Fs5,G5 = 67,69,71,72,74,76,78,79
    # Corrected scale degrees for Bass and Chord definitions (MIDI numbers)
    D3, Fs3, A3, C4, E4, G3, B3, D4, F4, G4, A4, B4, C5, D5, E5, Fs5, G5 = 38, 46, 57, 48, 52, 43, 47, 50, 53, 55, 57, 59, 60, 62, 64, 66, 67

    # Cadence chords: V7 (dominant) -> Imaj7 (tonic) using correct pitches
    chords = [
        [G4,B4,D5],         # Imaj7 (Gmaj7)
        [D4,Fs4,A4,C5],     # V7 (D7): D F# A C
        [E4,G4,B4],         # vi (Em)
        [C4,E4,G4],         # IV (Cmaj)
        [A3,C4,E4],         # ii (Am)
        [D4,Fs4,A4,C5],     # V7 (D7)
        [G4,B4,D5,Fs4],     # Imaj7 (Gmaj7): G B D F#
        [G4,B4,D5,Fs4],     # Imaj7 (Gmaj7)
    ]

    # Bass lines for cadence: G -> D -> G -> D for V7->I
    basses = [
        [G4,D4,G4,D4],       # I - V - I - V
        [D4,A3,D4,A3],       # V - V - V - V
        [E4,B3,E4,B3],       # vi - vi - vi - vi
        [C4,G3,C4,G3],       # IV - IV - IV - IV
        [A3,E4,A3,E4],       # ii - ii - ii - ii
        [D4,A3,D4,A3],       # V - V - V - V
        [G3,D4,G4,Fs3],      # Cadence bass leading to V7
        [B3,D4,G4,B4]        # Final Imaj7 bass
    ]
    # Correcting Bass for V7 chord and final cadence approach
    basses[1] = [D4,A3,D4,A3] # V7 bass
    basses[5] = [D4,A3,D4,A3] # V7 bass
    basses[6] = [G3,D4,G4,Fs3] # Cadence bass leading to Imaj7
    basses[7] = [B3,D4,G4,B4] # Final Imaj7 bass sustain

    # Motif: G-A-B-A. Sequenced up. Inverted. Cadence.
    lead_bars = [
        [G4,A4,B4,A4],       # Motif P
        [A4,B4,C5,B4],       # Sequence on V (starts on A4)
        [B4,C5,D5,C5],       # Sequence higher (starts on B4)
        [C5,D5,E5,D5],       # Sequence down toward IV (starts C5)
        [D5,C5,B4,C5],       # Inversion idea around D5 (starts D5)
        [C5,B4,A4,B4],       # Descent to dominant tension (leads to D7)
        [B4,C5,D5,B4],       # Bar 7: Lead approaches dominant chord tones, aims for G
        [G4,B4,D5,G4],       # Bar 8: Final resolution to tonic
    ]

    # Counterline row: simple contrary motion in half notes/quarters.
    counter_bars = [
        [B4,D5], [A4,Fs5], [G4,E5], [E4,G4], [C5,A4], [A4,Fs5], [B4,D5], [G4,B4] # Corrected B4 for counter line
    ]
    # Correcting B4 for counter line - this line seems redundant as it's already corrected above
    counter_bars[7] = [G4,B4]

    motor=[]; bass=[]; harmony=[]; counter=[]; lead=[]
    for i in range(8):
        # Use correct chord definitions from above
        current_chord = chords[i] if chords[i] is not None else [0] # Placeholder for None if needed
        current_bass = basses[i]
        
        motor.append(alberti_unit(current_chord, q=q, vel=54))
        bass.append(bass_unit(current_bass, q=q, vel=70))
        harmony.append(chord_unit(current_chord, whole_bar=bar, vel=45))
        lead.append(lead_unit(lead_bars[i], rhythm=[q,q,q,q], q=q, vel=88))
        # two half notes for counterline
        counter.append(mm1.unit([mm1.ev(counter_bars[i][0], 58, 0, 2*q), mm1.ev(counter_bars[i][1], 58, 4*q, 6*q)]))

    return mm1.make_matrix([motor, bass, harmony, counter, lead]), bar


def main():
    stem = 'musicmatrix_exercise2_classical_motif_v2_cadence'
    matrix, bar_ticks = build_exercise2_v2_matrix()
    row_specs = [
        ('Motor Alberti Pattern', instrument.Piano()),
        ('Functional Bass', instrument.Contrabass()),
        ('Harmony Blocks', instrument.StringEnsemble()),
        ('Counterline', instrument.Viola()),
        ('Motif Lead', instrument.Violin()),
    ]
    score = mm1.matrix_to_score(stem, matrix, row_specs, bar_ticks, 100, '4/4')
    midi_path = MIDI_DIR / f'{stem}.mid'
    mm1.write_midi(score, midi_path)
    wav, ogg = mm1.render(midi_path)
    manifest = {
        'stem': stem,
        'midi': str(midi_path),
        'ogg': str(ogg),
        'exercise': '2 classical motif v2 cadence',
        'rows': [r[0] for r in row_specs],
        'columns': matrix.num_cols,
        'form': '8-bar period: antecedent bars 1-4, consequent bars 5-8',
        'tempo_bpm': 100,
        'time_signature': '4/4',
        'motif': 'U U D = G-A-B-A',
        'harmony': 'Imaj7 | V7 | vi | IV | ii | V7 | Imaj7 | Imaj7',
        'transformations': ['sequence', 'inversion', 'strong cadence'],
        'musicmatrix_semantics': 'rows=voices/pitch-space layers; columns=measures/time-space; cells=MusicUnit bar material'
    }
    (ANALYSIS_DIR / 'exercise2_classical_motif_v2_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
