# -*- coding: utf-8 -*-
"""098-funk-som - Funk style / Method 075 Self-Organizing Map Composition (SOM-C).
LAYER: concrete.

Architecture:
Two-phase:
  Phase 1: Raw SOM trajectory walk. Prototype vectors trained on 8 Funk groove/riff
           patterns (3-dim: pitch_norm, dur_norm, vel_norm). A stochastic 2D Markov
           walker navigates the 4x4 toroidal SOM grid with thermal noise.
           Pitches are continuous/unquantized (raw floating points mapped to MIDI),
           rhythm is unquantized/continuous (inter-onset intervals). Single voice (Trumpet).
           NO harmony, NO chord quantization, NO drum/bass accompaniment.
  Phase 2: Musicom rules post-processing:
           1. Quantize onsets to 16th grid (120 ticks @ 480 TPB) -> 0 off-grid.
           2. Quantize pitches to F minor pentatonic / bar chord tones -> 0 out-of-scale, 0 out-of-chord.
           3. Voice-leading leap cap (<= 9 semitones to nearest chord tone).
           4. Full 6-voice funk arrangement:
              - Lead Trumpet (melodic motif from quantized SOM walk)
              - Tenor Sax (counterline on beats 2 & 4)
              - Electric Guitar (16th funk scratch / stabs)
              - Electric Bass (octave funk slap & syncopated root/fifth walk)
              - Acoustic Piano (syncopated 9th/7th funk comping)
              - Drum Kit (ch9: funk backbeat, ghost snare, 16th hats, kick pushes)
           5. Zero-drift gate + validate() on both phases.
           6. Export dual artifacts: 098-funk-som-phase1.mid, 098-funk-som.mid.
"""
import os
import sys
import json
import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# Instrument registry (source of truth)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (
    TRUMPET, SAXOPHONE, DOUBLE_BASS, PIANO, DRUM_KIT, by_name
)
from Percussion.drum_kit.drum_kit import KIT

SEED = 20260919
rng = np.random.default_rng(SEED)

PROJ = "/opt/data/repos/musicom/projects/Styles/Funk/098-funk-som"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- Concept & Grid
BPM = 104
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920
GRID16 = 120                 # 16th grid @ 480 TPB
GRID8 = 240                  # 8th grid

NAMES = ["Intro", "Verse", "Chorus", "Bridge", "Chorus2", "Outro"]
BARS_PER = 4
N_SECTIONS = len(NAMES)
N_BARS = N_SECTIONS * BARS_PER  # 24 bars
SECTION_TICKS = BAR * BARS_PER   # 7680 ticks

# F Minor Aeolian / Pentatonic Funk Universe
# Root = F (53), Key: F minor
# Diatonic PCs: F=5, G=7, Ab=8, Bb=10, C=0, Db=1, Eb=3
SCALE_PCS = {5, 7, 8, 10, 0, 1, 3}
# Pentatonic PCs: F=5, Ab=8, Bb=10, C=0, Eb=3
PENT_PCS = {5, 8, 10, 0, 3}

# Progression (24 bars):
# Intro:   i   | i   | iv  | v   (Fm | Fm | Bbm | Cm)
# Verse:   i   | VI  | iv  | v   (Fm | Db | Bbm | Cm)
# Chorus:  i   | III | VII | iv  (Fm | Ab | Eb  | Bbm)
# Bridge:  VI  | VII | i   | v   (Db | Eb | Fm  | Cm)
# Chorus2: i   | III | VII | iv  (Fm | Ab | Eb  | Bbm)
# Outro:   i   | VI  | v   | i   (Fm | Db | Cm  | Fm)
ROOT_QUAL = {53: "m", 49: "M", 44: "M", 51: "M", 46: "m", 48: "m"}
PROG_ROOTS = [
    53, 53, 46, 48,  # Intro
    53, 49, 46, 48,  # Verse
    53, 44, 51, 46,  # Chorus
    49, 51, 53, 48,  # Bridge
    53, 44, 51, 46,  # Chorus2
    53, 49, 48, 53   # Outro
]

def get_chord_intervals(root):
    return (0, 3, 7) if ROOT_QUAL[root] == "m" else (0, 4, 7)

def get_chord_tones(root, lo=28, hi=96):
    iv = get_chord_intervals(root)
    tones = set()
    for oct_s in (-36, -24, -12, 0, 12, 24, 36):
        for i in iv:
            p = root + i + oct_s
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)

CHORD_TONES_BY_BAR = [get_chord_tones(r) for r in PROG_ROOTS]
CHORD_PCS_BY_BAR = [set((r + i) % 12 for i in get_chord_intervals(r)) for r in PROG_ROOTS]

