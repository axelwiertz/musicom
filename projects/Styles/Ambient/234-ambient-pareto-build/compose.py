# -*- coding: utf-8 -*-
"""234-ambient-pareto-build — Multi-Objective Evolutionary Pareto Composition.

Nightly two-phase composition job (2026-10-10).

Style: Ambient. Method 098 Multi-Objective Evolutionary Pareto Composition
(MOEPC), layer CONCRETE, paradigm Stochastic. Form: cinematic-build
(Intro 4 / Build 8 / Rise 8 / Peak 8 / Resolve 4 = 32 bars).

Method 098 essence (NSGA-II, Deb 2002): a population of candidate melodic
genomes is evolved against FOUR conflicting objectives — harmonic quality,
melodic quality (conjunctness), rhythmic coherence, and voice independence
(contour interest). Non-dominated sorting + crowding distance yields a Pareto
FRONT of trade-off melodies; the front itself supplies the macro-form
(smooth archetype -> Intro/Resolve, balanced -> Build, active -> Rise/Peak).

Phase 1 (raw generative draft): the "balanced" Pareto-front melody, single
celesta voice, unquantized onsets + unquantized pitch (raw float genome),
no harmony, no chord-tone snapping -> -phase1.mid

Phase 2 (musicom rules): front archetypes mapped to sections, chord-tone
quantization per bar against a D-Aeolian modal progression, 120-tick
grid snap, sustained organ pad + cello bass + harp sparkle + sparse
cinematic percussion, voice-leading optimization/correction, zero-drift
gate -> 234-ambient-pareto-build.mid
"""
import os
import sys

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import CELESTA, ORGAN, CELLO, HARP

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree

import numpy as np

# ---- Composition parameters -------------------------------------------------
KEY_NAME = "D Aeolian"
KEY_ROOT_PC = 2
SCALE_INTERVALS = [0, 2, 3, 5, 7, 8, 10]      # D E F G A Bb C
KEY_PCS = [2, 4, 5, 7, 9, 10, 0]
KEY_ROOT_MIDI = 62                            # D4
BPM = 70
TPB = 480
BPB = 4
BAR = TPB * BPB                               # 1920

SECTIONS = ["Intro", "Build", "Rise", "Peak", "Resolve"]
SECTION_BARS = [4, 8, 8, 8, 4]
SECTION_TICKS = [b * BAR for b in SECTION_BARS]
NUM_BARS = sum(SECTION_BARS)                  # 32
TOTAL_TICKS = NUM_BARS * BAR                  # 61440

# D-Aeolian modal progression (0-based degrees: i=0 ii=1 III=2 iv=3 v=4 VI=5 VII=6)
BAR_DEGREES = [
    0, 0, 5, 5,                              # Intro  (i i VI VI)
    0, 5, 6, 5, 3, 0, 5, 6,                  # Build  (i VI VII VI iv i VI VII)
    3, 4, 5, 6, 3, 4, 0, 6,                  # Rise   (iv v VI VII iv v i VII)
    0, 5, 3, 4, 5, 6, 0, 0,                  # Peak   (i VI iv v VI VII i i)
    0, 0, 5, 0,                              # Resolve(i i VI i)
]
assert len(BAR_DEGREES) == NUM_BARS, "bar-degree count mismatch"

SECTION_ARCH = {"Intro": "smooth", "Build": "balanced", "Rise": "active",
                "Peak": "active", "Resolve": "smooth"}
SECTION_OCT = {"Intro": -12, "Build": 0, "Rise": 0, "Peak": 12, "Resolve": -12}

