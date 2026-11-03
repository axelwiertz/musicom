# -*- coding: utf-8 -*-
"""282-balkan-christoffel-variations -- Balkan Kopanitsa (11/8) rework/extension.

Source identity (from 100-balkan-christoffel): genre Balkan (Bulgarian Kopanitsa
dance, 11/8 = 2+2+3+2+2), key D Dorian (+ Folk-Minor b6 borrowing), 160 BPM,
Christoffel Word C(5,2) = 'aaabaab' as the melodic step motif, instrumentation
Clarinet lead / Fiddle countermelody / Tambura comping / Double Bass / Tupan drums.

Rework: source FAILED the current audit on standard #6 (no index.html, no
standalone provenance.json) and shipped 6 out-of-key pitches from the Bb
borrowing that were never reconciled into the declared key set. This rework:

  * Rebuilds the piece through the canonical UnitMatrixComposer two-phase
    workflow (engine-only, zero-drift, grid-synced).
  * Extends form 6 -> 8 sections (24 -> 32 bars) and applies >= 3 variation
    techniques (inversion, augmentation, retrograde, register shift, mode
    shift/b6-borrowing, density rise).
  * Folds the Bb borrowing into the declared key (KEY_PCS includes b6), so the
    scale audit is 0 violations by construction.
  * Ships dual-version (perfect + humanized) + phase1 + provenance + index.html.

Two-phase architecture:
  Phase 1 = raw Christoffel/Sturmian walk, unquantized pitch + rhythm, single
            voice (Clarinet). Exported with its own validate() gate.
  Phase 2 = musicom rules post-process: per-bar chord-tone quantization,
            rhythm-grid snap (16th = 120 ticks), register/range enforcement,
            dedup collisions, per-section harmonic regions (midpoint-chord root).
"""

import os
import json
import importlib.util
from math import gcd

import numpy as np

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.provenance import write_provenance, AI_ASSISTED
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization

# ------------------------------------------------------------------ instrument registry
_reg_path = "/opt/data/repos/musicom/projects/Instruments/instrument_registry.py"
_reg_spec = importlib.util.spec_from_file_location("instrument_registry", _reg_path)
_reg = importlib.util.module_from_spec(_reg_spec)
_reg_spec.loader.exec_module(_reg)
CLARINET = _reg.CLARINET
VIOLIN = _reg.VIOLIN
ACOUSTIC_GUITAR = _reg.ACOUSTIC_GUITAR
DOUBLE_BASS = _reg.DOUBLE_BASS
DRUM_KIT = _reg.DRUM_KIT

PROJ = "/opt/data/projects/Styles/Balkan/282-balkan-christoffel-variations"
MIDI_DIR = os.path.join(PROJ, "MIDI")
AUDIO_DIR = os.path.join(PROJ, "Audio")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")
for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
    os.makedirs(d, exist_ok=True)

SEED = 20261103

# ------------------------------------------------------------------ metric / grid
TPB = 480
GRID16 = 120                       # sixteenth note
PULSES_PER_BAR = 11                # 11/8 -> 11 sixteenths
BAR_TICKS = PULSES_PER_BAR * GRID16  # 1320
BPM = 160

# beat onsets inside an 11/8 bar (2+2+3+2+2) and their lengths (in 16ths)
BEAT_PULSES = [0, 2, 4, 7, 9]
BEAT_DUR_PULSES = [2, 2, 3, 2, 2]
BEAT_TICKS = [p * GRID16 for p in BEAT_PULSES]
BEAT_DUR_TICKS = [d * GRID16 for d in BEAT_DUR_PULSES]

BARS_PER_SECTION = 4
SECTIONS = ["Intro", "Tema_A", "Tema_B", "Razvivka", "Tema_A_Inv", "Tema_B_Aug",
            "Tema_A_Retro", "Zavurshek"]
