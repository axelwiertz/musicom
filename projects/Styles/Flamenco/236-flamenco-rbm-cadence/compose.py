# -*- coding: utf-8 -*-
"""236-flamenco-rbm-cadence — Restricted Boltzmann Machine Composition (Method 074).

Nightly two-phase composition job (2026-10-11).

Style: Flamenco. Method 074 Restricted Boltzmann Machine Composition (RBM-C),
layer CONCRETE, paradigm AI-Driven (energy-based / likelihood-trained).
Form: intro-falseta-letra-falseta-cierre (Intro 4 / Falseta 8 / Letra 8 /
Falseta 8 / Cierre 4 = 32 bars).

Method 074 essence (Hinton 2006, Contrastive Divergence): a bipartite
visible<->hidden network over a per-voice piano-roll learns an energy
landscape E(v,h) = -v'Wh - b'v - c'h. Visible units = (beat, pitch-bin)
activations; hidden units = learned chord/motif/register features. Composing
= block Gibbs sampling from the Boltzmann distribution; the chord/section
cadence (Andalusian Am-G-F-Em) supplies the macro-form conditioning schedule.

Phase 1 (raw generative draft): block-Gibbs-sampled piano-roll, single guitar
voice, unquantized onsets (off-grid jitter) + unquantized pitch (chromatic
bins, NOT scale-filtered, NOT chord-tone snapped) -> -phase1.mid

Phase 2 (musicom rules): per-bar chord-tone quantization against the
descending-tetrachord Andalusian cadence, 120/240-tick grid snap, full
texture (lead guitar falseta + compas rasgueado guitar + double-bass
descending roots + flute falseta arpeggios + palmas/cajon), voice-leading
check, zero-drift gate -> 236-flamenco-rbm-cadence.mid
"""
import json
import os
import sys

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import ACOUSTIC_GUITAR, DOUBLE_BASS, FLUTE

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from rules.voice_leading import VoiceLeadingRules

import numpy as np

# ---- Composition parameters -------------------------------------------------
KEY_NAME = "A Aeolian (Andalusian cadence)"
KEY_PCS = {9, 11, 0, 2, 4, 5, 7}          # A B C D E F G
BPM = 108
TPB = 480
BPB = 4
BAR = TPB * BPB                            # 1920 ticks

SECTIONS = ["Intro", "Falseta1", "Letra", "Falseta2", "Cierre"]
SECTION_BARS = [4, 8, 8, 8, 4]
NUM_BARS = sum(SECTION_BARS)               # 32
TOTAL_TICKS = NUM_BARS * BAR

# Andalusian cadence (descending tetrachord): Am -> G -> F -> Em
CADENCE = [
    {"name": "Am", "root": 57, "triad": [57, 60, 64], "pcs": {9, 0, 4}, "quality": "min"},
    {"name": "G",  "root": 55, "triad": [55, 59, 62], "pcs": {7, 11, 2}, "quality": "maj"},
    {"name": "F",  "root": 53, "triad": [53, 57, 60], "pcs": {5, 9, 0}, "quality": "maj"},
    {"name": "Em", "root": 52, "triad": [52, 55, 59], "pcs": {4, 7, 11}, "quality": "min"},
]
BAR_CHORD = list(range(4)) * 8             # 32 bars, index into CADENCE
assert len(BAR_CHORD) == NUM_BARS

VOICES = ["Lead", "Compas", "Bass", "Flute", "Palmas"]
PROGRAMS = [ACOUSTIC_GUITAR.midi_program, ACOUSTIC_GUITAR.midi_program,
            DOUBLE_BASS.midi_program, FLUTE.midi_program, 0]
