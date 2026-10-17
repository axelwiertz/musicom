# -*- coding: utf-8 -*-
"""246 — Balfolk Storytelling Jig (2-minute, 6/8 jig, D major).

Composed through the musicom engine (UnitMatrixComposer → validate → to_midi),
applying the methods suited to balfolk dance-tune storytelling:

  * 004 Prosodic Narrative Coupling  — melody contour = speech narrative:
      question phrase rises (unresolved), answer phrase falls (resolved);
      downbeat/stressed 6/8 slots carry the velocity accents (syllable stress).
  * 005 Prosodic Syntax Mapping     — the "period" punctuation maps to a
      ONE-BAR MELODY REST (rest placement): the tune takes a breath while
      the accompaniment plays on underneath.
  * 006 Cadence & Closure Mapping   — question ends on V (half cadence),
      answer ends on I (authentic cadence); classical closure strengths.
  * 007 Narrative Arc Register Plan — three passes rise D4 -> D5 (story builds).
  * 008 Call-Response Allocation    — question = leaner texture, answer fuller.

Form: 24 phrase-sentences, each = 4 bars storytelling + 1 bar melody-rest
(accompaniment continues). 3 passes x AABB, A=D-major home, B=G-centred lift.
120 bars of 6/8 at dotted-quarter=118 -> ~2:04.

Rendering: TWO versions side by side (workflow 2026-10-17):
  * `-perfect`   — grid-locked concrete layer, NO humanization (the
      compositional truth).
  * `-humanized` — style=balfolk folk profile + per-instrument DNA, seeded,
      zero-drift safe (applied in place on the same composer).

Ticks: ticks_per_beat=720 (1 beat = dotted quarter), beats_per_bar=2 ->
BAR = 1440 = one 6/8 measure. 8th = 240, 16th = 120 (grid-locked).
"""
import os
import sys
import numpy as np

REPO = "/opt/data/repos/musicom"
PROJ = "/opt/data/projects/Styles/Balfolk/246-balfolk-storytelling-jig"
sys.path.insert(0, f"{REPO}/projects/Instruments")

BPM = 118             # dotted-quarter tempo (standard 6/8 jig convention)
TPB = 720             # ticks per dotted-quarter
BPB = 2               # beats (dotted quarters) per 6/8 bar
BAR = TPB * BPB       # 1440 = one 6/8 measure
EIGHTH = BAR // 6     # 240
SIXTEENTH = BAR // 12  # 120

