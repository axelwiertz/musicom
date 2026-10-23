# -*- coding: utf-8 -*-
"""259-funk-som-extended — nightly rework (2026-10-23).

Source: 098-funk-som (F minor Funk / Method 075 Self-Organizing Map Composition).
REBUILD from scratch through the canonical UnitMatrixComposer engine, preserving
musical identity (Funk / F minor / 104 BPM / SOM-walk melodic contour / trumpet
+sax+piano+bass+drum-kit) but:
  * LONGER form: 8 sections x 4 bars = 32 bars (source had 6 x 4 = 24).
  * MORE variation: 7 distinct techniques (register shift, transposition,
    density rise, retrograde, inversion, augmentation, diminution + counterline
    + fade) mapped per section.
  * Per-section harmonic regions with MIDPOINT chord root (no bar-0 tonic bug).
  * Humanization + dual-version export (perfect / humanized) via export_dual.

Two-phase architecture:
  Phase 1 (raw): single-voice SOM-C draft. 4x4 toroidal Kohonen map trained on
    8 funk atoms; a Markov walk yields a pitch_index trajectory. Off-grid
    onsets (raw fingerprint). No harmony.
  Phase 2 (rules): snap to 16th grid -> pitch_index -> degree -> nearest chord
    tone of the bar its SNAPPED onset lands in (floor t//BAR) -> per-section
    variation transform -> voice-leading cap -> register/range enforcement ->
    dedupe collisions -> full 5-voice texture -> zero-drift landmark padding.

Engine-only: structures + workflows.unitmatrix_composer + workflows.humanize.
mido used READ-ONLY for audits. Instruments from the importable registry.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization

# ---- instrument registry (source of truth) ---------------------------------
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    TRUMPET, SAXOPHONE, PIANO, DOUBLE_BASS, DRUM_KIT,
)

# ---- concept ---------------------------------------------------------------
GENRE = "Funk"
NAME = "259-funk-som-extended"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 5                       # F
KEY_NAME = "F minor (aeolian)"
AEOLIAN_OFFS = [0, 2, 3, 5, 7, 8, 10]     # rel to F=5 -> F G Ab Bb C Db Eb
SCALE_PCS = set((TONIC + o) % 12 for o in AEOLIAN_OFFS)
BPM = 104
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = BAR // 4                 # 480
SEED = 20261023
rng = np.random.default_rng(SEED)

# ---- form: 8 sections x 4 bars = 32 bars -----------------------------------
FORM = [("Intro", 4), ("Verse", 4), ("Chorus", 4), ("Bridge", 4),
        ("Verse2", 4), ("Chorus2", 4), ("Break", 4), ("Outro", 4)]
N_BARS = sum(b for _, b in FORM)
SECTION_TICKS = {}
_tick = 0
for s, b in FORM:
    SECTION_TICKS[s] = (b * BAR, _tick)
    _tick += b * BAR
TOTAL_TICKS = _tick


def section_of_bar(b):
    acc = 0
    for sname, nbars in FORM:
        if acc <= b < acc + nbars:
            return sname
        acc += nbars
    return FORM[-1][0]


# ---- harmony: per-section regions, F-minor aeolian chords ------------------
DEG_NAMES = ["i", "ii", "III", "iv", "v", "VI", "VII"]
DEG_CHORD_LABELS = ["Fm", "Gdim", "Ab", "Bbm", "Cm", "Db", "Eb"]
DEG_QUALITIES = ["minor", "dim", "major", "minor", "minor", "major", "major"]


def chord_pcs(deg, seventh=False):
    idx = [deg % 7, (deg + 2) % 7, (deg + 4) % 7]
    if seventh:
        idx.append((deg + 6) % 7)
    return frozenset((TONIC + AEOLIAN_OFFS[i]) % 12 for i in idx)


def pc_to_pitch(pc, floor):
    for p in range(floor, floor + 12):
        if p % 12 == pc:
            return p
    return floor


def chord_tones(deg, seventh, floor, ceil):
    pcs = chord_pcs(deg, seventh)
    out = []
    for pc in sorted(pcs):
        p = pc_to_pitch(pc, floor)
        while p <= ceil:
            out.append(p)
            p += 12
    return sorted(out)


# flat per-bar chord specs: (degree, seventh)
# region roots at MIDPOINT bar (start + nbars//2) — varied, never all tonic
CHORD_SPECS = []
for b in range(N_BARS):
    s = section_of_bar(b)
    bi = b - SECTION_TICKS[s][1] // BAR
    if s == "Intro":
        spec = [(0, False), (0, False), (3, False), (4, False)][bi]
    elif s == "Verse":
        spec = [(0, False), (5, False), (3, False), (4, False)][bi]
    elif s == "Chorus":
        spec = [(0, False), (2, False), (6, False), (3, False)][bi]
    elif s == "Bridge":
        spec = [(5, False), (6, False), (0, False), (4, False)][bi]
    elif s == "Verse2":
        spec = [(0, False), (5, False), (2, False), (6, False)][bi]
    elif s == "Chorus2":
        spec = [(0, True), (2, True), (6, True), (3, True)][bi]
    elif s == "Break":
        spec = [(3, True), (4, True), (5, True), (6, True)][bi]
    else:  # Outro
        spec = [(0, False), (5, False), (4, False), (0, False)][bi]
    CHORD_SPECS.append(spec)


def bar_deg(b):
    return CHORD_SPECS[b][0]


# midpoint root per section (bars//2 into section)
section_roots = {}
for sname, nbars in FORM:
    soff = SECTION_TICKS[sname][1] // BAR
    mid = soff + nbars // 2
    d = CHORD_SPECS[mid][0]
    section_roots[sname] = d

# register pools per bar (chord tones realized per voice register)
LEAD_POOL = {b: chord_tones(CHORD_SPECS[b][0], CHORD_SPECS[b][1], 55, 88)
             for b in range(N_BARS)}
SAX_POOL = {b: chord_tones(CHORD_SPECS[b][0], CHORD_SPECS[b][1], 48, 76)
            for b in range(N_BARS)}
PIANO_POOL = {b: chord_tones(CHORD_SPECS[b][0], CHORD_SPECS[b][1], 60, 84)
              for b in range(N_BARS)}
BASS_POOL = {b: chord_tones(CHORD_SPECS[b][0], CHORD_SPECS[b][1], 33, 50)
             for b in range(N_BARS)}


def snap16(t):
    return int(round(t / SIXTEENTH) * SIXTEENTH)


# ============================================================================
# PHASE 1 — RAW SOM-C DRAFT (single voice, off-grid, pitch-index walk)
# ============================================================================
class KohonenSOM:
    """Toroidal 4x4 Self-Organizing Map in 3D feature space (pitch, dur, vel)."""

    def __init__(self, m=4, n=4, dim=3, seed=SEED):
        self.m, self.n, self.dim = m, n, dim
        self.rng = np.random.default_rng(seed)
        self.w = self.rng.uniform(0.1, 0.9, (m, n, dim))
        self.coords = np.array([(i, j) for i in range(m) for j in range(n)])

    def _tdist(self, a, b):
        ar, ac = self.coords[a]
        br, bc = self.coords[b]
        dr = min(abs(ar - br), self.m - abs(ar - br))
        dc = min(abs(ac - bc), self.n - abs(ac - bc))
        return dr * dr + dc * dc

    def train(self, data, epochs=100, alpha0=0.2, sigma0=2.0):
        W = self.w.reshape(-1, self.dim)
        for e in range(epochs):
            alpha = alpha0 * (1.0 - e / float(epochs))
            sigma = max(0.4, sigma0 * (1.0 - e / float(epochs)))
            for x in data:
                bmu = int(np.argmin(np.sum((W - x) ** 2, axis=1)))
                for j in range(self.m * self.n):
                    d = self._tdist(bmu, j)
                    h = np.exp(-d / (2.0 * sigma * sigma))
                    W[j] += alpha * h * (x - W[j])
        self.w = W.reshape(self.m, self.n, self.dim)

    def walk(self, steps, beta=2.0, waypoint=(0, 0), gamma=0.6):
        cur = list(waypoint)
        path = [self.w[cur[0], cur[1]].copy()]
        for _ in range(steps - 1):
            neigh, probs = [], []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]:
                nr, nc = (cur[0] + dr) % self.m, (cur[1] + dc) % self.n
                fd = np.sum((self.w[cur[0], cur[1]] - self.w[nr, nc]) ** 2)
                dr_w = min(abs(nr - waypoint[0]), self.m - abs(nr - waypoint[0]))
                dc_w = min(abs(nc - waypoint[1]), self.n - abs(nc - waypoint[1]))
                wd = np.sqrt(dr_w * dr_w + dc_w * dc_w)
                neigh.append((nr, nc))
                probs.append(np.exp(-beta * fd - gamma * wd))
            probs = np.array(probs) / np.sum(probs)
            cur = neigh[self.rng.choice(len(neigh), p=probs)]
            path.append(self.w[cur[0], cur[1]].copy())
        return np.array(path)


funk_corpus = np.array([
    [0.20, 0.25, 0.85],   # low syncopated slap
    [0.25, 0.125, 0.70],  # 16th funk pop
    [0.50, 0.50, 0.80],   # mid horn punch
    [0.60, 0.25, 0.90],   # high syncopated stab
    [0.75, 0.125, 0.95],  # upper register hook
    [0.40, 0.375, 0.75],  # melodic connective 8th
    [0.85, 0.25, 0.88],   # blue note accent
    [0.30, 0.75, 0.60],   # sustained bass drop
])
som = KohonenSOM(m=4, n=4, dim=3, seed=SEED)
som.train(funk_corpus, epochs=100)

# per-section waypoints + density (notes per 4-bar section)
WAYPOINTS = [(0, 0), (1, 1), (2, 2), (3, 1), (2, 3), (0, 1), (3, 3), (0, 2)]
DENSITY = [12, 16, 20, 14, 16, 20, 24, 12]


def nearest_scale_pitch(pitch, floor=52, ceil=88):
    best, bd = None, 1e9
    for p in range(floor, ceil + 1):
        if p % 12 in SCALE_PCS:
            d = abs(p - pitch)
            if d < bd:
                best, bd = p, d
    return best


raw_events = []                 # dicts: start_tick(abs), pitch_index, velocity, dur
for s_idx, (sname, nbars) in enumerate(FORM):
    sec_start = SECTION_TICKS[sname][1]
    sec_len = SECTION_TICKS[sname][0]
    vecs = som.walk(steps=DENSITY[s_idx], beta=2.0, waypoint=WAYPOINTS[s_idx])
    fracs = np.sort(rng.uniform(0.0, 1.0, len(vecs)))
    for k, w in enumerate(vecs):
        pi = float(np.clip(w[0] + rng.normal(0.0, 0.05), 0.0, 0.999))
        st = sec_start + int(fracs[k] * (sec_len - 1))
        dur = int(max(60.0, w[1] * 400.0))
        vel = int(np.clip(50 + w[2] * 55, 45, 115))
        raw_events.append({"start_tick": st, "pitch_index": pi,
                           "velocity": vel, "dur": dur})


def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    # ALWAYS append the zero-drift terminal landmark. Humanizer passes pitch-0
    # through untouched; this pins the cell end even after duration breathing.
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))
    return u


p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
p1.create_matrix(num_voices=1, num_sections=len(FORM))
p1.add_voice("RawSOM", program=TRUMPET.midi_program, channel=0)
for sname, nbars in FORM:
    p1.add_section(sname, bars=nbars)
for sname, (slen, soff) in SECTION_TICKS.items():
    evs = []
    for e in raw_events:
        if soff <= e["start_tick"] < soff + slen:
            pitch = nearest_scale_pitch(60 + e["pitch_index"] * 24, 55, 88)
            st = e["start_tick"] - soff
            end = min(st + e["dur"], slen - 1)
            evs.append(MusicEvent(pitch=pitch, volume=e["velocity"],
                                  start_tick=st, end_tick=end))
    p1.fill_voice_section("RawSOM", sname, unit_from(evs, slen))
ok1, msg1 = p1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
p1.to_midi(str(midi1))
write_provenance(str(midi1), AI_ASSISTED, f"musicom nightly {NAME}",
                 sources=["methods_db:075 Self-Organizing Map Composition (SOM-C)",
                          f"style:{GENRE}", "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "form": [s for s, _ in FORM],
                             "notes": "raw SOM-C pitch-index trajectory, off-grid"})
print("phase1 midi:", midi1, midi1.stat().st_size, "bytes")

# ============================================================================
# PHASE 2 — RULES POST-PROCESS (grid snap + chord quant + variation + texture)
# ============================================================================
def deg_transpose(d, k=3):
    return (d + k) % 7


def deg_invert(d, pivot=3):
    return (2 * pivot - d) % 7


def lead_events():
    notes = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        pool = LEAD_POOL[b]
        raw = [e for e in raw_events if b * BAR <= e["start_tick"] < (b + 1) * BAR]
        raw.sort(key=lambda e: e["start_tick"])
        if s == "Bridge":
            raw = raw[::-1]                     # retrograde within section
        for e in raw:
            st = snap16(e["start_tick"])
            if st >= (b + 1) * BAR:
                st = (b + 1) * BAR - SIXTEENTH
            d = int(e["pitch_index"] * 7) % 7
            dur = max(SIXTEENTH, snap16(e["dur"]))
            vel = e["velocity"]
            if s == "Chorus":
                d = deg_transpose(d, 3)         # transposition
                vel = min(127, vel + 6)         # density/energy rise
            elif s == "Verse2":
                d = deg_invert(d)               # inversion
            elif s == "Chorus2":
                dur = min(EIGHTH * 2, dur * 2)  # augmentation
            elif s == "Break":
                dur = SIXTEENTH                 # diminution (16th runs)
                vel = min(127, vel + 8)
            elif s == "Outro":
                dur = SIXTEENTH                 # diminution fragment
                vel = max(30, vel - 25)         # fade
            elif s == "Intro":
                dur = min(EIGHTH * 2, dur + EIGHTH)   # sparse
            # register shift per section
            reg_floor = {"Intro": 53, "Bridge": 67}.get(s, 60)
            target = pc_to_pitch((TONIC + AEOLIAN_OFFS[d]) % 12, reg_floor)
            best = min(pool, key=lambda p: abs(p - target))
            for cand in (best - 12, best + 12):
                if abs(cand - target) < abs(best - target):
                    best = cand
            pitch = max(49, min(88, best))
            notes.append(MusicEvent(pitch=pitch, volume=int(vel),
                                    start_tick=st,
                                    end_tick=min(st + dur, (b + 1) * BAR - 1)))
    return notes


def sax_events():
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        pool = SAX_POOL[b]
        bar0 = b * BAR
        if s in ("Chorus", "Chorus2", "Break"):
            # offbeat punch counterline (beats 2.5 and 4.5)
            for off in (BEAT * 2 + EIGHTH, BEAT * 3 + EIGHTH + SIXTEENTH):
                st = bar0 + off
                p = pool[len(pool) // 2] if len(pool) > 1 else pool[0]
                evs.append(MusicEvent(pitch=p, volume=84,
                                      start_tick=st, end_tick=st + SIXTEENTH))
        elif s in ("Verse", "Verse2"):
            for beat in (1, 3):
                st = bar0 + beat * BEAT
                p = pool[min(len(pool) - 1, 1)]
                evs.append(MusicEvent(pitch=p, volume=74,
                                      start_tick=st, end_tick=st + EIGHTH))
    return evs


def piano_events():
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        tones = PIANO_POOL[b]
        bar0 = b * BAR
        # funk syncopation: beat 1, "and" of 2, beat 4
        hits = [0, BEAT + EIGHTH, 3 * BEAT]
        if s in ("Chorus", "Chorus2", "Break"):
            hits = [0, BEAT + EIGHTH, 2 * BEAT + EIGHTH, 3 * BEAT]
        for hit in hits:
            st = bar0 + hit
            for p in tones[:3]:
                evs.append(MusicEvent(pitch=p, volume=72,
                                      start_tick=st, end_tick=st + SIXTEENTH))
    return evs


def bass_events():
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        tones = BASS_POOL[b]
        root = tones[0]
        bar0 = b * BAR
        # funk groove: beat 1 root, "and" octave, 2.5 octave, 3 root, 4 "and" root
        oct_note = root + 12 if root + 12 <= 50 else root
        groove = [(0, root, EIGHTH), (BEAT + SIXTEENTH * 3, oct_note, SIXTEENTH),
                  (2 * BEAT + EIGHTH, oct_note, SIXTEENTH), (3 * BEAT, root, EIGHTH),
                  (3 * BEAT + EIGHTH + SIXTEENTH, root, SIXTEENTH)]
        if s in ("Intro", "Outro"):
            groove = [(0, root, EIGHTH * 2)]
        for off, pitch, dur in groove:
            st = bar0 + off
            evs.append(MusicEvent(pitch=pitch, volume=92,
                                  start_tick=st, end_tick=min(st + dur, bar0 + BAR - 1)))
    return evs


def drums_events():
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        bar0 = b * BAR
        dense = s in ("Chorus", "Chorus2", "Break")
        # closed hats on 16ths
        for h in range(16):
            st = bar0 + h * SIXTEENTH
            v = 86 if h % 4 == 0 else 62
            p = 46 if h == 14 else 42
            evs.append(MusicEvent(pitch=p, volume=v,
                                  start_tick=st, end_tick=st + SIXTEENTH // 2))
        # snare backbeat 2 & 4 + ghost
        for off, v in ((BEAT, 100), (3 * BEAT, 105)):
            evs.append(MusicEvent(pitch=38, volume=v,
                                  start_tick=bar0 + off,
                                  end_tick=bar0 + off + SIXTEENTH))
        if dense:
            evs.append(MusicEvent(pitch=38, volume=55,
                                  start_tick=bar0 + 2 * BEAT + EIGHTH + SIXTEENTH,
                                  end_tick=bar0 + 2 * BEAT + EIGHTH + SIXTEENTH + SIXTEENTH))
        # kick
        k_ons = [0, BEAT + SIXTEENTH * 3, 2 * BEAT + EIGHTH, 3 * BEAT + EIGHTH]
        if s in ("Intro", "Outro"):
            k_ons = [0, 2 * BEAT + EIGHTH]
        for off in k_ons:
            st = bar0 + off
            evs.append(MusicEvent(pitch=36, volume=102,
                                  start_tick=st, end_tick=st + SIXTEENTH))
    return evs


def finalize_pitched(events, pool_by_bar):
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = snap16(e.start_tick)
        if st < 0:
            st = 0
        bar = min(st // BAR, N_BARS - 1)
        pool = pool_by_bar[bar]
        best = min(pool, key=lambda p: abs(p - e.pitch))
        for cand in (best - 12, best + 12):
            if abs(cand - e.pitch) < abs(best - e.pitch):
                best = cand
        out.append(MusicEvent(pitch=best, volume=int(e.volume),
                              start_tick=st, end_tick=max(st + 1, e.end_tick)))
    # dedupe (start, pitch) keep longest
    seen = {}
    res = []
    for e in out:
        if e.pitch == 0:
            res.append(e)
            continue
        key = (e.start_tick, e.pitch)
        if key in seen:
            seen[key].end_tick = max(seen[key].end_tick, e.end_tick)
        else:
            seen[key] = e
            res.append(e)
    res.sort(key=lambda e: (e.start_tick, e.pitch))
    return res


def cap_leaps(events, pool_by_bar, max_leap=10):
    evs = sorted([e for e in events if e.pitch], key=lambda e: e.start_tick)
    for i in range(1, len(evs)):
        prev, cur = evs[i - 1], evs[i]
        if cur.start_tick - prev.start_tick <= BAR and abs(cur.pitch - prev.pitch) > max_leap:
            bar = min(cur.start_tick // BAR, N_BARS - 1)
            pool = pool_by_bar[bar]
            target = prev.pitch + max_leap if cur.pitch > prev.pitch else prev.pitch - max_leap
            best = min(pool, key=lambda p: (abs(p - target), abs(p - cur.pitch)))
            cur.pitch = best
    return evs


lead_q = cap_leaps(finalize_pitched(lead_events(), LEAD_POOL), LEAD_POOL)
sax_q = finalize_pitched(sax_events(), SAX_POOL)
piano_q = finalize_pitched(piano_events(), PIANO_POOL)
bass_q = finalize_pitched(bass_events(), BASS_POOL)
drums_q = drums_events()

VOICES = [
    ("Lead", TRUMPET.midi_program, 0),
    ("Sax", SAXOPHONE.midi_program, 1),
    ("Piano", PIANO.midi_program, 2),
    ("Bass", DOUBLE_BASS.midi_program, 3),
    ("Drums", 0, 9),
]
events_by_voice = {
    "Lead": lead_q, "Sax": sax_q, "Piano": piano_q, "Bass": bass_q, "Drums": drums_q,
}

composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
composer.create_matrix(num_voices=len(VOICES), num_sections=len(FORM))
for vname, prog, ch in VOICES:
    composer.add_voice(vname, program=prog, channel=ch)
for sname, nbars in FORM:
    composer.add_section(sname, bars=nbars)

for vname, prog, ch in VOICES:
    evs = events_by_voice[vname]
    for sname, (slen, soff) in SECTION_TICKS.items():
        # SORT by start_tick: the humanizer's forward-clamp assumes ascending
        # onsets; unsorted cells get pinned off-grid. Sort before clipping.
        seg = sorted([e for e in evs if soff <= e.start_tick < soff + slen],
                     key=lambda e: (e.start_tick, e.pitch))
        for e in seg:
            e.start_tick -= soff
            e.end_tick -= soff
            if e.end_tick > slen:
                e.end_tick = slen
            if e.end_tick <= e.start_tick:
                e.end_tick = e.start_tick + 1
        composer.fill_voice_section(vname, sname, unit_from(seg, slen))

# ---- dual-version export (perfect then humanized) --------------------------
hz_seed = SEED + 1
hz_instruments = {
    "Lead": (4.0, 8.0, 0.0, 0.02),   # lock: funk lead on top (was Brass 7.0ms/4.0ms lag)
    "Sax": SAXOPHONE.humanize_dna,
    "Piano": PIANO.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=GENRE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked, no jitter"),
                          (humanized_path, "2-humanized", "style+instrument humanized")):
    write_provenance(str(path), AI_ASSISTED, f"musicom nightly {NAME}",
                     sources=["methods_db:075 Self-Organizing Map Composition (SOM-C)",
                              f"style:{GENRE}", "phase:2 rules",
                              f"humanize_seed:{hz_seed}"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "form": [s for s, _ in FORM],
                                 "humanize": hz, "note": note})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

# ---- grid visualization + summary ------------------------------------------
try:
    write_grid_visualization(composer.matrix,
                             str(ROOT / "Analysis" / "grid_visualization.txt"))
except Exception as exc:
    print("grid viz skipped:", exc)

summary = {
    "project": NAME, "genre": GENRE, "key": KEY_NAME, "bpm": BPM,
    "form": [s for s, _ in FORM], "bars": N_BARS, "total_ticks": TOTAL_TICKS,
    "source": "098-funk-som", "decision": "redesign (index.html + root provenance missing)",
    "variations": {
        "Intro": "register shift (low) + sparse",
        "Verse": "base motif (SOM-C contour)",
        "Chorus": "transposition (+3 degrees) + density rise",
        "Bridge": "retrograde + register shift (upper)",
        "Verse2": "inversion (pivot degree 3)",
        "Chorus2": "augmentation (x2) + 7th color",
        "Break": "diminution (16th) + sax counterline",
        "Outro": "diminution fragment + fade",
    },
    "section_roots_midpoint": {s: DEG_CHORD_LABELS[section_roots[s]]
                               for s, _ in FORM},
    "voices": [v for v, _, _ in VOICES],
    "humanize_seed": hz_seed,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("DONE compose")