VOICES = ["Lead", "Pad", "Bass", "Sparkle", "Drums"]
VOICE_PROGRAMS = [CELESTA.midi_program, ORGAN.midi_program, CELLO.midi_program,
                  HARP.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
BASE = "234-ambient-pareto-build"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")


# ---- NSGA-II (Method 098 core) ----------------------------------------------
N_NOTES = 96
DIM = N_NOTES * 3
POP = 64
GEN = 70
NP_RNG = np.random.default_rng(20261010)
KEY_PCS_F = np.array([float(p) for p in KEY_PCS])


def decode(x):
    p = x[0::3]
    o = x[1::3]
    d = x[2::3]
    pitch = 52.0 + p * 43.0                       # 52..95 (unquantized float)
    onset = o * (TOTAL_TICKS - 1)                 # 0..TOTAL (unquantized)
    dur = 240.0 + d * 1440.0                      # 240..1680
    order = np.argsort(onset)
    return pitch[order].copy(), onset[order].copy(), dur[order].copy()


def objectives(pitch, onset, dur):
    pc = np.mod(pitch, 12.0)
    dist = np.abs(pc[:, None] - KEY_PCS_F[None, :])
    dist = np.minimum(dist, 12.0 - dist)
    f1 = dist.min(axis=1).mean() / 6.0            # harmonic quality (0..1)

    iv = np.abs(np.diff(pitch))
    f2 = iv.mean() / 12.0                         # melodic quality (conjunct)

    gaps = np.diff(onset)
    gaps = np.clip(gaps, 1.0, None)
    cv = gaps.std() / (gaps.mean() + 1e-9)
    f3 = min(cv, 2.0) / 2.0                       # rhythmic coherence

    di = np.sign(np.diff(pitch))
    changes = int(np.sum(di[1:] != di[:-1]))
    interest_dir = changes / max(1, N_NOTES - 2)
    spread = (pitch.max() - pitch.min()) / 43.0
    interest = 0.5 * interest_dir + 0.5 * spread
    f4 = 1.0 - interest                           # voice independence (max interest)
    return np.array([f1, f2, f3, f4])


def _dom(a, b):
    return bool(np.all(a <= b) and np.any(a < b))


def fast_non_dominated_sort(fits):
    n = len(fits)
    S = [[] for _ in range(n)]
    n_p = [0] * n
    fronts = [[]]
    for i in range(n):
        for j in range(i + 1, n):
            if _dom(fits[i], fits[j]):
                S[i].append(j)
                n_p[j] += 1
            elif _dom(fits[j], fits[i]):
                S[j].append(i)
                n_p[i] += 1
        if n_p[i] == 0:
            fronts[0].append(i)
    k = 0
    while fronts[k]:
        nxt = []
        for i in fronts[k]:
            for j in S[i]:
                n_p[j] -= 1
                if n_p[j] == 0:
                    nxt.append(j)
        k += 1
        fronts.append(nxt)
    fronts.pop()
    return fronts


def crowding_distance(fits):
    n, m = fits.shape
    dist = np.zeros(n)
    for obj in range(m):
        idx = np.argsort(fits[:, obj])
        dist[idx[0]] = dist[idx[-1]] = np.inf
        fmin, fmax = fits[idx[0], obj], fits[idx[-1], obj]
        if fmax - fmin < 1e-9:
            continue
        for r in range(1, n - 1):
            dist[idx[r]] += (fits[idx[r + 1], obj] - fits[idx[r - 1], obj]) / (fmax - fmin)
    return dist


def sbx_crossover(p1, p2, eta=15.0):
    u = NP_RNG.random(len(p1))
    beta = np.where(u <= 0.5, (2.0 * u) ** (1.0 / (eta + 1)),
                    (1.0 / (2.0 * (1.0 - u))) ** (1.0 / (eta + 1)))
    c1 = 0.5 * ((1 + beta) * p1 + (1 - beta) * p2)
    c2 = 0.5 * ((1 - beta) * p1 + (1 + beta) * p2)
    return np.clip(c1, 0, 1), np.clip(c2, 0, 1)


def poly_mutate(x, eta=20.0, prob=None):
    prob = prob if prob is not None else 1.0 / DIM
    y = x.copy()
    mask = NP_RNG.random(DIM) < prob
    r = NP_RNG.random(DIM)
    delta = np.where(r < 0.5,
                     (2.0 * r) ** (1.0 / (eta + 1)) - 1.0,
                     1.0 - (2.0 * (1.0 - r)) ** (1.0 / (eta + 1)))
    y[mask] += delta[mask]
    return np.clip(y, 0, 1)


def evolve():
    pop = NP_RNG.random((POP, DIM))
    for gen in range(GEN):
        fits = np.array([objectives(*decode(ind)) for ind in pop])
        fronts = fast_non_dominated_sort(fits)
        rank = np.zeros(POP, dtype=int)
        for r, fr in enumerate(fronts):
            for i in fr:
                rank[i] = r
        cd = np.zeros(POP)
        for fr in fronts:
            if len(fr) > 1:
                cd[fr] = crowding_distance(fits[fr])
        offspring = []
        while len(offspring) < POP:
            a, b = NP_RNG.choice(POP, 2, replace=False)
            ta = a if (rank[a] < rank[b] or (rank[a] == rank[b] and cd[a] > cd[b])) else b
            c, d = NP_RNG.choice(POP, 2, replace=False)
            tb = c if (rank[c] < rank[d] or (rank[c] == rank[d] and cd[c] > cd[d])) else d
            c1, c2 = sbx_crossover(pop[ta], pop[tb])
            offspring.append(poly_mutate(c1))
            offspring.append(poly_mutate(c2))
        pop = np.array(offspring[:POP])
    fits = np.array([objectives(*decode(ind)) for ind in pop])
    fronts = fast_non_dominated_sort(fits)
    return pop, fits, fronts


def pick_archetypes(pop, fits, fronts):
    f0 = fronts[0]
    f0fits = fits[f0]
    # smooth = min f2 (conjunct); active = min f4 (max contour interest)
    smooth_i = f0[int(np.argmin(f0fits[:, 1]))]
    active_i = f0[int(np.argmin(f0fits[:, 3]))]
    # balanced = min sum of per-objective z-scores
    norm = (f0fits - f0fits.mean(0)) / (f0fits.std(0) + 1e-9)
    balanced_i = f0[int(np.argmin(norm.sum(1)))]
    return {
        "smooth": decode(pop[smooth_i]),
        "balanced": decode(pop[balanced_i]),
        "active": decode(pop[active_i]),
    }


# ---- Musicom rules helpers ---------------------------------------------------
def get_diatonic(degree, octave_shift=0):
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree) + octave_shift


