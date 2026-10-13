# -*- coding: utf-8 -*-
"""239 - Een Klein Meisje Rework (Dutch Folk nursery -> 6-section suite)

Rework of source project 029-een-klein-meisje (Dutch Folk / Child Folk
"Kleuterlied"). Source audit: engine FAIL (hand-rolled mido via
live_composer.py / stream_engine.py, inconsistent TPB 10080/480), zero-drift
FAIL (voice tracks 61400/61390/61410), rhythm-grid FAIL (256 off-grid pitched
onsets), track-setup FAIL (3 voice tracks, no drums), two-phase FAIL (no
phase1), provenance FAIL (index.html present but no provenance.json)
-> redesign required.

This rebuild preserves the musical identity (genre=Dutch Folk nursery,
key=G Major, tempo=105, Voice/Guitar/Bass instrumentation + drums, the
I-arpeggio "1-3-5-5-3-1 + 2-3" motif with IV/dominant cadence 4-2-1-5-3-1)
and EXTENDS the form from ~3.5 bars to 24 bars in 6 sections, applying 6
distinct variation techniques.

Two-phase architecture:
  Phase 1: Markov-interval walk over scale degrees (transition table estimated
           from the source melody) -> raw float pitch + jittered eighth-note
           rhythm, single voice, pre-rules.
  Phase 2: musicom rules post-process -> per-bar chord-tone quantization,
           120-tick 16th grid snap, dedup, voice-leading correction,
           per-section harmonic regions (midpoint root), 5-voice arrangement.
"""
import math
import os
import random

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_note_unit, create_chord_unit, create_empty_unit,
)
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# ---------------------------------------------------------------------------
# Project layout
# ---------------------------------------------------------------------------
STYLE_DIR = "/opt/data/projects/Styles/Folk"
PROJECT = "239-een-klein-meisje-rework"
BASE = os.path.join(STYLE_DIR, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

SEED = 20261013
RNG = random.Random(SEED)

# ---------------------------------------------------------------------------
# Concept / identity (preserved from 029)
# ---------------------------------------------------------------------------
BPM = 105
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR          # 1920 ticks/bar
GRID = 120                          # 16th note grid (8th = 240, 16th = 120)
TOTAL_BARS = 24
TOTAL_TICKS = TOTAL_BARS * BAR

TONIC = 67                           # G4
KEY_NAME = "G Major"
KEY_PCS = {7, 9, 11, 0, 2, 4, 6}     # G A B C D E F#

# Scale degrees -> absolute pitches (G4 .. F#5 as the seed octave)
DEG_NOTES = [67, 69, 71, 72, 74, 76, 78]   # 1..7 = G4 A4 B4 C5 D5 E5 F#5


def scale_note(idx):
    """idx = degree-1 (0-indexed, may exceed 6 for higher octaves)."""
    return DEG_NOTES[idx % 7] + (idx // 7) * 12


# ---------------------------------------------------------------------------
# Harmony: diatonic triads on G Major (all chord tones in KEY_PCS)
# ---------------------------------------------------------------------------
CHORD = {
    "I":   (7,  [0, 4, 7], "maj"),   # G   G B D
    "ii":  (9,  [0, 3, 7], "min"),   # Am  A C E
    "iii": (11, [0, 3, 7], "min"),   # Bm  B D F#
    "IV":  (0,  [0, 4, 7], "maj"),   # C   C E G
    "V":   (2,  [0, 4, 7], "maj"),   # D   D F# A
    "vi":  (4,  [0, 3, 7], "min"),   # Em  E G B
    "vii": (6,  [0, 3, 6], "dim"),   # F#dim (unused)
}
CHORD_NAMES = {"I": "G", "ii": "Am", "iii": "Bm", "IV": "C", "V": "D",
               "vi": "Em", "vii": "F#dim"}

# Per-bar chord degree across 24 bars (per-section harmonic regions).
# Each 4-bar section has its OWN short progression; midpoint degrees are
# deliberately varied so sections do NOT all land on tonic.
BAR_DEGREES = [
    # Intro (0-3): tonic region, gentle I IV V I turn
    "I", "IV", "V", "I",
    # A (4-7): identity theme, classic I vi ii V
    "I", "vi", "ii", "V",
    # B (8-11): transposed region (bright lift), vi IV iii V
    "vi", "IV", "iii", "V",
    # A2 (12-15): subdominant region, IV V vi I
    "IV", "V", "vi", "I",
    # C (16-19): dominant tension + density rise, V ii V vi
    "V", "ii", "V", "vi",
    # Outro (20-23): cadence, IV V I I
    "IV", "V", "I", "I",
]

# Sections: (name, bars, variation technique)
SECTIONS = [
    ("Intro", 4, "register_shift_down"),
    ("A",     4, "identity"),
    ("B",     4, "transpose_up_p5"),
    ("A2",    4, "retrograde"),
    ("C",     4, "augment_counterline"),
    ("Outro", 4, "invert_diminish"),
]
SECTION_STARTS = []
_acc = 0
for _name, _bars, _tech in SECTIONS:
    SECTION_STARTS.append(_acc)
    _acc += _bars


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


def snap_chord(pitch, degree, lo=48, hi=84):
    tones = [t for t in chord_tones(degree) if lo <= t <= hi]
    if not tones:
        tones = chord_tones(degree)
    return min(tones, key=lambda t: abs(t - pitch))


def snap_grid(t):
    return int(round(t / float(GRID)) * GRID)


# ---------------------------------------------------------------------------
# Phase 1: Markov-interval walk over scale degrees (raw, unquantized)
# ---------------------------------------------------------------------------
# Transition table estimated empirically from the source melody (28 notes):
#   1,3,5,5,3,1,2,3,1,3,5,5,3,1,2,3,4,2,1,5,3,1,4,2,1,5,3,1
TRANS = {
    1: [3, 3, 2, 2, 5, 5, 4],        # 1->3 x2, 1->2 x2, 1->5 x2, 1->4 x1
    2: [3, 3, 1, 1],                 # 2->3 x2, 2->1 x2
    3: [5, 5, 1, 1, 1, 1, 1, 4],     # 3->5 x2, 3->1 x5, 3->4 x1
    4: [2, 2],                       # 4->2 x2
    5: [5, 5, 3, 3, 3, 3],           # 5->5 x2, 5->3 x4
}


def walk_degrees(rng, start_deg, steps, octave=0):
    """Markov walk over scale degrees with occasional register drift."""
    out = []
    d = start_deg
    octv = octave
    for _ in range(steps):
        out.append((d, octv))
        d = rng.choice(TRANS[d])
        if rng.random() < 0.06:
            octv += rng.choice([-1, 1])
            octv = max(-1, min(1, octv))
    return out


def raw_section(rng, anchor_deg, bars, octave=0):
    """Raw generative draft for one section: float pitch + jittered rhythm."""
    steps = bars * 8
    walk = walk_degrees(rng, anchor_deg, steps, octave=octave)
    events = []
    beat = 0.0
    for (d, octv) in walk:
        if rng.random() < 0.08:            # occasional rest
            beat += 0.5 * rng.uniform(0.8, 1.5)
            continue
        pitch = float(scale_note(d - 1) + 12 * octv) + rng.uniform(-0.4, 0.4)
        dur = 0.5 * rng.uniform(0.8, 1.3)
        events.append({"pitch": pitch, "start": beat, "dur": dur})
        beat += 0.5 * rng.uniform(0.8, 1.6)
        if beat >= bars * 4.0 - 0.25:
            break
    return events


# ---------------------------------------------------------------------------
# Variation transforms (applied to the identity motif -> other sections)
# ---------------------------------------------------------------------------
def transform(raw, kind):
    if kind == "identity":
        return [dict(e) for e in raw]
    if kind == "register_shift_down":
        ev = [{"pitch": e["pitch"] - 12, "start": e["start"], "dur": e["dur"]}
              for e in raw]
        return ev[::2]                       # thin: keep every 2nd onset
    if kind == "transpose_up_p5":
        return [{"pitch": e["pitch"] + 7, "start": e["start"], "dur": e["dur"]}
                for e in raw]
    if kind == "retrograde":
        ps = [e["pitch"] for e in raw][::-1]
        return [{"pitch": ps[i], "start": raw[i]["start"], "dur": raw[i]["dur"]}
                for i in range(len(raw))]
    if kind == "augment_counterline":
        return [{"pitch": e["pitch"], "start": e["start"], "dur": e["dur"] * 2.0}
                for e in raw]
    if kind == "invert_diminish":
        return [{"pitch": 2 * TONIC - e["pitch"], "start": e["start"],
                 "dur": e["dur"] * 0.5} for e in raw]
    return [dict(e) for e in raw]


# ---------------------------------------------------------------------------
# Phase 2: rules post-process
# ---------------------------------------------------------------------------
def process_lead(raw_all):
    """Chord-tone quantization + grid snap + dedup + voice-leading."""
    events = []
    for e in raw_all:
        # Snap start FIRST, then attribute bar by floor(s//BAR) so pitch is
        # always quantized to the bar the note actually lands in (078 fix).
        s = snap_grid(e["start"] * TPB)
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = s // BAR
        bar = max(0, min(TOTAL_BARS - 1, bar))
        degree = BAR_DEGREES[bar]
        p = int(round(e["pitch"]))
        p = snap_chord(p, degree, lo=48, hi=84)
        d = snap_grid(e["dur"] * TPB)
        if d < GRID:
            d = GRID
        end = min(TOTAL_TICKS, s + d)
        if end <= s:
            end = min(TOTAL_TICKS, s + GRID)
        events.append(MusicEvent(pitch=p, volume=92, start_tick=s, end_tick=end))

    # dedup collided (start_tick, pitch) -> keep longest duration
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    events = sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))

    # voice-leading: break parallel perfect 5ths/8ves (stay chord-compliant)
    fixed = []
    for e in events:
        if fixed:
            prev = fixed[-1]
            gap = e.start_tick - prev.end_tick
            if abs(e.pitch - prev.pitch) in (5, 7, 12) and gap < TPB:
                bar = int(e.start_tick // BAR)
                tones = chord_tones(BAR_DEGREES[bar], lo=48, hi=84)
                cands = [t for t in tones
                         if t != e.pitch and abs(t - prev.pitch) not in (5, 7, 12)]
                if cands:
                    e.pitch = min(cands, key=lambda t: abs(t - e.pitch))
        fixed.append(e)
    return fixed


def build_bass_events():
    """Folk oompah: root-fifth-octave-fifth per bar (always chord tones)."""
    events = []
    for bar in range(TOTAL_BARS):
        deg = BAR_DEGREES[bar]
        root_pc, ivs, _q = CHORD[deg]
        root = root_pc + 36
        fifth = root + 7
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root, volume=88,
                                 start_tick=t0, end_tick=t0 + TPB))
        events.append(MusicEvent(pitch=fifth, volume=76,
                                 start_tick=t0 + TPB, end_tick=t0 + TPB * 2))
        events.append(MusicEvent(pitch=root + 12, volume=84,
                                 start_tick=t0 + TPB * 2, end_tick=t0 + TPB * 3))
        events.append(MusicEvent(pitch=fifth, volume=76,
                                 start_tick=t0 + TPB * 3, end_tick=t0 + BAR))
    return events


