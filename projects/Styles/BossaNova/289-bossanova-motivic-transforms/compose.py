# -*- coding: utf-8 -*-
"""289-bossanova-motivic-transforms -- Nightly composition job.

Two-phase architecture, Method 013 "Inversion / Retrograde Transform".

  Phase 1: single-voice raw draft. A fixed 8-note pitch motif (scale-degree
           contour) is transformed per section (Prime / Retrograde / Inversion /
           Prime-return) and laid on a bossa-nova anticipation rhythm with
           jittered OFF-GRID onsets. No harmony, no chord context.
  Phase 2: musicom rules post-process -> grid-lock to 16th (120 ticks),
           TIERED pitch discipline (strong = scale+chord, weak = scale),
           voice-leading cap, dedup, then a full 5-voice Bossa Nova texture
           (nylon-guitar comp, Rhodes pad, double bass, bossa drums). Exported
           as dual versions (-perfect + -humanized).

Engine only: structures + workflows.unitmatrix_composer + pitch_audit +
humanize. mido used for READ-ONLY verification.
"""
import os
import json
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from sound.synthesis.scale_quantizer import ScaleQuantizer, classify_weight, STRONG_GRID
from workflows.pitch_audit import audit_voice

# instrument registry (NOT pip-installed; sanctioned sys.path for registry only)
sys.path.insert(0, "/opt/data/projects/Instruments")
from instrument_registry import by_name  # noqa: E402

SEED = 20261106
STYLE = "BossaNova"
METHOD_ID = "013"
METHOD_NAME = "Inversion / Retrograde Transform"
LAYER = "concrete"
FORM = "intro-a-a-b-a"

PROJ = "/opt/data/projects/Styles/BossaNova/289-bossanova-motivic-transforms"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 120
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920 ticks
GRID = 120                   # 16th note
EIGHTH = 240
SIXTEENTH = 120

# F major: F G A Bb C D E -> pitch classes {5,7,9,10,0,2,4}
SCALE_PCS = {5, 7, 9, 10, 0, 2, 4}
SCALE_NAME = "major"
SCALE_ROOT = 53              # F3
sq = ScaleQuantizer(root=SCALE_ROOT, scale=SCALE_NAME)
STRONG_GRID_44 = tuple(STRONG_GRID["4/4"])   # (0, 960) = beats 1 & 3

# F major scale degree -> semitone offset from F
DEG_SEMI = [0, 2, 4, 5, 7, 9, 11]

# ---- Method 013 core motif (8 scale-degrees) + geometric transforms ----
MOTIF_P = [0, 1, 3, 2, 4, 2, 1, 0]          # F G Bb A C A G F  (prime)
AXIS = 2.0                                    # inversion axis (deg ~2.0)
MOTIF_R = MOTIF_P[::-1]                       # retrograde
MOTIF_I = [int(round(2 * AXIS - x)) for x in MOTIF_P]   # inversion
MOTIF_RI = MOTIF_I[::-1]                      # retrograde-inversion
TRANSFORMS = {"P": MOTIF_P, "R": MOTIF_R, "I": MOTIF_I, "RI": MOTIF_RI}

# F major 7th chords (jazz bossa vocabulary)
CHORDS = {
    "Fmaj7":  {"pcs": {5, 9, 0, 4},  "tones": [53, 57, 60, 64], "bass": 41},
    "Gm7":    {"pcs": {7, 10, 2, 5}, "tones": [55, 58, 62, 65], "bass": 43},
    "Am7":    {"pcs": {9, 0, 4, 7},  "tones": [57, 60, 64, 67], "bass": 45},
    "Bbmaj7": {"pcs": {10, 2, 5, 9}, "tones": [58, 62, 65, 69], "bass": 46},
    "C7":     {"pcs": {0, 4, 7, 10}, "tones": [60, 64, 67, 70], "bass": 48},
    "Dm7":    {"pcs": {2, 5, 9, 0},  "tones": [62, 65, 69, 72], "bass": 50},
    "Em7b5":  {"pcs": {4, 7, 10, 2}, "tones": [64, 67, 70, 74], "bass": 40},
}
CHORD_KEYS = list(CHORDS.keys())

