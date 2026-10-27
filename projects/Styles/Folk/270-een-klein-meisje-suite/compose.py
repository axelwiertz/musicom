# -*- coding: utf-8 -*-
"""270 - Een Klein Meisje Suite (Dutch Folk nursery rework/extension).

Rework agent (nightly). Chosen source: Folk/239-een-klein-meisje-rework
(Dutch Folk / Child Folk "Kleuterlied"). Audit vs current engine standards:

  - engine          PASS  (compose.py imports UnitMatrixComposer)
  - zero-drift      PASS  (5 voice tracks x 46080 ticks)
  - rhythm-grid     PASS  (0 off-grid pitched onsets)
  - track-setup     PASS  (5 voice tracks)
  - two-phase       PASS  (<id>.mid + <id>-phase1.mid present)
  - provenance+idx  PASS  (per-artifact provenance sidecars + index.html)

  -> core 6 standards PASS => EXTEND (not redesign). BUT source predates the
     2026-10-17 dual-version (perfect/humanized) + humanization mandate:
     it ships a single grid-locked phase-2 MIDI, no -perfect/-humanized pair.
     This rebuild EXTENDS the identity to 8 sections / 32 bars (source = 6
     sections / 24 bars) and applies the current dual-version + humanization
     contract.

Identity preserved: G Major, 105 BPM, 4/4, I-arpeggio nursery motif
(1-3-5-5-3-1 + neighbor 2-3), Markov interval walk over scale degrees,
5-voice band (Lead=Choir Aahs 53, Counter=Violin 41, Harmony=Steel Guitar 25,
Bass=33, Drums ch9).

Two-phase architecture:
  Phase 1: raw Markov-interval walk -> float pitch + jittered eighth rhythm,
           single voice, pre-rules (own composer + own validate gate).
  Phase 2: rules post-process -> per-bar chord-tone quantize (floor s//BAR),
           120-tick grid snap, dedup, voice-leading, per-section harmonic
           regions (midpoint root), 5-voice arrangement.

Variation techniques (>=3 required; 7 applied across 8 sections):
  register_shift_down, identity, retrograde, transpose_P5, augmentation
  (+counterline), inversion, diminution, inversion+diminution (outro cadence).
"""
import json
import os
import hashlib
import random

