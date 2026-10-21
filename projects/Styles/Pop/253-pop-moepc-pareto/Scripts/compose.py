# -*- coding: utf-8 -*-
"""253-pop-moepc-pareto — Multi-Objective Evolutionary Pareto Composition (Pop).

Autonomous nightly two-phase composition job (2026-10-20).

Style: Pop. Method 098 Multi-Objective Evolutionary Pareto Composition
(MOEPC), layer CONCRETE, paradigm Stochastic. Form: intro-verse-chorus-
bridge-outro (Intro 4 / Verse 8 / Chorus 8 / Bridge 4 / Outro 4 = 28 bars).

Method 098 essence (NSGA-II, Deb 2002): a population of candidate melodic
genomes is evolved against FOUR conflicting objectives — harmonic quality,
melodic quality (conjunctness), rhythmic coherence, and voice independence
(contour interest). Non-dominated sorting + crowding distance yields a Pareto
FRONT of trade-off melodies; the front itself supplies the macro-form
(smooth archetype -> Intro/Bridge/Outro, balanced -> Verse, active -> Chorus).

Phase 1 (raw generative draft): the "balanced" Pareto-front melody, single
piano voice, unquantized onsets + unquantized pitch (raw float genome),
no harmony, no chord-tone snapping -> -phase1.mid

Phase 2 (musicom rules): front archetypes mapped to sections, chord-tone
quantization per bar against a C-major I-V-vi-IV pop progression, 8th/16th
grid snap, synth pad + electric bass + glockenspiel sparkle + pop drum kit,
voice-leading optimization/correction, zero-drift gate. Dual-version export
(perfect grid-locked + seeded humanized) via workflows.humanize.export_dual.

Engine only: structures + workflows.unitmatrix_composer. NO raw mido authoring
(mido used ONLY for read-back audit).
"""
import json
import os
import sys

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import PIANO, SYNTH_PAD, ELECTRIC_BASS, GLOCKENSPIEL, DRUM_KIT

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree

import numpy as np

# ---- Composition parameters -------------------------------------------------
KEY_NAME = "C major (ionian)"
KEY_ROOT_PC = 0
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]      # C D E F G A B
KEY_PCS = [0, 2, 4, 5, 7, 9, 11]
KEY_ROOT_MIDI = 60                            # C4
BPM = 112
TPB = 480
BPB = 4
BAR = TPB * BPB                               # 1920
EIGHTH = 240
SIXTEENTH = 120

SECTIONS = ["Intro", "Verse", "Chorus", "Bridge", "Outro"]
SECTION_BARS = [4, 8, 8, 4, 4]
SECTION_TICKS = [b * BAR for b in SECTION_BARS]
NUM_BARS = sum(SECTION_BARS)                  # 28
TOTAL_TICKS = NUM_BARS * BAR                  # 53760

# C-major pop progression (I-V-vi-IV bestseller). 0-based degrees
# (I=0 ii=1 iii=2 IV=3 V=4 vi=5 vii=6). Section start roots vary:
# Intro I, Verse I, Chorus IV, Bridge vi, Outro I (four distinct openings).
BAR_DEGREES = [
    0, 0, 4, 4,                                # Intro  (I I V V)
    0, 4, 5, 3, 0, 4, 5, 3,                    # Verse  (I V vi IV x2)
    3, 4, 0, 5, 3, 4, 0, 4,                    # Chorus (IV V I vi IV V I V)
    5, 4, 3, 4,                                # Bridge (vi V IV V)
    0, 3, 4, 0,                                # Outro  (I IV V I)
]
assert len(BAR_DEGREES) == NUM_BARS, "bar-degree count mismatch"

SECTION_ARCH = {"Intro": "smooth", "Verse": "balanced", "Chorus": "active",
                "Bridge": "smooth", "Outro": "smooth"}
SECTION_OCT = {"Intro": -12, "Verse": 0, "Chorus": 0, "Bridge": 0, "Outro": -12}

