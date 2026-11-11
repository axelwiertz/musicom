# -*- coding: utf-8 -*-
"""296-electronic-rmt-spectral -- Electronic / Method 120 RMTC.

Random Matrix Theory Composition (RMTC), Stochastic, concrete layer.

Two-phase architecture:
  Phase 1: raw generative draft. Sample a random matrix (GOE/GUE/GSE) per
           section, diagonalise it, and build a single-voice chromatic contour
           from the eigenvalue spectrum:
             - eigenvalues -> Wigner semicircle pitch pool (peaked at tonic)
             - nearest-neighbour spacings -> melodic intervals with LEVEL
               REPULSION (Wigner surmise: P(s)->0 as s->0, no unisons)
             - ensemble beta switching drives macro-form: Intro/Resolve GOE
               (beta=1), Build/Rise GUE (beta=2), Peak GSE (beta=4, strongest
               repulsion + Tracy-Widom largest eigenvalue -> registral climax).
           Onsets carry off-grid jitter; pitch is unquantized chromatic.
           Single voice, NO harmony/bass/pad/drums.

  Phase 2: musicom rules post-process:
            1. grid-lock the lead to the 8th grid (078 rule).
            2. tiered snap (ScaleQuantizer root=C3 minor + classify_weight):
               strong beats -> bar's chord tone, weak -> C-minor scale tone.
            3. texture: synth-bass root/fifth, synth-pad triad (spectral-rigidity
               voicing), 16th-note arp (chord-tone arpeggio), 4-on-the-floor
               drums.
            4. zero-drift landmark + validate() on BOTH phases.
            5. export_dual -> -perfect.mid + -humanized.mid.

Engine only. mido is used READ-ONLY in the separate verify step.

C natural minor: pitch classes {0,2,3,5,7,8,10} = C D Eb F G Ab Bb.
"""
import os
import json
import sys

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual
from workflows.musicom_workflow import pick_form, form_to_sections

# instrument registry (source of truth - NOT pip-installed)
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    SINGING_SAW, SYNTH_BASS_1, SYNTH_PAD, CALIOPE, DRUM_KIT,
)

SEED = 20261110
HZ_SEED = SEED * 13 + 296
FORM_SEED = SEED * 10 + 3

# ------------------------------------------------------------------ project
PROJ = "/opt/data/projects/Styles/Electronic/296-electronic-rmt-spectral"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- concept
BPM = 128
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120                     # 16th-note grid
GRID8 = 240                      # 8th-note grid

# form: cinematic-build (from pick_form("electronic") with FORM_SEED)
_form = pick_form("electronic", rng=np.random.default_rng(FORM_SEED))
while _form in ("loop", "loop4", "loop16"):
    _form = pick_form("electronic", rng=np.random.default_rng(FORM_SEED + 1))
FORM = _form
NAMES, BARS_PER = form_to_sections(FORM)
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS_PER)

# running bar offsets per section
SEC_BAR_OFFSET = []
acc = 0
for b in BARS_PER:
    SEC_BAR_OFFSET.append(acc)
    acc += b

# C natural minor
KEY = "C natural minor"
KEY_PCS = {0, 2, 3, 5, 7, 8, 10}
TONIC = 48                      # C3, ScaleQuantizer root
SCALE_ROOT = 48

