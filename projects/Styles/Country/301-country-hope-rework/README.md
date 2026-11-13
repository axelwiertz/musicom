# 301-country-hope-rework

Nightly rework of `001-country-hope-loop` (legacy hand-rolled mido loop, all 6
engine standards failed). Rebuilt through the canonical `UnitMatrixComposer`
engine into a 20-bar Country suite.

## Concept
Warm, road-ready Country. G major I-IV-V backbone, boom-chick groove, hopeful
rising G-B-D arpeggio motif. 96 BPM, 4/4.

## Form (6 sections, 20 bars)
Intro(2) → Verse(4) → Chorus(4) → Verse2(4) → Bridge(4) → Outro(2)

## Voices
Lead Acoustic Guitar (25) · Steel Pad (26) · Piano (0) · Electric Bass (33) · Drums (ch9)

## Files
- `MIDI/` — phase1, perfect, humanized MIDI
- `Audio/` — perfect + humanized OGG (Opus, mastered to −14 LUFS)
- `Analysis/` — grid visualization, verification, summary
- `provenance.json`, `REPORT.md`, `index.html`

## Run
```bash
$MUSICOM_PYTHON compose.py    # build + export (phase1 + dual-version)
$MUSICOM_PYTHON verify.py     # read-only mido audits
$MUSICOM_PYTHON render.py     # fluidsynth -> master -> OGG
```