VOICES = ["Lead", "Pad", "Bass", "Sparkle", "Drums"]
VOICE_PROGRAMS = [PIANO.midi_program, SYNTH_PAD.midi_program,
                  ELECTRIC_BASS.midi_program, GLOCKENSPIEL.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 9]
INSTR_NAMES = ["Piano", "Synth Pad", "Electric Bass", "Glockenspiel", "Drum Kit"]
PITCHED_VOICES = ["Lead", "Pad", "Bass", "Sparkle"]

SEED = 253
HZ_SEED = SEED * 101 + 1                      # deterministic humanize seed
STYLE = "pop"

PROJECT_DIR = "/opt/data/projects/Styles/Pop/253-pop-moepc-pareto"
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)
BASE = "253-pop-moepc-pareto"
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")
PERFECT_PATH = os.path.join(MIDI_DIR, BASE + "-perfect.mid")
HUMANIZED_PATH = os.path.join(MIDI_DIR, BASE + "-humanized.mid")


# ---- NSGA-II (Method 098 core) ----------------------------------------------
N_NOTES = 84                                   # 3/bar over 28 bars
DIM = N_NOTES * 3
POP = 64
GEN = 70
NP_RNG = np.random.default_rng(20261020)
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
    f4 = 1.0 - interest                           # voice independence
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
    smooth_i = f0[int(np.argmin(f0fits[:, 1]))]
    active_i = f0[int(np.argmin(f0fits[:, 3]))]
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
    # sort by onset (humanizer forward-clamp needs ascending order), then pad
    ev_list = sorted(ev_list, key=lambda e: (e.start_tick, e.pitch))
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
    p1.add_voice("RawDraft", program=PIANO.midi_program, channel=0)
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

        pad_ev, bass_ev, sparkle_ev, drum_ev = [], [], [], []
        for bi in range(nbars):
            bar = bar_start + bi
            bs = bi * BAR
            triad = corr_triads[bar]
            r, th, f = triad
            # Pad (synth): sustained triad around C4
            pad_ev.append(MusicEvent(pitch=r, volume=60, start_tick=bs, end_tick=bs + BAR - 30))
            pad_ev.append(MusicEvent(pitch=th, volume=56, start_tick=bs, end_tick=bs + BAR - 30))
            pad_ev.append(MusicEvent(pitch=f, volume=56, start_tick=bs, end_tick=bs + BAR - 30))
            if sname in ("Chorus", "Verse"):
                pad_ev.append(MusicEvent(pitch=r + 12, volume=54, start_tick=bs, end_tick=bs + BAR - 30))
            # Bass (electric): pop root/fifth pattern (root down an octave)
            bass_ev.append(MusicEvent(pitch=r - 12, volume=88, start_tick=bs, end_tick=bs + 400))
            bass_ev.append(MusicEvent(pitch=r - 12, volume=76, start_tick=bs + 960, end_tick=bs + 960 + 320))
            bass_ev.append(MusicEvent(pitch=f - 12, volume=72, start_tick=bs + 1440, end_tick=bs + 1440 + 240))
            # Sparkle (glockenspiel): high 8th-note arpeggio
            pat = [r + 12, th + 12, f + 12, r + 24, f + 12, th + 12]
            offsets = [0, 240, 480, 960, 1200, 1440]
            for k, off in enumerate(offsets):
                sparkle_ev.append(MusicEvent(pitch=pat[k], volume=60,
                                             start_tick=bs + off, end_tick=bs + off + 220))
            # Drums (ch9): pop backbeat groove
            kick = MidiPercussion.BASS_DRUM
            snare = MidiPercussion.ACOUSTIC_SNARE
            chh = MidiPercussion.CLOSED_HI_HAT
            crash = MidiPercussion.CRASH_CYMBAL
            # kick on beats 1 & 3
            drum_ev.append(MusicEvent(pitch=kick, volume=92, start_tick=bs, end_tick=bs + 80))
            drum_ev.append(MusicEvent(pitch=kick, volume=88, start_tick=bs + 960, end_tick=bs + 1040))
            # snare backbeat on beats 2 & 4
            drum_ev.append(MusicEvent(pitch=snare, volume=80, start_tick=bs + 480, end_tick=bs + 560))
            drum_ev.append(MusicEvent(pitch=snare, volume=80, start_tick=bs + 1440, end_tick=bs + 1520))
            # closed hi-hat 8ths
            for eigh in range(0, 8):
                drum_ev.append(MusicEvent(pitch=chh, volume=64,
                                          start_tick=bs + eigh * 240, end_tick=bs + eigh * 240 + 60))
            if sname == "Chorus" and bi == 0:
                drum_ev.append(MusicEvent(pitch=crash, volume=76, start_tick=bs, end_tick=bs + 240))
            if sname == "Intro":
                # sparse intro: kick only, no backbeat/hh
                drum_ev = [e for e in drum_ev
                           if e.pitch not in (snare, chh) and e.volume > 0]
                if not drum_ev:
                    drum_ev = [MusicEvent(pitch=kick, volume=70, start_tick=bs, end_tick=bs + 80)]

        composer.fill_voice_section("Lead", sname, seal(lead_ev, sec_ticks))
        composer.fill_voice_section("Pad", sname, seal(pad_ev, sec_ticks))
        composer.fill_voice_section("Bass", sname, seal(bass_ev, sec_ticks))
        composer.fill_voice_section("Sparkle", sname, seal(sparkle_ev, sec_ticks))
        composer.fill_voice_section("Drums", sname, seal(drum_ev, sec_ticks))
        acc = bar_end

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 2 zero-drift FAILED: {msg}")

    # ---- dual-version export: perfect + humanized ---------------------------
    hz_instruments = {
        "Lead": PIANO.humanize_dna,
        "Pad": SYNTH_PAD.humanize_dna,
        "Bass": ELECTRIC_BASS.humanize_dna,
        "Sparkle": GLOCKENSPIEL.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    hz = export_dual(composer, PERFECT_PATH, HUMANIZED_PATH,
                     style=STYLE, seed=HZ_SEED, bpm=BPM, instruments=hz_instruments)

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode=KEY_NAME)

    return (composer, violations, fixed_report, corr_triads, len(fronts[0]),
            arch, pop, fits, fronts, hz, bar_triads)


