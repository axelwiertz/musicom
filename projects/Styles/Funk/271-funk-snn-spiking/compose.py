# -*- coding: utf-8 -*-
"""271 - Funk SNN Spiking (Method 109 SNN-C, two-phase architecture).

Nightly composition job (2026-10-28). Selection:
  style   = Funk
  method  = 109 Spiking Neural Network Composition (SNN-C)  [concrete, Nature-Led]
  key     = F major
  form    = rondo  (A B A C A, 4 bars each = 20 bars)
  seed    = 2034316830

Two-phase architecture:
  Phase 1 (raw): a spiking neural network of Izhikevich RS neurons, 12
    tonotopic pitch-class columns, driven by a thalamic theta (bar) + gamma
    (16th) clock, a prefrontal mode/scale bias, and an insula per-section
    tension envelope (HOME/LIFT/HOME/TENSE/TURN). Spike trains are decoded
    by population rate (softmax winner) into raw float-pitch, off-grid-onset,
    rate-velocity events. Single voice, NO harmony, unquantized -> own
    composer + own validate() gate.

  Phase 2 (rules): weight-aware tiered pitch discipline
    (classify_weight -> tiered_quantize: strong = scale+chord, weak = scale),
    16th grid snap, dedup, voice-leading, tagged chromatic approach ornaments
    on the lead, and a 5-voice funk arrangement (Lead=Clavinet,
    Counter=Clean Guitar, Brass=Brass Section, Bass=Electric Bass, Drums ch9).

  Dual-version contract: export_dual -> -perfect.mid (grid-locked) +
    -humanized.mid (style funk + per-instrument DNA).
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
STYLE_DIR = "/opt/data/projects/Styles/Funk"
PROJECT = "271-funk-snn-spiking"
BASE = os.path.join(STYLE_DIR, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

STYLE = "funk"
BPM = 105
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR                 # 1920
GRID = 120                                # 16th note grid (8th = 240)
TOTAL_BARS = 20
TOTAL_TICKS = TOTAL_BARS * BAR            # 38400
STRONG = STRONG_GRID["4/4"]               # (0, 960) beats 1 & 3

KEY_NAME = "F Major"
KEY_ROOT_PC = 5                           # F
KEY_PCS = {5, 7, 9, 10, 0, 2, 4}          # F G A Bb C D E
INTERVALS = [0, 2, 4, 5, 7, 9, 11]        # scale offsets from F
TONIC = 65                                # F4 (mirror axis)

# 1-based degree -> triad quality intervals (F major diatonic)
QUALITY = {1: (0, 4, 7), 2: (0, 3, 7), 3: (0, 3, 7), 4: (0, 4, 7),
           5: (0, 4, 7), 6: (0, 3, 7), 7: (0, 3, 6)}
DEGREE_NAMES = {1: "F", 2: "Gm", 3: "Am", 4: "Bb", 5: "C", 6: "Dm", 7: "Edim"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 2034316830                     # the nightly selection seed
RNG = random.Random(raw_seed)
NPRNG = np.random.default_rng(raw_seed)

# ---------------------------------------------------------------------------
# Form: rondo A B A C A (4 bars each = 20 bars). insula tension per section.
# ---------------------------------------------------------------------------
# (name, bars, progression [1-based degrees], tension, lead_octave_base)
# NOTE: unique internal names — the composer keys sections by name; the
# musical form is still rondo A-B-A-C-A (A1/A2/A3 = the returning refrain).
SECTIONS = [
    ("A1", 4, [1, 4, 6, 5], 0.25, 60),     # HOME  (rondo refrain A)
    ("B",  4, [6, 5, 4, 5], 0.55, 72),     # LIFT  (higher register)
    ("A2", 4, [1, 4, 6, 5], 0.25, 60),     # HOME  (refrain return)
    ("C",  4, [6, 2, 5, 1], 0.85, 60),     # TENSE (chromatic drive, ii-V-I)
    ("A3", 4, [1, 4, 6, 5], 0.40, 60),     # TURN  (final refrain resolve)
]
SECTION_START = {}
_acc = 0
for name, bars, prog, tension, octv in SECTIONS:
    SECTION_START[name] = _acc
    _acc += bars
assert _acc == TOTAL_BARS

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


def section_at(t_ms):
    """Return (section_index, tension, octave_base) for a simulation time."""
    bar = int(t_ms / BAR_MS)
    bar = max(0, min(TOTAL_BARS - 1, bar))
    acc = 0
    for i, (name, bars, prog, tension, octv) in enumerate(SECTIONS):
        if bar < acc + bars:
            return i, tension, octv
        acc += bars
    return len(SECTIONS) - 1, SECTIONS[-1][3], SECTIONS[-1][4]


def diatonic(deg_index, base=65):
    """Canonical diatonic note (Scale7ChordDegree) — no %7 wrapper."""
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_tones(d, lo=48, hi=84):
    """Absolute chord-tone set for 1-based degree d in [lo, hi]."""
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
# Phase 1: Spiking Neural Network (Izhikevich) -> raw events
# ---------------------------------------------------------------------------
# 12 tonotopic pitch-class columns (pc 0..11 = C..B), N neurons each (RS).
# F-major scale tones get a higher base drive (prefrontal mode knowledge);
# chromatic columns get a higher tension_bias (insula drives chromaticity).
SCALE_COLS = [pc for pc in range(12) if pc in KEY_PCS]     # {0,2,4,5,7,9}
CHROM_COLS = [pc for pc in range(12) if pc not in KEY_PCS]  # {1,3,6,8,10,11}


def simulate_snn(dt=0.5, n_per_col=8, threshold=2):
    """Simulate the multi-column SNN, return raw events (float pitch, off-grid)."""
    C = 12
    # RS neuron params (Izhikevich): a, b, c, d
    a, b, c_, d_ = 0.02, 0.2, -65.0, 8.0
    v = np.full((C, n_per_col), -65.0)
    u = np.full((C, n_per_col), b * -65.0)

    base = np.zeros(C)
    for pc in SCALE_COLS:
        base[pc] = 6.0
    for pc in CHROM_COLS:
        base[pc] = 3.2
    tension_bias = np.zeros(C)
    for pc in CHROM_COLS:
        tension_bias[pc] = 5.0       # chromatic columns light up under tension
    tension_bias[4] = 2.0            # leading tone E (in scale) also lifts

    # spike accumulation per column
    spikes = [[] for _ in range(C)]

    steps = int(TOTAL_MS / dt)
    two_pi = 2.0 * np.pi
    # precompute theta/gamma over time is large; compute inline per step
    noise = NPRNG.normal(0.0, 1.0, (steps, C))  # per-step per-column noise

    for s in range(steps):
        t = s * dt
        _si, tension, _oct = section_at(t)
        theta = np.sin(two_pi * t / BAR_MS)
        gamma = np.sin(two_pi * t / SIXTEENTH_MS)
        gate = 0.5 + 0.5 * theta                    # gamma gated by theta
        I = (base
             + 4.0 * theta
             + 3.0 * gate * gamma
             + tension * tension_bias
             + 2.0 * noise[s])
        Iv = I[:, None]                             # (C,1) -> broadcast (C,N)
        v = v + (0.04 * v * v + 5.0 * v + 140.0 - u + Iv) * dt
        u = u + a * (b * v - u) * dt
        fired = v >= 30.0
        if fired.any():
            v = np.where(fired, c_, v)
            u = np.where(fired, u + d_, u)
            for cc in range(C):
                idx = np.nonzero(fired[cc])[0]
                if idx.size:
                    spikes[cc].extend([t] * idx.size)

    # ---- decode spike trains -> raw events (jittered gamma windows) -------
    events = []
    t = 0.0
    while t < TOTAL_MS - SIXTEENTH_MS:
        w = SIXTEENTH_MS * (1.0 + NPRNG.uniform(-0.12, 0.12))
        w = max(20.0, min(SIXTEENTH_MS * 1.3, w))
        counts = np.array([sum(1 for sp in spikes[cc] if t <= sp < t + w)
                           for cc in range(C)])
        winner_rate = int(counts.max())
        if winner_rate >= threshold:
            winner = int(np.argmax(counts))
            rate = counts[winner]
            _si, _tension, oct_base = section_at(t)
            pitch = float(oct_base + winner + NPRNG.uniform(-0.35, 0.35))
            vel = int(np.clip(64 + 22 * (rate - 1), 58, 122))
            events.append({"pitch": pitch, "start": t, "dur": w, "vel": vel})
        t += w
    return events


def build_phase1(raw_events):
    """Phase 1: single voice (Lead), raw unquantized units, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
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
SQ = ScaleQuantizer(root=53, scale="major")   # F major anchored at F3


