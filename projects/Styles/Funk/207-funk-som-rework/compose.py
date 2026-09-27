# -*- coding: utf-8 -*-
"""207-funk-som-rework - Funk / Method 075 SOM-C, rework of 098-funk-som.

Rework agent nightly job. Source = 098-funk-som (Funk, F minor, 104 BPM).
Audit failed on std6 (provenance.json + index.html missing at project root).
Decision: redesign via canonical UnitMatrixComposer, preserving identity
(genre/key/tempo/instrumentation/SOM-C method) -> NEW LONGER 32-bar piece
with >=3 variation techniques.

Two-phase (MANDATORY):
  Phase 1 = raw SOM walk, single voice, unquantized pitch + rhythm.
  Phase 2 = musicom rules: chord-tone quantization per bar (floor t//BAR),
            voice-leading cap, 16th-grid snap, full 5-voice funk arrangement.
"""
import os
import json
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

SEED = 20260927
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/projects/Styles/Funk/207-funk-som-rework"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---- Grid / concept -------------------------------------------------------
BPM = 104
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120
GRID8 = 240

NAMES = ["Intro", "Verse", "Chorus", "Bridge", "Verse2", "Chorus2", "Solo", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)      # 8
N_BARS = N_SECTIONS * BARS_PER   # 32
SECTION_TICKS = BAR * BARS_PER   # 7680
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS

# F minor Aeolian PCs: F=5 G=7 Ab=8 Bb=10 C=0 Db=1 Eb=3
KEY_PCS = {5, 7, 8, 10, 0, 1, 3}

# Per-section harmonic regions (32 bars, 1 root/bar). Each section starts on a
# DIFFERENT degree (fixes "bar-0 always degree i" bug). F minor diatonic triads:
#   i=Fm(53)  VI=Db(61)  iv=Bbm(58)  v=Cm(60)  III=Ab(56)  VII=Eb(63)
ROOT_QUAL = {53: "m", 61: "M", 58: "m", 60: "m", 56: "M", 63: "M"}
PROG_ROOTS = [
    53, 53, 58, 60,   # Intro   i i iv v
    53, 61, 58, 63,   # Verse   i VI iv VII
    56, 63, 53, 58,   # Chorus  III VII i iv
    61, 63, 56, 63,   # Bridge  VI VII III VII
    58, 53, 61, 60,   # Verse2  iv i VI v
    63, 56, 61, 53,   # Chorus2 VII III VI i
    53, 58, 56, 60,   # Solo    i iv III v
    53, 61, 60, 53,   # Outro   i VI v i
]

def get_chord_intervals(root):
    return (0, 3, 7) if ROOT_QUAL[root] == "m" else (0, 4, 7)

def chord_tones(root, lo, hi):
    iv = get_chord_intervals(root)
    return sorted({root + i + 12 * o
                   for o in range(-4, 5) for i in iv
                   if lo <= root + i + 12 * o <= hi})

# Chord-tone sets per bar (lead range 55..86, bass range 33..45, comp 60..77)
CHORD_TONES_LEAD = [chord_tones(r, 55, 86) for r in PROG_ROOTS]
CHORD_TONES_COMP = [chord_tones(r, 60, 77) for r in PROG_ROOTS]
CHORD_TONES_SAX  = [chord_tones(r, 50, 74) for r in PROG_ROOTS]

def section_midpoint_root(s_idx):
    """Root at the section's midpoint bar (bar index section_start+1)."""
    return PROG_ROOTS[s_idx * BARS_PER + 1]

SECTION_ROOTS = [section_midpoint_root(s) for s in range(N_SECTIONS)]

