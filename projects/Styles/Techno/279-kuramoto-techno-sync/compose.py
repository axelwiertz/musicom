# -*- coding: utf-8 -*-
"""279 - Kuramoto Techno Sync (Method 038 KOPS, two-phase architecture).

Nightly composition job (2026-11-01). Selection (seed = nightly date 20261101):
  style   = Techno  (random draw from /opt/data/projects/Styles/ genre dirs)
  method  = 038 Kuramoto Oscillator Phase Synchronization (KOPS)  [concrete, Nature-Led]
  key     = A minor (aeolian)
  form    = intro-break-drop-outro  (Intro 4 / Break 8 / Drop 8 / Outro 4 = 24 bars)
  bpm     = 128

Two-phase architecture:
  Phase 1 (raw): a population of N coupled phase oscillators (the Kuramoto
    model, dtheta_i/dt = omega_i + (K/N) sum_j sin(theta_j - theta_i), via the
    mean-field r*exp(i*psi) trick). Each oscillator maps to a diatonic pitch
    row (A2..up two octaves of A natural minor); each phase wrapping of 2*pi
    fires a raw note. The coupling K is arced by a "composer's hand":
      intro 0.7 (desynchronized texture) -> break 0.7..2.8 (partial entrainment,
      emergent polyrhythmic lock-in) -> drop 3.5 (full phase-lock, unified
      driving pulse) -> outro 3.5..0.7 (decay). Velocity scales with the local
      order parameter r. Raw: float pitch + chromatic jitter, off-grid onsets,
      single voice, NO harmony -> own composer + validate() gate.

  Phase 2 (rules): weight-aware tiered pitch discipline (classify_weight ->
    tiered_quantize: strong = scale+chord, weak = scale), 16th grid snap,
    dedup, voice-leading (parallel 5th/octave break), tagged chromatic approach
    ornaments on the lead, and a 5-voice techno texture:
      Lead=Synth Voice (Kuramoto cascade), Harmony=Synth Brass 1 (strong-beat
      rave stabs), Pad=Synth Pad (sustained), Bass=Synth Bass 1 (driving 8th
      root pulse), Drums=Drum Kit ch9 (four-on-floor kick + offbeat hats +
      claps on 2 & 4).

  Dual-version contract: export_dual -> -perfect.mid (grid-locked) +
    -humanized.mid (style techno + per-instrument DNA).
"""
import json
import os
import hashlib
import random
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree
from sound.synthesis.scale_quantizer import (ScaleQuantizer, STRONG_GRID,
                                             classify_weight)
from workflows.pitch_audit import audit_voice

INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (SYNTH_VOICE, SYNTH_BRASS_1,  # noqa: E402
                                 SYNTH_PAD, SYNTH_BASS_1, DRUM_KIT)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Techno"
STYLE = "techno"
PROJECT = "279-kuramoto-techno-sync"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 128
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR                 # 1920
GRID = 120                                # 16th note (8th = 240)
EIGHTH = 240
TOTAL_BARS = 24
TOTAL_TICKS = TOTAL_BARS * BAR            # 46080
STRONG = STRONG_GRID["4/4"]               # (0, 960) beats 1 & 3
TICK_RATE = TPB * BPM / 60.0              # 1024.0 ticks/sec

KEY_NAME = "A minor (aeolian)"
TONIC_PC = 9                              # A
KEY_PCS = {9, 11, 0, 2, 4, 5, 7}          # A B C D E F G
INTERVALS = [0, 2, 3, 5, 7, 8, 10]        # natural-minor offsets from A
TONIC_BASE = 45                           # A2 (diatonic reference + quantizer root)

# 1-based degree -> triad quality intervals (A natural minor diatonic)
QUALITY = {1: (0, 3, 7), 2: (0, 3, 6), 3: (0, 4, 7), 4: (0, 3, 7),
           5: (0, 3, 7), 6: (0, 4, 7), 7: (0, 4, 7)}