def process_lead(raw_events):
    """Tiered quantize (strong=scale+chord, weak=scale) + grid snap + ornaments."""
    events = []
    for e in raw_events:
        s = snap(e["start"] / MS_PER_TICK)
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = min(TOTAL_BARS - 1, s // BAR)
        degree = BAR_DEGREES[bar]
        w = classify_weight(s, STRONG, BAR)
        ct = chord_tones(degree, lo=48, hi=84)
        p = SQ.tiered_quantize(e["pitch"], weight=w, chord_tones=ct)
        p = max(48, min(84, p))
        ev = MusicEvent(pitch=p, volume=e["vel"], start_tick=s,
                        end_tick=min(TOTAL_TICKS, s + GRID))
        # carry the structural tags for the tiered audit (dropped by to_midi)
        ev.weight = w
        events.append(ev)

    # dedup collided (start_tick, pitch) -> keep longest
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    events = sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))

    # funk phrasing-thinning: keep strong beats + all beat/'and' slots,
    # drop ~35% of the off-16th 'e'/'a' notes -> rests + ornament room
    thinned = []
    for e in events:
        if classify_weight(e.start_tick, STRONG, BAR) == "strong":
            thinned.append(e)
            continue
        slot16 = (e.start_tick % BAR) // GRID
        if slot16 % 2 == 0:                    # beats 0,4,8,12 + 'and' 2,6,10,14
            thinned.append(e)
            continue
        if RNG.random() < 0.35:                # off-16th: drop ~1/3
            continue
        thinned.append(e)
    events = thinned

    # voice-leading: break parallel perfect 5ths/octaves (adjacent onsets)
    fixed = []
    for e in events:
        if fixed:
            prev = fixed[-1]
            gap = e.start_tick - prev.end_tick
            if abs(e.pitch - prev.pitch) in (5, 7, 12) and gap < TPB:
                bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
                tones = chord_tones(BAR_DEGREES[bar], lo=48, hi=84)
                cands = [t for t in tones
                         if t != e.pitch and abs(t - prev.pitch) not in (5, 7, 12)]
                if cands:
                    e.pitch = min(cands, key=lambda t: abs(t - e.pitch))
        fixed.append(e)

    # tagged chromatic approach ornaments (lead MAY carry tagged ornaments):
    # a half-step-below approach into strong chord tones, only when chromatic
    # and the prior 16th slot is free. Deterministic (every 2nd eligible) ->
    # tag weight=weak + ornament=approach + resolve_pitch=target.
    events = fixed
    used_slots = {e.start_tick for e in events}
    ornaments = []
    eligible = 0
    for e in events:
        if classify_weight(e.start_tick, STRONG, BAR) != "strong":
            continue
        approach = e.pitch - 1
        if (approach % 12) in KEY_PCS:
            continue                      # not chromatic, skip (stays in-scale)
        slot = e.start_tick - GRID
        if slot < 0 or slot in used_slots:
            continue
        eligible += 1
        if eligible % 2 != 0:
            continue                      # keep sparse: every 2nd eligible
        oe = MusicEvent(pitch=approach, volume=max(50, e.volume - 10),
                        start_tick=slot, end_tick=e.start_tick)
        oe.weight = "weak"
        oe.ornament = "approach"
        oe.resolve_pitch = e.pitch
        ornaments.append(oe)
        used_slots.add(slot)
    return sorted(events + ornaments, key=lambda e: (e.start_tick, e.pitch))