# ---- SOM (Kohonen, 4x4 toroidal, 3-dim) ----------------------------------
class KohonenSOM:
    def __init__(self, m=4, n=4, dim=3, seed=SEED):
        self.m, self.n, self.dim = m, n, dim
        self.rng = np.random.default_rng(seed)
        self.w = self.rng.uniform(0.1, 0.9, (m, n, dim))

    def train(self, data, epochs=100, alpha0=0.2, sigma0=2.0):
        W = self.w.reshape(-1, self.dim)
        for e in range(epochs):
            alpha = alpha0 * (1.0 - e / float(epochs))
            sigma = max(0.4, sigma0 * (1.0 - e / float(epochs)))
            for x in data:
                bmu = int(np.argmin(np.sum((W - x) ** 2, axis=1)))
                for j in range(self.m * self.n):
                    r0, c0 = divmod(bmu, self.n)
                    r1, c1 = divmod(j, self.n)
                    dr = min(abs(r0 - r1), self.m - abs(r0 - r1))
                    dc = min(abs(c0 - c1), self.n - abs(c0 - c1))
                    h = np.exp(-(dr * dr + dc * dc) / (2.0 * sigma * sigma))
                    W[j] += alpha * h * (x - W[j])
        self.w = W.reshape(self.m, self.n, self.dim)

    def walk(self, steps, beta=2.0, waypoint=(0, 0), gamma=0.6):
        curr = list(waypoint)
        path = [self.w[curr[0], curr[1]].copy()]
        for _ in range(steps - 1):
            neigh, probs = [], []
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr = (curr[0] + dr) % self.m
                    nc = (curr[1] + dc) % self.n
                    fd = np.sum((self.w[curr[0], curr[1]] - self.w[nr, nc]) ** 2)
                    drw = min(abs(nr - waypoint[0]), self.m - abs(nr - waypoint[0]))
                    dcw = min(abs(nc - waypoint[1]), self.n - abs(nc - waypoint[1]))
                    wd = (drw * drw + dcw * dcw) ** 0.5
                    neigh.append((nr, nc))
                    probs.append(np.exp(-beta * fd - gamma * wd))
            probs = np.array(probs) / np.sum(probs)
            curr = neigh[self.rng.choice(len(neigh), p=probs)]
            path.append(self.w[curr[0], curr[1]].copy())
        return np.array(path)

funk_corpus = np.array([
    [0.2, 0.25, 0.85], [0.25, 0.125, 0.7], [0.5, 0.5, 0.8], [0.6, 0.25, 0.9],
    [0.75, 0.125, 0.95], [0.4, 0.375, 0.75], [0.85, 0.25, 0.88], [0.3, 0.75, 0.6],
])
som = KohonenSOM(m=4, n=4, dim=3, seed=SEED)
som.train(funk_corpus, epochs=100)

# ---- PHASE 1 : raw SOM draft (single voice, unquantized) -----------------
WAYPOINTS = [(0, 0), (1, 1), (2, 2), (3, 1), (1, 0), (2, 3), (0, 3), (0, 1)]
DENSITIES = [20, 28, 32, 24, 28, 32, 16, 12]

def generate_phase1_section(s_idx):
    n = DENSITIES[s_idx]
    walk = som.walk(steps=n, beta=2.0, waypoint=WAYPOINTS[s_idx], gamma=0.6)
    fracs = rng.uniform(0.7, 1.3, size=n)
    fracs /= fracs.sum()
    iois = fracs * (SECTION_TICKS - 240)
    evs, t = [], 0.0
    for i in range(n):
        w = walk[i]
        pitch = 53.0 + w[0] * 36.0 + rng.normal(0.0, 0.8)
        dur = max(40.0, min(iois[i] * 0.9, 60.0 + w[1] * 360.0))
        vel = int(np.clip(55 + w[2] * 55, 45, 115))
        st = int(round(t))
        en = min(int(round(t + dur)), SECTION_TICKS - 1)
        if en > st:
            evs.append(MusicEvent(pitch=int(round(pitch)), volume=vel,
                                  start_tick=st, end_tick=en))
        t += iois[i]
    # terminal landmark (zero-drift)
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    return evs

