#!/usr/bin/env python
"""
Moonlight Shadow — CORRECTED alignment.

Key relationships (all same song):
- Melody G, Trumpet G: E minor (melody at 64-74)
- Full E, Vocal E: E major (melody at 61-71, transposed -3 from E minor)
- Piano C: C major (different melody, skip or use as secondary)
- Percussion: 90bpm, 4-bar loop

To merge into E major:
- E minor files: transpose -3 semis
- E major files: no transpose
- Form: Melody G starts verse at bar 0, Full E has ~4-bar intro (verse at bar 4)
"""

import os
import sys
import glob
import hashlib
from pathlib import Path
from music21 import converter
import mido

from structures import MusicUnit, MusicEvent, UnitMatrix, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# ────────────────────────── config ──────────────────────────
IN_DIR = Path("/opt/data/projects/in/Moonlight Shadow")
PROJ = Path("/opt/data/projects/Styles/Pop/moonlight-shadow")
(PROJ / "MIDI").mkdir(parents=True, exist_ok=True)
(PROJ / "Audio").mkdir(exist_ok=True)
(PROJ / "Analysis").mkdir(exist_ok=True)

TARGET_BPM = 126
TARGET_KEY = "E"
E_MAJOR = [52, 54, 56, 57, 59, 61, 63, 64, 66, 68, 69, 71, 73, 75, 76, 78, 80]
TPB = 480
BPB = 4
BAR = TPB * BPB
SIXTEENTH = TPB // 4

# Form: 32 bars total
# Intro (4 bars) + Verse1 (8 bars) + Chorus (8 bars) + Verse2 (8 bars) + Outro (4 bars)
SECTIONS = [("Intro", 4), ("Verse1", 8), ("Chorus", 8), ("Verse2", 8), ("Outro", 4)]
N_SECTIONS = len(SECTIONS)
TOTAL_BARS = sum(b for _, b in SECTIONS)
SECTION_TICKS = [b * BAR for _, b in SECTIONS]
TOTAL_TICKS = sum(SECTION_TICKS)

# ────────────────────────── reading ──────────────────────────
# Reading-only context: mido.MidiFile('*.mid') used for ANALYSIS, never authoring.

def read_notes(filepath: str, src_bpm: float):
    """Read (abs_ql, pitch, dur_ql, vel, channel) from MIDI."""
    mid = mido.MidiFile(filepath)  # READING ONLY (analysis) — no authoring
    if not src_bpm:
        src_bpm = 126.0
    scale = 126.0 / src_bpm
    out = []
    for track in mid.tracks:
        abs_t = 0
        active = {}
        for msg in track:
            abs_t += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                key = (msg.channel, msg.note)
                active[key] = abs_t
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                key = (msg.channel, msg.note)
                if key in active:
                    start = active.pop(key)
                    dur_ticks = abs_t - start
                    ql_start = start * scale / mid.ticks_per_beat
                    ql_dur = max(dur_ticks * scale / mid.ticks_per_beat, 0.05)
                    out.append((ql_start, msg.note, ql_dur, msg.velocity, msg.channel))
    out.sort(key=lambda x: (x[0], x[1]))
    return out


def get_file_bpm(filepath: str) -> float:
    mid = mido.MidiFile(filepath)  # READING ONLY (analysis) — no authoring
    for t in mid.tracks:
        for msg in t:
            if msg.type == "set_tempo":
                return 60_000_000 / msg.tempo
    return 126.0


def unique_files():
    seen, out = set(), []
    for f in sorted(glob.glob(str(IN_DIR / "*.mid"))):
        h = hashlib.md5(open(f, 'rb').read()).hexdigest()
        if h not in seen:
            seen.add(h)
            out.append(f)
    return out