# ---- read-back audits (mido READING ONLY) ------------------------------------
def audit_midi(midi_path):
    import mido  # READING ONLY (analysis)
    mf = mido.MidiFile(midi_path)
    # map channel -> voice name (channel 9 = drums)
    ch_to_name = {}
    for v, ch in zip(VOICES, VOICE_CHANNELS):
        ch_to_name[ch] = v
    bar_pcs = []
    for b in range(NUM_BARS):
        d = BAR_DEGREES[b]
        pcs = set()
        for dd in (d, d + 2, d + 4):
            note = Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, dd)
            pcs.add(note % 12)
        bar_pcs.append(pcs)
    per_voice = {}
    for tr in mf.tracks:
        chan = None
        for msg in tr:
            if msg.type == "program_change":
                chan = msg.channel
                break
            if msg.type == "note_on" and msg.channel == 9:
                chan = 9
                break
        if chan is None:
            continue
        name = ch_to_name.get(chan)
        if name is None:
            continue
        t = 0
        notes = []
        for msg in tr:
            t += msg.time
            if msg.type == "note_on" and msg.velocity > 0 and msg.note > 0:
                notes.append((int(msg.note), t, int(msg.velocity)))
        pitched = name in PITCHED_VOICES
        off16 = sum(1 for (p, tt, v) in notes if tt % SIXTEENTH != 0)
        off8 = sum(1 for (p, tt, v) in notes if tt % EIGHTH != 0)
        out_scale = 0
        out_chord = 0
        if pitched:
            for (p, tt, v) in notes:
                pc = p % 12
                # Humanization never changes pitch; a boundary note jittered a
                # few ticks across a bar line still belongs to its authored bar.
                # Snap the onset to the nearest 8th grid (jitter <= 18t is always
                # < half an 8th = 120t) to recover the authored bar losslessly.
                bar = min(NUM_BARS - 1, (round(tt / EIGHTH) * EIGHTH) // BAR)
                if pc not in KEY_PCS:
                    out_scale += 1
                if pc not in bar_pcs[bar]:
                    out_chord += 1
        per_voice[name] = {"notes": len(notes), "off16": off16, "off8": off8,
                           "out_scale": out_scale, "out_chord": out_chord}
    return per_voice


def zero_drift(midi_path):
    import mido  # READING ONLY (analysis)
    mf = mido.MidiFile(midi_path)
    spans = [sum(msg.time for msg in tr) for tr in mf.tracks[1:]]
    return spans, len(spans)


# ---- main --------------------------------------------------------------------
def main():
    (composer, violations, fixed_report, triads, front_size, arch,
     pop, fits, fronts, hz, bar_triads) = compose()

    size1 = os.path.getsize(PHASE1_PATH)
    size_p = os.path.getsize(PERFECT_PATH)
    size_h = os.path.getsize(HUMANIZED_PATH)
    assert size1 > 40, f"phase1 too small ({size1})"
    assert size_p > 40, f"perfect too small ({size_p})"
    assert size_h > 40, f"humanized too small ({size_h})"

    aud_perf = audit_midi(PERFECT_PATH)
    aud_hum = audit_midi(HUMANIZED_PATH)
    spans_perf, nt_perf = zero_drift(PERFECT_PATH)
    spans_hum, nt_hum = zero_drift(HUMANIZED_PATH)

    section_roots = [BAR_DEGREES[sum(SECTION_BARS[:s])] for s in range(len(SECTIONS))]

    # front archetype objective values for the report
    def arch_fits(mel):
        return [round(float(o), 4) for o in objectives(*mel)]

    summary = {
        "project": BASE, "project_number": 253, "style": STYLE,
        "method_id": "098",
        "method_name": "Multi-Objective Evolutionary Pareto Composition (MOEPC)",
        "method_layer": "concrete",
        "form": "intro-verse-chorus-bridge-outro (4+8+8+4+4 = 28 bars)",
        "key": KEY_NAME, "key_pcs": KEY_PCS, "bpm": BPM, "meter": "4/4",
        "bar_ticks": BAR, "total_bars": NUM_BARS, "total_ticks": TOTAL_TICKS,
        "sections": [{"name": n, "bars": b} for n, b in zip(SECTIONS, SECTION_BARS)],
        "section_start_roots": section_roots,
        "progression_degrees": BAR_DEGREES,
        "pop": POP, "generations": GEN, "genome_notes": N_NOTES,
        "front_size": front_size,
        "archetypes": {k: {"f1_harmonic": arch_fits(v)[0], "f2_melodic": arch_fits(v)[1],
                           "f3_rhythmic": arch_fits(v)[2], "f4_indep": arch_fits(v)[3],
                           "notes": len(v[0])}
                       for k, v in arch.items()},
        "voices": [{"name": n, "program": p, "channel": c, "instrument": i,
                    "pitched": n in PITCHED_VOICES}
                   for n, p, c, i in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS, INSTR_NAMES)],
        "perfect_audit": aud_perf, "humanized_audit": aud_hum,
        "zero_drift": {"perfect_tracks": nt_perf, "humanized_tracks": nt_hum,
                       "perfect_span": spans_perf, "humanized_span": spans_hum},
        "voice_leading": {"corrections": len(fixed_report),
                          "parallel_hidden_fifth_violations": len(violations)},
        "humanize": {"style": STYLE, "seed": HZ_SEED,
                     "per_voice": {k: {"seed": v["seed"], "n_notes": v["n_notes"],
                                       "mean_abs_shift_ticks": v["mean_abs_shift_ticks"],
                                       "max_abs_shift_ticks": v["max_abs_shift_ticks"],
                                       "mean_abs_vel_delta": v["mean_abs_vel_delta"]}
                                   for k, v in hz.items()}},
        "seed": SEED,
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("=== GRID + HARMONY AUDIT ===")
    for v in VOICES:
        p = aud_perf.get(v, {})
        h = aud_hum.get(v, {})
        print(f"  {v:8s} perfect(off16={p.get('off16')},off8={p.get('off8')},"
              f"out_scale={p.get('out_scale')},out_chord={p.get('out_chord')})  "
              f"humanized(off16={h.get('off16')},off8={h.get('off8')},"
              f"out_scale={h.get('out_scale')},out_chord={h.get('out_chord')})")
    print("  section start roots:", section_roots)
    print("  zero-drift perfect:", nt_perf, "tracks len", set(spans_perf))
    print("  zero-drift humanized:", nt_hum, "tracks len", set(spans_hum))
    print("  front size:", front_size, "VL corrections:", len(fixed_report),
          "violations:", len(violations))
    for v in VOICES:
        h = hz[v]
        print(f"  hz[{v}] seed={h['seed']} mean={h['mean_abs_shift_ticks']}t "
              f"max={h['max_abs_shift_ticks']}t vel={h['mean_abs_vel_delta']}")

    print("PHASE1", PHASE1_PATH, size1)
    print("PERFECT", PERFECT_PATH, size_p)
    print("HUMANIZED", HUMANIZED_PATH, size_h)

    # ---- provenance sidecars ------------------------------------------------
    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + NSGA-II MOEPC (PRE-RULES raw draft)",
        parameters={"project": BASE, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "method": "098", "objectives": ["harmonic_quality", "melodic_quality",
                                                     "rhythmic_coherence", "voice_independence"],
                    "pop": POP, "generations": GEN, "genome_notes": N_NOTES,
                    "front_size": front_size, "archetype_used": "balanced",
                    "style": STYLE, "seed": SEED, "form": "intro-verse-chorus-bridge-outro",
                    "total_bars": NUM_BARS, "rules_applied": "NONE (pre-rules)"},
        notes="Phase 1 raw NSGA-II draft: balanced Pareto-front melody, single "
              "piano voice, unquantized onsets + unquantized pitch (float genome).")
    write_provenance(
        PERFECT_PATH, classification=AI_ASSISTED,
        generator="098 MOEPC + musicom rules (grid-locked)",
        parameters={"project": BASE, "phase": 2, "version": "perfect", "key": KEY_NAME,
                    "bpm": BPM, "method": "098", "style": STYLE, "seed": SEED,
                    "humanize_seed": HZ_SEED, "form": "intro-verse-chorus-bridge-outro",
                    "total_bars": NUM_BARS, "voices": VOICES,
                    "instruments": INSTR_NAMES, "front_size": front_size},
        notes="Phase 2 perfect: grid-locked concrete layer (no humanization). "
              "Pareto archetypes mapped to sections, chord-tone quantized per bar "
              "(C-major I-V-vi-IV), 8th/16th grid snap, voice-leading optimized, "
              "zero-drift gated.")
    write_provenance(
        HUMANIZED_PATH, classification=AI_ASSISTED,
        generator="098 MOEPC + musicom rules + humanize",
        parameters={"project": BASE, "phase": 2, "version": "humanized", "key": KEY_NAME,
                    "bpm": BPM, "method": "098", "style": STYLE, "seed": SEED,
                    "humanize_seed": HZ_SEED, "form": "intro-verse-chorus-bridge-outro",
                    "total_bars": NUM_BARS, "voices": VOICES,
                    "instruments": INSTR_NAMES, "front_size": front_size},
        notes="Phase 2 humanized: same concrete layer + style-derived seeded "
              "humanization (per-instrument DNA). Zero-drift safe.")
    return summary


if __name__ == "__main__":
    main()
