# -*- coding: utf-8 -*-
"""281 - Voice-Leading Graph Pop (Method 011 VLG, two-phase architecture).

Nightly composition job (2026-11-02). Selection (seed = nightly date 20261102):
  style   = Pop  (random draw from /opt/data/projects/Styles/ genre dirs)
  method  = 011 Voice-Leading Graph Search (VLG)  [concrete, Rules-Based]
  key     = C major (ionian)
  form    = intro-verse-chorus-bridge-outro  (4/8/8/4/4 = 28 bars)
  bpm     = 118

Two-phase architecture:
  Phase 1 (raw): the diatonic Neo-Riemannian voice-leading graph over the
    seven C-major triads (edges = R relative / L leading-tone exchange /
    plagal / authentic moves). A weighted graph walk (seeded) generates a
    28-bar chord sequence — section anchors steer each walk toward its
    cadence degree (intro->V, verse->IV, chorus->I, bridge->V, outro->I).
    The raw draft is the audible VOICE-LEADING LINE: at each chord change
    the minimal-movement voice note is emitted, plus a 4-note arpeggio of
    the triad, all as float pitch + chromatic jitter + off-grid onsets,
    single voice, NO harmony -> own composer + validate() gate.

  Phase 2 (rules): weight-aware tiered pitch discipline (classify_weight ->
    tiered_quantize: strong = scale+chord, weak = scale), 16th grid snap,
    dedup, voice-leading (parallel 5th/octave break), tagged chromatic
    approach ornaments on the lead, and a 5-voice pop texture:
      Lead=Piano (voice-leading melody), Harmony=Rhodes (comping stabs),
      Pad=Synth Pad (sustained), Bass=Electric Bass (8th root/octave pulse),
      Drums=Drum Kit ch9 (pop backbeat: kick 1&3, snare 2&4, 8th hats).

  Dual-version contract: export_dual -> -perfect.mid (grid-locked) +
    -humanized.mid (style pop + per-instrument DNA).
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
from instrument_registry import (PIANO, RHODES, SYNTH_PAD, ELECTRIC_BASS,  # noqa: E402
                                 DRUM_KIT)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Pop"
STYLE = "pop"
PROJECT = "281-voice-leading-graph-pop"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 118
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR                 # 1920
GRID = 120                                # 16th note (8th = 240)
EIGHTH = 240
TOTAL_BARS = 28
TOTAL_TICKS = TOTAL_BARS * BAR            # 53760
STRONG = STRONG_GRID["4/4"]               # (0, 960) beats 1 & 3

KEY_NAME = "C major (ionian)"
TONIC_PC = 0                              # C
KEY_PCS = {0, 2, 4, 5, 7, 9, 11}          # C D E F G A B
INTERVALS = [0, 2, 4, 5, 7, 9, 11]        # major offsets from C
TONIC_BASE = 60                           # C4 (quantizer root)

# 1-based degree -> triad quality intervals (C major diatonic)
QUALITY = {1: (0, 4, 7), 2: (0, 3, 7), 3: (0, 3, 7), 4: (0, 4, 7),
           5: (0, 4, 7), 6: (0, 3, 7), 7: (0, 3, 6)}
DEGREE_NAMES = {1: "C", 2: "Dm", 3: "Em", 4: "F", 5: "G", 6: "Am", 7: "Bdim"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = 20261102                        # the nightly selection seed
RNG = random.Random(raw_seed)              # phase-2 post-processing (ornaments)
NPRNG = np.random.default_rng(raw_seed)    # phase-1 generative drive (graph walk)

# ---------------------------------------------------------------------------
# Voice-leading graph (Neo-Riemannian diatonic, in-key)
#   1=I  2=ii  3=iii  4=IV  5=V  6=vi  7=vii*
#   R (relative):      I<->vi, IV<->ii, V<->iii
#   L (leading-tone):  I<->iii, IV<->vi, V<->vii*
#   + plagal IV->I, authentic V->I, subdominant I->IV, deceptive V->vi, etc.
# ---------------------------------------------------------------------------
VOICE_LEAD_GRAPH = {
    1: [6, 3, 4, 5],   # I  -> vi(R), iii(L), IV, V
    2: [5, 4],         # ii -> V, IV(R)
    3: [6, 4, 1],      # iii-> vi, IV, I(L)
    4: [2, 1, 5],      # IV -> ii(R), I(plagal), V
    5: [1, 3, 6],      # V  -> I(auth), iii(R), vi(deceptive)
    6: [4, 2, 5, 1],   # vi -> IV(L/R), ii, V, I
    7: [1],            # vii* -> I
}

# Form: (name, bars, start_degree, target_degree)
SECTIONS = [
    ("Intro",  4, 1, 5),    # I ... -> V (half cadence into verse)
    ("Verse",  8, 1, 4),    # I ... -> IV (axis loop, leads to chorus)
    ("Chorus", 8, 4, 1),    # IV ... -> I (authentic close)
    ("Bridge", 4, 6, 5),    # vi ... -> V (dominant prep)
    ("Outro",  4, 4, 1),    # IV ... -> I (plagal->authentic close)
]

SECTION_START = {}
_acc = 0
for name, bars, s, t in SECTIONS:
    SECTION_START[name] = _acc
    _acc += bars
assert _acc == TOTAL_BARS


def bfs_dist(a, b):
    if a == b:
        return 0
    seen = {a}
    frontier = [a]
    d = 0
    while frontier:
        d += 1
        nxt = []
        for n in frontier:
            for m in VOICE_LEAD_GRAPH[n]:
                if m == b:
                    return d
                if m not in seen:
                    seen.add(m)
                    nxt.append(m)
        frontier = nxt
    return 99


def graph_walk(start, target, bars, rng):
    """Weighted walk over the voice-leading graph from start toward target."""
    chords = [start]
    cur = start
    for i in range(1, bars):
        if i == bars - 1:
            nxt = target                      # force the cadence degree
        else:
            neigh = VOICE_LEAD_GRAPH[cur]
            dcur = bfs_dist(cur, target)
            weights = []
            for n in neigh:
                dn = bfs_dist(n, target)
                w = 4.0 if dn < dcur else 1.0
                if n == target:
                    w = 0.5                   # save the cadence for the last bar
                weights.append(w)
            nxt = rng.choices(neigh, weights=weights, k=1)[0]
        chords.append(nxt)
        cur = nxt
    return chords


# Generate the 28-bar progression via graph search
BAR_DEGREES = []
WALKS = {}
for name, bars, s, t in SECTIONS:
    walk = graph_walk(s, t, bars, RNG)
    WALKS[name] = list(walk)
    BAR_DEGREES.extend(walk)
assert len(BAR_DEGREES) == TOTAL_BARS


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


def triad_voicing(d, octave=0):
    """Root-position triad around C4 (lead/moving-voice reference)."""
    root_midi = 60 + INTERVALS[d - 1] + 12 * octave
    return [root_midi + iv for iv in QUALITY[d]]


def moving_voice(prev_degree, cur_degree):
    """The minimal-movement voice note between two triads (voice-leading line)."""
    pv = triad_voicing(prev_degree)
    cv = triad_voicing(cur_degree)
    common = set(p % 12 for p in pv) & set(c % 12 for c in cv)
    moving = [c for c in cv if (c % 12) not in common]
    if moving:
        return min(moving, key=lambda c: min(abs(c - p) for p in pv))
    return min(cv, key=lambda c: min(abs(c - p) for p in pv))


def snap(t):
    return int(round(t / float(GRID)) * GRID)


# ---------------------------------------------------------------------------
# Phase 1: graph-search voice-leading line -> raw firing events
# ---------------------------------------------------------------------------
def build_raw_lead():
    """Phase 1: single raw voice (Piano). Off-grid onset, float pitch with
    chromatic jitter, velocity shaped by bar position within the phrase."""
    raw = []
    for bar in range(TOTAL_BARS):
        degree = BAR_DEGREES[bar]
        t0 = bar * BAR
        voicing = triad_voicing(degree)
        # voice-leading note: minimal movement from the previous chord
        if bar == 0:
            vl = voicing[0]
        else:
            vl = moving_voice(BAR_DEGREES[bar - 1], degree)
        # per-bar raw note plan: [voice-leading, root, 3rd, 5th, octave, 5th]
        notes = [vl, voicing[0], voicing[1], voicing[2], voicing[0] + 12,
                 voicing[1]]
        slots = [0, 240, 480, 720, 960, 1440]       # rough 8th/16th grid
        for k, (n, slot) in enumerate(zip(notes, slots)):
            jit = RNG.randint(-40, 40)              # off-grid jitter
            tick = t0 + slot + jit
            if tick < 0 or tick >= TOTAL_TICKS:
                continue
            p = float(n + RNG.choice([-1, 0, 0, 1]))  # chromatic jitter
            vel = 74 if k in (0, 1) else 62
            raw.append({"pitch": p, "start": tick, "dur": EIGHTH - 40,
                        "vel": vel, "degree": degree, "kind": k})
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
    comp.add_voice("Lead", program=PIANO.midi_program, channel=0)
    for name, bars, s, t in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, s, t in SECTIONS:
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
SQ = ScaleQuantizer(root=TONIC_BASE, scale="major")   # C major


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
    """Rhodes comping stabs on strong beats 1 & 3 (grid-locked, in-chord)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        voicing = triad_voicing(d)
        t0 = bar * BAR
        for beat in (0, 960):
            t = t0 + beat
            for n in voicing:
                events.append(MusicEvent(pitch=n, volume=58, start_tick=t,
                                         end_tick=t + EIGHTH))
    return events