CHANNELS = [0, 1, 2, 3, 9]

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
os.makedirs(MIDI_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
BASE = "236-flamenco-rbm-cadence"
MIDI_PATH = os.path.join(MIDI_DIR, BASE + ".mid")
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")

# ---- RBM (Method 074 core) ---------------------------------------------------
T = NUM_BARS * 4            # 128 time columns (1 per beat)
PITCH_LO = 57               # A3
PITCH_HI = 76               # E5
P = PITCH_HI - PITCH_LO + 1  # 20 pitch bins (chromatic)
V = T * P                   # visible units
H = 48                      # hidden units
RNG = np.random.default_rng(20261011)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def chord_tones_midi(cidx, lo=PITCH_LO, hi=PITCH_HI):
    pcs = CADENCE[cidx]["pcs"]
    return [m for m in range(lo, hi + 1) if m % 12 in pcs]


def make_seed():
    """Synthetic flamenco-melody training sample (128 beats x 20 bins)."""
    roll = np.zeros((T, P), dtype=np.float64)
    for beat in range(T):
        cidx = BAR_CHORD[beat // 4]
        tones = chord_tones_midi(cidx)
        r = RNG.random()
        if r < 0.42:                       # chord-tone onset
            note = int(RNG.choice(tones))
            b = note - PITCH_LO
            if 0 <= b < P:
                roll[beat, b] = 1.0
        elif r < 0.50:                     # passing/neighbor (scale-adjacent)
            note = int(RNG.choice(tones)) + int(RNG.choice([-2, -1, 1, 2]))
            b = note - PITCH_LO
            if 0 <= b < P:
                roll[beat, b] = 1.0
    return roll


def train_rbm(seeds, epochs=28, lr=0.08, cd_k=1):
    W = RNG.normal(0.0, 0.05, (V, H)).astype(np.float64)
    bv = np.zeros(V, dtype=np.float64)
    bh = np.zeros(H, dtype=np.float64)
    for _ in range(epochs):
        for v0 in seeds:
            v0 = v0.reshape(-1)
            # positive phase
            h_prob = sigmoid(v0 @ W + bh)
            h_act = (RNG.random(H) < h_prob).astype(np.float64)
            pos = np.outer(v0, h_prob)
            # negative phase (CD-k)
            v = v0.copy()
            for _ in range(cd_k):
                hp = sigmoid(v @ W + bh)
                h = (RNG.random(H) < hp).astype(np.float64)
                vp = sigmoid(h @ W.T + bv)
                v = (RNG.random(V) < vp).astype(np.float64)
            h_final = sigmoid(v @ W + bh)
            neg = np.outer(v, h_final)
            W += lr * (pos - neg)
            bv += lr * (v0 - v)
            bh += lr * (h_prob - h_final)
    return W, bv, bh


def gibbs_sample(W, bv, bh, steps=120):
    v = (RNG.random(V) < 0.5).astype(np.float64)
    vp = np.full(V, 0.5, dtype=np.float64)
    for _ in range(steps):
        hp = sigmoid(v @ W + bh)
        h = (RNG.random(H) < hp).astype(np.float64)
        vp = sigmoid(h @ W.T + bv)
        v = (RNG.random(V) < vp).astype(np.float64)
    return v.reshape(T, P), vp.reshape(T, P)


# ---- Musicom rules helpers ---------------------------------------------------
def quantize_chord(raw, cidx, lo, hi):
    tones = chord_tones_midi(cidx, lo, hi)
    if not tones:
        tones = [raw]
    return min(tones, key=lambda t: abs(t - raw))


def snap_grid(t, grid=120):
    return int(round(t / float(grid)) * grid)


def dedup(events):
    best = {}
    for e in events:
        k = (e.start_tick, e.pitch)
        if k not in best or (e.end_tick - e.start_tick) > (best[k].end_tick - best[k].start_tick):
            best[k] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.end_tick))


def seal(ev_list, sec_ticks):
    if not ev_list:
        ev_list = [MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=sec_ticks)]
    last_end = max(e.end_tick for e in ev_list)
    if last_end < sec_ticks:
        ev_list.append(MusicEvent(pitch=0, volume=0, start_tick=last_end, end_tick=sec_ticks))
    return MusicUnit(events=ev_list)


