# -*- coding: utf-8 -*-
"""269-techno-contour-theory -- Method 095 Contour Theory Composition (CTC).

Two-phase architecture, engine-only (structures + unitmatrix_composer +
scale_quantizer tiered snap + workflows.humanize.export_dual + provenance).

METHOD 095 (ABSTRACT -> concrete interpretation): Contour Theory Composition.
A melodic contour (CSEG) is the SHAPE of a melody -- an ordered sequence of
pitch positions described by up/down/same relations, independent of exact
pitch. The abstract layer holds a contour CLASS (prime P + the I/R/RI
transformations: Inversion = rank -> maxrank-rank, Retrograde = reverse,
RI = both), forming a small ContourNetwork. The concrete layer maps each rank
to a scale degree (here: A-natural-minor pentatonic A C D E G) and registers
it. Phase 1 walks the contour network as an unquantized single-voice draft
(off-grid onsets + octave drift); Phase 2 grid-locks to 16ths, applies the
tiered weight-aware snap (strong -> in-scale AND in-chord, weak -> in-scale),
and builds a minimal-techno texture (clavi contour lead + pad + synth bass +
4-on-floor drums). Dual export (perfect + humanized).

FORM: intro-break-drop-outro (24 bars) -- the style-hinted canonical techno
form (pick_form("Techno") with loop_prob=0).
"""
import json
import random
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_GENERATED
from workflows.humanize import export_dual
from sound.synthesis.scale_quantizer import ScaleQuantizer, classify_weight
from visualization.grid import write_grid_visualization

# ---- instrument registry (source of truth) ---------------------------------
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import CLAVI, SYNTH_PAD, SYNTH_BASS_1, DRUM_KIT  # noqa: E402

# ---- concept ---------------------------------------------------------------
GENRE = "Techno"
STYLE = "Techno"
NAME = "269-techno-contour-theory"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 9                        # A
KEY_NAME = "A natural minor (aeolian)"
SCALE_PCS = [9, 11, 0, 2, 4, 5, 7]     # A B C D E F G
PENTA = [9, 0, 2, 4, 7]                # A C D E G (contour rank -> pc)
BPM = 128
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = 480
SEED = 20261026
STRONG = (0, 960)                # beats 1 & 3

# ---- form (intro-break-drop-outro, 24 bars) --------------------------------
SECTIONS = [("Intro", 4), ("Break", 8), ("Drop", 8), ("Outro", 4)]
TOTAL_BARS = sum(b for _, b in SECTIONS)
SECTION_START_BAR = {}
_acc = 0
for _n, _b in SECTIONS:
    SECTION_START_BAR[_n] = _acc
    _acc += _b

# ---- harmony: 4-bar cycle  Am  F  G  Am  (i bVI bVII i) --------------------
CHORD_LABELS = ["i", "bVI", "bVII", "i"]
CHORD_PCS = {0: [9, 0, 4], 1: [5, 9, 0], 2: [7, 11, 2], 3: [9, 0, 4]}
BASS_ROOT_MIDI = {0: 45, 1: 41, 2: 43, 3: 45}   # A2 F2 G2 A2


def chord_pcs(bar):
    return CHORD_PCS[bar % 4]


def chord_tones_midi(pcs, lo, hi):
    return sorted(p for p in range(lo, hi + 1) if p % 12 in set(pcs))


# ============================================================================
# METHOD 095 -- Contour Theory: contour class (P / I / R / RI)
# ============================================================================
# Base contour: 6 points, ranks 0..4, CAS (contour adjacency series) = up down
# up up down  ->  [+, -, +, +, -]
BASE_CSEG = [0, 3, 1, 2, 4, 1]
MAXRANK = 4


def invert_cseg(c):
    return [MAXRANK - r for r in c]


def retro_cseg(c):
    return list(reversed(c))


CONTOUR_CLASS = {
    "P":  BASE_CSEG,                    # prime      [+, -, +, +, -]
    "I":  invert_cseg(BASE_CSEG),       # inversion  [-, +, -, -, +]
    "R":  retro_cseg(BASE_CSEG),        # retrograde [+, -, -, +, -]
    "RI": retro_cseg(invert_cseg(BASE_CSEG)),  # retro-inv [-, +, +, -, +]
}

# rank -> MIDI pitch in lead register (A3 C4 D4 E4 G4)
RANK_PITCH = [57, 60, 62, 64, 67]


def rank_to_pitch(rank, octave=0):
    return RANK_PITCH[rank] + 12 * octave


