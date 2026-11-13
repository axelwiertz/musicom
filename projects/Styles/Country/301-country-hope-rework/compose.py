# -*- coding: utf-8 -*-
"""301-country-hope-rework -- Country rework of 001-country-hope-loop.

Nightly rework job. Source 001-country-hope-loop failed all 6 standards
(hand-rolled mido, single merged voice, no phase1, no provenance/index.html).
REDESIGN: rebuild from scratch through the canonical UnitMatrixComposer engine,
preserving only the musical identity (Country, G major I-IV-V backbone, 96 BPM,
boom-chick groove, hopeful rising G-B-D arpeggio motif, acoustic-guitar lead +
steel pad + piano + bass + drums).

Two-phase architecture:
  Phase 1 = raw "country contour walk" draft (arpeggiated-triad + neighbor-tone
            random walk, single voice, unquantized pitch + off-grid rhythm).
  Phase 2 = musicom rules post-process (blanket chord-tone quantization per bar,
            grid-lock to 16th, voice-leading cap, dedup) + full 5-voice Country
            texture, exported as dual versions (perfect + humanized).

Variation techniques (>=3 required; 8 applied):
  1. Augmentation  -- Intro + Outro (sparse, long notes, register drop)
  2. Baseline contour -- Verse (I-IV-I-V generative walk)
  3. Diminution + register shift up -- Chorus (denser 16th feel, center 79)
  4. Inversion (mirrored contour) + vi shade -- Verse2 (Em region)
  5. Retrograde (reversed contour) + counterline -- Bridge (ii-V-I)
  6. Density rise -- Chorus (full steel pad + piano comp + crash)
  7. Counterline -- Bridge (piano descending chord-tone line)
  8. Authentic cadence + augmentation -- Outro (V-I resolve, half-speed)

Engine only: structures + workflows.unitmatrix_composer + humanize + provenance
+ grid. mido used for READ-ONLY verification only.
"""
import os
import json

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer, create_empty_unit
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

SEED = 20261113
STYLE = "country"
KEY = "G"
KEY_LABEL = "G major (I-IV-V backbone; source labelled 'mixolydian' but realised D-major V)"
BPM = 96
SOURCE = "001-country-hope-loop"

PROJ = "/opt/data/projects/Styles/Country/301-country-hope-rework"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920 ticks
GRID = 120                   # 16th note
EIGHTH = 240

# G major: G A B C D E F# -> pitch classes {7,9,11,0,2,4,6}
SCALE_PCS = {7, 9, 11, 0, 2, 4, 6}
SCALE_NAME = "major"
SCALE_ROOT = 55              # G3 reference

# Country I-IV-V-vi-ii chords in G major (all diatonic).
CHORDS = {
    "G":  {"pcs": {7, 11, 2},  "bass": 43, "triad": [55, 59, 62], "quality": "major"},  # G B D
    "C":  {"pcs": {0, 4, 7},   "bass": 36, "triad": [48, 52, 55], "quality": "major"},  # C E G
    "D":  {"pcs": {2, 6, 9},   "bass": 38, "triad": [50, 54, 57], "quality": "major"},  # D F# A
    "Em": {"pcs": {4, 7, 11},  "bass": 40, "triad": [52, 55, 59], "quality": "minor"},  # E G B
    "Am": {"pcs": {9, 0, 4},   "bass": 45, "triad": [57, 60, 64], "quality": "minor"},  # A C E
}

# form: 6 sections, 20 bars (source was 8-bar loop -> N+3 sections, 2.5x longer)
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Bridge", "Outro"]
BARS = [2, 4, 4, 4, 4, 2]
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS)            # 20
SECTION_TICKS = [b * BAR for b in BARS]

