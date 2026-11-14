# -*- coding: utf-8 -*-
"""303-funk-som-suite -- extended rework of 098-funk-som (Funk / Method 075 SOM-C).

Nightly rework job (2026-11-14). Source 098-funk-som audited:
  standards 1-5 PASS (engine, zero-drift, grid, 5 tracks, two-phase).
  standard 6 FAIL: index.html MISSING + no root provenance.json.
  -> REDESIGN (packaging) + EXTEND (compliant musical core reused as DNA seed).

Two-phase architecture:
  Phase 1 = raw Self-Organizing Map trajectory walk (4x4 toroidal lattice,
            pitch/dur/vel prototypes, unquantized pitch + continuous rhythm),
            single voice (Trumpet). 8 sections.
  Phase 2 = musicom rules post-process (16th-grid snap, blanket chord-tone
            quantization per bar, voice-leading leap cap <=9, register clamp,
            dedup) + full 5-voice Funk arrangement, dual-version export
            (perfect + humanized) via canonical export_dual.

Longer + more varied:
  source = 6 sections x 4 bars = 24 bars.
  new    = 8 sections x 4 bars = 32 bars (N+2 sections, +33% length).

Variation techniques (6 applied):
  1. Transposition      -- Verse2 moved to subdominant Bb region (iv-i-VI-v)
                           + lead contour pitched up a perfect 4th (+5).
  2. Register shift     -- Chorus2 lead +1 octave (register 65-96).
  3. Retrograde         -- Bridge lead contour reversed in time.
  4. Augmentation       -- Breakdown lead + bass durations doubled (half-speed).
  5. Density contrast   -- Breakdown thins (sax/piano tacet, sparse drums);
                           Chorus/Chorus2 full (pad + sax + ghost snare).
  6. Counterline        -- Tenor Sax offbeat punches on beats 2.5 / 4.5.

Engine only: structures + workflows.unitmatrix_composer + humanize + provenance
+ grid. mido used for READ-ONLY verification only.
"""
import os
import json
import hashlib
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth for GM programs + humanize DNA).
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import TRUMPET, SAXOPHONE, DOUBLE_BASS, PIANO, DRUM_KIT

SEED = 20261114
hz_seed = int(hashlib.md5(("funk-som-suite-%d" % SEED).encode()).hexdigest()[:8], 16)
STYLE = "funk"
BPM = 104
SOURCE = "098-funk-som"
SOURCE_MIDI = "/opt/data/projects/Styles/Funk/098-funk-som/MIDI/098-funk-som.mid"

PROJ = "/opt/data/projects/Styles/Funk/303-funk-som-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920 ticks
GRID16 = 120                 # 16th note
GRID8 = 240                  # 8th note

# F natural minor: F G Ab Bb C Db Eb -> {5,7,8,10,0,1,3}
KEY_PCS = {5, 7, 8, 10, 0, 1, 3}
TONIC_PC = 5

