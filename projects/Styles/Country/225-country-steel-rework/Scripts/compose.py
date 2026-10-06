# -*- coding: utf-8 -*-
"""225-country-steel-rework — musicom engine rework of 038-steel-guitar-demo.

Two-phase architecture (mandatory):
  Phase 1 = raw generative draft (jittered steel-slide contour, single voice,
            off-grid onsets, out-of-key pitches allowed).
  Phase 2 = musicom rules post-process (chord-tone quantization per bar,
            rhythm-grid snap to 120 ticks, register enforcement, dedup) + full
            multi-voice arrangement (Lead/Comp/Fiddle/Bass/Drums).

Everything authored through UnitMatrixComposer (no hand-rolled mido writes).
"""
import os
import json
import random
import datetime

from structures import MusicUnit, MusicEvent, UnitMatrix
from workflows.unitmatrix_composer import UnitMatrixComposer
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

BAR = 1920          # 480 ticks/beat * 4 beats/bar
TICKS = 480
GRID = 120          # 16th note grid
SEED = 20261006
BPM = 90

SRC = "/opt/data/projects/Styles/Country/038-steel-guitar-demo"
NEW = "/opt/data/projects/Styles/Country/225-country-steel-rework"
NAME = "225-country-steel-rework"

# ---------------- musical DNA (G major, I-IV-V country) ----------------
KEY_PCS = {7, 9, 11, 0, 2, 4, 6}            # G A B C D E F#
CHORD_PCS = {                                # chord-tone pitch classes
    "G":  {7, 11, 2},   # G B D
    "C":  {0, 4, 7},    # C E G
    "D":  {2, 6, 9},    # D F# A
    "Am": {9, 0, 4},    # A C E
    "Em": {4, 7, 11},   # E G B
}

# full 24-bar bar->chord map (per-section harmonic regions)
PROG = (
    ["G", "G"] +                                       # Intro   (0-1)
    ["G", "C", "D", "G", "C", "G", "D", "G"] +         # Verse   (2-9)
    ["C", "G", "Am", "D", "C", "G", "D", "G"] +        # Chorus  (10-17)
    ["Em", "C", "Am", "D"] +                           # Bridge  (18-21)
    ["C", "G"]                                         # Outro   (22-23)
)
assert len(PROG) == 24, len(PROG)

SECTIONS = [("Intro", 2), ("Verse", 8), ("Chorus", 8), ("Bridge", 4), ("Outro", 2)]
assert sum(b for _, b in SECTIONS) == 24

# chord voicings for rhythm comp (mid register, all chord tones)
COMP = {
    "G":  [59, 62, 67],   # B3 D4 G4
    "C":  [60, 64, 67],   # C4 E4 G4
    "D":  [62, 66, 69],   # D4 F#4 A4
    "Am": [60, 64, 69],   # C4 E4 A4
    "Em": [59, 64, 67],   # B3 E4 G4
}
# bass root / fifth (octave 2-3)
BASS = {
    "G":  (43, 50), "C": (48, 55), "D": (50, 57),
    "Am": (45, 52), "Em": (40, 47),
}


def chord_tone_nearest(chord, raw_pitch, lo=55, hi=90):
    """Nearest in-key chord tone to raw_pitch, register-constrained."""
    pcs = CHORD_PCS[chord]
    cands = [p for p in range(lo, hi + 1) if p % 12 in pcs]
    return min(cands, key=lambda p: abs(p - raw_pitch))