def contour_plan():
    """Return [(abs_bar, rank, slot8th, octave)] across all 24 bars."""
    plan = []
    for name, bars in SECTIONS:
        sbar = SECTION_START_BAR[name]
        if name == "Intro":
            members, octave = ["P"], 0
        elif name == "Break":
            members, octave = ["P", "I", "R", "RI"], 0
        elif name == "Drop":
            members, octave = ["RI", "R", "I", "P"], 1   # register rise
        else:  # Outro
            members, octave = ["I", "P"], 0
        for bi in range(bars):
            member = members[bi % len(members)]
            cseg = CONTOUR_CLASS[member]
            for si, rank in enumerate(cseg):
                plan.append((sbar + bi, rank, si, octave))
    return plan


PLAN = contour_plan()

# ============================================================================
# PHASE 1 -- RAW CONTOUR DRAFT (single clavi voice, off-grid, octave drift)
# ============================================================================
rng1 = random.Random(SEED + 1)
phase1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
phase1.create_matrix(num_voices=1, num_sections=1)
phase1.add_voice("ContourRaw", program=CLAVI.midi_program, channel=0)
phase1.add_section("Raw", bars=TOTAL_BARS)

SPAN = TOTAL_BARS * BAR
raw_events = []
prev_end = 0
for (bar, rank, si, octave) in PLAN:
    if rng1.random() < 0.18:          # sparse rests (techno space)
        continue
    st = bar * BAR + si * EIGHTH + rng1.randint(-40, 41)   # off-grid jitter
    st = max(0, min(st, SPAN - 1))
    drift = rng1.choice([-1, 0, 0, 0, 0, 1])               # octave register drift
    p = rank_to_pitch(rank, octave + drift)
    p = max(45, min(84, p))
    if st < prev_end - 10:
        st = prev_end + 10
    dur = int(EIGHTH * (0.6 + 0.6 * rng1.random()))
    en = min(st + dur, SPAN)
    if en > st:
        raw_events.append(MusicEvent(pitch=p, volume=int(72 + 24 * rng1.random()),
                                     start_tick=st, end_tick=en))
        prev_end = en
raw_events.append(MusicEvent(0, 0, SPAN - 1, SPAN))        # landmark
phase1.set_unit(0, 0, MusicUnit(events=sorted(raw_events, key=lambda e: e.start_tick)))

ok1, msg1 = phase1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
phase1.to_midi(str(midi1))
write_provenance(str(midi1), AI_GENERATED, f"musicom {NAME}",
                 sources=["methods_db:095 Contour Theory Composition",
                          f"style:{STYLE}", "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "contour_class": CONTOUR_CLASS,
                             "rank_pitch": RANK_PITCH,
                             "notes": "contour network P/I/R/RI -> off-grid raw clavi"})
print(f"phase1 raw notes: {len([e for e in raw_events if e.pitch > 0])} "
      f"; midi {midi1.stat().st_size} bytes")

# ============================================================================
# PHASE 2 -- RULES (grid-lock + tiered weight-aware snap + techno texture)
# ============================================================================
sq = ScaleQuantizer(root=57, scale="minor")      # A natural minor


def quantize_to_grid(events, grid=SIXTEENTH):
    q = []
    for e in events:
        if e.pitch == 0:
            q.append(e)
            continue
        st = int(round(e.start_tick / grid) * grid)
        q.append(MusicEvent(pitch=e.pitch, volume=e.volume,
                            start_tick=st, end_tick=max(st + 1, e.end_tick)))
    return q


VOICES = [
    ("Lead", CLAVI.midi_program, 0),         # contour melody
    ("Pad", SYNTH_PAD.midi_program, 1),      # sustained harmony
    ("Bass", SYNTH_BASS_1.midi_program, 2),  # driving bass
    ("Drums", 0, 9),                          # percussion
]
N_V = len(VOICES)
phase2 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
phase2.create_matrix(num_voices=N_V, num_sections=len(SECTIONS))
for vname, prog, ch in VOICES:
    phase2.add_voice(vname, program=prog, channel=ch)
for name, bars in SECTIONS:
    phase2.add_section(name, bars=bars)

# --- lead (clavi): contour plan -> grid-lock -> tiered snap -----------------
lead_by_section = {name: [] for name, _ in SECTIONS}
for (bar, rank, si, octave) in PLAN:
    name = next(n for n, b in SECTIONS
                if SECTION_START_BAR[n] <= bar < SECTION_START_BAR[n] + b)
    local = (bar - SECTION_START_BAR[name]) * BAR + si * EIGHTH
    lead_by_section[name].append((local, rank, si, octave))

