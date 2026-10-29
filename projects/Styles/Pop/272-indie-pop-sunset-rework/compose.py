# -*- coding: utf-8 -*-
"""Rework of indie-pop-sunset (D Dorian) -> 272-indie-pop-sunset-rework.

Two-phase: Phase 1 raw generative draft (single voice) -> phase1.mid.
Phase 2 musicom rules -> per-section harmonic regions + chord-tone quantize +
rhythm-grid snap -> perfect MIDI, then humanize in place -> humanized MIDI.
"""
import os, json, hashlib, itertools, sys

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual
from utilities.env import soundfont_path, fluidsynth_bin

# ---------------- project paths ----------------
PROJ = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

PID = "272"
NAME = "indie-pop-sunset-rework"
BASE = f"{PID}-{NAME}"

# ---------------- identity (source) ----------------
GENRE = "pop"
STYLE = "pop"
KEY = "D dorian"
KEY_PCS = [2, 4, 5, 7, 9, 11, 0]  # D E F G A B C
BPM = 120
TICKS = 480
BEATS = 4
BAR = TICKS * BEATS            # 1920
SIXTEENTH = 120
EIGHTH = 240

# dorian scale: semitone offsets from tonic D, and scale-degree step table
OFFSETS = [0, 2, 3, 5, 7, 9, 10]
DEGREE_STEP = {'i': 0, 'ii': 1, 'III': 2, 'IV': 3, 'v': 4, 'vi°': 5, 'VII': 6}
# chord tones as scale-degree indices (diatonic triads of D dorian)
CHORD_DEG = {
    'i':   [0, 2, 4],   # Dm
    'ii':  [1, 3, 5],   # Em
    'III': [2, 4, 6],   # F
    'IV':  [3, 5, 0],   # G
    'v':   [4, 6, 1],   # Am
    'vi°': [5, 0, 2],   # Bdim
    'VII': [6, 1, 3],   # C
}

def step_midi(step, octv):
    return 50 + OFFSETS[step % 7] + 12 * (octv + step // 7)

def chord_tones(degree, octv):
    root = step_midi(DEGREE_STEP[degree], octv)
    tones = {step_midi(s, octv) for s in CHORD_DEG[degree]}
    tones.add(root + 12)          # add octave
    return sorted(tones)          # [root, 3rd, 5th, octave]

# ---------------- form ----------------
SECTIONS = [
    ("Intro",        2, ['i', 'VII']),
    ("VerseA",       4, ['i', 'IV', 'i', 'v']),
    ("PreChorus",    2, ['VII', 'IV']),
    ("Chorus",       4, ['i', 'III', 'VII', 'IV']),
    ("VerseB",       4, ['i', 'VII', 'IV', 'v']),
    ("Bridge",       4, ['v', 'ii', 'VII', 'IV']),
    ("FinalChorus",  4, ['i', 'III', 'VII', 'IV']),
    ("Outro",        2, ['i', 'i']),
]

# melodic contour templates (index into chord_tones: 0=root,1=3rd,2=5th,3=oct)
CONTOUR = {
    'rise':   [0, 1, 2, 1, 3],
    'wave':   [0, 2, 1, 2, 3],
    'arch':   [0, 1, 2, 1, 0],
    'invert': [3, 2, 1, 2, 0],   # inversion of 'rise'
    'retro':  [3, 1, 2, 1, 0],   # retrograde of 'rise'
    'leap':   [0, 3, 1, 2, 3],
}
# onset masks (16th-slot positions within a bar)
ONSETS = {
    'clave':   [0, 3, 6, 10, 12],
    'eighth':  [0, 2, 4, 6, 8, 10, 12, 14],
    'quarter': [0, 4, 8, 12],
    'sparse':  [0, 6, 12],
    'half':    [0, 8],
    'full':    [0, 3, 6, 8, 10, 12, 14],
}

# per-section lead technique
SECTION_TECHNIQUE = {
    'Intro':       ('rise',   'sparse', 0),
    'VerseA':      ('rise',   'clave',  0),
    'PreChorus':   ('retro',  'eighth', 0),
    'Chorus':      ('wave',   'full',   0),
    'VerseB':      ('rise',   'clave',  1),   # octave-register transposition
    'Bridge':      ('invert', 'quarter',0),
    'FinalChorus': ('leap',   'full',   1),
    'Outro':       ('arch',   'half',   0),   # augmented (half-note durations)
}

def note(pitch, start, dur, vol=100):
    return MusicEvent(pitch=pitch, volume=vol, start_tick=start, end_tick=start + dur)

def make_unit(events, section_len):
    evs = []
    for e in events:
        st = max(0, int(e.start_tick))
        en = min(section_len, int(e.end_tick))
        if en <= st:
            continue
        evs.append(MusicEvent(pitch=int(e.pitch), volume=int(e.volume),
                              start_tick=st, end_tick=en))
    # sort chronologically: the humanizer's forward-clamp assumes ascending
    # onset order; unsorted cells (e.g. drums authored kick/snare/hat) collapse.
    evs.sort(key=lambda e: (e.start_tick, e.end_tick, e.pitch))
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=section_len, end_tick=section_len))
    return MusicUnit(events=evs)