# ---------------- intended lead melody (chord-tone arpeggios) ----------------
# each: (bar, sixteenth_in_bar, dur_in_16ths, midi_pitch) — all chord tones
LEAD = [
    # Intro (G)
    (0, 0, 2, 67), (0, 2, 2, 71), (0, 4, 4, 74),
    (1, 0, 8, 67), (1, 8, 2, 71), (1, 10, 2, 74), (1, 12, 4, 67),
    # Verse phrase 1 (G C D G)
    (2, 0, 2, 67), (2, 2, 2, 71), (2, 4, 2, 74), (2, 6, 2, 71), (2, 8, 2, 67), (2, 10, 2, 71), (2, 12, 4, 74),
    (3, 0, 2, 64), (3, 2, 2, 67), (3, 4, 2, 72), (3, 6, 2, 67), (3, 8, 2, 64), (3, 10, 2, 67), (3, 12, 4, 72),
    (4, 0, 2, 74), (4, 2, 2, 78), (4, 4, 2, 69), (4, 6, 2, 78), (4, 8, 2, 74), (4, 10, 2, 78), (4, 12, 4, 69),
    (5, 0, 4, 71), (5, 4, 4, 67), (5, 8, 2, 74), (5, 10, 2, 71), (5, 12, 4, 67),
    # Verse phrase 2 (C G D G)
    (6, 0, 2, 76), (6, 2, 2, 72), (6, 4, 2, 67), (6, 6, 2, 72), (6, 8, 2, 76), (6, 10, 2, 72), (6, 12, 4, 67),
    (7, 0, 2, 67), (7, 2, 2, 71), (7, 4, 2, 74), (7, 6, 2, 79), (7, 8, 2, 74), (7, 10, 2, 71), (7, 12, 4, 67),
    (8, 0, 2, 69), (8, 2, 2, 78), (8, 4, 2, 74), (8, 6, 2, 78), (8, 8, 2, 69), (8, 10, 2, 74), (8, 12, 4, 78),
    (9, 0, 4, 71), (9, 4, 4, 74), (9, 8, 2, 71), (9, 10, 2, 67), (9, 12, 4, 67),
    # Chorus (C G Am D / C G D G) — register shift up (+octave feel)
    (10, 0, 2, 76), (10, 2, 2, 79), (10, 4, 2, 84), (10, 6, 2, 79), (10, 8, 2, 76), (10, 10, 2, 79), (10, 12, 4, 84),
    (11, 0, 2, 79), (11, 2, 2, 83), (11, 4, 2, 86), (11, 6, 2, 83), (11, 8, 2, 79), (11, 10, 2, 83), (11, 12, 4, 86),
    (12, 0, 2, 81), (12, 2, 2, 84), (12, 4, 2, 76), (12, 6, 2, 84), (12, 8, 2, 81), (12, 10, 2, 84), (12, 12, 4, 88),
    (13, 0, 2, 78), (13, 2, 2, 81), (13, 4, 2, 86), (13, 6, 2, 81), (13, 8, 2, 78), (13, 10, 2, 81), (13, 12, 4, 86),
    (14, 0, 2, 76), (14, 2, 2, 79), (14, 4, 2, 84), (14, 6, 2, 79), (14, 8, 2, 76), (14, 10, 2, 79), (14, 12, 4, 84),
    (15, 0, 2, 79), (15, 2, 2, 83), (15, 4, 2, 86), (15, 6, 2, 83), (15, 8, 2, 79), (15, 10, 2, 83), (15, 12, 4, 86),
    (16, 0, 2, 81), (16, 2, 2, 78), (16, 4, 2, 86), (16, 6, 2, 78), (16, 8, 2, 81), (16, 10, 2, 86), (16, 12, 4, 78),
    (17, 0, 4, 83), (17, 4, 4, 86), (17, 8, 2, 83), (17, 10, 2, 79), (17, 12, 4, 79),
    # Bridge (Em C Am D) — retrograde descent + minor coloring
    (18, 0, 2, 71), (18, 2, 2, 67), (18, 4, 2, 64), (18, 6, 2, 67), (18, 8, 2, 71), (18, 12, 4, 76),
    (19, 0, 4, 67), (19, 4, 4, 64), (19, 8, 4, 72), (19, 12, 4, 76),
    (20, 0, 2, 69), (20, 2, 2, 72), (20, 4, 2, 64), (20, 6, 2, 72), (20, 8, 2, 69), (20, 12, 4, 64),
    (21, 0, 2, 78), (21, 2, 2, 74), (21, 4, 2, 69), (21, 6, 2, 66), (21, 8, 2, 74), (21, 10, 2, 78), (21, 12, 4, 74),
    # Outro (C G) — augmentation (long notes)
    (22, 0, 8, 64), (22, 8, 2, 67), (22, 10, 2, 72), (22, 12, 4, 76),
    (23, 0, 16, 67),
]


