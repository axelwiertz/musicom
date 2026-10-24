# -*- coding: utf-8 -*-
"""263-chanson-frieze-canon -- nightly composition (2026-10-24).

Method 091 -- Coxeter-Conway Frieze Pattern Composition (CCFPC),
layer concrete, paradigm Rules-Based. Style Chanson, D major (ionian),
92 BPM, form verse-chorus (Intro 4 | Verse 8 | Chorus 8 | Verse2 8 |
Chorus2 8 | Outro 4 = 40 bars).

Two-phase architecture:
  Phase 1 (raw): a Coxeter-Conway frieze pattern (period n=16, one 4/4 bar
    of 16ths) built from a fan-triangulation quiddity via Euler continuants.
    The quiddity/interior rows are read column-wise (vertical contour) into a
    SINGLE raw voice: pitch = 60 + frieze_value (chromatic, off-scale by
    design), onsets OFF-GRID (jittered). NO harmony, NO grid.
  Phase 2 (rules): onset snap to 8th/16th grid, tiered pitch quantization
    (strong beat -> in-scale AND in-chord via ScaleQuantizer.tiered_quantize;
    weak -> in-scale only), full 6-voice chanson texture (oboe lead / clarinet
    glide-reflection canon / piano comp / string pad / double bass / light
    drum kit), zero-drift landmark padding. Dual-version export
    (perfect + humanized). Section development via Ptolemy diagonal flips
    (quiddity mutation) across section boundaries.

Engine-only: structures + workflows.unitmatrix_composer + workflows.humanize
+ sound.synthesis.scale_quantizer + workflows.provenance. mido NOT used for
authoring (read-only audits live in verify.py). Instruments from the
importable registry (source of truth).
"""
import json
import random
import sys
from pathlib import Path

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization
from sound.synthesis.scale_quantizer import ScaleQuantizer, classify_weight

# ---- instrument registry (source of truth) ---------------------------------
INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if INSTR_DIR not in sys.path:
    sys.path.insert(0, INSTR_DIR)
from instrument_registry import (  # noqa: E402
    OBOE, CLARINET, PIANO, STRING_ENSEMBLE, DOUBLE_BASS, DRUM_KIT,
)

# ---- concept ---------------------------------------------------------------
GENRE = "Chanson"
NAME = "263-chanson-frieze-canon"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 2                       # D
KEY_NAME = "D major (ionian)"
NAT = [0, 2, 4, 5, 7, 9, 11]    # major (ionian) intervals
SCALE_DEG_PCS = [(TONIC + o) % 12 for o in NAT]     # D E F# G A B C#
SCALE_PCS = set(SCALE_DEG_PCS)
BPM = 92
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = BAR // 4                 # 480
SEED = 20261024
rng = random.Random(SEED)

# ---- form: verse-chorus (40 bars), unique section names for the engine -----
FORM_NAME = "verse-chorus"
FORM = [("Intro", 4), ("Verse", 8), ("Chorus", 8),
        ("Verse2", 8), ("Chorus2", 8), ("Outro", 4)]
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


# ---- harmony: diatonic 7th chords in D major -------------------------------
DEG_NAMES = ["I7", "ii7", "iii7", "IV7", "V7", "vi7", "viiø7"]
DEG_LABELS = ["Dmaj7", "Em7", "F#m7", "Gmaj7", "A7", "Bm7", "C#m7b5"]


def deg_pc(d):
    return (TONIC + NAT[d % 7]) % 12


def chord_pcs_deg(d):
    return frozenset(deg_pc((d + k) % 7) for k in (0, 2, 4, 6))


