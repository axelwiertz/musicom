# 205-amapiano-study

**Amapiano** — South African house substyle. Research + engine composition.

| | |
|---|---|
| Style | Amapiano (isiZulu "the pianos") |
| Origin | South African townships (Pretoria/Gauteng), 2010s; global ~2019-2020 |
| Key | A minor (natural + harmonic G# leading tone) |
| Tempo | 112 BPM, 4/4 |
| Form | Intro(4) GrooveA(8) GrooveB(8) Breakdown(4) Climax(8) Outro(4) = 36 bars |
| Progression | i7 - VI7 - iv7 - V7 → Am7 \| Fmaj7 \| Dm7 \| E7 |
| Signature | Log drum (tuned FM bass-percussion), Rhodes 7th chords, rolling shaker |

## Voices

| Voice | GM | Role |
|---|---|---|
| Rhodes | 4 (Electric Piano 1) | soulful 7th-chord harmonic bed |
| LogDrum | 38 (Synth Bass 1) | signature tuned, syncopated bassline |
| Sub | 39 (Synth Bass 2) | deep sustained sub (octave 1) |
| Lead | 108 (Kalimba) | call-and-response (GrooveB) |
| Guitar | 27 (Clean Electric) | solos: sparse hook (Intro) + 8-bar solo (Climax) |
| Drums | ch9 | soft 4-on-floor kick + clap 2&4 + maracas shaker |

## Listen

- `Audio/205-amapiano-study.ogg` (Opus)
- `MIDI/205-amapiano-study.mid` (Phase 2, rules)
- `MIDI/205-amapiano-study-phase1.mid` (Phase 1, raw log-drum draft)

## Rebuild

```bash
/opt/data/micromamba/envs/musicom/bin/python compose.py      # MIDI
/opt/data/micromamba/envs/musicom/bin/python produce.py      # audio production (FX + SFX + mastering)
```

See `REPORT.md` for the full research, method, and verification numbers.