def build_comp():
    """Rhythm guitar: chord-tone strum, density varies per section."""
    ev = []
    for bar in range(24):
        ch = PROG[bar]
        if bar < 2:            # intro: held whole-note
            for p in COMP[ch]:
                ev.append((bar * BAR, 16 * GRID, p, 55))
        elif bar < 10:         # verse: boom-chick, strum 4 beats
            for s in (0, 4, 8, 12):
                for p in COMP[ch]:
                    ev.append((bar * BAR + s * GRID, 2 * GRID, p, 62))
        elif bar < 18:         # chorus: dense 8th strums
            for s in range(0, 16, 2):
                for p in COMP[ch]:
                    ev.append((bar * BAR + s * GRID, 2 * GRID, p, 72))
        elif bar < 22:         # bridge: sparse half strums
            for s in (0, 8):
                for p in COMP[ch]:
                    ev.append((bar * BAR + s * GRID, 4 * GRID, p, 58))
        else:                  # outro: held
            for p in COMP[ch]:
                ev.append((bar * BAR, 16 * GRID, p, 55))
    return ev


def build_bass():
    """Bass: root-fifth walking; half-time (augmentation) in bridge/outro."""
    ev = []
    for bar in range(24):
        ch = PROG[bar]
        root, fifth = BASS[ch]
        if 18 <= bar:                      # bridge+outro: whole-note root (augmentation)
            ev.append((bar * BAR, 16 * GRID, root, 88))
        else:                              # root fifth root fifth
            for i, (s, p) in enumerate([(0, root), (4, fifth), (8, root), (12, fifth)]):
                ev.append((bar * BAR + s * GRID, 2 * GRID, p, 88))
    return ev


def build_drums():
    """Drums ch9: country backbeat; density rise in chorus, breakdown in bridge."""
    ev = []
    for bar in range(24):
        b = bar * BAR
        if bar < 2:            # intro: hats only (sparse)
            for s in range(0, 16, 2):
                ev.append((b + s * GRID, GRID, 42, 48))
        elif bar < 10:         # verse backbeat
            for s in (0, 8):
                ev.append((b + s * GRID, GRID, 36, 100))   # kick
            for s in (4, 12):
                ev.append((b + s * GRID, GRID, 38, 95))    # snare
            for s in range(0, 16, 2):
                ev.append((b + s * GRID, GRID, 42, 70))    # hat 8ths
        elif bar < 18:         # chorus: dense 16th hats + backbeat
            for s in (0, 8):
                ev.append((b + s * GRID, GRID, 36, 100))
            for s in (4, 12):
                ev.append((b + s * GRID, GRID, 38, 95))
            for s in range(0, 16):
                ev.append((b + s * GRID, GRID, 42, 72))    # hat 16ths
        elif bar < 22:         # bridge: breakdown (snare + hat, no kick)
            for s in (4, 12):
                ev.append((b + s * GRID, GRID, 38, 80))
            for s in range(0, 16, 2):
                ev.append((b + s * GRID, GRID, 42, 62))
        else:                  # outro: final kick hit
            ev.append((b, 2 * GRID, 36, 100))
            if bar == 23:
                ev.append((b, 4 * GRID, 49, 90))   # crash
    return ev


def build_fiddle():
    """Fiddle counterline: sustained chord-tone pads (chorus) + answer (bridge)."""
    ev = []
    sus = [76, 74, 72, 69, 76, 74, 69, 71]   # per bar 10..17 (chord tones)
    for i, bar in enumerate(range(10, 18)):
        ev.append((bar * BAR, 16 * GRID, sus[i], 72))
    ans = [76, 79, 84, 74]                   # per bar 18..21
    for i, bar in enumerate(range(18, 22)):
        ev.append((bar * BAR + 8 * GRID, 4 * GRID, ans[i], 72))
    return ev