DEGREE_NAMES = {1: "Am", 2: "Bdim", 3: "C", 4: "Dm", 5: "Em", 6: "F", 7: "G"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 20261101                        # the nightly selection seed
RNG = random.Random(raw_seed)              # phase-2 post-processing (thin/ornaments)
NPRNG = np.random.default_rng(raw_seed)    # phase-1 generative drive (natural freqs)

# ---------------------------------------------------------------------------
# Form: intro-break-drop-outro (4/8/8/4 bars = 24 bars).
# (name, bars, progression [1-based degrees])
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Intro", 4, [1, 1, 6, 7]),                # i - i - bVI - bVII
    ("Break", 8, [1, 6, 3, 7, 1, 6, 3, 7]),    # i - bVI - bIII - bVII (x2)
    ("Drop",  8, [1, 6, 1, 7, 1, 6, 1, 7]),    # i - bVI - i - bVII (x2)
    ("Outro", 4, [1, 6, 7, 1]),                # i - bVI - bVII - i
]
SECTION_START = {}
_acc = 0
for name, bars, prog in SECTIONS:
    SECTION_START[name] = _acc
    _acc += bars
assert _acc == TOTAL_BARS

BAR_DEGREES = []
for name, bars, prog in SECTIONS:
    BAR_DEGREES.extend(prog)
assert len(BAR_DEGREES) == TOTAL_BARS


def bars_to_sec(nbars):
    return nbars * BEATS_PER_BAR * (60.0 / BPM)


def diatonic(deg_index, base=TONIC_BASE):
    """Canonical diatonic note (Scale7ChordDegree) — no %%7 wrapper."""
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_tones(d, lo=36, hi=96):
    """Absolute chord-tone set for 1-based degree d in [lo, hi]."""
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    out = set()
    for octv in range(-3, 11):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def pitch_row(r):
    """Oscillator index -> diatonic pitch (rows = scale degrees above A2)."""
    return Scale7ChordDegree.get_diatonic_note(TONIC_BASE, INTERVALS, r)


def snap(t):
    return int(round(t / float(GRID)) * GRID)


# ---------------------------------------------------------------------------
# Phase 1: Kuramoto oscillator ensemble -> raw firing events
# ---------------------------------------------------------------------------
N_OSC = 16                     # oscillator count (= pitch rows, A2..~two octaves)
OMEGA0 = 2.0 * np.pi * 0.6     # 0.6 Hz natural firing rate (uncoupled)
SPREAD = 0.30                  # natural-frequency dispersion (gauss)
DT = 0.002                     # integration step (seconds)

# section time boundaries (seconds) for the coupling arc
T_BREAK = bars_to_sec(4)       # 7.5 s
T_DROP = bars_to_sec(12)       # 22.5 s
T_OUTRO = bars_to_sec(20)      # 37.5 s
T_TOTAL = bars_to_sec(24)      # 45.0 s


def Kfn(t):
    """Composer's-hand coupling arc: desync -> partial lock -> full lock -> decay."""
    if t < T_BREAK:
        return 0.7
    if t < T_DROP:
        f = (t - T_BREAK) / (T_DROP - T_BREAK)
        return 0.7 + (2.8 - 0.7) * f
    if t < T_OUTRO:
        return 3.5
    f = (t - T_OUTRO) / (T_TOTAL - T_OUTRO)
    return 3.5 + (0.7 - 3.5) * f


def simulate_kuramoto():
    """Mean-field Kuramoto integration -> list of (t_sec, osc_index, order_param)."""
    omega = OMEGA0 * (1.0 + SPREAD * NPRNG.standard_normal(N_OSC))
    omega = np.maximum(omega, 0.05)
    theta = NPRNG.uniform(0.0, 2.0 * np.pi, N_OSC)
    events = []
    t = 0.0
    while t < T_TOTAL:
        z = np.exp(1j * theta).mean()
        r = abs(z)
        psi = np.angle(z)
        K = Kfn(t)
        theta += (omega + K * r * np.sin(psi - theta)) * DT
        fired = theta >= 2.0 * np.pi
        idx = np.nonzero(fired)[0]
        for i in idx:
            events.append((t, int(i), float(r)))
            theta[i] -= 2.0 * np.pi
        t += DT
    return events