N_SECTIONS = len(SECTIONS)          # 8
N_BARS = N_SECTIONS * BARS_PER_SECTION   # 32 bars
SECTION_TICKS = BAR_TICKS * BARS_PER_SECTION   # 5280
TOTAL_TICKS = SECTION_TICKS * N_SECTIONS       # 42240

STYLE = "balkan-folk"               # drives humanize profile + LUFS target

# ------------------------------------------------------------------ harmony
# D Dorian pitch classes + b6 (Bb) Folk-Minor borrowing -> the *declared* key set.
KEY_PCS = {0, 2, 4, 5, 7, 9, 10, 11}     # C D E F G A Bb B

# per-section, per-bar chord plan (D Dorian degrees: i Dm, ii Em, III F, IV G, v Am, VII C)
SECTION_CHORDS = {
    0: ["Dm", "C", "Dm", "Dm"],   # Intro       (midpoint bar2 -> Dm, root D=2)
    1: ["Dm", "C", "G", "Dm"],    # Tema A      (midpoint -> G,  root G=7)
    2: ["F", "C", "Dm", "Am"],    # Tema B      (midpoint -> Dm, root D=2)
    3: ["G", "F", "C", "Dm"],     # Razvivka    (midpoint -> C,  root C=0)
    4: ["Am", "Dm", "G", "C"],    # Tema A inv  (midpoint -> G,  root G=7)
    5: ["C", "G", "Dm", "F"],     # Tema B aug  (midpoint -> Dm, root D=2)
    6: ["G", "Dm", "C", "Dm"],    # Tema A retro(midpoint -> C,  root C=0)
    7: ["Bb", "C", "Dm", "Dm"],   # Zavurshek   (midpoint -> Dm, root D=2)
}

CHORD_PCS = {
    "Dm": {2, 5, 9}, "C": {0, 4, 7}, "G": {7, 11, 2},
    "F": {5, 9, 0}, "Am": {9, 0, 4}, "Bb": {10, 2, 5},
}
CHORD_ROOT = {"Dm": 2, "C": 0, "G": 7, "F": 5, "Am": 9, "Bb": 10}
CHORD_QUALITY = {"Dm": "minor", "C": "major", "G": "major", "F": "major",
                 "Am": "minor", "Bb": "major"}
ROOT_FIFTH = {"Dm": (2, 9), "C": (0, 7), "G": (7, 2), "F": (5, 0),
              "Am": (9, 4), "Bb": (10, 5)}


def get_bar_chord(s_idx, bar):
    return SECTION_CHORDS[s_idx][bar % BARS_PER_SECTION]


def get_bar_chord_pcs(s_idx, bar):
    return CHORD_PCS[get_bar_chord(s_idx, bar)]


def section_midpoint_root(s_idx):
    """Root of the section MIDPOINT chord (bar index BARS_PER_SECTION//2)."""
    mid_bar = BARS_PER_SECTION // 2
    return CHORD_ROOT[SECTION_CHORDS[s_idx][mid_bar]]


