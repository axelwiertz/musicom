# -*- coding: utf-8 -*-
"""273 - Cinematic Perlin Build (Method 040 Perlin Noise Composition, two-phase).

Nightly composition job (2026-10-29). Selection:
  style   = Cinematic
  method  = 040 Perlin Noise Composition (PNC)  [concrete, Nature-Led]
  key     = D minor (aeolian)
  form    = cinematic-build  (Intro 4 / Build 8 / Rise 8 / Peak 8 / Resolve 4 = 32 bars)
  bpm     = 76

Two-phase architecture:
  Phase 1 (raw): a 1D Perlin gradient-noise field (4-octave fractal Brownian
    motion) drives a smooth pitch contour; a second, higher-frequency noise
    field drives onset density and velocity. Raw events keep float pitch and
    jittered (off-grid) onsets. Single voice, NO harmony, unquantized -> own
    composer + own validate() gate.

  Phase 2 (rules): weight-aware tiered pitch discipline
    (classify_weight -> tiered_quantize: strong = scale+chord, weak = scale),
    16th grid snap, dedup, voice-leading, tagged chromatic approach ornaments
    on the lead, and a 5-voice cinematic arrangement (Lead=Violin,
    Counter=Flute, Pad=String Ensemble, Bass=Cello, Drums ch9).

  Dual-version contract: export_dual -> -perfect.mid (grid-locked) +
    -humanized.mid (style cinematic + per-instrument DNA).
"""
import json
import os
import hashlib
import random

import numpy as np

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree
from sound.synthesis.scale_quantizer import (ScaleQuantizer, STRONG_GRID,
                                             classify_weight)