# per-bar chord degree (40 bars, section-mapped)
CHORD_DEG = (
    [0, 3, 1, 4]                      # Intro: I IV ii V
    + [0, 5, 3, 4, 0, 5, 1, 4]        # Verse: I vi IV V I vi ii V
    + [3, 4, 0, 5, 3, 4, 0, 0]        # Chorus: IV V I vi IV V I I
    + [0, 5, 3, 4, 0, 5, 1, 4]        # Verse2
    + [3, 4, 0, 5, 3, 4, 0, 0]        # Chorus2
    + [3, 4, 0, 0]                    # Outro: IV V I I
)
assert len(CHORD_DEG) == N_BARS, f"chord bars {len(CHORD_DEG)} != {N_BARS}"
CHORD_PCS = [chord_pcs_deg(d) for d in CHORD_DEG]


def bar_deg(b):
    return CHORD_DEG[b]


def pool(deg, floor, ceil):
    pcs = sorted(chord_pcs_deg(deg))
    out = []
    for pc in pcs:
        p = floor + ((pc - floor) % 12)
        while p <= ceil:
            out.append(p)
            p += 12
    return sorted(out)


LEAD_POOL = {b: pool(CHORD_DEG[b], 59, 86) for b in range(N_BARS)}
COUNT_POOL = {b: pool(CHORD_DEG[b], 55, 86) for b in range(N_BARS)}
PIANO_POOL = {b: pool(CHORD_DEG[b], 48, 84) for b in range(N_BARS)}
PAD_POOL = {b: pool(CHORD_DEG[b], 48, 72) for b in range(N_BARS)}
BASS_POOL = {b: pool(CHORD_DEG[b], 28, 48) for b in range(N_BARS)}

# scale quantizer (D major, root D3 = 50)
sq = ScaleQuantizer(root=50, scale="major")
STRONG = (0, 960)


def snap16(t):
    return int(round(t / SIXTEENTH) * SIXTEENTH)


def clamp_scale(p, lo=55, hi=86):
    while p < lo:
        p += 12
    while p > hi:
        p -= 12
    return p


# ============================================================================
# FRIEZE PATTERN (Coxeter-Conway, n = 16 period = one 4/4 bar of 16ths)
# ============================================================================
N = 16


def fan_quiddity(n):
    q = [2] * n
    q[0] = n - 2
    q[1] = 1
    q[n - 1] = 1
    return q


def continuant(xs):
    """Euler continuant K(x1..xk): K()=1, K(x)=x, K(x,y)=xy-1, ..."""
    if not xs:
        return 1
    if len(xs) == 1:
        return xs[0]
    p2, p1 = 1, xs[0]
    for i in range(1, len(xs)):
        cur = xs[i] * p1 - p2
        p2, p1 = p1, cur
    return p1


def frieze_rows(quiddity, n):
    """Rows R_0..R_{n} (R_k[j] = continuant of k consecutive quiddity entries)."""
    return [[continuant([quiddity[(j + i) % n] for i in range(k)])
             for j in range(n)] for k in range(n + 1)]


def frieze_valid(q, n):
    rows = frieze_rows(q, n)
    if any(v != 1 for v in rows[0]):
        return False
    if any(v != 1 for v in rows[n - 2]):
        return False
    if any(v != 0 for v in rows[n - 1]):
        return False
    for k in range(1, n - 1):
        if any(v <= 0 for v in rows[k]):
            return False
    return True


def flip_quiddity(q, rng, n):
    """One Ptolemy diagonal flip (quiddity mutation): remove diagonal (i,j),
    add (i+1,j+1) -> q_i-=1, q_j-=1, q_{i+1}+=1, q_{j+1}+=1."""
    for _ in range(200):
        i = rng.randrange(n)
        dist = rng.choice([d for d in range(2, n - 1)])
        j = (i + rng.choice([dist, -dist])) % n
        if q[i] >= 2 and q[j] >= 2:
            i1, j1 = (i + 1) % n, (j + 1) % n
            nq = list(q)
            nq[i] -= 1
            nq[j] -= 1
            nq[i1] += 1
            nq[j1] += 1
            if all(v >= 1 for v in nq) and frieze_valid(nq, n):
                return nq
    return q


def flip_times(q, rng, n, k):
    out = list(q)
    for _ in range(k):
        out = flip_quiddity(out, rng, n)
    return out


