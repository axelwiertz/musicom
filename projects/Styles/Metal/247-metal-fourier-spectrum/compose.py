# -*- coding: utf-8 -*-
"""247 — Metal Fourier Spectrum (Method 113 PCFSC, abstract).

Autonomous nightly composition job (2026-10-16). Style: Metal.
Method 113 Pitch-Class Fourier Spectrum Composition (PCFSC), layer ABSTRACT,
paradigm Rules-Based.

Method 113 essence (Amiot 2016, Fourier space over Z_12):
  * A pitch-class SET (pool) maps to 12 complex Fourier coefficients
        f_A(k) = sum_{a in A} e^{2*pi*i*k*a/12}
    - magnitude |f_A(k)| = the *quality* spectrum (whole-tone -> energy only
      at k=6; octatonic -> k=4,8; diatonic -> peak at k=5,7).
    - phase arg f_A(k) = the *position*/tonic function (transposition =
      phase rotation; major/minor triads are magnitude-twins, mode lives in
      phase).
  * Composition = a trajectory in Fourier space: per-section target quality
    profile + a designed phase walk = the pitch-pool sequence + tension curve.
  * Tension = weighted Fourier-space distance between successive pools (TIV).

Abstract -> concrete interpretation for this piece (Metal, head-solos-head):
  * Section pools ARE the Fourier profiles (one pc-set per section):
      Head  : E natural minor  {4,6,7,9,11,0,2}  -> diatonic, |f5|/|f7| peak (HOME)
      Solo1 : E harmonic minor {4,6,7,9,11,0,3}  -> leading tone D#, |f5| + spread (LIFT)
      Solo2 : E half-whole octatonic {4,5,7,8,10,11,1,2} -> dim7 lattice |f3|/|f4|/|f8| (TENSE)
      Head  : return to natural minor (phase returns to anchor = HOME resolution)
  * Phase walk: Head locks the tonic anchor (v=0); Solo1 drifts the tonal
    center (rising leading-tone motion); Solo2 runs fast diminished sweeps
    (high phase velocity); Head return resolves to the opening anchor.
  * Complement pairing: rhythm power-chords (sparse 3-note pool) sit over the
    full 7-note natural-minor lead pool = same quality, two densities.

Form: head-solos-head -> Head(8) Solo1(8) Solo2(8) Head(8) = 32 bars.
Key E minor, 140 BPM, 480 TPB, 4/4, 16th grid (120 ticks).

Two-phase architecture (mandatory):
  Phase 1 (raw): single lead-guitar voice, raw pc-pool walk (unquantized
    pitch, off-grid micro-timing, NO harmony) -> 247-...-phase1.mid
  Phase 2 (rules): chord-tone quantization, 16th-grid onset snap, voice-
    leading check, full texture (lead + rhythm power chords + bass + drums),
    always-on seeded humanization -> 247-....mid
"""
import itertools
import json
import math
import os
import random
import sys

import numpy as np

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from rules.voice_leading import VoiceLeadingRules

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import OVERDRIVEN_GUITAR, ELECTRIC_BASS  # noqa: E402

# ---- Concept ----------------------------------------------------------------
SEED = 247
STYLE = "metal"
METHOD_ID = 113
METHOD_NAME = "Pitch-Class Fourier Spectrum Composition (PCFSC)"
LAYER = "abstract"
KEY_NAME = "E minor"
KEY_ROOT_PC = 4            # E
BPM = 140
TPB = 480
BPB = 4
BAR = TPB * BPB            # 1920
SIXTEENTH = 120
EIGHTH = 240

# ---- Form: head-solos-head (names disambiguated for the matrix) -------------
SECTIONS = [("Head1", 8), ("Solo1", 8), ("Solo2", 8), ("Head2", 8)]
TOTAL_BARS = sum(b for _, b in SECTIONS)
TOTAL_TICKS = TOTAL_BARS * BAR

