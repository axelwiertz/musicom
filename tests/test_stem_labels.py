"""Stem-label regression tests (bug fixed 2026-09-08).

The RenderPipeline labeled stems by GM program number ONLY. Channel 9
(GM percussion) carries program 0 ("standard kit"), so every drum stem was
mislabeled "Acoustic_Grand_Piano". This suite locks the fix: any track on
channel 9 must be labeled "Drums", whatever its program byte says.
"""

import os
import sys

import mido

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from sound.render.pipeline import RenderPipeline  # noqa: E402


def _build_midi_with_tracks(path, tracks):
    """Write a MIDI with a tempo track + one track per (channel, program, notes)."""
    mid = mido.MidiFile(ticks_per_beat=480)
    tempo = mido.MidiTrack()
    tempo.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
    mid.tracks.append(tempo)
    for channel, program, notes in tracks:
        tr = mido.MidiTrack()
        tr.append(mido.Message("program_change", program=program, channel=channel, time=0))
        t = 0
        for pitch in notes:
            tr.append(mido.Message("note_on", note=pitch, velocity=90, channel=channel, time=t))
            tr.append(mido.Message("note_off", note=pitch, velocity=0, channel=channel, time=240))
            t = 240
        mid.tracks.append(tr)
    mid.save(path)


def test_drums_on_channel9_labeled_drums_not_piano(tmp_path):
    """Channel 9 + program 0 → 'Drums', never 'Acoustic_Grand_Piano'."""
    p = str(tmp_path / "drum.mid")
    _build_midi_with_tracks(p, [(9, 0, [36, 38, 42])])  # GM kit: kick, snare, hat

    pipeline = RenderPipeline()
    # Monkeypatch the renderer so no fluidsynth is needed — we only assert labels.
    pipeline.renderer.render = lambda *a, **k: None

    stems = pipeline.render_stems(p, str(tmp_path), soundfont="/nonexistent.sf2")
    labels = list(stems.keys())
    assert any("Drums" in lab for lab in labels), f"expected a Drums stem, got {labels}"
    assert not any("Acoustic_Grand" in lab for lab in labels), \
        f"drum stem mislabeled as piano: {labels}"


def test_melodic_channel_keeps_gm_name(tmp_path):
    """Channel 0 + program 73 (Flute) still labels by GM name — fix must not
    break normal melodic labeling."""
    p = str(tmp_path / "flute.mid")
    _build_midi_with_tracks(p, [(0, 73, [72, 74, 76])])

    pipeline = RenderPipeline()
    pipeline.renderer.render = lambda *a, **k: None

    stems = pipeline.render_stems(p, str(tmp_path), soundfont="/nonexistent.sf2")
    labels = list(stems.keys())
    assert any("Flute" in lab for lab in labels), f"expected a Flute stem, got {labels}"


def test_drums_negative_program_change_absent(tmp_path):
    """A drums track WITHOUT any program_change (pure note_on on ch 9) is
    still labeled Drums via the note-channel inference."""
    p = str(tmp_path / "drum_nopc.mid")
    mid = mido.MidiFile(ticks_per_beat=480)
    tempo = mido.MidiTrack()
    tempo.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
    mid.tracks.append(tempo)
    tr = mido.MidiTrack()
    tr.append(mido.Message("note_on", note=36, velocity=90, channel=9, time=0))
    tr.append(mido.Message("note_off", note=36, velocity=0, channel=9, time=240))
    mid.tracks.append(tr)
    mid.save(p)

    pipeline = RenderPipeline()
    pipeline.renderer.render = lambda *a, **k: None

    stems = pipeline.render_stems(p, str(tmp_path), soundfont="/nonexistent.sf2")
    labels = list(stems.keys())
    assert any("Drums" in lab for lab in labels), f"expected a Drums stem, got {labels}"