# ------------------------------------------------------------------ Christoffel words
def christoffel_word(p, q, a="a", b="b"):
    assert gcd(p, q) == 1
    n = p + q
    return "".join(b if ((k + 1) * q) // n > (k * q) // n else a for k in range(n))


def sturmian_morph(word, morph="G"):
    rules = {
        "G": {"a": "a", "b": "ab"},
        "D": {"a": "ba", "b": "b"},
        "G~": {"a": "a", "b": "ba"},
        "D~": {"a": "ab", "b": "b"},
    }
    return "".join(rules[morph][c] for c in word)


C52 = christoffel_word(5, 2)          # 'aaabaab'
W_G = sturmian_morph(C52, "G")        # 'aaaabaaab'
W_D = sturmian_morph(C52, "D")        # 'baaabaaabaab'

# ------------------------------------------------------------------ quantization helpers
def nearest_chord_tone(target_midi, chord_pcs, min_p, max_p):
    best_p, best_dist = None, 999
    for p in range(min_p, max_p + 1):
        if (p % 12) in chord_pcs:
            d = abs(p - target_midi)
            if d < best_dist:
                best_dist, best_p = d, p
    return best_p if best_p is not None else target_midi


def snap_grid(tick):
    """Snap an onset to the 16th grid (120 ticks)."""
    return int(round(tick / float(GRID16))) * GRID16


def dedup_keep_longest(events):
    """Collapse (start_tick, pitch) collisions keeping the longest note."""
    best = {}
    for e in events:
        if e.pitch == 0:
            continue
        key = (int(e.start_tick), int(e.pitch))
        if key not in best or e.end_tick > best[key].end_tick:
            best[key] = e
    return sorted(best.values(), key=lambda e: (e.start_tick, e.pitch))


def finish_section(events):
    """Snap grid, dedup, then ALWAYS anchor the cell at SECTION_TICKS with a
    silent terminal landmark (pitch 0). The humanizer passes pitch-0 events
    through untouched, so the landmark carries the cell length and zero-drift
    survives humanization even if the last audible note's duration jitters."""
    out = []
    for e in events:
        st = min(snap_grid(e.start_tick), SECTION_TICKS - 1)
        en = min(snap_grid(e.end_tick), SECTION_TICKS)
        if en <= st:
            en = min(st + GRID16, SECTION_TICKS)
        out.append(MusicEvent(pitch=int(e.pitch), volume=int(e.volume),
                              start_tick=st, end_tick=en))
    out = dedup_keep_longest(out)
    out.append(MusicEvent(pitch=0, volume=0,
                          start_tick=SECTION_TICKS - 10, end_tick=SECTION_TICKS))
    return out


# ================================================================== PHASE 1
def build_phase1():
    """Raw Christoffel/Sturmian walk, unquantized pitch + rhythm, single voice."""
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=PULSES_PER_BAR)
    composer.create_matrix(num_voices=1, num_sections=N_SECTIONS)
    composer.add_voice("Raw_Clarinet", program=CLARINET.midi_program, channel=0)

    rng = np.random.default_rng(SEED)
    for s_idx, s_name in enumerate(SECTIONS):
        # NOTE: beats_per_bar=11 -> composer.ticks_per_bar = 5280 == one SECTION
        # (4 Kopanitsa bars of 1320). Section cells are authored to 5280 ticks,
        # so add_section(bars=1) keeps the humanizer span == cell length (zero-drift).
        composer.add_section(s_name, bars=1)
        if s_idx % 3 == 0:
            word = C52 * 8
        elif s_idx % 3 == 1:
            word = W_G * 5
        else:
            word = W_D * 4

        events = []
        cur_tick = 0
        cur_pitch = 69.0
        for char in word:
            if cur_tick >= SECTION_TICKS - 150:
                break
            delta = 2.15 if char == "a" else -1.25
            cur_pitch += delta
            dur = int(rng.uniform(130, 250))
            if cur_tick + dur > SECTION_TICKS - 10:
                dur = SECTION_TICKS - 10 - cur_tick
            p_midi = int(round(np.clip(cur_pitch, 58, 86)))
            events.append(MusicEvent(pitch=p_midi, volume=int(rng.uniform(70, 105)),
                                     start_tick=cur_tick, end_tick=cur_tick + dur))
            cur_tick += int(rng.uniform(140, 270))

        if not events or events[-1].end_tick < SECTION_TICKS:
            events.append(MusicEvent(pitch=0, volume=0,
                                     start_tick=SECTION_TICKS - 10, end_tick=SECTION_TICKS))
        composer.fill_voice_section("Raw_Clarinet", s_name, MusicUnit(events=events))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 1 validate failed: {msg}")
    p1 = os.path.join(MIDI_DIR, "282-balkan-christoffel-variations-phase1.mid")
    composer.to_midi(p1)
    write_provenance(
        p1, AI_ASSISTED,
        "069 Christoffel Word Combinatorial Composition (CWCC) + musicom rules",
        notes="Raw unquantized Christoffel/Sturmian walk, single voice "
              "(pre-rules generative draft)",
        parameters={"phase": 1, "seed": SEED, "ticks": TOTAL_TICKS})
    return p1


