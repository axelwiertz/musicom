# -*- coding: utf-8 -*-
"""317-factor-oracle-lounge -- Lounge via Factor Oracle Guided Improvisation.

Nightly composition job (2026-11-21). Selection: style=Lounge, method=067
Factor Oracle Guided Improvisation (FOGI, CONCRETE layer, Stochastic paradigm),
form=intro-a-a-b-a (pick_form("lounge") -> no style hint -> full non-loop
palette -> intro-a-a-b-a) = [Intro 4, A 8, A 8, B 8, A 8] = 36 bars.

MUSICAL DNA
  - Key F major (ionian) = pc {F,G,A,Bb,C,D,E} = {5,7,9,10,0,2,4}; tonic F.
  - 90 BPM, 4/4, 480 TPB, BAR=1920, 8th=240, 16th=120.
  - Method 067 FOGI: a Factor Oracle is built over a seed corpus (an
    automaton with forward transitions + suffix links; Allauzen-Crochemore-
    Raffinot 1999). Walking it forward emits an infinite corpus-styled
    improvisation: forward transitions continue the current motif, suffix-link
    recombination jumps to a repeated context (a "Trojan island" -- a motif
    that recurs), and restart returns to the head of the corpus (phrase
    breath). No training -- the automaton IS the model. The 7-symbol corpus
    (scale degrees 0..6) is the melodic pitch DNA; the walk emits the lead's
    degree stream. Section chaining (Intro/A/A/B/A) supplies the macro-form;
    per-bar 7th-chord regions supply the harmonic grammar for the chord-tone
    snap.
  - 5-voice Lounge texture: Flute lead (FO degree stream), Rhodes e-piano
    sustained 7th-chord pad, Jazz Guitar bossa shell comp, Acoustic Bass
    root/fifth/approach line, Drum Kit light bossa-lounge groove (rim 2&4).

TWO-PHASE
  Phase 1 (raw): single Flute voice, the raw FO degree walk -- jittered pitch
    (float + chromatic jitter), off-grid onsets, single voice, no harmony;
    own composer + validate().
  Phase 2 (rules): STRICT chord discipline (every note snaps to its own bar's
    7th-chord tone -> in-scale AND in-chord), 16th grid snap, 5-voice texture.
  Dual-version: export_dual -> -perfect.mid (grid-locked) + -humanized.mid.
"""
import json
import os
import sys
import hashlib

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.pitch_audit import audit_voice
from visualization.grid import write_grid_visualization
from rules.progression import Scale7ChordDegree

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import (  # noqa: E402
    FLUTE, RHODES, JAZZ_GUITAR, ACOUSTIC_BASS, DRUM_KIT)