def build_harmony_events():
    """Acoustic-guitar broken-chord strum on 8th grid (chord tones only)."""
    events = []
    for bar in range(TOTAL_BARS):
        deg = BAR_DEGREES[bar]
        root_pc, ivs, _q = CHORD[deg]
        lo = root_pc + 48
        tones = [lo + iv for iv in ivs]          # close voicing
        root = min(tones)
        third = sorted(tones)[1]
        fifth = max(tones)
        t0 = bar * BAR
        # 8 eighth-slots: root / strum / fifth / strum / root / strum / third / strum
        for slot in range(8):
            t = t0 + slot * (TPB // 2)
            if slot % 2 == 0:
                note = {0: root, 2: fifth, 4: root, 6: third}[slot]
                events.append(MusicEvent(pitch=note, volume=62,
                                         start_tick=t, end_tick=t + TPB // 2))
            else:
                for n in tones:
                    events.append(MusicEvent(pitch=n, volume=56,
                                             start_tick=t, end_tick=t + TPB // 4))
    return events


def build_counter_events():
    """Violin chord-tone arpeggio counterline in C + Outro (density rise)."""
    events = []
    for bar in range(16, TOTAL_BARS):            # sections C (16-19) + Outro (20-23)
        deg = BAR_DEGREES[bar]
        tones = chord_tones(deg, lo=60, hi=88)
        seq = tones + tones[::-1][1:-1]
        t0 = bar * BAR
        t = t0
        i = 0
        while t < t0 + BAR - GRID:
            n = seq[i % len(seq)]
            events.append(MusicEvent(pitch=n, volume=72,
                                     start_tick=t, end_tick=t + GRID))
            t += GRID
            i += 1
    return events


def build_drums_events():
    """Gentle nursery groove: kick 1&3, snare 2&4, 8th hi-hat (channel 9)."""
    events = []
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=88,
                                 start_tick=t0, end_tick=t0 + GRID))
        events.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=70,
                                 start_tick=t0 + TPB, end_tick=t0 + TPB + GRID))
        events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=88,
                                 start_tick=t0 + TPB * 2, end_tick=t0 + TPB * 2 + GRID))
        events.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=70,
                                 start_tick=t0 + TPB * 3, end_tick=t0 + TPB * 3 + GRID))
        for e8 in range(8):
            t = t0 + e8 * (TPB // 2)
            events.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT, volume=42,
                                     start_tick=t, end_tick=t + GRID))
    return events


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
    comp.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    for name, bars, _tech in SECTIONS:
        comp.add_section(name, bars=bars)

    for s_idx, (name, bars, _tech) in enumerate(SECTIONS):
        s_start = SECTION_STARTS[s_idx] * BAR
        s_ticks = bars * BAR
        seg = []
        for e in raw_all:
            st = int(round(e["start"] * TPB))
            if s_start <= st < s_start + s_ticks:
                seg.append(MusicEvent(
                    pitch=int(round(e["pitch"])),
                    volume=int(min(110, max(60, 74 + 24 * abs(e["pitch"] - 62) / 30.0))),
                    start_tick=st,
                    end_tick=int(round((e["start"] + e["dur"]) * TPB))))
        for ev in seg:
            if ev.pitch < 36:
                ev.pitch = 36
            if ev.pitch > 96:
                ev.pitch = 96
        comp.fill_voice_section("Lead", name,
                                MusicUnit(events=rel_events(seg, s_start, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


def build_phase2(lead_events, counter_events, harmony_events, bass_events,
                 drums_events):
    """Phase 2: 5-voice rules-processed arrangement, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=53, channel=0)                     # Choir Aahs
    comp.add_voice("Counter", program=MidiInstrument.VIOLIN, channel=1)
    comp.add_voice("Harmony", program=MidiInstrument.ACOUSTIC_GUITAR, channel=2)
    comp.add_voice("Bass", program=MidiInstrument.BASS, channel=3)
    comp.add_voice("Drums", program=0, channel=9)

    for name, bars, _tech in SECTIONS:
        comp.add_section(name, bars=bars)

    voice_event_map = {
        "Lead": lead_events,
        "Counter": counter_events,
        "Harmony": harmony_events,
        "Bass": bass_events,
        "Drums": drums_events,
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
<html><head><meta charset="utf-8"><title>239 Een Klein Meisje Rework</title>
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
<h1>239 &mdash; Een Klein Meisje Rework</h1>
<p class="mono">G Major &middot; 105 BPM &middot; 4/4 &middot; 24 bars &middot; 6 sections &middot; Dutch Folk nursery</p>
<div class="card"><h2>Form &amp; Variation</h2>
<table><tr><td class="td">Intro</td><td class="td">4b</td><td class="td">register shift &minus;12 + thin</td></tr>
<tr><td class="td">A</td><td class="td">4b</td><td class="td">identity (I-arpeggio motif)</td></tr>
<tr><td class="td">B</td><td class="td">4b</td><td class="td">transposition +P5 (bright lift)</td></tr>
<tr><td class="td">A2</td><td class="td">4b</td><td class="td">retrograde (contour reversed)</td></tr>
<tr><td class="td">C</td><td class="td">4b</td><td class="td">augmentation + counterline</td></tr>
<tr><td class="td">Outro</td><td class="td">4b</td><td class="td">inversion + diminution &rarr; cadence</td></tr>
</table></div>
<div class="card"><h2>Rhythm DNA (nursery 8th-note lilt)</h2>
<p class="mono grid"><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span><span class="on">&#9608;</span><span class="off">&#9617;</span></p></div>
<div class="card"><h2>Harmonic regions (per-section midpoint root)</h2>
<table><tr><td class="td">Intro</td><td class="td">V (D)</td></tr>
<tr><td class="td">A</td><td class="td">ii (Am)</td></tr>
<tr><td class="td">B</td><td class="td">iii (Bm)</td></tr>
<tr><td class="td">A2</td><td class="td">vi (Em)</td></tr>
<tr><td class="td">C</td><td class="td">V (D)</td></tr>
<tr><td class="td">Outro</td><td class="td">I (G)</td></tr></table></div>
<div class="card"><h2>Artifacts</h2>
<p><a href="MIDI/239-een-klein-meisje-rework.mid">phase2 MIDI</a> &middot;
<a href="MIDI/239-een-klein-meisje-rework-phase1.mid">phase1 MIDI</a> &middot;
<a href="Audio/239-een-klein-meisje-rework.ogg">audio (OGG)</a></p></div>
</body></html>"""
    with open(os.path.join(BASE, "index.html"), "w") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # ---- Phase 1: raw Markov-interval draft (single voice) -----------------
    A_raw = raw_section(RNG, anchor_deg=1, bars=4, octave=0)

    section_raw = {}
    section_raw["Intro"] = transform(A_raw, "register_shift_down")
    section_raw["A"] = transform(A_raw, "identity")
    section_raw["B"] = transform(A_raw, "transpose_up_p5")
    section_raw["A2"] = transform(A_raw, "retrograde")
    section_raw["C"] = transform(A_raw, "augment_counterline")
    section_raw["Outro"] = transform(A_raw, "invert_diminish")

    raw_all = []
    for s_idx, (name, bars, _tech) in enumerate(SECTIONS):
        sec_start = SECTION_STARTS[s_idx]
        for e in section_raw[name]:
            raw_all.append({
                "pitch": e["pitch"],
                "start": e["start"] + sec_start * 4.0,
                "dur": e["dur"],
            })

    phase1 = build_phase1(raw_all)
    phase1_mid = os.path.join(MIDI_DIR, "239-een-klein-meisje-rework-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(phase1_mid, AI_ASSISTED,
                     "musicom.method.markov_interval_walk_phase1 (rework of 029)",
                     sources=["source:029-een-klein-meisje (Dutch Folk nursery)",
                              "methods_db.md:Markov interval walk"],
                     parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": SEED,
                                 "phase": 1, "quantized": False,
                                 "key": KEY_NAME, "form": "6 sections (extended)"},
                     notes="Raw Markov interval walk over G-major scale degrees "
                           "(transition table estimated from source melody), "
                           "unquantized, single voice, pre-rules. Rework of 029 "
                           "(redesign: source failed engine + zero-drift + grid + "
                           "tracks + two-phase + provenance).")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
                             voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2: rules post-process (5 voices) ----------------------------
    lead_ev = process_lead(raw_all)
    counter_ev = build_counter_events()
    harmony_ev = build_harmony_events()
    bass_ev = build_bass_events()
    drums_ev = build_drums_events()

    phase2 = build_phase2(lead_ev, counter_ev, harmony_ev, bass_ev, drums_ev)
    phase2_mid = os.path.join(MIDI_DIR, "239-een-klein-meisje-rework.mid")
    phase2.to_midi(phase2_mid)
    write_provenance(phase2_mid, AI_ASSISTED,
                     "musicom.method.markov_interval_walk_phase2 + musicom rules (rework of 029)",
                     sources=["source:029-een-klein-meisje (Dutch Folk nursery)",
                              "methods_db.md:Markov interval walk"],
                     parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": SEED,
                                 "phase": 2, "quantized": True,
                                 "key": KEY_NAME, "rhythm": "nursery 8th-note lilt",
                                 "form": "6 sections (extended)",
                                 "variation_techniques": [
                                     "register_shift_down", "transposition_P5",
                                     "retrograde", "augmentation+counterline",
                                     "inversion+diminution"]},
                     notes="Rules post-process: per-bar chord-tone quantization, "
                           "120-tick grid snap, dedup, voice-leading, per-section "
                           "harmonic regions (midpoint root).")
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=["Lead", "Counter", "Harmony", "Bass",
                                          "Drums"], bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, phase2_mid):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    write_dashboard()

    roots = section_roots()
    print("PHASE1_MID:", phase1_mid, os.path.getsize(phase1_mid))
    print("PHASE2_MID:", phase2_mid, os.path.getsize(phase2_mid))
    print("SECTIONS:", len(SECTIONS), "BARS:", TOTAL_BARS)
    print("SECTION_ROOTS:", roots)
    print("LEAD_EVENTS:", len(lead_ev), "COUNTER:", len(counter_ev),
          "HARMONY:", len(harmony_ev), "BASS:", len(bass_ev),
          "DRUMS:", len(drums_ev))


if __name__ == "__main__":
    main()
