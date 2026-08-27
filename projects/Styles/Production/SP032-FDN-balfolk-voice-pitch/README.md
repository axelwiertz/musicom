# SP-032 FDN Reverberation — Balfolk Voice Pitch

**Nightly production pass** — random composition × random sound production method.

| | |
|---|---|
| Composition | `Balfolk/005-balfolk-production/audio/VoiceAudio_basic_pitch.mid` |
| Method | **SP-032 — Feedback Delay Network (FDN) Reverberation** |
| Layer | Synthesis Engines / Algorithmic Spatialization |
| Date | 2026-08-16 (cron) |
| Output dir | `/opt/data/projects/Styles/Production/SP032-FDN-balfolk-voice-pitch/` |

## What was done

1. **Dry render** — source MIDI (voice-derived basic-pitch transcription, 321 notes,
   pitch range 43–88, 4/4 @ 120 BPM, ~47.4 s of notes) rendered through FluidSynth
   (TimGM6mb.sf2) → `dry_render.wav`.
2. **SP-032 FDN reverb** — implemented per `methods_db.md` (Jot 1992 architecture):
   - 8 parallel delay lines, **mutually coprime prime lengths** (227–431 samples
     @44.1 kHz) → dense modal tail without comb coloration
   - **Householder unitary feedback matrix** `A = I − (2/N)·1·1ᵀ` → energy-conserving
     lossless core, stability guaranteed
   - Per-line gains `g_i = 10^(−3·M_i/(fs·RT60))` with `RT60 = 4.0 s`,
     `RT60_high = 1.4 s` → frequency-dependent decay (bright attack → warm tail)
   - One-pole lowpass damping per feedback path (crossover 3.2 kHz, `α = e^(−ω)`)
   - **Pre-delay 25 ms + 4 early reflections** (31/47/63/87 ms, gains 0.35/0.25/0.15/0.08)
   - **Stereo**: even delay lines → L, odd → R, width 0.85 via mid/side
   - Wet bus level-matched to dry peak, mixed at 42% wet
3. **Master** — peak-normalized to −1 dBFS.
4. **Export** — WAV + OGG (Opus 48 kbps, Telegram convention) + source MIDI copy.

## Artifacts

| File | Role |
|---|---|
| `VoiceAudio_basic_pitch.mid` | Source composition (copy) |
| `dry_render.wav` | FluidSynth dry render |
| `balfolk_voice_pitch_SP032_FDN.wav` | Processed (dry + FDN) |
| `balfolk_voice_pitch_SP032_FDN.ogg` | Processed, Telegram-ready |
| `provenance.json` | Full provenance + checks |
| `process_fdn.py` | Reproducible pipeline script |

## Verification (real numbers)

| Check | Result |
|---|---|
| FDN tail 1–2 s after last note (wet-only) | peak 0.0053, energy 0.05 |
| Dry level in same window | 0.00015 (36× quieter — tail is FDN's work) |
| Wet tail −40 dB point | 1.56 s after dry end |
| Silence ratio (whole mix) | 3.3 % |
| Peak level | −1.0 dBFS |

## What to listen for

- **Ending**: notes stop ~47.4 s but the room keeps ringing ~3–4 s — the FDN tail
  (this is the whole point of the method; dry render is silent after 48 s).
- **Warmth**: high frequencies decay faster than lows (RT60 1.4 s vs 4.0 s) — natural
  room behavior, no metallic ringing thanks to coprime delay lines.
- **Space**: pre-delay + early reflections separate the voice from the room; stereo
  width comes from the even/odd delay-line split, not from artificial chorusing.
- **Source character**: voice-derived pitch transcription (vocal contour as MIDI) now
  sits in a shared acoustic space.

## Notes / decisions

- Repo `sound/effects/fdn_reverb.py` (Rev Ocean "Tidal" style, short tail) was
  evaluated first; its feedback gain caps the tail at ~1.5 s. The `methods_db.md`
  reference implementation (Jot 1992 with explicit RT60 control) was used instead for
  spec fidelity — it is the method's own published algorithm.
- Level-matched wet bus: standard reverb-send practice; keeps dry/wet ratio musical
  without clipping.
- No custom MIDI authoring — source MIDI copied verbatim; only audio DSP applied.