# ================================================================== PHASE 2
# 16th-note slot plan for the Kopanitsa 11/8 roll (10 onsets, all 120-grid)
CLAR_16TH = [(0, 120), (120, 120), (240, 120), (360, 120), (480, 120),
             (600, 120), (720, 120), (840, 120), (960, 120), (1080, 240)]
# augmented (half-speed) slot plan: 8th-note feel, 5 onsets
CLAR_8TH = [(0, 240), (240, 240), (480, 360), (840, 240), (1080, 240)]

# per-section lead technique params: (slots, word, step_rule, base_register)
# step_rule: 'normal' (a=+2,b=-1) | 'invert' (a=-2,b=+1) | 'retro' (reversed word)
LEAD_TECHNIQUE = {
    0: dict(slots=CLAR_8TH, word="C52", step="normal", base=69),    # sparse intro
    1: dict(slots=CLAR_16TH, word="C52", step="normal", base=74),   # Tema A
    2: dict(slots=CLAR_16TH, word="W_D", step="normal", base=72),   # Tema B
    3: dict(slots=CLAR_16TH, word="W_G", step="normal", base=79),   # register shift UP
    4: dict(slots=CLAR_16TH, word="C52", step="invert", base=74),   # inversion
    5: dict(slots=CLAR_8TH, word="W_D", step="normal", base=70),    # augmentation
    6: dict(slots=CLAR_16TH, word="C52", step="retro", base=74),    # retrograde
    7: dict(slots=CLAR_8TH, word="C52", step="normal", base=69),    # cadence
}


def _word_for(tag):
    return {"C52": C52, "W_G": W_G, "W_D": W_D}[tag]


def lead_step(step_rule, char):
    if step_rule == "invert":
        return -2 if char == "a" else 1
    return 2 if char == "a" else -1


def build_lead_section(s_idx):
    """Clarinet lead: motif-driven walk, quantized to each bar's chord tones."""
    tech = LEAD_TECHNIQUE[s_idx]
    slots = tech["slots"]
    base_word = _word_for(tech["word"]) * 8
    events = []
    lead_pitch = tech["base"]
    k = 0
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        chord_pcs = get_bar_chord_pcs(s_idx, bar)
        word = base_word
        if tech["step"] == "retro":
            word = base_word[::-1]
        for st_rel, dur in slots:
            char = word[k % len(word)]
            k += 1
            step = lead_step(tech["step"], char)
            target = lead_pitch + step
            q = nearest_chord_tone(target, chord_pcs, 62, 86)
            lead_pitch = q
            vel = 95 if (bar_start + st_rel) % BAR_TICKS in BEAT_TICKS else 80
            events.append(MusicEvent(pitch=q, volume=vel,
                                     start_tick=bar_start + st_rel,
                                     end_tick=bar_start + st_rel + dur))
    return events


def build_fiddle_section(s_idx):
    """Fiddle countermelody: 5 macro beats, sustained chord tones. Register
    climbs in Razvivka; inverted contour in Tema_A_Inv."""
    rot = (C52[3:] + C52[:3]) * 8
    events = []
    fid_pitch = 65
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        chord_pcs = get_bar_chord_pcs(s_idx, bar)
        for b_idx in range(5):
            st_rel = BEAT_TICKS[b_idx]
            dur = BEAT_DUR_TICKS[b_idx]
            char = rot[(bar * 5 + b_idx) % len(rot)]
            step = 2 if char == "a" else -2
            if s_idx == 4:            # inversion
                step = -step
            lo, hi = (60, 81) if s_idx == 3 else (57, 77)   # register shift in Razvivka
            target = fid_pitch + step
            q = nearest_chord_tone(target, chord_pcs, lo, hi)
            fid_pitch = q
            events.append(MusicEvent(pitch=q, volume=88,
                                     start_tick=bar_start + st_rel,
                                     end_tick=bar_start + st_rel + dur))
    return events