# ---- Fourier pools (pc-sets) per section ------------------------------------
# Section index -> pc-set. Head (0,3) natural minor; Solo1 harmonic minor;
# Solo2 half-whole octatonic.
POOL_BY_SECTION = {
    0: {4, 6, 7, 9, 11, 0, 2},      # E natural minor (aeolian)
    1: {4, 6, 7, 9, 11, 0, 3},      # E harmonic minor (raised 7th -> D#)
    2: {4, 5, 7, 8, 10, 11, 1, 2},  # E half-whole octatonic (metal shred)
    3: {4, 6, 7, 9, 11, 0, 2},      # return to natural minor (HOME)
}
POOL_NAME = {
    0: "E natural minor (aeolian)",
    1: "E harmonic minor",
    2: "E half-whole octatonic",
    3: "E natural minor (aeolian, HOME)",
}

# ---- Chord plan (32 bars) ---------------------------------------------------
# (roman, name, root_pc, chord_tone_pcs) — every chord is a subset of its
# section pool, so chord-tone quantization => in-pool automatically.
_Em   = ("i",    "Em",    4, [4, 7, 11])
_C    = ("bVI",  "C",     0, [0, 4, 7])
_G    = ("bIII", "G",     7, [7, 11, 2])
_D    = ("bVII", "D",     2, [2, 6, 9])
_Am   = ("iv",   "Am",    9, [9, 0, 4])
_B    = ("V",    "B",     11, [11, 3, 6])
_Fsdim= ("ii°",  "F#dim", 6, [6, 9, 0])
_Edim7= ("i°7",  "Edim7", 4, [4, 7, 10, 1])
_Fdim7= ("°7",   "Fdim7", 5, [5, 8, 11, 2])
_Bdim = ("bvdim","Bdim",  11, [11, 2, 5])

_HEAD_CYCLE = [_Em, _Em, _C, _G, _D, _C, _D, _Em]              # aeolian cadence
_SOLO1_CYCLE = [_Em, _Am, _B, _Em, _C, _Fsdim, _B, _Em]        # leading-tone V
_SOLO2_CYCLE = [_Em, _Edim7, _Fdim7, _Em, _Edim7, _Bdim, _Fdim7, _Em]  # dim lattice
CHORDS = _HEAD_CYCLE + _SOLO1_CYCLE + _SOLO2_CYCLE + _HEAD_CYCLE
assert len(CHORDS) == TOTAL_BARS

# ---- Fourier machinery (method 113 core math) -------------------------------
OMEGA = np.exp(2j * np.pi / 12.0)


def pc_set_dft(pcs):
    """Complex Fourier coefficients f(k), k=0..11, of a pc-set."""
    v = np.zeros(12, dtype=complex)
    for p in pcs:
        v[p % 12] = 1.0
    k = np.arange(12)
    return np.array([np.sum(v * (OMEGA ** (kk * np.arange(12)))) for kk in range(12)])


def profile(pcs):
    """Normalized magnitude spectrum |f|/n (k=0..11). Quality fingerprint."""
    f = pc_set_dft(pcs)
    return np.abs(f) / max(1, len(pcs))


def fourier_tension(pcsA, pcsB):
    """Weighted Fourier-space distance (TIV-style tension) between two sets."""
    return float(np.sum(np.abs(pc_set_dft(pcsA) - pc_set_dft(pcsB))))


# ---- Section bookkeeping ----------------------------------------------------
SECTION_START_BARS = []
_acc = 0
for _n, _b in SECTIONS:
    SECTION_START_BARS.append(_acc)
    _acc += _b


def section_of_bar(bar):
    sec = 0
    for s in range(len(SECTIONS)):
        if bar >= SECTION_START_BARS[s]:
            sec = s
    return sec


def section_start_abs(s):
    return SECTION_START_BARS[s] * BAR


def section_ticks(s):
    return SECTIONS[s][1] * BAR