# jig "jig-gi-ty" lilt: within each dotted-quarter group of 3, dotted-8th +
# 16th + 8th. Onsets are all multiples of SIXTEENTH (grid-locked).
JIG_SLOT = [0, 3 * SIXTEENTH, 2 * EIGHTH, BAR // 2,
            BAR // 2 + 3 * SIXTEENTH, BAR // 2 + 2 * EIGHTH]
JIG_DUR = [3 * SIXTEENTH, SIXTEENTH, EIGHTH,
           3 * SIXTEENTH, SIXTEENTH, EIGHTH]

# D major scale degrees 0..7 -> semitones above D4
D_DEG_SEMI = [0, 2, 4, 5, 7, 9, 11, 12]
D_PC = {1, 2, 4, 6, 7, 9, 11}     # D major pitch classes (D E F# G A B C#)

# voices (balfolk ensemble)
LEAD, CHORDS, BASS, DRUMS = "Lead", "Chords", "Bass", "Drums"

HUMANIZE_SEED = 246
BASE = "246-balfolk-storytelling-jig"


def chord_tones(root_pc_deg, base=43):
    """root_pc_deg: degree 0..6 of D major -> (root, third, fifth) MIDI."""
    root = 50 + D_DEG_SEMI[root_pc_deg]          # ~D3 area
    return (root, root + 4, root + 7)            # all major triads (I/IV/V)


def phrase_harmony(part, direction):
    """Return list of 4 chords (one per bar) as degree triples.
    part 'A' | 'B', direction 'question' | 'answer'."""
    if part == "A":
        if direction == "question":
            return [0, 4, 0, 4]     # I V I V  (half cadence on V)
        return [4, 0, 3, 0]         # V I IV I (resolves to I)
    # B part — G-centred lift
    if direction == "question":
        return [3, 0, 4, 0]         # IV I V I
    return [3, 4, 0, 0]             # IV V I I (strong authentic close)


def narrative_degrees(direction, n=24, seed=0):
    """Narrative contour: question rises tonic->dominant, answer falls
    dominant->tonic, with a single melodic wave (the 'story' bump)."""
    rng = np.random.default_rng(seed)
    start, end = (0.0, 4.0) if direction == "question" else (4.0, 0.0)
    degs = []
    for i in range(n):
        t = i / (n - 1.0)
        linear = start + (end - start) * t
        wave = 0.7 * np.sin(np.pi * 2.0 * t)   # rise then settle
        jitter = rng.normal(0.0, 0.15)
        degs.append(int(round(max(0.0, min(7.0, linear + wave + jitter)))))
    return degs


def build():
    from structures import MusicUnit, MusicEvent
    from workflows.unitmatrix_composer import UnitMatrixComposer
    from instrument_registry import by_name

    VIOLIN = by_name("violin").midi_program
    GUITAR = by_name("acoustic_guitar").midi_program
    CONTRABASS = by_name("double_bass").midi_program

    PHRASES = 24            # 3 passes x 8 phrases (AABB each)
    BARS_PER_PHRASE = 5     # 4 storytelling + 1 melody-rest
    OCTAVE_BY_PASS = [0, 0, 1]
    BREATH_CHORD = 4        # dominant (V) held under the melody rest

    composer = UnitMatrixComposer(bpm=BPM, ticks_per_beat=TPB, beats_per_bar=BPB)
    composer.create_matrix(num_voices=4, num_sections=PHRASES)
    composer.add_voice(LEAD, program=VIOLIN, channel=0)
    composer.add_voice(CHORDS, program=GUITAR, channel=1)
    composer.add_voice(BASS, program=CONTRABASS, channel=2)
    composer.add_voice(DRUMS, program=0, channel=9)

    for p in range(PHRASES):
        composer.add_section(f"P{p:02d}", bars=BARS_PER_PHRASE)

    section_len = BARS_PER_PHRASE * BAR   # 5 * 1440 = 7200
    meta = []

    for p in range(PHRASES):
        part = "B" if (p % 8) >= 4 else "A"
        direction = "question" if (p % 2 == 0) else "answer"
        pss = p // 8
        octave = OCTAVE_BY_PASS[pss]
        meta.append((part, direction, pss, octave))

        chords_deg = phrase_harmony(part, direction)
        degs = narrative_degrees(direction, n=24, seed=p + 1)

        # ---- Lead: storytelling melody, 4 bars; RESTS the 5th bar ----
        lead_evs = []
        for i in range(24):                     # 4 bars x 6 slots (bar 4 empty)
            bar = i // 6
            slot = i % 6
            start = bar * BAR + JIG_SLOT[slot]
            dur = JIG_DUR[slot]
            pitch = 62 + D_DEG_SEMI[degs[i]] + 12 * octave
            vel = 100 if slot in (0, 3) else 68  # 004: stress accents
            lead_evs.append(MusicEvent(pitch=pitch, volume=vel,
                                       start_tick=start, end_tick=start + dur))

        # ---- Chords: guitar off-beat strum, 5 bars; strum rings (sustain) ----
        chord_evs = []
        for bar in range(5):
            cd = chords_deg[bar] if bar < 4 else BREATH_CHORD
            r, th, fi = chord_tones(cd)
            for off in (EIGHTH, 4 * EIGHTH):
                for tone in (r, th, fi):
                    chord_evs.append(MusicEvent(pitch=tone, volume=70,
                                                start_tick=bar * BAR + off,
                                                end_tick=bar * BAR + off + 2 * EIGHTH))

        # ---- Bass: dotted-quarter pulse, 5 bars; rings most of the beat ----
        bass_evs = []
        for bar in range(5):
            cd = chords_deg[bar] if bar < 4 else BREATH_CHORD
            root = 38 + D_DEG_SEMI[cd]
            for beat in (0, BAR // 2):
                bass_evs.append(MusicEvent(pitch=root, volume=92,
                                           start_tick=bar * BAR + beat,
                                           end_tick=bar * BAR + beat + 5 * SIXTEENTH))

        # ---- Drums: tapan (kick 1, rim 4), 5 bars ----
        drum_evs = []
        for bar in range(5):
            drum_evs.append(MusicEvent(pitch=36, volume=100,
                                       start_tick=bar * BAR,
                                       end_tick=bar * BAR + SIXTEENTH))
            drum_evs.append(MusicEvent(pitch=37, volume=60,
                                       start_tick=bar * BAR + BAR // 2,
                                       end_tick=bar * BAR + BAR // 2 + SIXTEENTH))

        def wrap(evs):
            u = MusicUnit()
            for e in evs:
                u.add_event(e)
            u.add_event(MusicEvent(0, 0, section_len, section_len))
            return u

        composer.set_unit(0, p, wrap(lead_evs))
        composer.set_unit(1, p, wrap(chord_evs))
        composer.set_unit(2, p, wrap(bass_evs))
        composer.set_unit(3, p, wrap(drum_evs))

    os.makedirs(f"{PROJ}/MIDI", exist_ok=True)

    # ---- dual-version export: perfect (grid-locked) + humanized (DNA) ----
    from workflows.humanize import export_dual
    hz_instruments = {
        LEAD: by_name("violin").humanize_dna,
        CHORDS: by_name("acoustic_guitar").humanize_dna,
        BASS: by_name("double_bass").humanize_dna,
        DRUMS: by_name("drum_kit").humanize_dna,
    }
    perfect_path = f"{PROJ}/MIDI/{BASE}-perfect.mid"
    humanized_path = f"{PROJ}/MIDI/{BASE}-humanized.mid"
    hz = export_dual(composer, perfect_path, humanized_path,
                     style="balfolk", seed=HUMANIZE_SEED, bpm=BPM,
                     instruments=hz_instruments)

    paths = {"perfect": perfect_path, "humanized": humanized_path}
    return paths, meta, hz


def render_and_master(midi_path, label):
    from utilities.env import fluidsynth_bin
    from sound.render.fluidsynth import discover_soundfont
    from sound.effects.mastering import master, target_for_style
    from sound.utils.io import read_wav, write_wav
    import subprocess

    os.makedirs(f"{PROJ}/Audio", exist_ok=True)
    sf = discover_soundfont()
    wav_path = f"{PROJ}/Audio/{BASE}-{label}.wav"
    # -R no -C no: dry render — the melody-rest bar must read as a real gap.
    r = subprocess.run([fluidsynth_bin(), "-ni", "-g", "1.2", "-R", "no", "-C", "no",
                        "-F", wav_path, sf, midi_path], capture_output=True, text=True)
    if r.returncode != 0 or os.path.getsize(wav_path) < 1000:
        raise RuntimeError(f"fluidsynth failed: {r.stderr[-500:]}")

    audio, sr = read_wav(wav_path)
    target = target_for_style("balfolk")        # 'folk' in 'balfolk' -> -16
    mastered, rep = master(audio, target_lufs=target, ceiling_db=-1.0, sample_rate=sr)
    write_wav(wav_path, mastered, sr, normalize=False)

    ogg_path = f"{PROJ}/Audio/{BASE}-{label}.ogg"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav_path,
                    "-codec:a", "libopus", "-b:a", "128k", ogg_path],
                   capture_output=True, text=True)
    return wav_path, ogg_path, target, rep


def verify(midi_path):
    import mido
    mid = mido.MidiFile(midi_path)
    lengths = [sum(m.time for m in tr) for tr in mid.tracks
               if any(x.type in ("note_on", "note_off") for x in tr)]
    zero_drift = len(set(lengths)) == 1

    # per-track onset maps + harmony audit (skip ch9 drums for scale check)
    out_of_scale = 0
    total_pitched = 0
    track_onsets = {}     # track_index -> set of absolute ticks with a note_on
    for ti, tr in enumerate(mid.tracks):
        ch = None
        for m in tr:
            if m.type == "program_change":
                ch = m.channel
        t = 0
        onsets = set()
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0 and m.note > 0:
                onsets.add(t)
                if ch != 9:
                    total_pitched += 1
                    if m.note % 12 not in D_PC:
                        out_of_scale += 1
        if onsets:
            track_onsets[ti] = onsets

    # melody-rest check: lead track has NO onset in each rest bar (bar 4 of
    # each 5-bar section), accompaniment tracks DO.
    PHRASES = 24
    BARS_PER_PHRASE = 5
    rest_bar_lo = [p * BARS_PER_PHRASE * BAR + 4 * BAR for p in range(PHRASES)]
    rest_bar_hi = [p * BARS_PER_PHRASE * BAR + 5 * BAR for p in range(PHRASES)]
    lead_idx = 1        # track 0 = conductor; track 1 = Lead (first add_voice)
    lead_onsets = track_onsets.get(lead_idx, set())
    lead_in_rest = sum(1 for lo, hi in zip(rest_bar_lo, rest_bar_hi)
                       if any(lo <= o < hi for o in lead_onsets))
    acc_in_rest = 0
    for ti, onsets in track_onsets.items():
        if ti == lead_idx:
            continue
        acc_in_rest += sum(1 for lo, hi in zip(rest_bar_lo, rest_bar_hi)
                           if any(lo <= o < hi for o in onsets))

    # grid audit: onsets OFF the 16th grid prove humanization ran (perfect=0).
    off_grid = sum(1 for onsets in track_onsets.values()
                   for o in onsets if o % SIXTEENTH != 0)

    return {
        "zero_drift": zero_drift,
        "track_lengths": lengths,
        "out_of_scale": out_of_scale,
        "total_pitched": total_pitched,
        "melody_rest_violations": lead_in_rest,     # must be 0
        "accomp_bars_with_rest_content": acc_in_rest,  # should be 24 (one per rest bar)
        "off_grid_onsets": off_grid,                # perfect=0, humanized>0
    }


if __name__ == "__main__":
    paths, meta, hz = build()
    for label in ("perfect", "humanized"):
        midi_path = paths[label]
        wav_path, ogg_path, target, rep = render_and_master(midi_path, label)
        v = verify(midi_path)
        print(f"[{label.upper()}]")
        print("  MIDI:", midi_path, os.path.getsize(midi_path), "bytes")
        print("  OGG:", ogg_path, os.path.getsize(ogg_path), "bytes")
        print("  MASTER target", target, "-> LUFS", rep["integrated_lufs"],
              "dBTP", rep["true_peak_db"])
        print("  VERIFY:", v)
    for voice, s in hz.items():
        print(f"  HUMANIZE {voice}: seed={s['seed']} mean_shift={s['mean_abs_shift_ticks']}t "
              f"max={s['max_abs_shift_ticks']}t vel_delta={s['mean_abs_vel_delta']} "
              f"(timing_ms={s['profile']['timing_sigma_ms']} layback={s['profile']['layback_ms']})")
    print("DONE")