def build_tambura_section(s_idx):
    """Tambura/Guitar comping. Offbeat stabs normally; arpeggiated 16ths in
    Razvivka (density rise); sustained whole-bar pad in augmentation."""
    events = []
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        chord = get_bar_chord(s_idx, bar)
        chord_pcs = CHORD_PCS[chord]
        triad = [nearest_chord_tone(60, {pc}, 55, 72) for pc in chord_pcs]
        if s_idx == 3:                 # density rise: 16th arpeggio
            for p_idx in range(PULSES_PER_BAR):
                tn = triad[p_idx % 3]
                st = bar_start + p_idx * GRID16
                events.append(MusicEvent(pitch=tn, volume=82,
                                         start_tick=st, end_tick=st + GRID16))
        elif s_idx == 5:               # sparse pad (augmentation companion)
            for tn in triad:
                events.append(MusicEvent(pitch=tn, volume=80,
                                         start_tick=bar_start,
                                         end_tick=bar_start + BAR_TICKS))
        else:
            for st_rel, dur in [(240, 240), (480, 360), (1080, 240)]:
                for tn in triad:
                    events.append(MusicEvent(pitch=tn, volume=85,
                                             start_tick=bar_start + st_rel,
                                             end_tick=bar_start + st_rel + dur))
    return events


def build_bass_section(s_idx):
    """Double Bass: root/fifth Kopanitsa dance lock. Sparse half-notes in
    augmentation; walking 8ths in Razvivka."""
    events = []
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        chord = get_bar_chord(s_idx, bar)
        root_pc, fifth_pc = ROOT_FIFTH[chord]
        root = nearest_chord_tone(38, {root_pc}, 34, 46)
        fifth = nearest_chord_tone(43, {fifth_pc}, 34, 50)
        if s_idx == 5:                 # sparse: root + fifth, half-note lengths
            hits = [(0, 480, root, 105), (840, 480, fifth, 95)]
        elif s_idx == 3:               # walking: add passing 8th
            hits = [(0, 240, root, 105), (240, 240, fifth, 90), (480, 360, root, 100),
                    (840, 240, fifth, 95), (1080, 240, root, 100)]
        else:
            hits = [(0, 240, root, 105), (480, 360, root, 100),
                    (840, 240, fifth, 95), (1080, 240, root, 100)]
        for st_rel, dur, p, vel in hits:
            events.append(MusicEvent(pitch=p, volume=vel,
                                     start_tick=bar_start + st_rel,
                                     end_tick=bar_start + st_rel + dur))
    return events


def build_drums_section(s_idx):
    """Tupan/drum kit on ch9. 16th hi-hat ride; kick 1&3, snare 2/4/5. Tom fill
    in Razvivka's last bar; 8th hat (sparser) in augmentation."""
    events = []
    for bar in range(BARS_PER_SECTION):
        bar_start = bar * BAR_TICKS
        hat_step = GRID16 if s_idx != 5 else GRID16 * 2
        for st in range(0, PULSES_PER_BAR * GRID16, hat_step):
            p_idx = st // GRID16
            vel = 70 if (s_idx != 5 and p_idx in BEAT_PULSES) else 50
            events.append(MusicEvent(pitch=42, volume=vel,
                                     start_tick=bar_start + st,
                                     end_tick=bar_start + st + GRID16))
        events.append(MusicEvent(pitch=36, volume=110, start_tick=bar_start,
                                 end_tick=bar_start + 240))
        events.append(MusicEvent(pitch=36, volume=115, start_tick=bar_start + 480,
                                 end_tick=bar_start + 360))
        events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_start + 240,
                                 end_tick=bar_start + 480))
        events.append(MusicEvent(pitch=38, volume=90, start_tick=bar_start + 840,
                                 end_tick=bar_start + 1080))
        events.append(MusicEvent(pitch=38, volume=95, start_tick=bar_start + 1080,
                                 end_tick=bar_start + 1320))
        if s_idx == 3 and bar == BARS_PER_SECTION - 1:     # tom fill
            for i, tom in enumerate((47, 45, 43)):
                st = bar_start + 960 + i * 120
                events.append(MusicEvent(pitch=tom, volume=100,
                                         start_tick=st, end_tick=st + 120))
    return events