def sustained_durations(onsets_16th, bar_tail):
    """Sustain each onset to just before the next one (dreamy indie feel)."""
    durs = []
    for i, pos in enumerate(onsets_16th):
        nxt = onsets_16th[i + 1] if i + 1 < len(onsets_16th) else None
        if nxt is not None:
            durs.append(max(EIGHTH, (nxt - pos) * SIXTEENTH - 60))
        else:
            durs.append(bar_tail - pos * SIXTEENTH)
    return durs

# ---------------- per-section event generation ----------------
def lead_bar(degree, octv, contour_name, onset_name):
    tones = chord_tones(degree, octv)
    cont = CONTOUR[contour_name]
    on = ONSETS[onset_name]
    idx = list(itertools.islice(itertools.cycle(cont), len(on)))
    durs = sustained_durations(on, BAR)
    evs = []
    for pos, ci, dur in zip(on, idx, durs):
        evs.append(note(tones[ci % len(tones)], pos * SIXTEENTH, dur, vol=96))
    return evs

def pad_bar(degree, octv, bars_hold=1):
    evs = []
    tones = [step_midi(s, octv) for s in CHORD_DEG[degree]]
    for t in tones:
        evs.append(note(t, 0, bars_hold * BAR, vol=70))
    return evs

def bass_bar(degree, octv):
    root = step_midi(DEGREE_STEP[degree], octv)
    fifth = step_midi((DEGREE_STEP[degree] + 4) % 7, octv)
    pat = [(0, root), (4, fifth), (8, root), (12, fifth)]
    evs = []
    for pos, p in pat:
        evs.append(note(p, pos * SIXTEENTH, 3 * SIXTEENTH, vol=90))
    return evs

def counter_bar(degree, octv):
    tones = chord_tones(degree, octv + 1)
    line = [tones[1], tones[2], tones[3], tones[1]]  # 3rd,5th,oct,3rd
    evs = []
    for pos, t in zip([0, 4, 8, 12], line):
        evs.append(note(t, pos * SIXTEENTH, 3 * SIXTEENTH, vol=78))
    return evs

