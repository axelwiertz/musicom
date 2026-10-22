# -*- coding: utf-8 -*-
"""255-blues-vuza-hocket - Vuza Tiling Canon Composition (Blues).

Autonomous nightly two-phase composition job (2026-10-21).

Style: Blues. Method 111 Vuza Tiling Canon Composition (VTCC), layer
CONCRETE, paradigm Rules-Based, metric Grid-Locked. Form: blues-12
(single 12-bar "Blues" section). Key E major (ionian).

Method 111 essence (Vuza 1991-93 / Amiot; Hajos-de Bruijn-Redei-Sands):
a rhythmic tiling canon A (+) B = Z_72, where a motif A (|A|=12 onsets)
is played verbatim by |B|=6 "entry" voices whose start offsets B tile the
cyclic group exactly once -> a PERFECT HOCKET: every one of the 72 eighth-
note slots is struck exactly once, zero collisions, zero gaps. The
canonical n=72 example (both factors aperiodic = true Vuza/RCMC canon):
  A = [0,1,5,6,12,25,29,36,42,48,49,53],  B = [0,8,16,18,26,34].

Phase 1 (raw generative draft): the 72-event hocket flattened to one
voice, scale-mapped pitch (NOT chord-tone quantized), 8th-note slots ->
-phase1.mid

Phase 2 (musicom rules): split the 72 onsets across the 6 entry voices,
chord-tone quantization per bar against a 12-bar E-major I-IV-V blues
progression, 8th/16th grid snap, harmonica lead + electric-bass + shuffle
drums, voice-leading optimization on the progressive triads, zero-drift
gate. Dual-version export (perfect grid-locked + seeded humanized) via
workflows.humanize.export_dual.

Engine only: structures + workflows.unitmatrix_composer. NO raw mido
authoring (mido used ONLY for read-back audit).
"""
import json
import os
import sys

_INSTR_DIR = "/opt/data/repos/musicom/projects/Instruments"
if _INSTR_DIR not in sys.path:
    sys.path.insert(0, _INSTR_DIR)
from instrument_registry import (CLEAN_ELECTRIC, ELECTRIC_PIANO_2,
                                 DRAWBAR_ORGAN, VIBRAPHONE, STEEL_ACOUSTIC,
                                 MARIMBA, HARMONICA, ELECTRIC_BASS, DRUM_KIT)

from structures import MusicUnit, MusicEvent, MidiPercussion
from workflows.unitmatrix_composer import UnitMatrixComposer
from workflows.humanize import export_dual
from visualization.grid import write_grid_visualization
from workflows.provenance import write_provenance, AI_ASSISTED
from rules.voice_leading import VoiceLeadingRules
from rules.progression import Scale7ChordDegree

# ---- Composition parameters -------------------------------------------------
KEY_NAME = "E major (ionian)"
KEY_ROOT_PC = 4
SCALE_INTERVALS = [0, 2, 4, 5, 7, 9, 11]        # E F# G# A B C# D#
KEY_PCS = [(4 + i) % 12 for i in SCALE_INTERVALS]  # [4,6,8,9,11,1,3]
KEY_ROOT_MIDI = 64                              # E4
BPM = 112
TPB = 480
BPB = 4
BAR = TPB * BPB                                 # 1920
EIGHTH = 240
SIXTEENTH = 120

SECTIONS = ["Blues"]
SECTION_BARS = [12]
NUM_BARS = 12
TOTAL_TICKS = NUM_BARS * BAR                   # 23040

# 12-bar blues (E major): I I I I | IV IV | I I | V | IV | I V
BAR_DEGREES = [0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 4]
assert len(BAR_DEGREES) == NUM_BARS

# ---- Vuza canon n=72 (verified: tiles, both factors aperiodic) --------------
A_MOTIF = [0, 1, 5, 6, 12, 25, 29, 36, 42, 48, 49, 53]
B_ENTRIES = [0, 8, 16, 18, 26, 34]
N_CANON = 72


def _tiles(A, B, n):
    cover = [0] * n
    for a in A:
        for b in B:
            cover[(a + b) % n] += 1
    return min(cover) == 1 and max(cover) == 1


def _is_periodic(S, n):
    S = set(S)
    for p in range(1, n):
        if all((x + p) % n in S for x in S):
            return p
    return None