q_base = fan_quiddity(N)
q_verse = flip_times(q_base, rng, N, 1)
q_chorus = flip_times(q_base, rng, N, 2)

SECTION_QUIDDITY = {
    "Intro": q_base, "Verse": q_verse, "Chorus": q_chorus,
    "Verse2": q_verse, "Chorus2": q_chorus, "Outro": q_base,
}
SECTION_FRIEZE = {s: frieze_rows(q, N) for s, q in SECTION_QUIDDITY.items()}

# verify every section frieze is structurally valid
for s, q in SECTION_QUIDDITY.items():
    assert frieze_valid(q, N), f"frieze invalid for section {s}"
    rows = SECTION_FRIEZE[s]
    assert rows[0][0] == 1 and rows[N - 2][0] == 1 and rows[N - 1][0] == 0
print("frieze quiddities:")
for s, q in SECTION_QUIDDITY.items():
    print(f"  {s:9} sum={sum(q):3} {q}")

# mirror-row multiset check (glide-reflection symmetry): R_1 vs R_{n-3}
r1 = SECTION_FRIEZE["Intro"][1]
rm = SECTION_FRIEZE["Intro"][N - 3]
assert sorted(r1) == sorted(rm), "glide-reflection mirror multiset mismatch"
print("glide-reflection mirror (R_1 vs R_{n-3}) value multiset: OK")


# ============================================================================
# PHASE 1 -- RAW FRIEZE DRAFT (single voice, off-grid, chromatic)
# ============================================================================
raw_events = []                 # dicts: start_tick, pitch, velocity, dur
for b in range(N_BARS):
    sname = section_of_bar(b)
    frieze = SECTION_FRIEZE[sname]
    row_idx = 1 + (b % 7)       # cycle interior strata for phrase variety
    for e in range(8):          # 8th-note slots
        v = frieze[row_idx][(2 * e) % N]
        if (v + e) % 3 == 0:
            continue
        onset = b * BAR + e * EIGHTH + rng.randint(12, 55)   # off-grid jitter
        pitch = 60 + v                                       # chromatic
        dur = rng.randint(120, 240)
        vel = 72 + 2 * v
        raw_events.append({"start_tick": onset, "pitch": pitch,
                           "velocity": min(118, vel), "dur": dur})


def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))   # zero-drift landmark
    return u


p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
p1.create_matrix(num_voices=1, num_sections=len(FORM))
p1.add_voice("FriezeRaw", program=OBOE.midi_program, channel=0)
for sname, nbars in FORM:
    p1.add_section(sname, bars=nbars)
for sname, (slen, soff) in SECTION_TICKS.items():
    evs = []
    for e in raw_events:
        if soff <= e["start_tick"] < soff + slen:
            st = e["start_tick"] - soff
            end = min(st + e["dur"], slen - 1)
            evs.append(MusicEvent(pitch=e["pitch"], volume=e["velocity"],
                                  start_tick=st, end_tick=end))
    p1.fill_voice_section("FriezeRaw", sname, unit_from(evs, slen))
ok1, msg1 = p1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
p1.to_midi(str(midi1))
write_provenance(str(midi1), "ai-generated", f"musicom nightly {NAME}",
                 sources=["methods_db:091 Coxeter-Conway Frieze Pattern (CCFPC)",
                          f"style:{GENRE}", "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "form": FORM_NAME,
                             "frieze": {"period": N, "fan_quiddity": q_base,
                                        "verse_quiddity": q_verse,
                                        "chorus_quiddity": q_chorus},
                             "notes": "frieze row/column contour -> chromatic "
                                      "off-grid raw line; Ptolemy flips per section"})
print(f"phase1 raw events={len(raw_events)}")
print("phase1 midi:", midi1, midi1.stat().st_size, "bytes")

# ============================================================================
# PHASE 2 -- RULES POST-PROCESS (grid snap + tiered quant + full chanson texture)
# ============================================================================