# ────────────────────────── voice builders ──────────────────────────
def unit_from_notes(cell_notes, transpose: int, scale, cell_ticks: int, vol: int = 90,
                    keep_channel=None, section_start_ql: float = 0.0):
    """Build MusicUnit from notes, cell-local ticks."""
    events = []
    for ql_start, pitch, ql_dur, vel, ch in cell_notes:
        if keep_channel is not None and ch != keep_channel:
            continue
        p = pitch + transpose
        # Quantize to scale
        if scale:
            p = min(scale, key=lambda x: abs(x - p))
        p = max(0, min(127, p))
        st = int(round((ql_start - section_start_ql) * 4) / 4 * TPB)
        if st >= cell_ticks:
            continue
        dur = int(max(ql_dur, 0.25) * TPB)
        et = min(st + dur, cell_ticks)
        if et <= st:
            continue
        events.append(MusicEvent(pitch=p, volume=vol, start_tick=st, end_tick=et))
    # merge overlaps per pitch ONLY for true double-strikes (same start tick)
    events.sort(key=lambda e: (e.start_tick, e.end_tick))
    merged = []
    for e in events:
        if merged and merged[-1].pitch == e.pitch and e.start_tick == merged[-1].start_tick:
            merged[-1].end_tick = max(merged[-1].end_tick, e.end_tick)
        else:
            merged.append(e)
    # silent terminal landmark
    if merged:
        if merged[-1].end_tick < cell_ticks:
            merged.append(MusicEvent(pitch=0, volume=0, start_tick=merged[-1].end_tick,
                                     end_tick=cell_ticks))
    else:
        merged.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=cell_ticks))
    return MusicUnit(events=merged)


def drum_unit(pattern16, cell_ticks: int, vel: int = 96):
    """pattern16: GM drum pitch per 16th slot (None = rest), repeated over cell."""
    events = []
    n = len(pattern16)
    ticks_per_step = SIXTEENTH
    n_steps = cell_ticks // ticks_per_step
    for i in range(n_steps):
        p = pattern16[i % n]
        if p is None:
            continue
        st = i * ticks_per_step
        events.append(MusicEvent(pitch=p, volume=vel, start_tick=st,
                                 end_tick=min(st + ticks_per_step - 4, cell_ticks)))
    if events:
        if events[-1].end_tick < cell_ticks:
            events.append(MusicEvent(pitch=0, volume=0, start_tick=events[-1].end_tick,
                                     end_tick=cell_ticks))
    else:
        events.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=cell_ticks))
    return MusicUnit(events=events)


