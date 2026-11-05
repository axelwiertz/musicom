# -*- coding: utf-8 -*-
"""286-country-hoedown-suite -- Country rework of 001-country-loop-seamless.

Rework job (nightly). Two-phase architecture:
  Phase 1: raw "country contour walk" draft (arpeggiated-triad + neighbor-tone
           random walk, single voice, unquantized pitch + off-grid rhythm).
  Phase 2: musicom rules post-process (blanket chord-tone quantization per bar,
           grid-lock to 16th, voice-leading cap, dedup) + full 5-voice Country
           texture, exported as dual versions (perfect + humanized).

Engine only: structures + workflows.unitmatrix_composer + rules + pitch_audit +
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

SEED = 20261105
STYLE = "country"
METHOD_ID = "CW"
METHOD_NAME = "Country Contour Walk (arpeggiated triad + neighbor-tone ornament)"
LAYER = "concrete"
FORM = "intro-verse-chorus-verse2-bridge-chorus2-outro"
SOURCE = "001-country-loop-seamless"

PROJ = "/opt/data/projects/Styles/Country/286-country-hoedown-suite"
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

# G major: G A B C D E F# -> pitch classes {7,9,11,0,2,4,6}
SCALE_PCS = {7, 9, 11, 0, 2, 4, 6}
SCALE_NAME = "major"
SCALE_ROOT = 55              # G3 reference
sq = ScaleQuantizer(root=SCALE_ROOT, scale=SCALE_NAME)
STRONG_GRID_44 = tuple(STRONG_GRID["4/4"])   # (0, 960) = beats 1 & 3

# Country I-IV-V-vi-ii chords in G major (all diatonic).
CHORDS = {
    "G":  {"pcs": {7, 11, 2},  "bass": 43, "triad": [55, 59, 62]},   # G3 B3 D4
    "C":  {"pcs": {0, 4, 7},   "bass": 36, "triad": [48, 52, 55]},   # C3 E3 G3
    "D":  {"pcs": {2, 6, 9},   "bass": 38, "triad": [50, 54, 57]},   # D3 F#3 A3
    "Em": {"pcs": {4, 7, 11},  "bass": 40, "triad": [52, 55, 59]},   # E3 G3 B3
    "Am": {"pcs": {9, 0, 4},   "bass": 45, "triad": [57, 60, 64]},   # A3 C4 E4
}
CHORD_KEYS = list(CHORDS.keys())

# form layout: 7 sections, 32 bars (source was 16-bar loop -> N+3 sections)
NAMES = ["Intro", "Verse", "Chorus", "Verse2", "Bridge", "Chorus2", "Outro"]
BARS = [4, 4, 8, 4, 4, 4, 4]
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS)            # 32
SECTION_TICKS = [b * BAR for b in BARS]

# per-section chord rotation -> varied midpoint roots (no bar-0 tonic monotony)
SECTION_ROT = {
    0: ["G", "C", "G", "D"],      # Intro   midpoint C
    1: ["G", "Em", "C", "D"],     # Verse   midpoint Em
    2: ["C", "G", "D", "G"],      # Chorus  midpoint G
    3: ["Em", "Am", "C", "D"],    # Verse2  midpoint Am
    4: ["Am", "Em", "C", "D"],    # Bridge  midpoint Em
    5: ["C", "G", "D", "G"],      # Chorus2 midpoint G
    6: ["G", "C", "D", "G"],      # Outro   midpoint C
}

# voices: (voice name, registry instrument name, GM program, channel)
VOICES = [
    ("Fiddle",  "violin",         40, 0),
    ("Guitar",  "steel_acoustic", 25, 1),
    ("Bass",    "acoustic_bass",  32, 2),
    ("Harmony", "acoustic_guitar", 24, 3),
    ("Drums",   "drum_kit",        0, 9),
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


# ----------------------------------------------------------------------
# Phase 1: raw country contour walk -> single-voice unquantized melody
# ----------------------------------------------------------------------
def country_walk(seed, dur_ticks, center, n_events, mode):
    """Arpeggiated-triad + neighbor-tone contour walk.

    Interval pool favours triad leaps (up/down 3rd, 4th, 5th) with stepwise
    passing/neighbor tones -- echoes the source fiddle's G-B-D-B arpeggio.
    Onsets + durations intentionally jittered (off-grid): phase-1 raw draft.
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
#   Intro   -> augmentation + register drop (sparse, long notes)
#   Verse   -> baseline contour
#   Chorus  -> register shift up + diminution (denser 16th feel)
#   Verse2  -> transposition (center up a 4th) + Am/Em mode shade
#   Bridge  -> inversion (mirrored contour) + relative-minor region
#   Chorus2 -> register up (counterline added in accompaniment)
#   Outro   -> retrograde (reversed contour) + register drop to resolve
LEAD_PARAMS = {
    0: dict(center=67, n_events=16, mode="augment"),
    1: dict(center=72, n_events=32, mode="base"),
    2: dict(center=79, n_events=64, mode="diminish"),
    3: dict(center=77, n_events=32, mode="base"),
    4: dict(center=74, n_events=40, mode="invert"),
    5: dict(center=79, n_events=48, mode="base"),
    6: dict(center=67, n_events=24, mode="retro"),
}

phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("ContourRaw", program=40, channel=0)
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS[s])
    st = SECTION_TICKS[s]
    evs = country_walk(SEED + s, st, **LEAD_PARAMS[s])
    evs.append(MusicEvent(pitch=0, volume=0, start_tick=st - 1, end_tick=st))
    phase1.set_unit(0, s, MusicUnit(events=evs))
ok1, msg1 = phase1.validate()
print("PHASE1 validate:", msg1)
P1_MIDI = os.path.join(MIDI_DIR, "286-country-hoedown-suite-phase1.mid")
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
        ck = SECTION_ROT[s][lb % 4]
        ct = chord_tones_for(ck)
        raw = max(55.0, min(84.0, float(int(e.pitch))))
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

# --- Guitar (row 1): boom-chick strum (root on 1&3, triad strum on 2&4)
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    # boom (low root) on beat 1 & 3, chick (triad strum) on beat 2 & 4
    acc[(1, s)].append(MusicEvent(pitch=triad[0], volume=78,
                                  start_tick=t0, end_tick=t0 + 400))
    for tone in triad:
        acc[(1, s)].append(MusicEvent(pitch=tone + 12, volume=62,
                                      start_tick=t0 + 480, end_tick=t0 + 760))
    acc[(1, s)].append(MusicEvent(pitch=triad[2], volume=74,
                                  start_tick=t0 + 960, end_tick=t0 + 1320))
    for tone in triad:
        acc[(1, s)].append(MusicEvent(pitch=tone + 12, volume=60,
                                      start_tick=t0 + 1440, end_tick=t0 + 1720))

# --- Bass (row 2): walking line (root, fifth, root, octave per bar)
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
            p, v = root, 96
        else:
            p, v = root + 12, 88
        acc[(2, s)].append(MusicEvent(pitch=p, volume=v, start_tick=bt, end_tick=bt + 380))

# --- Harmony (row 3): counterline (sustained chord third/fifth above the
#     fiddle), fullest in Chorus/Chorus2, light pad elsewhere
for bar in range(N_BARS):
    s, lb = bar_to_section(bar)
    ck = chord_key_for_bar(bar)
    triad = CHORDS[ck]["triad"]
    t0 = lb * BAR
    if s in (2, 5):          # chorus/chorus2: full counterline
        third = triad[1] + 12
        fifth = triad[2] + 12
        acc[(3, s)].append(MusicEvent(pitch=third, volume=66,
                                      start_tick=t0, end_tick=t0 + 900))
        acc[(3, s)].append(MusicEvent(pitch=fifth, volume=60,
                                      start_tick=t0 + 960, end_tick=t0 + 1800))
    elif s in (1, 4):        # verse/bridge: light pad
        fifth = triad[2] + 12
        acc[(3, s)].append(MusicEvent(pitch=fifth, volume=54,
                                      start_tick=t0, end_tick=t0 + 1680))
    elif s == 6:             # outro: resolve to root
        acc[(3, s)].append(MusicEvent(pitch=triad[0] + 12, volume=58,
                                      start_tick=t0, end_tick=t0 + BAR - 60))

# set accompaniment units
for (r, s), evs in acc.items():
    phase2.set_unit(r, s, MusicUnit(events=evs))

# --- Drums (row 4, channel 9): country backbeat (kick 1&3, snare 2&4, hats)
KICK, SNARE, HHAT, CRASH = 36, 38, 42, 49
DRUM_DENS = {0: 0.5, 1: 0.8, 2: 1.0, 3: 0.8, 4: 0.7, 5: 1.0, 6: 0.9}
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
                         mode="G major / Country Contour Walk + I-IV-V")

# ----------------------------------------------------------------------
# Dual-version export (perfect + humanized) via canonical export_dual
# ----------------------------------------------------------------------
from workflows.humanize import export_dual  # noqa: E402
hz_instruments = {v[0]: by_name(v[1]).humanize_dna for v in VOICES}
hz_seed = SEED
PERF_MIDI = os.path.join(MIDI_DIR, "286-country-hoedown-suite-perfect.mid")
HUM_MIDI = os.path.join(MIDI_DIR, "286-country-hoedown-suite-humanized.mid")
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
# provenance + summary
# ----------------------------------------------------------------------
from workflows.provenance import write_provenance, AI_ASSISTED  # noqa: E402

section_roots = [SECTION_ROT[s][1 % 4] for s in range(N_SECTIONS)]  # midpoint chord
prog_per_section = {NAMES[s]: SECTION_ROT[s] for s in range(N_SECTIONS)}

provenance_meta = {
    "bpm": BPM, "key": "G major", "scale": SCALE_NAME,
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
                 "Country Contour Walk + musicom rules",
                 parameters=dict(provenance_meta, phase="1"),
                 notes="raw single-voice arpeggio+neighbor contour walk, unquantized "
                       "pitch + jittered off-grid rhythm, no harmony")
write_provenance(PERF_MIDI, AI_ASSISTED,
                 "Country Contour Walk + musicom rules",
                 parameters=dict(provenance_meta, phase="2-perfect", humanize=None),
                 notes="grid-locked perfect layer: blanket chord-tone quantize per bar, "
                       "voice-leading checked, zero humanization")
write_provenance(HUM_MIDI, AI_ASSISTED,
                 "Country Contour Walk + musicom rules",
                 parameters=dict(provenance_meta, phase="2-humanized",
                                 humanize_seed=hz_seed, humanize_profiles=hz),
                 notes="humanized layer: country style profile + per-instrument DNA")

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