def build_pad():
    """Synth Pad sustained whole-bar chord (soft, full-length)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        voicing = [triad_voicing(d)[0] - 12, triad_voicing(d)[1] - 12,
                   triad_voicing(d)[2] - 12]
        t0 = bar * BAR
        for n in voicing:
            events.append(MusicEvent(pitch=n, volume=40, start_tick=t0,
                                     end_tick=t0 + BAR))
    return events


def build_bass():
    """Electric Bass driving 8th-note root/octave pulse (pop engine)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=36)          # C2 region
        t0 = bar * BAR
        for k in range(8):                        # 8th notes
            t = t0 + k * EIGHTH
            n = root if k % 2 == 0 else root + 12  # octave bounce on offbeats
            vel = 90 if k % 2 == 0 else 76        # accent on beats
            events.append(MusicEvent(pitch=n, volume=vel,
                                     start_tick=t, end_tick=t + 200))
    return events


def build_drums():
    """Drum kit (ch9): pop backbeat (kick 1&3, snare 2&4, 8th hats)."""
    events = []
    KICK, SNARE, CHAT, OHAT = 36, 38, 42, 46
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        for beat in (0, 960):                      # kick 1 & 3
            events.append(MusicEvent(pitch=KICK, volume=100,
                                     start_tick=t0 + beat, end_tick=t0 + beat + 120))
        for beat in (480, 1440):                   # snare 2 & 4
            events.append(MusicEvent(pitch=SNARE, volume=92,
                                     start_tick=t0 + beat, end_tick=t0 + beat + 100))
        for off in (0, 240, 480, 720, 960, 1200, 1440, 1680):   # 8th hats
            events.append(MusicEvent(pitch=CHAT, volume=58,
                                     start_tick=t0 + off, end_tick=t0 + off + 60))
        events.append(MusicEvent(pitch=OHAT, volume=55,       # open hat end of bar
                                 start_tick=t0 + 1680, end_tick=t0 + 1680 + 180))
    return events