# form layout: intro-a-a-b-a (5 sections, 36 bars)
NAMES = ["Intro", "A", "A", "B", "A"]
BARS = [4, 8, 8, 8, 8]
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS)            # 36
SECTION_TICKS = [b * BAR for b in BARS]

# per-section 4-bar chord rotation (A/B sections repeat the cycle twice)
SECTION_ROT = {
    0: ["Fmaj7", "Bbmaj7", "Gm7", "C7"],      # Intro  midpoint Bbmaj7
    1: ["Fmaj7", "Dm7", "Gm7", "C7"],         # A      midpoint Dm7
    2: ["Fmaj7", "Dm7", "Gm7", "C7"],         # A      midpoint Dm7
    3: ["Bbmaj7", "Gm7", "Am7", "Dm7"],       # B      midpoint Gm7 (contrast)
    4: ["Fmaj7", "Dm7", "Gm7", "C7"],         # A      midpoint Dm7 (recap)
}

# voices: (voice name, registry instrument, GM program, channel)
VOICES = [
    ("Flute",  "flute",          73, 0),
    ("Guitar", "acoustic_guitar", 24, 1),
    ("Rhodes", "rhodes",          4, 2),
    ("Bass",   "acoustic_bass",  32, 3),
    ("Drums",  "drum_kit",        0, 9),
]
N_V = len(VOICES)
vnames = [v[0] for v in VOICES]

# bossa nova anticipation rhythm (16th offsets within a bar) -- lead melody
BOSSA_OFFSETS = [0, 3, 6, 8, 11, 14]
# bossa guitar comp rhythm (16th offsets): "1, & of 2, 3, & of 4"
COMP_OFFSETS = [0, 6, 8, 14]


def bar_to_section(bar):
    cum = 0
    for s in range(N_SECTIONS):
        if bar < cum + BARS[s]:
            return s, bar - cum
        cum += BARS[s]
    return N_SECTIONS - 1, BARS[-1] - 1


def chord_key_for_bar(bar):
    s, lb = bar_to_section(bar)
    return SECTION_ROT[s][lb % 4]


def chord_tones_for(ck):
    tones = CHORDS[ck]["tones"]
    return sorted({t + 12 * o for t in tones for o in range(-2, 5)})


# ---------------------------------------------------------------------------
# Phase 1: raw motivic draft -- transformed motif x jittered bossa rhythm
# ---------------------------------------------------------------------------
def motif_walk(seed, sec_ticks, octave, transform, offsets, dur_pool):
    """Place the (transformed) motif on a bossa rhythm, off-grid + unquantized.

    Motif degrees cycle across the section; onsets sit on the bossa offsets
    with Gaussian jitter (NOT snapped -> phase-1 raw draft), pitch is the raw
    scale-degree pitch with random octave drift, no chord context.
    """
    r = np.random.default_rng(seed)
    M = TRANSFORMS[transform]
    events = []
    n_bars = sec_ticks // BAR
    k = 0
    for b in range(n_bars):
        t0 = b * BAR
        for off in offsets:
            deg = M[k % len(M)]
            k += 1
            octv = octave + int(r.choice([0, 0, 0, 0, 1, -1]))
            pitch = SCALE_ROOT + DEG_SEMI[deg] + 12 * octv
            onset = t0 + off * 120 + int(r.normal(0.0, 30.0))
            onset = max(t0, min(onset, t0 + BAR - 120))
            dur = int(r.choice(dur_pool))
            dur = min(dur, t0 + BAR - onset)
            velo = int(np.clip(72 + 22 * r.standard_normal(), 58, 105))
            events.append(MusicEvent(pitch=pitch, volume=velo,
                                     start_tick=onset, end_tick=onset + dur))
    return events