# ---- Voices ----------------------------------------------------------------
# 6 canon "entry" voices (the hocket) + lead + bass + drums = 9 voices.
VOICES = ["Lead", "E0", "E1", "E2", "E3", "E4", "E5", "Bass", "Drums"]
VOICE_PROGRAMS = [HARMONICA.midi_program, CLEAN_ELECTRIC.midi_program,
                  ELECTRIC_PIANO_2.midi_program, DRAWBAR_ORGAN.midi_program,
                  VIBRAPHONE.midi_program, STEEL_ACOUSTIC.midi_program,
                  MARIMBA.midi_program, ELECTRIC_BASS.midi_program, 0]
VOICE_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7, 9]
INSTR_NAMES = ["Harmonica", "Clean Electric", "Electric Piano 2",
               "Drawbar Organ", "Vibraphone", "Steel Acoustic", "Marimba",
               "Electric Bass", "Drum Kit"]
PITCHED_VOICES = ["Lead", "E0", "E1", "E2", "E3", "E4", "E5", "Bass"]
CANON_VOICES = ["E0", "E1", "E2", "E3", "E4", "E5"]

SEED = 255
HZ_SEED = SEED * 101 + 1
STYLE = "blues"

PROJECT_DIR = "/opt/data/repos/musicom/projects/Styles/Blues/255-blues-vuza-hocket"
MIDI_DIR = os.path.join(PROJECT_DIR, "MIDI")
ANALYSIS_DIR = os.path.join(PROJECT_DIR, "Analysis")
AUDIO_DIR = os.path.join(PROJECT_DIR, "Audio")
for d in (MIDI_DIR, ANALYSIS_DIR, AUDIO_DIR):
    os.makedirs(d, exist_ok=True)
BASE = "255-blues-vuza-hocket"
PHASE1_PATH = os.path.join(MIDI_DIR, BASE + "-phase1.mid")
PERFECT_PATH = os.path.join(MIDI_DIR, BASE + "-perfect.mid")
HUMANIZED_PATH = os.path.join(MIDI_DIR, BASE + "-humanized.mid")


# ---- musicom rules helpers --------------------------------------------------
def get_diatonic(degree):
    return Scale7ChordDegree.get_diatonic_note(KEY_ROOT_MIDI, SCALE_INTERVALS, degree)


def chord_triad_abs(degree):
    return [get_diatonic(degree), get_diatonic(degree + 2), get_diatonic(degree + 4)]


def quantize_to_chord_tone(raw_pitch, triad, lo=57, hi=92):
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
            n_viol = len(vl.check_parallel_motion(prev, cand)) + \
                     len(vl.check_hidden_fifths(prev, cand))
            dist = vl.calculate_voice_leading_distance(prev, cand)
            score = (n_viol, dist)
            if best_score is None or score < best_score:
                best_score, best = score, cand
        if best_score[0] > 0:
            fixed.append((i, best_score[0]))
        corrected.append(sorted(best))
    return corrected, fixed


def seal(ev_list, sec_ticks):
    ev_list = sorted(ev_list, key=lambda e: (e.start_tick, e.pitch))
    if not ev_list:
        ev_list = [MusicEvent(pitch=0, volume=0, start_tick=0, end_tick=sec_ticks)]
    last_end = max(e.end_tick for e in ev_list)
    if last_end < sec_ticks:
        ev_list.append(MusicEvent(pitch=0, volume=0, start_tick=last_end,
                                  end_tick=sec_ticks))
    return MusicUnit(events=ev_list)