def build_phase2(lead_ev, harmony_ev, pad_ev, bass_ev, drum_ev):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=PIANO.midi_program, channel=0)
    comp.add_voice("Harmony", program=RHODES.midi_program, channel=1)
    comp.add_voice("Pad", program=SYNTH_PAD.midi_program, channel=2)
    comp.add_voice("Bass", program=ELECTRIC_BASS.midi_program, channel=3)
    comp.add_voice("Drums", program=DRUM_KIT.midi_program, channel=9)

    for name, bars, s, t in SECTIONS:
        comp.add_section(name, bars=bars)

    vmap = {"Lead": lead_ev, "Harmony": harmony_ev, "Pad": pad_ev,
            "Bass": bass_ev, "Drums": drum_ev}
    for name, bars, s, t in SECTIONS:
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
    print("PROGRESSION per section:")
    for name, bars, s, t in SECTIONS:
        print(f"  {name}: {[DEGREE_NAMES[d] for d in WALKS[name]]}")

    raw_events = build_raw_lead()
    print("Phase-1 raw lead events:", len(raw_events))

    for name, bars, s, t in SECTIONS:
        s0 = SECTION_START[name] * BAR
        s1 = s0 + bars * BAR
        cnt = sum(1 for e in raw_events if s0 <= e["start"] < s1)
        print(f"  {name}: {cnt} raw events")

    # ---- Phase 1 raw draft (single voice) ----------------------------------
    phase1 = build_phase1(raw_events)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.method.011_voice_leading_graph_phase1",
        sources=[],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "intro-verse-chorus-bridge-outro", "style": STYLE,
                    "method": "011 VLG (Neo-Riemannian graph walk, weighted, "
                              "section cadence anchors)"},
        notes="Raw voice-leading graph search: weighted walk over the diatonic "
              "Neo-Riemannian graph (R/L/plagal/authentic edges) generates the "
              "28-bar chord sequence; the minimal-movement voice note + triad "
              "arpeggio is emitted as a single raw voice. Float pitch + "
              "chromatic jitter, off-grid onsets, pre-rules.")
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
        "Lead": PIANO.humanize_dna,
        "Harmony": RHODES.humanize_dna,
        "Pad": SYNTH_PAD.humanize_dna,
        "Bass": ELECTRIC_BASS.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    provenance_params = {
        "bpm": BPM, "key": "C", "mode": "ionian", "style": STYLE,
        "form": "intro-verse-chorus-bridge-outro", "bars": TOTAL_BARS,
        "sections": [s[0] for s in SECTIONS],
        "method": "011 VLG", "layer": "concrete", "paradigm": "Rules-Based",
        "progression": {s[0]: [DEGREE_NAMES[d] for d in WALKS[s[0]]]
                        for s in SECTIONS},
        "voices": [["Lead", "Piano", PIANO.midi_program],
                   ["Harmony", "Rhodes", RHODES.midi_program],
                   ["Pad", "Synth Pad", SYNTH_PAD.midi_program],
                   ["Bass", "Electric Bass", ELECTRIC_BASS.midi_program],
                   ["Drums", "Drum Kit", DRUM_KIT.midi_program, 9]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: tiered quantize + grid snap + "
        "dedup + voice-leading + tagged ornaments) (method 011 VLG)",
        sources=[phase1_mid],
        parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (intro-verse-chorus-bridge-outro, 28 bars).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (method 011 VLG)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style pop + per-instrument DNA).")

    # ---- grid visualization ------------------------------------------------
    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=["Lead", "Harmony", "Pad", "Bass", "Drums"], bpm=BPM)

    # ---- size asserts ------------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- summary -----------------------------------------------------------
    def _clean(v):
        if isinstance(v, dict):
            return {k: _clean(x) for k, x in v.items()}
        if isinstance(v, float):
            return round(v, 4)
        return v

    summary = {
        "style": STYLE, "genre": GENRE,
        "method": "011 VLG", "method_layer": "concrete",
        "method_paradigm": "Rules-Based",
        "form": "intro-verse-chorus-bridge-outro", "key": KEY_NAME, "bpm": BPM,
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "progression": {s[0]: [DEGREE_NAMES[d] for d in WALKS[s[0]]]
                        for s in SECTIONS},
        "raw_events": len(raw_events),
        "phase1_path": phase1_mid,
        "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "hz_seed": hz_seed,
        "hz": _clean({k: {kk: vv for kk, vv in v.items() if kk != "profile"}
                      for k, v in hz.items()}),
        "tiered_audit": tiered,
    }
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("LEAD:", len(lead_ev), "HARMONY:", len(harmony_ev), "PAD:", len(pad_ev),
          "BASS:", len(bass_ev), "DRUMS:", len(drum_ev))


if __name__ == "__main__":
    main()