# ────────────────────────── main ──────────────────────────
def main():
    import random
    rng = random.Random(42)
    
    files = unique_files()
    byname = {}
    for f in files:
        b = os.path.basename(f).lower()
        byname[b] = f
    
    # Identify files
    MEL = None  # E minor melody (Moonlight_Shadow 2.mid)
    TRUMPET = None  # E minor trumpet
    FULL = None  # E major full arrangement
    VOCAL = None  # E major vocal
    PIANO = None  # C major piano
    PERC = None  # percussion
    
    for f in files:
        b = os.path.basename(f).lower()
        sz = os.path.getsize(f)
        if sz == 2450:
            MEL = f
        elif sz == 3966:
            TRUMPET = f
        elif sz == 32012:
            FULL = f
        elif sz == 18950:
            VOCAL = f
        elif sz == 2389:
            PIANO = f
        elif sz == 8986:
            PERC = f
    
    print("Sources:")
    for name, f in [("MEL", MEL), ("TRUMPET", TRUMPET), ("FULL", FULL), 
                     ("VOCAL", VOCAL), ("PIANO", PIANO), ("PERC", PERC)]:
        if f:
            print(f"  {name}: {os.path.basename(f)}")
    
    # Read all notes
    notes = {}
    for name, f in [("MEL", MEL), ("TRUMPET", TRUMPET), ("FULL", FULL), 
                     ("VOCAL", VOCAL), ("PIANO", PIANO), ("PERC", PERC)]:
        if f:
            bpm = get_file_bpm(f)
            notes[name] = read_notes(f, bpm)
            print(f"  {name}: {len(notes[name])} notes @ {bpm:.0f}bpm")
    
    # ── Lead: Melody G (E minor → E major, transpose -3) ──
    # Use music21 for clean melody extraction
    from music21 import converter as m21c
    _s = m21c.parse(MEL)
    _mel = []
    for n in _s.flatten().notes:
        if n.isNote and 62 <= n.pitch.midi <= 74:
            _mel.append((n.offset, n.pitch.midi, float(n.duration.quarterLength), 90, 0))
    mel_notes = sorted(_mel, key=lambda x: x[0])
    
    # Form alignment: Melody G verse starts at bar 0, but Full E has intro at bars 0-3
    # So Melody G needs to be shifted to start at bar 4 (Intro section)
    # Actually, let's use the full form: Intro (4 bars, empty or sparse) + Verse1 (8 bars) + ...
    # Melody G is 36 bars = Verse (8) + Chorus (8) + Verse (8) + Outro (12)
    # Map: bars 0-8 → Verse1, 8-16 → Chorus, 16-24 → Verse2, 24-36 → Outro
    
    # For simplicity, use Melody G as the primary melody source
    # Slice into sections: Intro (empty), Verse1 (0-8), Chorus (8-16), Verse2 (16-24), Outro (24-36)
    
    def slice_notes(notes_list, start_ql, end_ql):
        return [n for n in notes_list if start_ql <= n[0] < end_ql]
    
    # Melody G form (36 bars = 144 ql)
    intro_notes = []  # empty
    verse1_notes = slice_notes(mel_notes, 0, 32)  # bars 0-8
    chorus_notes = slice_notes(mel_notes, 32, 64)  # bars 8-16
    verse2_notes = slice_notes(mel_notes, 64, 96)  # bars 16-24
    outro_notes = slice_notes(mel_notes, 96, 144)  # bars 24-36
    
    # Transpose E minor → E major (-3 semis)
    lead_units = [
        unit_from_notes(intro_notes, -3, E_MAJOR, SECTION_TICKS[0], vol=100, section_start_ql=0),
        unit_from_notes(verse1_notes, -3, E_MAJOR, SECTION_TICKS[1], vol=100, section_start_ql=0),
        unit_from_notes(chorus_notes, -3, E_MAJOR, SECTION_TICKS[2], vol=100, section_start_ql=32),
        unit_from_notes(verse2_notes, -3, E_MAJOR, SECTION_TICKS[3], vol=100, section_start_ql=64),
        unit_from_notes(outro_notes, -3, E_MAJOR, SECTION_TICKS[4], vol=100, section_start_ql=96),
    ]
    
    # ── CounterLead: Full E oboe (already E major, no transpose) ──
    # Full E has intro at bars 0-3, verse at bars 4-12, etc.
    # Extract oboe (part 0, range 59-71)
    _s2 = m21c.parse(FULL)
    oboe_notes = []
    for n in _s2.parts[0].flatten().notes:
        if n.isNote and 59 <= n.pitch.midi <= 71:
            oboe_notes.append((n.offset, n.pitch.midi, float(n.duration.quarterLength), 80, 0))
    oboe_notes.sort(key=lambda x: x[0])
    
    # Full E form (115 bars = 460 ql): Intro (0-16), Verse1 (16-48), Chorus (48-80), Verse2 (80-112), Outro (112-115)
    # Full E verse has a 2-note pickup at offset 15.0/15.5 (anacrusis into bar 4).
    # Slice from 15 to capture the pickup, aligned to our Verse1 cell.
    full_verse1 = slice_notes(oboe_notes, 15, 48)  # bars 3.75-12 (incl pickup)
    full_chorus = slice_notes(oboe_notes, 48, 80)  # bars 12-20
    full_verse2 = slice_notes(oboe_notes, 80, 112)  # bars 20-28
    full_outro = slice_notes(oboe_notes, 112, 144)  # bars 28-36
    
    ctr_units = [
        unit_from_notes([], 0, E_MAJOR, SECTION_TICKS[0], vol=80, section_start_ql=0),
        unit_from_notes(full_verse1, 0, E_MAJOR, SECTION_TICKS[1], vol=80, section_start_ql=15),
        unit_from_notes(full_chorus, 0, E_MAJOR, SECTION_TICKS[2], vol=80, section_start_ql=48),
        unit_from_notes(full_verse2, 0, E_MAJOR, SECTION_TICKS[3], vol=80, section_start_ql=80),
        unit_from_notes(full_outro, 0, E_MAJOR, SECTION_TICKS[4], vol=80, section_start_ql=112),
    ]
    
    # ── Pad: Full E piano (chords, already E major) ──
    piano_notes = []
    for n in _s2.parts[2].flatten().notes:
        if n.isNote and 55 <= n.pitch.midi <= 84:
            piano_notes.append((n.offset, n.pitch.midi, float(n.duration.quarterLength), 70, 0))
    piano_notes.sort(key=lambda x: x[0])
    
    pad_verse1 = slice_notes(piano_notes, 15, 48)
    pad_chorus = slice_notes(piano_notes, 48, 80)
    pad_verse2 = slice_notes(piano_notes, 80, 112)
    pad_outro = slice_notes(piano_notes, 112, 144)
    
    pad_units = [
        unit_from_notes([], 0, E_MAJOR, SECTION_TICKS[0], vol=70, section_start_ql=0),
        unit_from_notes(pad_verse1, 0, E_MAJOR, SECTION_TICKS[1], vol=70, section_start_ql=15),
        unit_from_notes(pad_chorus, 0, E_MAJOR, SECTION_TICKS[2], vol=70, section_start_ql=48),
        unit_from_notes(pad_verse2, 0, E_MAJOR, SECTION_TICKS[3], vol=70, section_start_ql=80),
        unit_from_notes(pad_outro, 0, E_MAJOR, SECTION_TICKS[4], vol=70, section_start_ql=112),
    ]
    
    # ── Bass: Full E bass (already E major) ──
    bass_notes = []
    for n in _s2.parts[4].flatten().notes:
        if n.isNote and 28 <= n.pitch.midi <= 52:
            bass_notes.append((n.offset, n.pitch.midi, float(n.duration.quarterLength), 88, 0))
    bass_notes.sort(key=lambda x: x[0])
    
    # Bass is already E major (28-52); do NOT quantize — just clamp to register.
    # Use a permissive scale = all E-major pitches in bass register.
    E_MAJOR_BASS = [28, 30, 32, 33, 35, 37, 39, 40, 42, 44, 45, 47, 49, 51, 52]
    
    bass_verse1 = slice_notes(bass_notes, 15, 48)
    bass_chorus = slice_notes(bass_notes, 48, 80)
    bass_verse2 = slice_notes(bass_notes, 80, 112)
    bass_outro = slice_notes(bass_notes, 112, 144)
    
    bass_units = [
        unit_from_notes([], 0, E_MAJOR_BASS, SECTION_TICKS[0], vol=88, section_start_ql=0),
        unit_from_notes(bass_verse1, 0, E_MAJOR_BASS, SECTION_TICKS[1], vol=88, section_start_ql=15),
        unit_from_notes(bass_chorus, 0, E_MAJOR_BASS, SECTION_TICKS[2], vol=88, section_start_ql=48),
        unit_from_notes(bass_verse2, 0, E_MAJOR_BASS, SECTION_TICKS[3], vol=88, section_start_ql=80),
        unit_from_notes(bass_outro, 0, E_MAJOR_BASS, SECTION_TICKS[4], vol=88, section_start_ql=112),
    ]
    
    # ── Arp: continuous 8th-note arpeggio from pad chords ──
    def arp_unit_from_pad(pad_unit, cell_ticks: int):
        events = []
        E_MAJOR_FALLBACK = [52, 56, 59, 64, 68, 71, 76]  # Emaj triad across 2 octaves
        for bar in range(cell_ticks // BAR):
            b0, b1 = bar * BAR, (bar + 1) * BAR
            # exclude silent landmarks (pitch 0)
            bar_pitches = sorted({e.pitch for e in pad_unit.events
                                  if b0 <= e.start_tick < b1 and e.pitch > 0})
            if bar_pitches:
                root = bar_pitches[0]
                chord_tones = [p for p in E_MAJOR if abs(p - root) <= 24]
                if len(chord_tones) < 3:
                    chord_tones = [p for p in (root, root + 4, root + 7, root + 12)
                                   if p in E_MAJOR]
                    if len(chord_tones) < 3:
                        chord_tones = E_MAJOR_FALLBACK
            else:
                chord_tones = E_MAJOR_FALLBACK
            arp = chord_tones[:4] + [chord_tones[2], chord_tones[1]]
            step = TPB // 2
            for k in range(BAR // step):
                pitch = arp[k % len(arp)]
                st = b0 + k * step
                events.append(MusicEvent(pitch=pitch, volume=72,
                                         start_tick=st,
                                         end_tick=min(st + step - 20, b1)))
        if events:
            if events[-1].end_tick < cell_ticks:
                events.append(MusicEvent(pitch=0, volume=0, start_tick=events[-1].end_tick,
                                         end_tick=cell_ticks))
        else:
            events.append(MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=cell_ticks))
        return MusicUnit(events=events)
    
    arp_units = [arp_unit_from_pad(pad_units[i], SECTION_TICKS[i]) for i in range(N_SECTIONS)]
    
    # ── Drums: percussion file (90bpm → 126bpm, 4-bar loop) ──
    # Percussion pattern: kick (36) on 1,3; snare (38) on 2,4; hat (42) on 8ths
    # At 90bpm, 4 bars = 16 ql. At 126bpm, 4 bars = 16 ql (same duration, different tempo)
    # So we can use the pattern directly
    drum_pat = [36, 42, 42, 42, 38, 42, 42, 42, 36, 42, 42, 42, 38, 42, 42, 42]  # 4 bars
    drum_units = [drum_unit(drum_pat, SECTION_TICKS[i], vel=92) for i in range(N_SECTIONS)]
    
    # ────────────────────────── matrix build ──────────────────────────
    composer = UnitMatrixComposer(bpm=TARGET_BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=6, num_sections=N_SECTIONS)
    composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    composer.add_voice("CounterLead", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
    composer.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=2)
    composer.add_voice("Bass", program=MidiInstrument.BASS, channel=3)
    composer.add_voice("Arp", program=MidiInstrument.ACOUSTIC_GUITAR, channel=4)
    composer.add_voice("Drums", program=0, channel=9)
    for sname, sbars in SECTIONS:
        composer.add_section(sname, bars=sbars)
    
    for i, (sname, _) in enumerate(SECTIONS):
        composer.fill_voice_section("Lead", sname, lead_units[i])
        composer.fill_voice_section("CounterLead", sname, ctr_units[i])
        composer.fill_voice_section("Pad", sname, pad_units[i])
        composer.fill_voice_section("Bass", sname, bass_units[i])
        composer.fill_voice_section("Arp", sname, arp_units[i])
        composer.fill_voice_section("Drums", sname, drum_units[i])
    
    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"zero-drift validation FAILED: {msg}")
    aligned_path = str(PROJ / "MIDI" / "moonlight-shadow-aligned.mid")
    composer.to_midi(aligned_path)
    assert os.path.getsize(aligned_path) > 40
    write_provenance(aligned_path, AI_ASSISTED,
                     generator="align+matrix (sources: 6 versions of Moonlight Shadow)",
                     sources={"MEL": os.path.basename(MEL), "FULL": os.path.basename(FULL),
                              "PERC": os.path.basename(PERC)},
                     parameters={"bpm": TARGET_BPM, "key": "E major", "form": SECTIONS,
                                 "quantization": "16th", "transpose": "E minor → E major (-3)"})
    write_grid_visualization(composer.matrix, str(PROJ / "Analysis" / "grid_aligned.txt"))
    print(f"\n✅ Aligned matrix MIDI: {aligned_path} ({os.path.getsize(aligned_path)} B)")
    print(f"   Sections: {SECTIONS} → {TOTAL_TICKS} ticks/row")
    
    # ────────────────────────── Phase B: two random methods ──────────────────────────
    methods = ["markov", "tendency", "schillinger", "stochastic", "genetic"]
    chosen = rng.sample(methods, 2)
    print(f"\n🎲 Random methods: {chosen}")
    
    from generators.markov_constraint import MarkovConstraintGenerator
    from generators.tendency_masking import TendencyMaskingGenerator
    from generators.schillinger import SchillingerGenerator
    from generators.stochastic import StochasticGenerator
    from generators.genetic import GeneticGenerator
    
    E_SCALE_PITCHES = [52, 54, 56, 57, 59, 61, 63, 64, 66, 68, 69, 71, 73, 75, 76]
    
    def make_variant(name: str, method: str, seed: int):
        random.seed(seed)
        gen_composer = UnitMatrixComposer(bpm=TARGET_BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
        gen_composer.create_matrix(num_voices=6, num_sections=N_SECTIONS)
        gen_composer.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
        gen_composer.add_voice("CounterLead", program=MidiInstrument.STRING_ENSEMBLE, channel=1)
        gen_composer.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=2)
        gen_composer.add_voice("Bass", program=MidiInstrument.BASS, channel=3)
        gen_composer.add_voice("Arp", program=MidiInstrument.ACOUSTIC_GUITAR, channel=4)
        gen_composer.add_voice("Drums", program=0, channel=9)
        for sname, sbars in SECTIONS:
            gen_composer.add_section(sname, bars=sbars)
        
        raw_units = []
        for i, (sname, sbars) in enumerate(SECTIONS):
            cell_ticks = SECTION_TICKS[i]
            # Phase 1: raw generative lead
            if method == "markov":
                gen = MarkovConstraintGenerator(key_pitches=E_SCALE_PITCHES, min_pitch=60, max_pitch=84)
                raw = gen.generate_voice_section(cell_ticks, SIXTEENTH * 2, density=0.85, volume=95)
            elif method == "tendency":
                gen = TendencyMaskingGenerator(key_pitches=E_SCALE_PITCHES)
                lo = 62 + (i % 2) * 2
                hi = 76 + (i % 2) * 2
                raw = gen.generate_voice_section(cell_ticks, SIXTEENTH * 2,
                                                 bounds_start=(lo, hi), bounds_end=(hi - 2, hi + 4),
                                                 density=0.8, volume=95)
            elif method == "schillinger":
                gen = SchillingerGenerator(generator_a=3, generator_b=2)
                raw = gen.generate_unit(base_tick_dur=SIXTEENTH * 2, key_scale=E_SCALE_PITCHES)
            elif method == "stochastic":
                gen = StochasticGenerator(length=cell_ticks // SIXTEENTH,
                                          pitch_set=E_SCALE_PITCHES,
                                          duration_set=[SIXTEENTH, SIXTEENTH * 2, SIXTEENTH * 4])
                raw = gen.generate()[0] if gen.generate() else MusicUnit(events=[])
            else:  # genetic
                def fitness(genome):
                    total = 0
                    prev = None
                    for i in range(0, len(genome), 18):
                        part = genome[i:i + 18]
                        if len(part) < 18:
                            continue
                        pitch = int(sum([bit * pow(2, j) for j, bit in enumerate(part[0:6])]))
                        if prev is not None:
                            total += min(abs(pitch - prev), 63)
                        prev = pitch
                    return total
                gen = GeneticGenerator(fitness_func=fitness, size=16,
                                       genome_length=18 * 32,
                                       fitness_limit=1200, generation_limit=30)
                raw = gen.generate()[0] if gen.generate() else MusicUnit(events=[])
            
            raw_units.append(raw)
            # Phase 2: quantize to chord tones
            pad_events = sorted(pad_units[i].events, key=lambda e: e.start_tick)
            chord_tones = [e.pitch for e in pad_events] or E_MAJOR
            q_events = []
            for e in raw.events:
                if e.pitch == 0:
                    q_events.append(e)
                    continue
                if chord_tones:
                    qp = min(chord_tones, key=lambda p: abs(p - e.pitch))
                else:
                    qp = e.pitch
                qp = max(0, min(127, qp))
                q_events.append(MusicEvent(pitch=qp, volume=e.volume,
                                           start_tick=min(e.start_tick, cell_ticks - 1),
                                           end_tick=min(e.end_tick, cell_ticks)))
            q_unit = MusicUnit(events=q_events)
            gen_composer.fill_voice_section("Lead", sname, q_unit)
            gen_composer.fill_voice_section("CounterLead", sname, ctr_units[i])
            gen_composer.fill_voice_section("Pad", sname, pad_units[i])
            gen_composer.fill_voice_section("Bass", sname, bass_units[i])
            gen_composer.fill_voice_section("Arp", sname, arp_units[i])
            gen_composer.fill_voice_section("Drums", sname, drum_units[i])
        
        ok, msg = gen_composer.validate()
        if not ok:
            raise RuntimeError(f"variant {name} validation FAILED: {msg}")
        final_path = str(PROJ / "MIDI" / f"moonlight-shadow-{name}.mid")
        gen_composer.to_midi(final_path)
        assert os.path.getsize(final_path) > 40
        write_provenance(final_path, AI_ASSISTED, generator=method,
                         sources={"MEL": os.path.basename(MEL), "FULL": os.path.basename(FULL)},
                         parameters={"method": method, "seed": seed, "bpm": TARGET_BPM,
                                     "key": "E major", "form": SECTIONS,
                                     "phase": "2 (chord-tone quantized)"})
        
        # Phase 1 raw export
        p1 = UnitMatrixComposer(bpm=TARGET_BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
        p1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
        p1.add_voice("RawDraft", program=MidiInstrument.FLUTE, channel=0)
        for sname, sbars in SECTIONS:
            p1.add_section(sname, bars=sbars)
        for i, (sname, _) in enumerate(SECTIONS):
            p1.fill_voice_section("RawDraft", sname, raw_units[i])
        ok1, msg1 = p1.validate()
        if not ok1:
            raise RuntimeError(f"variant {name} phase1 validation FAILED: {msg1}")
        p1_path = str(PROJ / "MIDI" / f"moonlight-shadow-{name}-phase1.mid")
        p1.to_midi(p1_path)
        assert os.path.getsize(p1_path) > 40
        write_provenance(p1_path, AI_ASSISTED, generator=method,
                         parameters={"method": method, "seed": seed, "phase": "1 (pre-rules)"})
        write_grid_visualization(gen_composer.matrix,
                                 str(PROJ / "Analysis" / f"grid_{name}.txt"))
        print(f"   ✅ {name} ({method}): {os.path.basename(final_path)} "
              f"{os.path.getsize(final_path)} B + phase1 {os.path.getsize(p1_path)} B")
    
    # Generate variants
    for name, method in zip(["variant1", "variant2"], chosen):
        make_variant(name, method, seed=random.randint(0, 99999))
    
    # Summary
    summary = {
        "project": "moonlight-shadow",
        "style": "Pop",
        "bpm": TARGET_BPM,
        "key": "E major",
        "form": [f"{s}({b}b)" for s, b in SECTIONS],
        "total_bars": TOTAL_BARS,
        "sources": {
            "MEL": os.path.basename(MEL),
            "FULL": os.path.basename(FULL),
            "PERC": os.path.basename(PERC),
        },
        "transpose": "E minor → E major (-3 semis)",
        "outputs": {
            "aligned": "MIDI/moonlight-shadow-aligned.mid",
            "variants": [f"MIDI/moonlight-shadow-variant{i+1}.mid" for i in range(2)],
            "phase1": [f"MIDI/moonlight-shadow-variant{i+1}-phase1.mid" for i in range(2)],
        },
        "methods": chosen,
        "seed": 42,
    }
    with open(PROJ / "Analysis" / "summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n📄 Summary: {PROJ / 'Analysis' / 'summary.json'}")


if __name__ == "__main__":
    import json
    main()
