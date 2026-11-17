# SP146-feedback-loop-fx-076-reggae-lsystem

Production pass (2026-11-17): **SP-146 Feedback-Loop Echo + Codec Loss**
(RC-20 V2 Echo/Loss-style) applied as an absolute layer to
`076-reggae-lsystem` (Reggae one-drop, A aeolian, 96 BPM).

- **Carrier**: FluidSynth dry render (FluidR3_GM.sf2) of a **reworked** MIDI —
  the PRE-FLIGHT harmony gate failed on the source (115 out-of-chord notes from
  section-level chord quantization), so Lead + Skank were re-quantized to the
  per-bar chord (i–bVII–i–bVI). Re-audit: 0 off-grid / 0 out-of-scale /
  0 out-of-chord, zero-drift clean.
- **Effect**: eighth-note dub echo (312.5 ms @ 96 BPM) with wobble, tanh drive,
  tone band-limiting, all-pass smear and in-loop codec loss, feedback 0.55,
  mix 0.35.
- **Master**: −14.0 LUFS (reggae target), −1.0 dBTP true peak.

Artifacts: `Audio/*.wav/.ogg`, `MIDI/076-reggae-lsystem-reworked.mid`,
`REPORT.md` (primary record), `Analysis/render_stats.json`, `provenance.json`.

Verification: FFT dominant-pc hit 0.9587, harmonic energy 0.5824, silence 7.27%
(tail only).