# form: 8 sections x 4 bars = 32 bars
NAMES = ["Intro", "Verse", "Chorus", "Bridge", "Verse2", "Chorus2", "Breakdown", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER      # 32
SECTION_TICKS = BAR * BARS_PER      # 7680

# Per-bar progression (root_pc, quality). Each section its own short region.
# F minor degrees: i=Fm(5) ii=Gdim(7) III=Ab(8) iv=Bbm(10) v=Cm(0) VI=Db(1) VII=Eb(3)
PROG = [
    (5, 'm'), (5, 'm'), (10, 'm'), (0, 'm'),     # Intro    i i iv v
    (5, 'm'), (1, 'M'), (10, 'm'), (0, 'm'),     # Verse    i VI iv v
    (5, 'm'), (8, 'M'), (3, 'M'), (10, 'm'),     # Chorus   i III VII iv
    (1, 'M'), (3, 'M'), (5, 'm'), (0, 'm'),      # Bridge   VI VII i v
    (10, 'm'), (5, 'm'), (1, 'M'), (0, 'm'),     # Verse2   iv i VI v  (transposed)
    (5, 'm'), (8, 'M'), (3, 'M'), (10, 'm'),     # Chorus2  i III VII iv (register up)
    (1, 'M'), (3, 'M'), (5, 'm'), (5, 'm'),      # Breakdown VI VII i i (augmented)
    (5, 'm'), (1, 'M'), (0, 'm'), (5, 'm'),      # Outro    i VI v i
]
assert len(PROG) == N_BARS


def chord_intervals(q):
    return (0, 3, 7) if q == 'm' else (0, 4, 7)


def chord_pcs(root_pc, q):
    return {(root_pc + i) % 12 for i in chord_intervals(q)}


def chord_tones(root_pc, q, lo, hi):
    iv = chord_intervals(q)
    return [p for p in range(lo, hi + 1) if (p - root_pc) % 12 in iv]


def low_root(root_pc, lo=33, hi=45):
    for p in range(lo, hi + 1):
        if p % 12 == root_pc:
            return p
    return lo


# voices: (voice name, GM program, channel, instrument-registry object)
VOICES = [
    ("Lead",  TRUMPET.midi_program,    0, TRUMPET),
    ("Sax",   SAXOPHONE.midi_program,  1, SAXOPHONE),
    ("Piano", PIANO.midi_program,      2, PIANO),
    ("Bass",  DOUBLE_BASS.midi_program, 3, DOUBLE_BASS),
    ("Drums", 0,                       9, DRUM_KIT),
]
N_V = len(VOICES)
vnames = [v[0] for v in VOICES]

HZ_INSTRUMENTS = {v[0]: v[3].humanize_dna for v in VOICES}


# ----------------------------------------------------------------------
# Kohonen Self-Organizing Map (Method 075 identity, reused from 098)
# ----------------------------------------------------------------------
class KohonenSOM:
    def __init__(self, m=4, n=4, dim=3, seed=SEED):
        self.m, self.n, self.dim = m, n, dim
        self.rng = np.random.default_rng(seed)
        self.w = self.rng.uniform(0.1, 0.9, (m, n, dim))
        self.grid_coords = np.array([(i, j) for i in range(m) for j in range(n)])

    def _toroidal_dist_sq(self, c_idx, j_idx):
        c_r, c_c = self.grid_coords[c_idx]
        j_r, j_c = self.grid_coords[j_idx]
        dr = min(abs(c_r - j_r), self.m - abs(c_r - j_r))
        dc = min(abs(c_c - j_c), self.n - abs(c_c - j_c))
        return dr * dr + dc * dc

    def train(self, data, epochs=100, alpha0=0.2, sigma0=2.0):
        W = self.w.reshape(-1, self.dim)
        for e in range(epochs):
            alpha = alpha0 * (1.0 - e / float(epochs))
            sigma = max(0.4, sigma0 * (1.0 - e / float(epochs)))
            for x in data:
                bmu = int(np.argmin(np.sum((W - x) ** 2, axis=1)))
                for j in range(self.m * self.n):
                    d_sq = self._toroidal_dist_sq(bmu, j)
                    h = np.exp(-d_sq / (2.0 * sigma * sigma))
                    W[j] += alpha * h * (x - W[j])
        self.w = W.reshape(self.m, self.n, self.dim)

    def walk(self, steps, beta=2.0, waypoint=(0, 0), gamma=0.6):
        curr = list(waypoint)
        path = [self.w[curr[0], curr[1]].copy()]
        for _ in range(steps - 1):
            neighbors, probs = [], []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]:
                nr = (curr[0] + dr) % self.m
                nc = (curr[1] + dc) % self.n
                feat_dist_sq = np.sum((self.w[curr[0], curr[1]] - self.w[nr, nc]) ** 2)
                dr_w = min(abs(nr - waypoint[0]), self.m - abs(nr - waypoint[0]))
                dc_w = min(abs(nc - waypoint[1]), self.n - abs(nc - waypoint[1]))
                way_dist = np.sqrt(dr_w * dr_w + dc_w * dc_w)
                probs.append(np.exp(-beta * feat_dist_sq - gamma * way_dist))
                neighbors.append((nr, nc))
            probs = np.array(probs) / np.sum(probs)
            curr = neighbors[self.rng.choice(len(neighbors), p=probs)]
            path.append(self.w[curr[0], curr[1]].copy())
        return np.array(path)