# ---------------------------------------------------------------------------
# Project layout / identity
# ---------------------------------------------------------------------------
GENRE = "Lounge"
STYLE = "lounge"
PROJECT = "317-factor-oracle-lounge"
BASE = os.path.join("/opt/data/projects/Styles", GENRE, PROJECT)
MIDI_DIR = os.path.join(BASE, "MIDI")
AUDIO_DIR = os.path.join(BASE, "Audio")
ANALYSIS_DIR = os.path.join(BASE, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 90
TPB = 480
BPB = 4
BAR = TPB * BPB                     # 1920
GRID = 120                          # 16th
EIGHTH = 240
QUARTER = 480

# Form intro-a-a-b-a -> 5 logical sections, 36 bars total.
# NOTE: section names MUST be unique -- fill_voice_section resolves by name
# (first match), so duplicate "A" names would silently collapse onto one column.
LOGICAL_SECTIONS = [("Intro", 4), ("A1", 8), ("A2", 8), ("B", 8), ("A3", 8)]
TOTAL_BARS = sum(b for _, b in LOGICAL_SECTIONS)   # 36
TOTAL_TICKS = TOTAL_BARS * BAR                     # 69120

KEY_NAME = "F major (ionian)"
TONIC_PC = 5                        # F
INTERVALS = [0, 2, 4, 5, 7, 9, 11]  # ionian / major step pattern
KEY_PCS = sorted({(TONIC_PC + iv) % 12 for iv in INTERVALS})  # {0,2,4,5,7,9,11}

# 1-based degree -> 7th-chord quality intervals (F major diatonic)
QUALITY = {1: (0, 4, 7, 11), 2: (0, 3, 7, 10), 3: (0, 3, 7, 10),
           4: (0, 4, 7, 11), 5: (0, 4, 7, 10), 6: (0, 3, 7, 10),
           7: (0, 3, 6, 10)}
DEGREE_NAMES = {1: "Fmaj7", 2: "Gm7", 3: "Am7", 4: "Bbmaj7", 5: "C7",
                6: "Dm7", 7: "Em7b5"}

# per-bar progression (1-based degrees), lounge ii-V-I-vi turnaround + B bridge
A_LOOP = [1, 6, 2, 5]               # I vi ii V (turnaround)
B_LOOP = [4, 5, 3, 6, 2, 5, 1, 5]   # IV V iii vi ii V I V (bridge)
DEGREES = []
for name, bars in LOGICAL_SECTIONS:
    if name == "B":
        DEGREES += B_LOOP[:bars]
    else:
        DEGREES += (A_LOOP * (bars // len(A_LOOP) + 1))[:bars]
assert len(DEGREES) == TOTAL_BARS, f"{len(DEGREES)} != {TOTAL_BARS}"

# 1-bar sections for the humanized composer: the humanizer's boundary clamp
# == bar boundary, so jitter never re-attributes a note to the wrong bar's
# chord (per-bar chord violations stay 0).
BAR_SECTIONS = [(f"Bar{b + 1}", 1) for b in range(TOTAL_BARS)]

# deterministic seeds
hz_seed = int(hashlib.md5(
    (STYLE + KEY_NAME + str(BPM) + str(TOTAL_BARS) + PROJECT).encode()
).hexdigest()[:8], 16) % 100000
raw_seed = 20261121
RNG = __import__("random").Random(raw_seed)
NPRNG = np.random.default_rng(raw_seed)

# ---------------------------------------------------------------------------
# Voices + registers
# ---------------------------------------------------------------------------
VOICES = ["Lead", "Rhodes", "Guitar", "Bass", "Drums"]
VOICE_PROGRAMS = [FLUTE.midi_program, RHODES.midi_program,
                  JAZZ_GUITAR.midi_program, ACOUSTIC_BASS.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]

LEAD_BASE = 77                      # F5
LEAD_LO, LEAD_HI = 65, 89           # flute range 60-96, sweet upper-mid
RHODES_LO, RHODES_HI = 55, 79       # rhodes sweet (60-79)
GUITAR_LO, GUITAR_HI = 48, 72       # jazz guitar sweet (48-72)
BASS_BASE = 41                      # F2
BASS_LO, BASS_HI = 36, 57           # acoustic bass sweet (40-57)


# ---------------------------------------------------------------------------
# Diatonic helpers (canonical Scale7ChordDegree -- no %7 wrapper)
# ---------------------------------------------------------------------------
def diatonic(deg_index, base=LEAD_BASE):
    return Scale7ChordDegree.get_diatonic_note(base, INTERVALS, deg_index)


def chord_pcs(d):
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    return sorted({(root_pc + iv) % 12 for iv in QUALITY[d]})


def chord_tones(d, lo=24, hi=96):
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    out = set()
    for octv in range(-3, 11):
        for iv in QUALITY[d]:
            n = root_pc + 12 * octv + iv
            if lo <= n <= hi:
                out.add(n)
    return sorted(out)


def to_register(pitch, lo, hi):
    p = int(pitch)
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


def voicing(d, lo, hi, n=4):
    """Root-position chord voicing (root, 3rd, 5th, [7th]) registered to range."""
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    ivs = QUALITY[d][:n]
    octv = 4
    notes = [root_pc + 12 * octv + iv for iv in ivs]
    while max(notes) > hi:
        notes = [x - 12 for x in notes]
    while min(notes) < lo:
        notes = [x + 12 for x in notes]
    return notes


def shell_voicing(d, lo, hi):
    """Jazz shell voicing: root, 3rd, 7th (drop the 5th)."""
    root_pc = (TONIC_PC + INTERVALS[d - 1]) % 12
    ivs = [QUALITY[d][0], QUALITY[d][1], QUALITY[d][3]]
    octv = 4
    notes = [root_pc + 12 * octv + iv for iv in ivs]
    while max(notes) > hi:
        notes = [x - 12 for x in notes]
    while min(notes) < lo:
        notes = [x + 12 for x in notes]
    return notes


# ---------------------------------------------------------------------------
# Factor Oracle (Allauzen-Crochemore-Raffinot 1999) + guided walk
# ---------------------------------------------------------------------------
def build_fo(corpus):
    """Return (trans, slink): forward-transition dicts and suffix links.

    trans[i] maps symbol -> next state (the corpus continuation); slink[i] is
    the longest proper suffix of the prefix ending at state i that is also a
    prefix (the "repeated context" pointer).
    """
    n = len(corpus)
    trans = [dict() for _ in range(n + 1)]
    slink = [-1] * (n + 1)
    slink[0] = -1
    for i in range(n):
        trans[i][corpus[i]] = i + 1
        k = slink[i]
        while k >= 0 and corpus[i] not in trans[k]:
            trans[k][corpus[i]] = i + 1
            k = slink[k]
        slink[i + 1] = 0 if k < 0 else trans[k][corpus[i]]
    return trans, slink


def fo_walk(trans, slink, n_steps, rng, continue_prob=0.8, restart_prob=0.03):
    """Emit n_steps corpus symbols by stochastic FO traversal."""
    state = 0
    seq = []
    for _ in range(n_steps):
        if rng.random() < restart_prob:
            state = 0
        fwd = list(trans[state].items())
        if not fwd:
            state = 0
            fwd = list(trans[state].items())
            if not fwd:
                break
        if rng.random() < continue_prob:
            sym, nxt = rng.choice(fwd)          # continue along corpus
        else:
            k = slink[state]                    # recombination via suffix link
            while k >= 0 and not trans[k]:
                k = slink[k]
            if k < 0:
                k = 0
            cand = list(trans[k].items())
            if not cand:
                state = 0
                continue
            sym, nxt = rng.choice(cand)         # jump to repeated context
        seq.append(sym)
        state = nxt
    return seq


# Lounge corpus (7 scale degrees; 0=F .. 6=E). Motifs with internal repetition
# so suffix links form recurrent "Trojan island" contexts.
CORPUS = [
    0, 2, 4, 2,          # F A C A  (tonic arpeggio)
    3, 2, 1, 2,          # Bb A G A
    0, 2, 3, 4,          # F A Bb C  (rising)
    5, 4, 3, 2,          # D C Bb A  (falling)
    0, 1, 2, 3,          # F G A Bb
    4, 2, 0, 4,          # C A F C
    3, 1, 2, 5,          # Bb G A D
    4, 2, 0, 2,          # C A F A
]
TRANS, SLINK = build_fo(CORPUS)

# rhythm gate: bossa-lounge syncopation, period 8 eighths (5 hits/bar)
GATE = [1, 0, 1, 1, 0, 1, 0, 1]    # hits at 8ths 0,2,3,5,7
N_SLOTS = TOTAL_BARS * 8            # 288 eighth slots
HIT_SLOTS = [s for s in range(N_SLOTS) if GATE[s % 8] == 1]
N_HITS = len(HIT_SLOTS)             # 180

# one deterministic FO walk -> the lead's degree stream (shared by both phases)
FO_SYMBOLS = fo_walk(TRANS, SLINK, N_HITS, RNG)
assert len(FO_SYMBOLS) == N_HITS


# ---------------------------------------------------------------------------
# Phase 1: raw FO walk (single voice, jittered, off-grid)
# ---------------------------------------------------------------------------
def build_raw_lead():
    raw = []
    for idx, slot in enumerate(HIT_SLOTS):
        degree = FO_SYMBOLS[idx]
        onset = slot * EIGHTH + RNG.randint(-60, 60)
        p = float(diatonic(degree, LEAD_BASE)) + float(RNG.choice([-1, 0, 0, 1]))
        vel = int(RNG.randint(70, 100))
        raw.append({"pitch": p, "start": max(0, onset), "dur": EIGHTH,
                    "vel": vel, "slot": slot, "degree": degree})
    raw.sort(key=lambda e: (e["start"], e["pitch"]))
    return raw


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
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=max(0, s_len - 10), end_tick=s_len))
    return out


def build_phase1(raw_events):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=1, num_sections=len(LOGICAL_SECTIONS))
    comp.add_voice("RawFlute", program=FLUTE.midi_program, channel=0)
    for name, bars in LOGICAL_SECTIONS:
        comp.add_section(name, bars=bars)

    acc = 0
    for name, bars in LOGICAL_SECTIONS:
        s_start = acc * BAR
        s_ticks = bars * BAR
        seg = []
        for e in raw_events:
            p = int(round(e["pitch"]))
            p = max(36, min(96, p))
            seg.append(MusicEvent(pitch=p, volume=e["vel"],
                                  start_tick=int(round(e["start"])),
                                  end_tick=int(round(e["start"] + e["dur"]))))
        seg.sort(key=lambda e: e.start_tick)
        comp.fill_voice_section("RawFlute", name,
                                MusicUnit(events=rel_events(seg, s_start, s_ticks)))
        acc += bars
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# Phase 2 builders (STRICT chord discipline -- every note = its bar's chord
# tone -> in-scale AND in-chord)
# ---------------------------------------------------------------------------
def snap_grid(t, grid=GRID):
    return int(round(t / float(grid)) * grid)