# per-section chord rotation -> varied midpoint roots (no bar-0 tonic monotony)
SECTION_ROT = {
    0: ["G", "C"],              # Intro   I IV      -> midpoint C (IV major)
    1: ["G", "C", "G", "D"],    # Verse   I IV I V  -> midpoint C (IV major)
    2: ["C", "G", "D", "G"],    # Chorus  IV I V I  -> midpoint G (I major)
    3: ["Em", "Em", "C", "D"],  # Verse2  vi vi IV V -> midpoint Em (vi minor)
    4: ["C", "Am", "D", "G"],   # Bridge  IV ii V I -> midpoint Am (ii minor)
    5: ["D", "G"],              # Outro   V I       -> midpoint G (I major)
}

# voices: (voice name, GM program, channel)
VOICES = [
    ("Lead Guitar", 25, 0),   # GM 25 acoustic steel (signature timbre)
    ("Steel Pad",   26, 1),   # GM 26 electric jazz (sustained pad)
    ("Piano",        0, 2),   # GM 0 acoustic grand (comp + counterline)
    ("Bass",        33, 3),   # GM 33 electric finger bass
    ("Drums",        0, 9),   # channel 9 percussion
]
N_V = len(VOICES)
vnames = [v[0] for v in VOICES]

# Humanization DNA per voice (timing_ms, velocity_sigma, layback_ms, duration_sigma).
# None -> style profile wins (per instrument-registry convention).
HZ_INSTRUMENTS = {
    "Lead Guitar": (None, 6.0, None, 0.02),
    "Steel Pad":   (None, 5.0, None, 0.02),
    "Piano":       (None, 5.0, None, 0.02),
    "Bass":        (5.0, 4.0, 8.0, 0.01),
    "Drums":       (2.0, 4.0, 0.0, 0.008),
}

hz_seed = SEED


def bar_to_section(bar):
    cum = 0
    for s in range(N_SECTIONS):
        if bar < cum + BARS[s]:
            return s, bar - cum
        cum += BARS[s]
    return N_SECTIONS - 1, BARS[-1] - 1


def chord_key_for_bar(bar):
    s, lb = bar_to_section(bar)
    return SECTION_ROT[s][lb]


def chord_tones_for(ck):
    triad = CHORDS[ck]["triad"]
    return sorted({t + 12 * o for t in triad for o in range(-3, 5)})


# ----------------------------------------------------------------------
# Phase 1: raw country contour walk -> single-voice unquantized melody
# ----------------------------------------------------------------------
def country_walk(seed, dur_ticks, center, n_events, mode):
    """Arpeggiated-triad + neighbor-tone contour walk.

    Interval pool favours the hopeful rising 1-3-5 arpeggio (G-B-D, echoing
    the source's chord voicing) with stepwise passing/neighbor tones. Onsets +
    durations intentionally jittered (off-grid): phase-1 raw draft.
    """
    r = np.random.default_rng(seed)
    IV = [0, 4, 3, -3, -4, 5, -5, 2, -2, 7, -7, 12, -12]
    W = np.array([1, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1], dtype=float)
    W /= W.sum()
    ivs = [int(r.choice(IV, p=W)) for _ in range(n_events)]
    if mode == "invert":
        ivs = [-v for v in ivs]          # inversion (mirrored contour)
    elif mode == "retro":
        ivs = ivs[::-1]                  # retrograde (reversed contour)
    step = dur_ticks / n_events
    pitch = float(center)
    events = []
    for k, iv in enumerate(ivs):
        onset = int(k * step + r.normal(0.0, 60.0))
        onset = max(0, min(onset, dur_ticks - 60))
        if mode == "augment":
            dur = int(max(200.0, step * 1.8))       # augmentation (longer notes)
        elif mode == "diminish":
            dur = int(max(90.0, step * 0.55))       # diminution (denser)
        else:
            dur = int(max(120.0, step * r.uniform(0.6, 1.05)))
        dur = min(dur, dur_ticks - onset)
        pitch = float(np.clip(pitch + iv, center - 15.0, center + 15.0))
        velo = int(np.clip(70 + 25 * r.standard_normal(), 55, 110))
        events.append(MusicEvent(pitch=int(round(pitch)), volume=velo,
                                 start_tick=onset, end_tick=onset + dur))
    return events


