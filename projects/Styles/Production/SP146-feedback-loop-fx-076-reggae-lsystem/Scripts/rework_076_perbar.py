# -*- coding: utf-8 -*-
"""Rework 076-reggae-lsystem for the PRE-FLIGHT harmony gate.

The source Phase-2 build quantizes the Lead organ and Skank guitar to the
SECTION's first-bar triad (one chord per 4-bar section), while the bass and the
harmonic bed (i - bVII - i - bVI, i.e. Am - G - Am - F) move PER BAR. Result:
115 out-of-chord notes (35 lead + 80 skank) in bars where the bar chord differs
from the section chord. This rework re-quantizes Lead + Skank to the PER-BAR
voice-leading-corrected triad so every pitched note is a chord tone of its own
bar. Bass is already per-bar correct (0 out-of-chord). Drums untouched.

Rebuild goes through the canonical engine (UnitMatrixComposer -> validate() ->
to_midi). The source project MIDI is NOT modified; a reworked copy is written
into this Production output folder.
"""
import importlib.util
import json
import os

from structures import MusicUnit, MusicEvent, MidiInstrument
from workflows.unitmatrix_composer import UnitMatrixComposer

# --- load the source compose.py as a module (reuse canonical logic) --------
SRC = "/opt/data/repos/musicom/projects/Styles/Reggae/076-reggae-lsystem/compose.py"
spec = importlib.util.spec_from_file_location("reggae_compose", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# --- constants (mirror source) --------------------------------------------
KEY_ROOT_MIDI = mod.KEY_ROOT_MIDI          # 45 (A2)
SCALE_INTERVALS = mod.SCALE_INTERVALS      # aeolian
BPM = mod.BPM
TPB = mod.TPB
BPB = mod.BPB
BAR = mod.BAR
SECTION_NAMES = mod.SECTION_NAMES
SECTION_BARS = mod.SECTION_BARS
NUM_SECTIONS = mod.NUM_SECTIONS
SECTION_TICKS = mod.SECTION_TICKS
CHORD_DEG_PER_BAR = mod.CHORD_DEG_PER_BAR   # 24 entries
VOICES = mod.VOICES
VOICE_PROGRAMS = mod.VOICE_PROGRAMS
VOICE_CHANNELS = mod.VOICE_CHANNELS
SEED = mod.SEED

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIDI_OUT = os.path.join(OUT, "MIDI")
os.makedirs(MIDI_OUT, exist_ok=True)
REWORKED_PATH = os.path.join(MIDI_OUT, "076-reggae-lsystem-reworked.mid")


def compose_reworked():
    word = mod.fib_word()
    raw_events = mod.lsystem_phase1_events(word, seed=SEED)
    phase1_sections = mod.split_events_by_section(raw_events, SECTION_TICKS,
                                                  NUM_SECTIONS)

    # per-bar voice-leading-corrected triads (canonical helpers)
    base_triads = [sorted(mod.chord_triad_abs(d)) for d in CHORD_DEG_PER_BAR]
    vl = mod.VoiceLeadingRules(style="classical")
    optimized = vl.optimize_voice_leading(base_triads)
    corrected_triads, fixed_report = mod.correct_voice_leading(optimized)

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=len(VOICES), num_sections=NUM_SECTIONS)
    for name, prog, ch in zip(VOICES, VOICE_PROGRAMS, VOICE_CHANNELS):
        composer.add_voice(name, program=prog, channel=ch)
    for n in SECTION_NAMES:
        composer.add_section(n, bars=SECTION_BARS)

    for s in range(NUM_SECTIONS):
        sec_events = phase1_sections[s].events

        # --- Lead: L-system contour, PER-BAR chord-tone quantized ----------
        lead_evs = []
        for e in sec_events:
            if e.pitch == 0:
                continue
            bar = e.start_tick // BAR
            tr = corrected_triads[s * SECTION_BARS + bar]   # PER-BAR triad
            qp = mod.quantize_to_chord_tone(e.pitch, tr)
            lead_evs.append(MusicEvent(pitch=qp, volume=e.volume,
                                       start_tick=e.start_tick,
                                       end_tick=e.end_tick))
        composer.fill_voice_section("Lead", SECTION_NAMES[s],
                                    MusicUnit(events=lead_evs))

        # --- Skank: staccato offbeat chops, PER-BAR triad ------------------
        skank_evs = []
        if s < NUM_SECTIONS - 1:      # dub cut: no skank in outro
            for bar in range(SECTION_BARS):
                t0 = bar * BAR
                tr = corrected_triads[s * SECTION_BARS + bar]  # PER-BAR triad
                for beat in range(BPB):
                    off = 480 * beat + 240          # the 'and'
                    for p in tr:
                        skank_evs.append(MusicEvent(
                            pitch=p + 12, volume=74,
                            start_tick=t0 + off, end_tick=t0 + off + 90))
        composer.fill_voice_section("Skank", SECTION_NAMES[s],
                                    MusicUnit(events=skank_evs))

        # --- Bass: one-drop bounce (already per-bar correct) ---------------
        bass_evs = []
        for bar in range(SECTION_BARS):
            t0 = bar * BAR
            tr = corrected_triads[s * SECTION_BARS + bar]
            root = tr[0] - 12
            fifth = tr[2] - 12
            bass_evs += [
                MusicEvent(pitch=root, volume=96, start_tick=t0,
                           end_tick=t0 + 240),
                MusicEvent(pitch=root, volume=92, start_tick=t0 + 240,
                           end_tick=t0 + 480),
                MusicEvent(pitch=fifth, volume=90, start_tick=t0 + 720,
                           end_tick=t0 + 960),
                MusicEvent(pitch=root, volume=100, start_tick=t0 + 960,
                           end_tick=t0 + 1440),
                MusicEvent(pitch=fifth, volume=90, start_tick=t0 + 1440,
                           end_tick=t0 + 1680),
                MusicEvent(pitch=root + 12, volume=84, start_tick=t0 + 1680,
                           end_tick=t0 + 1920),
            ]
        composer.fill_voice_section("Bass", SECTION_NAMES[s],
                                    MusicUnit(events=bass_evs))

        # --- Drums: one-drop kit (unchanged) -------------------------------
        drum_evs = []
        for bar in range(SECTION_BARS):
            t0 = bar * BAR
            for k in range(0, BAR, 240):
                vel = 52 if (k // 240) % 2 == 0 else 44
                drum_evs.append(MusicEvent(pitch=42, volume=vel,
                                           start_tick=t0 + k,
                                           end_tick=t0 + k + 90))
            drum_evs.append(MusicEvent(pitch=36, volume=104,
                                       start_tick=t0 + 960,
                                       end_tick=t0 + 1120))
            drum_evs.append(MusicEvent(pitch=38, volume=92,
                                       start_tick=t0 + 960,
                                       end_tick=t0 + 1100))
            drum_evs.append(MusicEvent(pitch=46, volume=64,
                                       start_tick=t0 + 1800,
                                       end_tick=t0 + 1910))
            if s in (2, 4):
                drum_evs.append(MusicEvent(pitch=38, volume=56,
                                           start_tick=t0 + 1080,
                                           end_tick=t0 + 1160))
        composer.fill_voice_section("Drums", SECTION_NAMES[s],
                                    MusicUnit(events=drum_evs))

        # --- pad every cell to exact section boundary (zero-drift) ---------
        for voice_name in VOICES:
            row = [v["name"] for v in composer.voices].index(voice_name)
            unit = composer.matrix.get_unit((row, s))
            last_end = max(e.end_tick for e in unit.events) if unit.events else 0
            if last_end < SECTION_TICKS:
                unit.add_event(MusicEvent(pitch=0, volume=0,
                                          start_tick=last_end,
                                          end_tick=SECTION_TICKS))

    ok, msg = composer.validate()
    if not ok:
        raise RuntimeError("reworked zero-drift validation FAILED: %s" % msg)
    composer.to_midi(REWORKED_PATH)
    return corrected_triads


if __name__ == "__main__":
    triads = compose_reworked()
    size = os.path.getsize(REWORKED_PATH)
    assert size > 40, "reworked MIDI too small (%d)" % size
    print("REWORKED_MIDI=" + REWORKED_PATH)
    print("size=%d" % size)
    print("n_triads=%d" % len(triads))
    prov = {
        "project": "076-reggae-lsystem",
        "rework": "per-bar chord-tone quantization (lead + skank)",
        "reason": "PRE-FLIGHT harmony gate: section-chord quantization left "
                  "115 out-of-chord notes in bars whose chord differs from the "
                  "section chord",
        "key": "A aeolian",
        "progression_per_bar": mod.PROG_NAMES,
        "voices": VOICES,
        "engine": "UnitMatrixComposer (validate() passed)",
        "bpm": BPM, "ticks_per_beat": TPB, "bars": NUM_SECTIONS * SECTION_BARS,
    }
    prov_path = REWORKED_PATH + ".provenance.json"
    with open(prov_path, "w") as f:
        json.dump(prov, f, indent=2)
    print("PROVENANCE=" + prov_path)