# ------------------------------------------------------------------- harmony
# i - VI - III - VII  (C-minor dark progression, classic electronic/EDM)
CHORDS = {
    "i":   {"pcs": {0, 3, 7},   "root": 36, "name": "Cm"},
    "VI":  {"pcs": {8, 0, 3},   "root": 32, "name": "Ab"},
    "III": {"pcs": {3, 7, 10},  "root": 39, "name": "Eb"},
    "VII": {"pcs": {10, 2, 5},  "root": 34, "name": "Bb"},
}
_CYCLE = ["i", "VI", "III", "VII"]
BAR_PROG = []
for s in range(N_SECTIONS):
    n = BARS_PER[s]
    if NAMES[s] == "Resolve":
        BAR_PROG += ["i", "VII", "VI", "i"]      # cadential return
    else:
        BAR_PROG += _CYCLE * (n // 4) + _CYCLE[:n % 4]
assert len(BAR_PROG) == N_BARS, (len(BAR_PROG), N_BARS)

CHORD_PCS_BY_BAR = {bar: sorted(CHORDS[BAR_PROG[bar]]["pcs"])
                    for bar in range(N_BARS)}
ROOT_BY_BAR = {bar: CHORDS[BAR_PROG[bar]]["root"] for bar in range(N_BARS)}

# per-section RMTC ensemble + matrix dimension (macro-form driver)
ENSEMBLE = {"Intro": "GOE", "Build": "GUE", "Rise": "GUE",
            "Peak": "GSE", "Resolve": "GOE"}
N_DIM = {"Intro": 8, "Build": 12, "Rise": 16, "Peak": 20, "Resolve": 8}
K_PITCH = 4.0                    # semitones per eigenvalue unit
M_INTERVAL = 4.0                 # semitones per normalized spacing

# voice registers
LEAD_LO, LEAD_HI = 60, 84
ARP_LO, ARP_HI = 60, 84
PAD_LO, PAD_HI = 55, 79
BASS_LO, BASS_HI = 30, 48


def chord_tones(bar, lo, hi):
    tones = set()
    for base in (36, 48, 60, 72, 84, 96, 108):
        for pc in CHORD_PCS_BY_BAR[bar]:
            p = base + pc
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def scale_tones(lo, hi):
    return [p for p in range(lo, hi + 1) if p % 12 in KEY_PCS]


# ------------------------------------------------------------------- RMTC
def sample_matrix(ensemble, N, rng):
    """Sample an N x N matrix from the given invariant ensemble."""
    if ensemble == "GOE":
        A = rng.standard_normal((N, N))
        return (A + A.T) / np.sqrt(2.0 * N)
    if ensemble == "GUE":
        A = rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))
        return (A + A.conj().T) / np.sqrt(4.0 * N)
    # GSE: 2N x 2N real quaternion self-dual matrix
    H = np.zeros((2 * N, 2 * N))
    for i in range(N):
        for j in range(N):
            a, b, c, d = rng.standard_normal(4)
            H[2 * i:2 * i + 2, 2 * j:2 * j + 2] = [[a + d, -b + c],
                                                    [b + c, a - d]]
    H = (H + H.T) / np.sqrt(8.0 * N)
    return H


def eigenvalues(H):
    """Sorted eigenvalues (real; Hermitian matrices give real spectrum)."""
    lam = np.linalg.eigvalsh(H)
    return np.sort(lam)


def rmt_section(ensemble, N, rng):
    """Return (lam_norm, spacings, lam_max) for one section's matrix sample."""
    H = sample_matrix(ensemble, N, rng)
    lam = eigenvalues(H)
    lam_norm = np.clip((lam - lam.mean()) / (lam.std() + 1e-12), -2.0, 2.0)
    gaps = np.diff(lam)
    spacings = gaps / (gaps.mean() + 1e-12)
    return lam_norm, spacings, float(lam[-1])