# per-section generative params (variation techniques live here)
LEAD_PARAMS = {
    0: dict(center=67, n_events=8,  mode="augment"),   # Intro  augmentation (sparse)
    1: dict(center=72, n_events=16, mode="base"),      # Verse  baseline contour
    2: dict(center=79, n_events=24, mode="diminish"),  # Chorus register up + denser
    3: dict(center=74, n_events=16, mode="invert"),    # Verse2 inversion + vi shade
    4: dict(center=71, n_events=20, mode="retro"),     # Bridge retrograde
    5: dict(center=67, n_events=8,  mode="augment"),   # Outro  augmentation + drop
}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("ContourRaw", program=25, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS[s])
    st = SECTION_TICKS[s]
    evs = country_walk(SEED + s, st, **LEAD_PARAMS[s])
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=st - 1, end_tick=st))
    phase1.set_unit(0, s, MusicUnit(events=evs))
ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
assert ok1, msg1
P1_MIDI = os.path.join(MIDI_DIR, "301-country-hope-rework-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written:", P1_MIDI)


# ----------------------------------------------------------------------
# Phase 2: rules post-process (blanket chord-tone quantize + grid lock)
# ----------------------------------------------------------------------
def process_lead(raw_events, s):
    """Grid-lock -> blanket chord-tone snap (every note -> ITS OWN bar's
    chord) -> voice-leading cap (leap <= 9) -> register clamp -> dedup."""
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
        ck = SECTION_ROT[s][lb]
        ct = chord_tones_for(ck)
        raw = max(55.0, min(84.0, float(int(e.pitch))))
        p = min(ct, key=lambda c: abs(c - raw))
        q.append(MusicEvent(pitch=p, volume=int(e.volume),
                            start_tick=st, end_tick=int(e.end_tick)))
    # voice-leading cap
    for i in range(1, len(q)):
        if abs(int(q[i].pitch) - int(q[i - 1].pitch)) > 9:
            lb = min(int(q[i].start_tick) // BAR, BARS[s] - 1)
            ck = SECTION_ROT[s][lb]
            ct = chord_tones_for(ck)
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
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for s, n in enumerate(NAMES):
    phase2.add_section(n, bars=BARS[s])

# lead (row 0): quantize phase-1 raw draft per section
for s in range(N_SECTIONS):
    raw_events = list(phase1.matrix.get_unit((0, s)).events)
    lead_events = process_lead(raw_events, s)
    phase2.set_unit(0, s, MusicUnit(events=lead_events))

acc = {(r, s): [] for r in range(1, N_V) for s in range(N_SECTIONS)}

# --- Steel Pad (row 1): sustained chord-tone harmony, fuller in chorus ---
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    if s in (0, 5):                      # intro/outro: sparse two-note pad
        acc[(1, s)].append(MusicEvent(pitch=triad[0] + 12, volume=56,
                                      start_tick=t0, end_tick=t0 + BAR - 60))
        acc[(1, s)].append(MusicEvent(pitch=triad[2] + 12, volume=50,
                                      start_tick=t0, end_tick=t0 + BAR - 60))
    elif s in (2, 3):                    # chorus/verse2: full pad, two chunks
        for tone in triad:
            acc[(1, s)].append(MusicEvent(pitch=tone + 12, volume=62,
                                          start_tick=t0, end_tick=t0 + 900))
        for tone in triad:
            acc[(1, s)].append(MusicEvent(pitch=tone + 12, volume=58,
                                          start_tick=t0 + 960, end_tick=t0 + 1800))
    else:                                # verse/bridge: two-note pad
        acc[(1, s)].append(MusicEvent(pitch=triad[1] + 12, volume=56,
                                      start_tick=t0, end_tick=t0 + 900))
        acc[(1, s)].append(MusicEvent(pitch=triad[2] + 12, volume=54,
                                      start_tick=t0 + 960, end_tick=t0 + 1800))

# --- Piano (row 2): comp + bridge counterline ---
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    if s == 4:                           # bridge: descending chord-tone counterline
        acc[(2, s)].append(MusicEvent(pitch=triad[2] + 12, volume=60,
                                      start_tick=t0, end_tick=t0 + 400))
        acc[(2, s)].append(MusicEvent(pitch=triad[1] + 12, volume=58,
                                      start_tick=t0 + 480, end_tick=t0 + 880))
        acc[(2, s)].append(MusicEvent(pitch=triad[0] + 12, volume=56,
                                      start_tick=t0 + 960, end_tick=t0 + 1360))
    elif s in (2, 3):                    # chorus/verse2: off-beat comp (2 & 4)
        for beat_tick in (480, 1440):
            for tone in triad:
                acc[(2, s)].append(MusicEvent(pitch=tone + 12, volume=60,
                                              start_tick=t0 + beat_tick,
                                              end_tick=t0 + beat_tick + 200))
    elif s == 1:                         # verse: light comp (root chick)
        for beat_tick in (480, 1440):
            acc[(2, s)].append(MusicEvent(pitch=triad[0] + 12, volume=54,
                                          start_tick=t0 + beat_tick,
                                          end_tick=t0 + beat_tick + 180))
    # intro/outro: piano tacet (sparse)

# --- Bass (row 3): boom-chick (root beat 1, fifth beat 3) ---
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    root = CHORDS[ck]["bass"]
    t0 = lb * BAR
    acc[(3, s)].append(MusicEvent(pitch=root, volume=100,
                                  start_tick=t0, end_tick=t0 + 460))
    acc[(3, s)].append(MusicEvent(pitch=root + 7, volume=86,
                                  start_tick=t0 + 960, end_tick=t0 + 1420))

# set accompaniment units
for (r, s), evs in acc.items():
    phase2.set_unit(r, s, MusicUnit(events=evs))

# --- Drums (row 4, channel 9): country backbeat with per-section density ---
KICK, SNARE, HHAT, CRASH = 36, 38, 42, 49
DRUM_DENS = {0: 0.5, 1: 0.8, 2: 1.0, 3: 0.8, 4: 0.7, 5: 0.8}
for s in range(N_SECTIONS):
    dens = DRUM_DENS[s]
    evs = []
    for lb in range(BARS[s]):
        t0 = lb * BAR
        evs.append(MusicEvent(pitch=KICK, volume=104, start_tick=t0, end_tick=t0 + 140))
        evs.append(MusicEvent(pitch=KICK, volume=100, start_tick=t0 + 960, end_tick=t0 + 1100))
        if dens >= 0.7:
            evs.append(MusicEvent(pitch=SNARE, volume=100, start_tick=t0 + 480, end_tick=t0 + 600))
            evs.append(MusicEvent(pitch=SNARE, volume=102, start_tick=t0 + 1440, end_tick=t0 + 1560))
        if dens >= 0.8:
            for k in (240, 720, 1200, 1680):
                evs.append(MusicEvent(pitch=HHAT, volume=54, start_tick=t0 + k, end_tick=t0 + k + 60))
        if dens >= 1.0:
            for k in (120, 600, 1080, 1560):
                evs.append(MusicEvent(pitch=HHAT, volume=40, start_tick=t0 + k, end_tick=t0 + k + 40))
    if s == N_SECTIONS - 1:
        t0 = (BARS[s] - 1) * BAR
        evs.append(MusicEvent(pitch=CRASH, volume=90, start_tick=t0 + 1680, end_tick=t0 + 1800))
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


# ----------------------------------------------------------------------
# Grid audit (pre-humanization = "perfect" layer)
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


perfect_grid = grid_audit(phase2)
print("\nGRID AUDIT (perfect):", json.dumps(perfect_grid, indent=2))
grid_pass = all(perfect_grid[v]["off_16th"] == 0 for v in vnames)
print("GRID PASS (perfect off-16th == 0):", grid_pass)
assert grid_pass, "grid audit failed (perfect must be 0 off-16th)"

# --- grid visualization (perfect layer, pre-humanization) ---
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="G major / Country Contour Walk + I-IV-V")