# per-section generative params (variation = the geometric transform + register)
LEAD_PARAMS = {
    0: dict(octave=1, transform="P",  offsets=[0, 8, 14], dur_pool=[360, 480]),          # sparse intro (prime)
    1: dict(octave=1, transform="P",  offsets=BOSSA_OFFSETS, dur_pool=[240, 240, 360, 480]),   # A1 prime
    2: dict(octave=1, transform="R",  offsets=BOSSA_OFFSETS, dur_pool=[240, 240, 360, 480]),   # A2 retrograde
    3: dict(octave=2, transform="I",  offsets=BOSSA_OFFSETS, dur_pool=[240, 240, 360, 480]),   # B  inversion (register lift)
    4: dict(octave=1, transform="P",  offsets=BOSSA_OFFSETS, dur_pool=[240, 240, 360, 480]),   # A3 prime (recap)
}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=73, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS[s])
    st = SECTION_TICKS[s]
    evs = motif_walk(SEED + s, st, **LEAD_PARAMS[s])
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=st - 1, end_tick=st))
    phase1.set_unit(0, s, MusicUnit(events=evs))
ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "289-bossanova-motivic-transforms-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written:", P1_MIDI)


# ---------------------------------------------------------------------------
# Phase 2: rules post-process (grid-lock + TIERED pitch discipline)
# ---------------------------------------------------------------------------
def process_lead(raw_events, s):
    """Grid-lock to 16th -> tiered quantize (strong=scale+chord, weak=scale)
    -> octave-normalize to flute range (pc-preserving) -> voice-leading cap
    -> dedup."""
    def in_range_ct(ck):
        return [c for c in chord_tones_for(ck) if 60 <= c <= 96]

    def octave_norm(p):
        p = int(p)
        while p < 60:
            p += 12
        while p > 96:
            p -= 12
        return p

    pitched = [e for e in raw_events if int(e.pitch) != 0]
    g = []
    for e in pitched:
        st = int(round(int(e.start_tick) / GRID) * GRID)
        st = min(st, SECTION_TICKS[s] - GRID)
        g.append(MusicEvent(pitch=int(e.pitch), volume=int(e.volume),
                            start_tick=st, end_tick=max(st + GRID, int(e.end_tick))))
    q = []
    for e in g:
        st = int(e.start_tick)
        lb = min(st // BAR, BARS[s] - 1)
        ck = SECTION_ROT[s][lb % 4]
        ct = in_range_ct(ck)
        w = classify_weight(st, STRONG_GRID_44, BAR)
        p = sq.tiered_quantize(float(int(e.pitch)), weight=w, chord_tones=ct)
        p = octave_norm(p)
        q.append(MusicEvent(pitch=p, volume=int(e.volume),
                            start_tick=st, end_tick=int(e.end_tick)))
    # voice-leading cap (leap <= 9)
    for i in range(1, len(q)):
        if abs(int(q[i].pitch) - int(q[i - 1].pitch)) > 9:
            lb = min(int(q[i].start_tick) // BAR, BARS[s] - 1)
            ck = SECTION_ROT[s][lb % 4]
            ct = in_range_ct(ck)
            q[i] = MusicEvent(
                pitch=min(ct, key=lambda c: abs(c - int(q[i - 1].pitch))),
                volume=int(q[i].volume),
                start_tick=int(q[i].start_tick), end_tick=int(q[i].end_tick))
    # dedup (start_tick, pitch) keep longest
    best = {}
    for e in q:
        key = (int(e.start_tick), int(e.pitch))
        if key not in best or int(e.end_tick) > int(best[key].end_tick):
            best[key] = e
    return sorted(best.values(), key=lambda e: (int(e.start_tick), int(e.pitch)))


phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, rn, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for s, n in enumerate(NAMES):
    phase2.add_section(n, bars=BARS[s])

# lead (row 0): quantize phase-1 raw draft per section
for s in range(N_SECTIONS):
    raw_events = list(phase1.matrix.get_unit((0, s)).events)
    lead_events = process_lead(raw_events, s)
    phase2.set_unit(0, s, MusicUnit(events=lead_events))

acc = {(r, s): [] for r in range(1, 5) for s in range(N_SECTIONS)}

# --- Guitar comp (row 1): bossa comp rhythm, chord stabs (nylon) ---
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    tones = CHORDS[ck]["tones"]
    t0 = lb * BAR
    if s == 0:  # intro: sparse, single downbeat hit
        for t in tones:
            acc[(1, s)].append(MusicEvent(pitch=t, volume=58,
                                          start_tick=t0, end_tick=t0 + 720))
    else:
        for off in COMP_OFFSETS:
            st = t0 + off * 120
            dur = 300 if off in (0, 8) else 240
            for t in tones:
                acc[(1, s)].append(MusicEvent(pitch=t, volume=64,
                                              start_tick=st, end_tick=st + dur))

# --- Rhodes (row 2): sustained whole-bar chord pad (upper register) ---
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    tones = [t + 12 for t in CHORDS[ck]["tones"]]
    t0 = lb * BAR
    vel = 46 if s == 0 else 52
    for t in tones:
        acc[(2, s)].append(MusicEvent(pitch=t, volume=vel,
                                      start_tick=t0, end_tick=t0 + BAR - 60))

# --- Bass (row 3): root on 1, fifth on 3, pickup fifth on & of 4 ---
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    root = CHORDS[ck]["bass"]
    fifth = root + 7
    t0 = lb * BAR
    if s == 0:  # intro: sustained root only
        acc[(3, s)].append(MusicEvent(pitch=root, volume=74,
                                      start_tick=t0, end_tick=t0 + BAR - 120))
    else:
        acc[(3, s)].append(MusicEvent(pitch=root, volume=82,
                                      start_tick=t0, end_tick=t0 + 960))
        acc[(3, s)].append(MusicEvent(pitch=fifth, volume=74,
                                      start_tick=t0 + 960, end_tick=t0 + 1680))
        acc[(3, s)].append(MusicEvent(pitch=fifth, volume=60,
                                      start_tick=t0 + 1680, end_tick=t0 + BAR - 60))

# write accompaniment cells (rows 1-3) into the matrix
for (r, s), evs in acc.items():
    phase2.set_unit(r, s, MusicUnit(events=evs))

# --- Drums (row 4, channel 9): bossa kit (side stick 2&4, light kick, 8th hats)
SIDESTICK, KICK, CHHAT, OHHAT = 37, 36, 42, 46
for s in range(N_SECTIONS):
    evs = []
    for lb in range(BARS[s]):
        t0 = lb * BAR
        if s != 0:  # kick only from A onward, soft on 1 & 3
            evs.append(MusicEvent(pitch=KICK, volume=60, start_tick=t0, end_tick=t0 + 120))
            evs.append(MusicEvent(pitch=KICK, volume=48, start_tick=t0 + 960, end_tick=t0 + 1080))
        evs.append(MusicEvent(pitch=SIDESTICK, volume=88, start_tick=t0 + 480, end_tick=t0 + 540))
        evs.append(MusicEvent(pitch=SIDESTICK, volume=88, start_tick=t0 + 1440, end_tick=t0 + 1500))
        for k in range(8):  # 8th hats
            v = 56 if k % 2 == 0 else 44
            evs.append(MusicEvent(pitch=CHHAT, volume=v,
                                  start_tick=t0 + k * 240, end_tick=t0 + k * 240 + 60))
        if s == 3:  # B section: open hat on the "&" of 4 for lift
            evs.append(MusicEvent(pitch=OHHAT, volume=52,
                                  start_tick=t0 + 1680, end_tick=t0 + 1740))
    phase2.set_unit(4, s, MusicUnit(events=evs))


# --- normalize every cell to exact section boundary (zero-drift invariant) ---
def normalize_cell(unit, total_ticks):
    out = []
    for e in list(unit.events):
        p, v = int(e.pitch), int(e.volume)
        st, et = int(e.start_tick), int(e.end_tick)
        if et > total_ticks:
            et = total_ticks
        if st >= total_ticks:
            st = total_ticks - 1
        out.append(MusicEvent(pitch=p, volume=v, start_tick=st, end_tick=et))
    if not any(int(e.pitch) == 0 and int(e.end_tick) == total_ticks for e in out):
        out.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    out.sort(key=lambda e: (int(e.start_tick), int(e.pitch)))
    return MusicUnit(events=out)


for v in range(N_V):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((v, s))
        st = SECTION_TICKS[s]
        if u is None or len(u.events) == 0:
            phase2.set_unit(v, s, create_empty_unit(st))
        else:
            phase2.set_unit(v, s, normalize_cell(u, st))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", msg2)
assert ok1 and ok2, (msg1, msg2)


# ---------------------------------------------------------------------------
# Audits (pre-humanization = "perfect" layer)
# ---------------------------------------------------------------------------
def grid_audit(composer):
    results = {}
    for v in range(N_V):
        onsets = []
        for s in range(N_SECTIONS):
            u = composer.matrix.get_unit((v, s))
            if u is None:
                continue
            for e in u.events:
                if int(e.pitch) != 0:
                    onsets.append(int(e.start_tick))
        off16 = [o for o in onsets if o % 120 != 0]
        off8 = [o for o in onsets if o % 240 != 0]
        results[vnames[v]] = {"onsets": len(onsets),
                              "off_16th": len(off16), "off_8th": len(off8)}
    return results


def harmony_audit(composer):
    results = {}
    for v in range(4):  # pitched voices only (drums ch9 excluded)
        agg = {"total": 0, "untagged_out_of_scale": 0, "tagged_non_resolving": 0,
               "strong_violations": 0, "tagged_resolving": 0,
               "weak_in_scale": 0, "strong_ok": 0}
        for s in range(N_SECTIONS):
            u = composer.matrix.get_unit((v, s))
            if u is None:
                continue
            notes = [e for e in u.events if int(e.pitch) != 0]
            cpb = {b: CHORDS[SECTION_ROT[s][b % 4]]["pcs"] for b in range(BARS[s])}
            r = audit_voice(notes, sorted(SCALE_PCS), chord_pcs_by_bar=cpb,
                            strong_grid=STRONG_GRID_44, bar_ticks=BAR, grid=EIGHTH)
            for k in ("total", "untagged_out_of_scale", "tagged_non_resolving",
                      "strong_violations", "tagged_resolving", "weak_in_scale",
                      "strong_ok"):
                agg[k] += int(getattr(r, k, 0))
        results[vnames[v]] = agg
    return results


perfect_grid = grid_audit(phase2)
perfect_harmony = harmony_audit(phase2)
print("\nGRID AUDIT (perfect):", json.dumps(perfect_grid, indent=2))
print("\nHARMONY AUDIT (perfect):", json.dumps(perfect_harmony, indent=2))

harmony_pass = all(
    perfect_harmony[v]["untagged_out_of_scale"] == 0
    and perfect_harmony[v]["tagged_non_resolving"] == 0
    and perfect_harmony[v]["strong_violations"] == 0
    for v in vnames[:4]
)
grid_pass = all(perfect_grid[v]["off_16th"] == 0 for v in vnames[:4])
print("\nHARMONY PASS:", harmony_pass, "| GRID PASS:", grid_pass)
assert harmony_pass, "harmony audit failed"
assert grid_pass, "grid audit failed (perfect must be 0 off-16th)"

from visualization.grid import write_grid_visualization  # noqa: E402
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="F major / Bossa Nova Inversion-Retrograde motif")


# ---------------------------------------------------------------------------
# Dual-version export (perfect + humanized) via canonical export_dual
# ---------------------------------------------------------------------------
from workflows.humanize import export_dual  # noqa: E402
hz_instruments = {v[0]: by_name(v[1]).humanize_dna for v in VOICES}
hz_seed = SEED
PERF_MIDI = os.path.join(MIDI_DIR, "289-bossanova-motivic-transforms-perfect.mid")
HUM_MIDI = os.path.join(MIDI_DIR, "289-bossanova-motivic-transforms-humanized.mid")
hz = export_dual(phase2, PERF_MIDI, HUM_MIDI, style=STYLE, seed=hz_seed,
                 bpm=BPM, instruments=hz_instruments)
print("\ndual-version exported")
print("humanize summary:", json.dumps(hz, indent=2))

humanized_grid = grid_audit(phase2)
print("\nGRID AUDIT (humanized):", json.dumps(humanized_grid, indent=2))
hz_off = sum(humanized_grid[v]["off_16th"] for v in vnames[:4])
hz_off_all = sum(humanized_grid[v]["off_16th"] for v in vnames)
print("humanized total off-16th (pitched):", hz_off)
print("humanized total off-16th (all voices):", hz_off_all)


# ---------------------------------------------------------------------------
# READ-ONLY mido verification: zero-drift readback
# ---------------------------------------------------------------------------
import mido  # noqa: E402


def readback(path):
    mid = mido.MidiFile(path)

    def track_total(tr):
        t = 0
        for m in tr:
            if not m.is_meta:
                t += m.time
        return t
    totals = [track_total(t) for t in mid.tracks]
    voice_tots = totals[1:]  # skip tempo track
    zero_drift = len(set(voice_tots)) == 1
    return {"tracks": totals, "voice_tots": voice_tots,
            "zero_drift": zero_drift, "length": voice_tots[0] if voice_tots else 0}


rb_perfect = readback(PERF_MIDI)
rb_humanized = readback(HUM_MIDI)
rb_phase1 = readback(P1_MIDI)
print("\nZERO-DRIFT perfect:", rb_perfect["zero_drift"], rb_perfect["length"])
print("ZERO-DRIFT humanized:", rb_humanized["zero_drift"], rb_humanized["length"])
print("ZERO-DRIFT phase1:", rb_phase1["zero_drift"], rb_phase1["length"])
assert rb_perfect["zero_drift"] and rb_humanized["zero_drift"] and rb_phase1["zero_drift"]

for p in (P1_MIDI, PERF_MIDI, HUM_MIDI):
    sz = os.path.getsize(p)
    print("size", os.path.basename(p), sz)
    assert sz > 40, p


# ---------------------------------------------------------------------------
# provenance + summary
# ---------------------------------------------------------------------------
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402

section_roots = [SECTION_ROT[s][1 % 4] for s in range(N_SECTIONS)]  # midpoint chord
prog_per_section = {NAMES[s]: SECTION_ROT[s] for s in range(N_SECTIONS)}

provenance_meta = {
    "bpm": BPM, "key": "F major", "scale": SCALE_NAME,
    "scale_pcs": sorted(SCALE_PCS),
    "style": STYLE, "method_id": METHOD_ID, "method": METHOD_NAME,
    "layer": LAYER, "form": FORM,
    "motif_prime": MOTIF_P, "motif_retrograde": MOTIF_R,
    "motif_inversion": MOTIF_I, "motif_retro_inversion": MOTIF_RI,
    "inversion_axis": AXIS,
    "section_transforms": {NAMES[s]: LEAD_PARAMS[s]["transform"] for s in range(N_SECTIONS)},
    "sections": N_SECTIONS, "bars": N_BARS,
    "progression_per_section": prog_per_section,
    "section_roots_midpoint": section_roots,
    "seed": SEED, "humanize_seed": hz_seed,
    "voices": [{"name": v[0], "instrument": v[1], "program": v[2], "channel": v[3]}
               for v in VOICES],
}

write_provenance(P1_MIDI, AI_ASSISTED,
                 "Inversion/Retrograde Transform + musicom rules",
                 parameters=dict(provenance_meta, phase="1"),
                 notes="raw single-voice motivic draft, transformed per section "
                       "(P/R/I/P), off-grid jittered onsets, no harmony")
write_provenance(PERF_MIDI, AI_ASSISTED,
                 "Inversion/Retrograde Transform + musicom rules",
                 parameters=dict(provenance_meta, phase="2-perfect", humanize=None),
                 notes="grid-locked perfect layer: tiered pitch discipline "
                       "(strong=scale+chord, weak=scale), zero humanization")
write_provenance(HUM_MIDI, AI_ASSISTED,
                 "Inversion/Retrograde Transform + musicom rules",
                 parameters=dict(provenance_meta, phase="2-humanized",
                                 humanize_seed=hz_seed, humanize_profiles=hz),
                 notes="humanized layer: bossa style profile + per-instrument DNA")

with open(os.path.join(PROJ, "provenance.json"), "w") as f:
    json.dump(provenance_meta, f, indent=2)

summary = {
    "perfect_grid": perfect_grid,
    "humanized_grid": humanized_grid,
    "harmony": perfect_harmony,
    "humanize": hz,
    "zero_drift": {"perfect": rb_perfect["zero_drift"],
                   "humanized": rb_humanized["zero_drift"],
                   "phase1": rb_phase1["zero_drift"],
                   "length_ticks": rb_perfect["length"]},
}
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print("\nPROGRESSION (per section):")
for s in range(N_SECTIONS):
    print("  ", NAMES[s], SECTION_ROT[s], "midpoint:", SECTION_ROT[s][1 % 4])

print("\nDONE compose.")