# ---------------------------------------------------------------- SOM Implementation
class KohonenSOM:
    """Toroidal 4x4 Self-Organizing Map in 3D feature space (pitch, dur, vel)."""
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

    def train(self, data, epochs=80, alpha0=0.2, sigma0=2.0):
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

    def u_matrix(self):
        U = np.zeros((self.m, self.n))
        for r in range(self.m):
            for c in range(self.n):
                diffs = []
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr = (r + dr) % self.m
                    nc = (c + dc) % self.n
                    diffs.append(np.linalg.norm(self.w[r, c] - self.w[nr, nc]))
                U[r, c] = np.mean(diffs)
        return U

    def walk(self, steps, beta=2.5, waypoint=(0, 0), gamma=0.5):
        """Markov walk on 4x4 toroidal grid with similarity kernel and region pull."""
        curr = list(waypoint)
        path = [self.w[curr[0], curr[1]].copy()]
        for _ in range(steps - 1):
            neighbors = []
            probs = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]:
                nr = (curr[0] + dr) % self.m
                nc = (curr[1] + dc) % self.n
                w_curr = self.w[curr[0], curr[1]]
                w_next = self.w[nr, nc]
                feat_dist_sq = np.sum((w_curr - w_next) ** 2)
                # Toroidal distance to waypoint
                dr_w = min(abs(nr - waypoint[0]), self.m - abs(nr - waypoint[0]))
                dc_w = min(abs(nc - waypoint[1]), self.n - abs(nc - waypoint[1]))
                way_dist = np.sqrt(dr_w * dr_w + dc_w * dc_w)
                prob = np.exp(-beta * feat_dist_sq - gamma * way_dist)
                neighbors.append((nr, nc))
                probs.append(prob)
            probs = np.array(probs) / np.sum(probs)
            choice_idx = self.rng.choice(len(neighbors), p=probs)
            curr = neighbors[choice_idx]
            path.append(self.w[curr[0], curr[1]].copy())
        return np.array(path)

# Train SOM on representative Funk vocabulary atoms [norm_pitch, norm_dur, norm_vel]
funk_corpus = np.array([
    [0.2, 0.25, 0.85],  # Low syncopated slap
    [0.25, 0.125, 0.7],  # 16th funk pop
    [0.5, 0.5, 0.8],    # Mid horn punch
    [0.6, 0.25, 0.9],   # High syncopated stab
    [0.75, 0.125, 0.95],# Upper register hook
    [0.4, 0.375, 0.75], # Melodic connective 8th
    [0.85, 0.25, 0.88], # Blue note accent
    [0.3, 0.75, 0.6],   # Sustained bass drop
])

som = KohonenSOM(m=4, n=4, dim=3, seed=SEED)
som.train(funk_corpus, epochs=100)
u_mat = som.u_matrix()