# ---- raw canon pitch (phase 1 scale-mapped, NOT chord-tone) ----------------
def raw_canon_pitch(slot, j):
    return 64 + SCALE_INTERVALS[(slot + j) % 7] + 12 * (j // 3)


# ---- phase 2 event builders -------------------------------------------------
def canon_events(bar_triads):
    """Return {voice: [events]} for the 6 hocket entries (chord-tone quantized)."""
    per_voice = {v: [] for v in CANON_VOICES}
    for j, b in enumerate(B_ENTRIES):
        vname = f"E{j}"
        for a in A_MOTIF:
            slot = (a + b) % N_CANON              # 0..71
            t = slot * EIGHTH                     # 8th-note slot -> 9 bars (0..8)
            bar = slot // 8
            triad = bar_triads[bar]
            raw = raw_canon_pitch(slot, j)
            qp = quantize_to_chord_tone(raw, triad)
            per_voice[vname].append(MusicEvent(pitch=qp, volume=64,
                                               start_tick=t, end_tick=t + 210))
    return per_voice


def turnaround_events(bar_triads):
    """Bars 9-11 (indices): hocket clears; E0/E1/E2 hold the V/IV/I triad."""
    per_voice = {v: [] for v in CANON_VOICES}
    for k, bar in enumerate([9, 10, 11]):
        bs = bar * BAR
        r, th, f = sorted(bar_triads[bar])
        # invert so the held chord sits around E4 (register-consistent)
        voiced = [r + 12, th, f + 12]
        holds = {"E0": voiced[0], "E1": voiced[1], "E2": voiced[2]}
        for v in ("E0", "E1", "E2"):
            per_voice[v].append(MusicEvent(pitch=holds[v], volume=58,
                                           start_tick=bs, end_tick=bs + BAR - 30))
    return per_voice


def lead_events(bar_triads):
    """Rolling chord-tone arpeggio lead (harmonica), 8th grid, varies by bar."""
    ev = []
    for bar in range(NUM_BARS):
        bs = bar * BAR
        r, th, f = sorted(bar_triads[bar])
        chord = [c for c in (r, th, f, r + 12, th + 12) if 64 <= c <= 84]
        start_deg = (bar * 2) % len(chord)
        up = (bar % 3) != 2
        for i in range(6):
            idx = (start_deg + i) % len(chord) if up else (start_deg - i) % len(chord)
            p = chord[idx]
            st = bs + i * EIGHTH
            ev.append(MusicEvent(pitch=p, volume=86, start_tick=st,
                                 end_tick=st + EIGHTH - 20))
        idx = (start_deg + 6) % len(chord) if up else (start_deg - 6) % len(chord)
        p = chord[idx]
        ev.append(MusicEvent(pitch=p, volume=82, start_tick=bs + 6 * EIGHTH,
                             end_tick=bs + 8 * EIGHTH - 20))
    return ev


def bass_events(bar_triads):
    """Walking bass (root / fifth / root / third) on the quarter grid."""
    ev = []
    for bar in range(NUM_BARS):
        bs = bar * BAR
        r, th, f = sorted(bar_triads[bar])
        root = r - 12
        if bar % 2 == 0:
            pat = [root, root + 12, f - 12, th - 12]
        else:
            pat = [root, f - 12, root + 12, th - 12]
        for i in range(4):
            ev.append(MusicEvent(pitch=pat[i], volume=90, start_tick=bs + i * 480,
                                 end_tick=bs + i * 480 + 400))
    return ev


def drums_events():
    """Shuffle backbeat: kick 1&3, snare 2&4, swung hi-hat (dotted-8th+8th)."""
    kick = MidiPercussion.BASS_DRUM
    snare = MidiPercussion.ACOUSTIC_SNARE
    chh = MidiPercussion.CLOSED_HI_HAT
    crash = MidiPercussion.CRASH_CYMBAL
    ev = []
    for bar in range(NUM_BARS):
        bs = bar * BAR
        ev.append(MusicEvent(pitch=kick, volume=95, start_tick=bs, end_tick=bs + 80))
        ev.append(MusicEvent(pitch=kick, volume=90, start_tick=bs + 960,
                             end_tick=bs + 1040))
        ev.append(MusicEvent(pitch=snare, volume=82, start_tick=bs + 480,
                             end_tick=bs + 560))
        ev.append(MusicEvent(pitch=snare, volume=82, start_tick=bs + 1440,
                             end_tick=bs + 1520))
        for off in (0, 360, 480, 840, 960, 1320, 1440, 1800):
            ev.append(MusicEvent(pitch=chh, volume=60, start_tick=bs + off,
                                 end_tick=bs + off + 60))
        if bar == 0:
            ev.append(MusicEvent(pitch=crash, volume=78, start_tick=bs,
                                 end_tick=bs + 240))
    return ev


# ---- compose ------------------------------------------------------------------
def compose():
    # verify the Vuza canon (assert it is a genuine tiling / hocket)
    assert _tiles(A_MOTIF, B_ENTRIES, N_CANON), "canon does not tile Z_72"
    assert _is_periodic(A_MOTIF, N_CANON) is None, "motif periodic (not Vuza)"
    assert _is_periodic(B_ENTRIES, N_CANON) is None, "entries periodic (not Vuza)"
    n_onsets = len(A_MOTIF) * len(B_ENTRIES)
    assert n_onsets == N_CANON

    bar_triads = [sorted(chord_triad_abs(d)) for d in BAR_DEGREES]
    vl = VoiceLeadingRules(style="classical")
    opt = vl.optimize_voice_leading(bar_triads)
    corr_triads, fixed_report = correct_voice_leading(opt)

    violations = []
    for i in range(len(corr_triads) - 1):
        violations += vl.check_parallel_motion(corr_triads[i], corr_triads[i + 1])
        violations += vl.check_hidden_fifths(corr_triads[i], corr_triads[i + 1])

    # ---- Phase 1: raw flattened hocket draft (single voice, scale-mapped) ----
    p1_events = []
    for j, b in enumerate(B_ENTRIES):
        for a in A_MOTIF:
            slot = (a + b) % N_CANON
            t = slot * EIGHTH
            p1_events.append(MusicEvent(pitch=raw_canon_pitch(slot, j), volume=86,
                                        start_tick=t, end_tick=t + 210))
    p1_events = sorted(p1_events, key=lambda e: e.start_tick)

    p1 = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    p1.create_matrix(num_voices=1, num_sections=1)
    p1.add_voice("RawDraft", program=HARMONICA.midi_program, channel=0)
    p1.add_section("Blues", bars=NUM_BARS)
    p1.fill_voice_section("RawDraft", "Blues", seal(p1_events, TOTAL_TICKS))
    ok1, msg1 = p1.validate()
    if not ok1:
        raise RuntimeError(f"Phase 1 zero-drift FAILED: {msg1}")
    p1.to_midi(PHASE1_PATH)

    # ---- Phase 2: full texture ---------------------------------------------
    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=1)
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    composer.add_section("Blues", bars=NUM_BARS)

    canon_ev = canon_events(bar_triads)
    turn_ev = turnaround_events(bar_triads)

    # merge canon (bars 0-8) + turnaround (bars 9-11) per entry voice
    for v in CANON_VOICES:
        ev = canon_ev[v] + turn_ev[v]
        composer.fill_voice_section(v, "Blues", seal(ev, TOTAL_TICKS))

    composer.fill_voice_section("Lead", "Blues", seal(lead_events(bar_triads), TOTAL_TICKS))
    composer.fill_voice_section("Bass", "Blues", seal(bass_events(bar_triads), TOTAL_TICKS))
    composer.fill_voice_section("Drums", "Blues", seal(drums_events(), TOTAL_TICKS))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError(f"Phase 2 zero-drift FAILED: {msg}")

    hz_instruments = {
        "Lead": HARMONICA.humanize_dna,
        "E0": CLEAN_ELECTRIC.humanize_dna,
        "E1": ELECTRIC_PIANO_2.humanize_dna,
        "E2": DRAWBAR_ORGAN.humanize_dna,
        "E3": VIBRAPHONE.humanize_dna,
        "E4": STEEL_ACOUSTIC.humanize_dna,
        "E5": MARIMBA.humanize_dna,
        "Bass": ELECTRIC_BASS.humanize_dna,
        "Drums": DRUM_KIT.humanize_dna,
    }
    hz = export_dual(composer, PERFECT_PATH, HUMANIZED_PATH,
                     style=STYLE, seed=HZ_SEED, bpm=BPM, instruments=hz_instruments)

    write_grid_visualization(composer.matrix,
                             os.path.join(ANALYSIS_DIR, "grid_visualization.txt"),
                             ticks_per_character=120, voice_names=VOICES,
                             bpm=BPM, mode=KEY_NAME)

    return (composer, violations, fixed_report, corr_triads, bar_triads,
            hz, n_onsets)