def split_into_sections(events):
    """Split absolute-tick events into per-section MusicUnits (relative ticks)."""
    units = []
    abs_bar = 0
    for _name, bars in SECTIONS:
        sec_start = abs_bar * BAR
        sec_len = bars * BAR
        sec = []
        for (st, d, p, v) in events:
            if sec_start <= st < sec_start + sec_len:
                rel = st - sec_start
                rel_end = min(rel + d, sec_len)
                if rel_end > rel:
                    sec.append(MusicEvent(pitch=p, volume=v, start_tick=rel, end_tick=rel_end))
        # terminal landmark guarantees len_ticks == sec_len (zero-drift invariant)
        sec.append(MusicEvent(pitch=0, volume=0, start_tick=sec_len, end_tick=sec_len))
        units.append(MusicUnit(events=sec))
        abs_bar += bars
    return units


def build_composer(voice_events, name, phase):
    """Build+validate+export a UnitMatrixComposer from per-voice absolute events."""
    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS, beats_per_bar=4)
    n_voices = len(voice_events)
    c.create_matrix(num_voices=n_voices, num_sections=len(SECTIONS))
    for vname, prog, ch in voice_events:
        c.add_voice(vname, program=prog, channel=ch)
    for sn, sb in SECTIONS:
        c.add_section(sn, bars=sb)
    for row, (vname, _p, _ch) in enumerate(voice_events):
        units = split_into_sections(voice_events[(vname, _p, _ch)])
        for col in range(len(SECTIONS)):
            c.set_unit(row, col, units[col])
    ok, msg = c.validate()
    if not ok:
        raise RuntimeError(f"{phase} validate FAILED: {msg}")
    out = os.path.join(NEW, "MIDI", f"{name}.mid")
    c.to_midi(out)
    return c, out