def build_raw_lead(events):
    """Phase 1: single raw voice (Synth Voice). Off-grid onset, float pitch
    with chromatic jitter, velocity from local order parameter r."""
    raw = []
    for t, i, r in events:
        tick = int(round(t * TICK_RATE)) + RNG.randint(-40, 40)
        p = float(pitch_row(i) + RNG.choice([-1, 0, 0, 1]))
        vel = int(min(112, 58 + r * 44))
        raw.append({"pitch": p, "start": tick, "dur": EIGHTH,
                    "vel": vel, "row": i, "r": r})
    raw.sort(key=lambda e: (e["start"], e["pitch"]))
    return raw


def rel_events(abs_events, s_start, s_len):
    """Shift absolute events into a section's relative tick frame + landmark."""
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
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=max(0, s_len - 10), end_tick=s_len))
    return out


def build_phase1(raw_events):
    """Phase 1: single voice (Lead), raw unquantized units, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=SYNTH_VOICE.midi_program, channel=0)
    for name, bars, prog in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog in SECTIONS:
        s_start = SECTION_START[name] * BAR
        s_ticks = bars * BAR
        seg = []
        for e in raw_events:
            if s_start <= e["start"] < s_start + s_ticks:
                p = int(round(e["pitch"]))
                p = max(36, min(96, p))
                seg.append(MusicEvent(pitch=p, volume=e["vel"],
                                      start_tick=int(round(e["start"])),
                                      end_tick=int(round(e["start"] + e["dur"]))))
        seg.sort(key=lambda e: e.start_tick)
        comp.fill_voice_section("Lead", name,
                                MusicUnit(events=rel_events(seg, s_start, s_ticks)))
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# Phase 2: rules post-process (weight-aware tiered pitch discipline)
# ---------------------------------------------------------------------------
SQ = ScaleQuantizer(root=TONIC_BASE, scale="minor")   # A natural minor


def process_lead(raw_events):
    """Tiered quantize (strong=scale+chord, weak=scale) + grid snap + ornaments."""
    events = []
    for e in raw_events:
        s = snap(e["start"])
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = min(TOTAL_BARS - 1, s // BAR)
        degree = BAR_DEGREES[bar]
        w = classify_weight(s, STRONG, BAR)
        ct = chord_tones(degree, lo=48, hi=88)
        p = SQ.tiered_quantize(e["pitch"], weight=w, chord_tones=ct)
        p = max(48, min(88, p))
        ev = MusicEvent(pitch=p, volume=e["vel"], start_tick=s,
                        end_tick=min(TOTAL_TICKS, s + GRID))
        ev.weight = w
        events.append(ev)

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
                tones = chord_tones(BAR_DEGREES[bar], lo=48, hi=88)
                cands = [t for t in tones
                         if t != e.pitch and abs(t - prev.pitch) not in (5, 7, 12)]
                if cands:
                    e.pitch = min(cands, key=lambda t: abs(t - e.pitch))
        fixed.append(e)
    events = fixed

    # tagged chromatic approach ornaments (lead MAY carry tagged ornaments)
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


def build_harmony():
    """Synth Brass 1 rave stabs on strong beats 1 & 3 (grid-locked, in-chord)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        tones = chord_tones(d, lo=53, hi=72)
        voicing = tones[:3]
        t0 = bar * BAR
        for beat in (0, 960):
            t = t0 + beat
            for n in voicing:
                events.append(MusicEvent(pitch=n, volume=60, start_tick=t,
                                         end_tick=t + EIGHTH))
    return events