# ----------------------------------------------------------------------
# Dual-version export (perfect + humanized) via canonical export_dual
# ----------------------------------------------------------------------
PERF_MIDI = os.path.join(MIDI_DIR, "301-country-hope-rework-perfect.mid")
HUM_MIDI = os.path.join(MIDI_DIR, "301-country-hope-rework-humanized.mid")
hz = export_dual(phase2, PERF_MIDI, HUM_MIDI, style=STYLE, seed=hz_seed,
                 bpm=BPM, instruments=HZ_INSTRUMENTS)
print("dual-version exported")
print("humanize summary:", json.dumps(hz, indent=2))

# humanized layer grid audit (post-humanization, composer now humanized)
humanized_grid = grid_audit(phase2)
print("\nGRID AUDIT (humanized):", json.dumps(humanized_grid, indent=2))
hz_off = sum(humanized_grid[v]["off_16th"] for v in vnames)
print("humanized total off-16th:", hz_off)


# ----------------------------------------------------------------------
# READ-ONLY mido verification: zero-drift readback
# ----------------------------------------------------------------------
import mido  # noqa: E402  (READING ONLY - analysis)


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
# provenance + summary
# ----------------------------------------------------------------------
section_roots = [(SECTION_ROT[s][1 % BARS[s]],
                  CHORDS[SECTION_ROT[s][1 % BARS[s]]]["quality"])
                 for s in range(N_SECTIONS)]