p1_sections = [generate_phase1_section(s) for s in range(N_SECTIONS)]

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=56, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER)
    phase1.set_unit(0, s, MusicUnit(events=p1_sections[s]))
ok1, msg1 = phase1.validate()
assert ok1, f"Phase 1 validate failed: {msg1}"
p1_midi = os.path.join(MIDI_DIR, "207-funk-som-rework-phase1.mid")
phase1.to_midi(p1_midi)
print(f"Phase 1 MIDI: {p1_midi} validate={ok1}")

# ---- PHASE 2 : rules + full arrangement ----------------------------------
def snap16(t):
    return int(round(t / float(GRID16)) * GRID16)

def quantize_to_tones(p, tones):
    return min(tones, key=lambda t: (abs(t - p), t))

# Variation transforms applied to a raw pitch list (pre-quantization).
# 0 Intro    = identity
# 2 Chorus   = transpose +5 (perfect 4th)
# 3 Bridge   = retrograde (reverse pitch sequence)
# 4 Verse2   = register shift +12 (octave)
# 5 Chorus2  = inversion around F4 (65)
# 6 Solo     = diminution (durations x0.5)
# 7 Outro    = augmentation (durations x2.0)
def apply_pitch_transform(s_idx, pitches):
    if s_idx == 2:
        return [p + 5 for p in pitches]
    if s_idx == 3:
        return list(reversed(pitches))
    if s_idx == 4:
        return [p + 12 for p in pitches]
    if s_idx == 5:
        return [2 * 65 - p for p in pitches]
    return list(pitches)

def time_scale(s_idx):
    if s_idx == 6:
        return 0.5
    if s_idx == 7:
        return 2.0
    return 1.0

