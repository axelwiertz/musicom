# -*- coding: utf-8 -*-
"""Project 014 Exercise 1 using Musicom UnitMatrix semantics + music21 export.

MusicMatrix/UnitMatrix meaning:
- rows = voices / pitch-space layers
- columns = measures / time-space segments
- cells = MusicUnit bar material

This script loads UnitMatrix/MusicUnit/MusicEvent from axelwiertz/musicom by file,
avoiding optional package-wide dependencies, then exports music21 MIDI.
"""
from pathlib import Path
import sys, types, importlib.util, subprocess, json
from collections import defaultdict

from music21 import stream, note, chord, instrument, tempo, meter, metadata, midi, volume

ROOT = Path('/opt/data/projects/014-genre-pattern-matrix')
MUSICOM = Path('/opt/data/repos/musicom')
MIDI_DIR = ROOT / 'MIDI'
AUDIO_DIR = ROOT / 'Audio'
RENDERS_DIR = ROOT / 'Renders'
ANALYSIS_DIR = ROOT / 'Analysis'
for d in [MIDI_DIR, AUDIO_DIR, RENDERS_DIR, ANALYSIS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

TPQ = 480
SF2 = '/usr/share/sounds/sf2/FluidR3_GM.sf2'


def load_musicom_matrix_classes():
    """Load only MusicEvent, MusicUnit, UnitMatrix from repo files.

    The repo package __init__ imports optional theory deps (networkx). We only need
    unit.py + matrix.py, so create a small synthetic package namespace.
    """
    # Stub visualization.Cycle for timegrid.py import.
    vis = types.ModuleType('visualization')
    class Cycle:
        def __init__(self, *args, **kwargs): pass
        def show(self, *args, **kwargs): pass
    vis.Cycle = Cycle
    sys.modules.setdefault('visualization', vis)

    pkg = types.ModuleType('structures')
    pkg.__path__ = [str(MUSICOM / 'structures')]
    sys.modules['structures'] = pkg

    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        return mod

    load('structures.timegrid', MUSICOM / 'structures' / 'timegrid.py')
    unit_mod = load('structures.unit', MUSICOM / 'structures' / 'unit.py')
    matrix_mod = load('structures.matrix', MUSICOM / 'structures' / 'matrix.py')
    return unit_mod.MusicEvent, unit_mod.MusicUnit, matrix_mod.UnitMatrix

MusicEvent, MusicUnit, UnitMatrix = load_musicom_matrix_classes()


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


def chord_pulse_unit(chord_notes, pulses, pulse_dur, vel=70):
    events = []
    for start in pulses:
        for p in chord_notes:
            events.append(ev(p, vel, start, start + pulse_dur))
    return unit(events)


def bass_hold_unit(pitch, bar_ticks, vel=75):
    return unit([ev(pitch, vel, 0, bar_ticks)])


def pulse_unit(pitches_starts, dur=120, vel=80):
    return unit([ev(p, v if len(t)==3 else vel, s, s+dur) for t in pitches_starts for p,s,*v0 in [t] for v in [v0[0] if v0 else vel]])


def musicunit_to_part(matrix, row, row_name, inst, bar_ticks, ql_per_tick):
    part = stream.Part(id=row_name.replace(' ', '_'))
    part.partName = row_name
    part.append(inst)
    for col in range(matrix.num_cols):
        u = matrix.get_unit((row, col))
        if u is None:
            continue
        groups = defaultdict(list)
        for e in u.events:
            groups[(e.start_tick, e.end_tick)].append(e)
        for (start, end), events in sorted(groups.items()):
            offset = (col * bar_ticks + start) * ql_per_tick
            dur = max(1, end - start) * ql_per_tick
            pitches = [int(e.pitch) for e in events]
            vel = int(sum(int(e.volume) for e in events) / len(events))
            if len(pitches) == 1:
                obj = note.Note(pitches[0], quarterLength=dur)
            else:
                obj = chord.Chord(pitches, quarterLength=dur)
            obj.volume = volume.Volume(velocity=vel)
            part.insert(offset, obj)
    return part


def matrix_to_score(title, matrix, row_specs, bar_ticks, tempo_bpm, time_sig):
    ql_per_tick = 1.0 / TPQ
    score = stream.Score(id=title.replace(' ', '_'))
    score.metadata = metadata.Metadata(title=title, composer='Musicom Agent')
    meta = stream.Part(id='meta')
    meta.append(tempo.MetronomeMark(number=tempo_bpm))
    meta.append(meter.TimeSignature(time_sig))
    score.insert(0, meta)
    for row, (row_name, inst) in enumerate(row_specs):
        score.insert(0, musicunit_to_part(matrix, row, row_name, inst, bar_ticks, ql_per_tick))
    return score


def write_midi(score, path):
    mf = midi.translate.streamToMidiFile(score)
    data = mf.writestr()
    Path(path).write_bytes(data)


def render(mid_path):
    mid_path = Path(mid_path)
    wav = RENDERS_DIR / (mid_path.stem + '.wav')
    ogg = AUDIO_DIR / (mid_path.stem + '.ogg')
    subprocess.run(['fluidsynth', '-ni', SF2, str(mid_path), '-F', str(wav), '-r', '44100'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(wav), '-af', 'volume=0.9', '-codec:a', 'libopus', '-application', 'voip', '-b:a', '64k', str(ogg)], check=True)
    return wav, ogg


def build_balfolk_matrix():
    eighth = TPQ // 2
    bar = 6 * eighth
    D4,E4,F4,G4,A4,B4,C5,D5 = 62,64,65,67,69,71,72,74
    chords = [[50,57,62,65], [48,55,60,64], [50,57,62,65], [43,50,55,59], [50,57,62,65], [48,55,60,64], [43,50,55,59], [50,57,62,65]]
    roots = [38,36,38,43,38,36,43,38]
    bars_notes = [[D4,E4,F4,A4,G4,F4], [E4,F4,G4,C5,B4,A4], [D4,F4,E4,A4,G4,F4], [G4,A4,B4,A4,G4,E4], [D4,E4,F4,A4,G4,F4], [E4,F4,G4,C5,B4,A4], [G4,A4,B4,D5,C5,A4], [F4,E4,D4,A4,F4,D4]]
    rows = []
    rows.append([pulse_unit([(36,0,92),(36,3*eighth,74)], dur=eighth//2) for _ in range(8)])
    rows.append([bass_hold_unit(r, bar, 72) for r in roots])
    rows.append([chord_pulse_unit(c, [0,3*eighth], eighth*2, 68) for c in chords])
    rows.append([notes_unit(n, eighth, 84, 0.92, accent_idxs=(0,3)) for n in bars_notes])
    return make_matrix(rows), bar


def build_jazz_matrix():
    q = TPQ
    bar = 4*q
    chords = [[50,57,60,65], [43,53,59,65], [48,55,59,64], [48,55,59,64], [52,59,62,67], [45,55,61,67], None, [48,55,59,64]]
    roots = [[50,53,57,60],[43,47,50,53],[48,52,55,59],[48,52,55,59],[52,55,59,62],[45,49,52,55],[50,53,57,59],[48,52,55,60]]
    long = int(q*2/3); short = q-long
    melodies = [[62,65,69,72,71,69], [65,67,71,74,72,71], [64,67,71,76,74,72], [67,64,62,60], [64,67,71,74,72,71], [61,64,67,73,72,69], [65,69,72,71,67,65], [64,62,60,55]]
    drum_units=[]; bass_units=[]; harm_units=[]; lead_units=[]
    for i in range(8):
        drum_events=[]
        for k in range(4): drum_events.append(ev(51,55,k*q,k*q+q//4))
        drum_events += [ev(38,70,q,q+q//4), ev(38,70,3*q,3*q+q//4)]
        drum_units.append(unit(drum_events))
        bass_units.append(unit([ev(n,78,k*q,k*q+int(q*0.9)) for k,n in enumerate(roots[i])]))
        if i == 6:
            harm_units.append(chord_pulse_unit([50,57,60,65],[q],q,64) + chord_pulse_unit([43,53,59,65],[3*q],q,64))
        else:
            harm_units.append(chord_pulse_unit(chords[i],[q,3*q],q,62))
        t=0; evs=[]
        for j,n in enumerate(melodies[i]):
            dur = long if j%2==0 else short
            evs.append(ev(n,92 if j in (0,2,4) else 78,t,t+int(dur*0.95)))
            t += dur
            if t >= bar: break
        lead_units.append(unit(evs))
    return make_matrix([drum_units,bass_units,harm_units,lead_units]), bar


def build_hybrid_matrix():
    eighth = TPQ // 2
    bar = 6 * eighth
    D4,E4,F4,G4,A4,B4,C5,D5 = 62,64,65,67,69,71,72,74
    chords = [[50,57,60,64,65], [48,55,59,64], [50,57,60,64,65], [43,53,57,59,64], [50,57,60,64,65], [48,55,59,64], [43,53,57,59,64], [50,57,60,64,65]]
    roots = [38,36,38,43,38,36,43,38]
    vars = [[D4,F4,E4,A4,G4,F4], [E4,F4,G4,C5,B4,A4], [D4,F4,E4,A4,G4,F4], [G4,A4,B4,A4,G4,E4], [D4,F4,E4,A4,G4,F4], [E4,F4,G4,C5,B4,A4], [G4,A4,B4,D5,C5,A4], [F4,E4,D4,A4,F4,D4]]
    rows = []
    rows.append([pulse_unit([(36,0,88),(36,3*eighth,72)], dur=eighth//2) for _ in range(8)])
    rows.append([bass_hold_unit(r, bar, 74) for r in roots])
    rows.append([chord_pulse_unit(c, [0,3*eighth], eighth*2, 62) for c in chords])
    rows.append([notes_unit(n, eighth, 84, 0.94, accent_idxs=(0,3)) for n in vars])
    return make_matrix(rows), bar


def main():
    specs = [
        ('musicmatrix_exercise1a_balfolk_dorian_jig', build_balfolk_matrix, 142.5, '6/8', [('Foot Pulse / Drums', instrument.Woodblock()), ('Bass Voice', instrument.AcousticBass()), ('Harmony Voice', instrument.Accordion()), ('Lead Voice', instrument.Violin())]),
        ('musicmatrix_exercise1b_jazz_ii_v_i_swing', build_jazz_matrix, 120, '4/4', [('Ride + Backbeat', instrument.Woodblock()), ('Walking Bass', instrument.AcousticBass()), ('Piano Harmony', instrument.Piano()), ('Sax Lead', instrument.AltoSaxophone())]),
        ('musicmatrix_exercise1c_hybrid_balfolk_jazz', build_hybrid_matrix, 142.5, '6/8', [('Jig Pulse / Drums', instrument.Woodblock()), ('Modal Bass', instrument.AcousticBass()), ('Jazz Color Harmony', instrument.Piano()), ('Folk Lead', instrument.Violin())]),
    ]
    outputs=[]
    manifest=[]
    for stem, builder, bpm, ts, row_specs in specs:
        matrix, bar_ticks = builder()
        score = matrix_to_score(stem, matrix, row_specs, bar_ticks, bpm, ts)
        midi_path = MIDI_DIR / f'{stem}.mid'
        write_midi(score, midi_path)
        wav, ogg = render(midi_path)
        outputs.append((midi_path, ogg))
        manifest.append({
            'stem': stem,
            'midi': str(midi_path),
            'ogg': str(ogg),
            'rows': [r[0] for r in row_specs],
            'columns': matrix.num_cols,
            'bar_ticks': bar_ticks,
            'tempo_bpm': bpm,
            'time_signature': ts,
            'matrix_semantics': 'rows=voices/pitch-space layers; columns=measures/time-space; cells=MusicUnit bar material',
        })
    # concat compare audio from WAV outputs generated above
    concat = RENDERS_DIR / 'musicmatrix_concat.txt'
    with open(concat, 'w') as f:
        for midi_path, ogg in outputs:
            wav = RENDERS_DIR / (Path(midi_path).stem + '.wav')
            f.write(f"file '{wav}'\n")
    allwav = RENDERS_DIR / 'musicmatrix_exercise1_all_three_compare.wav'
    allogg = AUDIO_DIR / 'musicmatrix_exercise1_all_three_compare.ogg'
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(allwav)], check=True)
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(allwav),'-codec:a','libopus','-application','voip','-b:a','64k',str(allogg)], check=True)
    manifest.append({'stem':'musicmatrix_exercise1_all_three_compare','ogg':str(allogg), 'type':'comparison_render'})
    (ANALYSIS_DIR / 'musicmatrix_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