def lead_events():
    notes = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        frieze = SECTION_FRIEZE[s]
        row_idx = 1 + (b % 7)
        for e in range(8):
            v = frieze[row_idx][(2 * e) % N]
            if (v + e) % 3 == 0:
                continue
            st = b * BAR + e * EIGHTH
            raw = 60 + v
            w = classify_weight(st, STRONG, BAR)
            if w == "strong":
                p = sq.tiered_quantize(raw, weight="strong",
                                       chord_tones=LEAD_POOL[b])
            else:
                p = clamp_scale(sq.quantize(raw), 59, 86)
            dur = EIGHTH
            vel = 88
            if s in ("Chorus", "Chorus2"):
                dur = min(EIGHTH * 2, dur + SIXTEENTH)
                vel = min(116, vel + 6)
            elif s == "Outro":
                dur = EIGHTH
                vel = 80
            notes.append(MusicEvent(pitch=int(p), volume=int(vel),
                                    start_tick=st,
                                    end_tick=min(st + dur, (b + 1) * BAR - 1)))
    return notes


def counter_events():
    """Clarinet glide-reflection canon: mirrored row (R_{n-2-k}) at the
    off-16ths (phase-shifted call-response against the lead)."""
    notes = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        frieze = SECTION_FRIEZE[s]
        row_idx = 1 + (b % 7)
        mir = N - 2 - row_idx          # glide-reflection partner row
        for e in range(8):
            c = (2 * e + 1) % N        # odd 16th (the "and"s)
            v = frieze[mir][c]
            if (v + e) % 3 == 0:
                continue
            st = b * BAR + (2 * e + 1) * SIXTEENTH
            p = clamp_scale(sq.quantize(60 + v), 55, 84)   # weak: scale only
            notes.append(MusicEvent(pitch=int(p), volume=70,
                                    start_tick=st, end_tick=st + SIXTEENTH))
    return notes


def piano_events():
    """Piano comp: off-beat chord voicings (chanson accompaniment)."""
    evs = []
    for b in range(N_BARS):
        tones = PIANO_POOL[b]
        bar0 = b * BAR
        for st in (bar0 + 3 * EIGHTH, bar0 + 7 * EIGHTH):   # 720, 1680
            for p in tones[:4]:
                evs.append(MusicEvent(pitch=p, volume=60,
                                      start_tick=st, end_tick=st + EIGHTH))
    return evs


def pad_events():
    """String ensemble pad: sustained chord tones in Intro/Chorus/Outro."""
    evs = []
    for b in range(N_BARS):
        if section_of_bar(b) not in ("Intro", "Chorus", "Chorus2", "Outro"):
            continue
        tones = PAD_POOL[b]
        bar0 = b * BAR
        for p in tones[:4]:
            evs.append(MusicEvent(pitch=p, volume=66, start_tick=bar0,
                                  end_tick=bar0 + BAR - 1))
    return evs


def bass_events():
    """Double bass: root on 1&3 (strong), octave syncopation + diatonic
    approach into the next root (weak)."""
    evs = []
    for b in range(N_BARS):
        tones = BASS_POOL[b]
        root = tones[0]
        fifth = min(tones, key=lambda p: abs(p - (root + 7)))
        octv = min(root + 12, 48)
        bar0 = b * BAR
        evs.append(MusicEvent(pitch=root, volume=94, start_tick=bar0,
                              end_tick=bar0 + SIXTEENTH * 3))
        evs.append(MusicEvent(pitch=octv, volume=80,
                              start_tick=bar0 + 720, end_tick=bar0 + 720 + SIXTEENTH))
        evs.append(MusicEvent(pitch=fifth, volume=88, start_tick=bar0 + 960,
                              end_tick=bar0 + 960 + SIXTEENTH * 2))
        next_root = BASS_POOL[(b + 1) % N_BARS][0]
        approach = clamp_scale(sq.quantize(next_root - 1), 28, 48)
        evs.append(MusicEvent(pitch=int(approach), volume=78,
                              start_tick=bar0 + 1680,
                              end_tick=bar0 + 1680 + SIXTEENTH))
    return evs