from structures import MusicUnit, MusicEvent, MidiInstrument, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
STYLE_DIR = "/opt/data/projects/Styles/Folk"
PROJECT = "270-een-klein-meisje-suite"
BASE = os.path.join(STYLE_DIR, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

STYLE = "folk"
BPM = 105
TPB = 480
BEATS_PER_BAR = 4
BAR = TPB * BEATS_PER_BAR                 # 1920
GRID = 120                                # 16th note grid (8th = 240)
TOTAL_BARS = 32
TOTAL_TICKS = TOTAL_BARS * BAR

KEY_NAME = "G Major"
KEY_PCS = {7, 9, 11, 0, 2, 4, 6}          # G A B C D E F#
INTERVALS = [0, 2, 4, 5, 7, 9, 11]        # scale offsets from G
TONIC = 67                                 # G4 (mirror axis for inversion)

# 1-based degree -> triad quality intervals (G major diatonic)
QUALITY = {1: (0, 4, 7), 2: (0, 3, 7), 3: (0, 3, 7), 4: (0, 4, 7),
           5: (0, 4, 7), 6: (0, 3, 7), 7: (0, 3, 6)}
DEGREE_NAMES = {1: "G", 2: "Am", 3: "Bm", 4: "C", 5: "D", 6: "Em", 7: "F#dim"}

# deterministic seeds
hz_seed = int(hashlib.md5(PROJECT.encode()).hexdigest()[:8], 16) % 100000
raw_seed = int(hashlib.md5(b"raw-270").hexdigest()[:8], 16) % 100000
RNG = random.Random(raw_seed)

# ---------------------------------------------------------------------------
# Form: 8 sections x 4 bars = 32 bars, per-section harmonic region
# ---------------------------------------------------------------------------
# (name, bars, progression [1-based degrees], variation_technique)
SECTIONS = [
    ("Intro",  4, [1, 4, 5, 1], "register_shift_down"),
    ("A",      4, [1, 6, 2, 5], "identity"),
    ("Ap",     4, [6, 4, 3, 5], "retrograde"),
    ("B",      4, [4, 5, 6, 1], "transpose_p5"),
    ("C",      4, [5, 2, 5, 6], "augment"),
    ("D",      4, [6, 4, 5, 1], "invert"),
    ("E",      4, [1, 5, 6, 4], "diminish"),
    ("Outro",  4, [4, 5, 1, 1], "invert_diminish"),
]
SECTION_START = {}
_acc = 0
for name, bars, prog, tech in SECTIONS:
    SECTION_START[name] = _acc
    _acc += bars
TOTAL_BARS = _acc

# flat per-bar degree list (for verification + midpoint)
BAR_DEGREES = []
for name, bars, prog, tech in SECTIONS:
    BAR_DEGREES.extend(prog)


def section_midpoint_root():
    """Per-section midpoint degree (NOT bar-0, avoids all-i bug)."""
    out = []
    for name, bars, prog, tech in SECTIONS:
        mid = prog[len(prog) // 2]
        out.append((name, DEGREE_NAMES[mid], mid))
    return out


def diatonic(deg_index, base=67):
    """Canonical diatonic note (Scale7ChordDegree) — no %7 wrapper."""
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_tones(d, lo=36, hi=96):
    """Absolute chord-tone set for 1-based degree d in [lo, hi]."""
    root_pc = (7 + INTERVALS[d - 1]) % 12        # absolute pitch class
    q = QUALITY[d]
    out = set()
    for octv in range(-2, 9):
        for iv in q:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def snap(t):
    return int(round(t / float(GRID)) * GRID)


# ---------------------------------------------------------------------------
# Phase 1: Markov interval walk over scale degrees (raw, unquantized)
# ---------------------------------------------------------------------------
# Transition table estimated from the source melody (degrees 1..5):
#   1,3,5,5,3,1,2,3 | 1,3,5,5,3,1,2,3 | 4,2,1,5,3,1 | 4,2,1,5,3,1
TRANS = {
    1: [3, 3, 2, 2, 5, 5, 4],
    2: [3, 3, 1, 1],
    3: [5, 5, 1, 1, 1, 1, 1, 4],
    4: [2, 2],
    5: [5, 5, 3, 3, 3, 3],
}


def walk_degrees(rng, start_deg, steps, octave=0):
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
    steps = bars * 8
    walk = walk_degrees(rng, anchor_deg, steps, octave=octave)
    events = []
    beat = 0.0
    for (d, octv) in walk:
        if rng.random() < 0.08:                     # occasional rest
            beat += 0.5 * rng.uniform(0.8, 1.5)
            continue
        pitch = float(diatonic(d - 1) + 12 * octv) + rng.uniform(-0.4, 0.4)
        dur = 0.5 * rng.uniform(0.8, 1.3)
        events.append({"pitch": pitch, "start": beat, "dur": dur})
        beat += 0.5 * rng.uniform(0.8, 1.6)
        if beat >= bars * 4.0 - 0.25:
            break
    return events


# ---------------------------------------------------------------------------
# Variation transforms
# ---------------------------------------------------------------------------
def transform(raw, kind):
    if kind == "identity":
        return [dict(e) for e in raw]
    if kind == "register_shift_down":
        ev = [{"pitch": e["pitch"] - 12, "start": e["start"], "dur": e["dur"]}
              for e in raw]
        return ev[::2]                              # thin: keep every 2nd onset
    if kind == "transpose_p5":
        return [{"pitch": e["pitch"] + 7, "start": e["start"], "dur": e["dur"]}
                for e in raw]
    if kind == "retrograde":
        ps = [e["pitch"] for e in raw][::-1]
        return [{"pitch": ps[i], "start": raw[i]["start"], "dur": raw[i]["dur"]}
                for i in range(len(raw))]
    if kind == "augment":
        return [{"pitch": e["pitch"], "start": e["start"], "dur": e["dur"] * 2.0}
                for e in raw]
    if kind == "invert":
        return [{"pitch": 2 * TONIC - e["pitch"], "start": e["start"],
                 "dur": e["dur"]} for e in raw]
    if kind == "diminish":
        return [{"pitch": e["pitch"], "start": e["start"], "dur": e["dur"] * 0.5}
                for e in raw]
    if kind == "invert_diminish":
        return [{"pitch": 2 * TONIC - e["pitch"], "start": e["start"],
                 "dur": e["dur"] * 0.5} for e in raw]
    return [dict(e) for e in raw]


# ---------------------------------------------------------------------------
# Phase 2: rules post-process
# ---------------------------------------------------------------------------
def process_lead(raw_all):
    """Chord-tone quantize + grid snap + dedup + voice-leading."""
    events = []
    for e in raw_all:
        s = snap(e["start"] * TPB)
        s = max(0, min(TOTAL_TICKS - GRID, s))
        bar = s // BAR
        bar = max(0, min(TOTAL_BARS - 1, bar))
        degree = BAR_DEGREES[bar]
        p = int(round(e["pitch"]))
        p = min(chord_tones(degree, lo=48, hi=84),
                key=lambda t: abs(t - p))
        d = snap(e["dur"] * TPB)
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

    # voice-leading: break parallel perfect 5ths/octaves
    fixed = []
    for e in events:
        if fixed:
            prev = fixed[-1]
            gap = e.start_tick - prev.end_tick
            if abs(e.pitch - prev.pitch) in (5, 7, 12) and gap < TPB:
                bar = int(e.start_tick // BAR)
                bar = max(0, min(TOTAL_BARS - 1, bar))
                tones = chord_tones(BAR_DEGREES[bar], lo=48, hi=84)
                cands = [t for t in tones
                         if t != e.pitch and abs(t - prev.pitch) not in (5, 7, 12)]
                if cands:
                    e.pitch = min(cands, key=lambda t: abs(t - e.pitch))
        fixed.append(e)
    return fixed


def build_bass_events():
    """Folk oompah: root-fifth-octave-fifth per bar (chord tones only)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=43)          # G2 region
        fifth = root + 7
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root, volume=88,
                                 start_tick=t0, end_tick=t0 + TPB))
        events.append(MusicEvent(pitch=fifth, volume=76,
                                 start_tick=t0 + TPB, end_tick=t0 + 2 * TPB))
        events.append(MusicEvent(pitch=root + 12, volume=84,
                                 start_tick=t0 + 2 * TPB, end_tick=t0 + 3 * TPB))
        events.append(MusicEvent(pitch=fifth, volume=76,
                                 start_tick=t0 + 3 * TPB, end_tick=t0 + BAR))
    return events


def build_harmony_events():
    """Steel-guitar broken-chord strum on 8th grid (chord tones only)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = BAR_DEGREES[bar]
        root = diatonic(d - 1, base=55)          # G3 close voicing
        q = QUALITY[d]
        tones = [root + iv for iv in q]
        root_n = min(tones)
        third = sorted(tones)[1]
        fifth = max(tones)
        t0 = bar * BAR
        for slot in range(8):
            t = t0 + slot * (TPB // 2)
            if slot % 2 == 0:
                note = {0: root_n, 2: fifth, 4: root_n, 6: third}[slot]
                events.append(MusicEvent(pitch=note, volume=62,
                                         start_tick=t, end_tick=t + TPB // 2))
            else:
                for n in tones:
                    events.append(MusicEvent(pitch=n, volume=56,
                                             start_tick=t, end_tick=t + TPB // 4))
    return events


def build_counter_events():
    """Violin chord-tone arpeggio counterline C/D/E/Outro (density rise)."""
    events = []
    for bar in range(16, TOTAL_BARS):            # sections C..Outro
        d = BAR_DEGREES[bar]
        tones = chord_tones(d, lo=60, hi=88)
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
    """Gentle nursery groove: kick 1&3, snare 2&4, 8th hi-hat (ch9)."""
    events = []
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=88,
                                 start_tick=t0, end_tick=t0 + GRID))
        events.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=70,
                                 start_tick=t0 + TPB, end_tick=t0 + TPB + GRID))
        events.append(MusicEvent(pitch=MidiPercussion.BASS_DRUM, volume=88,
                                 start_tick=t0 + 2 * TPB, end_tick=t0 + 2 * TPB + GRID))
        events.append(MusicEvent(pitch=MidiPercussion.ACOUSTIC_SNARE, volume=70,
                                 start_tick=t0 + 3 * TPB, end_tick=t0 + 3 * TPB + GRID))
        for e8 in range(8):
            t = t0 + e8 * (TPB // 2)
            events.append(MusicEvent(pitch=MidiPercussion.CLOSED_HI_HAT, volume=42,
                                     start_tick=t, end_tick=t + GRID))
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
    # ALWAYS append the silent terminal landmark (pitch 0, passed through the
    # humanizer untouched) so a negative humanization offset on the last note
    # can never shorten the section boundary (zero-drift anchor).
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=max(0, s_len - 10), end_tick=s_len))
    return out


def build_phase1(raw_all):
    """Phase 1: single voice (Lead), raw unquantized units, own composer."""
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=MidiInstrument.FLUTE, channel=0)
    for name, bars, prog, tech in SECTIONS:
        comp.add_section(name, bars=bars)

    for name, bars, prog, tech in SECTIONS:
        s_start = SECTION_START[name] * BAR
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
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS_PER_BAR)
    comp.create_matrix(num_voices=5, num_sections=len(SECTIONS))
    comp.add_voice("Lead", program=53, channel=0)                    # Choir Aahs
    comp.add_voice("Counter", program=MidiInstrument.VIOLIN, channel=1)
    comp.add_voice("Harmony", program=MidiInstrument.ACOUSTIC_GUITAR, channel=2)
    comp.add_voice("Bass", program=MidiInstrument.BASS, channel=3)
    comp.add_voice("Drums", program=0, channel=9)

    for name, bars, prog, tech in SECTIONS:
        comp.add_section(name, bars=bars)

    voice_event_map = {
        "Lead": lead_events,
        "Counter": counter_events,
        "Harmony": harmony_events,
        "Bass": bass_events,
        "Drums": drums_events,
    }

    for name, bars, prog, tech in SECTIONS:
        s_start = SECTION_START[name] * BAR
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
# Main
# ---------------------------------------------------------------------------
def main():
    # ---- Phase 1 raw draft (single voice) ---------------------------------
    A_raw = raw_section(RNG, anchor_deg=1, bars=4, octave=0)
    section_raw = {}
    for name, bars, prog, tech in SECTIONS:
        section_raw[name] = transform(A_raw, tech)

    raw_all = []
    for name, bars, prog, tech in SECTIONS:
        sec_start = SECTION_START[name]
        for e in section_raw[name]:
            raw_all.append({
                "pitch": e["pitch"],
                "start": e["start"] + sec_start * 4.0,
                "dur": e["dur"],
            })

    phase1 = build_phase1(raw_all)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom.method.markov_interval_walk_phase1 (extension of 239)",
        sources=["source:239-een-klein-meisje-rework (Dutch Folk nursery)"],
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "8 sections (extended from 6)"},
        notes="Raw Markov interval walk over G-major scale degrees, "
              "unquantized, single voice, pre-rules. Extension of 239.")
    write_grid_visualization(
        phase1.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
        voice_names=["Lead"], bpm=BPM)

    # ---- Phase 2 rules post-process (5 voices) ----------------------------
    lead_ev = process_lead(raw_all)
    counter_ev = build_counter_events()
    harmony_ev = build_harmony_events()
    bass_ev = build_bass_events()
    drums_ev = build_drums_events()

    phase2 = build_phase2(lead_ev, counter_ev, harmony_ev, bass_ev, drums_ev)

    # ---- dual-version export (perfect + humanized) ------------------------
    hz_instruments = {
        "Lead":    (None, 9.0, None, 0.04),   # voice-like: style governs timing
        "Counter": (None, 6.0, None, 0.02),   # violin melodic
        "Harmony": (None, 6.0, None, 0.02),   # guitar strum
        "Bass":    (5.0, 4.0, 8.0, 0.01),     # lays back 8 ms
        "Drums":   (2.0, 4.0, 0.0, 0.008),    # anchors grid
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ----------------------------------------------
    provenance_params = {
        "bpm": BPM, "key": "G", "mode": "major", "style": STYLE,
        "form": "-".join(s[0] for s in SECTIONS),
        "bars": TOTAL_BARS, "sections": [s[0] for s in SECTIONS],
        "voices": [["Lead", "Choir Aahs", 53], ["Counter", "Violin", 41],
                   ["Harmony", "Steel Guitar", 25], ["Bass", "Electric Bass", 33],
                   ["Drums", "ch9", 0]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom two-phase (phase=2 rules: chord-tone quantize + grid snap + dedup + voice-leading) (extension of 239)",
        sources=["source:239-een-klein-meisje-rework", phase1_mid],
        parameters=dict(provenance_params, phase=2, version="perfect", off_grid=0),
        notes="Grid-locked perfect layer (8 sections / 32 bars).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom two-phase (phase=2 + humanization) (extension of 239)",
        sources=[perfect_path],
        parameters=dict(provenance_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style folk + per-instrument DNA).")

    # ---- grid visualization -----------------------------------------------
    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=["Lead", "Counter", "Harmony", "Bass", "Drums"], bpm=BPM)

    # ---- size asserts -----------------------------------------------------
    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- summary ----------------------------------------------------------
    mid_roots = section_midpoint_root()
    summary = {
        "chosen_source": "Folk/239-een-klein-meisje-rework",
        "chosen_genre": "Folk",
        "audit_result": "core 6 standards PASS (engine, zero-drift, grid, tracks, "
                        "two-phase, provenance+index); pre-2026-10-17 dual-version gap",
        "redesign_required": False,
        "decision": "EXTEND (identity-preserving) + dual-version/humanization upgrade",
        "new_project": BASE,
        "form_bars": TOTAL_BARS,
        "form_sections": len(SECTIONS),
        "variation_techniques": ["register_shift_down", "retrograde", "transpose_p5",
                                 "augment+counterline", "inversion", "diminution",
                                 "inversion+diminution"],
        "section_midpoint_roots": [(n, dn) for (n, dn, d) in mid_roots],
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
        "phase1_path": phase1_mid,
        "perfect_path": perfect_path,
        "humanized_path": humanized_path,
    }
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    # rework audit (source project) + copy into new project
    audit = {
        "chosen": "Folk/239-een-klein-meisje-rework",
        "genre": "Folk",
        "standard_failures": [],
        "redesign_required": False,
        "source_identity": {
            "key": "G Major", "bpm": 105, "meter": "4/4",
            "motif": "I-arpeggio 1-3-5-5-3-1 + neighbor 2-3; IV/dominant cadence",
            "voices": ["Lead/Choir Aahs 53", "Counter/Violin 41",
                       "Harmony/Steel Guitar 25", "Bass/33", "Drums ch9"],
            "form": "6 sections / 24 bars (Intro-A-B-A2-C-Outro)",
            "note": "pre-2026-10-17: single phase-2 MIDI, no perfect/humanized pair",
        },
    }
    with open(os.path.join(ANALYSIS_DIR, "rework_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)
    src_audit = "/opt/data/projects/Styles/Folk/239-een-klein-meisje-rework/Analysis/rework_audit.json"
    with open(src_audit, "w") as f:
        json.dump(audit, f, indent=2)

    print("SECTION_MIDPOINT_ROOTS:", mid_roots)
    print("LEAD_EVENTS:", len(lead_ev), "COUNTER:", len(counter_ev),
          "HARMONY:", len(harmony_ev), "BASS:", len(bass_ev),
          "DRUMS:", len(drums_ev))


if __name__ == "__main__":
    main()