FUNK_CORPUS = np.array([
    [0.2, 0.25, 0.85], [0.25, 0.125, 0.7], [0.5, 0.5, 0.8], [0.6, 0.25, 0.9],
    [0.75, 0.125, 0.95], [0.4, 0.375, 0.75], [0.85, 0.25, 0.88], [0.3, 0.75, 0.6],
])

som = KohonenSOM(m=4, n=4, dim=3, seed=SEED)
som.train(FUNK_CORPUS, epochs=100)
rng = np.random.default_rng(SEED)


# ----------------------------------------------------------------------
# Phase 1: raw SOM trajectory walk -> single-voice unquantized draft
# ----------------------------------------------------------------------
WAYPOINTS = [(0, 0), (1, 1), (2, 2), (3, 1), (1, 2), (2, 3), (3, 3), (0, 2)]
DENSITIES = [20, 32, 40, 28, 32, 40, 16, 20]


def generate_phase1_events():
    all_events = []
    for s_idx in range(N_SECTIONS):
        n_ev = DENSITIES[s_idx]
        wp = WAYPOINTS[s_idx]
        walk_vecs = som.walk(steps=n_ev, beta=2.0, waypoint=wp, gamma=0.6)
        fracs = rng.uniform(0.7, 1.3, size=n_ev)
        fracs /= np.sum(fracs)
        raw_iois = fracs * (SECTION_TICKS - 240)
        sec_events = []
        current_tick = 0.0
        for i in range(n_ev):
            w = walk_vecs[i]
            raw_pitch = 53.0 + w[0] * 36.0 + rng.normal(0.0, 0.8)
            ioi = raw_iois[i]
            dur = max(40.0, min(ioi * 0.9, 60.0 + w[1] * 360.0))
            vel = int(np.clip(55 + w[2] * 55, 45, 115))
            st = int(round(current_tick))
            en = int(round(current_tick + dur))
            if en > SECTION_TICKS - 1:
                en = SECTION_TICKS - 1
            if en > st:
                sec_events.append(MusicEvent(pitch=int(round(raw_pitch)), volume=vel,
                                             start_tick=st, end_tick=en))
            current_tick += ioi
        if not sec_events or sec_events[-1].end_tick < SECTION_TICKS:
            sec_events.append(MusicEvent(pitch=0, volume=0,
                                         start_tick=SECTION_TICKS - 1,
                                         end_tick=SECTION_TICKS))
        all_events.append(sec_events)
    return all_events


p1_section_events = generate_phase1_events()

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=TRUMPET.midi_program, channel=0)
for s_idx, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    phase1.set_unit(0, s_idx, MusicUnit(events=p1_section_events[s_idx]))
ok1, msg1 = phase1.validate()
assert ok1, "Phase 1 validate failed: %s" % msg1
P1_MIDI = os.path.join(MIDI_DIR, "303-funk-som-suite-phase1.mid")
phase1.to_midi(P1_MIDI)
print("PHASE1 validate:", msg1, "->", P1_MIDI)


# ----------------------------------------------------------------------
# Phase 2: rules post-process + full 5-voice arrangement
# ----------------------------------------------------------------------
def snap(tick):
    return int(round(tick / float(GRID16)) * GRID16)


