# -*- coding: utf-8 -*-
"""241 - Soul Voice-Leading Graph Rework (D minor, 92 BPM, 8 sections = 32 bars).

Rework of source project 084-soul-voiceleading-graph (Soul, Method 011
Voice-Leading Graph Search). Source audit: engine FAIL (compose_084.py gone,
no engine-evidence in repo), provenance+index FAIL (no root provenance.json,
no index.html). Zero-drift / grid / tracks / two-phase all PASS on the
existing MIDI, but the authoring script + sidecars are missing
-> redesign required (rebuild through canonical UnitMatrixComposer).

Identity preserved: genre=Soul, key=D minor (aeolian), tempo=92 BPM,
TenorSax/Rhodes/Violin/Guitar/Bass/Drums instrumentation, the D-aeolian
progression vocabulary (i iv VI VII / III VII), and Method 011's weighted
random walk over a tonal-function graph as the generative core.

Extended from 24 to 32 bars (8 sections), applying 6 distinct variation
techniques (register-shift, transposition, retrograde, augmentation,
inversion, diminution) + identity + recapitulation.

Two-phase architecture:
  Phase 1: weighted tonal-function-graph walk -> raw degree + fractional-tick
           rhythm (off-grid, out-of-chord by design), single voice.
  Phase 2: musicom rules post-process -> 120-tick grid snap, per-bar chord-tone
           quantization (floor t//BAR), dedup, leap-cap voice-leading,
           per-section harmonic regions (midpoint root), 6-voice arrangement.
"""
import itertools
import json
import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# ---------------------------------------------------------------------------
# Project layout
# ---------------------------------------------------------------------------
STYLE_DIR = "/opt/data/projects/Styles/Soul"
PROJECT = "241-soul-voiceleading-graph-rework"
BASE = os.path.join(STYLE_DIR, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

SEED = 20261014
RNG = random.Random(SEED)

# ---------------------------------------------------------------------------
# Concept / identity (preserved from 084)
# ---------------------------------------------------------------------------
BPM = 92
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR          # 1920 ticks/bar
GRID = 120                          # 16th-note grid (8th = 240, 16th = 120)
TOTAL_BARS = 32
TOTAL_TICKS = TOTAL_BARS * BAR

TONIC = 62                           # D4 (pc 2)
KEY_NAME = "D minor (aeolian)"
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}     # D E F G A Bb C

# Scale degree 1..7 -> MIDI pitch (D4 E4 F4 G4 A4 Bb4 C5)
DEG_NOTES = [62, 64, 65, 67, 69, 70, 72]


