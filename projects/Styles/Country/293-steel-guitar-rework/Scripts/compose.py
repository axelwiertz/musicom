# -*- coding: utf-8 -*-
"""293-steel-guitar-rework — Country steel-slide rework.

Reworks 038-steel-guitar-demo (hand-rolled mido, zero-drift FAIL, 2-track)
through the canonical UnitMatrixComposer engine into a longer, more varied
20-bar country piece in G major (90 BPM, I-IV-V family).

Two-phase architecture:
  Phase 1 = raw generative draft (seeded random walk, unquantized + out-of-key,
            single voice)   -> 293-steel-guitar-rework-phase1.mid
  Phase 2 = musicom rules post-process (chord-tone quantize per bar, rhythm-grid
            snap to 120-tick grid, dedup, register clamp, voice-leading clamp)
            -> 293-steel-guitar-rework-perfect.mid (grid-locked)
            -> 293-steel-guitar-rework-humanized.mid (style+instrument humanize)
"""
import os
import random
import hashlib

from structures import MusicUnit, MusicEvent
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from workflows.provenance import write_provenance, AI_ASSISTED
from visualization.grid import write_grid_visualization

# --------------------------------------------------------------------------
# Concept
# --------------------------------------------------------------------------
STYLE = "country"
KEY = "G"
BPM = 90
TPB = 480
BPB = 4
BAR = TPB * BPB          # 1920 ticks
BEAT = TPB               # 480
EIGHTH = 240
SIXTEENTH = 120

# G major pitch classes (G A B C D E F#)
KEY_PCS = {7, 9, 11, 0, 2, 4, 6}

# Diatonic triads in G major: degree -> [root, third, fifth] pitch classes
DEGREE_TRIADS = {
    'I':   [7, 11, 2],    # G B D
    'ii':  [9, 0, 4],     # A C E
    'iii': [11, 2, 6],    # B D F#
    'IV':  [0, 4, 7],     # C E G
    'V':   [2, 6, 9],     # D F# A
    'vi':  [4, 7, 11],    # E G B
    'vii': [6, 9, 0],     # F# A C
}

# Form: (section name, bars, per-bar chord degrees)  -- 20 bars, 6 sections
SECTIONS = [
    ("Intro",   2, ['I', 'IV']),
    ("Verse",   4, ['I', 'IV', 'I', 'V']),
    ("Chorus",  4, ['I', 'IV', 'V', 'I']),
    ("Bridge",  4, ['IV', 'I', 'ii', 'V']),
    ("Verse2",  4, ['I', 'IV', 'I', 'V']),
    ("Outro",   2, ['V', 'I']),
]

BAR_CHORDS = [c for (_n, _b, chords) in SECTIONS for c in chords]
TOTAL_BARS = len(BAR_CHORDS)          # 20
TOTAL_TICKS = TOTAL_BARS * BAR        # 38400

# Voice config: name -> (program, channel)
VOICES = [
    ("Steel Guitar",   25, 0),   # GM 25 acoustic steel (signature timbre)
    ("Fiddle",         40, 1),   # GM 40 violin (counterline)
    ("Rhythm Guitar",  24, 2),   # GM 24 acoustic nylon (strum comp)
    ("Bass",           32, 3),   # GM 32 acoustic bass
    ("Drums",           0, 9),   # channel 9 percussion
]

# Humanization DNA per voice (timing_ms, velocity_sigma, layback_ms, duration_sigma)
# None -> style profile wins (per instrument-registry convention).
HZ_INSTRUMENTS = {
    "Steel Guitar":   (None, 6.0, None, 0.02),   # melodic: style timing/layback
    "Fiddle":         (None, 6.0, None, 0.02),   # melodic
    "Rhythm Guitar":  (None, 6.0, None, 0.02),   # melodic (strum)
    "Bass":           (5.0, 4.0, 8.0, 0.01),     # lays back 8 ms
    "Drums":          (2.0, 4.0, 0.0, 0.008),    # anchors
}

