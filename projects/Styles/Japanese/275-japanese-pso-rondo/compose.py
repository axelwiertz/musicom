# -*- coding: utf-8 -*-
"""275 - Japanese PSO Rondo (Method 117 Particle Swarm Optimization, two-phase).

Nightly composition job (2026-10-30). Selection:
  style   = Japanese (traditional ensemble)
  method  = 117 Particle Swarm Optimization Composition (PSOC)  [concrete, Stochastic]
  key     = A yo pentatonic (major pentatonic): A B C# E F#
  form    = rondo (A1 4 / B 4 / A2 4 / C 4 / A3 4 = 20 bars)
  bpm     = 78

Two-phase architecture:
  Phase 1 (raw): a Particle Swarm optimizer searches a continuous
    (pitch x onset x velocity) space. Each particle encodes N lead notes;
    fitness rewards scale proximity, stepwise motion, and 8th-grid metric
    alignment. The global-best particle is decoded with RAW float pitch
    (rounded, NOT snapped) and off-grid onsets -> single voice, no harmony,
    own composer + own validate() gate.

  Phase 2 (rules): weight-aware tiered pitch discipline
    (classify_weight -> tiered_quantize: strong = scale+chord, weak = scale),
    16th grid snap, dedup, voice-leading, tagged chromatic approach ornaments
    on the lead, and a 5-voice Japanese arrangement (Lead=Koto 107,
    Counter=Shakuhachi 77, Harmony=Shamisen 106, Bass=Koto low 107,
    Drums ch9).

  Dual-version contract: export_dual -> -perfect.mid (grid-locked) +
    -humanized.mid (style japanese + per-instrument DNA).
"""
import json
import os
import hashlib
import random
import sys

import numpy as np

sys.path.insert(0, "/opt/data/repos/musicom/projects/Instruments")
from instrument_registry import by_name  # noqa: E402
KOTO = by_name("koto")
SHAKUHACHI = by_name("shakuhachi")
SHAMISEN = by_name("shamisen")

from structures import MusicUnit, MusicEvent, MidiInstrument  # noqa: E402
from workflows.unitmatrix_composer import UnitMatrixComposer  # noqa: E402
from workflows.humanize import export_dual  # noqa: E402
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402
from visualization.grid import write_grid_visualization  # noqa: E402
from rules.progression import Scale7ChordDegree  # noqa: E402
from sound.synthesis.scale_quantizer import (ScaleQuantizer, STRONG_GRID,  # noqa: E402
                                             classify_weight)