def chord_triad_abs(degree):
    return [get_diatonic(degree), get_diatonic(degree + 2), get_diatonic(degree + 4)]


def quantize_to_chord_tone(raw_pitch, triad, lo=55, hi=96):
    candidates = set()
    for p in triad:
        for shift in (-24, -12, 0, 12, 24):
            cand = p + shift
            if lo <= cand <= hi:
                candidates.add(cand)
    if not candidates:
        candidates = set(triad)
    return min(candidates, key=lambda c: abs(c - raw_pitch))


def correct_voice_leading(triads):
    vl = VoiceLeadingRules(style="classical")
    corrected = [sorted(triads[0])]
    fixed = []
    for i in range(1, len(triads)):
        prev = corrected[-1]
        base = sorted(triads[i])
        candidates = [base]
        for rot in range(1, len(base)):
            candidates.append(vl._rotate_chord(base, rot))
        candidates = list(candidates) + [[p + 12 for p in c] for c in list(candidates)]
        best, best_score = candidates[0], None
        for cand in candidates:
            pv = vl.check_parallel_motion(prev, cand)
            hv = vl.check_hidden_fifths(prev, cand)
            n_viol = len(pv) + len(hv)
            dist = vl.calculate_voice_leading_distance(prev, cand)
            score = (n_viol, dist)
            if best_score is None or score < best_score:
                best_score, best = score, cand
        if best_score[0] > 0:
            fixed.append((i, best_score[0]))
        corrected.append(sorted(best))
    return corrected, fixed


def snap_grid(t, grid=120):
    return int(round(t / float(grid)) * grid)


def dedup_collisions(events):
    best = {}
    for e in events:
        key = (e.start_tick, e.pitch)
        if key not in best or (e.end_tick - e.start_tick) > (best[key].end_tick - best[key].start_tick):
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.end_tick))


def section_lead_events(melody, bar_start, bar_end, corr_triads, octave_shift=0):
    pitch, onset, dur = melody
    start_tick = bar_start * BAR
    end_tick = bar_end * BAR
    sec_ticks = (bar_end - bar_start) * BAR
    events = []
    for i in range(len(onset)):
        if onset[i] < start_tick or onset[i] >= end_tick:
            continue
        st_global = snap_grid(onset[i], 240)
        if st_global < start_tick or st_global >= end_tick:
            continue
        bar = int(st_global // BAR)
        triad = corr_triads[bar]
        raw = int(round(pitch[i])) + octave_shift
        qp = quantize_to_chord_tone(raw, triad, lo=62, hi=92)
        st = st_global - start_tick
        if st >= sec_ticks - 30:
            continue
        et = min(st + int(dur[i]), sec_ticks - 20)
        if et > st + 30:
            events.append(MusicEvent(pitch=qp, volume=86, start_tick=st, end_tick=et))
    return dedup_collisions(events)


def seal(ev_list, sec_ticks):
    if not ev_list:
        ev_list = [MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=sec_ticks)]
    last_end = max(e.end_tick for e in ev_list)
    if last_end < sec_ticks:
        ev_list.append(MusicEvent(pitch=0, volume=0, start_tick=last_end, end_tick=sec_ticks))
    return MusicUnit(events=ev_list)


