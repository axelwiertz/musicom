# -*- coding: utf-8 -*-
"""Exercise 1 v3: reduce brightness + add melody answer.

User feedback on v2:
- Dance improved? no
- Brightness too bright
- Hybrid still balanced
- Next: reduce brightness and add melody answer

Design:
- reduce brightness: remove C# #11; use B (Dorian 6) as softer bright color
- add melody answer: bars 5-8 answer bars 1-4 with lower/closing contour
- dance: return closer to v1 jig pulse; no shaker row
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


def build_hybrid_v3_answer():
    eighth = TPQ // 2
    bar = 6 * eighth
    D4,E4,F4,G4,A4,B4,C5,D5,E5 = 62,64,65,67,69,71,72,74,76

    # Softer bright: no C#. Use Dorian B natural and Cmaj9. G13 without #11.
    chords = [
        [50,57,60,64,65],      # Dm9
        [48,55,59,62,64],      # Cmaj9
        [50,57,60,64,65],      # Dm9
        [43,53,57,59,64],      # G13 (no #11)
        [50,57,60,64,65],      # Dm9
        [48,55,59,62,64],      # Cmaj9
        [43,53,57,59,64],      # G13
        [50,57,59,64,69],      # D6/9 close (B = Dorian glow)
    ]
    roots = [38,36,38,43,38,36,43,38]

    # Bars 1-4 question. Bars 5-8 answer: similar rhythm, lower resolution/closing contour.
    lead_bars = [
        [D4,F4,E4,A4,G4,F4],     # Q1: Dorian statement
        [E4,F4,G4,C5,B4,A4],     # Q2: lifts to B/C
        [D4,F4,E4,A4,G4,F4],     # Q3 repeat
        [G4,A4,B4,A4,G4,E4],     # Q4 open answer prep, no C#
        [A4,G4,F4,E4,F4,G4],     # A1 response descends then turns
        [B4,A4,G4,F4,E4,D4],     # A2 Dorian B resolves down
        [G4,A4,B4,C5,B4,A4],     # A3 lift without sharp brightness
        [F4,E4,D4,A4,F4,D4],     # A4 final close
    ]

    rows=[]
    # Moderate dance: v1-like pulse with small pickup, no shaker grid.
    rows.append([mm1.pulse_unit([(36,0,100),(36,3*eighth,82),(38,5*eighth,48)], dur=eighth//2) for _ in range(8)])
    rows.append([mm1.bass_hold_unit(r, bar, 76) for r in roots])
    rows.append([mm1.chord_pulse_unit(c, [0,3*eighth], eighth*2, 64) for c in chords])
    rows.append([mm1.notes_unit(n, eighth, vel=86, dur_ratio=0.95, accent_idxs=(0,3)) for n in lead_bars])
    return mm1.make_matrix(rows), bar


def main():
    stem='musicmatrix_exercise1e_hybrid_v3_answer'
    matrix, bar_ticks = build_hybrid_v3_answer()
    row_specs = [
        ('Balanced Jig Pulse', instrument.Woodblock()),
        ('Modal Bass', instrument.AcousticBass()),
        ('Soft Jazz Color Harmony', instrument.Piano()),
        ('Folk Lead Question Answer', instrument.Violin()),
    ]
    score = mm1.matrix_to_score(stem, matrix, row_specs, bar_ticks, 142.5, '6/8')
    midi_path = MIDI_DIR / f'{stem}.mid'
    mm1.write_midi(score, midi_path)
    wav, ogg = mm1.render(midi_path)

    # One compare: v2 -> v3. Only send this in Telegram.
    v2_wav = RENDERS_DIR / 'musicmatrix_exercise1d_hybrid_v2_bright_dance.wav'
    concat = RENDERS_DIR / 'musicmatrix_exercise1_hybrid_v2_v3_concat.txt'
    concat.write_text(f"file '{v2_wav}'\nfile '{wav}'\n", encoding='utf-8')
    compare_wav = RENDERS_DIR / 'musicmatrix_exercise1_hybrid_v2_v3_compare.wav'
    compare_ogg = AUDIO_DIR / 'musicmatrix_exercise1_hybrid_v2_v3_compare.ogg'
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(compare_wav)], check=True)
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(compare_wav),'-codec:a','libopus','-application','voip','-b:a','64k',str(compare_ogg)], check=True)

    manifest = {
        'stem': stem,
        'midi': str(midi_path),
        'ogg': str(ogg),
        'compare_ogg': str(compare_ogg),
        'rows': [r[0] for r in row_specs],
        'columns': matrix.num_cols,
        'tempo_bpm': 142.5,
        'time_signature': '6/8',
        'transformations': [
            'reduced brightness: removed C# #11; kept softer Dorian B natural and G13 without #11',
            'added melody answer: bars 5-8 answer bars 1-4 with descending/closing contour',
            'reduced dance clutter: removed shaker grid and returned to balanced jig pulse'
        ],
        'musicmatrix_semantics': 'rows=voices/pitch-space layers; columns=measures/time-space; cells=MusicUnit bar material'
    }
    (ANALYSIS_DIR / 'exercise1_v3_answer_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
