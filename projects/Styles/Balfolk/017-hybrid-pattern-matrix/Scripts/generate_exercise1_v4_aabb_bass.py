# -*- coding: utf-8 -*-
"""Exercise 1 v4: AABB form + bass variation.

Based on accepted v3:
- brightness ok: no C# #11, keep Dorian B
- melody answer ok
- dance clarity ok

v4:
- expand to 16 bars: A A B B
- add bass variation: root/fifth/octave movement and approach notes
- one final listening file only
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


def bass_pattern(root_low, root_mid, fifth_mid, next_root=None, bar_ticks=1440, eighth=240, variant='root'):
    """One-bar bass MusicUnit for 6/8.

    Clear dance gravity: count 1 + 4. Variation uses fifth/octave/pickup.
    """
    events = []
    if variant == 'root':
        events += [mm1.ev(root_low, 78, 0, 3*eighth), mm1.ev(root_mid, 72, 3*eighth, 6*eighth)]
    elif variant == 'fifth':
        events += [mm1.ev(root_low, 82, 0, 2*eighth), mm1.ev(fifth_mid, 70, 2*eighth, 3*eighth), mm1.ev(root_mid, 80, 3*eighth, 5*eighth), mm1.ev(fifth_mid, 58, 5*eighth, 6*eighth)]
    elif variant == 'walk':
        approach = next_root if next_root is not None else root_mid
        events += [mm1.ev(root_low, 82, 0, 2*eighth), mm1.ev(fifth_mid, 68, 2*eighth, 3*eighth), mm1.ev(root_mid, 82, 3*eighth, 5*eighth), mm1.ev(approach, 62, 5*eighth, 6*eighth)]
    elif variant == 'cadence':
        events += [mm1.ev(root_low, 86, 0, 2*eighth), mm1.ev(fifth_mid, 70, 2*eighth, 3*eighth), mm1.ev(root_mid, 84, 3*eighth, 4*eighth), mm1.ev(fifth_mid, 64, 4*eighth, 5*eighth), mm1.ev(root_low, 88, 5*eighth, 6*eighth)]
    return mm1.unit(events)


def build_v4_aabb():
    eighth = TPQ // 2
    bar = 6 * eighth
    D4,E4,F4,G4,A4,B4,C5,D5,E5 = 62,64,65,67,69,71,72,74,76

    # 4-bar A, repeat A with small lead lift, 4-bar B answer, repeat B with cadence.
    harmony_4_A = [
        [50,57,60,64,65],      # Dm9
        [48,55,59,62,64],      # Cmaj9
        [50,57,60,64,65],      # Dm9
        [43,53,57,59,64],      # G13
    ]
    harmony_4_B = [
        [50,57,60,64,65],      # Dm9
        [48,55,59,62,64],      # Cmaj9
        [43,53,57,59,64],      # G13
        [50,57,59,64,69],      # D6/9 close
    ]
    chords = harmony_4_A + harmony_4_A + harmony_4_B + harmony_4_B

    # roots: low, mid, fifth, optional approach to next root mid
    roots = [
        (38,50,45,48), (36,48,43,50), (38,50,45,43), (43,55,50,50),
        (38,50,45,48), (36,48,43,50), (38,50,45,43), (43,55,50,50),
        (38,50,45,48), (36,48,43,43), (43,55,50,50), (38,50,45,50),
        (38,50,45,48), (36,48,43,43), (43,55,50,50), (38,50,45,None),
    ]
    variants = ['root','fifth','walk','walk', 'root','fifth','walk','cadence', 'fifth','walk','walk','cadence', 'fifth','walk','walk','cadence']

    # Melody A/A/B/B. A' and B' have mild variation; no C#.
    A = [
        [D4,F4,E4,A4,G4,F4],
        [E4,F4,G4,C5,B4,A4],
        [D4,F4,E4,A4,G4,F4],
        [G4,A4,B4,A4,G4,E4],
    ]
    Ap = [
        [D4,F4,E4,A4,B4,A4],
        [E4,F4,G4,C5,B4,A4],
        [D4,E4,F4,A4,G4,F4],
        [G4,A4,B4,C5,B4,A4],
    ]
    B = [
        [A4,G4,F4,E4,F4,G4],
        [B4,A4,G4,F4,E4,D4],
        [G4,A4,B4,C5,B4,A4],
        [F4,E4,D4,A4,F4,D4],
    ]
    Bp = [
        [A4,G4,F4,E4,D4,F4],
        [B4,A4,G4,F4,E4,D4],
        [G4,A4,B4,D5,C5,A4],
        [F4,E4,D4,A4,F4,D4],
    ]
    lead_bars = A + Ap + B + Bp

    pulse_units=[]; bass_units=[]; harmony_units=[]; lead_units=[]
    for i in range(16):
        # Clear jig. Extra pickup on bars 4/8/12/16 only.
        pickup = [(38,5*eighth,52)] if i in (3,7,11,15) else []
        pulse_units.append(mm1.pulse_unit([(36,0,102),(36,3*eighth,84)] + pickup, dur=eighth//2))
        rl, rm, fm, approach = roots[i]
        bass_units.append(bass_pattern(rl, rm, fm, approach, bar, eighth, variants[i]))
        harmony_units.append(mm1.chord_pulse_unit(chords[i], [0,3*eighth], eighth*2, 63))
        # Strong first phrase note, slightly more phrase lift at B sections.
        vel = 86 if i < 8 else 88
        lead_units.append(mm1.notes_unit(lead_bars[i], eighth, vel=vel, dur_ratio=0.95, accent_idxs=(0,3)))

    return mm1.make_matrix([pulse_units, bass_units, harmony_units, lead_units]), bar


def main():
    stem = 'musicmatrix_exercise1f_hybrid_v4_aabb_bass'
    matrix, bar_ticks = build_v4_aabb()
    row_specs = [
        ('AABB Jig Pulse', instrument.Woodblock()),
        ('Bass Variation', instrument.AcousticBass()),
        ('Soft Jazz Color Harmony', instrument.Piano()),
        ('Folk Lead AABB', instrument.Violin()),
    ]
    score = mm1.matrix_to_score(stem, matrix, row_specs, bar_ticks, 142.5, '6/8')
    midi_path = MIDI_DIR / f'{stem}.mid'
    mm1.write_midi(score, midi_path)
    wav, ogg = mm1.render(midi_path)
    manifest = {
        'stem': stem,
        'midi': str(midi_path),
        'ogg': str(ogg),
        'rows': [r[0] for r in row_specs],
        'columns': matrix.num_cols,
        'form': 'A A B B, 16 bars of 6/8',
        'tempo_bpm': 142.5,
        'time_signature': '6/8',
        'transformations': [
            'expanded accepted v3 into AABB form',
            'added bass variation: root/fifth/octave/approach patterns while preserving jig gravity',
            'kept reduced brightness: no C# #11, Dorian B only'
        ],
        'musicmatrix_semantics': 'rows=voices/pitch-space layers; columns=measures/time-space; cells=MusicUnit bar material'
    }
    (ANALYSIS_DIR / 'exercise1_v4_aabb_bass_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