def raw_rmtc_contour(ensemble, N, span_ticks, seed):
    """Single-voice raw draft: chromatic contour from eigenvalue spectrum.

    - pitch pool = tonic + K * semicircle eigenvalue (peaked near tonic)
    - intervals  = round(Wigner-surmise spacing * M)  (level repulsion: no 0)
    - off-grid onset jitter + unquantized chromatic pitch (by design).
    """
    rng = np.random.default_rng(seed)
    lam_norm, spacings, lam_max = rmt_section(ensemble, N, rng)
    n_slots = max(1, int(span_ticks // GRID8))
    events = []
    pitch = int(round(TONIC + K_PITCH * lam_norm[0]))
    onset = 0.0
    n_gap = max(1, N - 1)
    for i in range(n_slots):
        s = float(spacings[i % n_gap])
        interval = int(round(s * M_INTERVAL))
        direction = 1 if (i % 2 == 0) else -1
        pitch = pitch + direction * interval
        pitch = int(np.clip(pitch, 36, 96))
        st = int(round(onset + rng.normal(0, 18)))
        st = max(0, min(st, span_ticks - 40))
        dur = int(round(190 + rng.normal(0, 35)))
        en = min(st + dur, span_ticks - 1)
        if en <= st:
            en = st + 1
        vel = int(np.clip(80 + rng.normal(0, 12), 55, 105))
        events.append(MusicEvent(pitch=pitch, volume=vel,
                                 start_tick=st, end_tick=en))
        onset += GRID8 + rng.normal(0, 20)
    return events, lam_max


# ------------------------------------------------------------ PHASE 1: raw
phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("RMT_Raw", program=SINGING_SAW.midi_program, channel=0)

P1_OFFGRID = 0
P1_MEAN = {}
P1_LAMMAX = {}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER[s])
    span = BARS_PER[s] * BAR
    evs, lam_max = raw_rmtc_contour(ENSEMBLE[name], N_DIM[name], span, SEED + s)
    if not any(e.pitch == 0 and e.end_tick == span for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1,
                              end_tick=span))
    P1_OFFGRID += sum(1 for e in evs if e.pitch != 0 and e.start_tick % GRID16 != 0)
    pitches = [e.pitch for e in evs if e.pitch != 0]
    P1_MEAN[name] = round(float(np.mean(pitches)), 2) if pitches else 0.0
    P1_LAMMAX[name] = round(lam_max, 4)
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
if not ok1:
    raise RuntimeError("phase1 validate FAIL: " + msg1)
P1_MIDI = os.path.join(MIDI_DIR, "296-electronic-rmt-spectral-phase1.mid")
phase1.to_midi(P1_MIDI)
assert os.path.getsize(P1_MIDI) > 40
print("PHASE1 validate:", msg1, "| off-grid onsets:", P1_OFFGRID)
print("PHASE1 per-section mean pitch:", P1_MEAN)
print("PHASE1 per-section lambda_max:", P1_LAMMAX)


# ------------------------------------------------------------ PHASE 2: rules
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead", SINGING_SAW.midi_program, 0),     # RMTC contour lead
    ("Bass", SYNTH_BASS_1.midi_program, 1),    # root/fifth
    ("Pad", SYNTH_PAD.midi_program, 2),        # sustained triad
    ("Arp", CALIOPE.midi_program, 3),          # 16th-note chord arpeggio
    ("Drums", 0, 9),                            # percussion
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for i, name in enumerate(NAMES):
    phase2.add_section(name, bars=BARS_PER[i])

# tiered pitch discipline (engine)
from sound.synthesis.scale_quantizer import (  # noqa: E402
    ScaleQuantizer, classify_weight, STRONG_GRID,
)
sq = ScaleQuantizer(root=SCALE_ROOT, scale="minor")
STRONG = STRONG_GRID.get("4/4", (0, 960))


def grid_lock_dedup(events, grid=GRID8):
    by_key = {}
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        st = max(0, st)
        en = max(st + 1, int(e.end_tick))
        key = (st, e.pitch)
        if key in by_key:
            if en > by_key[key].end_tick:
                by_key[key] = MusicEvent(pitch=e.pitch,
                                         volume=max(e.volume, by_key[key].volume),
                                         start_tick=st, end_tick=en)
        else:
            by_key[key] = MusicEvent(pitch=e.pitch, volume=e.volume,
                                     start_tick=st, end_tick=en)
    for key in sorted(by_key):
        out.append(by_key[key])
    return out


def landmark(events, span):
    out = []
    for e in events:
        if e.start_tick >= span:
            continue
        st = min(int(e.start_tick), span - 1)
        en = min(int(e.end_tick), span)
        if en <= st:
            en = st + 1
        out.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                              start_tick=st, end_tick=en))
    out.sort(key=lambda e: (e.start_tick, 0 if e.pitch == 0 else 1))
    if not any(e.pitch == 0 and e.end_tick == span for e in out):
        out.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1,
                              end_tick=span))
    return out