def build_lead():
    """Flute: FO degree stream, each onset snapped to nearest chord tone of its
    own bar (STRICT), 16th-grid locked."""
    events = []
    for idx, slot in enumerate(HIT_SLOTS):
        degree = FO_SYMBOLS[idx]
        bar = slot // 8
        d = DEGREES[bar]
        ct = chord_tones(d, LEAD_LO, LEAD_HI)
        raw_note = diatonic(degree, LEAD_BASE)
        raw_note = to_register(raw_note, LEAD_LO, LEAD_HI)
        p = min(ct, key=lambda t: abs(t - raw_note))
        onset = snap_grid(slot * EIGHTH)
        onset = max(0, min(TOTAL_TICKS - GRID, onset))
        vel = 80 + (idx % 3) * 7
        events.append(MusicEvent(pitch=p, volume=vel, start_tick=onset,
                                 end_tick=min(TOTAL_TICKS, onset + 200)))
    return events


def build_rhodes():
    """Rhodes e-piano: sustained whole-bar 7th-chord pad (root position)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = DEGREES[bar]
        v = voicing(d, RHODES_LO, RHODES_HI, 4)
        t0 = bar * BAR
        for n in v:
            events.append(MusicEvent(pitch=n, volume=58, start_tick=t0,
                                     end_tick=t0 + 1700))
    events.sort(key=lambda e: (e.start_tick, e.pitch))
    return events


def build_guitar():
    """Jazz guitar bossa shell comp: root+3rd+7th, syncopated 16th pattern
    (1, and-of-2, 3, and-of-4)."""
    events = []
    HITS = (0, 6, 8, 14)             # 16th slots
    for bar in range(TOTAL_BARS):
        d = DEGREES[bar]
        v = shell_voicing(d, GUITAR_LO, GUITAR_HI)
        t0 = bar * BAR
        for h in HITS:
            t = t0 + h * GRID
            vel = 70 if h in (0, 8) else 56
            for n in v:
                events.append(MusicEvent(pitch=n, volume=vel, start_tick=t,
                                         end_tick=t + 90))
    events.sort(key=lambda e: (e.start_tick, e.pitch))
    return events


def build_bass():
    """Acoustic bass bossa line: root (1) -> fifth (3) -> approach-to-next-root
    (and-of-4 pickup, snapped to current bar's chord tone -> STRICT)."""
    events = []
    for bar in range(TOTAL_BARS):
        d = DEGREES[bar]
        ct = chord_tones(d, BASS_LO, BASS_HI)
        root = diatonic(d - 1, BASS_BASE)
        root = to_register(root, BASS_LO, BASS_HI)
        fifth = to_register(root + 7, BASS_LO, BASS_HI)
        next_d = DEGREES[(bar + 1) % TOTAL_BARS]
        next_root = diatonic(next_d - 1, BASS_BASE)
        approach_target = to_register(next_root - 2, BASS_LO, BASS_HI)
        approach = min(ct, key=lambda t: abs(t - approach_target))
        t0 = bar * BAR
        events.append(MusicEvent(pitch=root, volume=82, start_tick=t0,
                                 end_tick=t0 + 420))
        events.append(MusicEvent(pitch=fifth, volume=70, start_tick=t0 + 960,
                                 end_tick=t0 + 1320))
        events.append(MusicEvent(pitch=approach, volume=58,
                                 start_tick=t0 + 1680, end_tick=t0 + 1780))
    events.sort(key=lambda e: e.start_tick)
    return events


def build_drums():
    """Light bossa-lounge groove: kick 1&3, rim/cross-stick 2&4, off-beat hats."""
    events = []
    for bar in range(TOTAL_BARS):
        t0 = bar * BAR
        events.append(MusicEvent(pitch=36, volume=78, start_tick=t0,
                                 end_tick=t0 + 60))
        events.append(MusicEvent(pitch=37, volume=62, start_tick=t0 + 480,
                                 end_tick=t0 + 540))
        events.append(MusicEvent(pitch=36, volume=70, start_tick=t0 + 960,
                                 end_tick=t0 + 1020))
        events.append(MusicEvent(pitch=37, volume=62, start_tick=t0 + 1440,
                                 end_tick=t0 + 1500))
        for off in (240, 720, 1200, 1680):
            events.append(MusicEvent(pitch=42, volume=50, start_tick=t0 + off,
                                     end_tick=t0 + off + 40))
    events.sort(key=lambda e: (e.start_tick, e.pitch))
    return events


def build_phase2(vmap, sections_spec):
    comp = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    comp.create_matrix(num_voices=len(VOICES), num_sections=len(sections_spec))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        comp.add_voice(name, program=prog, channel=ch)
    for name, bars in sections_spec:
        comp.add_section(name, bars=bars)

    acc = 0
    for name, bars in sections_spec:
        s_start = acc * BAR
        s_ticks = bars * BAR
        for vname, all_ev in vmap.items():
            seg = [e for e in all_ev if s_start <= e.start_tick < s_start + s_ticks]
            comp.fill_voice_section(vname, name,
                                    MusicUnit(events=rel_events(seg, s_start, s_ticks)))
        acc += bars
    ok, msg = comp.validate()
    if not ok:
        raise RuntimeError(f"phase2 validate failed: {msg}")
    return comp


# ---------------------------------------------------------------------------
# Audits
# ---------------------------------------------------------------------------
def count_offgrid(events, grid=GRID):
    off = sum(1 for e in events if e.pitch > 0 and e.start_tick % grid != 0)
    return off, sum(1 for e in events if e.pitch > 0)


def count_violations(events):
    scale = chord = 0
    for e in events:
        if e.pitch <= 0:
            continue
        pc = e.pitch % 12
        bar = min(TOTAL_BARS - 1, e.start_tick // BAR)
        if pc not in KEY_PCS:
            scale += 1
        if pc not in chord_pcs(DEGREES[bar]):
            chord += 1
    return scale, chord


CHORD_PCS_BY_BAR = {b: chord_pcs(DEGREES[b]) for b in range(TOTAL_BARS)}


def tiered_audit(events):
    return audit_voice(events, KEY_PCS, chord_pcs_by_bar=CHORD_PCS_BY_BAR,
                       strong_grid=(0, 960), bar_ticks=BAR, grid=EIGHTH)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # ---- Phase 1 raw draft -------------------------------------------------
    raw_events = build_raw_lead()
    print("Phase-1 raw lead events:", len(raw_events))
    phase1 = build_phase1(raw_events)
    phase1_mid = os.path.join(MIDI_DIR, PROJECT + "-phase1.mid")
    phase1.to_midi(phase1_mid)
    write_provenance(
        phase1_mid, AI_ASSISTED,
        "musicom composition 317 (phase=1 raw, method 067 FOGI)",
        parameters={"bpm": BPM, "bars": TOTAL_BARS, "seed": raw_seed,
                    "phase": 1, "quantized": False, "key": KEY_NAME,
                    "form": "intro-a-a-b-a (36 bars)", "style": STYLE,
                    "method": "067 FOGI (Factor Oracle over 32-symbol corpus)",
                    "corpus_len": len(CORPUS), "fo_symbols": len(FO_SYMBOLS)},
        notes="Raw Factor Oracle degree walk (32-symbol lounge corpus), "
              "off-grid, float pitch + jitter, single voice, pre-rules.")
    write_grid_visualization(
        phase1.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization_phase1.txt"),
        voice_names=["RawFlute"], bpm=BPM)

    # ---- Phase 2 rules post-process (5 voices) -----------------------------
    lead_ev = build_lead()
    rhodes_ev = build_rhodes()
    guitar_ev = build_guitar()
    bass_ev = build_bass()
    drums_ev = build_drums()
    vmap = {"Lead": lead_ev, "Rhodes": rhodes_ev, "Guitar": guitar_ev,
            "Bass": bass_ev, "Drums": drums_ev}

    phase2 = build_phase2(vmap, BAR_SECTIONS)

    # ---- STRICT discipline audit on pitched voices -------------------------
    pitched = lead_ev + rhodes_ev + guitar_ev + bass_ev
    off, tot = count_offgrid(pitched)
    scale_v, chord_v = count_violations(pitched)
    print(f"Perfect-layer off-grid (pitched): {off}/{tot}")
    print(f"STRICT scale violations: {scale_v}  chord violations: {chord_v}")
    assert off == 0, f"perfect layer has {off} off-grid onsets"
    assert scale_v == 0, f"scale violations: {scale_v}"
    assert chord_v == 0, f"chord violations: {chord_v}"

    # ---- tiered audit_voice (P1 invariant) per pitched voice ---------------
    tiered = {}
    for vname in ("Lead", "Rhodes", "Guitar", "Bass"):
        r = tiered_audit(vmap[vname])
        tiered[vname] = {
            "audible": r.audible,
            "strong_ok": r.strong_ok,
            "weak_in_scale": r.weak_in_scale,
            "untagged_out_of_scale": r.untagged_out_of_scale,
            "tagged_non_resolving": r.tagged_non_resolving,
            "strong_violations": r.strong_violations,
            "passes": r.passes,
        }
        assert r.passes, f"tiered audit failed for {vname}: {r.summary()}"
        print(f"  {vname}: {r.summary()}")

    write_grid_visualization(
        phase2.matrix,
        os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
        voice_names=VOICES, bpm=BPM)

    # ---- dual-version export (perfect + humanized) -------------------------
    hz_instruments = {
        "Lead": FLUTE.humanize_dna,
        "Rhodes": RHODES.humanize_dna,
        "Guitar": JAZZ_GUITAR.humanize_dna,
        "Bass": ACOUSTIC_BASS.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    perfect_path = os.path.join(MIDI_DIR, PROJECT + "-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, PROJECT + "-humanized.mid")
    hz = export_dual(phase2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM,
                     instruments=hz_instruments)

    # ---- provenance sidecars ------------------------------------------------
    prov_params = {
        "bpm": BPM, "key": "F", "mode": "ionian", "style": STYLE,
        "form": "intro-a-a-b-a (36 bars)", "bars": TOTAL_BARS,
        "method": "067 FOGI", "layer": "concrete", "paradigm": "Stochastic",
        "progression": [DEGREE_NAMES[d] for d in DEGREES],
        "corpus": CORPUS, "fo_symbols": FO_SYMBOLS,
        "gate": GATE,
        "voices": [[v, n, o.midi_program] for v, n, o in [
            ("Lead", "Flute", FLUTE), ("Rhodes", "Rhodes", RHODES),
            ("Guitar", "Jazz Guitar", JAZZ_GUITAR),
            ("Bass", "Acoustic Bass", ACOUSTIC_BASS),
            ("Drums", "Drum Kit", DRUM_KIT)]],
        "humanize_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
    }
    write_provenance(
        perfect_path, AI_ASSISTED,
        "musicom composition 317 (phase=2 strict chord discipline) (method 067 FOGI)",
        sources=[phase1_mid],
        parameters=dict(prov_params, phase=2, version="perfect",
                        off_grid=0, scale_violations=0, chord_violations=0),
        notes="Grid-locked perfect layer (36-bar lounge, 5 voices).")
    write_provenance(
        humanized_path, AI_ASSISTED,
        "musicom composition 317 (phase=2 + humanization) (method 067 FOGI)",
        sources=[perfect_path],
        parameters=dict(prov_params, phase=2, version="humanized",
                        humanize_seed=hz_seed,
                        humanize_stats={k: {kk: (float(vv) if isinstance(vv, float) else vv)
                                            for kk, vv in v.items() if kk != "profile"}
                                        for k, v in hz.items()}),
        notes="Humanized layer (style lounge + per-instrument DNA).")

    for p in (phase1_mid, perfect_path, humanized_path):
        assert os.path.getsize(p) > 40, f"empty/corrupt: {p}"

    # ---- root provenance.json ----------------------------------------------
    root_prov = dict(prov_params)
    root_prov.update({
        "project": PROJECT, "genre": GENRE, "key_name": KEY_NAME,
        "tonic_pc": TONIC_PC, "key_pcs": KEY_PCS,
        "bars": TOTAL_BARS, "ticks": TOTAL_TICKS,
        "form": "intro-a-a-b-a (36 bars)",
        "progression_names": [DEGREE_NAMES[d] for d in DEGREES],
        "corpus_len": len(CORPUS), "fo_symbols_len": len(FO_SYMBOLS),
        "tiered_audit": tiered,
        "hz_seed": hz_seed, "raw_seed": raw_seed,
        "humanize_profiles": {k: v["profile"] for k, v in hz.items()},
        "generator": "musicom composition agent (nightly) 2026-11-21",
        "classification": "ai-assisted",
    })
    with open(os.path.join(BASE, "provenance.json"), "w") as f:
        json.dump(root_prov, f, indent=2, default=str)

    # ---- summary -------------------------------------------------------------
    summary = {
        "style": STYLE, "genre": GENRE, "project": PROJECT,
        "method": "067 FOGI", "layer": "concrete", "form": "intro-a-a-b-a",
        "key": KEY_NAME, "bpm": BPM, "bars": TOTAL_BARS,
        "progression": [DEGREE_NAMES[d] for d in DEGREES],
        "corpus_len": len(CORPUS), "fo_symbols_len": len(FO_SYMBOLS),
        "raw_events": len(raw_events),
        "phase1_path": phase1_mid, "perfect_path": perfect_path,
        "humanized_path": humanized_path,
        "off_grid": off, "scale_violations": scale_v, "chord_violations": chord_v,
        "tiered_audit": tiered,
        "hz_seed": hz_seed,
        "hz": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
               for k, v in hz.items()},
    }
    print("COMPOSE_OK")
    print(json.dumps(summary, indent=2, default=str))
    with open(os.path.join(ANALYSIS_DIR, "compose_summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("LEAD:", len(lead_ev), "RHODES:", len(rhodes_ev),
          "GUITAR:", len(guitar_ev), "BASS:", len(bass_ev),
          "DRUMS:", len(drums_ev))


if __name__ == "__main__":
    main()