def compose():
    # ---- Phase 1: raw RBM draft -------------------------------------------
    print("[rbm] building seeds ...")
    seeds = [make_seed() for _ in range(12)]
    print("[rbm] training (V=%d H=%d) ..." % (V, H))
    W, bv, bh = train_rbm(seeds)
    print("[rbm] gibbs sampling ...")
    roll, prob = gibbs_sample(W, bv, bh)

    # thin to 1 note per beat (keep most-confident active bin)
    cells_by_beat = {}
    for beat in range(T):
        for b in range(P):
            if roll[beat, b] > 0.5:
                cells_by_beat.setdefault(beat, []).append((prob[beat, b], PITCH_LO + b))
    raw_cells = []
    for beat in sorted(cells_by_beat):
        a, midi = max(cells_by_beat[beat])   # keep most-confident bin per beat
        raw_cells.append((beat, midi))

    def split_raw(cells):
        sections = []
        acc = 0
        for nbars in SECTION_BARS:
            sec_ticks = nbars * BAR
            start_beat = acc * 4
            end_beat = (acc + nbars) * 4
            ev = []
            for (beat, midi) in cells:
                if beat < start_beat or beat >= end_beat:
                    continue
                st = max(0, (beat - start_beat) * 480 + int(RNG.integers(-70, 71)))
                dur = int(RNG.integers(200, 500))
                et = min(sec_ticks, st + dur)
                if et <= st:
                    continue
                ev.append(MusicEvent(pitch=midi, volume=86, start_tick=st, end_tick=et))
            ev = sorted(ev, key=lambda e: (e.start_tick, e.end_tick))
            if not ev or ev[-1].end_tick < sec_ticks:
                ev.append(MusicEvent(pitch=0, volume=0,
                                     start_tick=ev[-1].end_tick if ev else 0,
                                     end_tick=sec_ticks))
            sections.append(MusicUnit(events=ev))
            acc += nbars
        return sections

    phase1_sections = split_raw(raw_cells)

    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    p1.add_voice("RawDraft", program=ACOUSTIC_GUITAR.midi_program, channel=0)
    for sname, nbars in zip(SECTIONS, SECTION_BARS):
        p1.add_section(sname, bars=nbars)
    for s in range(len(SECTIONS)):
        p1.fill_voice_section("RawDraft", SECTIONS[s], phase1_sections[s])
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError("Phase 1 zero-drift FAILED: " + msg1)
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: musicom rules post-process -------------------------------
    bar_triads = [sorted(CADENCE[c]["triad"]) for c in BAR_CHORD]
    vl = VoiceLeadingRules(style="classical")
    violations = []
    for i in range(len(bar_triads) - 1):
        violations += vl.check_parallel_motion(bar_triads[i], bar_triads[i + 1])
        violations += vl.check_hidden_fifths(bar_triads[i], bar_triads[i + 1])

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for name, prog, ch in zip(VOICES, PROGRAMS, CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for sname, nbars in zip(SECTIONS, SECTION_BARS):
        composer.add_section(sname, bars=nbars)

    acc = 0
    for s, sname in enumerate(SECTIONS):
        nbars = SECTION_BARS[s]
        start_beat = acc * 4
        sec_ticks = nbars * BAR

        lead_ev, compas_ev, bass_ev, flute_ev, palmas_ev = [], [], [], [], []

        # Lead: RBM melody, chord-tone quantized + 120-grid snapped
        for (beat, midi) in raw_cells:
            if beat < start_beat or beat >= start_beat + nbars * 4:
                continue
            bar = beat // 4
            cidx = BAR_CHORD[bar]
            rel = (beat - start_beat) * 480
            st = snap_grid(rel, 120)
            if st >= sec_ticks - 30:
                continue
            qp = quantize_chord(midi, cidx, 62, 88)
            et = min(st + 360, sec_ticks - 20)
            lead_ev.append(MusicEvent(pitch=qp, volume=88, start_tick=st, end_tick=et))

        # Compas: rasgueado strums (quarter hits + 8th off-beat doubles)
        for bi in range(nbars):
            bar = acc + bi
            cidx = BAR_CHORD[bar]
            tr = CADENCE[cidx]["triad"]
            bs = bi * BAR
            for (off, vel) in [(0, 72), (480, 64), (960, 70), (1440, 64)]:
                compas_ev.append(MusicEvent(pitch=tr[0], volume=vel, start_tick=bs + off, end_tick=bs + off + 200))
                compas_ev.append(MusicEvent(pitch=tr[1], volume=vel, start_tick=bs + off, end_tick=bs + off + 200))
                compas_ev.append(MusicEvent(pitch=tr[2], volume=vel, start_tick=bs + off, end_tick=bs + off + 200))
            if sname.startswith("Falseta"):
                for (off, vel) in [(240, 58), (720, 56), (1200, 58), (1680, 56)]:
                    compas_ev.append(MusicEvent(pitch=tr[0], volume=vel, start_tick=bs + off, end_tick=bs + off + 160))
                    compas_ev.append(MusicEvent(pitch=tr[1] + 12, volume=vel, start_tick=bs + off, end_tick=bs + off + 160))

        # Bass: descending roots (root on 1, fifth on 3), double bass
        for bi in range(nbars):
            bar = acc + bi
            cidx = BAR_CHORD[bar]
            tr = CADENCE[cidx]["triad"]
            bs = bi * BAR
            bass_ev.append(MusicEvent(pitch=tr[0] - 12, volume=82, start_tick=bs, end_tick=bs + 700))
            bass_ev.append(MusicEvent(pitch=tr[2] - 12, volume=74, start_tick=bs + 960, end_tick=bs + 960 + 600))

        # Flute: falseta arpeggios (Falseta sections only), chord tones
        if sname.startswith("Falseta"):
            for bi in range(nbars):
                bar = acc + bi
                cidx = BAR_CHORD[bar]
                bs = bi * BAR
                tones = [t for t in chord_tones_midi(cidx, 72, 96)]
                seq = [tones[0], tones[1], tones[2], tones[3], tones[2], tones[1],
                       tones[0], tones[1], tones[2], tones[3], tones[4], tones[3]]
                offs = [i * 120 for i in range(12)]
                for k, off in enumerate(offs):
                    flute_ev.append(MusicEvent(pitch=seq[k % len(seq)], volume=62,
                                               start_tick=bs + off, end_tick=bs + off + 110))

        # Palmas (ch9): cajon kick + hand claps + claves
        for bi in range(nbars):
            bs = bi * BAR
            kick = MidiPercussion.BASS_DRUM
            clap = MidiPercussion.HAND_CLAP
            clave = MidiPercussion.CLAVES
            palmas_ev.append(MusicEvent(pitch=kick, volume=74, start_tick=bs, end_tick=bs + 80))
            palmas_ev.append(MusicEvent(pitch=kick, volume=70, start_tick=bs + 960, end_tick=bs + 1040))
            palmas_ev.append(MusicEvent(pitch=clap, volume=72, start_tick=bs + 480, end_tick=bs + 540))
            palmas_ev.append(MusicEvent(pitch=clap, volume=72, start_tick=bs + 1440, end_tick=bs + 1500))
            if sname.startswith("Falseta") or sname == "Letra":
                for off in (240, 720, 1200, 1680):
                    palmas_ev.append(MusicEvent(pitch=clave, volume=60, start_tick=bs + off, end_tick=bs + off + 70))

        composer.fill_voice_section("Lead", sname, seal(lead_ev, sec_ticks))
        composer.fill_voice_section("Compas", sname, seal(compas_ev, sec_ticks))
        composer.fill_voice_section("Bass", sname, seal(bass_ev, sec_ticks))
        composer.fill_voice_section("Flute", sname, seal(flute_ev, sec_ticks))
        composer.fill_voice_section("Palmas", sname, seal(palmas_ev, sec_ticks))
        acc += nbars

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError("Phase 2 zero-drift FAILED: " + msg)
    composer.to_midi(MIDI_PATH)

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode=KEY_NAME)

    return composer, violations, raw_cells, roll