# ---- Composition -------------------------------------------------------------
def compose():
    print("[evolve] NSGA-II population ...")
    pop, fits, fronts = evolve()
    print(f"[evolve] done. Pareto front rank-0 size: {len(fronts[0])}")
    arch = pick_archetypes(pop, fits, fronts)

    # Phase-1 raw melody = balanced archetype, split by section (single voice)
    def split_by_section(melody):
        pitch, onset, dur = melody
        sections = []
        acc = 0
        for s, nbars in enumerate(SECTION_BARS):
            start_tick = acc * BAR
            end_tick = (acc + nbars) * BAR
            sec_ticks = nbars * BAR
            cell = []
            for i in range(len(onset)):
                if onset[i] < start_tick or onset[i] >= end_tick:
                    continue
                st = max(0, int(onset[i] - start_tick))
                et = min(sec_ticks, int(onset[i] - start_tick + dur[i]))
                if et <= st:
                    continue
                cell.append(MusicEvent(pitch=int(round(pitch[i])), volume=86,
                                       start_tick=st, end_tick=et))
            cell = sorted(cell, key=lambda e: (e.start_tick, e.end_tick))
            if not cell or cell[-1].end_tick < sec_ticks:
                cell.append(MusicEvent(pitch=0, volume=0,
                                       start_tick=cell[-1].end_tick if cell else 0,
                                       end_tick=sec_ticks))
            sections.append(MusicUnit(events=cell))
            acc += nbars
        return sections

    phase1_sections = split_by_section(arch["balanced"])

    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawDraft", program=CELESTA.midi_program, channel=0)
    for sname, nbars in zip(SECTIONS, SECTION_BARS):
        p1.add_section(sname, bars=nbars)
    for s in range(len(SECTIONS)):
        p1.fill_voice_section("RawDraft", SECTIONS[s], phase1_sections[s])
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # Phase 2: harmony + voice-leading + chord-tone quantization + texture
    bar_triads = [sorted(chord_triad_abs(d)) for d in BAR_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    opt_triads = vl.optimize_voice_leading(bar_triads)
    corr_triads, fixed_report = correct_voice_leading(opt_triads)

    violations = []
    for i in range(len(corr_triads) - 1):
        violations += vl.check_parallel_motion(corr_triads[i], corr_triads[i + 1])
        violations += vl.check_hidden_fifths(corr_triads[i], corr_triads[i + 1])

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for sname, nbars in zip(SECTIONS, SECTION_BARS):
        composer.add_section(sname, bars=nbars)

    acc = 0
    for s, sname in enumerate(SECTIONS):
        nbars = SECTION_BARS[s]
        bar_start = acc
        bar_end = acc + nbars
        sec_ticks = nbars * BAR
        arch_name = SECTION_ARCH[sname]
        octave = SECTION_OCT[sname]

        lead_ev = section_lead_events(arch[arch_name], bar_start, bar_end,
                                      corr_triads, octave_shift=octave)

        pad_ev, bass_ev, harp_ev, drum_ev = [], [], [], []
        for bi in range(nbars):
            bar = bar_start + bi
            bs = bi * BAR
            triad = corr_triads[bar]
            r, th, f = triad
            # Pad (organ): sustained triad, root around D4
            pad_ev.append(MusicEvent(pitch=r, volume=64, start_tick=bs, end_tick=bs + BAR - 30))
            pad_ev.append(MusicEvent(pitch=th, volume=60, start_tick=bs, end_tick=bs + BAR - 30))
            pad_ev.append(MusicEvent(pitch=f, volume=60, start_tick=bs, end_tick=bs + BAR - 30))
            if sname in ("Peak", "Rise"):
                pad_ev.append(MusicEvent(pitch=r + 12, volume=58, start_tick=bs, end_tick=bs + BAR - 30))
            # Bass (cello): root + fifth, root one octave down
            bass_ev.append(MusicEvent(pitch=r - 12, volume=78, start_tick=bs, end_tick=bs + BAR - 40))
            bass_ev.append(MusicEvent(pitch=f - 12, volume=70, start_tick=bs + 960, end_tick=bs + 960 + 400))
            # Sparkle (harp): high arpeggio, 8th-note grid (quiet)
            pat = [r + 12, th + 12, f + 12, r + 24, f + 12, th + 12]
            offsets = [0, 240, 480, 960, 1200, 1440]
            for k, off in enumerate(offsets):
                harp_ev.append(MusicEvent(pitch=pat[k], volume=58,
                                          start_tick=bs + off, end_tick=bs + off + 220))
            # Drums (ch9): sparse cinematic
            kick = MidiPercussion.BASS_DRUM
            low_tom = MidiPercussion.LOW_TOM
            crash = MidiPercussion.CRASH_CYMBAL
            if sname in ("Build", "Rise", "Peak"):
                drum_ev.append(MusicEvent(pitch=kick, volume=72,
                                          start_tick=bs, end_tick=bs + 80))
                drum_ev.append(MusicEvent(pitch=low_tom, volume=68,
                                          start_tick=bs + 960, end_tick=bs + 1030))
            if sname == "Peak" and bi % 2 == 0:
                drum_ev.append(MusicEvent(pitch=crash, volume=80,
                                          start_tick=bs, end_tick=bs + 200))

        composer.fill_voice_section("Lead", sname, seal(lead_ev, sec_ticks))
        composer.fill_voice_section("Pad", sname, seal(pad_ev, sec_ticks))
        composer.fill_voice_section("Bass", sname, seal(bass_ev, sec_ticks))
        composer.fill_voice_section("Sparkle", sname, seal(harp_ev, sec_ticks))
        composer.fill_voice_section("Drums", sname, seal(drum_ev, sec_ticks))
        acc = bar_end

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 2 zero-drift FAILED: {msg}")
    composer.to_midi(MIDI_PATH)

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode=KEY_NAME)

    return (composer, violations, fixed_report, corr_triads,
            len(fronts[0]), arch, pop, fits, fronts)


