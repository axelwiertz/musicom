# -*- coding: utf-8 -*-
"""258-groove-rbn-critical -- nightly composition (2026-10-22).

Method 082 -- Random Boolean Network Criticality Composition (RBNCC),
layer concrete, paradigm Nature-Led. Style Groove, A natural minor,
104 BPM, form aba (A 8 | B 8 | A 8 = 24 bars).

Two-phase architecture:
  Phase 1 (raw): a Kauffman random Boolean network (N=24, K=2, p=0.5,
    critical) is run synchronously; its trajectory (pre-attractor transient
    = connective/tension, attractor cycle = the repeating groove) is decoded
    into a SINGLE raw voice. Pitch = active pc-bit (chromatic, off-scale by
    design); onset presence = rhythm-bit mask; onsets OFF-GRID (jittered).
    NO harmony, NO grid.
  Phase 2 (rules): onset snap to the 16th grid, tiered pitch quantization
    (strong beat -> in-scale AND in-chord via ScaleQuantizer.tiered_quantize;
    weak beat -> in-scale only), full 5-voice groove texture (clavi lead /
    rhodes comp / electric bass / synth pad on B only / groove drums),
    zero-drift landmark padding. Dual-version export (perfect + humanized).

Engine-only: structures + workflows.unitmatrix_composer + workflows.humanize
+ sound.synthesis.scale_quantizer + workflows.provenance. mido is NOT used
for authoring here (read-only audits live in verify.py). Instruments come from
the importable registry (source of truth).
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
    CLAVI, RHODES, ELECTRIC_BASS, SYNTH_PAD, DRUM_KIT,
)

# ---- concept ---------------------------------------------------------------
GENRE = "Groove"
NAME = "258-groove-rbn-critical"
ROOT = Path(f"/opt/data/projects/Styles/{GENRE}/{NAME}")
for sub in ("MIDI", "Audio", "Analysis"):
    (ROOT / sub).mkdir(parents=True, exist_ok=True)

TONIC = 9                       # A
KEY_NAME = "A natural minor"
NAT = [0, 2, 3, 5, 7, 8, 10]    # natural-minor (aeolian) intervals
SCALE_DEG_PCS = [(TONIC + o) % 12 for o in NAT]     # A B C D E F G
SCALE_PCS = set(SCALE_DEG_PCS)
BPM = 104
TPB = 480
BAR = 1920
EIGHTH = 240
SIXTEENTH = 120
BEAT = BAR // 4                 # 480
SEED = 20261022
rng = random.Random(SEED)

# ---- form: aba (A 8 | B 8 | A 8) = 24 bars (unique section names for engine)
FORM_NAME = "aba"
FORM = [("A1", 8), ("B", 8), ("A2", 8)]
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


# ---- harmony: diatonic 7th chords in A natural minor -----------------------
DEG_NAMES = ["i7", "ii7", "III7", "iv7", "v7", "VI7", "VII7"]
DEG_LABELS = ["Am7", "Bm7b5", "Cmaj7", "Dm7", "Em7", "Fmaj7", "G7"]


def deg_pc(d):
    return (TONIC + NAT[d % 7]) % 12


def chord_pcs_deg(d):
    # four-note 7th chord: scale degrees d, d+2, d+4, d+6 (all diatonic)
    return frozenset(deg_pc((d + k) % 7) for k in (0, 2, 4, 6))


# per-bar chord degree (A1 | B | A2); every chord is diatonic to A natural minor
CHORD_DEG = ([0, 0, 5, 6, 0, 0, 5, 6]
             + [2, 5, 3, 4, 2, 5, 3, 4]
             + [0, 0, 5, 6, 0, 0, 5, 6])
CHORD_PCS = [chord_pcs_deg(d) for d in CHORD_DEG]


def bar_deg(b):
    return CHORD_DEG[b]


def pool(deg, floor, ceil):
    """Chord-tone register pool (absolute MIDI pitches)."""
    pcs = sorted(chord_pcs_deg(deg))
    out = []
    for pc in pcs:
        p = floor + ((pc - floor) % 12)
        while p <= ceil:
            out.append(p)
            p += 12
    return sorted(out)


LEAD_POOL = {b: pool(CHORD_DEG[b], 53, 88) for b in range(N_BARS)}
COMP_POOL = {b: pool(CHORD_DEG[b], 48, 84) for b in range(N_BARS)}
BASS_POOL = {b: pool(CHORD_DEG[b], 28, 48) for b in range(N_BARS)}
PAD_POOL = {b: pool(CHORD_DEG[b], 48, 72) for b in range(N_BARS)}

# scale quantizer (A natural minor, root A3 = 57)
sq = ScaleQuantizer(root=57, scale="minor")
STRONG = (0, 960)


def snap16(t):
    return int(round(t / SIXTEENTH) * SIXTEENTH)


# ============================================================================
# PHASE 1 -- RAW RBN DRAFT (single voice, off-grid, chromatic)
# ============================================================================
def build_rbn(N, K, p, seed):
    r = random.Random(seed)
    nodes = []
    for _ in range(N):
        ins = r.sample(range(N), K)
        table = [r.random() < (1 - p) for _ in range(1 << K)]
        nodes.append((ins, table))
    return nodes


def step(nodes, x):
    out = []
    for ins, table in nodes:
        idx = 0
        for bitpos, src in enumerate(ins):
            idx |= (x[src] << bitpos)
        out.append(1 if table[idx] else 0)
    return out


def detect_cycle(nodes, x0):
    # Brent's algorithm -> (mu transient len, lam cycle len)
    power = lam = 1
    tortoise = x0
    hare = step(nodes, x0)
    while tortoise != hare:
        if power == lam:
            tortoise = hare
            power *= 2
            lam = 0
        hare = step(nodes, hare)
        lam += 1
    mu = 0
    tortoise = hare = x0
    for _ in range(lam):
        hare = step(nodes, hare)
    while tortoise != hare:
        tortoise = step(nodes, tortoise)
        hare = step(nodes, hare)
        mu += 1
    return mu, lam


N = 24
K = 2
P = 0.5
N_SLOTS = N_BARS * 16            # 24 bars x 16th slots
nodes = build_rbn(N, K, P, SEED)
x0 = [rng.random() < (1 - P) for _ in range(N)]
MU, LAM = detect_cycle(nodes, x0)
states = []
x = x0
for _ in range(N_SLOTS):
    states.append(x)
    x = step(nodes, x)

raw_events = []                 # dicts: start_tick, pc, velocity, dur
prev_pc = None
for t in range(N_SLOTS):
    st_ = states[t]
    pitch_mask = st_[0:12]
    rhythm_bits = st_[12:24]
    active = [i for i in range(12) if pitch_mask[i]]
    if not active or not rhythm_bits[t % 12]:
        continue
    # parsimonious pick: active pc nearest to the previous sounding pc
    if prev_pc is None:
        pc = active[0]
    else:
        pc = min(active, key=lambda i: min((i - prev_pc) % 12,
                                           (prev_pc - i) % 12))
    prev_pc = pc
    onset = t * SIXTEENTH + rng.randint(12, 55)     # always off-grid
    vel = 64 + 4 * sum(rhythm_bits)                  # 64..112
    dur = rng.randint(60, 150)
    raw_events.append({"start_tick": onset, "pc": pc,
                       "velocity": vel, "dur": dur})


def unit_from(events, sec_len):
    u = MusicUnit()
    for e in events:
        if e.end_tick > e.start_tick:
            u.add_event(e)
    u.add_event(MusicEvent(0, 0, sec_len, sec_len))   # zero-drift landmark
    return u


p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
p1.create_matrix(num_voices=1, num_sections=len(FORM))
p1.add_voice("RBNRaw", program=CLAVI.midi_program, channel=0)
for sname, nbars in FORM:
    p1.add_section(sname, bars=nbars)
for sname, (slen, soff) in SECTION_TICKS.items():
    evs = []
    for e in raw_events:
        if soff <= e["start_tick"] < soff + slen:
            pitch = 48 + e["pc"]                        # literal chromatic pc
            st = e["start_tick"] - soff
            end = min(st + e["dur"], slen - 1)
            evs.append(MusicEvent(pitch=pitch, volume=e["velocity"],
                                  start_tick=st, end_tick=end))
    p1.fill_voice_section("RBNRaw", sname, unit_from(evs, slen))
ok1, msg1 = p1.validate()
assert ok1, f"phase1 validate failed: {msg1}"
midi1 = ROOT / "MIDI" / f"{NAME}-phase1.mid"
p1.to_midi(str(midi1))
write_provenance(str(midi1), "ai-generated", f"musicom nightly {NAME}",
                 sources=["methods_db:082 RBN Criticality (Kauffman Boolean net)",
                          f"style:{GENRE}", "phase:1 raw draft"],
                 parameters={"phase": 1, "seed": SEED, "key": KEY_NAME,
                             "bpm": BPM, "form": FORM_NAME,
                             "rbn": {"N": N, "K": K, "p": P,
                                     "mu": MU, "lam": LAM, "slots": N_SLOTS},
                             "notes": "RBN trajectory -> chromatic off-grid raw "
                                      "line; transient=connective, attractor=groove"})
print(f"RBN: N={N} K={K} p={P} mu={MU} lam={LAM} slots={N_SLOTS} "
      f"raw_events={len(raw_events)}")
print("phase1 midi:", midi1, midi1.stat().st_size, "bytes")

# ============================================================================
# PHASE 2 -- RULES POST-PROCESS (grid snap + tiered quant + full groove texture)
# ============================================================================

def clamp_scale(p):
    while p < 55:
        p += 12
    while p > 86:
        p -= 12
    return p


def lead_events():
    notes = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        raw = [e for e in raw_events
               if b * BAR <= e["start_tick"] < (b + 1) * BAR]
        raw.sort(key=lambda e: e["start_tick"])
        for e in raw:
            st = snap16(e["start_tick"])
            if st >= (b + 1) * BAR:
                st = (b + 1) * BAR - SIXTEENTH
            w = classify_weight(st, STRONG, BAR)
            if w == "strong":
                p = sq.tiered_quantize(48 + e["pc"], weight="strong",
                                       chord_tones=LEAD_POOL[b])
            else:
                p = clamp_scale(sq.quantize(48 + e["pc"]))
            dur = max(SIXTEENTH, snap16(e["dur"]))
            vel = e["velocity"]
            if s == "B":                       # lift: longer, brighter
                dur = min(EIGHTH * 2, dur + SIXTEENTH)
                vel = min(118, vel + 6)
            elif s == "A2":                    # return: back to groove
                dur = SIXTEENTH
            notes.append(MusicEvent(pitch=int(p), volume=int(vel),
                                    start_tick=st,
                                    end_tick=min(st + dur, (b + 1) * BAR - 1)))
    return notes


def comp_events():
    """Rhodes comp: chord voicings on the 'and' of 2 and 4 (off-beats)."""
    evs = []
    for b in range(N_BARS):
        tones = COMP_POOL[b]
        bar0 = b * BAR
        for st in (bar0 + 3 * EIGHTH, bar0 + 7 * EIGHTH):   # 720, 1680
            for p in tones[:4]:
                evs.append(MusicEvent(pitch=p, volume=62,
                                      start_tick=st, end_tick=st + EIGHTH))
    return evs


def bass_events():
    """Groove bass: root on 1&3 (strong), 5th/octave syncopation (weak),
    diatonic approach into the next bar's root."""
    evs = []
    for b in range(N_BARS):
        tones = BASS_POOL[b]
        root = tones[0]
        fifth = min(tones, key=lambda p: abs(p - (root + 7)))
        octv = root + 12
        bar0 = b * BAR
        # beat 1 (strong): root
        evs.append(MusicEvent(pitch=root, volume=96, start_tick=bar0,
                              end_tick=bar0 + SIXTEENTH * 3))
        # 'and' of 2 (weak syncopation): octave
        evs.append(MusicEvent(pitch=min(octv, 48), volume=82,
                              start_tick=bar0 + 720, end_tick=bar0 + 720 + SIXTEENTH))
        # beat 3 (strong): fifth
        evs.append(MusicEvent(pitch=fifth, volume=90, start_tick=bar0 + 960,
                              end_tick=bar0 + 960 + SIXTEENTH * 2))
        # 'and' of 4 (weak): diatonic approach into next root
        nxt = CHORD_DEG[(b + 1) % N_BARS]
        next_root = BASS_POOL[(b + 1) % N_BARS][0]
        approach = sq.quantize(next_root - 1)          # scale tone below root
        approach = max(28, min(48, approach))
        evs.append(MusicEvent(pitch=int(approach), volume=80,
                              start_tick=bar0 + 1680, end_tick=bar0 + 1680 + SIXTEENTH))
    return evs


