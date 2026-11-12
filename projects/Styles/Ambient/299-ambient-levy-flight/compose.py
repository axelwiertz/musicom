# -*- coding: utf-8 -*-
"""299-ambient-levy-flight -- Ambient / Method 053 Levy Flight Composition (LFC).

Stochastic, concrete layer.

Two-phase architecture:
  Phase 1: raw generative draft. A single melodic voice walks a Levy flight --
           heavy-tailed (power-law) step-length distribution. Clusters of tiny
           steps = conjunct motif cells; rare long jumps = dramatic register
           flights (the defining fingerprint of a Levy walk vs Gaussian random
           walk). Section macro-form is driven by the tail index alpha:
             - low  alpha (1.3) = heavy tails -> sparse, register-shattering jumps
             - high alpha (2.5) = near-Gaussian -> dense small-step clusters
           Onsets carry off-grid jitter; pitch is unquantized chromatic.
           Single voice, NO harmony/bass/pad/drums.

  Phase 2: musicom rules post-process:
            1. grid-lock the lead to the 8th grid (078 rule).
            2. tiered snap (ScaleQuantizer root=A + classify_weight):
               strong beats -> bar's chord tone, weak -> A-minor scale tone.
            3. texture: synth-bass root/fifth, warm-pad sustained triad,
               vibraphone arp (sparse), soft ambient drums.
            4. zero-drift landmark + validate() on BOTH phases.
            5. export_dual -> -perfect.mid + -humanized.mid.

Engine only. mido is used READ-ONLY in a separate verify step.

A natural minor: pitch classes {0,2,4,5,7,9,11} = A B C D E F G.
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
    FLUTE, WARM_PAD, SYNTH_BASS_1, VIBRAPHONE, DRUM_KIT,
)

SEED = 20261111
HZ_SEED = SEED * 13 + 299
FORM_SEED = SEED * 10 + 7

# ------------------------------------------------------------------ project
PROJ = "/opt/data/projects/Styles/Ambient/299-ambient-levy-flight"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

# ------------------------------------------------------------------- concept
BPM = 72
TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
GRID16 = 120
GRID8 = 240

_form = pick_form("ambient", rng=np.random.default_rng(FORM_SEED))
while _form in ("loop", "loop4", "loop16"):
    _form = pick_form("ambient", rng=np.random.default_rng(FORM_SEED + 1))
FORM = _form
NAMES, BARS_PER = form_to_sections(FORM)
N_SECTIONS = len(NAMES)
N_BARS = sum(BARS_PER)

SEC_BAR_OFFSET = []
acc = 0
for b in BARS_PER:
    SEC_BAR_OFFSET.append(acc)
    acc += b

# A natural minor
KEY = "A natural minor"
KEY_PCS = {0, 2, 4, 5, 7, 9, 11}
TONIC = 57                      # A3
SCALE_ROOT = 57

# ------------------------------------------------------------------- harmony
# i - VI - III - VII  (Am - F - C - G : classic ambient/dark progression)
CHORDS = {
    "i":   {"pcs": {9, 0, 4},   "root": 45, "name": "Am"},
    "VI":  {"pcs": {5, 9, 0},   "root": 41, "name": "F"},
    "III": {"pcs": {0, 4, 7},   "root": 36, "name": "C"},
    "VII": {"pcs": {7, 11, 2},  "root": 43, "name": "G"},
}
_CYCLE = ["i", "VI", "III", "VII"]
BAR_PROG = []
for s in range(N_SECTIONS):
    n = BARS_PER[s]
    if NAMES[s] == "Resolve":
        BAR_PROG += ["i", "VII", "VI", "i"]
    else:
        BAR_PROG += _CYCLE * (n // 4) + _CYCLE[:n % 4]
assert len(BAR_PROG) == N_BARS, (len(BAR_PROG), N_BARS)

CHORD_PCS_BY_BAR = {bar: sorted(CHORDS[BAR_PROG[bar]]["pcs"])
                    for bar in range(N_BARS)}
ROOT_BY_BAR = {bar: CHORDS[BAR_PROG[bar]]["root"] for bar in range(N_BARS)}

# per-section Levy tail index (macro-form driver)
ALPHA = {"Intro": 1.3, "Build": 1.6, "Rise": 1.9,
         "Peak": 1.4, "Resolve": 2.5}
# any section name fallback (form may differ)
_DEFAULT_ALPHA = {"Intro": 1.3, "Build": 1.6, "Rise": 1.9, "Peak": 1.4,
                  "Resolve": 2.5, "S1": 1.3, "S2": 1.6, "S3": 1.9,
                  "S4": 1.4, "S5": 2.0, "S6": 2.5, "Blues": 1.6, "A": 1.6,
                  "B": 1.9, "Verse": 1.6, "Chorus": 1.4, "Head": 1.6,
                  "Solo1": 1.4, "Solo2": 1.4, "Falseta": 1.4, "Letra": 1.6,
                  "Cierre": 2.2, "Break": 1.4, "Drop": 1.4, "Outro": 2.5,
                  "Verse2": 1.9, "Chorus2": 1.4, "Bridge": 2.0, "Loop": 1.6}
ALPHA = {n: _DEFAULT_ALPHA.get(n, 1.6) for n in NAMES}

# voice registers
LEAD_LO, LEAD_HI = 60, 88
ARP_LO, ARP_HI = 60, 84
PAD_LO, PAD_HI = 57, 79
BASS_LO, BASS_HI = 30, 55


def chord_tones(bar, lo, hi):
    tones = set()
    for base in (36, 48, 60, 72, 84, 96):
        for pc in CHORD_PCS_BY_BAR[bar]:
            p = base + pc
            if lo <= p <= hi:
                tones.add(p)
    return sorted(tones)


def scale_tones(lo, hi):
    return [p for p in range(lo, hi + 1) if p % 12 in KEY_PCS]


# ------------------------------------------------------------------- Levy
def levy_steps(n, alpha, rng):
    """Heavy-tailed step magnitudes: Pareto with tail index alpha.

    mag = (1 - U)^(-1/alpha), U ~ Uniform(0,1].
    alpha small -> heavy tail (rare huge jumps); alpha large -> light tail.
    """
    u = rng.random(n)
    u[u >= 1.0] = 0.999999
    return (1.0 - u) ** (-1.0 / alpha)


def raw_levy_contour(span_ticks, alpha, seed, tonic=TONIC):
    """Single-voice raw draft: a Levy walk in pitch space.

    - step direction = +/-1, magnitude = Pareto (heavy tail)
    - small magnitudes (most mass) -> 1-2 semitone steps = conjunct motif cells
    - rare huge magnitudes -> register flights (clipped at 36..96)
    - off-grid onset jitter + unquantized pitch (by design).
    """
    rng = np.random.default_rng(seed)
    n_slots = max(1, int(span_ticks // GRID8))
    mags = levy_steps(n_slots, alpha, rng)
    dirs = rng.choice([-1.0, 1.0], n_slots)
    events = []
    pitch = tonic
    onset = 0.0
    for i in range(n_slots):
        interval = int(round(dirs[i] * mags[i]))
        pitch = int(np.clip(pitch + interval, 36, 96))
        st = int(round(onset + rng.normal(0, 18)))
        st = max(0, min(st, span_ticks - 40))
        dur = int(round(230 + rng.normal(0, 40)))
        en = min(st + dur, span_ticks - 1)
        if en <= st:
            en = st + 1
        vel = int(np.clip(74 + rng.normal(0, 12), 45, 100))
        events.append(MusicEvent(pitch=pitch, volume=vel,
                                 start_tick=st, end_tick=en))
        onset += GRID8 + rng.normal(0, 20)
    return events


# ------------------------------------------------------------ PHASE 1: raw
phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
phase1.create_matrix(num_voices=1, num_sections=N_SECTIONS)
phase1.add_voice("Levy_Raw", program=FLUTE.midi_program, channel=0)

P1_OFFGRID = 0
P1_MEAN = {}
P1_MAXLEAP = {}
for s, name in enumerate(NAMES):
    phase1.add_section(name, bars=BARS_PER[s])
    span = BARS_PER[s] * BAR
    evs = raw_levy_contour(span, ALPHA[name], SEED + s)
    if not any(e.pitch == 0 and e.end_tick == span for e in evs):
        evs.append(MusicEvent(pitch=0, volume=0, start_tick=span - 1,
                              end_tick=span))
    P1_OFFGRID += sum(1 for e in evs if e.pitch != 0 and e.start_tick % GRID16 != 0)
    pitches = [e.pitch for e in evs if e.pitch != 0]
    P1_MEAN[name] = round(float(np.mean(pitches)), 2) if pitches else 0.0
    diffs = [abs(pitches[i] - pitches[i - 1])
             for i in range(1, len(pitches))]
    P1_MAXLEAP[name] = max(diffs) if diffs else 0
    phase1.set_unit(0, s, MusicUnit(events=evs))

ok1, msg1 = phase1.validate()
if not ok1:
    raise RuntimeError("phase1 validate FAIL: " + msg1)
P1_MIDI = os.path.join(MIDI_DIR, "299-ambient-levy-flight-phase1.mid")
phase1.to_midi(P1_MIDI)
assert os.path.getsize(P1_MIDI) > 40
print("PHASE1 validate:", msg1, "| off-grid onsets:", P1_OFFGRID)
print("PHASE1 per-section mean pitch:", P1_MEAN)
print("PHASE1 per-section max leap:", P1_MAXLEAP)


# ------------------------------------------------------------ PHASE 2: rules
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
VOICES = [
    ("Lead", FLUTE.midi_program, 0),          # Levy contour lead
    ("Pad", WARM_PAD.midi_program, 1),        # sustained triad
    ("Bass", SYNTH_BASS_1.midi_program, 2),   # root/fifth
    ("Arp", VIBRAPHONE.midi_program, 3),      # sparse chord arpeggio
    ("Drums", 0, 9),                           # soft ambient kit
]
N_V = len(VOICES)
phase2.create_matrix(num_voices=N_V, num_sections=N_SECTIONS)
for name, prog, ch in VOICES:
    phase2.add_voice(name, program=prog, channel=ch)
for i, name in enumerate(NAMES):
    phase2.add_section(name, bars=BARS_PER[i])

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


def lead_register(name):
    if name in ("Peak", "Drop", "Solo1", "Solo2"):
        return 60, 96
    if name in ("Rise", "Build", "S2", "S3"):
        return 60, 90
    return LEAD_LO, LEAD_HI


# ---- lead: Levy contour, grid-locked + tiered snap -----------------------
for s, name in enumerate(NAMES):
    span = BARS_PER[s] * BAR
    evs = raw_levy_contour(span, ALPHA[name], SEED + s)
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


def sec_of_bar(bar):
    s = 0
    while bar >= SEC_BAR_OFFSET[s] + BARS_PER[s]:
        s += 1
    return s


# ---- bass: root (beat 1) + fifth (beat 3), sustained ---------------------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    root = ROOT_BY_BAR[bar]
    fifth = root + 7
    unit = phase2.matrix.get_unit((1, s))
    events = list(unit.events) if unit is not None else []
    events.append(MusicEvent(pitch=root, volume=96, start_tick=t0,
                             end_tick=t0 + int(BAR * 0.9)))
    events.append(MusicEvent(pitch=fifth, volume=80, start_tick=t0 + 960,
                             end_tick=t0 + 960 + int(BAR * 0.85)))
    phase2.set_unit(1, s, MusicUnit(events=events))


# ---- pad: sustained triad per bar ----------------------------------------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    tones = chord_tones(bar, lo=PAD_LO, hi=PAD_HI)
    unit = phase2.matrix.get_unit((2, s))
    events = list(unit.events) if unit is not None else []
    for k, p in enumerate(tones):
        events.append(MusicEvent(pitch=p, volume=48 + 3 * k,
                                 start_tick=t0, end_tick=t0 + BAR - 60))
    phase2.set_unit(2, s, MusicUnit(events=events))


# ---- arp: sparse 8th-note chord arpeggio (denser in Peak/Rise) -----------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    tones = chord_tones(bar, lo=ARP_LO, hi=ARP_HI)
    unit = phase2.matrix.get_unit((3, s))
    events = list(unit.events) if unit is not None else []
    dense = (NAMES[s] in ("Peak", "Rise", "Build", "Drop", "S3", "S4"))
    for k in range(8):
        if not dense and k % 2 == 1:
            continue
        t = t0 + k * GRID8
        p = tones[k % len(tones)]
        events.append(MusicEvent(pitch=p, volume=52 if dense else 44,
                                 start_tick=t, end_tick=t + int(GRID8 * 0.6)))
    phase2.set_unit(3, s, MusicUnit(events=events))


# ---- drums: soft ambient kick + offbeat tick (sparse, low velocity) ------
for bar in range(N_BARS):
    s = sec_of_bar(bar)
    t0 = (bar - SEC_BAR_OFFSET[s]) * BAR
    unit = phase2.matrix.get_unit((4, s))
    events = list(unit.events) if unit is not None else []
    dense = (NAMES[s] in ("Peak", "Rise", "Build"))
    # soft kick on beat 1 (and 3 only when dense)
    events.append(MusicEvent(pitch=36, volume=58 if dense else 48,
                             start_tick=t0, end_tick=t0 + 80))
    if dense:
        events.append(MusicEvent(pitch=36, volume=52, start_tick=t0 + 960,
                                 end_tick=t0 + 960 + 80))
    # airy offbeat tick (closed hat, very soft)
    for e8 in range(8):
        if e8 % 2 == 1:
            events.append(MusicEvent(pitch=42, volume=30,
                                     start_tick=t0 + e8 * GRID8,
                                     end_tick=t0 + e8 * GRID8 + 40))
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
perfect_mid = os.path.join(MIDI_DIR, "299-ambient-levy-flight-perfect.mid")
human_mid = os.path.join(MIDI_DIR, "299-ambient-levy-flight-humanized.mid")

hz_instruments = {
    "Lead": FLUTE.humanize_dna,
    "Pad": WARM_PAD.humanize_dna,
    "Bass": SYNTH_BASS_1.humanize_dna,
    "Arp": VIBRAPHONE.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
hz = export_dual(phase2, perfect_mid, human_mid,
                 style="ambient", seed=HZ_SEED, bpm=BPM,
                 instruments=hz_instruments)
print("export_dual OK; hz summary:")
print(json.dumps(hz, indent=2, default=str))


# ------------------------------------------------------------------ provenance
write_provenance(P1_MIDI, AI_ASSISTED,
                 "Levy Flight Composition (Method 053) -- raw draft",
                 parameters={"phase": "1", "layer": "raw", "style": "ambient",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM,
                             "alpha_per_section": ALPHA,
                             "section_mean_pitch": P1_MEAN,
                             "section_max_leap": P1_MAXLEAP},
                 notes="phase1 raw draft: single-voice Levy-walk chromatic contour; "
                       "Pareto tail-index alpha -> heavy-tailed steps (clusters of "
                       "conjunct motif cells + rare register flights); per-section "
                       "alpha schedule -> macro-form; off-grid onset jitter + "
                       "unquantized pitch; no harmony.")
write_provenance(perfect_mid, AI_ASSISTED,
                 "Levy Flight 053 + musicom rules (phase 2, grid-locked)",
                 parameters={"phase": "2", "layer": "perfect", "style": "ambient",
                             "key": KEY, "bpm": BPM, "seed": SEED,
                             "humanize_seed": HZ_SEED,
                             "sections": N_SECTIONS, "bars": N_BARS,
                             "form": FORM,
                             "progression": BAR_PROG,
                             "alpha_per_section": ALPHA},
                 notes="grid-locked concrete layer; off-grid onsets == 0; "
                       "tiered snap (strong->chord tone, weak->A-minor scale).")
write_provenance(human_mid, AI_ASSISTED,
                 "Levy Flight 053 + rules + humanize (phase 2, humanized)",
                 parameters={"phase": "2", "layer": "humanized", "style": "ambient",
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
    "project": "299-ambient-levy-flight",
    "genre": "Ambient",
    "method": "053 Levy Flight Composition (LFC)",
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
    "alpha_per_section": ALPHA,
    "section_mean_pitch_phase1": P1_MEAN,
    "section_max_leap_phase1": P1_MAXLEAP,
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