def drums_events():
    """Light chanson kit (channel 9): soft kick, brush backbeat (side stick),
    tick hi-hat; slightly brighter in chorus."""
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        bar0 = b * BAR
        for e in (1, 3, 5, 7):                       # off-8th hat tick
            st = bar0 + e * EIGHTH
            evs.append(MusicEvent(pitch=42, volume=46,
                                  start_tick=st, end_tick=st + SIXTEENTH))
        for st in (bar0, bar0 + 960):                # soft kick 1 & 3
            evs.append(MusicEvent(pitch=36, volume=72,
                                  start_tick=st, end_tick=st + SIXTEENTH))
        for st in (bar0 + 480, bar0 + 1440):         # brush backbeat 2 & 4
            evs.append(MusicEvent(pitch=37, volume=58,
                                  start_tick=st, end_tick=st + SIXTEENTH))
        if s in ("Chorus", "Chorus2"):               # open hat lift
            evs.append(MusicEvent(pitch=46, volume=54,
                                  start_tick=bar0 + 1680,
                                  end_tick=bar0 + 1680 + SIXTEENTH))
    return evs


def finalize(events):
    out = []
    for e in events:
        if e.pitch == 0:
            out.append(e)
            continue
        st = snap16(e.start_tick)
        out.append(MusicEvent(pitch=int(e.pitch), volume=int(e.volume),
                              start_tick=st, end_tick=max(st + 1, e.end_tick)))
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


lead_q = finalize(lead_events())
count_q = finalize(counter_events())
piano_q = finalize(piano_events())
pad_q = finalize(pad_events())
bass_q = finalize(bass_events())
drums_q = drums_events()

VOICES = [
    ("Oboe", OBOE.midi_program, 0),
    ("Clarinet", CLARINET.midi_program, 1),
    ("Piano", PIANO.midi_program, 2),
    ("Strings", STRING_ENSEMBLE.midi_program, 3),
    ("Bass", DOUBLE_BASS.midi_program, 4),
    ("Drums", 0, 9),
]
events_by_voice = {
    "Oboe": lead_q, "Clarinet": count_q, "Piano": piano_q,
    "Strings": pad_q, "Bass": bass_q, "Drums": drums_q,
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
    "Oboe": OBOE.humanize_dna,
    "Clarinet": CLARINET.humanize_dna,
    "Piano": PIANO.humanize_dna,
    "Strings": STRING_ENSEMBLE.humanize_dna,
    "Bass": DOUBLE_BASS.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=GENRE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked, no jitter"),
                          (humanized_path, "2-humanized", "style+instrument humanized")):
    write_provenance(str(path), "ai-generated", f"musicom nightly {NAME}",
                     sources=["methods_db:091 Coxeter-Conway Frieze", f"style:{GENRE}",
                              "phase:2 rules", f"humanize_seed:{hz_seed}"],
                     parameters={"phase": phase, "seed": SEED, "key": KEY_NAME,
                                 "bpm": BPM, "form": FORM_NAME,
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
    "project": NAME, "genre": GENRE,
    "method": "091 Coxeter-Conway Frieze Pattern Composition (CCFPC)",
    "layer": "concrete", "paradigm": "Rules-Based",
    "key": KEY_NAME, "bpm": BPM, "form": FORM_NAME,
    "form_sections": [s for s, _ in FORM], "bars": N_BARS,
    "total_ticks": TOTAL_TICKS, "tonic": TONIC,
    "scale_pcs": SCALE_DEG_PCS,
    "frieze": {"period": N, "fan_quiddity": q_base,
               "verse_quiddity": q_verse, "chorus_quiddity": q_chorus,
               "raw_event_count": len(raw_events)},
    "chord_degrees": CHORD_DEG,
    "chord_labels": [DEG_LABELS[d] for d in CHORD_DEG],
    "voices": [v for v, _, _ in VOICES],
    "humanize_seed": hz_seed,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("DONE compose")