SEC_NAMES = [n for n, _ in SECTIONS]
for name, bars in SECTIONS:
    evs = []
    for (local, rank, si, octave) in lead_by_section[name]:
        raw_pitch = rank_to_pitch(rank, octave)
        abar = SECTION_START_BAR[name] + local // BAR
        ctones = chord_tones_midi(chord_pcs(abar), 57, 79)
        w = classify_weight(local, STRONG, BAR)
        if w == "strong":
            p = sq.tiered_quantize(raw_pitch, "strong", ctones)
        else:
            p = sq.tiered_quantize(raw_pitch, "weak")
        p = max(57, min(79, p))
        evs.append(MusicEvent(pitch=p, volume=86, start_tick=local,
                              end_tick=min(local + EIGHTH - 40, bars * BAR)))
    phase2.set_unit(0, SEC_NAMES.index(name), MusicUnit(events=evs))

# --- pad (synth pad): sustained triad per bar -------------------------------
for name, bars in SECTIONS:
    evs = []
    for bi in range(bars):
        abar = SECTION_START_BAR[name] + bi
        tones = chord_tones_midi(chord_pcs(abar), 48, 72)[:3]
        t0 = bi * BAR
        for k, p in enumerate(tones):
            evs.append(MusicEvent(pitch=p, volume=48 + 4 * k,
                                  start_tick=t0, end_tick=t0 + BAR - 60))
    phase2.set_unit(1, [n for n, _ in SECTIONS].index(name), MusicUnit(events=evs))

# --- bass (synth bass): section-specific techno pattern ---------------------
for name, bars in SECTIONS:
    evs = []
    for bi in range(bars):
        abar = SECTION_START_BAR[name] + bi
        r = BASS_ROOT_MIDI[abar % 4]
        t0 = bi * BAR
        if name == "Intro":
            for off in (0, 960):
                evs.append(MusicEvent(pitch=r, volume=92, start_tick=t0 + off,
                                      end_tick=t0 + off + EIGHTH - 30))
        elif name == "Break":
            for off in (240, 720, 1200, 1680):          # off-beat pump
                evs.append(MusicEvent(pitch=r, volume=90, start_tick=t0 + off,
                                      end_tick=t0 + off + EIGHTH - 30))
        elif name == "Drop":
            for i in range(16):                          # 16th drive, octave on odd
                p = r + 12 if i % 2 else r
                evs.append(MusicEvent(pitch=p, volume=88, start_tick=t0 + i * SIXTEENTH,
                                      end_tick=t0 + i * SIXTEENTH + SIXTEENTH - 20))
        else:  # Outro
            for off in (0, 960):
                evs.append(MusicEvent(pitch=r, volume=84, start_tick=t0 + off,
                                      end_tick=t0 + off + EIGHTH - 30))
    phase2.set_unit(2, [n for n, _ in SECTIONS].index(name), MusicUnit(events=evs))

# --- drums (ch9): 4-on-floor techno -----------------------------------------
KICK, CLAP, SNARE, CLHAT, OPENHAT = 36, 39, 38, 42, 46
for name, bars in SECTIONS:
    evs = []
    for bi in range(bars):
        t0 = bi * BAR
        if name == "Intro":
            for kb in (0, 480, 960, 1440):
                evs.append(MusicEvent(pitch=KICK, volume=100, start_tick=t0 + kb,
                                      end_tick=t0 + kb + 120))
            for i in range(8):
                evs.append(MusicEvent(pitch=CLHAT, volume=46, start_tick=t0 + i * EIGHTH,
                                      end_tick=t0 + i * EIGHTH + 60))
        elif name == "Break":
            for kb in (0, 480, 960, 1440):
                evs.append(MusicEvent(pitch=KICK, volume=98, start_tick=t0 + kb,
                                      end_tick=t0 + kb + 120))
            for i in range(8):
                evs.append(MusicEvent(pitch=CLHAT, volume=48, start_tick=t0 + i * EIGHTH,
                                      end_tick=t0 + i * EIGHTH + 60))
            for sb in (480, 1440):
                evs.append(MusicEvent(pitch=CLAP, volume=80, start_tick=t0 + sb,
                                      end_tick=t0 + sb + 120))
            if bi >= bars - 2:                          # snare build
                for i in range(8):
                    evs.append(MusicEvent(pitch=SNARE, volume=70, start_tick=t0 + i * EIGHTH,
                                          end_tick=t0 + i * EIGHTH + 60))
        elif name == "Drop":
            for kb in (0, 480, 960, 1440):
                evs.append(MusicEvent(pitch=KICK, volume=102, start_tick=t0 + kb,
                                      end_tick=t0 + kb + 120))
            for i in range(16):
                evs.append(MusicEvent(pitch=CLHAT, volume=52, start_tick=t0 + i * SIXTEENTH,
                                      end_tick=t0 + i * SIXTEENTH + 40))
            for sb in (480, 1440):
                evs.append(MusicEvent(pitch=CLAP, volume=88, start_tick=t0 + sb,
                                      end_tick=t0 + sb + 120))
            for oh in (240, 720, 1200, 1680):
                evs.append(MusicEvent(pitch=OPENHAT, volume=60, start_tick=t0 + oh,
                                      end_tick=t0 + oh + 90))
        else:  # Outro
            evs.append(MusicEvent(pitch=KICK, volume=90, start_tick=t0,
                                  end_tick=t0 + 120))
            for i in range(8):
                evs.append(MusicEvent(pitch=CLHAT, volume=42, start_tick=t0 + i * EIGHTH,
                                      end_tick=t0 + i * EIGHTH + 60))
    phase2.set_unit(3, [n for n, _ in SECTIONS].index(name), MusicUnit(events=evs))