def split_abs_to_section(abs_events, s):
    start = section_start_abs(s)
    length = section_ticks(s)
    end = start + length
    cell = []
    # Sort by onset: the humanizer's forward-clamp assumes ascending onsets;
    # unsorted voices (e.g. drums: kick/snare/hats interleaved) would otherwise
    # get catastrophically forward-shifted.
    for e in sorted(abs_events, key=lambda e: (e.start_tick, e.pitch)):
        if e.end_tick <= start or e.start_tick >= end:
            continue
        st = max(0, e.start_tick - start)
        et = min(length, e.end_tick - start)
        if et <= st:
            continue
        cell.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                               start_tick=st, end_tick=et))
    if not cell or cell[-1].end_tick < length:
        last = cell[-1].end_tick if cell else 0
        cell.append(MusicEvent(pitch=0, volume=0, start_tick=last, end_tick=length))
    # Always pin the section end with a silent terminal landmark (end_tick ==
    # length) so len_ticks() == section length and survives humanization
    # (pitch-0 landmarks pass through untouched). Prevents a 4-12 tick
    # shortfall when the last audible note's tail is jittered inward.
    cell.append(MusicEvent(pitch=0, volume=0, start_tick=length, end_tick=length))
    return MusicUnit(events=cell)


# ---- Pitch helper -----------------------------------------------------------
def midi_pc(pc, lo, hi, center=None):
    """Nearest MIDI note for a pitch class within [lo,hi], biased to center."""
    center = center if center is not None else (lo + hi) // 2
    best, bestd = None, None
    for n in range(lo, hi + 1):
        if n % 12 == pc % 12:
            d = abs(n - center)
            if bestd is None or d < bestd:
                bestd, best = d, n
    return best


def chord_tones_midi(pcs, lo, hi):
    """Expand chord pcs to MIDI notes spanning [lo,hi] (sorted, octave-folded)."""
    out = set()
    for pc in pcs:
        n = midi_pc(pc, lo, hi)
        if n is not None:
            out.add(n)
    out = sorted(out)
    if not out:
        out = [lo]
    return out


def dedup(events):
    d, order = {}, []
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in d:
            d[key] = e
            order.append(key)
        elif (e.end_tick - e.start_tick) > (d[key].end_tick - d[key].start_tick):
            d[key] = e
    return [d[k] for k in order]


def bar_clamp(composer, voice_events):
    """Snap humanized onsets that crossed BACKWARD over a bar line forward to
    their intended bar's downbeat.

    The canonical humanizer forward-clamps per-section but does not pin bar
    lines, so a downbeat note jittered ~1-20 ticks early can land in the tail
    of the previous bar and read as out-of-chord against the previous bar's
    chord. Humanization preserves event order and pitch, so the i-th audible
    note in each cell corresponds to the i-th pre-humanize audible note; use
    that to recover the intended bar and pull the onset back onto it.
    """
    row_of = {v["name"]: v["row"] for v in composer.voices}
    for s in range(len(SECTIONS)):
        sec_start = section_start_abs(s)
        sec_len = section_ticks(s)
        for vname in VOICES:
            pre_local = []
            for e in voice_events[vname]:
                if e.pitch == 0:
                    continue
                if sec_start <= e.start_tick < sec_start + sec_len:
                    pre_local.append((e.start_tick - sec_start, e.pitch))
            # match split_abs_to_section's ordering (onset, then pitch)
            pre_local.sort(key=lambda x: (x[0], x[1]))
            row = row_of[vname]
            unit = composer.matrix.get_unit((row, s))
            if unit is None:
                continue
            # audible-note indices in the stored structured array (data order)
            post_idx = [i for i in range(len(unit.data))
                        if int(unit.data[i]['pitch']) != 0]
            for (pe_onset, _pitch), idx in zip(pre_local, post_idx):
                bar_in_section = pe_onset // BAR
                bar_start = bar_in_section * BAR
                st = int(unit.data[idx]['start_tick'])
                et = int(unit.data[idx]['end_tick'])
                if st < bar_start:
                    unit.data['start_tick'][idx] = bar_start
                    if et < bar_start + 1:
                        unit.data['end_tick'][idx] = bar_start + 1
                elif st >= bar_start + BAR:
                    unit.data['start_tick'][idx] = bar_start + BAR - 1
                    if et <= st:
                        unit.data['end_tick'][idx] = bar_start + BAR


# ---- Rhythm cells (16th-grid locked) ----------------------------------------
GALLOP = [0, 120, 240, 480, 600, 720, 960, 1080, 1200, 1440, 1560, 1680]  # 16-16-8 x4
STRAIGHT_16 = [i * 120 for i in range(16)]
STRAIGHT_8 = [i * 240 for i in range(8)]


