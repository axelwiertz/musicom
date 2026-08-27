# 078-soul-voiceleading — Soul / Method 007 Voice-Leading Graph Search

**Style:** Soul (F minor) · **Method:** 007 Voice-Leading Graph Search (TonalNetworkGenerator)
**BPM:** 96 · **Key:** F natural minor · **Bars:** 24 · **Sections:** Intro, Verse, Chorus, Verse2, Chorus2, Outro (4 bars each)

## Concept
Soul groove driven by a weighted random walk over the tonal function graph.
The graph nodes are functional regions (tonic/subdominant/dominant/mediant/
pre_dominant/borrow); edges carry functional affinity weights
(dominant→tonic 0.95, pre_dominant→dominant 0.9, ...). Phase 1 walks this
graph for raw melodic material; Phase 2 resolves it onto a diatonic F-minor
soul progression with voice-leading rules.

## Two-Phase Pipeline
- **Phase 1** (`MIDI/078-soul-voiceleading-phase1.mid`): raw single-voice
  graph-walk draft. Pitches = chromatic wander around each graph node's chord
  tones — unquantized, no harmonic context, no bass, no drums. Audibly a
  floating "function-hopping" line: it lands near tonic/dominant regions but
  the register drifts and chords never lock underneath.
- **Phase 2** (`MIDI/078-soul-voiceleading.mid`): rules post-process. Every
  phase-1 event quantized to the nearest chord tone of the bar's F-minor soul
  progression (i iv V III | i iv V VI ...), voice-leading leap cap <= 9
  semitones, `rules.voice_leading.VoiceLeadingRules` check (hidden fifths on
  lead: 0 flags), then a full soul texture:
  Lead (Tenor Sax 65), Horn stabs on 2&/4&, Rhodes 3rd+7th comp, Violin
  counterline (instrument library, sweet spot G4-B5), octave-pulse electric
  bass, backbeat drums (kick 1&3, snare 2&4, hat 8ths, claps+ride in choruses).

## Voices
Lead(65), Horns(61), Rhodes(4), Violin(40), Bass(33), Drums(ch9)

## Artifacts
- `MIDI/078-soul-voiceleading.mid` + `MIDI/078-soul-voiceleading-phase1.mid` (both with provenance sidecars)
- `Audio/078-soul-voiceleading.ogg` / `.wav` + phase1 renders
- `Analysis/grid_visualization.txt`, `Analysis/summary.json`
- `compose.py` (engine-only, preflight-clean)

## Verification
- Phase1 validate: OK · Phase2 validate: OK
- Silence check: 4.8% silence (mix), 11.5% (phase1) — no silent-WAV trap
- Preflight: exit 0 (compliant, no raw-MIDI)
- All artifacts > 40 bytes
