# -*- coding: utf-8 -*-
"""
285-flamenco-boids-falseta -- Flamenco / Method 031 Boids Swarm Flocking.

Nightly composition job (ID 1fc3fd65d359). Two-phase architecture:
  Phase 1: raw Reynolds-boids swarm draft (single voice, unquantized pitch + rhythm).
  Phase 2: musicom rules post-process (tiered quantize -> grid lock -> voice leading)
           + full Flamenco texture, exported as dual versions (perfect + humanized).

Engine only: structures + workflows.unitmatrix_composer + scale_quantizer +
rules + pitch_audit + humanize. mido used for READ-ONLY verification only.
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

SEED = 20261104
STYLE = "flamenco"
METHOD_ID = "031"
METHOD_NAME = "Boids Swarm Flocking (Reynolds separation/alignment/cohesion)"
LAYER = "concrete"          # Nature-Led paradigm, concrete engine implementation
FORM = "intro-falseta-letra-falseta-cierre"

PROJ = "/opt/data/projects/Styles/Flamenco/285-flamenco-boids-falseta"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 100
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920 ticks
GRID = 120                   # 16th note
EIGHTH = 240

# E natural Phrygian ("por arriba"): E F G A B C D.
# Its pitch-class set equals C major (relative-major), so the quantizer uses
# the built-in "major" scale rooted at C; the melodic tonic stays E.
SCALE_PCS = {4, 5, 7, 9, 11, 0, 2}
SCALE_NAME = "major"          # ScaleQuantizer built-in; same PC set as E Phrygian
SCALE_ROOT = 60               # C4 reference (pitch-class set == E Phrygian)
sq = ScaleQuantizer(root=SCALE_ROOT, scale=SCALE_NAME)
STRONG_GRID_44 = tuple(STRONG_GRID["4/4"])   # (0, 960) = beats 1 & 3

# Andalusian cadence (descending bass A-G-F-E), fully diatonic to E Phrygian.
CHORDS = {
    "Am": {"pcs": {9, 0, 4},   "bass": 45, "triad": [57, 60, 64]},
    "G":  {"pcs": {7, 11, 2},  "bass": 43, "triad": [55, 59, 62]},
    "F":  {"pcs": {5, 9, 0},   "bass": 41, "triad": [53, 57, 60]},
    "Em": {"pcs": {4, 7, 11},  "bass": 40, "triad": [52, 55, 59]},
}
CHORD_KEYS = ["Am", "G", "F", "Em"]

# form layout (from FORM_PALETTE["intro-falseta-letra-falseta-cierre"])
NAMES = ["Intro", "Falseta1", "Letra", "Falseta2", "Cierre"]
BARS = [4, 8, 8, 8, 4]
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS)            # 32
SECTION_TICKS = [b * BAR for b in BARS]

# per-section cadence rotation (each section its OWN starting chord -> varied
# midpoint roots, avoids the bar-0 tonic monotony)
SECTION_ROT = {
    0: ["Am", "G", "F", "Em"],
    1: ["G", "F", "Em", "Am"],
    2: ["F", "Em", "Am", "G"],
    3: ["Em", "Am", "G", "F"],
    4: ["Am", "G", "F", "Em"],
}

# voices: (voice name, registry instrument name, GM program, channel)
VOICES = [
    ("Falseta",   "acoustic_guitar", 24, 0),
    ("Rasgueado", "steel_acoustic",  25, 1),
    ("Bass",      "acoustic_bass",   32, 2),
    ("Violin",    "violin",          40, 3),
    ("Drums",     "drum_kit",         0, 9),
]
N_V = len(VOICES)
vnames = [v[0] for v in VOICES]


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
    triad = CHORDS[ck]["triad"]
    return sorted({t + 12 * o for t in triad for o in range(-2, 5)})


# ----------------------------------------------------------------------
# Phase 1: raw Reynolds boids swarm -> single-voice unquantized melody
# ----------------------------------------------------------------------
def boids_raw_events(seed, dur_ticks, n_boids, n_samples, center, spread):
    """Reynolds flocking in (time-phase, pitch) space.

    separation (push apart close neighbours) / alignment (match neighbour
    velocity) / cohesion (move to local centroid) + a tonic-centre bias and
    damping. The flock CENTROID pitch is sampled at each checkpoint -> the
    emergent single-voice melody. Onsets + durations are intentionally raw
    (jittered, off-grid); this is the phase-1 generative draft.
    """
    r = np.random.default_rng(seed)
    pos = np.column_stack([
        r.uniform(0.0, 1.0, n_boids),        # normalized time phase
        r.normal(center, spread, n_boids),   # pitch (semitones)
    ])
    vel = np.column_stack([
        r.normal(0.0, 0.05, n_boids),
        r.normal(0.0, 1.5, n_boids),
    ])
    SEP_R, SEP_W, ALI_W, COH_W = 0.15, 1.8, 0.35, 0.25
    TONIC_BIAS, DAMP = 0.04, 0.88
    steps_per_sample = 24
    events = []
    for k in range(n_samples):
        for _ in range(steps_per_sample):
            pos[:, 0] = np.mod(pos[:, 0], 1.0)
            for i in range(n_boids):
                d = pos - pos[i]
                dt = np.minimum(np.abs(d[:, 0]), 1.0 - np.abs(d[:, 0]))
                dist = np.hypot(dt, d[:, 1])
                nb = (dist < SEP_R) & (dist > 1e-6)
                sep = np.zeros(2)
                if nb.any():
                    sep = -SEP_W * np.mean(d[nb] / (dist[nb, None] + 1e-3), axis=0)
                ali = ALI_W * (vel.mean(axis=0) - vel[i])
                coh = COH_W * (pos.mean(axis=0) - pos[i])
                tonic = TONIC_BIAS * (np.array([0.0, center]) - pos[i])
                vel[i] += sep + ali + coh + tonic + r.normal(0.0, 0.5, 2)
                vel[i] *= DAMP
                pos[i] += vel[i]
                pos[i, 1] = float(np.clip(pos[i, 1], 40.0, 104.0))
        midi = float(np.mean(pos[:, 1]))
        onset = int(k * (dur_ticks / n_samples) + r.normal(0.0, 40.0))
        onset = max(0, min(onset, dur_ticks - 60))
        dur = int(max(80.0, (dur_ticks / n_samples) * r.uniform(0.55, 1.15)))
        dur = min(dur, dur_ticks - onset)
        velo = int(np.clip(60 + 30 * float(np.std(vel[:, 1])), 46, 108))
        events.append(MusicEvent(pitch=int(round(midi)), volume=velo,
                                 start_tick=onset, end_tick=onset + dur))
    return events


BOID_PARAMS = {
    0: dict(n_boids=10, n_samples=12, center=68, spread=5),   # Intro sparse
    1: dict(n_boids=16, n_samples=40, center=74, spread=6),   # Falseta1 flourish
    2: dict(n_boids=12, n_samples=30, center=72, spread=5),   # Letra lyrical
    3: dict(n_boids=20, n_samples=48, center=78, spread=7),   # Falseta2 dense/high
    4: dict(n_boids=8,  n_samples=10, center=66, spread=4),   # Cierre resolving
}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("BoidsRaw", program=24, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS[s])
    st = SECTION_TICKS[s]
    evs = boids_raw_events(SEED + s, st, **BOID_PARAMS[s])
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=st - 1, end_tick=st))
    phase1.set_unit(0, s, MusicUnit(events=evs))
ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "285-flamenco-boids-falseta-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written:", P1_MIDI)


# ----------------------------------------------------------------------
# Phase 2: rules post-process (tiered quantize + grid lock + voice leading)
# ----------------------------------------------------------------------
def process_lead(raw_events, s):
    """Tiered pitch discipline: grid-lock -> classify_weight -> tiered_quantize
    (strong -> scale THEN chord; weak -> scale) -> voice-leading cap -> dedup."""
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
        w = classify_weight(st, STRONG_GRID_44, BAR)
        ct = chord_tones_for(ck) if w == "strong" else None
        p = int(sq.tiered_quantize(float(int(e.pitch)), weight=w, chord_tones=ct))
        q.append(MusicEvent(pitch=p, volume=int(e.volume),
                            start_tick=st, end_tick=int(e.end_tick)))
    for i in range(1, len(q)):
        if abs(int(q[i].pitch) - int(q[i - 1].pitch)) > 9:
            lb = min(int(q[i].start_tick) // BAR, BARS[s] - 1)
            ck = SECTION_ROT[s][lb % 4]
            ct = chord_tones_for(ck)
            q[i] = MusicEvent(
                pitch=min(ct, key=lambda c: abs(c - int(q[i - 1].pitch))),
                volume=int(q[i].volume),
                start_tick=int(q[i].start_tick), end_tick=int(q[i].end_tick))
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
lead_chunks = {}
for s in range(N_SECTIONS):
    raw_events = list(phase1.matrix.get_unit((0, s)).events)
    lead_events = process_lead(raw_events, s)
    lead_chunks[s] = lead_events
    phase2.set_unit(0, s, MusicUnit(events=lead_events))

acc = {(r, s): [] for r in range(1, 5) for s in range(N_SECTIONS)}

# --- Rasgueado (row 1): rolling 8th-note chord strum (rasgueado feel)
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    for k in range(0, BAR, EIGHTH):
        tone = triad[(k // EIGHTH) % 3] + 12
        velo = 58 if (k // EIGHTH) % 2 == 0 else 46
        acc[(1, s)].append(MusicEvent(pitch=tone, volume=velo,
                                      start_tick=t0 + k, end_tick=t0 + k + 200))

# --- Bass (row 2): Andalusian root/fifth, octave leap at bar end
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    root = CHORDS[ck]["bass"]
    t0 = lb * BAR
    for beat in range(4):
        bt = t0 + beat * 480
        if beat == 0:
            p, v = root, 104
        elif beat == 1:
            p, v = root + 7, 84
        elif beat == 2:
            p, v = root, 100
        else:
            p, v = root + 12, 90
        acc[(2, s)].append(MusicEvent(pitch=p, volume=v, start_tick=bt, end_tick=bt + 380))

# --- Violin (row 3): counterline (sustained chord tones) in falseta/letra,
#     tonic pedal in the cierre
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    if s in (1, 2, 3):
        third = triad[1] + 12
        fifth = triad[2] + 12
        acc[(3, s)].append(MusicEvent(pitch=third, volume=64,
                                      start_tick=t0, end_tick=t0 + 900))
        acc[(3, s)].append(MusicEvent(pitch=fifth, volume=58,
                                      start_tick=t0 + 960, end_tick=t0 + 1800))
    elif s == 4:
        p = 64 if lb == BARS[4] - 1 else triad[2] + 12
        acc[(3, s)].append(MusicEvent(pitch=p, volume=60,
                                      start_tick=t0, end_tick=t0 + BAR - 60))

# set accompaniment units
for (r, s), evs in acc.items():
    phase2.set_unit(r, s, MusicUnit(events=evs))

# --- Drums (row 4, channel 9): palmas (claps) + cajon (kick/snare) compas
KICK, SNARE, CLAP, HHAT, CRASH = 36, 38, 39, 42, 49
DRUM_DENS = {0: 0.5, 1: 1.0, 2: 0.7, 3: 1.0, 4: 0.8}
for s in range(N_SECTIONS):
    dens = DRUM_DENS[s]
    evs = []
    for lb in range(BARS[s]):
        t0 = lb * BAR
        evs.append(MusicEvent(pitch=KICK, volume=104, start_tick=t0, end_tick=t0 + 140))
        evs.append(MusicEvent(pitch=CLAP, volume=86, start_tick=t0, end_tick=t0 + 80))
        evs.append(MusicEvent(pitch=KICK, volume=100, start_tick=t0 + 960, end_tick=t0 + 1100))
        if dens >= 0.6:
            evs.append(MusicEvent(pitch=SNARE, volume=100, start_tick=t0 + 480, end_tick=t0 + 600))
            evs.append(MusicEvent(pitch=SNARE, volume=104, start_tick=t0 + 1440, end_tick=t0 + 1560))
        if dens >= 0.8:
            evs.append(MusicEvent(pitch=CLAP, volume=90, start_tick=t0 + 720, end_tick=t0 + 800))
            evs.append(MusicEvent(pitch=CLAP, volume=94, start_tick=t0 + 1680, end_tick=t0 + 1760))
        if dens >= 1.0:
            for k in (240, 720, 1200, 1680):
                evs.append(MusicEvent(pitch=HHAT, volume=54, start_tick=t0 + k, end_tick=t0 + k + 60))
    if s == N_SECTIONS - 1:
        t0 = (BARS[s] - 1) * BAR
        evs.append(MusicEvent(pitch=CRASH, volume=90, start_tick=t0 + 1680, end_tick=t0 + 1800))
    phase2.set_unit(4, s, MusicUnit(events=evs))


# --- normalize every cell to exact section boundary (zero-drift invariant)
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


# ----------------------------------------------------------------------
# Audits (pre-humanization = "perfect" layer)
# ----------------------------------------------------------------------
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
grid_pass = all(perfect_grid[v]["off_16th"] == 0 for v in vnames)
print("\nHARMONY PASS:", harmony_pass, "| GRID PASS:", grid_pass)
assert harmony_pass, "harmony audit failed"
assert grid_pass, "grid audit failed (perfect must be 0 off-16th)"

# --- grid visualization (perfect layer, pre-humanization)
from visualization.grid import write_grid_visualization  # noqa: E402
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="E Phrygian / Method 031 Boids + Andalusian cadence")

# ----------------------------------------------------------------------
# Dual-version export (perfect + humanized) via canonical export_dual
# ----------------------------------------------------------------------
from workflows.humanize import export_dual  # noqa: E402
hz_instruments = {v[0]: by_name(v[1]).humanize_dna for v in VOICES}
hz_seed = SEED
PERF_MIDI = os.path.join(MIDI_DIR, "285-flamenco-boids-falseta-perfect.mid")
HUM_MIDI = os.path.join(MIDI_DIR, "285-flamenco-boids-falseta-humanized.mid")
hz = export_dual(phase2, PERF_MIDI, HUM_MIDI, style=STYLE, seed=hz_seed,
                 bpm=BPM, instruments=hz_instruments)
print("dual-version exported")
print("humanize summary:", json.dumps(hz, indent=2))

# humanized layer grid audit (post-humanization, composer now humanized)
humanized_grid = grid_audit(phase2)
print("\nGRID AUDIT (humanized):", json.dumps(humanized_grid, indent=2))
hz_off = sum(humanized_grid[v]["off_16th"] for v in vnames)
print("humanized total off-16th:", hz_off)


# ----------------------------------------------------------------------
# READ-ONLY mido verification: zero-drift readback + off-grid counts
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# provenance + summary + REPORT + README + index.html
# ----------------------------------------------------------------------
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402

section_roots = [SECTION_ROT[s][1 % 4] for s in range(N_SECTIONS)]  # midpoint chord
prog_per_section = {NAMES[s]: SECTION_ROT[s] for s in range(N_SECTIONS)}

provenance_meta = {
    "bpm": BPM, "key": "E Phrygian (por arriba)", "scale": SCALE_NAME,
    "scale_pcs": sorted(SCALE_PCS),
    "style": STYLE, "method_id": METHOD_ID, "method": METHOD_NAME,
    "layer": LAYER, "form": FORM,
    "sections": N_SECTIONS, "bars": N_BARS,
    "progression_per_section": prog_per_section,
    "section_roots_midpoint": section_roots,
    "seed": SEED, "humanize_seed": hz_seed,
    "voices": [{"name": v[0], "instrument": v[1], "program": v[2], "channel": v[3]}
               for v in VOICES],
}

write_provenance(P1_MIDI, AI_ASSISTED,
                 "Boids Swarm Flocking (Method 031) + musicom rules",
                 parameters=dict(provenance_meta, phase="1"),
                 notes="raw single-voice Reynolds-boids draft, unquantized pitch "
                       "+ jittered off-grid rhythm, flock-centroid melody, no harmony")
write_provenance(PERF_MIDI, AI_ASSISTED,
                 "Boids Swarm Flocking (Method 031) + musicom rules",
                 parameters=dict(provenance_meta, phase="2-perfect", humanize=None),
                 notes="grid-locked perfect layer: tiered quantize (strong->scale+chord, "
                       "weak->scale), voice-leading checked, zero humanization")
write_provenance(HUM_MIDI, AI_ASSISTED,
                 "Boids Swarm Flocking (Method 031) + musicom rules",
                 parameters=dict(provenance_meta, phase="2-humanized",
                                 humanize_seed=hz_seed, humanize_profiles=hz),
                 notes="humanized layer: flamenco style profile + per-instrument DNA")

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