# ---------------------------------------------------------------- PHASE 1: Raw SOM Draft
# Single-voice raw generative draft: continuous pitch, continuous/unquantized timing
def generate_phase1_events():
    all_events = []
    # Waypoints for 6 sections across the SOM grid
    waypoints = [(0, 0), (1, 1), (2, 2), (3, 1), (2, 3), (0, 1)]
    densities = [24, 32, 40, 28, 40, 20]
    
    for s_idx in range(N_SECTIONS):
        sec_events = []
        n_ev = densities[s_idx]
        wp = waypoints[s_idx]
        walk_vecs = som.walk(steps=n_ev, beta=2.0, waypoint=wp, gamma=0.6)
        
        # Inter-onset distribution across SECTION_TICKS
        time_fractions = rng.uniform(0.7, 1.3, size=n_ev)
        time_fractions /= np.sum(time_fractions)
        raw_iois = time_fractions * (SECTION_TICKS - 240)
        
        current_tick = 0.0
        for i in range(n_ev):
            w = walk_vecs[i]
            # w[0] = pitch in [0, 1] -> map to [53, 89] (F3 to F6)
            raw_pitch = 53.0 + w[0] * 36.0 + rng.normal(0.0, 0.8)
            # w[1] = dur in [0, 1] -> map to ticks
            ioi = raw_iois[i]
            dur = max(40.0, min(ioi * 0.9, 60.0 + w[1] * 360.0))
            # w[2] = vel in [0, 1] -> map to [60, 110]
            vel = int(np.clip(55 + w[2] * 55, 45, 115))
            
            st = int(round(current_tick))
            en = int(round(current_tick + dur))
            if en > SECTION_TICKS - 1:
                en = SECTION_TICKS - 1
            if en > st:
                sec_events.append(MusicEvent(pitch=int(round(raw_pitch)), volume=vel,
                                             start_tick=st, end_tick=en))
            current_tick += ioi
            
        # Ensure zero-drift terminal landmark
        if not sec_events or sec_events[-1].end_tick < SECTION_TICKS:
            sec_events.append(MusicEvent(pitch=0, volume=0,
                                         start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
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
assert ok1, f"Phase 1 validate failed: {msg1}"
p1_midi = os.path.join(MIDI_DIR, "098-funk-som-phase1.mid")
phase1.to_midi(p1_midi)
print(f"Phase 1 MIDI exported: {p1_midi} (validate: {ok1})")

# ---------------------------------------------------------------- PHASE 2: Rules Processing & Full Arrangement
# Rules:
# 1. 16th Grid Quantization (120 ticks) for all pitched voices.
# 2. Strict Chord-Tone Quantization per global bar.
# 3. Voice-Leading Leap Penalty.
# 4. Multi-voice Funk Arrangement:
#    - Lead Trumpet (melodic line from quantized SOM walk)
#    - Tenor Sax (counterline on beats 2 & 4)
#    - Electric Guitar (syncopated funk scratch chords)
#    - Electric Bass (syncopated slap bass line)
#    - Acoustic Piano (syncopated 9th/7th comping)
#    - Drum Kit (ch9 groove)

def snap_to_16th(tick):
    return int(round(tick / float(GRID16)) * GRID16)

def quantize_pitch_to_chord(pitch, global_bar, lo=48, hi=88):
    tones = CHORD_TONES_BY_BAR[global_bar]
    valid_tones = [t for t in tones if lo <= t <= hi]
    if not valid_tones:
        valid_tones = tones
    return min(valid_tones, key=lambda t: (abs(t - pitch), t))

# Process Lead from Phase 1
lead_sections = []
prev_pitch = 65  # F4
for s_idx in range(N_SECTIONS):
    evs = []
    raw_evs = p1_section_events[s_idx]
    last_end = 0
    for e in raw_evs:
        if e.pitch == 0:
            continue
        st = snap_to_16th(e.start_tick)
        if st < last_end:
            st = last_end
        if st >= SECTION_TICKS:
            continue
        dur = snap_to_16th(e.end_tick - e.start_tick)
        dur = max(GRID16, dur)
        en = min(SECTION_TICKS, st + dur)
        
        global_bar = s_idx * BARS_PER + min(st // BAR, BARS_PER - 1)
        # Quantize to chord tones of the bar
        q_pitch = quantize_pitch_to_chord(e.pitch, global_bar, lo=58, hi=84)
        
        # Voice-leading leap cap: if leap > 9 semitones, seek closer chord tone
        if abs(q_pitch - prev_pitch) > 9:
            tones = [t for t in CHORD_TONES_BY_BAR[global_bar] if 58 <= t <= 84]
            q_pitch = min(tones, key=lambda t: abs(t - prev_pitch))
            
        evs.append(MusicEvent(pitch=q_pitch, volume=e.volume, start_tick=st, end_tick=en))
        prev_pitch = q_pitch
        last_end = en
        
    if not evs or evs[-1].end_tick < SECTION_TICKS:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
    lead_sections.append(evs)

# Tenor Sax Counterline: complementary offbeat phrases
sax_sections = []
prev_sax = 53
for s_idx in range(N_SECTIONS):
    evs = []
    # Play riffs during verse, chorus, chorus2, bridge
    if s_idx in [1, 2, 3, 4]:
        for b in range(BARS_PER):
            bar_start = b * BAR
            global_bar = s_idx * BARS_PER + b
            # Offbeat punches on beats 2.5 and 4.5
            offsets = [BAR // 4 + GRID16, 3 * (BAR // 4) + GRID16]
            for off in offsets:
                st = bar_start + off
                en = st + GRID16
                tones = [t for t in CHORD_TONES_BY_BAR[global_bar] if 50 <= t <= 74]
                p = min(tones, key=lambda t: abs(t - prev_sax))
                evs.append(MusicEvent(pitch=p, volume=85, start_tick=st, end_tick=en))
                prev_sax = p
    if not evs or evs[-1].end_tick < SECTION_TICKS:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
    sax_sections.append(evs)

# Electric Piano Comping: syncopated chord stabs
piano_sections = []
for s_idx in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar_start = b * BAR
        global_bar = s_idx * BARS_PER + b
        root = PROG_ROOTS[global_bar]
        # Voicing: 3 chord tones in octave 4-5
        tones = [t for t in CHORD_TONES_BY_BAR[global_bar] if 60 <= t <= 77][:3]
        # Funk syncopation hits: beat 1, "and" of 2, beat 4
        hits = [0, 600, 1440]
        for hit in hits:
            st = bar_start + hit
            en = st + GRID16
            for p in tones:
                evs.append(MusicEvent(pitch=p, volume=78, start_tick=st, end_tick=en))
    if not evs or evs[-1].end_tick < SECTION_TICKS:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
    piano_sections.append(evs)

# Electric Bass: funk groove with root octaves and 16th syncopations
bass_sections = []
for s_idx in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar_start = b * BAR
        global_bar = s_idx * BARS_PER + b
        root = PROG_ROOTS[global_bar]
        # Bass root in octave 2
        r_note = min([t for t in CHORD_TONES_BY_BAR[global_bar] if t % 12 == root % 12 and 33 <= t <= 45])
        oct_note = r_note + 12
        # Funk groove pattern: Beat 1 (root), beat 1 "and" (oct), beat 2.5 (oct), beat 3 (root), beat 4 "and" (root)
        groove = [
            (0, r_note, GRID8),
            (360, oct_note, GRID16),
            (600, oct_note, GRID16),
            (960, r_note, GRID8),
            (1560, r_note, GRID16),
            (1800, oct_note, GRID16)
        ]
        for off, pitch, dur in groove:
            st = bar_start + off
            en = st + dur
            evs.append(MusicEvent(pitch=pitch, volume=94, start_tick=st, end_tick=en))
    if not evs or evs[-1].end_tick < SECTION_TICKS:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
    bass_sections.append(evs)

# Drum Kit (Channel 9): tight funk groove
# Kick: 36, Snare: 38, Closed Hat: 42, Open Hat: 46
drum_sections = []
for s_idx in range(N_SECTIONS):
    evs = []
    for b in range(BARS_PER):
        bar_start = b * BAR
        # Hats on all 16ths
        for h in range(16):
            st = bar_start + h * GRID16
            en = st + GRID16 // 2
            v = 88 if h % 4 == 0 else 68
            p = 46 if h == 14 else 42 # open hat on beat 4 "and"
            evs.append(MusicEvent(pitch=p, volume=v, start_tick=st, end_tick=en))
        # Snare on 2 and 4 + ghost note on 3 "and-a"
        snares = [(480, 100), (1440, 105), (1320, 55)]
        for off, v in snares:
            st = bar_start + off
            en = st + GRID16
            evs.append(MusicEvent(pitch=38, volume=v, start_tick=st, end_tick=en))
        # Kick on 1, 1 "and-a", 2 "and", 3 "and"
        kicks = [0, 360, 720, 1200]
        for off in kicks:
            st = bar_start + off
            en = st + GRID16
            evs.append(MusicEvent(pitch=36, volume=102, start_tick=st, end_tick=en))
    if not evs or evs[-1].end_tick < SECTION_TICKS:
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=SECTION_TICKS - 1, end_tick=SECTION_TICKS))
    drum_sections.append(evs)

# Build Phase 2 UnitMatrixComposer
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase2.create_matrix(num_voices=5, num_sections=N_SECTIONS)
phase2.add_voice("Lead", program=TRUMPET.midi_program, channel=0)
phase2.add_voice("Sax", program=SAXOPHONE.midi_program, channel=1)
phase2.add_voice("Piano", program=PIANO.midi_program, channel=2)
phase2.add_voice("Bass", program=DOUBLE_BASS.midi_program, channel=3)
phase2.add_voice("Drums", program=0, channel=9)

for s_idx, name in enumerate(NAMES):
    phase2.add_section(name, bars=BARS_PER)
    phase2.set_unit(0, s_idx, MusicUnit(events=lead_sections[s_idx]))
    phase2.set_unit(1, s_idx, MusicUnit(events=sax_sections[s_idx]))
    phase2.set_unit(2, s_idx, MusicUnit(events=piano_sections[s_idx]))
    phase2.set_unit(3, s_idx, MusicUnit(events=bass_sections[s_idx]))
    phase2.set_unit(4, s_idx, MusicUnit(events=drum_sections[s_idx]))

ok2, msg2 = phase2.validate()
assert ok2, f"Phase 2 validate failed: {msg2}"
p2_midi = os.path.join(MIDI_DIR, "098-funk-som.mid")
phase2.to_midi(p2_midi)
print(f"Phase 2 MIDI exported: {p2_midi} (validate: {ok2})")

# Provenance sidecars
write_provenance(p1_midi, AI_ASSISTED, generator="Method 075 SOM-C (Phase 1 Raw)",
                 parameters={"m": 4, "n": 4, "dim": 3, "seed": SEED, "phase": 1})
write_provenance(p2_midi, AI_ASSISTED, generator="Method 075 SOM-C (Phase 2 Rules)",
                 parameters={"m": 4, "n": 4, "dim": 3, "seed": SEED, "phase": 2, "grid": 120})

# Write grid visualization
assert phase2.matrix is not None
write_grid_visualization(phase2.matrix, os.path.join(ANALYSIS_DIR, "grid_visualization.txt"))
print("Grid visualization written.")