PID = "293"
NAME = "293-steel-guitar-rework"
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIDI_DIR = os.path.join(PROJ, "MIDI")
ANALYSIS_DIR = os.path.join(PROJ, "Analysis")

hz_seed = int(hashlib.md5(f"{PID}-{STYLE}-{KEY}-{BPM}".encode()).hexdigest()[:8], 16)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def lead_root_pc_midi(pc):
    """Map a pitch class to a MIDI note in the C4-B4 octave (60-71)."""
    m = pc
    while m < 60:
        m += 12
    while m >= 72:
        m -= 12
    return m


def motif_ascending(deg, octave=0):
    """Ascending [root, third, fifth] voicing of a chord degree (lead register)."""
    rp, tp, fp = DEGREE_TRIADS[deg]
    root = lead_root_pc_midi(rp) + 12 * octave
    third = root + ((tp - rp) % 12)
    fifth = root + ((fp - rp) % 12)
    return root, third, fifth


def degree_tones(deg, low, high):
    """All MIDI chord-tone pitches of a degree within [low, high]."""
    pcs = DEGREE_TRIADS[deg]
    out = set()
    for octv in range(0, 10):
        for pc in pcs:
            m = pc + 12 * octv
            if low <= m <= high:
                out.add(m)
    return sorted(out)


def pc_to_midi(pc, low=40, high=58):
    m = pc
    while m < low:
        m += 12
    while m > high:
        m -= 12
    return m


def make_unit(events, section_len):
    """Build a cell MusicUnit from (pitch, vel, start, end) tuples + terminal landmark."""
    # CRITICAL: sort by onset so the humanizer's forward-clamp (max(prev_start, ...))
    # does not cascade early events forward. Unsorted cells (e.g. drum hits written
    # kick-snare-hat order) catastrophically push later-processed early notes.
    events = sorted(events, key=lambda x: (x[2], x[0]))
    evs = []
    for (p, v, s, e) in events:
        s = max(0, min(int(s), section_len - 1))
        e = max(s + 1, min(int(e), section_len))
        evs.append(MusicEvent(pitch=int(p), volume=int(v),
                              start_tick=int(s), end_tick=int(e)))
    # terminal landmark keeps len_ticks() == section_len (zero-drift); pitch 0 skipped in MIDI
    evs.append(MusicEvent(pitch=0, volume=0,
                          start_tick=section_len - 10, end_tick=section_len))
    return MusicUnit(events=evs)


def snap(tick):
    return int(round(tick / SIXTEENTH)) * SIXTEENTH


# --------------------------------------------------------------------------
# Phase 1 — raw generative draft (seeded random walk, unquantized, out-of-key)
# --------------------------------------------------------------------------
def phase1_raw_events(seed=293):
    rng = random.Random(seed)
    events = []
    pitch = 67            # G4 start
    tick = 0
    while tick < TOTAL_TICKS - 200:
        dur = rng.randint(200, 420)
        pitch += rng.choice([-3, -2, -1, 1, 2, 3])
        pitch = max(50, min(79, pitch))
        vel = rng.randint(82, 106)
        events.append((pitch, vel, tick, tick + dur))
        tick += rng.randint(220, 500)   # unquantized spacing -> off-grid onsets
    return events