def scale_note(idx):
    """idx = degree-1 (0-indexed); may exceed 6 for higher octaves."""
    return DEG_NOTES[idx % 7] + (idx // 7) * 12


# ---------------------------------------------------------------------------
# Harmony: diatonic triads on D aeolian (all chord tones in KEY_PCS)
# ---------------------------------------------------------------------------
CHORD = {
    "i":   (2,  [0, 3, 7], "min"),   # Dm    D F A
    "ii":  (4,  [0, 3, 6], "dim"),   # Edim  E G Bb
    "III": (5,  [0, 4, 7], "maj"),   # F     F A C
    "iv":  (7,  [0, 3, 7], "min"),   # Gm    G Bb D
    "v":   (9,  [0, 3, 7], "min"),   # Am    A C E
    "VI":  (10, [0, 4, 7], "maj"),   # Bb    Bb D F
    "VII": (0,  [0, 4, 7], "maj"),   # C     C E G
}
CHORD_NAMES = {"i": "Dm", "ii": "Edim", "III": "F", "iv": "Gm", "v": "Am",
               "VI": "Bb", "VII": "C"}

# Per-bar chord degree across 32 bars (per-section harmonic regions).
BAR_DEGREES = [
    # Intro (0-3): i VI iv VII
    "i", "VI", "iv", "VII",
    # Verse (4-7): i III VII iv
    "i", "III", "VII", "iv",
    # Chorus (8-11): III VII VI VII
    "III", "VII", "VI", "VII",
    # Bridge (12-15): iv v III VI
    "iv", "v", "III", "VI",
    # Verse2 (16-19): i iv VI VII
    "i", "iv", "VI", "VII",
    # Chorus2 (20-23): III VII VI VII
    "III", "VII", "VI", "VII",
    # Break (24-27): v iv III VII
    "v", "iv", "III", "VII",
    # Outro (28-31): iv v i i
    "iv", "v", "i", "i",
]
assert len(BAR_DEGREES) == TOTAL_BARS

# Sections: (name, bars, variation technique)
SECTIONS = [
    ("Intro",   4, "register_shift_down_thin"),
    ("Verse",   4, "identity"),
    ("Chorus",  4, "transpose_up_m3"),
    ("Bridge",  4, "retrograde"),
    ("Verse2",  4, "augmentation"),
    ("Chorus2", 4, "inversion_density_rise"),
    ("Break",   4, "diminution"),
    ("Outro",   4, "recapitulation"),
]
SECTION_STARTS = []
_acc = 0
for _name, _bars, _tech in SECTIONS:
    SECTION_STARTS.append(_acc)
    _acc += _bars

ARPEGGIO_SECTIONS = {"Chorus", "Chorus2", "Break"}   # violin counterline


def section_roots():
    """Midpoint-chord roots per section (NOT bar-0, avoids all-i bug)."""
    out = []
    for idx, (name, bars, _tech) in enumerate(SECTIONS):
        s = SECTION_STARTS[idx]
        mid = s + bars // 2
        deg = BAR_DEGREES[mid]
        root_pc, _iv, qual = CHORD[deg]
        out.append((name, CHORD_NAMES[deg], root_pc, qual, deg))
    return out


def chord_tones(degree, lo=36, hi=96):
    root_pc, ivs, _q = CHORD[degree]
    tones = set()
    for octv in range(-2, 9):
        base = root_pc + 12 * octv
        for iv in ivs:
            n = base + iv
            if lo <= n <= hi:
                tones.add(n)
    return sorted(tones)


def chord_pcs(degree):
    root_pc, ivs, _q = CHORD[degree]
    return {(root_pc + iv) % 12 for iv in ivs}


def pitch_in(pc, lo, hi, center=None):
    """MIDI pitch with pitch-class pc inside [lo,hi], nearest center."""
    center = center if center is not None else (lo + hi) // 2
    best, bestd = None, None
    for k in range(0, 12):
        n = pc + 12 * k
        if n > hi:
            break
        if lo <= n <= hi:
            d = abs(n - center)
            if bestd is None or d < bestd:
                bestd, best = d, n
    for k in range(-1, -13, -1):
        n = pc + 12 * k
        if n < lo:
            break
        if lo <= n <= hi:
            d = abs(n - center)
            if bestd is None or d < bestd:
                bestd, best = d, n
    return best


def snap_chord(pitch, degree, lo=48, hi=84):
    tones = [t for t in chord_tones(degree) if lo <= t <= hi]
    if not tones:
        tones = chord_tones(degree)
    return min(tones, key=lambda t: abs(t - pitch))


def snap_grid(t):
    return int(round(t / float(GRID)) * GRID)


# ---------------------------------------------------------------------------
# Phase 1: weighted random walk over a tonal-function graph (Method 011)
# ---------------------------------------------------------------------------
# Weighted directed graph over scale degrees 1..7 (D aeolian), biased toward
# stepwise + chord-tone motion (soul gravity toward 1/3/5).
GRAPH = {
    1: [(2, 3), (3, 2), (4, 2), (5, 2), (6, 1)],   # D -> E,F,G,A,Bb
    2: [(1, 3), (3, 2), (4, 1), (5, 1)],           # E -> D,F,G,A
    3: [(1, 2), (2, 2), (4, 2), (5, 1)],           # F -> D,E,G,A
    4: [(1, 2), (2, 1), (3, 2), (5, 2), (7, 1)],   # G -> D,E,F,A,C
    5: [(1, 2), (3, 1), (4, 2), (6, 1), (7, 1)],   # A -> D,F,G,Bb,C
    6: [(1, 1), (4, 1), (5, 1), (7, 2)],           # Bb -> D,G,A,C
    7: [(1, 2), (2, 1), (6, 2), (5, 1)],           # C -> D,E,Bb,A
}


def graph_step(rng, d):
    opts, wts = zip(*GRAPH[d])
    return rng.choices(opts, weights=wts, k=1)[0]


def raw_section(rng, anchor_deg, bars, octave=0):
    """Raw generative draft: degree walk + fractional-tick rhythm (off-grid)."""
    steps = bars * 8
    events = []
    d = anchor_deg
    octv = octave
    beat = 0.0
    for _ in range(steps):
        if rng.random() < 0.08:            # occasional rest
            beat += 0.5 * rng.uniform(0.8, 1.5)
            continue
        dur = 0.5 * rng.uniform(0.8, 1.3)
        events.append({"deg": d, "oct": octv, "start": beat, "dur": dur})
        d = graph_step(rng, d)
        if rng.random() < 0.05:            # rare register drift
            octv += rng.choice([-1, 1])
            octv = max(-1, min(1, octv))
        beat += 0.5 * rng.uniform(0.8, 1.6)
        if beat >= bars * 4.0 - 0.25:
            break
    return events


# ---------------------------------------------------------------------------
# Variation transforms (degree-based -> always diatonic)
# ---------------------------------------------------------------------------
def transform(raw, kind):
    if kind == "identity":
        return [dict(e) for e in raw]
    if kind == "register_shift_down_thin":
        return [{"deg": e["deg"], "oct": e["oct"] - 1,
                 "start": e["start"], "dur": e["dur"]} for e in raw][::2]
    if kind == "transpose_up_m3":
        # diatonic up a minor 3rd = +2 scale steps (D -> F, the relative major)
        return [{"deg": ((e["deg"] - 1 + 2) % 7) + 1, "oct": e["oct"],
                 "start": e["start"], "dur": e["dur"]} for e in raw]
    if kind == "retrograde":
        rev = list(reversed(raw))
        return [{"deg": rev[i]["deg"], "oct": rev[i]["oct"],
                 "start": raw[i]["start"], "dur": raw[i]["dur"]}
                for i in range(len(raw))]
    if kind == "augmentation":
        return [{"deg": e["deg"], "oct": e["oct"],
                 "start": e["start"], "dur": e["dur"] * 2.0} for e in raw]
    if kind == "inversion_density_rise":
        # diatonic inversion around degree 1 (tonic): d -> 8 - d
        return [{"deg": 8 - e["deg"], "oct": e["oct"],
                 "start": e["start"], "dur": e["dur"]} for e in raw]
    if kind == "diminution":
        return [{"deg": e["deg"], "oct": e["oct"],
                 "start": e["start"], "dur": e["dur"] * 0.5} for e in raw]
    if kind == "recapitulation":
        return [dict(e) for e in raw]
    return [dict(e) for e in raw]


def raw_pitch(e):
    return scale_note(e["deg"] - 1) + 12 * e["oct"]


# ---------------------------------------------------------------------------
# Phase 2: rules post-process
# ---------------------------------------------------------------------------
def process_lead(raw_all):
    """Chord-tone quantization + grid snap + leap-cap + dedup."""
    events = []
    for e in raw_all:
        s = snap_grid(e["start"] * TPB)
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = s // BAR
        bar = max(0, min(TOTAL_BARS - 1, bar))
        degree = BAR_DEGREES[bar]
        p = int(round(raw_pitch(e)))
        p = snap_chord(p, degree, lo=48, hi=84)
        d = snap_grid(e["dur"] * TPB)
        if d < GRID:
            d = GRID
        end = min(TOTAL_TICKS, s + d)
        if end <= s:
            end = min(TOTAL_TICKS, s + GRID)
        events.append(MusicEvent(pitch=p, volume=92, start_tick=s, end_tick=end))

    events.sort(key=lambda ev: (ev.start_tick, ev.pitch))

    # leap-cap voice-leading: keep consecutive melodic leaps <= 12 semitones,
    # re-snapping to the note's OWN bar chord tone (stays chord-compliant).
    for i in range(1, len(events)):
        prev = events[i - 1]
        if abs(events[i].pitch - prev.pitch) > 12:
            bar = events[i].start_tick // BAR
            tones = chord_tones(BAR_DEGREES[bar], lo=48, hi=84)
            cands = [t for t in tones if abs(t - prev.pitch) <= 12]
            if cands:
                events[i].pitch = min(cands, key=lambda t: abs(t - prev.pitch))

    # dedup collided (start_tick, pitch) -> keep longest duration
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    return sorted(best.values(), key=lambda ev: (ev.start_tick, ev.pitch))


def min_motion_voicings(lo=55, hi=72):
    """Violin triad pad: greedy min-motion voice-leading across 32 bars."""
    voicings = []
    prev = None
    for deg in BAR_DEGREES:
        root_pc, ivs, _q = CHORD[deg]
        pcs = [(root_pc + iv) % 12 for iv in ivs]
        if prev is None:
            v = sorted(set(pitch_in(p, lo, hi) for p in pcs))
            while len(v) < 3:
                v.append(v[-1] + 12)
            v = v[:3]
        else:
            best, bestd = None, None
            for perm in itertools.permutations(pcs):
                cand = [pitch_in(perm[j], lo, hi, center=prev[j]) for j in range(3)]
                if any(c is None for c in cand) or len(set(cand)) < 3:
                    continue
                d = sum(abs(prev[j] - cand[j]) for j in range(3))
                if bestd is None or d < bestd:
                    bestd, best = d, sorted(cand)
            if best is None:
                best = sorted(set(pitch_in(p, lo, hi) for p in pcs))
                while len(best) < 3:
                    best.append(best[-1] + 12)
                best = best[:3]
            v = sorted(best)
        voicings.append(v)
        prev = v
    return voicings


def build_rhodes():
    """Rhodes offbeat 8th comp — chord stabs on the 'and' of each beat."""
    events = []
    for bar in range(TOTAL_BARS):
        deg = BAR_DEGREES[bar]
        root_pc, ivs, _q = CHORD[deg]
        tones = sorted(set(pitch_in((root_pc + iv) % 12, 55, 76) for iv in ivs))
        t0 = bar * BAR
        for off in (240, 720, 1200, 1680):
            for n in tones:
                events.append(MusicEvent(pitch=n, volume=64,
                                         start_tick=t0 + off,
                                         end_tick=t0 + off + 240))
    return events


def build_violin(voicings):
    """Triad pad (min-motion) in non-chorus sections; 8th-note chord-tone
    arpeggio counterline in Chorus/Chorus2/Break (density rise)."""
    events = []
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        name = SECTIONS[sec][0]
        deg = BAR_DEGREES[bar]
        t0 = bar * BAR
        if name not in ARPEGGIO_SECTIONS:
            v = voicings[bar]
            for p in v:
                events.append(MusicEvent(pitch=p, volume=70,
                                         start_tick=t0, end_tick=t0 + BAR))
        else:
            tones = chord_tones(deg, lo=60, hi=88)
            seq = tones + tones[::-1][1:-1]
            t = t0
            i = 0
            while t < t0 + BAR - 240:
                events.append(MusicEvent(pitch=seq[i % len(seq)], volume=74,
                                         start_tick=t, end_tick=t + 240))
                t += 240
                i += 1
    return events


def build_guitar():
    """Acoustic-guitar 8th strum (root/strum/fifth/strum/root/strum/third/strum)."""
    events = []
    for bar in range(TOTAL_BARS):
        deg = BAR_DEGREES[bar]
        root_pc, ivs, _q = CHORD[deg]
        lo = root_pc + 48
        tones = [lo + iv for iv in ivs]
        root = min(tones)
        third = sorted(tones)[1]
        fifth = max(tones)
        t0 = bar * BAR
        for slot in range(8):
            t = t0 + slot * 240
            if slot % 2 == 0:
                note = {0: root, 2: fifth, 4: root, 6: third}[slot]
                events.append(MusicEvent(pitch=note, volume=62,
                                         start_tick=t, end_tick=t + 240))
            else:
                for n in tones:
                    events.append(MusicEvent(pitch=n, volume=54,
                                             start_tick=t, end_tick=t + 120))
    return events


def build_bass():
    """Electric bass root-fifth-octave-fifth pulse (all chord tones)."""
    events = []
    for bar in range(TOTAL_BARS):
        deg = BAR_DEGREES[bar]
        root_pc, _ivs, _q = CHORD[deg]
        root = root_pc + 36
        fifth = root + 7
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root, volume=90,
                                 start_tick=t0, end_tick=t0 + 480))
        events.append(MusicEvent(pitch=fifth, volume=78,
                                 start_tick=t0 + 480, end_tick=t0 + 960))
        events.append(MusicEvent(pitch=root + 12, volume=86,
                                 start_tick=t0 + 960, end_tick=t0 + 1440))
        events.append(MusicEvent(pitch=fifth, volume=78,
                                 start_tick=t0 + 1440, end_tick=t0 + BAR))
    return events