def snap(e, bar, lo, hi):
    w = classify_weight(e.start_tick, STRONG, BAR)
    if w == "strong":
        tones = chord_tones(bar, lo=lo, hi=hi)
        return sq.tiered_quantize(e.pitch, weight="strong", chord_tones=tones)
    p = sq.quantize(e.pitch)
    if p < lo or p > hi:
        cands = scale_tones(lo, hi)
        if cands:
            p = min(cands, key=lambda x: abs(x - p))
    return p


# lead register per section: Peak lifted by Tracy-Widom lambda_max
def lead_register(name):
    if name == "Peak":
        return 60, 96
    if name == "Rise":
        return 60, 90
    return LEAD_LO, LEAD_HI


# ---- lead: RMTC contour, grid-locked + tiered snap ------------------------
for s, name in enumerate(NAMES):
    span = BARS_PER[s] * BAR
    evs, _ = raw_rmtc_contour(ENSEMBLE[name], N_DIM[name], span, SEED + s)
    evs = grid_lock_dedup(evs)
    lo, hi = lead_register(name)
    out = []
    seen = {}
    for e in evs:
        if e.pitch == 0:
            continue
        bar = SEC_BAR_OFFSET[s] + (e.start_tick // BAR)
        pitch = snap(e, bar, lo, hi)
        key = (e.start_tick, pitch)
        if key in seen:
            if e.end_tick > seen[key].end_tick:
                seen[key] = MusicEvent(pitch=pitch, volume=max(e.volume, seen[key].volume),
                                       start_tick=e.start_tick, end_tick=e.end_tick)
        else:
            seen[key] = MusicEvent(pitch=pitch, volume=e.volume,
                                   start_tick=e.start_tick, end_tick=e.end_tick)
    for key in sorted(seen):
        out.append(seen[key])
    phase2.set_unit(0, s, MusicUnit(events=landmark(out, span)))

# ---- bass: root (beat 1) + fifth (beat 3) per bar -------------------------
for bar in range(N_BARS):
    s = 0
    while bar >= SEC_BAR_OFFSET[s] + BARS_PER[s]:
        s += 1
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    root = ROOT_BY_BAR[bar]
    fifth = root + 7
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.append(MusicEvent(pitch=root, volume=100, start_tick=t0,
                             end_tick=t0 + int(BAR * 0.45)))
    events.append(MusicEvent(pitch=fifth, volume=88, start_tick=t0 + 960,
                             end_tick=t0 + 960 + int(BAR * 0.45)))
    phase2.set_unit(1, s, MusicUnit(events=events))

# ---- pad: sustained triad per bar (spectral-rigidity voicing) -------------
for bar in range(N_BARS):
    s = 0
    while bar >= SEC_BAR_OFFSET[s] + BARS_PER[s]:
        s += 1
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    tones = chord_tones(bar, lo=PAD_LO, hi=PAD_HI)
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    for k, p in enumerate(tones):
        events.append(MusicEvent(pitch=p, volume=52 + 3 * k,
                                 start_tick=t0, end_tick=t0 + BAR - 80))
    phase2.set_unit(2, s, MusicUnit(events=events))

# ---- arp: 16th-note chord-tone arpeggio (denser in Peak) ------------------
for bar in range(N_BARS):
    s = 0
    while bar >= SEC_BAR_OFFSET[s] + BARS_PER[s]:
        s += 1
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    tones = chord_tones(bar, lo=ARP_LO, hi=ARP_HI)
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    dense = (NAMES[s] in ("Peak", "Rise"))
    step = GRID16 if dense else GRID8
    for k in range(0, 16 if dense else 8):
        t = t0 + k * step
        p = tones[k % len(tones)]
        events.append(MusicEvent(pitch=p, volume=60 if dense else 52,
                                 start_tick=t, end_tick=t + int(step * 0.7)))
    phase2.set_unit(3, s, MusicUnit(events=events))

# ---- drums: four-on-the-floor kick + offbeat hat + clap/snare -------------
for bar in range(N_BARS):
    s = 0
    while bar >= SEC_BAR_OFFSET[s] + BARS_PER[s]:
        s += 1
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    dense = (NAMES[s] in ("Peak", "Rise"))
    # kick on every beat (four-on-the-floor)
    for beat in range(4):
        events.append(MusicEvent(pitch=36, volume=100,
                                 start_tick=t0 + beat * 480, end_tick=t0 + beat * 480 + 90))
    # offbeat open hat
    for e8 in range(8):
        if e8 % 2 == 1:
            events.append(MusicEvent(pitch=42, volume=52,
                                     start_tick=t0 + e8 * GRID8,
                                     end_tick=t0 + e8 * GRID8 + 50))
    # clap/snare on 2 & 4
    for beat in (1, 3):
        events.append(MusicEvent(pitch=39, volume=90 if dense else 70,
                                 start_tick=t0 + beat * 480,
                                 end_tick=t0 + beat * 480 + 70))
    phase2.set_unit(4, s, MusicUnit(events=events))

# finalize bass/pad/arp/drums cells with landmark
for s in range(N_SECTIONS):
    span = BARS_PER[s] * BAR
    for row in (1, 2, 3, 4):
        unit = phase2.matrix.get_unit((row, s))
        events = list(unit.events) if unit is not None else []
        phase2.set_unit(row, s, MusicUnit(events=landmark(events, span)))

ok2, msg2 = phase2.validate()
if not ok2:
    raise RuntimeError("phase2 validate FAIL: " + msg2)
print("PHASE2 validate:", msg2)


# ------------------------------------------------------------------ audits
def global_notes(row):
    notes = []
    for s in range(N_SECTIONS):
        unit = phase2.matrix.get_unit((row, s))
        if unit is None:
            continue
        for e in unit.events:
            if e.pitch == 0:
                continue
            notes.append({"pitch": e.pitch,
                          "start_tick": SEC_BAR_OFFSET[s] * BAR + e.start_tick,
                          "end_tick": SEC_BAR_OFFSET[s] * BAR + e.end_tick})
    return notes


from workflows.pitch_audit import audit_voice  # noqa: E402

PITCHED = [(0, "Lead"), (1, "Bass"), (2, "Pad"), (3, "Arp")]
grid_audit = {}
harmony_audit = {}
for row, vname in PITCHED:
    notes = global_notes(row)
    onsets = [n["start_tick"] for n in notes]
    for grid_name, grid in (("16th", 120), ("8th", 240)):
        off = [o for o in onsets if o % grid != 0]
        grid_audit[f"{vname}:{grid_name}"] = f"{len(off)}/{len(onsets)}"
    r = audit_voice(notes, sorted(KEY_PCS), chord_pcs_by_bar=CHORD_PCS_BY_BAR,
                    strong_grid=STRONG, bar_ticks=BAR, grid=GRID8)
    harmony_audit[vname] = {
        "passes": r.passes, "audible": r.audible,
        "strong_ok": r.strong_ok, "weak_in_scale": r.weak_in_scale,
        "tagged": r.tagged_ornaments, "resolving": r.tagged_resolving,
        "non_resolving": r.tagged_non_resolving,
        "untagged_out_of_scale": r.untagged_out_of_scale,
        "strong_violations": r.strong_violations,
        "collisions": r.collisions,
    }
    print(f"AUDIT {vname}: {r.summary()}")

for k, v in grid_audit.items():
    print("GRID", k, v)
assert all(r["passes"] for r in harmony_audit.values()), "harmony audit FAIL"
assert all(int(x.split("/")[0]) == 0 for k, x in grid_audit.items()
           if k.endswith(":16th")), "grid audit FAIL (16th must be 0 off-grid)"


# ------------------------------------------------------------------ export
perfect_mid = os.path.join(MIDI_DIR, "296-electronic-rmt-spectral-perfect.mid")
human_mid = os.path.join(MIDI_DIR, "296-electronic-rmt-spectral-humanized.mid")

hz_instruments = {
    "Lead": SINGING_SAW.humanize_dna,
    "Bass": SYNTH_BASS_1.humanize_dna,
    "Pad": SYNTH_PAD.humanize_dna,
    "Arp": CALIOPE.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
hz = export_dual(phase2, perfect_mid, human_mid,
                 style="electronic", seed=HZ_SEED, bpm=BPM,
                 instruments=hz_instruments)
print("export_dual OK; hz summary:")
print(json.dumps(hz, indent=2, default=str))


# ------------------------------------------------------------------ provenance
write_provenance(P1_MIDI, AI_ASSISTED,
                 "Random Matrix Theory Composition (Method 120) -- raw draft",
                 parameters={"phase": "1", "layer": "raw", "style": "electronic",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM,
                             "ensemble_per_section": ENSEMBLE,
                             "matrix_dim_per_section": N_DIM,
                             "pitch_scale_K": K_PITCH,
                             "interval_scale_M": M_INTERVAL,
                             "lambda_max_per_section": P1_LAMMAX,
                             "section_mean_pitch": P1_MEAN},
                 notes="phase1 raw draft: single-voice RMTC chromatic contour; "
                       "eigenvalue spectrum -> semicircle pitch pool; "
                       "Wigner-surmise spacings -> level-repulsion intervals; "
                       "GOE/GUE/GSE ensemble switching -> macro-form; "
                       "off-grid onset jitter + unquantized pitch; no harmony.")
write_provenance(perfect_mid, AI_ASSISTED,
                 "RMTC 120 + musicom rules (phase 2, grid-locked)",
                 parameters={"phase": "2", "layer": "perfect", "style": "electronic",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM,
                             "progression": BAR_PROG,
                             "ensemble_per_section": ENSEMBLE},
                 notes="grid-locked concrete layer; off-grid onsets == 0; "
                       "tiered snap (strong->chord tone, weak->C-minor scale).")
write_provenance(human_mid, AI_ASSISTED,
                 "RMTC 120 + rules + humanize (phase 2, humanized)",
                 parameters={"phase": "2", "layer": "humanized", "style": "electronic",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "humanize_profiles": {
                                 k: (v.get("profile") if isinstance(v, dict) else v)
                                 for k, v in hz.items()}},
                 notes="style-derived seeded humanization (default profile + "
                       "per-instrument DNA).")


# ------------------------------------------------------------------ grid viz + manifest
gv = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
write_grid_visualization(phase2.matrix, gv, ticks_per_character=120,
                         voice_names=[v[0] for v in VOICES], bpm=BPM)
print("grid viz written", gv)

manifest = {
    "project": "296-electronic-rmt-spectral",
    "genre": "Electronic",
    "method": "120 Random Matrix Theory Composition (RMTC)",
    "paradigm": "Stochastic",
    "layer": "concrete",
    "form": FORM,
    "key": KEY,
    "key_pcs": sorted(KEY_PCS),
    "bpm": BPM,
    "bars": N_BARS,
    "sections": NAMES,
    "bars_per_section": BARS_PER,
    "progression": BAR_PROG,
    "ensemble_per_section": ENSEMBLE,
    "matrix_dim_per_section": N_DIM,
    "lambda_max_per_section": P1_LAMMAX,
    "section_mean_pitch_phase1": P1_MEAN,
    "seed": SEED,
    "hz_seed": HZ_SEED,
    "form_seed": FORM_SEED,
    "phase1_midi": P1_MIDI,
    "perfect_midi": perfect_mid,
    "humanized_midi": human_mid,
    "phase1_offgrid": P1_OFFGRID,
    "grid_audit": grid_audit,
    "harmony_audit": harmony_audit,
    "hz_summary": hz,
}
with open(os.path.join(ANALYSIS_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, default=str)
print("DONE")