# --------------------------------------------------------------------------
# Phase 2 — musicom rules post-processing
# --------------------------------------------------------------------------
def quantize_lead(raw_events):
    """Chord-tone quantize (per bar, floor t//BAR), grid-snap, dedup, voice-lead."""
    lead = []
    for (pitch, vel, start, end) in raw_events:
        s = snap(start)
        e = snap(end)
        if e <= s:
            e = s + SIXTEENTH
        # attribute to the SNAPPED onset's bar (floor s//BAR) so a note whose
        # raw onset straddles a bar boundary is re-quantized to its FINAL bar.
        bar = min(s // BAR, TOTAL_BARS - 1)
        deg = BAR_CHORDS[bar]
        tones = degree_tones(deg, 55, 79)
        q = min(tones, key=lambda t: abs(t - pitch))
        lead.append([q, vel, s, e])

    # dedup collided (start_tick, pitch) keeping longest duration
    lead.sort(key=lambda x: (x[2], x[0], -(x[3] - x[2])))
    deduped = []
    seen = set()
    for q, vel, s, e in lead:
        key = (s, q)
        if key in seen:
            continue
        seen.add(key)
        deduped.append([q, vel, s, e])

    # voice-leading clamp: limit melodic leap to <= 9 semitones
    corrected = 0
    deduped.sort(key=lambda x: x[2])
    out = []
    prev_pitch = None
    for q, vel, s, e in deduped:
        bar = min(s // BAR, TOTAL_BARS - 1)
        if prev_pitch is not None and abs(q - prev_pitch) > 9:
            tones = degree_tones(BAR_CHORDS[bar], 55, 79)
            cand = [t for t in tones if abs(t - prev_pitch) <= 9]
            if cand:
                q = min(cand, key=lambda t: abs(t - q))
                corrected += 1
        out.append([q, vel, s, e])
        prev_pitch = q

    # register clamp (steel sweet spot)
    for ev in out:
        ev[0] = max(50, min(79, ev[0]))
    return out, corrected


def lead_for_section(section_name, bar_index, walk_events):
    """Lead (steel guitar) events for one bar, by section-specific technique."""
    deg = BAR_CHORDS[bar_index]
    sec = bar_index * BAR
    ev = []

    if section_name == "Intro":
        # STATEMENT — ascending 1->3->5 slide (G->B->D)
        r, t, f = motif_ascending(deg, octave=0)
        ev = [(r, 92, sec + 0, sec + 400), (t, 92, sec + 480, sec + 880),
              (f, 96, sec + 960, sec + 1720)]
    elif section_name == "Verse":
        # GENERATIVE WALK — quantized raw draft
        ev = [e for e in walk_events if e[2] // BAR == bar_index]
    elif section_name == "Chorus":
        # TRANSPOSITION — motif follows I-IV-V-I harmonic region (re-harmonized/transposed)
        r, t, f = motif_ascending(deg, octave=0)
        ev = [(r, 95, sec + 0, sec + 360), (t, 95, sec + 480, sec + 840),
              (f, 98, sec + 960, sec + 1720)]
    elif section_name == "Bridge":
        # INVERSION — descending 5->3->1 (mirror of the ascending motif)
        r, t, f = motif_ascending(deg, octave=0)
        ev = [(f, 90, sec + 0, sec + 420), (t, 90, sec + 480, sec + 900),
              (r, 88, sec + 960, sec + 1720)]
    elif section_name == "Verse2":
        # REGISTER SHIFT — verse walk (bars 2-5) replayed one octave higher
        # Verse2 = bars 14-17 (I,IV,I,V) mirrors Verse = bars 2-5 (I,IV,I,V).
        src_bar = bar_index - 12
        target_tones = degree_tones(deg, 55, 79)
        for (p, v, s, e) in walk_events:
            if s // BAR != src_bar:
                continue
            ns = (s - src_bar * BAR) + bar_index * BAR
            ne = (e - src_bar * BAR) + bar_index * BAR
            shifted = min(79, p + 12)
            # defensive re-quantize to the CURRENT bar's chord
            q = min(target_tones, key=lambda t: abs(t - shifted))
            ev.append((q, v, ns, ne))
        if not ev:   # safety fallback
            r, t, f = motif_ascending(deg, octave=1)
            ev = [(r, 92, sec + 0, sec + 400), (t, 92, sec + 480, sec + 880),
                  (f, 96, sec + 960, sec + 1720)]
    elif section_name == "Outro":
        # RETROGRADE — intro motif (G->B->D) reversed as descending close
        r, t, f = motif_ascending(deg, octave=0)
        ev = [(f, 94, sec + 0, sec + 400), (t, 92, sec + 480, sec + 880),
              (r, 90, sec + 960, sec + 1720)]
    return ev


def build_per_voice_events():
    """Return (voices, raw, walk, vl_corrections)."""
    raw = phase1_raw_events()
    walk, vl_corr = quantize_lead(raw)

    voices = {name: {} for (name, _p, _c) in VOICES}

    bar = 0
    for (sname, bars, chords) in SECTIONS:
        for i in range(bars):
            ab = bar
            sec_off = i * BAR
            deg = BAR_CHORDS[ab]

            # --- lead (steel guitar) ---
            lead_abs = lead_for_section(sname, ab, walk)
            voices["Steel Guitar"][sname] = voices["Steel Guitar"].get(sname, []) + [
                (p, v, s - ab * BAR + sec_off, e - ab * BAR + sec_off)
                for (p, v, s, e) in lead_abs
            ]

            # --- fiddle counterline (sustained chord-tone harmony) ---
            if sname in ("Verse", "Chorus", "Bridge", "Verse2"):
                tones = degree_tones(deg, 60, 84)
                hi = tones[len(tones) // 2] if tones else 72
                lo = tones[0] if tones else 67
                voices["Fiddle"][sname] = voices["Fiddle"].get(sname, []) + [
                    (lo, 72, sec_off + 0, sec_off + 900),
                    (hi, 74, sec_off + 960, sec_off + 960 + 900),
                ]

            # --- rhythm guitar strum (chick on beats 2 & 4) ---
            tones = degree_tones(deg, 48, 72)
            voicing = sorted(tones, key=lambda t: abs(t - 60))[:3]
            for beat_tick in (480, 1440):
                for m in voicing:
                    voices["Rhythm Guitar"][sname] = voices["Rhythm Guitar"].get(sname, []) + [
                        (m, 78, sec_off + beat_tick, sec_off + beat_tick + 200)
                    ]

            # --- bass (root beat 1, fifth beat 3) ---
            rp, _tp, fp = DEGREE_TRIADS[deg]
            r_m = pc_to_midi(rp)
            f_m = pc_to_midi(fp)
            voices["Bass"][sname] = voices["Bass"].get(sname, []) + [
                (r_m, 96, sec_off + 0, sec_off + 460),
                (f_m, 88, sec_off + 960, sec_off + 1420),
            ]

            # --- drums (country backbeat; denser in Chorus/Verse2) ---
            d = [(36, 100, sec_off + 0, sec_off + 100),      # kick 1
                 (36, 92, sec_off + 960, sec_off + 1060)]    # kick 3
            d += [(38, 95, sec_off + 480, sec_off + 580),    # snare 2
                  (38, 95, sec_off + 1440, sec_off + 1540)]  # snare 4
            for k in range(8):
                d.append((42, 70, sec_off + k * EIGHTH, sec_off + k * EIGHTH + 90))
            if sname in ("Chorus", "Verse2"):
                d.append((36, 85, sec_off + 1200, sec_off + 1300))   # off-beat kick
                d.append((49, 92, sec_off + 0, sec_off + 240))       # crash
            voices["Drums"][sname] = voices["Drums"].get(sname, []) + d

            bar += 1

    return voices, raw, walk, vl_corr


# --------------------------------------------------------------------------
# Build composers + export
# --------------------------------------------------------------------------
def build_phase1_composer(raw):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    c.create_matrix(num_voices=1, num_sections=len(SECTIONS))
    c.add_voice("Lead (raw)", program=25, channel=0)
    bar = 0
    for idx, (sname, bars, chords) in enumerate(SECTIONS):
        sec_len = bars * BAR
        c.add_section(sname, bars=bars)
        cell = [(p, v, s - bar * BAR, e - bar * BAR)
                for (p, v, s, e) in raw if bar * BAR <= s < (bar + bars) * BAR]
        c.set_unit(0, idx, make_unit(cell, sec_len))
        bar += bars
    return c


def build_phase2_composer(voices):
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    c.create_matrix(num_voices=len(VOICES), num_sections=len(SECTIONS))
    for (name, program, channel) in VOICES:
        c.add_voice(name, program=program, channel=channel)
    for idx, (sname, bars, chords) in enumerate(SECTIONS):
        c.add_section(sname, bars=bars)
    for r, (name, program, channel) in enumerate(VOICES):
        for col, (sname, bars, chords) in enumerate(SECTIONS):
            sec_len = bars * BAR
            c.set_unit(r, col, make_unit(voices[name].get(sname, []), sec_len))
    return c


def main():
    os.makedirs(MIDI_DIR, exist_ok=True)
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    voices, raw, walk, vl_corr = build_per_voice_events()

    # ---- Phase 1 ----
    c1 = build_phase1_composer(raw)
    ok, msg = c1.validate()
    assert ok, f"phase1 validate FAILED: {msg}"
    phase1_path = os.path.join(MIDI_DIR, f"{NAME}-phase1.mid")
    c1.to_midi(phase1_path)
    write_provenance(phase1_path, AI_ASSISTED,
                     generator="random-walk (raw, pre-rules)",
                     sources=["038-steel-guitar-demo/MIDI/country_ensemble_16bar.mid"],
                     parameters={"phase": 1, "key": KEY, "bpm": BPM, "seed": 293,
                                 "note": "unquantized + out-of-key by construction"},
                     notes="Phase 1 raw generative draft (single voice).")

    # ---- Phase 2 (dual-version) ----
    c2 = build_phase2_composer(voices)
    perfect_path = os.path.join(MIDI_DIR, f"{NAME}-perfect.mid")
    humanized_path = os.path.join(MIDI_DIR, f"{NAME}-humanized.mid")
    hz = export_dual(c2, perfect_path, humanized_path,
                     style=STYLE, seed=hz_seed, bpm=BPM, instruments=HZ_INSTRUMENTS)

    # ---- provenance for phase-2 ----
    for path, phase, gen in [
        (perfect_path, "2-perfect", "random-walk + musicom rules (grid-locked)"),
        (humanized_path, "2-humanized", "random-walk + musicom rules + humanize"),
    ]:
        write_provenance(path, AI_ASSISTED, generator=gen,
                         sources=["038-steel-guitar-demo/MIDI/country_ensemble_16bar.mid",
                                  f"{NAME}-phase1.mid"],
                         parameters={"phase": phase, "key": KEY, "bpm": BPM,
                                     "style": STYLE, "humanize_seed": hz_seed,
                                     "humanize_profiles": hz},
                         notes="Redesign of 038-steel-guitar-demo (all 6 standards failed).")

    # ---- grid visualization (perfect matrix) ----
    grid_path = os.path.join(ANALYSIS_DIR, "grid_visualization.txt")
    write_grid_visualization(c2.matrix, grid_path, ticks_per_character=240,
                             voice_names=[v[0] for v in VOICES], bpm=BPM, mode="G major")

    # ---- report numbers ----
    print("PID", PID, "NAME", NAME)
    print("hz_seed", hz_seed)
    print("phase1", phase1_path, os.path.getsize(phase1_path))
    print("perfect", perfect_path, os.path.getsize(perfect_path))
    print("humanized", humanized_path, os.path.getsize(humanized_path))
    print("voice_leading_corrections (perfect lead):", vl_corr)
    print("humanize summary:")
    for k, v in hz.items():
        print("  ", k, "shift_mean", v["mean_abs_shift_ticks"],
              "shift_max", v["max_abs_shift_ticks"], "vel_delta", v["mean_abs_vel_delta"])
    print("grid_viz", grid_path)
    print("DONE")


if __name__ == "__main__":
    main()
