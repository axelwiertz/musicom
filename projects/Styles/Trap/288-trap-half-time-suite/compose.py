# -*- coding: utf-8 -*-
"""288-trap-half-time-suite -- Trap rework of 209-trap-half-time-rework.

Rework job (nightly). Two-phase architecture:
  Phase 1: raw Brownian-walk draft (dark-minor interval pool, single voice,
           unquantized pitch + jittered off-grid rhythm, no harmony).
  Phase 2: musicom rules post-process (blanket chord-tone quantization per bar,
           grid-lock to 16th, voice-leading cap, dedup) + full 5-voice Trap
           texture (square lead, saw counter, dark pad, 808 sub, half-time
           drums), exported as dual versions (perfect + humanized).

Engine only: structures + workflows.unitmatrix_composer + pitch_audit +
humanize. mido used for READ-ONLY verification only.
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
STYLE = "trap"
METHOD_ID = "BW"
METHOD_NAME = "Trap Brownian Walk (dark-minor interval pool + half-time groove)"
LAYER = "concrete"
FORM = "intro-verse-chorus-verse2-bridge-chorus2-break-outro"
SOURCE = "209-trap-half-time-rework"

PROJ = "/opt/data/projects/Styles/Trap/288-trap-half-time-suite"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

BPM = 140
TPB = 480
BEATS = 4
BAR = TPB * BEATS            # 1920 ticks
GRID = 120                   # 16th note
EIGHTH = 240
SIXTEENTH = 120

# C natural minor: C D Eb F G Ab Bb -> pitch classes {0,2,3,5,7,8,10}
SCALE_PCS = {0, 2, 3, 5, 7, 8, 10}
SCALE_NAME = "minor"
SCALE_ROOT = 48              # C3 reference
sq = ScaleQuantizer(root=SCALE_ROOT, scale=SCALE_NAME)
STRONG_GRID_44 = tuple(STRONG_GRID["4/4"])   # (0, 960) = beats 1 & 3

# C natural minor diatonic chords (triads + sub-bass roots)
CHORDS = {
    "Cm":   {"pcs": {0, 3, 7},  "bass": 36, "triad": [48, 51, 55]},
    "Ddim": {"pcs": {2, 5, 8},  "bass": 38, "triad": [50, 53, 56]},
    "Eb":   {"pcs": {3, 7, 10}, "bass": 39, "triad": [51, 55, 58]},
    "Fm":   {"pcs": {5, 8, 0},  "bass": 41, "triad": [53, 56, 60]},
    "Gm":   {"pcs": {7, 10, 2}, "bass": 43, "triad": [55, 58, 62]},
    "Ab":   {"pcs": {8, 0, 3},  "bass": 44, "triad": [56, 60, 63]},
    "Bb":   {"pcs": {10, 2, 5}, "bass": 46, "triad": [58, 62, 65]},
}
CHORD_KEYS = list(CHORDS.keys())

# form layout: 8 sections, 32 bars (source was 24 bars / 6 sections -> N+2)
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Bridge", "Chorus2", "Break", "Outro"]
BARS = [4, 4, 4, 4, 4, 4, 4, 4]
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS)            # 32
SECTION_TICKS = [b * BAR for b in BARS]

# per-section chord rotation -> varied midpoint roots (no bar-0 tonic monotony)
SECTION_ROT = {
    0: ["Cm", "Ab", "Cm", "Ab"],      # Intro   midpoint Ab
    1: ["Cm", "Gm", "Ab", "Bb"],      # Verse   midpoint Gm
    2: ["Ab", "Eb", "Bb", "Cm"],      # Chorus  midpoint Eb
    3: ["Fm", "Ab", "Gm", "Cm"],      # Verse2  midpoint Ab
    4: ["Ddim", "Gm", "Cm", "Bb"],    # Bridge  midpoint Gm (darkest)
    5: ["Ab", "Eb", "Bb", "Cm"],      # Chorus2 midpoint Eb
    6: ["Cm", "Cm", "Ab", "Cm"],      # Break   midpoint Cm (ambient)
    7: ["Cm", "Ab", "Cm", "Cm"],      # Outro   midpoint Ab
}

# voices: (voice name, registry instrument, GM program, channel)
VOICES = [
    ("Lead",    "synth_brass_1", 80, 0),
    ("Counter", "synth_voice",   81, 1),
    ("Pad",     "synth_pad",     88, 2),
    ("808",     "synth_bass_1",  38, 3),
    ("Drums",   "drum_kit",       0, 9),
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
    return sorted({t + 12 * o for t in triad for o in range(-3, 5)})


# ---------------------------------------------------------------------------
# Phase 1: raw trap Brownian walk -> single-voice unquantized melody
# ---------------------------------------------------------------------------
def trap_walk(seed, dur_ticks, center, n_events, mode):
    """Dark-minor interval pool + neighbour-tone Brownian walk.

    Interval pool favours minor-2nd/3rd steps with occasional octave/5th leaps
    (808-style drop) -- echoes the source's sparse square-lead contour.
    Onsets + durations intentionally jittered (off-grid): phase-1 raw draft.
    """
    r = np.random.default_rng(seed)
    IV = [0, 2, -2, 3, -3, 1, -1, 5, -5, 7, -7, 12, -12]
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
            dur = int(max(240.0, step * 1.8))       # augmentation (long notes)
        elif mode == "diminish":
            dur = int(max(90.0, step * 0.55))       # diminution (denser)
        else:
            dur = int(max(120.0, step * r.uniform(0.6, 1.05)))
        dur = min(dur, dur_ticks - onset)
        pitch = float(np.clip(pitch + iv, center - 12.0, center + 12.0))
        velo = int(np.clip(70 + 25 * r.standard_normal(), 55, 110))
        events.append(MusicEvent(pitch=int(round(pitch)), volume=velo,
                                 start_tick=onset, end_tick=onset + dur))
    return events


# per-section generative params (variation techniques live here)
#   Intro   -> augmentation + register drop (sparse, long notes)
#   Verse   -> baseline contour walk
#   Chorus  -> register shift up + diminution (denser 16th feel)
#   Verse2  -> transposition (center up a 4th) + Fm/Ab mode shade
#   Bridge  -> inversion (mirrored contour) + Ddim dark region
#   Chorus2 -> register up (counterline added in accompaniment)
#   Break   -> augmentation + near-sparse (sustained pad only)
#   Outro   -> retrograde (reversed contour) + register drop to resolve
LEAD_PARAMS = {
    0: dict(center=60, n_events=12, mode="augment"),
    1: dict(center=66, n_events=24, mode="base"),
    2: dict(center=72, n_events=48, mode="diminish"),
    3: dict(center=71, n_events=24, mode="base"),
    4: dict(center=64, n_events=32, mode="invert"),
    5: dict(center=72, n_events=48, mode="base"),
    6: dict(center=60, n_events=8,  mode="augment"),
    7: dict(center=60, n_events=16, mode="retro"),
}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("LeadRaw", program=80, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS[s])
    st = SECTION_TICKS[s]
    evs = trap_walk(SEED + s, st, **LEAD_PARAMS[s])
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=st - 1, end_tick=st))
    phase1.set_unit(0, s, MusicUnit(events=evs))
ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "288-trap-half-time-suite-phase1.mid")
phase1.to_midi(P1_MIDI)
print("phase1 written:", P1_MIDI)


# ---------------------------------------------------------------------------
# Phase 2: rules post-process (blanket chord-tone quantize + grid lock)
# ---------------------------------------------------------------------------
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
        ck = SECTION_ROT[s][lb % 4]
        ct = chord_tones_for(ck)
        raw = max(48.0, min(84.0, float(int(e.pitch))))
        p = min(ct, key=lambda c: abs(c - raw))
        q.append(MusicEvent(pitch=p, volume=int(e.volume),
                            start_tick=st, end_tick=int(e.end_tick)))
    # voice-leading cap
    for i in range(1, len(q)):
        if abs(int(q[i].pitch) - int(q[i - 1].pitch)) > 9:
            lb = min(int(q[i].start_tick) // BAR, BARS[s] - 1)
            ck = SECTION_ROT[s][lb % 4]
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

# --- 808 sub (row 3): sustained sub root whole bar + octave pulse on beat 3
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    root = CHORDS[ck]["bass"]
    t0 = lb * BAR
    if s == 6:                 # Break: sparse, low sub only
        acc[(3, s)].append(MusicEvent(pitch=root, volume=72,
                                      start_tick=t0, end_tick=t0 + BAR - 120))
    else:
        acc[(3, s)].append(MusicEvent(pitch=root, volume=94,
                                      start_tick=t0, end_tick=t0 + BAR - 120))
        acc[(3, s)].append(MusicEvent(pitch=root + 12, volume=76,
                                      start_tick=t0 + 960, end_tick=t0 + BAR - 120))

# --- Pad (row 2): sustained dark triad (up an octave into the sweet spot),
#     shimmer octave added in chorus/chorus2
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    vel = 56 if s in (0, 6) else 64
    for tone in triad:
        acc[(2, s)].append(MusicEvent(pitch=tone + 12, volume=vel,
                                      start_tick=t0, end_tick=t0 + BAR - 60))
    if s in (2, 5):
        for tone in triad[:2]:
            acc[(2, s)].append(MusicEvent(pitch=tone + 24, volume=52,
                                          start_tick=t0, end_tick=t0 + BAR - 60))

# --- Counter (row 1): counterline (3rd/5th/octave chord tones), fullest in
#     Chorus/Chorus2, light elsewhere
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    if s in (2, 5):            # chorus/chorus2: arpeggio counterline
        acc[(1, s)].append(MusicEvent(pitch=triad[1] + 12, volume=64,
                                      start_tick=t0, end_tick=t0 + 480))
        acc[(1, s)].append(MusicEvent(pitch=triad[2] + 12, volume=60,
                                      start_tick=t0 + 480, end_tick=t0 + 960))
        acc[(1, s)].append(MusicEvent(pitch=triad[0] + 24, volume=58,
                                      start_tick=t0 + 960, end_tick=t0 + 1440))
    elif s == 4:               # bridge: descending (inverted feel)
        acc[(1, s)].append(MusicEvent(pitch=triad[2] + 12, volume=56,
                                      start_tick=t0, end_tick=t0 + 960))
        acc[(1, s)].append(MusicEvent(pitch=triad[1] + 12, volume=56,
                                      start_tick=t0 + 960, end_tick=t0 + 1920))
    elif s in (1, 3):          # verse/verse2: light sustained 5th
        acc[(1, s)].append(MusicEvent(pitch=triad[2] + 12, volume=50,
                                      start_tick=t0, end_tick=t0 + BAR - 60))
    elif s == 7:               # outro: resolve to root
        acc[(1, s)].append(MusicEvent(pitch=triad[0] + 12, volume=54,
                                      start_tick=t0, end_tick=t0 + BAR - 60))

for (r, s), evs in acc.items():
    phase2.set_unit(r, s, MusicUnit(events=evs))

# --- Drums (row 4, channel 9): trap half-time (kick 1 + and-of-3, snare 3,
#     16th hats, 32nd roll before beat 4 in chorus)
KICK, SNARE, CHHAT, OHHAT, CRASH = 36, 38, 42, 46, 49
DRUM_DENS = {0: 0.4, 1: 0.7, 2: 1.0, 3: 0.7, 4: 0.8, 5: 1.0, 6: 0.15, 7: 0.5}
for s in range(N_SECTIONS):
    dens = DRUM_DENS[s]
    evs = []
    for lb in range(BARS[s]):
        t0 = lb * BAR
        evs.append(MusicEvent(pitch=KICK, volume=100, start_tick=t0, end_tick=t0 + 120))
        if dens >= 0.6:
            evs.append(MusicEvent(pitch=KICK, volume=96, start_tick=t0 + 1200, end_tick=t0 + 1320))
        if dens >= 0.5:
            evs.append(MusicEvent(pitch=SNARE, volume=100, start_tick=t0 + 960, end_tick=t0 + 1080))
        if dens >= 0.7:
            for k in range(16):
                v = 52 if k % 2 == 0 else 64
                evs.append(MusicEvent(pitch=CHHAT, volume=v,
                                      start_tick=t0 + k * 120, end_tick=t0 + k * 120 + 60))
        elif dens >= 0.4:
            for k in range(8):
                evs.append(MusicEvent(pitch=CHHAT, volume=50,
                                      start_tick=t0 + k * 240, end_tick=t0 + k * 240 + 60))
        if dens >= 1.0:        # 32nd roll before beat 4
            for j in range(4):
                evs.append(MusicEvent(pitch=CHHAT, volume=88,
                                      start_tick=t0 + 14 * 120 + j * 60,
                                      end_tick=t0 + 14 * 120 + j * 60 + 30))
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
grid_pass = all(perfect_grid[v]["off_16th"] == 0 for v in vnames[:4])  # pitched only (drums ch9 exempt)
print("\nHARMONY PASS:", harmony_pass, "| GRID PASS:", grid_pass)
assert harmony_pass, "harmony audit failed"
assert grid_pass, "grid audit failed (perfect must be 0 off-16th)"

from visualization.grid import write_grid_visualization  # noqa: E402
grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, grid_path, ticks_per_character=120,
                         voice_names=vnames, bpm=BPM,
                         mode="C natural minor / Trap Brownian Walk + half-time groove")


# ---------------------------------------------------------------------------
# Dual-version export (perfect + humanized) via canonical export_dual
# ---------------------------------------------------------------------------
from workflows.humanize import export_dual  # noqa: E402
hz_instruments = {v[0]: by_name(v[1]).humanize_dna for v in VOICES}
hz_seed = SEED
PERF_MIDI = os.path.join(MIDI_DIR, "288-trap-half-time-suite-perfect.mid")
HUM_MIDI = os.path.join(MIDI_DIR, "288-trap-half-time-suite-humanized.mid")
hz = export_dual(phase2, PERF_MIDI, HUM_MIDI, style=STYLE, seed=hz_seed,
                 bpm=BPM, instruments=hz_instruments)
print("\ndual-version exported")
print("humanize summary:", json.dumps(hz, indent=2))

humanized_grid = grid_audit(phase2)
print("\nGRID AUDIT (humanized):", json.dumps(humanized_grid, indent=2))
hz_off = sum(humanized_grid[v]["off_16th"] for v in vnames[:4])  # pitched voices only
hz_off_all = sum(humanized_grid[v]["off_16th"] for v in vnames)
print("humanized total off-16th (pitched):", hz_off)
print("humanized total off-16th (all voices):", hz_off_all)


# ---------------------------------------------------------------------------
# READ-ONLY mido verification: zero-drift readback + off-grid counts
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
    "bpm": BPM, "key": "C natural minor", "scale": SCALE_NAME,
    "scale_pcs": sorted(SCALE_PCS),
    "style": STYLE, "method_id": METHOD_ID, "method": METHOD_NAME,
    "layer": LAYER, "form": FORM, "source": SOURCE,
    "sections": N_SECTIONS, "bars": N_BARS,
    "progression_per_section": prog_per_section,
    "section_roots_midpoint": section_roots,
    "seed": SEED, "humanize_seed": hz_seed,
    "voices": [{"name": v[0], "instrument": v[1], "program": v[2], "channel": v[3]}
               for v in VOICES],
}

write_provenance(P1_MIDI, AI_ASSISTED,
                 "Trap Brownian Walk + musicom rules",
                 parameters=dict(provenance_meta, phase="1"),
                 notes="raw single-voice dark-minor Brownian walk, unquantized "
                       "pitch + jittered off-grid rhythm, no harmony")
write_provenance(PERF_MIDI, AI_ASSISTED,
                 "Trap Brownian Walk + musicom rules",
                 parameters=dict(provenance_meta, phase="2-perfect", humanize=None),
                 notes="grid-locked perfect layer: blanket chord-tone quantize per bar, "
                       "voice-leading checked, zero humanization")
write_provenance(HUM_MIDI, AI_ASSISTED,
                 "Trap Brownian Walk + musicom rules",
                 parameters=dict(provenance_meta, phase="2-humanized",
                                 humanize_seed=hz_seed, humanize_profiles=hz),
                 notes="humanized layer: trap style profile + per-instrument DNA")

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