def build_drums():
    """Soul backbeat: kick 1&3, snare 2&4, 8th hats, claps in choruses."""
    events = []
    for bar in range(TOTAL_BARS):
        sec = section_of_bar(bar)
        name = SECTIONS[sec][0]
        t0 = bar * BAR
        events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=92,
                                 start_tick=t0, end_tick=t0 + GRID))
        events.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=72,
                                 start_tick=t0 + 480, end_tick=t0 + 480 + GRID))
        events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=92,
                                 start_tick=t0 + 960, end_tick=t0 + 960 + GRID))
        events.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=72,
                                 start_tick=t0 + 1440, end_tick=t0 + 1440 + GRID))
        for e8 in range(8):
            t = t0 + e8 * 240
            events.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT, volume=44,
                                     start_tick=t, end_tick=t + GRID))
        if name in ("Chorus", "Chorus2"):
            for b in (1, 3):
                events.append(MusicEvent(pitch=MidiPercussion.HAND_CLAP, volume=68,
                                         start_tick=t0 + b * 480,
                                         end_tick=t0 + b * 480 + GRID))
    return events


def section_of_bar(bar):
    sec = 0
    for s in range(len(SECTIONS)):
        if bar >= SECTION_STARTS[s]:
            sec = s
    return sec


# ---------------------------------------------------------------------------
# Matrix helpers
# ---------------------------------------------------------------------------
def rel_events(abs_events, s_start, s_len):
    """Absolute -> relative ticks for one section cell + terminal landmark."""
    out = []
    for e in abs_events:
        s = e.start_tick - s_start
        en = e.end_tick - s_start
        if en <= 0 or s >= s_len:
            continue
        s = max(0, s)
        en = min(s_len, en)
        if en <= s:
            en = min(s_len, s + GRID)
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=s, end_tick=en))
    if not out or max(e.end_tick for e in out) < s_len:
        out.append(MusicEvent(pitch=0, volume=0,
                              start_tick=s_len - 10, end_tick=s_len))
    return out