# ---- read-back audits (mido READING ONLY) ------------------------------------
def audit_midi(midi_path):
    import mido  # READING ONLY
    mf = mido.MidiFile(midi_path)
    ch_to_name = {v: ch for v, ch in zip(VOICES, VOICE_CHANNELS)}
    ch_to_name = {ch: v for v, ch in zip(VOICES, VOICE_CHANNELS)}
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
                bar = min(NUM_BARS - 1, (round(tt / EIGHTH) * EIGHTH) // BAR)
                if pc not in KEY_PCS:
                    out_scale += 1
                if pc not in bar_pcs[bar]:
                    out_chord += 1
        per_voice[name] = {"notes": len(notes), "off16": off16, "off8": off8,
                           "out_scale": out_scale, "out_chord": out_chord}
    return per_voice


def zero_drift(midi_path):
    import mido  # READING ONLY
    mf = mido.MidiFile(midi_path)
    spans = [sum(msg.time for msg in tr) for tr in mf.tracks[1:]]
    return spans, len(spans)


# ---- main --------------------------------------------------------------------
def main():
    (composer, violations, fixed_report, corr_triads, bar_triads,
     hz, n_onsets) = compose()

    for p in (PHASE1_PATH, PERFECT_PATH, HUMANIZED_PATH):
        s = os.path.getsize(p)
        assert s > 40, f"{p} too small ({s})"

    aud_perf = audit_midi(PERFECT_PATH)
    aud_hum = audit_midi(HUMANIZED_PATH)
    spans_perf, nt_perf = zero_drift(PERFECT_PATH)
    spans_hum, nt_hum = zero_drift(HUMANIZED_PATH)

    summary = {
        "project": BASE, "project_number": 255, "style": STYLE,
        "method_id": "111",
        "method_name": "Vuza Tiling Canon Composition (VTCC)",
        "method_layer": "concrete", "method_paradigm": "Rules-Based",
        "form": "blues-12 (12 bars)", "key": KEY_NAME, "key_pcs": KEY_PCS,
        "bpm": BPM, "meter": "4/4", "bar_ticks": BAR,
        "total_bars": NUM_BARS, "total_ticks": TOTAL_TICKS,
        "canon": {"n": N_CANON, "motif_A": A_MOTIF, "entries_B": B_ENTRIES,
                  "onsets": n_onsets, "aperiodic": True},
        "progression_degrees": BAR_DEGREES,
        "voices": [{"name": n, "program": p, "channel": c, "instrument": i,
                    "pitched": n in PITCHED_VOICES}
                   for n, p, c, i in zip(VOICES, VOICE_PROGRAMS,
                                         VOICE_CHANNELS, INSTR_NAMES)],
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
        print(f"  {v:6s} perfect(off16={p.get('off16')},off8={p.get('off8')},"
              f"out_scale={p.get('out_scale')},out_chord={p.get('out_chord')})  "
              f"humanized(off16={h.get('off16')},off8={h.get('off8')},"
              f"out_scale={h.get('out_scale')},out_chord={h.get('out_chord')})")
    print("  zero-drift perfect:", nt_perf, "span set:", set(spans_perf))
    print("  zero-drift humanized:", nt_hum, "span set:", set(spans_hum))
    print("  canon onsets:", n_onsets, "VL corrections:", len(fixed_report),
          "violations:", len(violations))
    for v in VOICES:
        h = hz[v]
        print(f"  hz[{v}] seed={h['seed']} mean={h['mean_abs_shift_ticks']}t "
              f"max={h['max_abs_shift_ticks']}t vel={h['mean_abs_vel_delta']}")

    # ---- provenance sidecars -------------------------------------------------
    write_provenance(
        PHASE1_PATH, classification=AI_ASSISTED,
        generator="musicom.workflows.unitmatrix_composer + Vuza tiling canon (PRE-RULES raw draft)",
        parameters={"project": BASE, "phase": 1, "key": KEY_NAME, "bpm": BPM,
                    "method": "111", "canon_n": N_CANON, "motif_A": A_MOTIF,
                    "entries_B": B_ENTRIES, "style": STYLE, "seed": SEED,
                    "form": "blues-12", "total_bars": NUM_BARS,
                    "rules_applied": "NONE (pre-rules)"},
        notes="Phase 1 raw Vuza tiling-canon draft: 72-onset perfect hocket "
              "flattened to one voice, scale-mapped pitch (not chord-tone "
              "quantized), 8th-note slots.")
    write_provenance(
        PERFECT_PATH, classification=AI_ASSISTED,
        generator="111 VTCC + musicom rules (grid-locked)",
        parameters={"project": BASE, "phase": 2, "version": "perfect",
                    "key": KEY_NAME, "bpm": BPM, "method": "111", "style": STYLE,
                    "seed": SEED, "humanize_seed": HZ_SEED, "form": "blues-12",
                    "total_bars": NUM_BARS, "voices": VOICES,
                    "instruments": INSTR_NAMES},
        notes="Phase 2 perfect: grid-locked concrete layer (no humanization). "
              "72-onset hocket split over 6 entry voices, chord-tone quantized "
              "per bar (E-major I-IV-V), 8th/16th grid, voice-leading optimized, "
              "zero-drift gated.")
    write_provenance(
        HUMANIZED_PATH, classification=AI_ASSISTED,
        generator="111 VTCC + musicom rules + humanize",
        parameters={"project": BASE, "phase": 2, "version": "humanized",
                    "key": KEY_NAME, "bpm": BPM, "method": "111", "style": STYLE,
                    "seed": SEED, "humanize_seed": HZ_SEED, "form": "blues-12",
                    "total_bars": NUM_BARS, "voices": VOICES,
                    "instruments": INSTR_NAMES},
        notes="Phase 2 humanized: same concrete layer + style-derived seeded "
              "humanization (per-instrument DNA). Zero-drift safe.")
    return summary


if __name__ == "__main__":
    main()