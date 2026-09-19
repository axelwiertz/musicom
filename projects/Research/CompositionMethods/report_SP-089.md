# Research Report: Method SP-089 — TR-808 Analog Cymbal Physical-Circuit Synthesis (TACS)

**Date:** 2026-09-19  
**Agent:** Sound Production Research Agent  
**Method ID:** SP-089  
**Method Name:** TR-808 Analog Cymbal Physical-Circuit Synthesis (TACS)  
**Layer:** `absolute` (Sound Production — Synthesis Engines)  

---

## 1. Executive Summary & One-Line Description

**TR-808 Analog Cymbal Physical-Circuit Synthesis (TACS)** synthesizes the Roland TR-808 crash and ride cymbal voices from its original 1980 analog hardware circuit schematic: an astable multivibrator bank of six CMOS Schmitt-trigger square-wave oscillators summed into twin high-order active bandpass filters (~3.4 kHz and ~7.1 kHz), gated by three independent swing-type non-linear transistor VCAs driven by multi-stage RC envelope generators, shaped by Sallen-Key highpass filters and an interconnected passive tone stage, and equalized by an active differentiator buffer (+6 dB/octave). It yields an authentic, responsive metallic sheen with continuous decay/tone control and zero sampled audio.

---

## 2. Summary Table Entry

Added to `/opt/data/projects/Research/CompositionMethods/methods_db.md` (top summary table, line 186):

```markdown
| **SP-089** | TR-808 Analog Cymbal Physical-Circuit Synthesis (TACS) | **Synthesis Engines** | Circuit-Faithful Analog Metallic Cymbal / Multi-Band Percussion Timbre | Synthesizes the TR-808 cymbal voice via its circuit topology: six Schmitt-trigger square-wave oscillators summed into dual active bandpass filters (~3.4 kHz and ~7.1 kHz), gated by three swing-type non-linear transistor VCAs with RC envelope generators, shaped by Sallen-Key highpass filters and an interconnected passive tone stage with a $+6\text{ dB/oct}$ differentiator buffer. Deterministic metallic sheen without sampling; $\mathcal{O}(1)$ per sample. Candidate: `sound/synthesis/drum_synth_808.py`. |
```

---

## 3. Database Modifications & Line Counts

- **File:** `/opt/data/projects/Research/CompositionMethods/methods_db.md`
- **Line count before:** 18,946 lines
- **Line count after:** 19,145 lines
- **Delta:** +199 lines (1 summary table row + 198 detailed section lines)

---

## 4. Artifact Paths

- **Detailed DB Append:** `/opt/data/projects/Research/CompositionMethods/methods_db.md` (appended to end under Sound Production Methods Framework)
- **Standalone Specification:** `/opt/data/projects/Research/CompositionMethods/sound_method_SP-089_TACS.md`
- **Report File:** `/opt/data/projects/Research/CompositionMethods/report_SP-089.md`
- **Candidate Code Path:** `sound/synthesis/drum_synth_808.py` (or `sound/synthesis/tr808_cymbal.py`), plugged into `workflows.musicom_workflow.produce(method="SP-089")`.

---

## 5. Technical Mechanics (Summary)

1. **CMOS Schmitt Inverter Bank (HD14584):** Six astable multivibrators produce inharmonic square waves ($f_1=205.3, f_2=369.6, f_3=304.4, f_4=522.7, f_5=800.0, f_6=540.0\text{ Hz}$) with duty cycle $D \approx 47.98\%$.
2. **Dual Active Bandpass Pre-Filters:** 3rd-order active bridged-T op-amp bandpass filters peak at $f_{c1} \approx 3440\text{ Hz}$ and $f_{c2} \approx 7100\text{ Hz}$, accentuating upper inharmonic intermodulation products.
3. **Attack Smoother & Envelopes:** 1 ms CPU trigger smoothed with $\tau \approx 102.4\ \mu\text{s}$ lowpass filter; multi-stage RC discharge yields variable decay (150 ms to 2.25 s) and punch clicks.
4. **Swing-Type VCAs:** Non-linear common-emitter transistor stage where the collector rail is modulated directly by envelope voltage $V_{\mathrm{env}}(t)$, introducing soft tanh saturation and sharp diode gating.
5. **Highpass & Tone Stage:** Sallen-Key filters (5.5 kHz, 8.2 kHz, 10.5 kHz resonant) feed a passive tone-crossfading network and a $+6\text{ dB/oct}$ differentiator op-amp output buffer.

---

## 6. Musical Elements Framework

- **PITCH:** Inharmonic metallic cluster. Dense, non-octave partial intervals provide realistic bronze shimmer.
- **RHYTHM:** Point-process impulsive triggers with sub-millisecond attack response; continuous decay range.
- **HARMONY:** Broad-spectrum metallic overtone cluster; non-functional harmonic coloration consonant over any progression.
- **STRUCTURE:** Serves as macro-structural punctuation (crash hits at section downbeats) or groove driving force (ride pulses).
- **TEXTURE:** Airy, bright high-frequency sheen (3.5 kHz to 12 kHz) avoiding low-mid mix masking.

---

## 7. Quirks, Pitfalls & Mitigations

- **Bilinear Nyquist Cramping:** High filter poles (7.1 kHz to 10.5 kHz) suffer warping at 44.1 kHz. Mitigated via 2× internal oversampling (88.2 kHz) and tangent pre-warping.
- **VCA Idle Bleed:** Linear gain causes square-wave hum. Mitigated via hard diode cutoff threshold ($V_{\mathrm{on}} \approx 0.59\text{ V}$).
- **Aliasing:** Square-wave step transitions mitigated via oversampling and soft-clipping saturation.
- **Phase Variance:** Free-running randomized initial phases prevent identical, robotic digital transients across successive hits.

---

## 8. Next Free SP ID

**SP-090** (highest documented SP method is now SP-089; summary table and file scans confirm SP-090 is completely free).