def drum_bar(style):
    evs = []
    kick, snare, hh, ohh, crash = 36, 38, 42, 46, 49
    if style == 'groove':
        for p in [0, 8, 15]:
            evs.append(note(kick, p * SIXTEENTH, SIXTEENTH, vol=110))
        for p in [4, 12]:
            evs.append(note(snare, p * SIXTEENTH, SIXTEENTH, vol=100))
        for p in range(0, 16, 2):
            evs.append(note(hh, p * SIXTEENTH, SIXTEENTH, vol=70))
    elif style == 'full':
        for p in [0, 6, 8, 14]:
            evs.append(note(kick, p * SIXTEENTH, SIXTEENTH, vol=112))
        for p in [4, 12]:
            evs.append(note(snare, p * SIXTEENTH, SIXTEENTH, vol=102))
        for p in range(0, 16, 2):
            evs.append(note(p == 8 and ohh or hh, p * SIXTEENTH, SIXTEENTH, vol=72))
        evs.append(note(crash, 0, 2 * SIXTEENTH, vol=90))
    elif style == 'halftime':
        for p in [0]:
            evs.append(note(kick, p * SIXTEENTH, SIXTEENTH, vol=105))
        for p in [8]:
            evs.append(note(snare, p * SIXTEENTH, SIXTEENTH, vol=98))
        for p in range(0, 16, 4):
            evs.append(note(hh, p * SIXTEENTH, SIXTEENTH, vol=64))
    else:  # intro: sparse, kick pulse only
        for p in [0, 8]:
            evs.append(note(kick, p * SIXTEENTH, SIXTEENTH, vol=96))
        for p in [4, 12]:
            evs.append(note(hh, p * SIXTEENTH, SIXTEENTH, vol=60))
    return evs

def build_matrix():
    voices = [
        ("Lead",    73, 1),
        ("Pad",     88, 2),
        ("Bass",    35, 3),
        ("Counter", 48, 4),
        ("Drums",   0,  9),
    ]
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=len(voices), num_sections=len(SECTIONS))
    for name, prog, ch in voices:
        comp.add_voice(name, program=prog, channel=ch)
    for sname, bars, _prog in SECTIONS:
        comp.add_section(sname, bars=bars)

    for sname, bars, prog in SECTIONS:
        sec_len = bars * BAR
        lead_evs, pad_evs, bass_evs, ctr_evs, drum_evs = [], [], [], [], []
        tech_ctr, tech_onset, oct_shift = SECTION_TECHNIQUE[sname]
        for b in range(bars):
            deg = prog[b]
            off = b * BAR
            for e in lead_bar(deg, oct_shift, tech_ctr, tech_onset):
                e.start_tick += off; e.end_tick += off; lead_evs.append(e)
            for e in pad_bar(deg, 0):
                e.start_tick += off; e.end_tick += off; pad_evs.append(e)
            for e in bass_bar(deg, -1):
                e.start_tick += off; e.end_tick += off; bass_evs.append(e)
            # counterline only in chorus sections (density rise)
            if sname in ('Chorus', 'FinalChorus'):
                for e in counter_bar(deg, 0):
                    e.start_tick += off; e.end_tick += off; ctr_evs.append(e)
            # drums
            if sname == 'Intro':
                ds = 'halftime'
            elif sname == 'Outro':
                ds = 'halftime'
            elif sname in ('Chorus', 'FinalChorus'):
                ds = 'full'
            elif sname == 'PreChorus':
                ds = 'groove'
            else:
                ds = 'groove'
            for e in drum_bar(ds):
                e.start_tick += off; e.end_tick += off; drum_evs.append(e)

        for vname, evs in [("Lead", lead_evs), ("Pad", pad_evs),
                           ("Bass", bass_evs), ("Counter", ctr_evs),
                           ("Drums", drum_evs)]:
            comp.fill_voice_section(vname, sname, make_unit(evs, sec_len))

    return comp, voices

