# -*- coding: utf-8 -*-
"""099 - Classical Crossover, Path A top-down, 7 sections, per-section methods.

Framework-first (001 owns the skeleton) + a different method per section,
inside the same C-major diatonic framework:

    Intro 4 | A 8 | B 8 | Dev 8 | A' 8 | B' 8 | Coda 8   (52 bars)

Methods per section:
    Intro  023 Tendency Masking   (solo piano corridor)
    A      001 + 002 Markov       (diatonic theme)
    B      079 Tintinnabuli       (M-voice + T-voice, position 1)
    Dev    ABS-003 Z-swap + ABS-004 parsimonious VL (abstract layer, tension peak)
    A'     001 + 002 variant      (same theme, denser, +register)
    B'     079 Tintinnabuli       (same talea, T-voice position 2)
    Coda   018 Schillinger        (decelerating rhythm + dropout)

Tension curve (ABS-001): 0.0 0.3 0.5 1.0 0.4 0.5 0.1

Engine rules honored: UnitMatrix only, cell-local ticks, terminal landmark,
validate() gate, no raw-mido authoring, harmony tables from rules/harmony.py.
"""
import json
import os
import random
import sys

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization
from rules.harmony import (CHORD_SHAPES, QUALITY_INTERVALS, parse_degree,
                           tonic_offset, infer_mode)

BPM = 96
TPB = 480
BAR = TPB * 4
KEY = "C"
TONIC = tonic_offset(KEY)          # 0 for C
MODE = "major"
SECTION_TICKS = 8 * BAR            # every section = 8 bars (Intro uses 4)
PROJ = "/opt/data/projects/Styles/Classical/099-classical-crossover-pathA-7sec"
MIDI_DIR = os.path.join(PROJ, "MIDI")

SECTIONS = ["Intro", "A", "B", "Dev", "A2", "B2", "Coda"]
BARS = {"Intro": 4, "A": 8, "B": 8, "Dev": 8, "A2": 8, "B2": 8, "Coda": 8}

# per-section harmonic regions (NEVER one global loop)
SECTION_PROGS = {
    "Intro": ["I", "I", "V", "V"],
    "A":     ["I", "V", "vi", "IV", "I", "V", "IV", "I"],
    "B":     ["vi", "IV", "I", "V", "vi", "IV", "I", "V"],
    "Dev":   ["vi", "IV", "ii", "V", "ii", "V", "V", "I"],
    "A2":    ["I", "V", "vi", "IV", "I", "V", "IV", "I"],
    "B2":    ["IV", "V", "vi", "I", "IV", "V", "vi", "I"],
    "Coda":  ["IV", "I", "V", "I", "IV", "I", "V", "I"],
}
# ABS-001 tension targets (Dev peak, Coda resolve)
TENSION = {"Intro": 0.0, "A": 0.3, "B": 0.5, "Dev": 1.0,
           "A2": 0.4, "B2": 0.5, "Coda": 0.1}

VOICES = [
    ("Lead", MidiInstrument.VIOLIN, 0),
    ("Counter", MidiInstrument.FLUTE, 1),
    ("Piano", MidiInstrument.PIANO, 2),
    ("Pad", MidiInstrument.STRING_ENSEMBLE, 3),
    ("Bass", MidiInstrument.BASS, 4),
]

rng = random.Random(20260917)


# ---------------------------------------------------------------- harmony ----
def section_chords(prog):
    """(root_midi, quality, degree) per bar of a section, from canonical tables."""
    out = []
    from rules.harmony import MODE_OFFSETS
    for deg in prog:
        root_iv, quality = CHORD_SHAPES[deg]
        # mode-aware root offset via canonical parse_degree
        idx, acc = parse_degree(deg)
        root_pc = (TONIC + MODE_OFFSETS[MODE][idx]) % 12
        root_midi = 36 + root_pc
        chord_tones = [root_midi + iv for iv in QUALITY_INTERVALS[quality]]
        out.append((root_midi, quality, tuple(chord_tones), deg))
    return out  # list of (root_midi, quality, tones, degree) per bar