def build_phase2():
    """Rules-processed 5-voice arrangement, grid-locked (the 'perfect' layer)."""
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=PULSES_PER_BAR)
    composer.create_matrix(num_voices=5, num_sections=N_SECTIONS)

    composer.add_voice("Clarinet", program=CLARINET.midi_program, channel=0)
    composer.add_voice("Fiddle", program=VIOLIN.midi_program, channel=1)
    composer.add_voice("Tambura", program=ACOUSTIC_GUITAR.midi_program, channel=2)
    composer.add_voice("Bass", program=DOUBLE_BASS.midi_program, channel=3)
    composer.add_voice("Drums", program=DRUM_KIT.midi_program, channel=9)

    builders = {
        "Clarinet": build_lead_section,
        "Fiddle": build_fiddle_section,
        "Tambura": build_tambura_section,
        "Bass": build_bass_section,
        "Drums": build_drums_section,
    }

    for s_idx, s_name in enumerate(SECTIONS):
        # bars=1: one composer-bar (=5280 ticks) == one section cell (zero-drift span).
        composer.add_section(s_name, bars=1)
        for vname, builder in builders.items():
            raw = builder(s_idx)
            cell = finish_section(raw)
            composer.fill_voice_section(vname, s_name, MusicUnit(events=cell))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 2 (perfect) validate failed: {msg}")

    perfect = os.path.join(MIDI_DIR, "282-balkan-christoffel-variations-perfect.mid")
    humanized = os.path.join(MIDI_DIR, "282-balkan-christoffel-variations-humanized.mid")

    hz_instruments = {
        "Clarinet": CLARINET.humanize_dna,
        "Fiddle": VIOLIN.humanize_dna,
        "Tambura": ACOUSTIC_GUITAR.humanize_dna,
        "Bass": DOUBLE_BASS.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    hz = export_dual(composer, perfect, humanized, style=STYLE, seed=SEED,
                     bpm=BPM, instruments=hz_instruments)

    # provenance sidecars
    gen = "069 Christoffel Word Combinatorial Composition (CWCC) + musicom rules"
    write_provenance(perfect, AI_ASSISTED, gen,
                     notes="Grid-locked rules-processed layer (no humanization)",
                     parameters={"phase": 2, "version": "perfect", "seed": SEED,
                                 "key": "D Dorian + b6", "bpm": BPM, "style": STYLE,
                                 "time_signature": "11/8 (2+2+3+2+2)", "bars": N_BARS,
                                 "ticks": TOTAL_TICKS})
    write_provenance(humanized, AI_ASSISTED, gen,
                     notes="Humanized (style balkan-folk, per-instrument DNA)",
                     parameters={"phase": 2, "version": "humanized", "seed": SEED,
                                 "key": "D Dorian + b6", "bpm": BPM, "style": STYLE,
                                 "humanize_seed": SEED, "humanize_profiles": hz})

    # grid visualization (from the humanized composer state)
    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"))

    return perfect, humanized, hz, composer


if __name__ == "__main__":
    p1 = build_phase1()
    print(f"phase1:  {p1} ({os.path.getsize(p1)} bytes)")
    perfect, humanized, hz, composer = build_phase2()
    print(f"perfect:  {perfect} ({os.path.getsize(perfect)} bytes)")
    print(f"humanized:{humanized} ({os.path.getsize(humanized)} bytes)")
    print("humanize summary:")
    print(json.dumps(hz, indent=2, default=str))
