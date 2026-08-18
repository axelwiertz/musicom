# Research

This directory holds **open research seeds** — ideas that are *not yet* part of
the main library. Everything else that used to live here has been promoted to
first-class code (see the table below) and removed to avoid duplication.

## What remains (open areas)

| File | Research area | Status |
|------|---------------|--------|
| `trainmodel.py` | **Neural / ML music generation** — tokenizes monophonic parts, trains an LSTM (embedding → LSTM → softmax) on music21 corpus, samples with temperature. | Seed only. The TensorFlow imports are commented out; the tokenization + sampling logic works standalone. |
| `intervalnetwork.py` | **Graph export & visualization** — builds a chromatic interval network (chord qualities as nodes, voice-leading edges) and exports to GraphML / GEXF / GML + a PNG via NetworkX/matplotlib. | Seed only. The *generation* half is now `generators/tonal_network.py`; this file is the *visualization/export* half that hasn't been promoted. |

## Promoted (removed from here — now in the library)

| Removed research file | Promoted to | Notes |
|-----------------------|-------------|-------|
| `arvo_project.py` | `generators/tintinnabuli.py` | Pärt tintinnabuli + isorhythm |
| `rhythm.py` | `structures/metrical.py` | Hierarchical metrical tree + quantization |
| `network.py` | `generators/tonal_network.py` | Weighted graph-walk progressions |
| `interval.py` | `structures/intervals.py` | Forte ICV, Hindemith, delta encoding |
| `serial.py` | `transformers/pitchsequence.py` | 12-tone row transformations |
| `pitch_class_space.py` | `rules/set_theory.py` | Combinations/permutations of pitch classes |
| `percussion_voice.py` | `structures/instrument.py` + `generators/rhythm.py` | Percussion mapping + rhythm patterns |
| `musicdata.py` | `converters/unit.py` + `converters/pattern.py` | DataFrame/Excel export |
| `pianoroll.py` | `converters/pypianoroll_converter.py` | Pianoroll ↔ MIDI |
| `audio/soundwave.py` | `sound/synthesis/additive.py` | Additive synthesis |
| `audio/sound.md` | `sound/` package | Superseded by the full synthesis stack |

## Missing / incomplete research areas (contribution targets)

These are gaps identified during the research→library audit. They are **not**
in the repo yet and are good first contributions:

1. **Neural generation** — the `trainmodel.py` seed only covers monophonic
   LSTM. Missing: polyphonic/multi-voice models, transformer/attention
   architectures, a training-data pipeline (tokenizer → dataset → model →
   sampler) wired into the `MusicUnit`/`UnitMatrix` model, and a
   `generators/`-style interface (`MusicGenerator.generate()`).
2. **Graph export & visualization** — `intervalnetwork.py` exports static
   NetworkX graphs. Missing: a reusable `visualization/` module that renders
   any tonal/interval network (GraphML/GEXF/GML/PNG), plus integration with
   `generators/tonal_network.py` so a generated progression can be drawn.
3. **Time-signature metadata in MIDI export** — `converters/midi_converter.py`
   writes tempo but **no `time_signature` meta event**; asymmetric meters
   (e.g. 7/8) are represented mathematically in the grid but not encoded in
   the exported MIDI. A contribution would add `time_signature` meta to the
   export path.
4. **Pitch-class manipulation** — `structures/pitchclass.py` still has a
   `#TODO` for inversion/retrograde/transposition of pitch-class sets.
5. **Voice-leading graphs** — `research/network.py`'s richer idea (8+ chord
   qualities with voice-leading edges, `smooth_four_voice_leading`) is only
   partially covered by `rules/voice_leading.py`; a full tonal-network
   traversal with voice-leading optimization is open.
6. **MusicPy analysis path** — `analysis/musicpy_analysis.py` exists but the
   `musicpy` dependency is optional and under-tested.

See the main [README](../README.md) → **Contributing** for how to get started.