# ---- Phase-1 raw draft ------------------------------------------------------
def build_raw_events():
    """Single lead voice, raw pc-pool walk: unquantized pitch + off-grid
    micro-timing, NO harmony. Pitch indices drawn from a random walk over the
    section pool (the abstract Fourier plan realized WITHOUT the rules layer)."""
    rng = random.Random(SEED)
    out = []
    n_events = TOTAL_BARS * 8
    for i in range(n_events):
        bar = min(TOTAL_BARS - 1, int(i * TOTAL_BARS / float(n_events)))
        sec = section_of_bar(bar)
        pool = sorted(POOL_BY_SECTION[sec])
        # raw pitch: random walk over pool indices -> unquantized MIDI
        idx = rng.randrange(len(pool))
        pc = pool[idx]
        pitch = midi_pc(pc, 55, 95, center=70)
        # off-grid onset: base slot + jitter (NOT a multiple of 120)
        st = int(i * (TOTAL_TICKS / float(n_events))) + rng.randint(-90, 90)
        st = max(0, min(TOTAL_TICKS - 40, st))
        dur = 80 + rng.randint(0, 160)
        vel = 55 + rng.randint(0, 55)
        out.append(MusicEvent(pitch=pitch, volume=vel,
                              start_tick=st,
                              end_tick=min(TOTAL_TICKS, st + dur)))
    return out


# ---- Phase-2 voices ---------------------------------------------------------
def build_lead(chords):
    """Lead guitar: chord-tone arpeggio runs, register/velocity per section.
    Head = gallop riff; Solo1 = 16th ascending sweep (phase drift); Solo2 =
    descending dim7 sweep (fast phase); Head = gallop return. 16th-grid only."""
    events = []
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        base = bar * BAR
        tones = chord_tones_midi(chords[bar][3], 64, 91)
        if sec == 0 or sec == 3:
            slots = GALLOP
            vel_base = 92
            pat = [0, 1, 2, 1]
        elif sec == 1:
            slots = STRAIGHT_16
            vel_base = 88
            pat = [0, 1, 2, 3]
        else:  # sec == 2
            slots = STRAIGHT_16
            vel_base = 95
            pat = [0, 1, 2, 3, 2, 1]
        k = 0
        for slot in slots:
            ti = tones[pat[k % len(pat)] % len(tones)]
            k += 1
            st = base + slot
            dur = SIXTEENTH if sec in (1, 2) else (2 * SIXTEENTH if slot % 240 == 0 else SIXTEENTH)
            vel = vel_base - (k % 2) * 8
            events.append(MusicEvent(pitch=ti, volume=vel,
                                     start_tick=st, end_tick=st + dur))
    return dedup(events)


def build_rhythm(chords):
    """Rhythm guitar: palm-muted power chords (root+5th+octave), 8th chug in
    Head, 16th chug in solos (the sparse-pool density over the full lead pool)."""
    events = []
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        base = bar * BAR
        rpc = chords[bar][2]
        cpc = set(chords[bar][3])
        root = midi_pc(rpc, 40, 52, center=45)
        # Power-chord upper interval: perfect 5th if present, else the tritone
        # (diminished "diabolus" power chord — idiomatic for the octatonic
        # dim7 shred section), else minor 3rd. Every tone stays a chord tone.
        if (rpc + 7) % 12 in cpc:
            upper = root + 7
        elif (rpc + 6) % 12 in cpc:
            upper = root + 6
        elif (rpc + 3) % 12 in cpc:
            upper = root + 3
        else:
            upper = root + 7
        octv = root + 12
        if sec in (1, 2):
            slots = STRAIGHT_16
            dur = 90
        else:
            slots = STRAIGHT_8
            dur = 170
        for slot in slots:
            st = base + slot
            for p in (root, upper, octv):
                events.append(MusicEvent(pitch=p, volume=86,
                                         start_tick=st, end_tick=st + dur))
    return dedup(events)


def build_bass(chords):
    """Electric bass: root locked with the kick — 8ths in Head, 16ths in solos."""
    events = []
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        base = bar * BAR
        rpc = chords[bar][2]
        root = midi_pc(rpc, 28, 40, center=34)
        if sec in (1, 2):
            slots = STRAIGHT_16
        else:
            slots = STRAIGHT_8
        for slot in slots:
            st = base + slot
            events.append(MusicEvent(pitch=root, volume=92,
                                     start_tick=st, end_tick=st + 100))
    return dedup(events)