def build_bass_events():
    """Funk 16th-note syncopated bass (root/5th/octave, all chord tones)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=41)          # F2 region
        fifth = root + 7
        octv = root + 12
        t0 = bar * BAR
        # 16 sixteenth slots; (slot, note) pattern (syncopated funk line)
        pat = [(0, root), (3, octv), (4, root), (6, fifth), (8, root),
               (11, fifth), (12, root), (14, fifth), (15, root)]
        for slot, note in pat:
            t = t0 + slot * GRID
            vel = 96 if slot in (0, 8) else 78
            events.append(MusicEvent(pitch=note, volume=vel,
                                     start_tick=t, end_tick=t + GRID))
    return events


def build_guitar_events():
    """Clean electric 16th 'chicken scratch' comp (chord tones, off-beats)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=53)           # F3 close voicing
        voicing = sorted(root + iv for iv in QUALITY[d])
        t0 = bar * BAR
        for slot in (2, 5, 6, 10, 13, 14):       # off-beat scratch slots
            t = t0 + slot * GRID
            for j, n in enumerate(voicing):
                events.append(MusicEvent(pitch=n, volume=52 + 4 * j,
                                         start_tick=t, end_tick=t + GRID // 2))
    return events


def build_brass_events():
    """Brass section stabs (short chord voicing, syncopated hits)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=65)           # F4 punchy register
        voicing = sorted(root + iv for iv in QUALITY[d])
        t0 = bar * BAR
        for slot in (6, 14):                     # 'and' of 2 and 'and' of 4
            t = t0 + slot * GRID
            for n in voicing:
                events.append(MusicEvent(pitch=n, volume=86,
                                         start_tick=t, end_tick=t + GRID // 2))
    return events


def build_drums_events():
    """Funk groove: syncopated kick, backbeat snare, 16th hats."""
    events = []
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        # kick: 1, 'a' of 2, 3 (+ occasional 'a' of 4)
        for slot in (0, 7, 8):
            events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=100,
                                     start_tick=t0 + slot * GRID,
                                     end_tick=t0 + slot * GRID + GRID))
        if bar % 2 == 1:
            events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=88,
                                     start_tick=t0 + 15 * GRID,
                                     end_tick=t0 + 15 * GRID + GRID))
        # snare backbeat on 2 & 4
        for slot in (4, 12):
            events.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=86,
                                     start_tick=t0 + slot * GRID,
                                     end_tick=t0 + slot * GRID + GRID))
        # 16th closed hats, accents on the beats
        for slot in range(16):
            vel = 60 if slot % 4 == 0 else 40
            events.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT, volume=vel,
                                     start_tick=t0 + slot * GRID,
                                     end_tick=t0 + slot * GRID + GRID // 2))
        # open hat on 'and' of 4 (slot 14) — GM 46
        events.append(MusicEvent(pitch=46, volume=70,
                                 start_tick=t0 + 14 * GRID,
                                 end_tick=t0 + 15 * GRID))
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


def build_phase2(lead_ev, guitar_ev, brass_ev, bass_ev, drums_ev):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=7, channel=0)        # Clavinet
    comp.add_voice("Guitar", program=27, channel=1)     # Clean Electric
    comp.add_voice("Brass", program=61, channel=2)      # Brass Section
    comp.add_voice("Bass", program=33, channel=3)       # Electric Bass
    comp.add_voice("Drums", program=0, channel=9)

    for name, bars, prog, tension, octv in SECTIONS:
        comp.add_section(name, bars=bars)

    vmap = {"Lead": lead_ev, "Guitar": guitar_ev, "Brass": brass_ev,
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


def run_tiered_audit(lead_ev, guitar_ev, brass_ev, bass_ev):
    """Tiered pitch discipline audit (Phase 3 P1) on the 4 pitched voices."""
    scale_pcs = sorted(KEY_PCS)
    chord_by_bar = {b: chord_pcs(BAR_DEGREES[b]) for b in range(TOTAL_BARS)}
    voices = {"Lead": lead_ev, "Guitar": guitar_ev, "Brass": brass_ev,
              "Bass": bass_ev}
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
    raw_events = simulate_snn()
    print("SNN raw events:", len(raw_events))

    # ---- Phase 1 raw draft (single voice) ----------------------------------
    phase1 = build_phase1(raw_events)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.method.109_snn_spiking_phase1",
        sources=[],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "rondo A-B-A-C-A", "style": STYLE,
                    "method": "109 SNN-C (Izhikevich, theta-gamma, STDP-decode)"},
        notes="Raw Izhikevich SNN spike-train decode: 12 tonotopic columns, "
              "theta (bar) + gamma (16th) clock, insula tension envelope. "
              "Float pitch, off-grid onsets, single voice, pre-rules.")
    write_grid_visualization(
        phase1.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
        voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2 rules post-process (5 voices) ----------------------------
    lead_ev = process_lead(raw_events)
    guitar_ev = build_guitar_events()
    brass_ev = build_brass_events()
    bass_ev = build_bass_events()
    drums_ev = build_drums_events()

    phase2 = build_phase2(lead_ev, guitar_ev, brass_ev, bass_ev, drums_ev)

    # ---- tiered pitch-discipline audit (Phase 3 P1) -----------------------
    tiered = run_tiered_audit(lead_ev, guitar_ev, brass_ev, bass_ev)
    if not tiered["all_pass"]:
        print("TIERED_AUDIT_FAIL:", json.dumps(tiered, indent=2))
        raise RuntimeError("tiered pitch audit failed — see pitch_audit.json")
    with open(os.path.join(ANALYSIS_DIR, "pitch_audit.json"), "w") as f:
        json.dump(tiered, f, indent=2)
    print("TIERED_AUDIT:", json.dumps(tiered, indent=2))

    # ---- dual-version export (perfect + humanized) ------------------------
    hz_instruments = {
        "Lead":   (None, 5.0, None, 0.015),   # clavinet melodic
        "Guitar": (None, 6.0, None, 0.02),    # clean electric comp
        "Brass":  (None, 8.0, None, 0.02),    # brass stabs
        "Bass":   (5.0, 4.0, 8.0, 0.01),      # lays back 8 ms
        "Drums":  (2.0, 4.0, 0.0, 0.008),     # anchors grid
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    provenance_params = {
        "bpm": BPM, "key": "F", "mode": "major", "style": STYLE,
        "form": "rondo A-B-A-C-A", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "method": "109 SNN-C", "layer": "concrete", "paradigm": "Nature-Led",
        "voices": [["Lead", "Clavinet", 7], ["Guitar", "Clean Electric", 27],
                   ["Brass", "Brass Section", 61], ["Bass", "Electric Bass", 33],
                   ["Drums", "ch9", 0]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered quantize + grid snap + "
        "dedup + voice-leading + tagged ornaments) (method 109 SNN-C)",
        sources=[phase1_mid],
        parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (rondo, 20 bars).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 109 SNN-C)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style funk + per-instrument DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=["Lead", "Guitar", "Brass", "Bass", "Drums"], bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- summary -----------------------------------------------------------
    summary = {
        "style": STYLE, "genre": "Funk",
        "method": "109 SNN-C", "method_layer": "concrete",
        "method_paradigm": "Nature-Led",
        "form": "rondo A-B-A-C-A", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "snr_raw_events": len(raw_events),
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

    print("LEAD_EVENTS:", len(lead_ev), "GUITAR:", len(guitar_ev),
          "BRASS:", len(brass_ev), "BASS:", len(bass_ev),
          "DRUMS:", len(drums_ev))


if __name__ == "__main__":
    main()