from workflows.pitch_audit import audit_voice

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
STYLE_DIR = "/opt/data/projects/Styles/Cinematic"
PROJECT = "273-cinematic-perlin-build"
BASE = os.path.join(STYLE_DIR, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

STYLE = "cinematic"
BPM = 76
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR                 # 1920
GRID = 120                                # 16th note grid (8th = 240)
STRONG = STRONG_GRID["4/4"]               # (0, 960) beats 1 & 3

KEY_NAME = "D Minor (aeolian)"
KEY_ROOT_PC = 2                           # D
KEY_PCS = {2, 4, 5, 7, 9, 10, 0}          # D E F G A Bb C
INTERVALS = [0, 2, 3, 5, 7, 8, 10]        # aeolian offsets from D
TONIC = 50                                # D3 (mirror axis region)

# 1-based degree -> triad quality intervals (D aeolian diatonic)
QUALITY = {1: (0, 3, 7), 2: (0, 3, 6), 3: (0, 4, 7), 4: (0, 3, 7),
           5: (0, 3, 7), 6: (0, 4, 7), 7: (0, 4, 7)}
DEGREE_NAMES = {1: "Dm", 2: "Edim", 3: "F", 4: "Gm", 5: "Am", 6: "Bb", 7: "C"}

# ---------------------------------------------------------------------------
# Form: cinematic-build (5 sections). tension + lead octave ramp.
# ---------------------------------------------------------------------------
# (name, bars, progression [1-based degrees], tension, lead_octave_base)
SECTIONS = [
    ("Intro",   4, [1, 1, 6, 7],                0.15, 55),
    ("Build",   8, [1, 6, 3, 7, 1, 6, 3, 7],    0.40, 60),
    ("Rise",    8, [6, 7, 1, 5, 4, 7, 1, 5],    0.65, 64),
    ("Peak",    8, [1, 6, 3, 7, 1, 6, 3, 7],    0.90, 67),
    ("Resolve", 4, [1, 6, 7, 1],                0.35, 60),
]
TOTAL_BARS = sum(s[1] for s in SECTIONS)          # 32
TOTAL_TICKS = TOTAL_BARS * BAR                    # 61440

SECTION_START = {}
SECTION_OF_BAR = []
_acc = 0
for name, bars, prog, tension, octv in SECTIONS:
    SECTION_START[name] = _acc
    SECTION_OF_BAR.extend([name] * bars)
    _acc += bars
assert _acc == TOTAL_BARS
assert len(SECTION_OF_BAR) == TOTAL_BARS

BAR_DEGREES = []
for name, bars, prog, tension, octv in SECTIONS:
    BAR_DEGREES.extend(prog)
assert len(BAR_DEGREES) == TOTAL_BARS

# ms geometry
BEAT_MS = 60000.0 / BPM
BAR_MS = BEAT_MS * BEATS_PER_BAR
SIXTEENTH_MS = BEAT_MS / 4.0
TOTAL_MS = TOTAL_BARS * BAR_MS
MS_PER_TICK = BEAT_MS / TPB

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 928473                           # the nightly selection seed
RNG = random.Random(raw_seed)
NPRNG = np.random.default_rng(raw_seed)


def section_at(t_ms):
    bar = int(t_ms / BAR_MS)
    bar = max(0, min(TOTAL_BARS - 1, bar))
    name = SECTION_OF_BAR[bar]
    for (n, bars, prog, tension, octv) in SECTIONS:
        if n == name:
            return tension, octv
    return SECTIONS[-1][3], SECTIONS[-1][4]


def diatonic(deg_index, base=50):
    """Canonical diatonic note (Scale7ChordDegree) -- no %7 wrapper."""
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_tones(d, lo=48, hi=84):
    root_pc = (KEY_ROOT_PC + INTERVALS[d - 1]) % 12
    out = set()
    for octv in range(-3, 10):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def chord_pcs(d):
    root_pc = (KEY_ROOT_PC + INTERVALS[d - 1]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def snap(t):
    return int(round(t / float(GRID)) * GRID)


# ---------------------------------------------------------------------------
# Phase 1: Perlin gradient noise (fBm) -> raw events
# ---------------------------------------------------------------------------
def make_perm(seed):
    p = np.random.default_rng(seed).permutation(256).astype(int).tolist()
    return p + p


def _fade(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _grad(h, x):
    return (1.0 if (h & 1) else -1.0) * x


def perlin1(perm, x):
    X = int(np.floor(x))
    xf = x - X
    u = _fade(xf)
    i = X & 255
    a = _grad(perm[i], xf)
    b = _grad(perm[i + 1], xf - 1.0)
    return a + u * (b - a)


def fbm(perm, x, octaves=4, lacunarity=2.0, gain=0.5):
    amp = 1.0
    freq = 1.0
    tot = 0.0
    norm = 0.0
    for _ in range(octaves):
        tot += amp * perlin1(perm, x * freq)
        norm += amp
        amp *= gain
        freq *= lacunarity
    return tot / norm


def gen_raw_events():
    """Perlin pitch-contour + activity-density -> raw float-pitch events."""
    perm_pitch = make_perm(raw_seed + 1)
    perm_act = make_perm(raw_seed + 2)
    events = []
    t = 0.0
    while t < TOTAL_MS - SIXTEENTH_MS:
        tension, oct_base = section_at(t)
        x = t * 0.001
        pv = fbm(perm_pitch, x * 0.40)          # smooth melodic contour
        av = fbm(perm_act, x * 1.60 + 7.31)     # onset density field
        thresh = 0.15 - 0.40 * tension          # higher tension -> denser
        if av > thresh:
            pitch = float(oct_base + pv * 6.0)
            pitch = max(40.0, min(96.0, pitch))
            vel = int(np.clip(66 + 40 * av + 10 * tension, 45, 122))
            onset = t + NPRNG.uniform(-0.12, 0.12) * SIXTEENTH_MS
            dur = SIXTEENTH_MS * (1.6 + 0.8 * NPRNG.random())
            events.append({"pitch": pitch, "start": onset, "dur": dur, "vel": vel})
        t += SIXTEENTH_MS
    return events


def build_phase1(raw_events):
    """Phase 1: single voice (Lead), raw unquantized units, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=MidiInstrument.VIOLIN, channel=0)
    for name, bars, prog, tension, octv in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog, tension, octv in SECTIONS:
        s_start_ms = SECTION_START[name] * BAR_MS
        s_ms = bars * BAR_MS
        s_ticks = bars * BAR
        seg = []
        for e in raw_events:
            if s_start_ms <= e["start"] < s_start_ms + s_ms:
                st = int(round(e["start"] / MS_PER_TICK))
                en = int(round((e["start"] + e["dur"]) / MS_PER_TICK))
                p = int(round(e["pitch"]))
                p = max(36, min(96, p))
                seg.append(MusicEvent(pitch=p, volume=e["vel"],
                                      start_tick=st, end_tick=en))
        seg.sort(key=lambda e: e.start_tick)
        comp.fill_voice_section("Lead", name,
                                MusicUnit(events=rel_events(seg, 0, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# Phase 2: rules post-process (weight-aware tiered pitch discipline)
# ---------------------------------------------------------------------------
SQ = ScaleQuantizer(root=50, scale="minor")   # D minor anchored at D3


def process_lead(raw_events):
    """Tiered quantize (strong=scale+chord, weak=scale) + grid snap + ornaments."""
    events = []
    for e in raw_events:
        s = snap(e["start"] / MS_PER_TICK)
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = min(TOTAL_BARS - 1, s // BAR)
        degree = BAR_DEGREES[bar]
        w = classify_weight(s, STRONG, BAR)
        ct = chord_tones(degree, lo=50, hi=84)
        p = SQ.tiered_quantize(e["pitch"], weight=w, chord_tones=ct)
        p = max(48, min(86, p))
        ev = MusicEvent(pitch=p, volume=e["vel"], start_tick=s,
                        end_tick=min(TOTAL_TICKS, s + 2 * GRID))
        ev.weight = w
        events.append(ev)

    # dedup collided (start_tick, pitch) -> keep longest
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    events = sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))

    # voice-leading: break parallel perfect 5ths/octaves (adjacent onsets)
    fixed = []
    for e in events:
        if fixed:
            prev = fixed[-1]
            gap = e.start_tick - prev.end_tick
            if abs(e.pitch - prev.pitch) in (5, 7, 12) and gap < TPB:
                bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
                tones = chord_tones(BAR_DEGREES[bar], lo=48, hi=86)
                cands = [t for t in tones
                         if t != e.pitch and abs(t - prev.pitch) not in (5, 7, 12)]
                if cands:
                    e.pitch = min(cands, key=lambda t: abs(t - e.pitch))
        fixed.append(e)

    # tagged chromatic approach ornaments (lead MAY carry tagged ornaments):
    # a half-step-below approach into strong chord tones, only when chromatic
    # and the prior 16th slot is free. Deterministic (every 2nd eligible).
    events = fixed
    used_slots = {e.start_tick for e in events}
    ornaments = []
    eligible = 0
    for e in events:
        if classify_weight(e.start_tick, STRONG, BAR) != "strong":
            continue
        approach = e.pitch - 1
        if (approach % 12) in KEY_PCS:
            continue
        slot = e.start_tick - GRID
        if slot < 0 or slot in used_slots:
            continue
        eligible += 1
        if eligible % 2 != 0:
            continue
        oe = MusicEvent(pitch=approach, volume=max(50, e.volume - 10),
                        start_tick=slot, end_tick=e.start_tick)
        oe.weight = "weak"
        oe.ornament = "approach"
        oe.resolve_pitch = e.pitch
        ornaments.append(oe)
        used_slots.add(slot)
    return sorted(events + ornaments, key=lambda e: (e.start_tick, e.pitch))


def build_counter(raw_events):
    """Flute counterline: octave-up, half-density harmonized echo of the contour."""
    events = []
    for i, e in enumerate(raw_events):
        if i % 2 != 0:
            continue
        s = snap((e["start"] + 0.5 * SIXTEENTH_MS) / MS_PER_TICK)
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = min(TOTAL_BARS - 1, s // BAR)
        degree = BAR_DEGREES[bar]
        w = classify_weight(s, STRONG, BAR)
        ct = chord_tones(degree, lo=60, hi=96)
        p = SQ.tiered_quantize(e["pitch"] + 12.0, weight=w, chord_tones=ct)
        p = max(60, min(96, p))
        ev = MusicEvent(pitch=p, volume=max(40, e["vel"] - 15), start_tick=s,
                        end_tick=min(TOTAL_TICKS, s + 2 * GRID))
        ev.weight = w
        events.append(ev)
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def build_pad():
    """String ensemble sustained whole-note triads (root-position close voicing)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=50)
        voicing = sorted(root + iv for iv in QUALITY[d])
        t0 = bar * BAR
        for n in voicing:
            events.append(MusicEvent(pitch=n, volume=52,
                                     start_tick=t0, end_tick=t0 + BAR - GRID))
    return events


def build_bass():
    """Cello low root pedal + fifth on beat 3 (all chord tones)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=38)      # D2 region
        fifth = root + 7
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root, volume=80,
                                 start_tick=t0, end_tick=t0 + BAR - GRID))
        events.append(MusicEvent(pitch=fifth, volume=62,
                                 start_tick=t0 + 960, end_tick=t0 + BAR - GRID))
    return events


def build_drums():
    """Sparse cinematic percussion: soft kick, cymbal section accents, Peak toms."""
    events = []
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        name = SECTION_OF_BAR[bar]
        # soft kick on beat 1 (all bars) and beat 3 (build/rise/peak)
        events.append(MusicEvent(pitch=36, volume=66,
                                 start_tick=t0, end_tick=t0 + GRID))
        if name in ("Build", "Rise", "Peak"):
            events.append(MusicEvent(pitch=36, volume=48,
                                     start_tick=t0 + 960, end_tick=t0 + 960 + GRID))
        # cymbal crash at section starts (from Build onward)
        if bar == SECTION_START[name] and name != "Intro":
            events.append(MusicEvent(pitch=49, volume=56,
                                     start_tick=t0, end_tick=t0 + 2 * GRID))
        # Peak: low-tom swell accent on beat 4
        if name == "Peak":
            events.append(MusicEvent(pitch=45, volume=50,
                                     start_tick=t0 + 1440, end_tick=t0 + 1440 + GRID))
    return events


# ---------------------------------------------------------------------------
# Matrix helpers
# ---------------------------------------------------------------------------
def rel_events(abs_events, s_start, s_len):
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
    out.sort(key=lambda e: e.start_tick)
    # silent terminal landmark (zero-drift anchor; humanizer passes untouched)
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=max(0, s_len - 10), end_tick=s_len))
    return out


def build_phase2(lead_ev, counter_ev, pad_ev, bass_ev, drums_ev):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=40, channel=0)        # Violin
    comp.add_voice("Counter", program=73, channel=1)     # Flute
    comp.add_voice("Pad", program=48, channel=2)         # String Ensemble
    comp.add_voice("Bass", program=42, channel=3)        # Cello
    comp.add_voice("Drums", program=0, channel=9)

    for name, bars, prog, tension, octv in SECTIONS:
        comp.add_section(name, bars=bars)

    vmap = {"Lead": lead_ev, "Counter": counter_ev, "Pad": pad_ev,
            "Bass": bass_ev, "Drums": drums_ev}
    for name, bars, prog, tension, octv in SECTIONS:
        s_start = SECTION_START[name] * BAR
        s_ticks = bars * BAR
        for vname, all_ev in vmap.items():
            seg = [e for e in all_ev if s_start <= e.start_tick < s_start + s_ticks]
            comp.fill_voice_section(vname, name,
                                    MusicUnit(events=rel_events(seg, s_start, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


def run_tiered_audit(lead_ev, counter_ev, pad_ev, bass_ev):
    """Tiered pitch discipline audit on the 4 pitched voices."""
    scale_pcs = sorted(KEY_PCS)
    chord_by_bar = {b: chord_pcs(BAR_DEGREES[b]) for b in range(TOTAL_BARS)}
    voices = {"Lead": lead_ev, "Counter": counter_ev,
              "Pad": pad_ev, "Bass": bass_ev}
    report = {}
    all_pass = True
    for vname, ev in voices.items():
        r = audit_voice(ev, scale_pcs, chord_pcs_by_bar=chord_by_bar,
                        strong_grid=STRONG, bar_ticks=BAR, grid=240)
        report[vname] = {
            "audible": r.audible,
            "strong_ok": r.strong_ok,
            "weak_in_scale": r.weak_in_scale,
            "tagged_ornaments": r.tagged_ornaments,
            "tagged_resolving": r.tagged_resolving,
            "tagged_non_resolving": r.tagged_non_resolving,
            "untagged_out_of_scale": r.untagged_out_of_scale,
            "strong_violations": r.strong_violations,
            "passes": r.passes,
        }
        if not r.passes:
            all_pass = False
    report["all_pass"] = all_pass
    return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    raw_events = gen_raw_events()
    print("Perlin raw events:", len(raw_events))

    # ---- Phase 1 raw draft (single voice) ----------------------------------
    phase1 = build_phase1(raw_events)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.method.040_perlin_noise_phase1",
        sources=[],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "cinematic-build", "style": STYLE,
                    "method": "040 Perlin Noise Composition (fBm gradient noise)"},
        notes="Raw Perlin fBm decode: 4-octave gradient-noise pitch contour + "
              "activity-density field. Float pitch, off-grid onsets, single "
              "voice, pre-rules.")
    write_grid_visualization(
        phase1.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
        voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2 rules post-process (5 voices) ----------------------------
    lead_ev = process_lead(raw_events)
    counter_ev = build_counter(raw_events)
    pad_ev = build_pad()
    bass_ev = build_bass()
    drums_ev = build_drums()

    phase2 = build_phase2(lead_ev, counter_ev, pad_ev, bass_ev, drums_ev)

    # ---- tiered pitch-discipline audit -------------------------------------
    tiered = run_tiered_audit(lead_ev, counter_ev, pad_ev, bass_ev)
    if not tiered["all_pass"]:
        print("TIERED_AUDIT_FAIL:", json.dumps(tiered, indent=2))
        raise RuntimeError("tiered pitch audit failed -- see pitch_audit.json")
    with open(os.path.join(ANALYSIS_DIR, "pitch_audit.json"), "w") as f:
        json.dump(tiered, f, indent=2)
    print("TIERED_AUDIT:", json.dumps(tiered, indent=2))

    # ---- dual-version export (perfect + humanized) ------------------------
    hz_instruments = {
        "Lead":    (None, 6.0, None, 0.03),   # violin melodic
        "Counter": (None, 7.0, None, 0.02),   # flute melodic
        "Pad":     (None, 4.0, None, 0.02),   # string ensemble
        "Bass":    (6.0, 5.0, 8.0, 0.01),     # cello lays back 8 ms
        "Drums":   (2.0, 3.0, 0.0, 0.005),    # anchors grid
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    provenance_params = {
        "bpm": BPM, "key": "D", "mode": "minor", "style": STYLE,
        "form": "cinematic-build", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "method": "040 Perlin Noise Composition", "layer": "concrete",
        "paradigm": "Nature-Led",
        "voices": [["Lead", "Violin", 40], ["Counter", "Flute", 73],
                   ["Pad", "String Ensemble", 48], ["Bass", "Cello", 42],
                   ["Drums", "ch9", 0]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered quantize + grid snap + "
        "dedup + voice-leading + tagged ornaments) (method 040 Perlin)",
        sources=[phase1_mid],
        parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (cinematic-build, 32 bars).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 040 Perlin)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style cinematic + per-instrument DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=["Lead", "Counter", "Pad", "Bass", "Drums"], bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- summary -----------------------------------------------------------
    summary = {
        "style": STYLE, "genre": "Cinematic",
        "method": "040 Perlin Noise Composition", "method_layer": "concrete",
        "method_paradigm": "Nature-Led",
        "form": "cinematic-build", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "pnc_raw_events": len(raw_events),
        "phase1_path": phase1_mid,
        "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "section_tension": [(s[0], s[3]) for s in SECTIONS],
    }
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("LEAD_EVENTS:", len(lead_ev), "COUNTER:", len(counter_ev),
          "PAD:", len(pad_ev), "BASS:", len(bass_ev), "DRUMS:", len(drums_ev))


if __name__ == "__main__":
    main()