if __name__ == "__main__":
    (composer, violations, fixed_report, triads, front_size,
     arch, pop, fits, fronts) = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, f"Phase 2 MIDI too small ({size2})"
    assert size1 > 40, f"Phase 1 MIDI too small ({size1})"
    print(f"[OK] Phase 1 MIDI: {PHASE1_PATH} ({size1} bytes)")
    print(f"[OK] Phase 2 MIDI: {MIDI_PATH} ({size2} bytes)")
    print(f"[OK] Pareto front rank-0 size: {front_size}")
    print(f"[OK] Voice-leading corrections: {len(fixed_report)} chord(s)")
    print(f"[OK] Parallel/hidden fifth violations: {len(violations)}")

    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + NSGA-II MOEPC (PRE-RULES raw draft)",
        parameters={"project": BASE, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "method": 98, "objectives": ["harmonic_quality", "melodic_quality",
                                                 "rhythmic_coherence", "voice_independence"],
                    "pop": POP, "generations": GEN, "genome_notes": N_NOTES,
                    "front_size": front_size, "archetype_used": "balanced",
                    "rules_applied": "NONE (pre-rules)"},
        notes="Phase 1 raw NSGA-II draft: balanced Pareto-front melody, single "
              "celesta voice, unquantized onsets + unquantized pitch (float genome).")

    write_provenance(
        MIDI_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + musicom rules",
        parameters={"project": BASE, "phase": 2, "key": KEY_NAME, "bpm": BPM,
                    "method": 98, "form": "cinematic-build",
                    "sections": SECTIONS, "bars": NUM_BARS,
                    "section_archetypes": SECTION_ARCH,
                    "section_octaves": SECTION_OCT,
                    "bar_degrees": BAR_DEGREES,
                    "instruments": {v: p for v, p in zip(VOICES, VOICE_PROGRAMS)},
                    "rules_applied": "per-bar chord-tone quantization, 120-tick grid snap, "
                                     "diatonic block harmony, voice-leading + correction"},
        notes="Phase 2 rules-processed ambient cinematic build. NSGA-II Pareto-front "
              "archetypes (smooth/balanced/active) mapped to form sections; chord-tone "
              "quantized + grid-snapped against D-Aeolian modal progression.")

    # Persist archetype objective vectors for the report
    import json
    summary = {
        "front_size": front_size,
        "objective_names": ["harmonic_quality", "melodic_quality", "rhythmic_coherence", "voice_independence"],
        "archetypes": {k: {"objectives": [round(float(x), 4) for x in objectives(*v)]}
                       for k, v in arch.items()},
        "bar_degrees": BAR_DEGREES,
        "voice_leading_corrections": len(fixed_report),
        "violations": len(violations),
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("[OK] Provenance sidecars + summary.json written.")
