#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""209-trap-half-time-rework — rework of 001-trap-half-time.

Longer (24 bars / 6 sections) + more varied. Two-phase architecture:
  Phase 1 = raw generative draft (Brownian-walk pitch_index, jittered
            onsets, single voice) -> phase1.mid
  Phase 2 = musicom rules: chord-tone quantization per bar, rhythm-grid
            snap (120/240), dedup, register/range + voice-leading ->
            full multi-voice phase2.mid
Identity preserved: Trap half-time, 140 BPM, C natural minor, 808 sub,
dark pad, sparse square lead, kick(1 + and-of-3) / snare(3).
"""
import os
import random

from structures import MusicEvent, MusicUnit, MidiInstrument
from workflows.unitmatrix_composer import (
    UnitMatrixComposer, create_empty_unit,
)
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED

TPB = 480
BEATS = 4
BAR = TPB * BEATS                # 1920
QUARTER = TPB                    # 480
EIGHTH = TPB // 2                # 240
SIXTEENTH = TPB // 4             # 120
BPM = 140
BARS_PER_SECTION = 4
SECTION = BAR * BARS_PER_SECTION  # 7680
TOTAL_BARS = 24

OUT = os.path.dirname(os.path.abspath(__file__))
MIDI_DIR = os.path.join(OUT, "MIDI")
AUDIO_DIR = os.path.join(OUT, "Audio")
ANALYSIS_DIR = os.path.join(OUT, "Analysis")

# --- key / harmony (C natural minor) ---
KEY_PCS = {0, 2, 3, 5, 7, 8, 10}
CHORD = {
    "Cm": [0, 3, 7], "Ddim": [2, 5, 8], "Eb": [3, 7, 10],
    "Fm": [5, 8, 0], "Gm": [7, 10, 2], "Ab": [8, 0, 3], "Bb": [10, 2, 5],
}
SECTION_NAMES = ["Intro", "VerseA", "Chorus", "VerseB", "Bridge", "Outro"]
SECTION_CHORDS = [
    ["Cm", "Cm", "Ab", "Ab"],   # Intro  bars 0-3
    ["Cm", "Gm", "Ab", "Bb"],   # VerseA bars 4-7
    ["Ab", "Eb", "Bb", "Cm"],   # Chorus bars 8-11
    ["Cm", "Gm", "Fm", "Bb"],   # VerseB bars 12-15
    ["Fm", "Ab", "Gm", "Cm"],   # Bridge bars 16-19
    ["Cm", "Ab", "Cm", "Cm"],   # Outro  bars 20-23
]


def flat_chords():
    return [c for sec in SECTION_CHORDS for c in sec]


def chord_tones(bar, lo=48, hi=84):
    pcs = CHORD[flat_chords()[bar]]
    return [p for p in range(lo, hi + 1) if p % 12 in pcs]


def section_of_bar(bar):
    return bar // BARS_PER_SECTION


def unit_from(events, sec=SECTION):
    ev = [e for e in events]
    for e in ev:
        if e.end_tick > sec:
            e.end_tick = sec
        if e.start_tick >= sec:
            e.start_tick = sec - 10
    if not ev or ev[-1].end_tick < sec:
        ev.append(MusicEvent(pitch=0, volume=0, start_tick=sec - 10,
                             end_tick=sec))
    return MusicUnit(events=ev)


# --------------------------------------------------------------------------
# PHASE 1 — raw generative draft (Brownian walk, single voice)
# --------------------------------------------------------------------------
def generate_raw(rng, n_bars=TOTAL_BARS):
    """Raw pitch_index walk + jittered onsets. Returns list of dicts."""
    raws = []
    pi = 0.5
    for bar in range(n_bars):
        base = bar * BAR
        n_on = rng.randint(3, 5)
        times = sorted(rng.randint(0, BAR - 60) for _ in range(n_on))
        for t in times:
            pi += rng.uniform(-0.12, 0.12)
            pi = min(1.0, max(0.0, pi))
            dur = rng.choice([EIGHTH, EIGHTH * 3, BAR // 2, BAR])
            raws.append({"tick": base + t, "pi": pi, "dur": dur, "bar": bar})
    return raws


def phase1_events(raws):
    """Coarse unquantized mapping: pi -> 48 + round(pi*24)."""
    return [MusicEvent(pitch=48 + int(round(r["pi"] * 24)),
                       volume=88, start_tick=r["tick"],
                       end_tick=min(r["tick"] + r["dur"],
                                    r["bar"] * BAR + BAR))
            for r in raws]


# --------------------------------------------------------------------------
# PHASE 2 — musicom rules
# --------------------------------------------------------------------------
def transform_raw(r, sec_name):
    """Variation technique applied to the raw event (pre-quantization)."""
    r = dict(r)
    if sec_name == "Intro":            # AUGMENTATION + register drop
        r["dur"] = r["dur"] * 2
        r["low"] = True
    elif sec_name == "Chorus":         # DIMINUTION (density rise)
        r["dur"] = max(SIXTEENTH * 2, r["dur"] // 2)
    elif sec_name == "VerseB":         # TRANSPOSITION +5 semitones (P4)
        r["pi"] = min(1.0, max(0.0, r["pi"] + 5.0 / 24.0))
    elif sec_name == "Bridge":         # INVERSION + register drop
        r["pi"] = 1.0 - r["pi"]
        r["low"] = True
    elif sec_name == "Outro":          # AUGMENTATION + fade
        r["dur"] = r["dur"] * 2
        r["fade"] = True
    return r


def quantize_lead(r, sec_name):
    """Rules: chord-tone quantize, grid snap, register/range, fade."""
    bar = r["bar"]
    tones = chord_tones(bar)
    target = 48 + r["pi"] * 24
    if r.get("low"):
        target -= 12
    pitch = min(tones, key=lambda x: abs(x - target))
    pitch = max(48, min(84, pitch))          # register/range enforcement
    bar_base = bar * BAR
    snapped = int(round(r["tick"] / 120.0)) * 120   # 8th/16th grid snap
    snapped = max(bar_base, min(bar_base + BAR - 120, snapped))
    end = min(snapped + r["dur"], bar_base + BAR)
    vol = 68 if r.get("fade") else 88
    return pitch, snapped, end, vol


def phase2_lead(raws):
    """Build sorted lead notes, then voice-leading + dedup."""
    notes = []
    for r in raws:
        sec = SECTION_NAMES[section_of_bar(r["bar"])]
        tr = transform_raw(r, sec)
        pitch, snapped, end, vol = quantize_lead(tr, sec)
        notes.append([snapped, pitch, end, vol])
    notes.sort(key=lambda x: (x[0], x[1]))

    # voice-leading: bound consecutive leaps to <= 16 semitones
    for i in range(1, len(notes)):
        if abs(notes[i][1] - notes[i - 1][1]) > 16:
            bar = notes[i][0] // BAR
            tones = chord_tones(bar)
            prev = notes[i - 1][1]
            cands = [t for t in tones if abs(t - prev) <= 16]
            if cands:
                notes[i][1] = min(cands, key=lambda x: abs(x - prev))

    # dedup (start_tick, pitch) keeping longest duration
    seen = {}
    for s, p, e, v in notes:
        key = (s, p)
        if key not in seen or (e - s) > (seen[key][2] - seen[key][0]):
            seen[key] = (s, p, e, v)
    deduped = sorted(seen.values(), key=lambda x: (x[0], x[1]))
    return [MusicEvent(pitch=p, volume=v, start_tick=s, end_tick=e)
            for (s, p, e, v) in deduped]


def split_by_section(events):
    out = {n: [] for n in SECTION_NAMES}
    for e in events:
        bar = e.start_tick // BAR
        si = section_of_bar(bar)
        off = si * SECTION
        out[SECTION_NAMES[si]].append(MusicEvent(
            pitch=e.pitch, volume=e.volume,
            start_tick=e.start_tick - off,
            end_tick=e.end_tick - off))
    return out


# --- arrangement voices ---
def build_808_events():
    ev = []
    for bar in range(TOTAL_BARS):
        root_pc = CHORD[flat_chords()[bar]][0]
        t = bar * BAR
        ev.append(MusicEvent(pitch=36 + root_pc, volume=95, start_tick=t,
                             end_tick=t + BAR))
    return split_by_section(ev)


def build_pad_events():
    ev = []
    for bar in range(TOTAL_BARS):
        pcs = CHORD[flat_chords()[bar]]
        t = bar * BAR
        for pc in pcs:
            ev.append(MusicEvent(pitch=48 + pc, volume=64, start_tick=t,
                                 end_tick=t + BAR))
    return split_by_section(ev)


def build_kick_events():
    ev = []
    for bar in range(TOTAL_BARS):
        sec = SECTION_NAMES[section_of_bar(bar)]
        base = bar * BAR
        if sec in ("Intro", "Outro"):
            ev.append(MusicEvent(pitch=36, volume=100, start_tick=base,
                                 end_tick=base + SIXTEENTH))
        else:
            ev.append(MusicEvent(pitch=36, volume=105, start_tick=base,
                                 end_tick=base + SIXTEENTH))
            ev.append(MusicEvent(pitch=36, volume=105,
                                 start_tick=base + 10 * SIXTEENTH,
                                 end_tick=base + 11 * SIXTEENTH))
            ev.append(MusicEvent(pitch=38, volume=100,
                                 start_tick=base + 8 * SIXTEENTH,
                                 end_tick=base + 9 * SIXTEENTH))
    return split_by_section(ev)


def build_hat_events():
    ev = []
    for bar in range(TOTAL_BARS):
        sec = SECTION_NAMES[section_of_bar(bar)]
        base = bar * BAR
        if sec in ("Intro", "Outro"):
            for i in range(8):
                ev.append(MusicEvent(pitch=70, volume=55, start_tick=base + i * EIGHTH,
                                     end_tick=base + i * EIGHTH + SIXTEENTH))
        else:
            for i in range(16):
                v = 60 if i % 2 == 0 else 75
                ev.append(MusicEvent(pitch=70, volume=v, start_tick=base + i * SIXTEENTH,
                                     end_tick=base + i * SIXTEENTH + SIXTEENTH))
            if sec == "Chorus":  # 32nd roll before beat 4
                for j in range(4):
                    ev.append(MusicEvent(pitch=70, volume=90,
                                         start_tick=base + 14 * SIXTEENTH + j * (SIXTEENTH // 2),
                                         end_tick=base + 14 * SIXTEENTH + j * (SIXTEENTH // 2) + SIXTEENTH // 2))
    return split_by_section(ev)


def build_counter_events():
    """Counterline = density rise in Chorus + Bridge (3rd/5th chord tones)."""
    ev = []
    for bar in range(TOTAL_BARS):
        sec = SECTION_NAMES[section_of_bar(bar)]
        if sec not in ("Chorus", "Bridge"):
            continue
        pcs = CHORD[flat_chords()[bar]]
        base = bar * BAR
        fifth = 48 + pcs[2]
        third = 48 + pcs[1]
        if sec == "Chorus":
            ev.append(MusicEvent(pitch=fifth, volume=70, start_tick=base,
                                 end_tick=base + QUARTER))
            ev.append(MusicEvent(pitch=third, volume=70, start_tick=base + QUARTER,
                                 end_tick=base + 2 * QUARTER))
        else:  # Bridge: descending (inverted feel)
            ev.append(MusicEvent(pitch=fifth, volume=66, start_tick=base,
                                 end_tick=base + QUARTER))
            ev.append(MusicEvent(pitch=third, volume=66, start_tick=base + QUARTER,
                                 end_tick=base + 2 * QUARTER))
    return split_by_section(ev)


def main():
    for d in (MIDI_DIR, AUDIO_DIR, ANALYSIS_DIR):
        os.makedirs(d, exist_ok=True)

    rng = random.Random(209)
    raws = generate_raw(rng)

    # ---------------- PHASE 1 (raw, single voice) ----------------
    p1_events = phase1_events(raws)
    p1_by_sec = split_by_section(p1_events)
    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    p1.create_matrix(num_voices=1, num_sections=len(SECTION_NAMES))
    p1.add_voice("LeadRaw", program=80, channel=0)
    for sec in SECTION_NAMES:
        p1.add_section(sec, bars=BARS_PER_SECTION)
        p1.fill_voice_section("LeadRaw", sec,
                              unit_from(p1_by_sec.get(sec, [])))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"PHASE1 VALIDATION FAILED: {msg1}")
    phase1_path = os.path.join(MIDI_DIR, "209-trap-half-time-rework-phase1.mid")
    p1.to_midi(phase1_path)
    assert os.path.getsize(phase1_path) > 40
    write_provenance(phase1_path, AI_ASSISTED,
                     "trap-half-time-rework phase1 (Brownian raw draft, pre-rules)",
                     parameters={"phase": 1, "method": "brownian-walk",
                                 "key": "C natural minor",
                                 "bpm": BPM, "bars": TOTAL_BARS,
                                 "rules_applied": False})

    # ---------------- PHASE 2 (rules -> full multi-voice) ----------------
    lead = phase2_lead(raws)
    lead_by_sec = split_by_section(lead)
    b808 = build_808_events()
    pad = build_pad_events()
    kick = build_kick_events()
    hat = build_hat_events()
    counter = build_counter_events()

    c = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BEATS)
    c.create_matrix(num_voices=6, num_sections=len(SECTION_NAMES))
    c.add_voice("KickSnare", program=0, channel=9)
    c.add_voice("Hat", program=0, channel=9)
    c.add_voice("808", program=MidiInstrument.BASS, channel=2)
    c.add_voice("Pad", program=MidiInstrument.STRING_ENSEMBLE, channel=3)
    c.add_voice("Lead", program=80, channel=0)
    c.add_voice("Counter", program=81, channel=1)

    fills = {
        "KickSnare": kick, "Hat": hat, "808": b808,
        "Pad": pad, "Lead": lead_by_sec, "Counter": counter,
    }
    for sec in SECTION_NAMES:
        c.add_section(sec, bars=BARS_PER_SECTION)
        for vname, m in fills.items():
            c.fill_voice_section(vname, sec, unit_from(m.get(sec, [])))

    ok2, msg2 = c.validate()
    if not ok2:
        raise RuntimeError(f"PHASE2 VALIDATION FAILED: {msg2}")
    phase2_path = os.path.join(MIDI_DIR, "209-trap-half-time-rework.mid")
    c.to_midi(phase2_path)
    assert os.path.getsize(phase2_path) > 40
    write_provenance(phase2_path, AI_ASSISTED,
                     "trap-half-time-rework phase2 (brownian + musicom rules)",
                     parameters={"phase": 2, "method": "brownian-walk + rules",
                                 "key": "C natural minor",
                                 "bpm": BPM, "bars": TOTAL_BARS,
                                 "rules_applied": True,
                                 "variations": [
                                     "Intro: augmentation + register drop",
                                     "Chorus: diminution + density rise (counterline)",
                                     "VerseB: transposition +5 semitones",
                                     "Bridge: inversion + register drop",
                                     "Outro: augmentation + fade",
                                 ]})

    write_grid_visualization(c.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=240,
                             voice_names=["KickSnare", "Hat", "808", "Pad",
                                          "Lead", "Counter"],
                             bpm=BPM)

    print("PHASE1", phase1_path, os.path.getsize(phase1_path), msg1)
    print("PHASE2", phase2_path, os.path.getsize(phase2_path), msg2)
    print("bars", TOTAL_BARS, "sections", len(SECTION_NAMES))
    print("KEY_PCS", sorted(KEY_PCS))


if __name__ == "__main__":
    main()