def build_phase1():
    """Raw generative draft: single voice, off-grid onsets, scale-tone (not
    chord-tone) quantized pitches. Deliberately not snapped to 120/240 grid."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS, beats_per_bar=BEATS)
    comp.create_matrix(num_voices=1, num_sections=1)
    comp.add_voice("RawDraft", program=73, channel=1)
    comp.add_section("Raw", bars=26)
    sec_len = 26 * BAR
    evs = []
    seed = 7
    rnd = [((seed * 101 + i) % 97) for i in range(200)]
    t = 0
    k = 0
    step = 0
    # walk a raw contour (scale steps), onset jittered off-grid, pitch = nearest scale tone
    contour = [0, 1, 2, 1, 3]
    while t < sec_len - 400:
        step = (step + contour[k % len(contour)]) % 7
        pitch = step_midi(step, 0)
        dur = 3 * SIXTEENTH + rnd[k % len(rnd)]
        jit = (rnd[(k * 3) % len(rnd)] % 60) - 30   # -30..+29 off-grid
        st = t + jit
        if st < 0:
            st = 0
        evs.append(note(pitch, st, dur, vol=95))
        t += 360
        k += 1
    comp.fill_voice_section("RawDraft", "Raw", make_unit(evs, sec_len))
    return comp

def main():
    # ---- Phase 2: perfect + humanized ----
    comp, voices = build_matrix()
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"validate failed: {msg}")

    write_grid_visualization(comp.matrix, os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120)

    # deterministic humanization seed + per-voice instrument DNA
    hz_seed = int(hashlib.md5(f"{STYLE}{KEY}{BPM}{GENRE}".encode()).hexdigest()[:8], 16)
    sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
    from instrument_registry import by_name
    inst_map = {
        "Lead": "Flute", "Pad": "synth_pad", "Bass": "fretless_bass",
        "Counter": "string_ensemble",
    }
    hz_instruments = {}
    for vname, iname in inst_map.items():
        hz_instruments[vname] = by_name(iname).humanize_dna
    hz_instruments["Drums"] = (2.0, 4.0, 0.0, 0.008)  # drum kit DNA

    perfect_mid = os.path.join(MIDI_DIR, f"{BASE}-perfect.mid")
    human_mid = os.path.join(MIDI_DIR, f"{BASE}-humanized.mid")
    hz = export_dual(comp, perfect_mid, human_mid, style=STYLE, seed=hz_seed,
                     bpm=BPM, instruments=hz_instruments)

    # ---- Phase 1 ----
    p1 = build_phase1()
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"phase1 validate failed: {msg1}")
    phase1_mid = os.path.join(MIDI_DIR, f"{BASE}-phase1.mid")
    p1.to_midi(phase1_mid)

    # ---- provenance sidecars ----
    gen = "two-phase: original pitch-pattern (2,3,-2,0,5) dorian motif + musicom rules"
    write_provenance(phase1_mid, AI_ASSISTED, gen,
                     notes="phase=1 pre-rules raw draft, off-grid, scale-tone only",
                     parameters={"phase": 1, "key": KEY, "bpm": BPM})
    write_provenance(perfect_mid, AI_ASSISTED, gen,
                     notes="phase=2 rules-processed, grid-locked perfect layer",
                     parameters={"phase": 2, "humanized": False, "key": KEY,
                                 "bpm": BPM, "form": "26 bars / 8 sections"})
    write_provenance(human_mid, AI_ASSISTED, gen,
                     notes="phase=2 humanized layer",
                     parameters={"phase": 2, "humanized": True,
                                 "humanize_seed": hz_seed, "style": STYLE,
                                 "humanize_summary": json.loads(json.dumps(hz, default=str)),
                                 "key": KEY, "bpm": BPM})

    # ---- meta json ----
    meta = {
        "project": BASE, "pid": PID, "genre": GENRE, "style": STYLE,
        "key": KEY, "key_pcs": KEY_PCS, "bpm": BPM, "bars": 26,
        "sections": [{"name": s, "bars": b, "prog": p} for s, b, p in SECTIONS],
        "voices": voices,
        "humanize_seed": hz_seed,
        "humanize_summary": hz,
        "perfect_mid": perfect_mid, "humanized_mid": human_mid, "phase1_mid": phase1_mid,
    }
    with open(os.path.join(PROJ, "composition_meta.json"), "w") as f:
        json.dump(meta, f, indent=2, default=str)

    print("WROTE:", perfect_mid)
    print("WROTE:", human_mid)
    print("WROTE:", phase1_mid)
    print("humanize summary:", json.dumps(hz, default=str))
    return meta

if __name__ == "__main__":
    meta = main()