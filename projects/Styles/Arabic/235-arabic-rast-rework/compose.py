# -*- coding: utf-8 -*-
"""235 - Arabic Rast Rework (Ant-Colony DNA -> extended 6-section suite)

Rework of source project 071-arabic-rast-ant-colony (Arabic / Rast maqam /
maqsum rhythm / Method 041 ACOPF). Source audit: engine-authored PASS,
zero-drift PASS, 5-voice PASS, two-phase PASS, but rhythm-grid sync FAIL
(32 off-grid pitched onsets) and provenance.json + index.html MISSING
-> redesign required.

This rebuild preserves the musical identity (genre=Arabic, key=D Rast
approx = D Phrygian on 12-TET grid, tempo=100, flute-lead + strings + bass +
pad + drums instrumentation, ant-colony generative method) and EXTENDS the
form from 16 bars (A/B/A2/C) to 24 bars in 6 sections, applying 6 distinct
variation techniques.

Two-phase architecture:
  Phase 1: ant-colony raw pitch trajectory (unquantized floats, chaotic
           rhythm), single voice, pre-rules.
  Phase 2: musicom rules post-process -> per-bar chord-tone quantization,
           rhythm-grid snap (120-tick 16th), voice-leading correction,
           per-section harmonic regions, multi-voice arrangement.
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
STYLE_DIR = "/opt/data/projects/Styles/Arabic"
PROJECT = "235-arabic-rast-rework"
BASE = os.path.join(STYLE_DIR, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

SEED = 20261011
RNG = random.Random(SEED)

# ---------------------------------------------------------------------------
# Concept / identity (preserved from 071)
# ---------------------------------------------------------------------------
BPM = 100
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR          # 1920 ticks/bar
GRID = 120                          # 16th note grid (8th = 240, 16th = 120)
TOTAL_BARS = 24
TOTAL_TICKS = TOTAL_BARS * BAR

TONIC = 62                           # D4
# Rast maqam on D, 12-TET approximation = D Phrygian pitch-class set
# (captures the quarter-flat 2nd/3rd + neutral color of Rast):
#   D(2) Eb(3) F(5) G(7) A(9) Bb(10) C(0)
KEY_PCS = {0, 2, 3, 5, 7, 9, 10}
KEY_NAME = "D Rast (12-TET approx = D Phrygian)"

# ---------------------------------------------------------------------------
# Harmony: diatonic triads on D Phrygian (all chord tones in KEY_PCS)
# degree -> (root_pc, quality intervals, quality name)
# ---------------------------------------------------------------------------
CHORD = {
    "i":    (2,  [0, 3, 7], "min"),   # Dm   D F A
    "bII":  (3,  [0, 4, 7], "maj"),   # Eb   Eb G Bb
    "bIII": (5,  [0, 4, 7], "maj"),   # F    F A C
    "iv":   (7,  [0, 3, 7], "min"),   # Gm   G Bb D
    "v":    (9,  [0, 3, 6], "dim"),   # Adim A C Eb
    "bVI":  (10, [0, 4, 7], "maj"),   # Bb   Bb D F
    "bVII": (0,  [0, 3, 7], "min"),   # Cm   C Eb G
}
CHORD_NAMES = {"i": "Dm", "bII": "Eb", "bIII": "F", "iv": "Gm",
               "v": "Adim", "bVI": "Bb", "bVII": "Cm"}

# Per-bar chord degree across 24 bars (per-section harmonic regions).
# Each 4-bar section has its OWN short progression; sections do NOT all
# land on degree i.
BAR_DEGREES = [
    # Intro (0-3): tonic region, sparse
    "i", "i", "bII", "i",
    # A (4-7): identity theme, Phrygian cadence turn
    "i", "bII", "bVII", "i",
    # B (8-11): transposed region (iv / G area) + mode color
    "iv", "bIII", "bVI", "iv",
    # A2 (12-15): retrograde, tonic return
    "i", "bII", "i", "i",
    # C (16-19): climax, tension region (bII/bVI/bVII)
    "bII", "bVI", "bVII", "bVII",
    # Outro (20-23): Phrygian cadence bII -> i
    "i", "bII", "bII", "i",
]

# Sections: (name, bars, variation technique)
SECTIONS = [
    ("Intro", 4, "register_shift_down"),
    ("A",     4, "identity"),
    ("B",     4, "transpose_up_p4"),
    ("A2",    4, "retrograde"),
    ("C",     4, "augment_density_counterline"),
    ("Outro", 4, "invert_diminish_cadence"),
]
SECTION_STARTS = []
acc = 0
for _name, bars, _tech in SECTIONS:
    SECTION_STARTS.append(acc)
    acc += bars

# Section roots via MIDPOINT chord (s_start + bars//2); derive quality from
# the midpoint degree name. NOT the bar-0 (always-i) bug.
def section_roots():
    out = []
    for name, bars, _tech in SECTIONS:
        s = sum(b for _, b, _ in SECTIONS[:SECTIONS.index((name, bars, _tech))])
        mid = s + bars // 2
        deg = BAR_DEGREES[mid]
        root_pc, _iv, qual = CHORD[deg]
        out.append((name, CHORD_NAMES[deg], root_pc, qual, deg))
    return out


def chord_tones(degree, lo=36, hi=96):
    """Absolute MIDI chord tones of a degree, within [lo, hi]."""
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


def snap_chord(pitch, degree, lo=48, hi=84):
    """Snap a (rounded) pitch to nearest chord tone in register [lo, hi]."""
    tones = [t for t in chord_tones(degree) if lo <= t <= hi]
    if not tones:
        tones = chord_tones(degree)
    return min(tones, key=lambda t: abs(t - pitch))


def snap_grid(t):
    """Snap an absolute tick to the 16th-note grid (multiple of 120)."""
    return int(round(t / float(GRID)) * GRID)


# ---------------------------------------------------------------------------
# Phase 1: Ant-Colony Optimization raw draft (Method 041, unquantized)
# ---------------------------------------------------------------------------
class AntColonyPitch:
    """Ant agents walk a pitch graph; pheromone x consonance heuristic."""

    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.nodes = list(range(45, 85))
        self.phero = {n: 1.0 for n in self.nodes}

    def _bias(self, a, b):
        d = abs(b - a) % 12
        return {0: 1.5, 1: 1.1, 2: 1.3, 3: 1.0, 4: 1.2, 5: 1.4,
                7: 1.5, 8: 0.8, 9: 0.7, 10: 0.6, 11: 0.5}.get(d, 0.9)

    def walk(self, anchor, steps):
        cur = float(anchor)
        out = []
        for _ in range(steps):
            cands = [n for n in self.nodes if n != int(cur)]
            weights = [self.phero[n] * self._bias(int(cur), n)
                       * (1.0 + 0.35 * math.exp(-abs(n - anchor) / 14.0))
                       for n in cands]
            nxt = self.rng.choices(cands, weights=weights, k=1)[0]
            raw = nxt + self.rng.uniform(-0.45, 0.45)
            out.append(raw)
            self.phero[nxt] = self.phero[nxt] * 0.85 + 1.6
            for k in self.phero:
                self.phero[k] *= 0.995
            cur = nxt
        return out


def raw_section(colony, anchor, bars, rng, gap_scale=1.0):
    """Raw generative draft for one section: float pitches + chaotic rhythm.

    Section-relative beats. NOT quantized to scale or grid (Phase 1).
    """
    events = []
    beat = 0.0
    limit = bars * 4.0 - 0.25
    while beat < limit:
        steps = rng.randint(2, 4)
        traj = colony.walk(anchor, steps)
        for p in traj:
            gap = (rng.uniform(0.5, 4.0) ** 1.35) * gap_scale
            gap = max(0.5, min(4.0, gap))
            dur = min(gap, rng.uniform(0.75, 1.5))
            events.append({"pitch": p, "start": beat, "dur": dur})
            beat += gap
            if beat >= limit:
                break
    return events


# ---------------------------------------------------------------------------
# Variation transforms (applied to the A motif -> all other sections)
# ---------------------------------------------------------------------------
def transform(raw, kind, tonic=TONIC):
    if kind == "identity":
        return list(raw)
    if kind == "register_shift_down":
        # drop an octave + thin (keep every 2nd onset)
        ev = [{"pitch": e["pitch"] - 12, "start": e["start"], "dur": e["dur"]}
              for e in raw]
        return ev[::2]
    if kind == "transpose_up_p4":
        return [{"pitch": e["pitch"] + 5, "start": e["start"], "dur": e["dur"]}
                for e in raw]
    if kind == "retrograde":
        # melodic retrograde: reverse pitch contour, rhythm retained
        pitches = [e["pitch"] for e in raw][::-1]
        return [{"pitch": pitches[i], "start": raw[i]["start"],
                 "dur": raw[i]["dur"]} for i in range(len(raw))]
    if kind == "augment_density_counterline":
        # augmentation: durations x2 (sparser, longer notes)
        return [{"pitch": e["pitch"], "start": e["start"], "dur": e["dur"] * 2.0}
                for e in raw]
    if kind == "invert_diminish_cadence":
        # inversion around tonic + diminution (durations x0.5)
        return [{"pitch": 2 * tonic - e["pitch"], "start": e["start"],
                 "dur": e["dur"] * 0.5} for e in raw]
    return list(raw)


# ---------------------------------------------------------------------------
# Phase 2: rules post-process
# ---------------------------------------------------------------------------
def process_lead(raw_all):
    """Chord-tone quantization + grid snap + dedup + voice-leading."""
    events = []
    for e in raw_all:
        bar = int(e["start"] // 4)
        bar = max(0, min(TOTAL_BARS - 1, bar))
        degree = BAR_DEGREES[bar]
        p = int(round(e["pitch"]))
        p = snap_chord(p, degree, lo=48, hi=84)
        s = snap_grid(e["start"] * TPB)
        s = max(0, min(TOTAL_TICKS - GRID, s))
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
            d = abs(e.pitch - prev.pitch)
            if d in (5, 7, 12) and (e.start_tick - prev.end_tick) < TPB:
                bar = int(e.start_tick // BAR)
                tones = chord_tones(BAR_DEGREES[bar], lo=48, hi=84)
                cands = [t for t in tones
                         if t != e.pitch and abs(t - prev.pitch) not in (5, 7, 12)]
                if cands:
                    e.pitch = min(cands, key=lambda t: abs(t - e.pitch))
        fixed.append(e)
    return fixed


def build_harmony_events():
    """Sustained 3-tone chords per bar (chord tones only)."""
    events = []
    for bar in range(TOTAL_BARS):
        deg = BAR_DEGREES[bar]
        root_pc, ivs, _q = CHORD[deg]
        base = root_pc + 48
        t0 = bar * BAR
        for iv in ivs:
            events.append(MusicEvent(pitch=base + iv, volume=68,
                                     start_tick=t0, end_tick=t0 + BAR))
    return events


def build_bass_events():
    """Root + octave on a maqsum (3+3+2) heavy pulse."""
    events = []
    for bar in range(TOTAL_BARS):
        deg = BAR_DEGREES[bar]
        root_pc, _iv, _q = CHORD[deg]
        root = root_pc + 36
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root, volume=90,
                                 start_tick=t0, end_tick=t0 + TPB * 1.5))
        events.append(MusicEvent(pitch=root + 12, volume=80,
                                 start_tick=t0 + TPB * 2, end_tick=t0 + TPB * 3))
        events.append(MusicEvent(pitch=root, volume=84,
                                 start_tick=t0 + TPB * 3, end_tick=t0 + BAR))
    return events


def build_pad_events():
    """Low sustained root + fifth drone (chord-aware, always compliant)."""
    events = []
    for bar in range(TOTAL_BARS):
        deg = BAR_DEGREES[bar]
        root_pc, ivs, _q = CHORD[deg]
        t0 = bar * BAR
        for iv in (0, 7):  # root + fifth
            events.append(MusicEvent(pitch=root_pc + 48 + iv, volume=60,
                                     start_tick=t0, end_tick=t0 + BAR))
    return events


def build_counter_events():
    """Chord-tone arpeggio counterline in C + Outro (density rise)."""
    events = []
    for bar in range(16, TOTAL_BARS):          # sections C (16-19) + Outro (20-23)
        deg = BAR_DEGREES[bar]
        tones = chord_tones(deg, lo=60, hi=84)
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
    """Maqsum 3+3+2 on 16th grid (channel 9, excluded from pitch checks)."""
    MAQSUM = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0]
    step16 = BAR // 16
    events = []
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        for i, hit in enumerate(MAQSUM):
            if hit:
                events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=100,
                                         start_tick=t0 + i * step16,
                                         end_tick=t0 + i * step16 + step16 // 2))
                if i in (0, 4):
                    events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=100,
                                             start_tick=t0 + i * step16 + step16 * 2,
                                             end_tick=t0 + i * step16 + step16 * 3))
                else:
                    events.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=92,
                                             start_tick=t0 + i * step16,
                                             end_tick=t0 + i * step16 + step16 // 2))
            events.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT, volume=56,
                                     start_tick=t0 + i * step16 + step16 // 2,
                                     end_tick=t0 + i * step16 + step16))
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
        seg = [MusicEvent(pitch=int(round(e["pitch"])),
                          volume=int(min(110, max(60, 74 + 24 * abs(e["pitch"] - 62) / 30.0))),
                          start_tick=int(round(e["start"] * TPB)),
                          end_tick=int(round((e["start"] + e["dur"]) * TPB)))
               for e in raw_all
               if s_start <= round(e["start"] * TPB) < s_start + s_ticks]
        for e in seg:
            if e.pitch < 45:
                e.pitch = 45
            if e.pitch > 84:
                e.pitch = 84
        comp.fill_voice_section("Lead", name,
                                MusicUnit(events=rel_events(seg, s_start, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


def build_phase2(lead_events, counter_events, harmony_events, bass_events,
                 pad_events, drums_events):
    """Phase 2: 6-voice rules-processed arrangement, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=6, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    comp.add_voice("Counter", program=MidiInstrument.VIOLIN, channel=1)
    comp.add_voice("Harmony", program=MidiInstrument.STRING_ENSEMBLE, channel=2)
    comp.add_voice("Bass", program=MidiInstrument.BASS, channel=3)
    comp.add_voice("Pad", program=MidiInstrument.SYNTH_PAD, channel=4)
    comp.add_voice("Drums", program=0, channel=9)

    for name, bars, _tech in SECTIONS:
        comp.add_section(name, bars=bars)

    voice_event_map = {
        "Lead": lead_events,
        "Counter": counter_events,
        "Harmony": harmony_events,
        "Bass": bass_events,
        "Pad": pad_events,
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
<html><head><meta charset="utf-8"><title>235 Arabic Rast Rework</title>
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
<h1>235 — Arabic Rast Rework</h1>
<p class="mono">D Rast (Phrygian approx) · 100 BPM · 4/4 · 24 bars · 6 sections</p>
<div class="card"><h2>Form &amp; Variation</h2>
<table><tr><td class="td">Intro</td><td class="td">4b</td><td class="td">register shift −12 + thin</td></tr>
<tr><td class="td">A</td><td class="td">4b</td><td class="td">identity (ant-colony motif)</td></tr>
<tr><td class="td">B</td><td class="td">4b</td><td class="td">transposition +P4 (iv region)</td></tr>
<tr><td class="td">A2</td><td class="td">4b</td><td class="td">retrograde (contour reversed)</td></tr>
<tr><td class="td">C</td><td class="td">4b</td><td class="td">augmentation + counterline</td></tr>
<tr><td class="td">Outro</td><td class="td">4b</td><td class="td">inversion + diminution → cadence</td></tr>
</table></div>
<div class="card"><h2>Maqsum 3+3+2 (16th grid)</h2>
<p class="mono grid"><span class="on">█</span><span class="off">░░░</span><span class="on">█</span><span class="off">░░░</span><span class="on">█</span><span class="off">░░</span><span class="on">█</span><span class="off">░░░</span></p></div>
<div class="card"><h2>Harmonic regions (per-section midpoint root)</h2>
<table><tr><td class="td">Intro</td><td class="td">bII (Eb)</td></tr>
<tr><td class="td">A</td><td class="td">bVII (Cm)</td></tr>
<tr><td class="td">B</td><td class="td">bVI (Bb)</td></tr>
<tr><td class="td">A2</td><td class="td">i (Dm)</td></tr>
<tr><td class="td">C</td><td class="td">bVII (Cm)</td></tr>
<tr><td class="td">Outro</td><td class="td">bII (Eb)</td></tr></table></div>
<div class="card"><h2>Artifacts</h2>
<p><a href="MIDI/235-arabic-rast-rework.mid">phase2 MIDI</a> ·
<a href="MIDI/235-arabic-rast-rework-phase1.mid">phase1 MIDI</a> ·
<a href="Audio/235-arabic-rast-rework.ogg">audio (OGG)</a></p></div>
</body></html>"""
    with open(os.path.join(BASE, "index.html"), "w") as f:
        f.write(html)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # ---- Phase 1: raw ant-colony draft (single voice) ----------------------
    colony = AntColonyPitch(SEED)
    A_raw = raw_section(colony, anchor=62, bars=4, rng=RNG, gap_scale=1.0)

    section_raw = {}
    section_raw["Intro"] = transform(A_raw, "register_shift_down")
    section_raw["A"] = transform(A_raw, "identity")
    section_raw["B"] = transform(A_raw, "transpose_up_p4")
    section_raw["A2"] = transform(A_raw, "retrograde")
    section_raw["C"] = transform(A_raw, "augment_density_counterline")
    section_raw["Outro"] = transform(A_raw, "invert_diminish_cadence")

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
    phase1_mid = os.path.join(MIDI_DIR, "235-arabic-rast-rework-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(phase1_mid, AI_ASSISTED,
                     "musicom.method041.ant_colony_phase1 (rework of 071)",
                     sources=["methods_db.md:Method 041 ACOPF",
                              "source:071-arabic-rast-ant-colony"],
                     parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": SEED,
                                 "phase": 1, "quantized": False,
                                 "key": KEY_NAME, "form": "6 sections (extended)"},
                     notes="Raw ant-colony pitch trajectory, unquantized, "
                           "single voice, pre-rules. Rework of 071 (redesign: "
                           "source failed rhythm-grid + index/provenance).")
    write_grid_visualization(phase1.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
                             voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2: rules post-process (6 voices) ----------------------------
    lead_ev = process_lead(raw_all)
    counter_ev = build_counter_events()
    harmony_ev = build_harmony_events()
    bass_ev = build_bass_events()
    pad_ev = build_pad_events()
    drums_ev = build_drums_events()

    phase2 = build_phase2(lead_ev, counter_ev, harmony_ev, bass_ev, pad_ev, drums_ev)
    phase2_mid = os.path.join(MIDI_DIR, "235-arabic-rast-rework.mid")
    phase2.to_midi(phase2_mid)
    write_provenance(phase2_mid, AI_ASSISTED,
                     "musicom.method041.ant_colony_phase2 + musicom rules (rework of 071)",
                     sources=["methods_db.md:Method 041 ACOPF",
                              "source:071-arabic-rast-ant-colony"],
                     parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": SEED,
                                 "phase": 2, "quantized": True,
                                 "key": KEY_NAME, "rhythm": "Maqsum 3+3+2",
                                 "form": "6 sections (extended)",
                                 "variation_techniques": [
                                     "register_shift_down", "transposition_P4",
                                     "retrograde", "augmentation+counterline",
                                     "inversion+diminution"]},
                     notes="Rules post-process: per-bar chord-tone quantization, "
                           "120-tick grid snap, dedup, voice-leading, per-section "
                           "harmonic regions (midpoint root).")
    write_grid_visualization(phase2.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             voice_names=["Lead", "Counter", "Harmony", "Bass",
                                          "Pad", "Drums"], bpm=BPM)

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
          "PAD:", len(pad_ev), "DRUMS:", len(drums_ev))


if __name__ == "__main__":
    main()