# ---- normalize every cell to exact section boundary (zero-drift) -----------
def normalize_cell(unit, total_ticks):
    out = []
    for e in unit.events:
        if e.end_tick > total_ticks:
            e.end_tick = total_ticks
        if e.start_tick >= total_ticks:
            e.start_tick = total_ticks - 1
        if e.end_tick > e.start_tick:
            out.append(e)
    if not any(e.pitch == 0 and e.end_tick == total_ticks for e in out):
        out.append(MusicEvent(0, 0, total_ticks - 1, total_ticks))
    return MusicUnit(events=sorted(out, key=lambda e: (e.start_tick, e.pitch)))


for r in range(N_V):
    for name, bars in SECTIONS:
        col = [n for n, _ in SECTIONS].index(name)
        u = phase2.matrix.get_unit((r, col))
        phase2.set_unit(r, col, normalize_cell(u, bars * BAR))

ok2, msg2 = phase2.validate()
assert ok2, f"phase2 validate failed: {msg2}"

# ---- dual-version export (perfect then humanized) --------------------------
hz_seed = SEED + 1
hz_instruments = {
    "Lead": CLAVI.humanize_dna,
    "Pad": SYNTH_PAD.humanize_dna,
    "Bass": SYNTH_BASS_1.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(phase2, str(perfect_path), str(humanized_path),
                 style=STYLE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked"),
                          (humanized_path, "2-humanized", "techno humanized")):
    write_provenance(str(path), AI_GENERATED, f"musicom {NAME}",
                     sources=["methods_db:095 Contour Theory Composition",
                              f"style:{STYLE}", "phase:2 rules"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "contour_class": CONTOUR_CLASS,
                                 "humanize": {k: {kk: vv for kk, vv in v.items() if kk != "profile"}
                                              for k, v in hz.items()},
                                 "note": note})
print("perfect midi:", perfect_path, perfect_path.stat().st_size, "bytes")
print("humanized midi:", humanized_path, humanized_path.stat().st_size, "bytes")

# ---- grid visualization + summary ------------------------------------------
grid_path = ROOT / "Analysis" / "grid_visualization.txt"
write_grid_visualization(phase2.matrix, str(grid_path), ticks_per_character=120)

summary = {
    "project": NAME, "genre": GENRE, "style_key": STYLE,
    "method": "095 Contour Theory Composition (CTC)",
    "layer": "abstract", "paradigm": "Rules-Based (contour class network)",
    "key": KEY_NAME, "tonic_pc": TONIC, "scale_pcs": SCALE_PCS, "bpm": BPM,
    "form": "intro-break-drop-outro",
    "sections": [n for n, _ in SECTIONS],
    "bars_per_section": [b for _, b in SECTIONS], "total_bars": TOTAL_BARS,
    "contour": {
        "base_cseg": BASE_CSEG, "maxrank": MAXRANK,
        "contour_class": CONTOUR_CLASS,
        "rank_pitch": RANK_PITCH,
        "note": "contour class P/I/R/RI (up/down/same shape); rank -> pentatonic degree",
    },
    "chords": {"labels": CHORD_LABELS, "pcs_by_degree": CHORD_PCS,
               "roots_midi": BASS_ROOT_MIDI},
    "voices": [v for v, _, _ in VOICES],
    "instruments": [CLAVI.name, SYNTH_PAD.name, SYNTH_BASS_1.name, DRUM_KIT.name],
    "humanize_seed": hz_seed,
    "humanize_stats": hz,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)
print("chords:", " ".join(CHORD_LABELS), "(cycle)")
print("DONE compose")
