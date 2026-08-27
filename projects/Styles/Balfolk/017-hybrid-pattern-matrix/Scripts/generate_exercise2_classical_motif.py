# -*- coding: utf-8 -*-
"""Exercise 2: Classical Motif Development with MusicMatrix.

Focus:
- Classical = architecture + motivic transformation
- Form = antecedent/consequent 8-bar period
- Motif = U U D (rise, rise, fall)
- Transformations = sequence, inversion, cadence
"""
from pathlib import Path
import importlib.util, json
from music21 import instrument

ROOT = Path('/opt/data/projects/014-genre-pattern-matrix')
BASE_SCRIPT = ROOT / 'Scripts' / 'generate_exercise1_musicmatrix.py'
spec = importlib.util.spec_from_file_location('mm1', BASE_SCRIPT)
mm1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mm1)

TPQ = mm1.TPQ
MIDI_DIR = mm1.MIDI_DIR
AUDIO_DIR = mm1.AUDIO_DIR
ANALYSIS_DIR = mm1.ANALYSIS_DIR


def chord_unit(notes, whole_bar=4*TPQ, vel=62):
    return mm1.chord_pulse_unit(notes, [0], whole_bar, vel)


def alberti_unit(chord_notes, q=TPQ, vel=58):
    """Simple classical accompaniment: low-high-mid-high eighths over 4/4."""
    # order: root, fifth, third, fifth; repeated twice
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


def build_exercise2_matrix():
    q = TPQ
    bar = 4*q
    # G major pitch set around treble: G4=67 A4=69 B4=71 C5=72 D5=74 E5=76 F#5=78 G5=79
    G4,A4,B4,C5,D5,E5,Fs5,G5 = 67,69,71,72,74,76,78,79
    D4,E4,Fs4 = 62,64,66

    # Harmony: I | V | vi | IV | ii | V | I | I
    # Voiced low/mid for piano/string harmony.
    chords = [
        [55,59,62],  # G major: G3 B3 D4
        [50,54,57],  # D major: D3 F#3 A3
        [52,55,59],  # Em: E3 G3 B3
        [48,52,55],  # C: C3 E3 G3
        [45,48,52],  # Am: A2 C3 E3
        [50,54,57],  # D
        [55,59,62],  # G
        [55,59,62],  # G
    ]
    basses = [
        [43,50,55,50],  # G-D-G-D
        [38,45,50,45],  # D-A-D-A
        [40,47,52,47],  # E-B-E-B
        [36,43,48,43],  # C-G-C-G
        [33,40,45,40],  # A-E-A-E
        [38,45,50,45],  # D-A-D-A
        [43,50,55,50],  # G-D-G-D
        [43,55,59,67],  # cadence broaden
    ]

    # Motif U U D = G-A-B-A. Then sequence up/down, inversion D D U, cadence.
    lead_bars = [
        [G4,A4,B4,A4],       # motif P
        [D5,E5,Fs5,E5],      # sequence on V
        [E5,Fs5,G5,Fs5],     # sequence/lift
        [C5,D5,E5,D5],       # sequence down toward IV
        [E5,D5,C5,D5],       # inversion idea (D D U around E)
        [D5,C5,B4,A4],       # descent to dominant tension
        [B4,C5,D5,B4],       # resolution expansion
        [A4,Fs4,G4,G4],      # cadence: 2-7-1-1
    ]

    # Counterline row: simple contrary motion in half notes/quarters.
    counter_bars = [
        [B4,D5], [A4,Fs4], [G4,B4], [E4,G4], [C5,A4], [A4,Fs4], [G4,B4], [D4,G4]
    ]

    motor=[]; bass=[]; harmony=[]; lead=[]; counter=[]
    for i in range(8):
        motor.append(alberti_unit(chords[i], q=q, vel=54))
        bass.append(bass_unit(basses[i], q=q, vel=70))
        harmony.append(chord_unit(chords[i], whole_bar=bar, vel=45))
        lead.append(lead_unit(lead_bars[i], rhythm=[q,q,q,q], q=q, vel=88))
        # two half notes
        counter.append(mm1.unit([mm1.ev(counter_bars[i][0], 58, 0, 2*q), mm1.ev(counter_bars[i][1], 58, 2*q, 4*q)]))

    return mm1.make_matrix([motor, bass, harmony, counter, lead]), bar


def main():
    stem = 'musicmatrix_exercise2_classical_motif_v1'
    matrix, bar_ticks = build_exercise2_matrix()
    row_specs = [
        ('Motor Alberti Pattern', instrument.Piano()),
        ('Functional Bass', instrument.Contrabass()),
        ('Harmony Blocks', instrument.StringInstrument()),
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
        'exercise': '2 classical motif development',
        'rows': [r[0] for r in row_specs],
        'columns': matrix.num_cols,
        'form': '8-bar period: antecedent bars 1-4, consequent bars 5-8',
        'tempo_bpm': 100,
        'time_signature': '4/4',
        'motif': 'U U D = G-A-B-A',
        'harmony': 'I | V | vi | IV | ii | V | I | I',
        'transformations': ['sequence', 'inversion/contrary motion', 'cadence'],
        'musicmatrix_semantics': 'rows=voices/pitch-space layers; columns=measures/time-space; cells=MusicUnit bar material'
    }
    (ANALYSIS_DIR / 'exercise2_classical_motif_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