def pad_events():
    """Synth pad: sustained chord tones, B section only (lift)."""
    evs = []
    for b in range(N_BARS):
        if section_of_bar(b) != "B":
            continue
        tones = PAD_POOL[b]
        bar0 = b * BAR
        for p in tones[:4]:
            evs.append(MusicEvent(pitch=p, volume=66, start_tick=bar0,
                                  end_tick=bar0 + BAR - 1))
    return evs


def drums_events():
    """Funk groove kit (channel 9): syncopated kick, backbeat snare, 16th hats."""
    evs = []
    for b in range(N_BARS):
        s = section_of_bar(b)
        bar0 = b * BAR
        for k in range(16):                             # hi-hat 16ths
            st = bar0 + k * SIXTEENTH
            acc = 88 if (k % 4 in (1, 3)) else 58       # accent the off-16ths
            evs.append(MusicEvent(pitch=42, volume=acc,
                                  start_tick=st, end_tick=st + SIXTEENTH))
        for st in (bar0, bar0 + 720, bar0 + 960):       # syncopated kick
            evs.append(MusicEvent(pitch=36, volume=98,
                                  start_tick=st, end_tick=st + SIXTEENTH))
        for st in (bar0 + 480, bar0 + 1440):            # backbeat snare
            evs.append(MusicEvent(pitch=38, volume=90,
                                  start_tick=st, end_tick=st + SIXTEENTH))
        if s == "B":                                    # open hat in the lift
            evs.append(MusicEvent(pitch=46, volume=80,
                                  start_tick=bar0 + 1680,
                                  end_tick=bar0 + 1680 + SIXTEENTH))
    return evs