from workflows.pitch_audit import audit_voice  # noqa: E402

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
STYLE_DIR = "/opt/data/projects/Styles/Japanese"
PROJECT = "275-japanese-pso-rondo"
BASE = os.path.join(STYLE_DIR, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

STYLE = "japanese"
BPM = 78
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR                 # 1920
GRID = 120                                # 16th note grid (8th = 240)
STRONG = STRONG_GRID["4/4"]               # (0, 960) beats 1 & 3

KEY_NAME = "A Yo Pentatonic (major pentatonic)"
KEY_ROOT_PC = 9                           # A
KEY_PCS = {9, 11, 1, 4, 6}                # A B C# E F#
INTERVALS = [0, 2, 4, 7, 9]               # major pentatonic offsets from A
TONIC = 57                                # A3 (mirror axis region)

# 1-based degree -> chord interval offsets (all within the yo pentatonic).
# Open / suspended sonorities idiomatic to koto; only deg 1 has a major 3rd.
QUALITY = {1: (0, 4, 7), 2: (0, 5, 7), 3: (0, 5, 8), 4: (0, 5, 7), 5: (0, 5, 7)}
DEGREE_NAMES = {1: "A", 2: "B(sus)", 3: "C#(sus)", 4: "E(sus)", 5: "F#(sus)"}

# Instrument registry (source of truth)
LEAD_PROG = KOTO.midi_program          # 107
COUNTER_PROG = SHAKUHACHI.midi_program # 77
HARMONY_PROG = SHAMISEN.midi_program   # 106
BASS_PROG = KOTO.midi_program          # 107 (low register)

# ---------------------------------------------------------------------------
# Form: rondo (A-B-A-C-A). Disambiguated section names for the matrix.
# ---------------------------------------------------------------------------
# (name, bars, progression [1-based degrees], tension)
SECTIONS = [
    ("A1", 4, [1, 1, 4, 1],             0.45),
    ("B",  4, [3, 5, 3, 4],             0.65),
    ("A2", 4, [1, 1, 4, 1],             0.50),
    ("C",  4, [5, 4, 5, 3],             0.80),
    ("A3", 4, [1, 4, 5, 1],             0.55),
]
TOTAL_BARS = sum(s[1] for s in SECTIONS)          # 20
TOTAL_TICKS = TOTAL_BARS * BAR                    # 38400

SECTION_START = {}
SECTION_OF_BAR = []
_acc = 0
for name, bars, prog, tension in SECTIONS:
    SECTION_START[name] = _acc
    SECTION_OF_BAR.extend([name] * bars)
    _acc += bars
assert _acc == TOTAL_BARS
assert len(SECTION_OF_BAR) == TOTAL_BARS

BAR_DEGREES = []
for name, bars, prog, tension in SECTIONS:
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
raw_seed = 731029                           # the nightly selection seed
RNG = random.Random(raw_seed)
NPRNG = np.random.default_rng(raw_seed)


def section_tension(bar):
    bar = max(0, min(TOTAL_BARS - 1, bar))
    name = SECTION_OF_BAR[bar]
    for (n, bars, prog, tension) in SECTIONS:
        if n == name:
            return tension
    return SECTIONS[-1][3]


def diatonic(deg_index, base=57):
    """Canonical diatonic note (Scale7ChordDegree) -- no %7 wrapper."""
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_tones(d, lo=57, hi=88):
    root_pc = (KEY_ROOT_PC + INTERVALS[d - 1]) % 12
    out = set()
    for octv in range(-4, 10):
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
# Phase 1: Particle Swarm Optimization -> raw events
# ---------------------------------------------------------------------------
TOTAL_NOTES = 40                           # 2 notes/bar (sparse "ma" spacing)
NOTES_PER_BAR = TOTAL_NOTES // TOTAL_BARS  # 2


def pso_optimize():
    """Minimize -fitness over a continuous (pitch, onset, velocity) space."""
    N = TOTAL_NOTES
    D = 3 * N
    P = 40
    T = 90
    w_max, w_min = 0.9, 0.4
    c1 = c2 = 2.0
    v_max = 0.2

    scale_members = sorted({KEY_ROOT_PC + 12 * octv + iv
                            for octv in range(-1, 8) for iv in INTERVALS
                            if 48 <= KEY_ROOT_PC + 12 * octv + iv <= 90})
    grid8 = [0, 240, 480, 720, 960, 1200, 1440, 1680]

    def decode(x):
        notes = []
        for i in range(N):
            bar = (i * TOTAL_BARS) // N
            pitch = 57.0 + x[3 * i] * 24.0          # 57..81 (A3..A5)
            ofrac = x[3 * i + 1]                     # within-bar onset fraction
            vel = 45.0 + x[3 * i + 2] * 65.0        # 45..110
            notes.append((pitch, ofrac, vel, bar))
        return notes

    def fitness(x):
        notes = decode(x)
        sc = 0.0
        prev = None
        for (pitch, ofrac, vel, bar) in notes:
            near = min(scale_members, key=lambda s: abs(s - pitch))
            sc += max(0.0, 1.0 - abs(near - pitch) / 5.0)   # tonal
            if prev is not None:
                st = abs(pitch - prev)
                sc += 1.0 if st <= 2 else (0.5 if st <= 4 else 0.0)  # stepwise
            prev = pitch
            bt = ofrac * BAR
            ng = min(grid8, key=lambda g: abs(bt - g))
            sc += max(0.0, 1.0 - abs(bt - ng) / 240.0)    # metric
        return sc

    rng = NPRNG
    x = rng.random((P, D))
    # bias onset toward a per-bar slot so notes spread across the bar
    for i in range(N):
        slot = (i % NOTES_PER_BAR) / float(NOTES_PER_BAR) + 0.5 / NOTES_PER_BAR
        x[:, 3 * i + 1] = np.clip(slot + rng.normal(0, 0.06, P), 0.0, 1.0)
    v = rng.uniform(-v_max, v_max, (P, D))
    pbest = x.copy()
    pbest_fit = np.array([fitness(xi) for xi in x])
    g = pbest[pbest_fit.argmax()].copy()
    gfit = pbest_fit.max()

    for t in range(T):
        w = w_max - (w_max - w_min) * (t / float(T))
        r1 = rng.random((P, D))
        r2 = rng.random((P, D))
        v = w * v + c1 * r1 * (pbest - x) + c2 * r2 * (g - x)
        v = np.clip(v, -v_max, v_max)
        x = np.clip(x + v, 0.0, 1.0)
        fit = np.array([fitness(xi) for xi in x])
        improve = fit > pbest_fit
        pbest[improve] = x[improve]
        pbest_fit[improve] = fit[improve]
        if fit.max() > gfit:
            gfit = fit.max()
            g = x[fit.argmax()].copy()

    return decode(g), gfit


def gen_raw_events():
    notes, best_fit = pso_optimize()
    events = []
    for (pitch, ofrac, vel, bar) in notes:
        onset_ms = bar * BAR_MS + ofrac * BAR_MS
        dur_ms = SIXTEENTH_MS * (1.8 + 0.7 * NPRNG.random())
        events.append({
            "pitch": float(pitch),           # raw float (not snapped)
            "start": onset_ms,               # off-grid (continuous fraction)
            "dur": dur_ms,
            "vel": int(np.clip(vel, 45, 110)),
        })
    events.sort(key=lambda e: e["start"])
    return events, best_fit


def build_phase1(raw_events):
    """Phase 1: single voice (Lead=Koto), raw unquantized units, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=LEAD_PROG, channel=0)
    for name, bars, prog, tension in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog, tension in SECTIONS:
        s_start_ms = SECTION_START[name] * BAR_MS
        s_start_ticks = SECTION_START[name] * BAR
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
                                MusicUnit(events=rel_events(seg, s_start_ticks, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# Phase 2: rules post-process (weight-aware tiered pitch discipline)
# ---------------------------------------------------------------------------
SQ = ScaleQuantizer(root=57, scale="pentatonic")   # A yo pentatonic


def process_lead(raw_events):
    """Tiered quantize (strong=scale+chord, weak=scale) + grid snap + ornaments."""
    events = []
    for e in raw_events:
        s = snap(e["start"] / MS_PER_TICK)
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = min(TOTAL_BARS - 1, s // BAR)
        degree = BAR_DEGREES[bar]
        w = classify_weight(s, STRONG, BAR)
        ct = chord_tones(degree, lo=57, hi=88)
        p = SQ.tiered_quantize(e["pitch"], weight=w, chord_tones=ct)
        p = max(52, min(88, p))
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
                tones = chord_tones(BAR_DEGREES[bar], lo=52, hi=88)
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
    """Shakuhachi counterline: octave-up, half-density harmonized echo."""
    events = []
    for i, e in enumerate(raw_events):
        if i % 2 != 0:
            continue
        s = snap((e["start"] + 0.5 * SIXTEENTH_MS) / MS_PER_TICK)
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = min(TOTAL_BARS - 1, s // BAR)
        degree = BAR_DEGREES[bar]
        w = classify_weight(s, STRONG, BAR)
        ct = chord_tones(degree, lo=64, hi=96)
        p = SQ.tiered_quantize(e["pitch"] + 12.0, weight=w, chord_tones=ct)
        p = max(64, min(96, p))
        ev = MusicEvent(pitch=p, volume=max(40, e["vel"] - 15), start_tick=s,
                        end_tick=min(TOTAL_TICKS, s + 3 * GRID))
        ev.weight = w
        events.append(ev)
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def build_harmony():
    """Shamisen plucked arpeggio: chord tones, quarter-note plucks per bar."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=57)      # A3 region (shamisen sweet spot)
        voicing = [root + iv for iv in QUALITY[d]]
        t0 = bar * BAR
        for pluck in range(4):
            n = voicing[pluck % 3]
            events.append(MusicEvent(pitch=n, volume=56,
                                     start_tick=t0 + pluck * 480,
                                     end_tick=t0 + pluck * 480 + 360))
    return events


def build_bass():
    """Koto low root pedal + in-scale companion on beat 3 (all scale tones)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=45)     # A2 region (koto low)
        alt = bass_alt(root)
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root, volume=72,
                                 start_tick=t0, end_tick=t0 + BAR - GRID))
        events.append(MusicEvent(pitch=alt, volume=58,
                                 start_tick=t0 + 960, end_tick=t0 + BAR - GRID))
    return events


def bass_alt(root):
    """An in-scale companion a 5th/4th above root (pentatonic-safe), else octave."""
    for iv in (7, 5, 12):
        cand = root + iv
        if (cand % 12) in KEY_PCS:
            return cand
    return root + 12


def build_drums():
    """Sparse taiko-flavoured percussion: deep kick, low-tom accents, crash."""
    events = []
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        name = SECTION_OF_BAR[bar]
        # deep "taiko" thump on beat 1 (all bars)
        events.append(MusicEvent(pitch=36, volume=68,
                                 start_tick=t0, end_tick=t0 + GRID))
        # low-tom accent on beat 3 (all bars)
        events.append(MusicEvent(pitch=45, volume=52,
                                 start_tick=t0 + 960, end_tick=t0 + 960 + GRID))
        # rim on the 16th after beat 2 (B/C sections = denser)
        if name in ("B", "C"):
            events.append(MusicEvent(pitch=37, volume=44,
                                     start_tick=t0 + 1080, end_tick=t0 + 1080 + GRID))
        # crash at section starts (from B onward)
        if bar == SECTION_START[name] and name != "A1":
            events.append(MusicEvent(pitch=49, volume=54,
                                     start_tick=t0, end_tick=t0 + 2 * GRID))
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


def build_phase2(lead_ev, counter_ev, harm_ev, bass_ev, drums_ev):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=LEAD_PROG, channel=0)        # Koto
    comp.add_voice("Counter", program=COUNTER_PROG, channel=1)  # Shakuhachi
    comp.add_voice("Harmony", program=HARMONY_PROG, channel=2)  # Shamisen
    comp.add_voice("Bass", program=BASS_PROG, channel=3)        # Koto low
    comp.add_voice("Drums", program=0, channel=9)

    for name, bars, prog, tension in SECTIONS:
        comp.add_section(name, bars=bars)

    vmap = {"Lead": lead_ev, "Counter": counter_ev, "Harmony": harm_ev,
            "Bass": bass_ev, "Drums": drums_ev}
    for name, bars, prog, tension in SECTIONS:
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


def run_tiered_audit(lead_ev, counter_ev, harm_ev, bass_ev):
    """Tiered pitch discipline audit on the 4 pitched voices."""
    scale_pcs = sorted(KEY_PCS)
    chord_by_bar = {b: chord_pcs(BAR_DEGREES[b]) for b in range(TOTAL_BARS)}
    voices = {"Lead": lead_ev, "Counter": counter_ev,
              "Harmony": harm_ev, "Bass": bass_ev}
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
    raw_events, best_fit = gen_raw_events()
    print("PSO raw events:", len(raw_events), "best_fitness:", round(best_fit, 3))

    # ---- Phase 1 raw draft (single voice) ----------------------------------
    phase1 = build_phase1(raw_events)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.method.117_pso_phase1",
        sources=[],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "rondo", "style": STYLE,
                    "pso_population": 40, "pso_iterations": 90,
                    "method": "117 Particle Swarm Optimization Composition"},
        notes="Raw PSO decode: swarm-optimized continuous (pitch x onset x "
              "velocity) lead. Float pitch (rounded, not snapped), off-grid "
              "onsets, single voice, pre-rules.")
    write_grid_visualization(
        phase1.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
        voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2 rules post-process (5 voices) ----------------------------
    lead_ev = process_lead(raw_events)
    counter_ev = build_counter(raw_events)
    harm_ev = build_harmony()
    bass_ev = build_bass()
    drums_ev = build_drums()

    phase2 = build_phase2(lead_ev, counter_ev, harm_ev, bass_ev, drums_ev)

    # ---- tiered pitch-discipline audit -------------------------------------
    tiered = run_tiered_audit(lead_ev, counter_ev, harm_ev, bass_ev)
    if not tiered["all_pass"]:
        print("TIERED_AUDIT_FAIL:", json.dumps(tiered, indent=2))
        raise RuntimeError("tiered pitch audit failed -- see pitch_audit.json")
    with open(os.path.join(ANALYSIS_DIR, "pitch_audit.json"), "w") as f:
        json.dump(tiered, f, indent=2)
    print("TIERED_AUDIT:", json.dumps(tiered, indent=2))

    # ---- dual-version export (perfect + humanized) ------------------------
    hz_instruments = {
        "Lead":    (None, 6.0, None, 0.02),   # koto melodic
        "Counter": (None, 7.0, None, 0.03),   # shakuhachi breathy
        "Harmony": (None, 5.0, None, 0.02),   # shamisen pluck
        "Bass":    (6.0, 4.0, 8.0, 0.01),     # low koto lays back 8 ms
        "Drums":   (2.0, 3.0, 0.0, 0.005),    # anchors grid
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    provenance_params = {
        "bpm": BPM, "key": "A", "mode": "pentatonic", "style": STYLE,
        "form": "rondo", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "method": "117 Particle Swarm Optimization Composition", "layer": "concrete",
        "paradigm": "Stochastic",
        "voices": [["Lead", "Koto", LEAD_PROG], ["Counter", "Shakuhachi", COUNTER_PROG],
                   ["Harmony", "Shamisen", HARMONY_PROG], ["Bass", "Koto", BASS_PROG],
                   ["Drums", "ch9", 0]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "pso_best_fitness": round(best_fit, 3),
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered quantize + grid snap + "
        "dedup + voice-leading + tagged ornaments) (method 117 PSOC)",
        sources=[phase1_mid],
        parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (rondo, 20 bars).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 117 PSOC)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style japanese + per-instrument DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=["Lead", "Counter", "Harmony", "Bass", "Drums"], bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- summary -----------------------------------------------------------
    summary = {
        "style": STYLE, "genre": "Japanese",
        "method": "117 Particle Swarm Optimization Composition", "method_layer": "concrete",
        "method_paradigm": "Stochastic",
        "form": "rondo", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "pso_raw_events": len(raw_events),
        "pso_best_fitness": round(best_fit, 3),
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
          "HARMONY:", len(harm_ev), "BASS:", len(bass_ev), "DRUMS:", len(drums_ev))


if __name__ == "__main__":
    main()