def build_pad():
    """Synth Pad sustained whole-bar chord (only in Break/Drop/Outro for arc)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        tones = chord_tones(d, lo=48, hi=72)
        t0 = bar * BAR
        for n in tones[:3]:
            events.append(MusicEvent(pitch=n, volume=44, start_tick=t0,
                                     end_tick=t0 + BAR))
    return events


def build_bass():
    """Synth Bass 1 driving 8th-note root pulse (techno engine)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=33)          # A1 region
        t0 = bar * BAR
        for k in range(8):                        # 8th notes
            t = t0 + k * EIGHTH
            vel = 86 if k % 2 == 0 else 74        # accent on beats
            events.append(MusicEvent(pitch=root, volume=vel,
                                     start_tick=t, end_tick=t + 200))
    return events


def build_drums():
    """Drum kit (ch9): four-on-floor kick, offbeat hats, clap on 2 & 4."""
    events = []
    KICK, CLAP, CHAT, OHAT = 36, 39, 42, 46
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        for beat in (0, 480, 960, 1440):            # four-on-floor
            events.append(MusicEvent(pitch=KICK, volume=100,
                                     start_tick=t0 + beat, end_tick=t0 + beat + 120))
        for beat in (480, 1440):                    # clap on 2 & 4
            events.append(MusicEvent(pitch=CLAP, volume=80,
                                     start_tick=t0 + beat, end_tick=t0 + beat + 100))
        for off in (240, 720, 1200, 1680):          # offbeat hats
            events.append(MusicEvent(pitch=CHAT, volume=60,
                                     start_tick=t0 + off, end_tick=t0 + off + 60))
        events.append(MusicEvent(pitch=OHAT, volume=58,       # open hat end of bar
                                 start_tick=t0 + 1680, end_tick=t0 + 1680 + 180))
    return events


def build_phase2(lead_ev, harmony_ev, pad_ev, bass_ev, drum_ev):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=SYNTH_VOICE.midi_program, channel=0)
    comp.add_voice("Harmony", program=SYNTH_BRASS_1.midi_program, channel=1)
    comp.add_voice("Pad", program=SYNTH_PAD.midi_program, channel=2)
    comp.add_voice("Bass", program=SYNTH_BASS_1.midi_program, channel=3)
    comp.add_voice("Drums", program=DRUM_KIT.midi_program, channel=9)

    for name, bars, prog in SECTIONS:
        comp.add_section(name, bars=bars)

    vmap = {"Lead": lead_ev, "Harmony": harmony_ev, "Pad": pad_ev,
            "Bass": bass_ev, "Drums": drum_ev}
    for name, bars, prog in SECTIONS:
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


def run_tiered_audit(lead_ev, harmony_ev, pad_ev, bass_ev):
    """Tiered pitch discipline audit (Phase 3 P1) on the 4 pitched voices."""
    scale_pcs = sorted(KEY_PCS)
    chord_by_bar = {b: chord_pcs(BAR_DEGREES[b]) for b in range(TOTAL_BARS)}
    voices = {"Lead": lead_ev, "Harmony": harmony_ev, "Pad": pad_ev, "Bass": bass_ev}
    report = {}
    all_pass = True
    for vname, ev in voices.items():
        r = audit_voice(ev, scale_pcs, chord_pcs_by_bar=chord_by_bar,
                        strong_grid=STRONG, bar_ticks=BAR, grid=EIGHTH)
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


