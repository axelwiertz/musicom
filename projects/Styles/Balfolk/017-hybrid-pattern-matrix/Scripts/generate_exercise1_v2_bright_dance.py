# -*- coding: utf-8 -*-
"""Exercise 1 v2: brighter + more dance hybrid.

Builds a MusicMatrix/UnitMatrix hybrid variation:
- brighter: C# (#11 over G13) as a brief Lydian bulb, resolving to D
- more dance: stronger 1/4 jig accents, extra 8th-note shaker, bass octave push
"""
from pathlib import Path
import importlib.util, subprocess, json
from music21 import instrument

ROOT = Path('/opt/data/projects/014-genre-pattern-matrix')
BASE_SCRIPT = ROOT / 'Scripts' / 'generate_exercise1_musicmatrix.py'

spec = importlib.util.spec_from_file_location('mm1', BASE_SCRIPT)
mm1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mm1)

TPQ = mm1.TPQ
MIDI_DIR = mm1.MIDI_DIR
AUDIO_DIR = mm1.AUDIO_DIR
RENDERS_DIR = mm1.RENDERS_DIR
ANALYSIS_DIR = mm1.ANALYSIS_DIR


def build_hybrid_v2_bright_dance():
    eighth = TPQ // 2
    bar = 6 * eighth
    D4,E4,F4,G4,A4,B4,C5,Cs5,D5,E5 = 62,64,65,67,69,71,72,73,74,76

    # Harmony: keep hybrid identity, add brightness in G13#11 bars via C#.
    # Dm9, Cmaj9, Dm9, G13#11, Dm9, Cmaj9, G13#11, Dm6/9.
    chords = [
        [50,57,60,64,65],        # Dm9
        [48,55,59,62,64],        # Cmaj9
        [50,57,60,64,65],        # Dm9
        [43,53,57,59,64,73],     # G13#11 (C# bright bulb)
        [50,57,60,64,65],        # Dm9
        [48,55,59,62,64],        # Cmaj9
        [43,53,57,59,64,73],     # G13#11
        [50,57,59,64,69],        # D6/9 color close
    ]
    roots_low = [38,36,38,43,38,36,43,38]
    roots_oct = [50,48,50,55,50,48,55,50]

    # Melody: mostly folk-simple, with C# in bars 4 and 7 resolving upward to D.
    lead_bars = [
        [D4,F4,E4,A4,G4,F4],
        [E4,F4,G4,C5,B4,A4],
        [D4,F4,E4,A4,G4,F4],
        [G4,A4,B4,Cs5,D5,A4],
        [D4,F4,E4,A4,B4,A4],
        [E4,F4,G4,C5,B4,A4],
        [G4,A4,B4,Cs5,D5,E5],
        [D5,Cs5,D5,A4,F4,D4],
    ]

    drum_units=[]; bass_units=[]; harm_units=[]; lead_units=[]; shaker_units=[]
    for i in range(8):
        # More dance: strong 1 and 4, plus light 6 pickup.
        drum_units.append(mm1.pulse_unit([(36,0,118),(36,3*eighth,96),(38,5*eighth,58)], dur=eighth//2))
        # Shaker all six eighths, accent 1 and 4.
        shaker_events=[]
        for k in range(6):
            vel = 64 if k in (0,3) else 42
            shaker_events.append(mm1.ev(42, vel, k*eighth, k*eighth + eighth//3))
        shaker_units.append(mm1.unit(shaker_events))
        # Bass: low hold + octave punches on 1 and 4.
        bass_events = [mm1.ev(roots_low[i], 82, 0, bar)]
        bass_events += [mm1.ev(roots_oct[i], 96, 0, eighth), mm1.ev(roots_oct[i], 84, 3*eighth, 4*eighth)]
        bass_units.append(mm1.unit(bass_events))
        # Harmony: pulses on 1 and 4, plus shorter chucks on 3 and 6.
        harm_events=[]
        for p in chords[i]:
            harm_events.append(mm1.ev(p, 70, 0, 2*eighth))
            harm_events.append(mm1.ev(p, 64, 3*eighth, 5*eighth))
            harm_events.append(mm1.ev(p, 50, 2*eighth, 2*eighth + eighth//2))
            harm_events.append(mm1.ev(p, 48, 5*eighth, 5*eighth + eighth//2))
        harm_units.append(mm1.unit(harm_events))
        lead_units.append(mm1.notes_unit(lead_bars[i], eighth, vel=88, dur_ratio=0.96, accent_idxs=(0,3)))

    rows=[drum_units, shaker_units, bass_units, harm_units, lead_units]
    return mm1.make_matrix(rows), bar


def main():
    stem='musicmatrix_exercise1d_hybrid_v2_bright_dance'
    matrix, bar_ticks = build_hybrid_v2_bright_dance()
    row_specs = [
        ('Dance Pulse / Strong Jig', instrument.Woodblock()),
        ('Shaker Eighth Grid', instrument.Woodblock()),
        ('Bass Octave Push', instrument.AcousticBass()),
        ('Bright Jazz Color Harmony', instrument.Piano()),
        ('Folk Lead with Lydian Bulb', instrument.Violin()),
    ]
    score = mm1.matrix_to_score(stem, matrix, row_specs, bar_ticks, 148, '6/8')
    midi_path = MIDI_DIR / f'{stem}.mid'
    mm1.write_midi(score, midi_path)
    wav, ogg = mm1.render(midi_path)

    # Compare previous hybrid C -> v2 D.
    old_wav = RENDERS_DIR / 'musicmatrix_exercise1c_hybrid_balfolk_jazz.wav'
    concat = RENDERS_DIR / 'musicmatrix_exercise1_hybrid_v1_v2_concat.txt'
    concat.write_text(f"file '{old_wav}'\nfile '{wav}'\n", encoding='utf-8')
    compare_wav = RENDERS_DIR / 'musicmatrix_exercise1_hybrid_v1_v2_compare.wav'
    compare_ogg = AUDIO_DIR / 'musicmatrix_exercise1_hybrid_v1_v2_compare.ogg'
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(compare_wav)], check=True)
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(compare_wav),'-codec:a','libopus','-application','voip','-b:a','64k',str(compare_ogg)], check=True)

    manifest = {
        'stem': stem,
        'midi': str(midi_path),
        'ogg': str(ogg),
        'compare_ogg': str(compare_ogg),
        'rows': [r[0] for r in row_specs],
        'columns': matrix.num_cols,
        'tempo_bpm': 148,
        'time_signature': '6/8',
        'transformations': [
            'more dance: stronger 1/4 accents, shaker eighth grid, bass octave push',
            'brighter: C# as #11 over G13#11 in bars 4 and 7, resolving to D',
            'kept balance: Balfolk rhythm and folk contour preserved; jazz color stays in harmony row'
        ],
        'musicmatrix_semantics': 'rows=voices/pitch-space layers; columns=measures/time-space; cells=MusicUnit bar material'
    }
    (ANALYSIS_DIR / 'exercise1_v2_bright_dance_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