prog_per_section = {NAMES[s]: SECTION_ROT[s] for s in range(N_SECTIONS)}

provenance_meta = {
    "bpm": BPM, "key": KEY, "key_label": KEY_LABEL, "scale": SCALE_NAME,
    "scale_pcs": sorted(SCALE_PCS),
    "style": STYLE, "source": SOURCE,
    "sections": N_SECTIONS, "bars": N_BARS,
    "progression_per_section": prog_per_section,
    "section_roots_midpoint": section_roots,
    "variation_techniques": [
        "augmentation (Intro+Outro)", "baseline contour (Verse)",
        "diminution + register shift (Chorus)", "inversion + vi shade (Verse2)",
        "retrograde + counterline (Bridge)", "density rise (Chorus)",
        "counterline (Bridge piano)", "authentic cadence V-I (Outro)",
    ],
    "seed": SEED, "humanize_seed": hz_seed,
    "voices": [{"name": v[0], "program": v[1], "channel": v[2]} for v in VOICES],
}

write_provenance(P1_MIDI, AI_ASSISTED,
                 "Country Contour Walk (raw, pre-rules)",
                 sources=[SOURCE + "/MIDI/country-hope-loop-v7.mid"],
                 parameters=dict(provenance_meta, phase="1"),
                 notes="raw single-voice arpeggio+neighbor contour walk, unquantized "
                       "pitch + jittered off-grid rhythm, no harmony")
write_provenance(PERF_MIDI, AI_ASSISTED,
                 "Country Contour Walk + musicom rules (grid-locked)",
                 sources=[SOURCE + "/MIDI/country-hope-loop-v7.mid",
                          "301-country-hope-rework-phase1.mid"],
                 parameters=dict(provenance_meta, phase="2-perfect", humanize=None),
                 notes="grid-locked perfect layer: blanket chord-tone quantize per bar, "
                       "voice-leading checked, zero humanization")
write_provenance(HUM_MIDI, AI_ASSISTED,
                 "Country Contour Walk + musicom rules + humanize",
                 sources=[SOURCE + "/MIDI/country-hope-loop-v7.mid",
                          "301-country-hope-rework-phase1.mid"],
                 parameters=dict(provenance_meta, phase="2-humanized",
                                 humanize_seed=hz_seed, humanize_profiles=hz),
                 notes="humanized layer: country style profile + per-instrument DNA")

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
    json.dump(summary, f, indent=2)

print("\nPROGRESSION (per section):")
for s in range(N_SECTIONS):
    print("  ", NAMES[s], SECTION_ROT[s],
          "midpoint:", SECTION_ROT[s][1 % BARS[s]])

print("\nDONE compose.")