if __name__ == "__main__":
    composer, violations, raw_cells, roll = compose()

    size2 = os.path.getsize(MIDI_PATH)
    size1 = os.path.getsize(PHASE1_PATH)
    assert size2 > 40, "Phase 2 MIDI too small (%d)" % size2
    assert size1 > 40, "Phase 1 MIDI too small (%d)" % size1
    print("[OK] Phase 1 MIDI: %s (%d bytes)" % (PHASE1_PATH, size1))
    print("[OK] Phase 2 MIDI: %s (%d bytes)" % (MIDI_PATH, size2))
    print("[OK] Raw RBM notes sampled: %d" % len(raw_cells))
    print("[OK] Voice-leading parallel/hidden-5th violations (idiomatic parallel tetrachord): %d" % len(violations))

    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + RBM-C (PRE-RULES raw draft)",
        parameters={"project": BASE, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "method": 74, "visible_units": V, "hidden_units": H,
                    "cd_k": 1, "gibbs_steps": 90, "seeds": 12,
                    "rules_applied": "NONE (pre-rules)"},
        notes="Phase 1 raw RBM block-Gibbs draft: chromatic pitch bins, unquantized "
              "onsets (off-grid jitter), single nylon-guitar voice, no harmony, no "
              "chord-tone snapping.")

    write_provenance(
        MIDI_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + musicom rules",
        parameters={"project": BASE, "phase": 2, "key": KEY_NAME, "bpm": BPM,
                    "method": 74, "form": "intro-falseta-letra-falseta-cierre",
                    "sections": SECTIONS, "bars": NUM_BARS,
                    "cadence": [c["name"] for c in CADENCE],
                    "bar_chord": BAR_CHORD,
                    "instruments": {v: p for v, p in zip(VOICES, PROGRAMS)},
                    "rules_applied": "per-bar chord-tone quantization, 120/240-tick grid snap, "
                                     "diatonic Andalusian cadence harmony, voice-leading check"},
        notes="Phase 2 rules-processed flamenco. RBM-sampled melody chord-tone quantized "
              "+ grid-snapped against the descending Andalusian cadence (Am-G-F-Em); "
              "compas rasgueado guitar + double-bass descending roots + flute falseta + "
              "palmas/cajon percussion.")

    summary = {
        "method": 74,
        "method_name": "Restricted Boltzmann Machine Composition (RBM-C)",
        "layer": "concrete",
        "paradigm": "AI-Driven (energy-based)",
        "visible_units": V, "hidden_units": H,
        "raw_notes": len(raw_cells),
        "voice_leading_violations": len(violations),
        "cadence": [c["name"] for c in CADENCE],
    }
    with open(os.path.join(ANALYSIS_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print("[OK] provenance + summary.json written.")