def build_drums():
    """Metal kit: Head = rock beat (kick 1&3, snare 2&4, hats 8th); Solo1/2 =
    double-kick 16ths; crash on section seams. 16th-grid locked."""
    events = []
    kick = MidiPercussion.BASS_DRUM
    snare = MidiPercussion.ACOUSTIC_SNARE
    hh = MidiPercussion.CLOSED_HI_HAT
    crash = MidiPercussion.CRASH_CYMBAL
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        base = bar * BAR
        is_first = bar in SECTION_START_BARS
        # kick
        if sec in (1, 2):
            for slot in STRAIGHT_16:
                events.append(MusicEvent(pitch=kick, volume=88,
                                         start_tick=base + slot,
                                         end_tick=base + slot + 60))
        else:
            for beat in (0, 960):
                events.append(MusicEvent(pitch=kick, volume=92,
                                         start_tick=base + beat,
                                         end_tick=base + beat + 60))
        # snare on 2 & 4
        for beat in (480, 1440):
            events.append(MusicEvent(pitch=snare, volume=100,
                                     start_tick=base + beat,
                                     end_tick=base + beat + 80))
        # hats: 8th in Head, 16th in solos
        hh_slots = STRAIGHT_16 if sec == 2 else STRAIGHT_8
        for slot in hh_slots:
            if (slot % 480) == 0 and sec in (0, 3):
                pass  # leave beat downbeats open for kick clarity in Head
            events.append(MusicEvent(pitch=hh, volume=64,
                                     start_tick=base + slot,
                                     end_tick=base + slot + 40))
        # crash on section downbeats
        if is_first:
            events.append(MusicEvent(pitch=crash, volume=90,
                                     start_tick=base, end_tick=base + 400))
    return dedup(events)


# ---- Compose ----------------------------------------------------------------
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)

BASE = "247-metal-fourier-spectrum"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

VOICES = ["Lead", "Rhythm", "Bass", "Drums"]
VOICE_PROGRAMS = [OVERDRIVEN_GUITAR.midi_program, OVERDRIVEN_GUITAR.midi_program,
                  ELECTRIC_BASS.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 9]
PITCHED_VOICES = ["Lead", "Rhythm", "Bass"]


def audit_voice(name, events, pitched):
    onsets = [e.start_tick for e in events if e.pitch != 0]
    off16 = sum(1 for o in onsets if o % 120 != 0)
    off8 = sum(1 for o in onsets if o % 240 != 0)
    out_scale = 0
    out_chord = 0
    if pitched:
        for e in events:
            if e.pitch == 0:
                continue
            pc = e.pitch % 12
            bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
            sec = section_of_bar(bar)
            pool = POOL_BY_SECTION[sec]
            cpc = set(CHORDS[bar][3])
            if pc not in pool:
                out_scale += 1
            if pc not in cpc:
                out_chord += 1
    return {"name": name, "n_notes": len(onsets), "off16": off16,
            "off8": off8, "out_scale": out_scale, "out_chord": out_chord}