def build_phase1(raw_all):
    """Phase 1: single voice (Lead), raw unquantized units, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=66, channel=0)      # Tenor Sax
    for name, bars, _tech in SECTIONS:
        comp.add_section(name, bars=bars)

    for s_idx, (name, bars, _tech) in enumerate(SECTIONS):
        s_start = SECTION_STARTS[s_idx] * BAR
        s_ticks = bars * BAR
        seg = []
        for e in raw_all:
            st = int(round(e["start"] * TPB))
            if s_start <= st < s_start + s_ticks:
                pitch = int(round(raw_pitch(e) + RNG.uniform(-0.3, 0.3)))
                pitch = max(36, min(96, pitch))
                seg.append(MusicEvent(
                    pitch=pitch,
                    volume=int(min(110, max(60, 74 + 24 * abs(pitch - 62) / 30.0))),
                    start_tick=st,
                    end_tick=int(round((e["start"] + e["dur"]) * TPB))))
        comp.fill_voice_section("Lead", name,
                                MusicUnit(events=rel_events(seg, s_start, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


def build_phase2(lead_events, rhodes_events, violin_events, guitar_events,
                 bass_events, drums_events):
    """Phase 2: 6-voice rules-processed arrangement, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=6, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=66, channel=0)                        # Tenor Sax
    comp.add_voice("Rhodes", program=4, channel=1)                       # E. Piano 1
    comp.add_voice("Violin", program=MidiInstrument.VIOLIN, channel=2)
    comp.add_voice("Guitar", program=MidiInstrument.ACOUSTIC_GUITAR, channel=3)
    comp.add_voice("Bass", program=MidiInstrument.BASS, channel=4)
    comp.add_voice("Drums", program=0, channel=9)

    for name, bars, _tech in SECTIONS:
        comp.add_section(name, bars=bars)

    voice_event_map = {
        "Lead": lead_events, "Rhodes": rhodes_events, "Violin": violin_events,
        "Guitar": guitar_events, "Bass": bass_events, "Drums": drums_events,
    }

    for s_idx, (name, bars, _tech) in enumerate(SECTIONS):
        s_start = SECTION_STARTS[s_idx] * BAR
        s_ticks = bars * BAR
        for vname, all_ev in voice_event_map.items():
            seg = [e for e in all_ev if s_start <= e.start_tick < s_start + s_ticks]
            comp.fill_voice_section(vname, name,
                                    MusicUnit(events=rel_events(seg, s_start, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# index.html dashboard (VoltAgent styling)
# ---------------------------------------------------------------------------
def write_dashboard():
    html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>241 Soul Voice-Leading Graph Rework</title>
<style>
body{background:#050507;color:#e5e7eb;font-family:system-ui;margin:0;padding:40px}
h1{font-size:60px;line-height:1.0;color:#00d992;margin:0 0 8px}
.mono{font-family:'JetBrains Mono',monospace}
.grid{display:inline-block;line-height:1.15;letter-spacing:2px}
.on{color:#00d992}.off{color:#2a2a2e}
.card{background:#101010;border:1px solid #1c1c1c;border-radius:12px;padding:20px;margin:16px 0}
table{border-collapse:collapse}.td{padding:6px 14px;border-bottom:1px solid #1c1c1c}
a{color:#00d992}
</style></head><body>
<h1>241 &mdash; Soul Voice-Leading Graph Rework</h1>
<p class="mono">D minor &middot; 92 BPM &middot; 4/4 &middot; 32 bars &middot; 8 sections &middot; Soul</p>
<div class="card"><h2>Form &amp; Variation</h2>
<table>
<tr><td class="td">Intro</td><td class="td">4b</td><td class="td">register shift &minus;12 + thin</td></tr>
<tr><td class="td">Verse</td><td class="td">4b</td><td class="td">identity (graph-walk motif)</td></tr>
<tr><td class="td">Chorus</td><td class="td">4b</td><td class="td">transposition +m3 (to relative major)</td></tr>
<tr><td class="td">Bridge</td><td class="td">4b</td><td class="td">retrograde (contour reversed)</td></tr>
<tr><td class="td">Verse2</td><td class="td">4b</td><td class="td">augmentation &times;2</td></tr>
<tr><td class="td">Chorus2</td><td class="td">4b</td><td class="td">inversion + density rise</td></tr>
<tr><td class="td">Break</td><td class="td">4b</td><td class="td">diminution &times;0.5</td></tr>
<tr><td class="td">Outro</td><td class="td">4b</td><td class="td">recapitulation &rarr; cadence</td></tr>
</table></div>
<div class="card"><h2>Rhythm DNA (soul backbeat 8th)</h2>
<p class="mono grid"><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span></p></div>
<div class="card"><h2>Harmonic regions (per-section midpoint root)</h2>
<table>
<tr><td class="td">Intro</td><td class="td">iv (Gm)</td></tr>
<tr><td class="td">Verse</td><td class="td">VII (C)</td></tr>
<tr><td class="td">Chorus</td><td class="td">VI (Bb)</td></tr>
<tr><td class="td">Bridge</td><td class="td">III (F)</td></tr>
<tr><td class="td">Verse2</td><td class="td">VI (Bb)</td></tr>
<tr><td class="td">Chorus2</td><td class="td">VI (Bb)</td></tr>
<tr><td class="td">Break</td><td class="td">III (F)</td></tr>
<tr><td class="td">Outro</td><td class="td">i (Dm)</td></tr></table></div>
<div class="card"><h2>Artifacts</h2>
<p><a href="MIDI/241-soul-voiceleading-graph-rework.mid">phase2 MIDI</a> &middot;
<a href="MIDI/241-soul-voiceleading-graph-rework-phase1.mid">phase1 MIDI</a> &middot;
<a href="Audio/241-soul-voiceleading-graph-rework.ogg">audio (OGG)</a></p></div>
</body></html>"""
    with open(os.path.join(BASE, "index.html"), "w") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    A_raw = raw_section(RNG, anchor_deg=1, bars=4, octave=0)

    section_raw = {name: transform(A_raw, tech) for name, _b, tech in SECTIONS}

    raw_all = []
    for s_idx, (name, bars, _tech) in enumerate(SECTIONS):
        sec_start = SECTION_STARTS[s_idx]
        for e in section_raw[name]:
            raw_all.append({
                "deg": e["deg"], "oct": e["oct"],
                "start": e["start"] + sec_start * 4.0, "dur": e["dur"],
            })

    # ---- Phase 1: raw weighted-graph draft (single voice) -----------------
    phase1 = build_phase1(raw_all)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(phase1_mid, AI_ASSISTED,
                     "musicom.method.011_voiceleading_graph_walk_phase1 (rework of 084)",
                     sources=["source:084-soul-voiceleading-graph (Soul, Method 011)",
                              "methods_db.md:Voice-Leading Graph Search"],
                     parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": SEED,
                                 "phase": 1, "quantized": False, "key": KEY_NAME,
                                 "form": "8 sections (extended from 6)"},
                     notes="Raw weighted walk over a D-aeolian tonal-function graph "
                           "(weighted degree transitions biased to chord tones), "
                           "fractional-tick rhythm, single voice, pre-rules. Rework "
                           "of 084 (redesign: source compose.py missing + no "
                           "provenance/index).")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
                             voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2: rules post-process (6 voices) ---------------------------
    lead_ev = process_lead(raw_all)
    voicings = min_motion_voicings()
    rhodes_ev = build_rhodes()
    violin_ev = build_violin(voicings)
    guitar_ev = build_guitar()
    bass_ev = build_bass()
    drums_ev = build_drums()

    phase2 = build_phase2(lead_ev, rhodes_ev, violin_ev, guitar_ev, bass_ev, drums_ev)
    phase2_mid = os.path.join(MIDI_DIR, PROJECT + ".mid")
    phase2.to_midi(phase2_mid)
    write_provenance(phase2_mid, AI_ASSISTED,
                     "musicom.method.011_voiceleading_graph_walk_phase2 + musicom rules (rework of 084)",
                     sources=["source:084-soul-voiceleading-graph (Soul, Method 011)",
                              "methods_db.md:Voice-Leading Graph Search"],
                     parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": SEED,
                                 "phase": 2, "quantized": True, "key": KEY_NAME,
                                 "rhythm": "soul backbeat 8th", "form": "8 sections (extended)",
                                 "variation_techniques": [
                                     "register_shift_down_thin", "transposition_up_m3",
                                     "retrograde", "augmentation", "inversion_density_rise",
                                     "diminution", "recapitulation"]},
                     notes="Rules post-process: per-bar chord-tone quantization "
                           "(floor t//BAR), 120-tick grid snap, dedup, leap-cap "
                           "voice-leading, per-section harmonic regions (midpoint "
                           "root), min-motion violin pad + chorus counterline.")
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=["Lead", "Rhodes", "Violin", "Guitar",
                                          "Bass", "Drums"], bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, phase2_mid):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    write_dashboard()

    roots = section_roots()
    summary = {
        "project": PROJECT, "source": "084-soul-voiceleading-graph",
        "key": KEY_NAME, "key_pcs": sorted(KEY_PCS), "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [{"name": n, "bars": b, "technique": t}
                                         for n, b, t in SECTIONS],
        "bar_degrees": BAR_DEGREES,
        "section_roots": [{"name": n, "chord": c, "root_pc": r, "quality": q}
                          for n, c, r, q, _ in roots],
        "variation_techniques": ["register_shift_down_thin", "transposition_up_m3",
                                 "retrograde", "augmentation", "inversion_density_rise",
                                 "diminution", "recapitulation"],
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print("PHASE1_MID:", phase1_mid, os.path.getsize(phase1_mid))
    print("PHASE2_MID:", phase2_mid, os.path.getsize(phase2_mid))
    print("SECTIONS:", len(SECTIONS), "BARS:", TOTAL_BARS)
    print("SECTION_ROOTS:", roots)
    print("EVENTS lead=%d rhodes=%d violin=%d guitar=%d bass=%d drums=%d" %
          (len(lead_ev), len(rhodes_ev), len(violin_ev), len(guitar_ev),
           len(bass_ev), len(drums_ev)))


if __name__ == "__main__":
    main()