def count_offgrid(events, grid=120):
    off = sum(1 for e in events if e.pitch > 0 and e.start_tick % grid != 0)
    return off, sum(1 for e in events if e.pitch > 0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    events = simulate_kuramoto()
    print("Kuramoto firings:", len(events))

    raw_events = build_raw_lead(events)
    print("Phase-1 raw lead events:", len(raw_events))

    # per-section raw density
    for name, bars, prog in SECTIONS:
        s0 = SECTION_START[name] * BAR
        s1 = s0 + bars * BAR
        cnt = sum(1 for e in raw_events if s0 <= e["start"] < s1)
        rbar = [e["r"] for e in raw_events if s0 <= e["start"] < s1]
        rmean = float(np.mean(rbar)) if rbar else 0.0
        print(f"  {name}: {cnt} raw events, mean r={rmean:.3f}")

    # ---- Phase 1 raw draft (single voice) ----------------------------------
    phase1 = build_phase1(raw_events)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.method.038_kuramoto_phase1",
        sources=[],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "intro-break-drop-outro", "style": STYLE,
                    "method": "038 KOPS (Kuramoto, N=16 mean-field, K arc 0.7->3.5)"},
        notes="Raw Kuramoto ensemble: 16 coupled phase oscillators over 24 bars; "
              "coupling arc desync->partial-lock->full-lock->decay; velocity from "
              "order parameter. Float pitch + chromatic jitter, off-grid onsets, "
              "single voice, pre-rules.")
    write_grid_visualization(
        phase1.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
        voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2 rules post-process (5 voices) ----------------------------
    lead_ev = process_lead(raw_events)
    harmony_ev = build_harmony()
    pad_ev = build_pad()
    bass_ev = build_bass()
    drum_ev = build_drums()

    phase2 = build_phase2(lead_ev, harmony_ev, pad_ev, bass_ev, drum_ev)

    # ---- tiered pitch-discipline audit (Phase 3 P1) -----------------------
    tiered = run_tiered_audit(lead_ev, harmony_ev, pad_ev, bass_ev)
    if not tiered["all_pass"]:
        print("TIERED_AUDIT_FAIL:", json.dumps(tiered, indent=2))
        raise RuntimeError("tiered pitch audit failed — see pitch_audit.json")
    with open(os.path.join(ANALYSIS_DIR, "pitch_audit.json"), "w") as f:
        json.dump(tiered, f, indent=2)
    print("TIERED_AUDIT:", json.dumps(tiered, indent=2))

    # ---- grid audit on the phase-2 event lists (perfect layer) ------------
    off, tot = count_offgrid(lead_ev + harmony_ev + pad_ev + bass_ev + drum_ev)
    print(f"Perfect-layer off-grid (all voices incl drums): {off}/{tot}")
    assert off == 0, f"perfect layer has {off} off-grid onsets"

    # ---- dual-version export (perfect + humanized) ------------------------
    hz_instruments = {
        "Lead": SYNTH_VOICE.humanize_dna,
        "Harmony": SYNTH_BRASS_1.humanize_dna,
        "Pad": SYNTH_PAD.humanize_dna,
        "Bass": SYNTH_BASS_1.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    provenance_params = {
        "bpm": BPM, "key": "A", "mode": "aeolian", "style": STYLE,
        "form": "intro-break-drop-outro", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "method": "038 KOPS", "layer": "concrete", "paradigm": "Nature-Led",
        "voices": [["Lead", "Synth Voice", SYNTH_VOICE.midi_program],
                   ["Harmony", "Synth Brass 1", SYNTH_BRASS_1.midi_program],
                   ["Pad", "Synth Pad", SYNTH_PAD.midi_program],
                   ["Bass", "Synth Bass 1", SYNTH_BASS_1.midi_program],
                   ["Drums", "Drum Kit", DRUM_KIT.midi_program, 9]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered quantize + grid snap + "
        "dedup + voice-leading + tagged ornaments) (method 038 KOPS)",
        sources=[phase1_mid],
        parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (intro-break-drop-outro, 24 bars).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 038 KOPS)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style techno + per-instrument DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=["Lead", "Harmony", "Pad", "Bass", "Drums"], bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- summary -----------------------------------------------------------
    summary = {
        "style": STYLE, "genre": GENRE,
        "method": "038 KOPS", "method_layer": "concrete",
        "method_paradigm": "Nature-Led",
        "form": "intro-break-drop-outro", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "kuramoto_firings": len(events),
        "raw_events": len(raw_events),
        "oscillators": N_OSC, "omega0_hz": OMEGA0 / (2 * np.pi),
        "phase1_path": phase1_mid,
        "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "progression": {s[0]: [DEGREE_NAMES[d] for d in s[2]] for s in SECTIONS},
    }
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("LEAD:", len(lead_ev), "HARMONY:", len(harmony_ev), "PAD:", len(pad_ev),
          "BASS:", len(bass_ev), "DRUMS:", len(drum_ev))


if __name__ == "__main__":
    main()