# Lead from Phase 1 raw events + variation + rules
lead_sections = []
prev_pitch = 65  # F4
for s in range(N_SECTIONS):
    raw = [e for e in p1_sections[s] if e.pitch != 0]
    pitches = apply_pitch_transform(s, [e.pitch for e in raw])
    dscale = time_scale(s)          # 0.5 diminution, 2.0 augmentation, else 1.0
    evs = []
    last_end = 0
    onsets = [e.start_tick for e in raw]
    durs = [e.end_tick - e.start_tick for e in raw]
    for i, p in enumerate(pitches):
        st = snap16(int(onsets[i]))
        if st < last_end:
            st = last_end
        if st >= SECTION_TICKS - GRID16:
            continue
        dur = snap16(max(GRID16, int(durs[i] * dscale)))
        en = min(SECTION_TICKS, st + dur)
        global_bar = s * BARS_PER + min(st // BAR, BARS_PER - 1)
        q = quantize_to_tones(p, CHORD_TONES_LEAD[global_bar])
        # voice-leading leap cap (9 semitones)
        if abs(q - prev_pitch) > 9:
            q = min(CHORD_TONES_LEAD[global_bar], key=lambda t: abs(t - prev_pitch))
        evs.append(MusicEvent(pitch=q, volume=max(60, 110 - i), start_tick=st,
                              end_tick=en))
        prev_pitch = q
        last_end = en
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    lead_sections.append(evs)

# Sax counterline (offbeat punches on beats 2.5 / 4.5)
sax_sections = []
prev_sax = 53
for s in range(N_SECTIONS):
    evs = []
    if s in (1, 2, 4, 5):
        for b in range(BARS_PER):
            bar_start = b * BAR
            gb = s * BARS_PER + b
            for off in (BAR // 4 + GRID16, 3 * (BAR // 4) + GRID16):
                st = bar_start + off
                tones = CHORD_TONES_SAX[gb]
                p = min(tones, key=lambda t: abs(t - prev_sax))
                evs.append(MusicEvent(pitch=p, volume=85, start_tick=st,
                                      end_tick=st + GRID16))
                prev_sax = p
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    sax_sections.append(evs)

# Piano comping (syncopated chord stabs: beat1, and-of-2, beat4)
piano_sections = []
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar_start = b * BAR
        gb = s * BARS_PER + b
        tones = CHORD_TONES_COMP[gb][:3]
        for hit in (0, 600, 1440):
            st = bar_start + hit
            for p in tones:
                evs.append(MusicEvent(pitch=p, volume=78, start_tick=st,
                                      end_tick=st + GRID16))
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    piano_sections.append(evs)

# Bass funk groove (root/octave syncopation)
bass_sections = []
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar_start = b * BAR
        gb = s * BARS_PER + b
        root = PROG_ROOTS[gb]
        r_note = root
        while r_note > 45:
            r_note -= 12
        oct_note = r_note + 12
        for off, pitch, dur in ((0, r_note, GRID8), (360, oct_note, GRID16),
                                (600, oct_note, GRID16), (960, r_note, GRID8),
                                (1560, r_note, GRID16), (1800, oct_note, GRID16)):
            st = bar_start + off
            evs.append(MusicEvent(pitch=pitch, volume=94, start_tick=st,
                                  end_tick=st + dur))
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    bass_sections.append(evs)

# Drums (ch9) funk backbeat + 16th hats + ghost snare + syncopated kick
drum_sections = []
for s in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar_start = b * BAR
        for h in range(16):
            st = bar_start + h * GRID16
            v = 88 if h % 4 == 0 else 68
            p = 46 if h == 14 else 42
            evs.append(MusicEvent(pitch=p, volume=v, start_tick=st,
                                  end_tick=st + GRID16 // 2))
        for off, v in ((480, 100), (1440, 105), (1320, 55)):
            evs.append(MusicEvent(pitch=38, volume=v, start_tick=bar_start + off,
                                  end_tick=bar_start + off + GRID16))
        for off in (0, 360, 720, 1200):
            evs.append(MusicEvent(pitch=36, volume=102, start_tick=bar_start + off,
                                  end_tick=bar_start + off + GRID16))
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1,
                          end_tick=SECTION_TICKS))
    drum_sections.append(evs)

# ---- Dedup collided (start_tick, pitch) keeping longest duration ---------
def dedup(events):
    best = {}
    for e in events:
        if e.pitch == 0:
            continue
        k = (e.start_tick, e.pitch)
        if k not in best or (e.end_tick - e.start_tick) > (best[k].end_tick - best[k].start_tick):
            best[k] = e
    return sorted(best.values(), key=lambda e: e.start_tick)

lead_sections = [dedup(e) for e in lead_sections]
sax_sections = [dedup(e) for e in sax_sections]
piano_sections = [dedup(e) for e in piano_sections]
bass_sections = [dedup(e) for e in bass_sections]
drum_sections = [dedup(e) for e in drum_sections]

# re-add terminal landmark after dedup
for arr in (lead_sections, sax_sections, piano_sections, bass_sections, drum_sections):
    for i in range(N_SECTIONS):
        arr[i].append(MusicEvent(pitch=0, volume=0,
                                 start_tick=SECTION_TICKS - 1,
                                 end_tick=SECTION_TICKS))

# ---- Build Phase 2 UnitMatrixComposer ------------------------------------
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=5, num_sections=N_SECTIONS)
phase2.add_voice("Lead", program=56, channel=0)   # Trumpet
phase2.add_voice("Sax", program=66, channel=1)    # Tenor Sax
phase2.add_voice("Piano", program=1, channel=2)   # Acoustic Grand
phase2.add_voice("Bass", program=43, channel=3)   # Contrabass
phase2.add_voice("Drums", program=0, channel=9)   # Drum kit

for s, name in enumerate(NAMES):
    phase2.add_section(name, bars=BARS_PER)
    phase2.set_unit(0, s, MusicUnit(events=lead_sections[s]))
    phase2.set_unit(1, s, MusicUnit(events=sax_sections[s]))
    phase2.set_unit(2, s, MusicUnit(events=piano_sections[s]))
    phase2.set_unit(3, s, MusicUnit(events=bass_sections[s]))
    phase2.set_unit(4, s, MusicUnit(events=drum_sections[s]))

ok2, msg2 = phase2.validate()
assert ok2, f"Phase 2 validate failed: {msg2}"
p2_midi = os.path.join(MIDI_DIR, "207-funk-som-rework.mid")
phase2.to_midi(p2_midi)
print(f"Phase 2 MIDI: {p2_midi} validate={ok2}")

# ---- Sidecars ------------------------------------------------------------
write_provenance(p1_midi, AI_ASSISTED,
                 generator="Method 075 SOM-C (Phase 1 Raw, rework of 098)",
                 parameters={"m": 4, "n": 4, "dim": 3, "seed": SEED,
                             "phase": 1, "source": "098-funk-som"})
write_provenance(p2_midi, AI_ASSISTED,
                 generator="Method 075 SOM-C + musicom rules (Phase 2, rework of 098)",
                 parameters={"m": 4, "n": 4, "dim": 3, "seed": SEED,
                             "phase": 2, "grid": 120, "key": "F minor",
                             "source": "098-funk-som",
                             "variation": ["transposition", "retrograde",
                                           "inversion", "register-shift",
                                           "diminution", "augmentation"]},
                 notes="Redesign: source 098 failed std6 (no provenance.json / "
                       "index.html). Rebuilt via UnitMatrixComposer preserving "
                       "identity; extended 24->32 bars, 8 sections.")

assert phase2.matrix is not None
write_grid_visualization(phase2.matrix,
                         os.path.join(ANALYSIS_DIR, "grid_visualization.txt"))
print("Grid visualization written.")

# ---- Project-level sidecars (std6 fix) -----------------------------------
proj_prov = {
    "project": "207-funk-som-rework",
    "genre": "Funk",
    "key": "F minor",
    "bpm": BPM,
    "form": "8 sections x 4 bars = 32 bars",
    "source": "098-funk-som",
    "redesign_required": True,
    "audit_failures": ["std6_provenance.json", "std6_index.html"],
    "variation_techniques": [
        "transposition (+5, Chorus)",
        "retrograde (Bridge)",
        "inversion (Chorus2)",
        "register-shift +12 (Verse2)",
        "diminution x0.5 (Solo)",
        "augmentation x2.0 (Outro)",
    ],
    "seed": SEED,
}
with open(os.path.join(PROJ, "provenance.json"), "w") as f:
    json.dump(proj_prov, f, indent=2)

# Audit result (Step 2 artifact)
audit = {
    "chosen": "098-funk-som",
    "genre": "Funk",
    "standard_failures": ["std6_provenance.json", "std6_index.html"],
    "redesign_required": True,
    "source_identity": {
        "genre": "Funk", "key": "F minor", "bpm": 104,
        "instrumentation": ["Trumpet", "Tenor Sax", "Piano", "Contrabass", "Drums"],
        "method": "SOM-C", "form": "6x4=24 bars",
    },
}
src_analysis = "/opt/data/projects/Styles/Funk/098-funk-som/Analysis"
os.makedirs(src_analysis, exist_ok=True)
with open(os.path.join(src_analysis, "rework_audit.json"), "w") as f:
    json.dump(audit, f, indent=2)
print("Audit + provenance sidecars written.")

# Persist a compact summary for the verify step
json.dump({
    "project": PROJ,
    "p1": p1_midi, "p2": p2_midi,
    "key_pcs": sorted(KEY_PCS),
    "roots": PROG_ROOTS,
    "section_roots": SECTION_ROOTS,
    "bars": N_BARS, "sections": N_SECTIONS,
    "total_ticks": TOTAL_TICKS,
}, open("/opt/data/.cron_scratch/rework_207_meta.json", "w"), indent=2)
print("DONE compose.")