def compose():
    # ---- Phase 1: raw single-voice draft ------------------------------------
    raw = build_raw_events()
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawLead", program=OVERDRIVEN_GUITAR.midi_program, channel=0)
    for name, bars in SECTIONS:
        p1.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        p1.fill_voice_section("RawLead", name, split_abs_to_section(raw, s))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: rules post-process ----------------------------------------
    lead = build_lead(CHORDS)
    rhythm = build_rhythm(CHORDS)
    bass = build_bass(CHORDS)
    drums = build_drums()
    voice_events = {"Lead": lead, "Rhythm": rhythm, "Bass": bass, "Drums": drums}

    # inline grid + harmony audit on the PRE-humanization quantized events
    inline_audit = {v: audit_voice(v, voice_events[v], v in PITCHED_VOICES)
                    for v in VOICES}

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for name, bars in SECTIONS:
        composer.add_section(name, bars=bars)
    for s, (name, _bars) in enumerate(SECTIONS):
        for vname in VOICES:
            composer.fill_voice_section(vname, name,
                                        split_abs_to_section(voice_events[vname], s))

    # grid visualization captures the clean quantized grid (pre-humanize)
    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(composer.matrix, grid_path, ticks_per_character=120,
                             voice_names=VOICES, bpm=BPM, mode="E minor (Fourier pools)")

    # voice-leading check on the rhythm power-chord voicings (informational)
    vl = VoiceLeadingRules(style="classical")
    rhythm_voicings = []
    for bar in range(TOTAL_BARS):
        rpc = CHORDS[bar][2]
        root = midi_pc(rpc, 40, 52, center=45)
        rhythm_voicings.append([root, root + 7, root + 12])
    vl_violations = []
    for i in range(1, len(rhythm_voicings)):
        vl_violations += vl.check_parallel_motion(rhythm_voicings[i - 1],
                                                  rhythm_voicings[i])
        vl_violations += vl.check_hidden_fifths(rhythm_voicings[i - 1],
                                                rhythm_voicings[i])

    # ---- always-on seeded humanization --------------------------------------
    from workflows.humanize import humanize_composer
    hz_instruments = {
        "Lead": OVERDRIVEN_GUITAR.humanize_dna,
        "Rhythm": OVERDRIVEN_GUITAR.humanize_dna,
        "Bass": ELECTRIC_BASS.humanize_dna,
        "Drums": (2.0, 4.0, 0.0, 0.008),   # drum kit anchors the grid
    }
    hz = humanize_composer(composer, style=STYLE, seed=SEED, bpm=BPM,
                           instruments=hz_instruments)

    # Bar-line guard: snap onsets that jittered backward over a bar boundary
    # back onto their intended downbeat (keeps every note in its bar's chord).
    bar_clamp(composer, voice_events)

    ok2, msg2 = composer.validate()
    if not ok2:
        raise RuntimeError(f"Phase 2 zero-drift FAILED: {msg2}")
    composer.to_midi(MIDI_PATH)

    # ---- Fourier spectra + tension curve (method 113 outputs) ---------------
    spectra = {}
    for s, (name, _b) in enumerate(SECTIONS):
        pool = POOL_BY_SECTION[s]
        prof = profile(pool)
        spectra[s] = {
            "section": name, "pool": sorted(pool), "pool_name": POOL_NAME[s],
            "cardinality": len(pool),
            "f5": round(float(np.abs(pc_set_dft(pool)[5])), 4),
            "f7": round(float(np.abs(pc_set_dft(pool)[7])), 4),
            "f6": round(float(np.abs(pc_set_dft(pool)[6])), 4),
            "f3": round(float(np.abs(pc_set_dft(pool)[3])), 4),
            "f4": round(float(np.abs(pc_set_dft(pool)[4])), 4),
            "profile": [round(float(x), 4) for x in prof],
        }
    tension_curve = []
    for s in range(len(SECTIONS) - 1):
        tension_curve.append({
            "from": SECTIONS[s][0], "to": SECTIONS[s + 1][0],
            "fourier_tension": round(fourier_tension(POOL_BY_SECTION[s],
                                                     POOL_BY_SECTION[s + 1]), 4),
        })
    tension_curve.append({
        "from": SECTIONS[-1][0], "to": "end (loop to Head)",
        "fourier_tension": round(fourier_tension(POOL_BY_SECTION[3],
                                                 POOL_BY_SECTION[0]), 4),
    })

    summary = {
        "method_id": METHOD_ID, "method_name": METHOD_NAME, "layer": LAYER,
        "style": STYLE, "key": KEY_NAME, "root_pc": KEY_ROOT_PC,
        "bpm": BPM, "ticks_per_beat": TPB, "beats_per_bar": BPB,
        "bar_ticks": BAR, "grid": SIXTEENTH, "eighth": EIGHTH,
        "form": "head-solos-head",
        "sections": [{"name": n, "bars": b} for n, b in SECTIONS],
        "total_bars": TOTAL_BARS, "total_ticks": TOTAL_TICKS,
        "spectra": spectra, "tension_curve": tension_curve,
        "voices": [{"name": n, "program": p, "channel": c, "pitched": n in PITCHED_VOICES}
                   for n, p, c in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS)],
        "chord_path": [
            {"bar": i, "roman": CHORDS[i][0], "name": CHORDS[i][1],
             "root_pc": CHORDS[i][2], "chord_tone_pcs": CHORDS[i][3]}
            for i in range(TOTAL_BARS)],
        "vl_violations": len(vl_violations),
        "inline_audit": inline_audit,
        "humanize": {k: {"seed": v["seed"],
                         "profile": v["profile"],
                         "n_notes": v["n_notes"],
                         "mean_abs_shift_ticks": v["mean_abs_shift_ticks"],
                         "max_abs_shift_ticks": v["max_abs_shift_ticks"],
                         "mean_abs_vel_delta": v["mean_abs_vel_delta"]}
                     for k, v in hz.items()},
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    return composer, ok1, inline_audit, vl_violations, len(raw), hz, summary