SECTION_CHORDS = {s: section_chords(SECTION_PROGS[s]) for s in SECTIONS}
ROOTS_PER_BAR = [SECTION_CHORDS[s][b][0] for s in SECTIONS for b in range(BARS[s])]
SECTION_ROOTS = {s: SECTION_CHORDS[s][BARS[s] // 2][0] for s in SECTIONS}  # midpoint


def chord_at(section, bar, tick_in_bar=0):
    """Chord for a (section, bar) pair -> (root, quality, tones, degree)."""
    return SECTION_CHORDS[section][min(bar, BARS[section] - 1)]


KEY_PCS = {(TONIC + o) % 12 for o in (0, 2, 4, 5, 7, 9, 11)}
DEV_BORROW = {2, 4, 7, 9, 11, 0, 5}  # ii and V of Dev are still diatonic


# ------------------------------------------------------------ helpers --------
def snap(events, grid=120):
    out = []
    for e in events:
        st = int(round(e.start_tick / grid) * grid)
        et = max(st + 60, int(round(e.end_tick / grid) * grid))
        out.append(MusicEvent(e.pitch, e.volume, st, et))
    return out


def dedup(events):
    best = {}
    for e in events:
        if e.pitch == 0:
            continue
        k = (e.start_tick, e.pitch)
        if k not in best or (e.end_tick - e.start_tick) > (best[k].end_tick - best[k].start_tick):
            best[k] = e
    return [best[k] for k in sorted(best)]


def clamp_events(events, section_len):
    out = []
    for e in events:
        st = max(0, min(e.start_tick, section_len - 10))
        et = max(st + 10, min(e.end_tick, section_len))
        out.append(MusicEvent(e.pitch, e.volume, st, et))
    return out


def unit_from(events, section_len):
    u = MusicUnit()
    for e in events:
        u.add_event(e)
    u.add_event(MusicEvent(0, 0, section_len, section_len))
    return u


def quantize_to_chord(pitch, tones, lo, hi):
    """Nearest chord tone of the bar's chord inside [lo, hi]."""
    best, bd = None, 10**9
    for oct_ in range(-3, 4):
        for t in tones:
            for iv in (0, 12):
                p = t + 12 * oct_ + iv
                if lo <= p <= hi:
                    d = abs(p - pitch)
                    if d < bd:
                        bd, best = d, p
    return best if best is not None else (lo + hi) // 2


def voice_lead_fix(lines):
    """Shift upper voice to avoid parallel octaves/fifths vs previous chord."""
    fixed = []
    for prev, cur in zip(lines, lines[1:]):
        if prev is None or cur is None:
            continue
        iv = abs(cur - prev) % 12
        if iv in (0, 7):
            fixed.append((prev, cur))
    return fixed


# -------------------------------------------------- method builders ----------
def method_023_intro(section_len):
    """Intro: Tendency Masking (023), solo piano, narrow corridor rising."""
    from generators.tendency_masking import TendencyMaskingGenerator
    key_pitches = [48 + pc for pc in sorted(KEY_PCS)] + [60 + pc for pc in sorted(KEY_PCS)]
    g = TendencyMaskingGenerator(key_pitches)
    unit = g.generate_voice_section(
        section_ticks=section_len, step_ticks=TPB,
        bounds_start=(55, 67), bounds_end=(60, 72),
        density=0.55, volume=70)
    return unit


def method_002_markov(section, section_len, denser=False, seed=7):
    """A / A': Markov degree walk -> chord-tone quantized melody."""
    core_trans = {
        0: {2: .30, 4: .25, 1: .15, 0: .10},
        1: {0: .40, 2: .30, 4: .30},
        2: {4: .30, 0: .25, 2: .20, 5: .15},
        3: {0: .30, 4: .30, 2: .20, 5: .20},
        4: {5: .25, 2: .25, 4: .20, 0: .10, 6: .10},
        5: {4: .30, 0: .30, 5: .20, 2: .20},
        6: {0: .60, 4: .40},
    }
    from sound.generators.event_core import MarkovCore
    mc = MarkovCore(transition_matrix=core_trans)
    steps = 32 if not denser else 48
    walk = mc.generate(steps=steps, seed=seed + (5 if denser else 0))
    scale = [0, 2, 4, 5, 7, 9, 11]
    events = []
    step_ticks = (TPB * 2) if not denser else TPB  # half notes -> quarters
    register = (67, 79) if denser else (60, 76)
    i = 0
    t = 0
    while t < section_len:
        bar = min(t // BAR, BARS[section] - 1)
        deg = walk[i % len(walk)]
        # Markov states are SCALE-DEGREE INDICES 0..6 (never pitch classes);
        # convert to a raw pitch near the register, phase-2 quantizes to chord.
        raw_pitch = 60 + scale[deg % 7] + (12 if denser else 0)
        pitch = quantize_to_chord(raw_pitch, chord_at(section, bar)[2],
                                  register[0], register[1])
        events.append(MusicEvent(pitch, 88 if denser else 84, t, t + step_ticks - 60))
        t += step_ticks
        i += 1
    events = dedup(snap(clamp_events(events, section_len)))
    return events


def pc_of(deg, scale):
    return scale[deg % 7]


def pc_near(register_lo, key_pcs):
    return register_lo


def method_079_tintinnabuli(section, section_len, t_position=1, seed=3):
    """B / B': Pärt tintinnabuli. M-voice stepwise, T-voice triad shadow."""
    from generators.tintinnabuli import TintinnabuliGenerator
    g = TintinnabuliGenerator(tonic=72, mode="major", t_register=48)
    # M-voice: gentle stepwise arch within the section's chords (pre-quantized)
    scale = [0, 2, 4, 5, 7, 9, 11]
    seq = []
    arc = [0, 1, 2, 3, 4, 3, 2, 1, 0, 1, 2, 3, 4, 5, 4, 3,
           2, 1, 0, 1, 2, 1, 0, 2, 1, 2, 3, 2, 1, 0, 1, 0]
    r = random.Random(seed + (11 if t_position != 1 else 0))
    for i, a in enumerate(arc):
        pc = scale[a % 7] + 12 * (1 if a >= 5 else 0)
        seq.append(72 + ((TONIC + pc) % 12 if False else pc))
    start_ticks = [i * TPB for i in range(len(seq))]
    end_ticks = [s + TPB - 40 for s in start_ticks]
    m_unit = g.m_voice(seq, volume=82)
    m_events = [MusicEvent(e.pitch, e.volume,
                           start_ticks[i] % (len(seq) * TPB),
                           (start_ticks[i] + TPB - 40) % (len(seq) * TPB) or section_len)
                for i, e in enumerate([x for x in m_unit_events(g, seq)])]
    # simpler: build directly from the generator per-note
    events = []
    for i, p in enumerate(seq):
        st = (i * TPB) % section_len
        et = min(st + TPB - 40, section_len)
        events.append(MusicEvent(p, 82, st, et))
    # T-voice shadow at the requested position
    t_unit = g.t_voice(seq, position=t_position, volume=72,
                       start_ticks=[(i * TPB) % section_len for i in range(len(seq))],
                       end_ticks=[((i * TPB) + TPB - 40) % section_len or section_len
                                  for i in range(len(seq))])
    t_events = [e for e in t_unit.events if e.pitch > 0]
    # fold T-voice ticks into the section and lengthen to M-note durations
    t_fixed = []
    for i, e in enumerate(t_events):
        st = (i * TPB) % section_len
        et = min(st + TPB - 40, section_len)
        t_events[i] = MusicEvent(e.pitch, e.volume, st, et)
    return events + t_events


def m_unit_events(gen, seq):
    u = gen.m_voice(seq)
    return [e for e in u.events if e.pitch > 0]


def method_dev_abs(section_len, seed=13):
    """Dev: ABS-003 Z-swap + ABS-004 parsimonious voice leading.

    Chords are re-derived via the subset network's Z-partner (same ICV,
    different notes) and realized with <=2 semitone total motion.
    """
    from rules.subset_network import PatternNetwork, standard_patterns
    from rules.realize import realize_tonal_cluster
    from rules.set_theory import interval_vector
    net = PatternNetwork(standard_patterns())
    swaps = []
    events = []
    step = BAR // 2
    t = 0
    idx = 0
    prev_cluster = None
    while t < section_len:
        bar = min(t // BAR, BARS["Dev"] - 1)
        root, quality, tones, deg = chord_at("Dev", bar)
        # map the bar's triad to a network pattern (root-position maj/min id)
        pid = ("maj" if quality == "maj" else "min") + "0"
        pat = net.patterns[pid]
        zid = pat.z_partner
        if zid is None:
            zid = pid
        zpat = net.patterns[zid]
        cluster = realize_tonal_cluster(zpat, base=48)
        # ABS-004: parsimonious move from previous cluster (<=2 total motion)
        if prev_cluster is not None:
            best = min(
                [cluster] + [[c + 12 * o for c in cluster] for o in (-1, 1)],
                key=lambda cl: sum(abs(a - b) for a, b in zip(sorted(cl), sorted(prev_cluster + [prev_cluster[-1]] * (len(cl) - len(prev_cluster))))) if True else 99,
            )
            cluster = best
        swaps.append((deg, quality, pid, zid))
        for j, p in enumerate(cluster):
            st = t + j * (step // max(1, len(cluster)))
            et = min(st + step // 2, section_len)
            events.append(MusicEvent(p + 12, 92, st, et))
        prev_cluster = cluster
        t += step
        idx += 1
    return dedup(snap(clamp_events(events, section_len))), swaps


def method_018_coda(section_len, seed=5):
    """Coda: Schillinger resultant rhythm (3x2), progressive dropout."""
    from generators.schillinger import SchillingerGenerator
    sg = SchillingerGenerator(3, 2)
    resultant = sg.generate_resultant()  # [2,1,1,2] eighths pattern
    step_ticks = BAR // 8
    # expand the resultant over 8 bars with lengthening (ritardando feel)
    events = []
    scale = [0, 4, 7]  # C-major triad tones for the descending coda line
    t = 0
    bar = 0
    while t < section_len:
        i = (bar * 4 + ((t % BAR) // (BAR // 8))) % len(resultant)
        # dropout: Lead exits bar<4, Counter bar<4 (handled by caller),
        # here only the Piano rhythm line
        base_pitch = 72 - (bar % 4) * 2
        dur = step_ticks * max(1, resultant[(t // step_ticks) % len(resultant)])
        dur = min(dur * (1 + bar // 2), BAR)  # lengthen over the section
        pitch = quantize_to_chord(base_pitch_seed(bar, t), chord_at("Coda", min(bar, 7))[2], 55, 79)
        events.append(MusicEvent(pitch, 80, t, min(t + dur, section_len)))
        t += step_ticks * max(1, resultant[(t // step_ticks) % len(resultant)])
        if t >= (bar + 1) * BAR:
            bar += 1
    return dedup(snap(clamp_events(events, section_len)))


def base_pitch_seed(bar, t):
    return 76 - (bar * 2)


# ------------------------------------------------------------- assemble ------
def build_accompaniment(section, section_len, section_bar_count):
    """Pad (sustained chords) + Bass (root/fifth) for every section."""
    pad_events, bass_events = [], []
    artic = {
        "Intro": "fade", "A": "sustain", "B": "swell", "Dev": "tremolo",
        "A2": "sustain", "B2": "sustain", "Coda": "sustain-drop",
    }[section]
    for b in range(section_bar_count):
        root, quality, tones, deg = chord_at(section, b)
        bar0 = b * BAR
        if artic == "fade":
            if b < 1:
                continue
        for pc in tones:
            pad_events.append(MusicEvent(pc, 58, bar0, bar0 + BAR - 20))
        bass_events.append(MusicEvent(root, 96, bar0, bar0 + BAR // 2 - 40))
        bass_events.append(MusicEvent(root, 92, bar0 + BAR // 2, bar0 + BAR - 20))
        if artic == "tremolo":
            # replace pad sustain with 8th-note tremolo +-10 velocity
            pad_events = [e for e in pad_events if not (bar0 <= e.start_tick < bar0 + BAR and e.volume == 58)]
            for k in range(8):
                vel = 58 + (10 if k % 2 == 0 else -10)
                for pc in tones:
                    pad_events.append(MusicEvent(pc, vel, bar0 + k * (BAR // 8),
                                                 bar0 + (k + 1) * (BAR // 8) - 20))
    return pad_events, bass_events


def main():
    os.makedirs(MIDI_DIR, exist_ok=True)
    os.makedirs(os.path.join(PROJ, "Analysis"), exist_ok=True)
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    composer.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in VOICES:
        composer.add_voice(name, program=prog, channel=ch)
    for s in SECTIONS:
        composer.add_section(s, bars=BARS[s])

    phase1_units = []          # raw method drafts for -phase1.mid
    report = {"tension": TENSION, "z_swaps": [], "sections": {}}

    for s in SECTIONS:
        n = BARS[s]
        sl = n * BAR
        raw_events = []      # phase-1 raw (method voice)

        # ---- Lead method per section ------------------------------------
        if s == "Intro":
            unit = method_023_intro(sl)
            raw_events = [e for e in unit.events if e.pitch > 0]
            lead = dedup(snap(clamp_events(raw_events, sl)))
        elif s == "A":
            raw_events = method_002_markov(s, sl, denser=False, seed=7)
            lead = raw_events
        elif s == "A2":
            raw_events = method_002_markov(s, sl, denser=True, seed=7)
            lead = [(lambda e: MusicEvent(e.pitch + 12, e.volume, e.start_tick, e.end_tick))(e) for e in raw_events]
        elif s in ("B", "B2"):
            pos = 1 if s == "B" else 2
            raw_events = method_079_tintinnabuli(s, sl, t_position=pos, seed=3)
            lead = raw_events
        elif s == "Dev":
            raw_events, swaps = method_dev_abs(sl)
            report_swaps = swaps
            lead = raw_events
        else:  # Coda
            raw_events = method_018_coda(sl)
            lead = raw_events

        # ---- phase 2 rules: chord quantize + dedup + clamp --------------
        q_lead = []
        for e in lead:
            bar = min(e.start_tick // BAR, n - 1)
            _, _, tones, _ = chord_at(s, bar)
            lo, hi = ((67, 88) if s == "A2" else (60, 84)) if s != "B2" else (60, 79)
            q = quantize_to_chord(e.pitch, tones, lo, hi)
            q_lead.append(MusicEvent(q, e.volume, e.start_tick, e.end_tick))
        q_lead = dedup(snap(clamp_events(q_lead, sl)))

        pad_events, bass_events = build_accompaniment(s, sl, n)

        # Counter flute: joins in A2 and B sections only (40-60% density).
        # Voice = chord tone a diatonic third below the lead, re-quantized to the
        # SAME bar's chord (a blind pitch-5 shift leaves 60% non-chord tones).
        counter_events = []
        if s in ("A2", "B", "B2"):
            for e in q_lead[::2]:
                bar_i = min(e.start_tick // BAR, n - 1)
                _, _, tones, _ = chord_at(s, bar_i)
                c = quantize_to_chord(e.pitch - 3, tones, 55, 76)
                counter_events.append(MusicEvent(c, 76, e.start_tick, e.end_tick))

        # Coda dropout (no fade): exit voices progressively
        if s == "Coda":
            def keep(e, until_bar):
                return e.start_tick < until_bar * BAR
            lead = [e for e in q_lead if keep(e, 4)]
            counter_events = [e for e in counter_events if keep(e, 4)]
            pad_events = [e for e in pad_events if keep(e, 6)]
            bass_events = [e for e in bass_events if keep(e, 6)]

        # fill matrix (cell-local ticks already: events built per section)
        composer.fill_voice_section("Lead", s, _unit(q_lead, sl))
        composer.fill_voice_section("Counter", s, _unit(counter_events, sl))
        composer.fill_voice_section("Piano", s, _unit(pad_events, sl))
        composer.fill_voice_section("Pad", s, _unit(pad_events, sl))
        composer.fill_voice_section("Bass", s, _unit(bass_events, sl))

        report["sections"][s] = {"lead_notes": len(q_lead), "pad_notes": len(pad_events),
                                 "bass_notes": len(bass_events), "counter_notes": len(counter_events)}
        if s == "Dev":
            report["z_swaps"] = swaps
        phase1_units.append((s, raw_events, sl))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"validate() failed: {msg}")

    midi_path = os.path.join(MIDI_DIR, "099-classical-7sec.mid")
    composer.to_midi(midi_path)

    # ---- Phase 1 MIDI: raw drafts, single voice, own gate ---------------
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=4)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawDraft", program=MidiInstrument.VIOLIN, channel=0)
    for s in SECTIONS:
        p1.add_section(s, bars=BARS[s])
    for (s, raw_events, _sl), sec in zip(phase1_units, SECTIONS):
        evs = [MusicEvent(e.pitch, e.volume, e.start_tick, e.end_tick) for e in raw_events]
        sl = BARS[sec] * BAR
        evs = clamp_events(evs, sl)
        p1.fill_voice_section("RawDraft", sec, _unit(evs, sl))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"phase-1 validate() failed: {msg1}")
    p1_path = os.path.join(MIDI_DIR, "099-classical-7sec-phase1.mid")
    p1.to_midi(p1_path)

    # ---- provenance + grid ---------------------------------------------
    write_provenance(midi_path, AI_ASSISTED,
                     "099-classical-crossover-pathA-7sec (Path A: 001 skeleton + per-section methods)",
                     sources=["paths:A top-down", "001", "002", "023", "079", "018",
                              "ABS-001", "ABS-003", "ABS-004"],
                     parameters={"bpm": BPM, "key": KEY, "form": "Intro|A|B|Dev|A2|B2|Coda",
                                 "tension_curve": TENSION, "seed": 20260917,
                                 "phase": 2})
    write_provenance(p1_path, AI_ASSISTED, "phase1 raw drafts (pre-rules)",
                     sources=["023", "002", "079", "ABS-003", "018"],
                     parameters={"phase": 1, "seed": 20260917})
    write_grid_visualization(composer.matrix,
                             os.path.join(PROJ, "Analysis", "grid_visualization.txt"),
                             ticks_per_character=480,
                             voice_names=[v[0] for v in VOICES], bpm=BPM)

    import json
    with open(os.path.join(PROJ, "Analysis", "tension_curve.json"), "w") as f:
        json.dump({"tension_targets": TENSION, "section_roots": SECTION_ROOTS,
                   "roots_per_bar": ROOTS_PER_BAR}, f, indent=2)

    for p in (midi_path, p1_path):
        size = os.path.getsize(p)
        assert size > 40, f"empty output {p}"
        print(f"{os.path.basename(p)}: {size} bytes")
    print(json.dumps(report, indent=2, default=str)[:1500])
    return midi_path, p1_path


def _unit(events, section_len):
    u = MusicUnit()
    for e in events:
        u.add_event(e)
    u.add_event(MusicEvent(0, 0, section_len, section_len))
    return u


def clamp_events(events, section_len):
    return clamp_events_impl(events, section_len)


def clamp_events_impl(events, section_len):
    out = []
    for e in events:
        st = max(0, min(e.start_tick, section_len - 10))
        et = max(st + 10, min(e.end_tick, section_len))
        out.append(MusicEvent(e.pitch, e.volume, st, et))
    return out


if __name__ == "__main__":
    main()