def finalize(events):
    """Grid-snap + register clamp + (start,pitch) dedupe for pitched voices."""
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
comp_q = finalize(comp_events())
bass_q = finalize(bass_events())
pad_q = finalize(pad_events())
drums_q = drums_events()

VOICES = [
    ("Clavi", CLAVI.midi_program, 0),
    ("Rhodes", RHODES.midi_program, 1),
    ("Bass", ELECTRIC_BASS.midi_program, 2),
    ("Pad", SYNTH_PAD.midi_program, 3),
    ("Drums", 0, 9),
]
events_by_voice = {
    "Clavi": lead_q, "Rhodes": comp_q, "Bass": bass_q,
    "Pad": pad_q, "Drums": drums_q,
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
    "Clavi": (3.0, 5.0, 0.0, 0.015),   # lock: tight clavi lead (was Keys 6.0ms)
    "Rhodes": RHODES.humanize_dna,
    "Bass": ELECTRIC_BASS.humanize_dna,
    "Pad": SYNTH_PAD.humanize_dna,
    "Drums": DRUM_KIT.humanize_dna,
}
perfect_path = ROOT / "MIDI" / f"{NAME}-perfect.mid"
humanized_path = ROOT / "MIDI" / f"{NAME}-humanized.mid"
hz = export_dual(composer, str(perfect_path), str(humanized_path),
                 style=GENRE, seed=hz_seed, bpm=BPM, instruments=hz_instruments)

for path, phase, note in ((perfect_path, "2-perfect", "grid-locked, no jitter"),
                          (humanized_path, "2-humanized", "style+instrument humanized")):
    write_provenance(str(path), "ai-generated", f"musicom nightly {NAME}",
                     sources=["methods_db:082 RBN Criticality", f"style:{GENRE}",
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
    "method": "082 Random Boolean Network Criticality Composition (RBNCC)",
    "layer": "concrete", "paradigm": "Nature-Led",
    "key": KEY_NAME, "bpm": BPM, "form": FORM_NAME,
    "form_sections": [s for s, _ in FORM], "bars": N_BARS,
    "total_ticks": TOTAL_TICKS, "tonic": TONIC,
    "scale_pcs": SCALE_DEG_PCS,
    "rbn": {"N": N, "K": K, "p": P, "mu": MU, "lam": LAM, "slots": N_SLOTS,
            "raw_event_count": len(raw_events)},
    "chord_degrees": CHORD_DEG,
    "chord_labels": [DEG_LABELS[d] for d in CHORD_DEG],
    "voices": [v for v, _, _ in VOICES],
    "humanize_seed": hz_seed,
}
with open(ROOT / "Analysis" / "summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("DONE compose")