if __name__ == "__main__":
    composer, ok1, inline_audit, vl_violations, n_raw, hz, summary = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2})"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1})"

    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Phase 1 zero-drift: {ok1}")
    print(f"[OK] Phase 2 zero-drift: True")
    print(f"[OK] Bars: {TOTAL_BARS}, sections: {len(SECTIONS)}")
    print(f"[OK] Raw grain events: {n_raw}")
    print("[OK] Inline grid/harmony audit (pre-humanize):")
    for vname, a in inline_audit.items():
        print(f"     {vname:7s} notes={a['n_notes']:4d} off16={a['off16']} "
              f"off8={a['off8']} out_scale={a['out_scale']} "
              f"out_chord={a['out_chord']}")
    print(f"[OK] Voice-leading violations (rhythm voicings, informational): {len(vl_violations)}")
    print("[OK] Fourier spectra (|f5|, |f7|, |f6|, |f3|, |f4|):")
    for s in range(len(SECTIONS)):
        sp = summary["spectra"][s]
        print(f"     {sp['section']:5s} {sp['pool_name']:38s} "
              f"f5={sp['f5']} f7={sp['f7']} f6={sp['f6']} f3={sp['f3']} f4={sp['f4']}")
    print("[OK] Fourier tension curve:")
    for t in summary["tension_curve"]:
        print(f"     {t['from']:6s} -> {t['to']:20s} tension={t['fourier_tension']}")
    print("[OK] Humanization:")
    for vname, h in hz.items():
        print(f"     {vname:7s} seed={h['seed']} mean_shift={h['mean_abs_shift_ticks']:.1f}t "
              f"max={h['max_abs_shift_ticks']}t vel_delta={h['mean_abs_vel_delta']:.1f}")

    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator=f"Method 113 {METHOD_NAME} - PRE-RULES raw draft (abstract)",
        parameters={"method": METHOD_ID, "phase": 1, "layer": LAYER,
                    "key": KEY_NAME, "bpm": BPM, "sections": len(SECTIONS),
                    "total_bars": TOTAL_BARS, "seed": SEED, "style": STYLE,
                    "form": "head-solos-head"},
        notes="Phase 1 (abstract layer raw): single overdriven-guitar voice, "
              "raw random walk over the per-section Fourier pc-pools. "
              "Unquantized pitch + off-grid micro-timing, NO harmony, off-grid "
              "by design.")
    write_provenance(
        MIDI_PATH, classification=AI_ASSISTED,
        generator=f"Method 113 {METHOD_NAME} + musicom rules",
        parameters={"method": METHOD_ID, "phase": 2, "layer": LAYER,
                    "key": KEY_NAME, "bpm": BPM, "sections": len(SECTIONS),
                    "total_bars": TOTAL_BARS, "seed": SEED, "style": STYLE,
                    "form": "head-solos-head", "voices": VOICES,
                    "humanize_seed": SEED},
        notes="Phase 2 (rules): chord-tone quantization per bar + 16th-grid "
              "onset snap; voice-leading check; full texture (lead arpeggio, "
              "rhythm power chords, bass lock, metal kit); always-on seeded "
              "humanization. Fourier quality trajectory: natural minor (HOME) "
              "-> harmonic minor (LIFT) -> octatonic dim lattice (TENSE) -> "
              "natural minor (HOME).")
    print("[OK] Provenance sidecars written (phase 1 + phase 2).")