# per-section lead variation spec: (transform, transpose_semitones, lo, hi)
LEAD_SPEC = {
    0: ("none",          0, 58, 84),   # Intro    (baseline, lower register)
    1: ("none",          0, 58, 84),   # Verse    (baseline contour)
    2: ("none",          0, 62, 88),   # Chorus   (register up, denser)
    3: ("retro",         0, 58, 84),   # Bridge   (retrograde contour)
    4: ("transpose",     5, 62, 89),   # Verse2   (transposition +4th)
    5: ("octave",       12, 65, 96),   # Chorus2  (register shift +1 oct)
    6: ("retro_augment", 0, 55, 79),   # Breakdown (retrograde + augmentation)
    7: ("none",          0, 55, 84),   # Outro    (baseline, sparse)
}


def process_lead(s_idx, raw_events):
    t, trans, rlo, rhi = LEAD_SPEC[s_idx]
    items = [(int(e.pitch),
              max(GRID16, snap(int(e.end_tick) - int(e.start_tick))),
              int(e.volume), int(e.start_tick))
             for e in raw_events if int(e.pitch) != 0]
    if t in ("retro", "retro_augment"):
        items = list(reversed(items))
    if t == "transpose":
        items = [(p + trans, d, v, s) for p, d, v, s in items]
    elif t == "octave":
        items = [(p + trans, d, v, s) for p, d, v, s in items]
    if t in ("augment", "retro_augment"):
        items = [(p, min(SECTION_TICKS, d * 2), v, s) for p, d, v, s in items]

    out = []
    last_end = 0
    prev_pitch = 65
    rebuild = t in ("retro", "retro_augment", "augment")
    for (p, d, v, orig_start) in items:
        if rebuild:
            st = snap(last_end)
        else:
            st = snap(orig_start)
            if st < last_end:
                st = last_end
        if st >= SECTION_TICKS - GRID16:
            continue
        en = min(SECTION_TICKS, st + d)
        bar = s_idx * BARS_PER + min(st // BAR, BARS_PER - 1)
        root_pc, q = PROG[bar]
        tones = chord_tones(root_pc, q, rlo, rhi)
        if not tones:
            tones = [rlo]
        p_q = min(tones, key=lambda t: (abs(t - p), t))
        if abs(p_q - prev_pitch) > 9:
            p_q = min(tones, key=lambda t: abs(t - prev_pitch))
        out.append(MusicEvent(pitch=p_q, volume=v, start_tick=st, end_tick=en))
        prev_pitch = p_q
        last_end = en
    # dedup (start_tick, pitch) keep longest
    best = {}
    for e in out:
        k = (int(e.start_tick), int(e.pitch))
        if k not in best or int(e.end_tick) > int(best[k].end_tick):
            best[k] = e
    return sorted(best.values(), key=lambda e: (int(e.start_tick), int(e.pitch)))


# Tenor Sax counterline: offbeat punches on beats 2.5 & 4.5 (density contrast:
# tacet in Intro/Breakdown/Outro).
SAX_ACTIVE = {1, 2, 3, 4, 5}


def build_sax(s_idx):
    evs = []
    if s_idx in SAX_ACTIVE:
        prev = 53
        for b in range(BARS_PER):
            bar = s_idx * BARS_PER + b
            root_pc, q = PROG[bar]
            t0 = b * BAR
            for off in (BAR // 4 + GRID16, 3 * (BAR // 4) + GRID16):
                st = t0 + off
                tones = chord_tones(root_pc, q, 50, 74)
                p = min(tones, key=lambda t: abs(t - prev))
                evs.append(MusicEvent(pitch=p, volume=85, start_tick=st,
                                      end_tick=st + GRID16))
                prev = p
    return evs


# Piano funk comping: syncopated chord stabs (tacet in Breakdown).
PIANO_ACTIVE = {0, 1, 2, 3, 4, 5, 7}


def build_piano(s_idx):
    evs = []
    if s_idx in PIANO_ACTIVE:
        for b in range(BARS_PER):
            bar = s_idx * BARS_PER + b
            root_pc, q = PROG[bar]
            t0 = b * BAR
            tones = chord_tones(root_pc, q, 60, 77)[:3]
            for hit in (0, 600, 1440):
                st = t0 + hit
                for p in tones:
                    evs.append(MusicEvent(pitch=p, volume=78, start_tick=st,
                                          end_tick=st + GRID16))
    return evs


# Bass: funk slap/pop groove; Breakdown augmented (whole-bar roots).
def build_bass(s_idx):
    evs = []
    for b in range(BARS_PER):
        bar = s_idx * BARS_PER + b
        root_pc, q = PROG[bar]
        t0 = b * BAR
        r = low_root(root_pc, 33, 45)
        oct_note = r + 12
        if s_idx == 6:  # Breakdown: augmentation (long roots, half-speed)
            evs.append(MusicEvent(pitch=r, volume=90, start_tick=t0,
                                  end_tick=t0 + BAR - GRID8))
            evs.append(MusicEvent(pitch=oct_note, volume=78, start_tick=t0 + 960,
                                  end_tick=t0 + 960 + BAR // 2 - GRID8))
        else:
            groove = [
                (0, r, GRID8), (360, oct_note, GRID16), (600, oct_note, GRID16),
                (960, r, GRID8), (1560, r, GRID16), (1800, oct_note, GRID16),
            ]
            for off, pitch, dur in groove:
                evs.append(MusicEvent(pitch=pitch, volume=94, start_tick=t0 + off,
                                      end_tick=t0 + off + dur))
    return evs


# Drums (channel 9): full funk groove; Breakdown sparse.
KICK, SNARE, HH_CL, HH_OP, CRASH = 36, 38, 42, 46, 49


def build_drums(s_idx):
    evs = []
    if s_idx == 6:  # Breakdown: sparse (kick on beat 1, soft 8th hats)
        for b in range(BARS_PER):
            t0 = b * BAR
            evs.append(MusicEvent(pitch=KICK, volume=88, start_tick=t0,
                                  end_tick=t0 + GRID8))
            for k in (GRID8, 3 * GRID8, 5 * GRID8, 7 * GRID8):
                evs.append(MusicEvent(pitch=HH_CL, volume=48, start_tick=t0 + k,
                                      end_tick=t0 + k + GRID16))
        return evs
    for b in range(BARS_PER):
        t0 = b * BAR
        for h in range(16):
            st = t0 + h * GRID16
            v = 88 if h % 4 == 0 else 68
            p = HH_OP if h == 14 else HH_CL
            evs.append(MusicEvent(pitch=p, volume=v, start_tick=st,
                                  end_tick=st + GRID16 // 2))
        for off, v in ((480, 100), (1440, 105), (1320, 55)):
            evs.append(MusicEvent(pitch=SNARE, volume=v, start_tick=t0 + off,
                                  end_tick=t0 + off + GRID16))
        for off in (0, 360, 720, 1200):
            evs.append(MusicEvent(pitch=KICK, volume=102, start_tick=t0 + off,
                                  end_tick=t0 + off + GRID16))
    if s_idx == N_SECTIONS - 1:  # Outro: final crash
        t0 = (BARS_PER - 1) * BAR
        evs.append(MusicEvent(pitch=CRASH, volume=90, start_tick=t0 + 1680,
                              end_tick=t0 + 1800))
    return evs


phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch, _ in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for s, name in enumerate(NAMES):
    phase2.add_section(name, bars=BARS_PER)

# row 0 lead (quantized SOM walk + per-section variation)
for s in range(N_SECTIONS):
    lead_events = process_lead(s, p1_section_events[s])
    phase2.set_unit(0, s, MusicUnit(events=lead_events))
# rows 1-4 accompaniment
for s in range(N_SECTIONS):
    phase2.set_unit(1, s, MusicUnit(events=build_sax(s)))
    phase2.set_unit(2, s, MusicUnit(events=build_piano(s)))
    phase2.set_unit(3, s, MusicUnit(events=build_bass(s)))
    phase2.set_unit(4, s, MusicUnit(events=build_drums(s)))


def normalize_cell(unit, total_ticks):
    out = []
    for e in list(unit.events):
        p, v = int(e.pitch), int(e.volume)
        st, et = int(e.start_tick), int(e.end_tick)
        if et > total_ticks:
            et = total_ticks
        if st >= total_ticks:
            st = total_ticks - 1
        if st < 0:
            st = 0
        if et <= st:
            et = min(total_ticks, st + 1)
        out.append(MusicEvent(pitch=p, volume=v, start_tick=st, end_tick=et))
    if not any(int(e.pitch) == 0 and int(e.end_tick) == total_ticks for e in out):
        out.append(MusicEvent(pitch=0, volume=0, start_tick=total_ticks - 1,
                              end_tick=total_ticks))
    out.sort(key=lambda e: (int(e.start_tick), int(e.pitch)))
    return MusicUnit(events=out)


for v in range(N_V):
    for s in range(N_SECTIONS):
        u = phase2.matrix.get_unit((v, s))
        if u is None or len(u.events) == 0:
            phase2.set_unit(v, s, create_empty_unit(SECTION_TICKS))
        else:
            phase2.set_unit(v, s, normalize_cell(u, SECTION_TICKS))

ok2, msg2 = phase2.validate()
print("PHASE2 validate:", msg2)
assert ok2, msg2


# ----------------------------------------------------------------------
# Grid audit (pre-humanization = perfect layer)
# ----------------------------------------------------------------------
def grid_audit(composer):
    assert composer.matrix is not None
    results = {}
    for v in range(N_V):
        off = 0
        n = 0
        for s in range(N_SECTIONS):
            u = composer.matrix.get_unit((v, s))
            if u is None:
                continue
            for e in u.events:
                if int(e.pitch) != 0:
                    n += 1
                    if int(e.start_tick) % 120 != 0:
                        off += 1
        results[vnames[v]] = {"onsets": n, "off_grid": off}
    return results


perfect_grid = grid_audit(phase2)
print("\nGRID AUDIT (perfect):", json.dumps(perfect_grid, indent=2))
grid_pass = all(perfect_grid[v]["off_grid"] == 0 for v in vnames)
assert grid_pass, "grid audit failed (perfect must be 0 off-grid)"
print("GRID PASS (perfect off-grid == 0):", grid_pass)

grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
assert phase2.matrix is not None
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="F minor / Funk SOM-C suite")


# ----------------------------------------------------------------------
# Dual-version export (perfect + humanized) via canonical export_dual
# ----------------------------------------------------------------------
PERF_MIDI = os.path.join(MIDI_DIR, "303-funk-som-suite-perfect.mid")
HUM_MIDI = os.path.join(MIDI_DIR, "303-funk-som-suite-humanized.mid")
hz = export_dual(phase2, PERF_MIDI, HUM_MIDI, style=STYLE, seed=hz_seed,
                 bpm=BPM, instruments=HZ_INSTRUMENTS)
print("dual-version exported")
print("humanize summary:", json.dumps(hz, indent=2, default=str))

humanized_grid = grid_audit(phase2)
print("\nGRID AUDIT (humanized):", json.dumps(humanized_grid, indent=2))
hz_off = sum(humanized_grid[v]["off_grid"] for v in vnames)
print("humanized total off-grid:", hz_off)
assert hz_off > 0, "humanization did not run (off-grid == 0)"


# ----------------------------------------------------------------------
# READ-ONLY mido verification (zero-drift + sizes)
# ----------------------------------------------------------------------
import mido  # noqa: E402  (READING ONLY - analysis)


def readback(path):
    mid = mido.MidiFile(path)
    totals = []
    for tr in mid.tracks:
        t = 0
        for m in tr:
            if not m.is_meta:
                t += m.time
        totals.append(t)
    voice_tots = totals[1:]
    return {"tracks": len(mid.tracks) - 1,
            "voice_tots": voice_tots,
            "zero_drift": len(set(voice_tots)) == 1,
            "length": voice_tots[0] if voice_tots else 0}


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
# provenance + root summary
# ----------------------------------------------------------------------
def section_midpoint(s):
    lb = BARS_PER // 2
    root_pc, q = PROG[s * BARS_PER + lb]
    return [root_pc, q]


section_roots = [section_midpoint(s) for s in range(N_SECTIONS)]
prog_per_section = {
    NAMES[s]: ["%d%s" % (PROG[s * BARS_PER + b][0],
                         PROG[s * BARS_PER + b][1])
               for b in range(BARS_PER)]
    for s in range(N_SECTIONS)
}

provenance_meta = {
    "bpm": BPM, "key": "F", "key_label": "F natural minor (aeolian/pentatonic)",
    "scale": "minor", "scale_pcs": sorted(KEY_PCS),
    "style": STYLE, "source": SOURCE,
    "source_midi": SOURCE_MIDI,
    "method": "075 Self-Organizing Map Composition (SOM-C), extended",
    "sections": N_SECTIONS, "bars": N_BARS,
    "bars_per_section": BARS_PER,
    "progression_per_section": prog_per_section,
    "section_roots_midpoint": section_roots,
    "variation_techniques": [
        "transposition +4th / subdominant Bb region (Verse2)",
        "register shift +1 octave (Chorus2)",
        "retrograde contour (Bridge)",
        "augmentation x2 durations (Breakdown)",
        "density contrast (Breakdown sparse vs Chorus full)",
        "sax counterline offbeat punches (Verse/Chorus/Bridge/Verse2/Chorus2)",
    ],
    "seed": SEED, "humanize_seed": hz_seed,
    "voices": [{"name": v[0], "program": v[1], "channel": v[2]} for v in VOICES],
}

write_provenance(P1_MIDI, AI_ASSISTED,
                 "Funk SOM-C trajectory walk (raw, pre-rules)",
                 sources=[SOURCE_MIDI],
                 parameters=dict(provenance_meta, phase="1"),
                 notes="raw single-voice SOM walk (4x4 toroidal lattice), unquantized "
                       "pitch + continuous rhythm, no harmony")
write_provenance(PERF_MIDI, AI_ASSISTED,
                 "Funk SOM-C + musicom rules (grid-locked)",
                 sources=[SOURCE_MIDI, "303-funk-som-suite-phase1.mid"],
                 parameters=dict(provenance_meta, phase="2-perfect", humanize=None),
                 notes="grid-locked perfect layer: 16th-grid snap, blanket chord-tone "
                       "quantize per bar, voice-leading cap <=9, dedup")
write_provenance(HUM_MIDI, AI_ASSISTED,
                 "Funk SOM-C + musicom rules + humanize",
                 sources=[SOURCE_MIDI, "303-funk-som-suite-phase1.mid",
                          "303-funk-som-suite-perfect.mid"],
                 parameters=dict(provenance_meta, phase="2-humanized",
                                 humanize_seed=hz_seed, humanize_profiles=hz),
                 notes="humanized layer: funk style profile + per-instrument DNA")

with open(os.path.join(PROJ, "provenance.json"), "w") as f:
    json.dump(provenance_meta, f, indent=2)

summary = {
    "perfect_grid": perfect_grid,
    "humanized_grid": humanized_grid,
    "humanize": hz,
    "zero_drift": {"perfect": rb_perfect["zero_drift"],
                   "humanized": rb_humanized["zero_drift"],
                   "phase1": rb_phase1["zero_drift"],
                   "length_ticks": rb_perfect["length"]},
}
with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\nPROGRESSION (per section) + midpoint:")
for s in range(N_SECTIONS):
    print("  ", NAMES[s], prog_per_section[NAMES[s]],
          "midpoint:", section_roots[s])

print("\nDONE compose.")