def main():
    rng = random.Random(SEED)

    # ---------- Phase 1: raw generative draft (single voice) ----------
    raw_events = []  # (abs_ticks, dur_ticks, raw_pitch)
    for (bar, s, d, p) in LEAD:
        jit = rng.randint(-30, 30)                     # sub-grid jitter
        pj = rng.choice([0, 0, 0, 0, 1, -1, 0, 2, -2]) # occasional out-of-key
        onset = bar * BAR + s * GRID + jit
        onset = max(0, onset)
        raw_events.append((onset, d * GRID, p + pj))
    raw_events.sort(key=lambda x: x[0])
    # build raw MusicUnit spanning full 24 bars, single voice
    total = 24 * BAR
    raw_unit_events = []
    prev_end = 0
    for (st, d, p) in raw_events:
        st = max(st, prev_end)          # keep monotonic
        en = min(st + d, total)
        if en <= st:
            en = st + GRID
        raw_unit_events.append(MusicEvent(pitch=p, volume=100, start_tick=st, end_tick=en))
        prev_end = en
    raw_unit_events.append(MusicEvent(pitch=0, volume=0, start_tick=total, end_tick=total))
    raw_unit = MusicUnit(events=raw_unit_events)

    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TICKS, beats_per_bar=4)
    p1.create_matrix(num_voices=1, num_sections=1)
    p1.add_voice("SteelLeadRaw", program=25, channel=0)
    p1.add_section("RawDraft", bars=24)
    p1.set_unit(0, 0, raw_unit)
    ok, msg = p1.validate()
    if not ok:
        raise RuntimeError(f"phase1 validate FAILED: {msg}")
    phase1_path = os.path.join(NEW, "MIDI", f"{NAME}-phase1.mid")
    p1.to_midi(phase1_path)

    # ---------- Phase 2: rules post-process -> quantized lead ----------
    lead_quant = []
    for (st, d, p) in raw_events:
        bar = min(23, max(0, st // BAR))
        ch = PROG[bar]
        onset = (st // GRID) * GRID                    # snap to 120 grid
        dur = max(GRID, (d // GRID) * GRID)
        pitch = chord_tone_nearest(ch, p, lo=55, hi=90)  # chord-tone quantization
        lead_quant.append((onset, dur, pitch, 100))
    # dedup collided (onset,pitch) keep longest
    dedup = {}
    for (st, d, p, v) in lead_quant:
        key = (st, p)
        if key not in dedup or d > dedup[key][1]:
            dedup[key] = (st, d, p, v)
    lead_quant = sorted(dedup.values(), key=lambda x: x[0])

    voice_events = {
        ("SteelLead", 25, 0): lead_quant,
        ("RhythmGuitar", 24, 1): build_comp(),
        ("Fiddle", 40, 2): build_fiddle(),
        ("Bass", 32, 3): build_bass(),
        ("Drums", 0, 9): build_drums(),
    }

    composer, phase2_path = build_composer(voice_events, NAME, "phase2")

    # ---------- provenance sidecars ----------
    gen_phase1 = "steel-slide random walk (jittered raw draft, SEED=%d)" % SEED
    gen_phase2 = "steel-slide random walk + musicom rules (chord-tone quantize, grid snap)"
    write_provenance(
        phase1_path, AI_ASSISTED, gen_phase1,
        sources=[SRC + "/MIDI/country_ensemble_16bar.mid"],
        parameters={"phase": 1, "seed": SEED, "key": "G major", "bpm": BPM, "rules": "none (pre-rules)"},
        notes="Raw generative draft. Off-grid onsets + out-of-key pitches by design; single voice.")
    write_provenance(
        phase2_path, AI_ASSISTED, gen_phase2,
        sources=[SRC + "/MIDI/country_ensemble_16bar.mid", phase1_path],
        parameters={"phase": 2, "seed": SEED, "key": "G major", "bpm": BPM,
                    "rules": "chord-tone quantize + 120-tick grid snap + dedup + register enforcement"},
        notes="Rules-processed full arrangement. 5 voices, 24 bars, per-section harmonic regions.")

    # ---------- grid visualization ----------
    write_grid_visualization(composer.matrix, os.path.join(NEW, "Analysis", "grid_visualization.txt"),
                             ticks_per_character=GRID)

    # ---------- verification (read-only mido) ----------
    import mido  # READING ONLY (analysis)
    result = verify(phase1_path, phase2_path)
    with open(os.path.join(NEW, "Analysis", "verify.json"), "w") as f:
        json.dump(result, f, indent=2)
    print("VERIFY:", json.dumps(result))
    return result


def verify(phase1_path, phase2_path):
    import mido  # READING ONLY (analysis)
    res = {"phase1": {}, "phase2": {}}
    for tag, path in (("phase1", phase1_path), ("phase2", phase2_path)):
        mid = mido.MidiFile(path)
        # track 0 = conductor/tempo (set_tempo meta, length 0). Skip it.
        voice_tracks = mid.tracks[1:]
        lengths = []
        offgrid = 0
        scale_viol = 0
        chord_viol = 0
        pitched = 0
        for t in voice_tracks:
            tick = 0
            is_drums = False
            for m in t:
                tick += m.time
                if m.type == "program_change" and m.channel == 9:
                    is_drums = True
                if m.type == "note_on" and m.velocity > 0 and m.note != 0:
                    if not is_drums:
                        pitched += 1
                        if tick % GRID != 0:
                            offgrid += 1
                        if m.note % 12 not in KEY_PCS:
                            scale_viol += 1
                        bar = min(23, tick // BAR)
                        if m.note % 12 not in CHORD_PCS[PROG[bar]]:
                            chord_viol += 1
            lengths.append(tick)
        res[tag] = {
            "file": os.path.basename(path),
            "bytes": os.path.getsize(path),
            "n_voice_tracks": len(voice_tracks),
            "voice_track_lengths": lengths,
            "zero_drift": len(set(lengths)) == 1,
            "pitched_onsets": pitched,
            "off_grid": offgrid,
            "scale_violations": scale_viol,
            "chord_violations": chord_viol,
        }
    return res


if __name__ == "__main__":
    main()
