# Linear Arithmetic Synthesis (LASS) — SP-112

## Layer
**absolute** — Sound Production (Synthesis Engines)
Code path: `sound/synthesis/la_synthesis.py`

## Overview
Linear Arithmetic (LA) Synthesis is the Roland D-50 hybrid (March 1987): a note is assembled **along a timeline** from a one-shot PCM attack transient (the perceptual fingerprint of an instrument: hammer, pluck, breath "chiff", mallet, voice onset) crossfaded into a subtractively-synthesized sustain body (saw/PWM through a resonant lowpass). The "arithmetic" is the timeline assembly — addition of partials, subtraction by filtering, optional ring-modulation sum/difference — explicitly *not* additive synthesis.

Position in the SP table: it fills the hybrid gap between full sampling (SP-002 VST3, SP-044 concatenative — real audio, weak reshape) and pure subtractive synthesis (SP-029 — full sustain control, weak attack). The D-50's insight: **memory goes to the transient, synthesis goes to the tail.** Two partials = a tone; two tones = a patch; partials are either PCM or synth sources, each with TVA (time-variant amplifier) + TVF (time-variant filter) envelopes. The LA32 chip (MT-32, 1989) is the canonical hardware implementation.

## The LA Architecture

```
PCM partial (P)  ──► interp/loop ──► E_P (TVA) ──┐
                                                ├─ balance(b) ─► voice out
synth partial (S)─► osc (saw/PWM) ► TVF LPF ─► E_S (TVA) ──┘
```

- **PCM partial**: one-shot attack transient OR looped single-cycle embellishment waveform (synthetic additive-derived waves, inharmonic cycles). Playback rate $r = f_0/f_\text{sample}$ with fractional interpolation.
- **Synth partial**: phase-accumulator saw or variable-duty pulse (PWM), PolyBLEP-corrected (SP-029/SP-110 convention), through a resonant lowpass (ZDF SVF, SP-020).
- **Balance** $b(t)\in[0,1]$: equal-power crossfade between P and S — the "timeline" control. Static, enveloped, or LFO-driven.
- **TVA/TVF envelopes**: D-50-style multi-segment (T1..T4 / L1..L4), linear-in-dB for TVA, linear-in-Hz for TVF.
- **Pitch envelope** $\Pi(n)$: shared by BOTH partials (they must stay in tune with each other).
- Per-voice extras: key tracking on TVF, partial detune, up to 3 LFOs (vibrato, PWM, balance tremolo), optional chorus/reverb post-chain.

## Mathematics

### Balance mix (equal-power)
$$y(n) = g_P(b(n))\,E_P(n)\,x_P(n) + g_S(b(n))\,E_S(n)\,x_S(n)$$
$$g_P(b) = \cos\!\big(\tfrac{\pi}{2} b\big),\qquad g_S(b) = \sin\!\big(\tfrac{\pi}{2} b\big)$$
(The linear crossfade dips ~3 dB mid-mix for uncorrelated signals; the cosine/sine law is constant-power.)

### PCM read position
$$p_{n+1} = p_n + r(n),\qquad r(n) = \frac{f_0\,\Pi(n)}{f_\text{sample}}$$
One-shot: play to table end, then TVA closes (or balance hands to S). Looped: wrap $p_n$ at loop points. Interpolation: linear (min) / cubic (recommended); mipmap (SP-041) when $r>2$.

### Synth oscillator
$$\phi_{n+1} = \big(\phi_n + 2\pi f_0\,\Pi(n)/f_s\big) \bmod 2\pi$$
$$\text{saw: } s(\phi)=\tfrac{2\phi}{\pi}-1,\qquad \text{pulse: } p(\phi)=\begin{cases}+1 & \phi<2\pi D\\ -1 & \text{else}\end{cases}$$
+ PolyBLEP correction at the discontinuities.

### TVF cutoff trajectory (key tracking)
$$f_c(n) = f_{c0} + (f_{c1}-f_{c0})\,E_{TVF}(n) + k_t\,(f_0 - f_\text{ref})$$
$f_c$ one-pole-smoothed ($\tau\approx 1$–5 ms) to avoid zipper clicks. Resonant lowpass: 2nd-order ZDF SVF (SP-020) or one-pole-with-resonance.

### TVA peak (velocity)
$$L_\text{peak} = L_0\,(\text{vel}/127)^{\gamma},\qquad \gamma\approx 0.5\text{–}1.0$$
Velocity also scales TVF amount (hard hits open the filter + emphasize the transient).

### Cost
$\mathcal{O}(1)$ per sample per partial → $\mathcal{O}(2)$ per voice (interp + osc + filter + 2 envelopes + balance). ~3–4× a bare SP-110 PWM voice; real-time for dozens of voices at 48 kHz.

## Musicom Pipeline Implementation (Python/NumPy)

```python
import numpy as np

def polyblep_naive(phase, dt):
    """PolyBLEP correction for a discontinuity at phase=0 (dt = 2pi f0/fs)."""
    if phase < dt:
        t = phase / dt
        return t + t - t * t - 1.0
    if phase > 2.0 * np.pi - dt:
        t = (phase - 2.0 * np.pi) / dt
        return t * t + t + t + 1.0
    return 0.0

def svf_lowpass(x, fc, q, sr, state):
    """One-pole-resonance lowpass (cheap stand-in for SP-020 ZDF SVF)."""
    out = np.empty_like(x)
    lp, bp = state
    for i in range(len(x)):
        f = 2.0 * np.sin(np.pi * fc[i] / sr)
        hp = x[i] - lp - q * bp
        bp += f * hp
        lp += f * bp
        out[i] = lp
    return out, (lp, bp)

def segment_env(n_attack, n_release, peak, sustain, sr,
                a=0.01, r=0.3, curve="db"):
    """4-segment TVA-style env: attack(lin-in-dB)->sustain->release."""
    n = n_attack + 1 + n_release
    env = np.zeros(n)
    # attack: exponential toward peak (linear in dB)
    for i in range(n_attack):
        frac = i / max(1, n_attack - 1)
        env[i] = peak * (sustain / peak) ** (1 - frac) if curve == "db" \
                 else peak * frac
    env[n_attack] = sustain
    for j in range(n_release):
        frac = (j + 1) / n_release
        env[n_attack + 1 + j] = sustain * (0.0 + 1e-4) ** frac
    return env

def render_la_note(f0, dur, sr=48000, pcm=None, pcm_rate=1.0,
                   wave="saw", duty=0.5, cutoff0=800.0, cutoff1=4000.0,
                   reso=0.7, keytrack=0.3, balance_style="bloom",
                   b_attack=0.05, vel=100, seed=0, loop=None):
    """Render one note-length LA voice block (PCM attack + synth sustain)."""
    n = int(dur * sr)
    dt = 2.0 * np.pi * f0 / sr
    phi = 0.0
    pos = 0.0 if pcm is not None else None
    lp, bp = 0.0, 0.0

    out = np.zeros(n)
    # balance trajectory: "bloom" = 0 -> 1 over b_attack s, "stab" = 0, "pad" = 1
    if balance_style == "bloom":
        nb = max(1, int(b_attack * sr))
        b = np.minimum(np.arange(n) / nb, 1.0)
    elif balance_style == "stab":
        b = np.zeros(n)
    else:  # pad
        b = np.ones(n)

    gp = np.cos(0.5 * np.pi * b)
    gs = np.sin(0.5 * np.pi * b)

    # envelopes
    na = max(1, int(0.01 * sr)); nr = max(1, int(0.3 * sr))
    ep = segment_env(na, nr, 1.0, 0.2, sr)       # PCM TVA (fast close)
    es = segment_env(na, nr, 1.0, 0.6, sr)       # synth TVA (longer sustain)
    if pcm is None or len(pcm) == 0:
        gp[:] = 0.0  # no PCM table -> pure synth (pad mode)

    fc = np.empty(n)
    etvf = np.linspace(0.0, 1.0, n)  # TVF: sweep cutoff to cutoff1
    kt = keytrack * (f0 - 261.6256)   # key tracking (C4 ref)
    fc = cutoff0 + (cutoff1 - cutoff0) * etvf + kt
    fc = np.maximum(fc, 20.0)

    xp = np.zeros(n)
    if pcm is not None and len(pcm) > 0:
        for i in range(n):
            idx = int(pos)
            frac = pos - idx
            if idx + 1 < len(pcm):
                xp[i] = pcm[idx] * (1 - frac) + pcm[idx + 1] * frac
            else:
                if loop is not None:          # looped embellishment
                    pos = loop[0] + (pos - loop[0]) % (loop[1] - loop[0])
                    idx = int(pos); frac = pos - idx
                    xp[i] = pcm[idx] * (1 - frac) + pcm[idx + 1] * frac
                else:                          # one-shot: end of table
                    break
            pos += dt / (2.0 * np.pi) * (f0 / 44100.0) * pcm_rate
    xs = np.empty(n)
    for i in range(n):
        ph = phi
        if wave == "saw":
            xs[i] = 2.0 * ph / (2.0 * np.pi) - 1.0
            xs[i] -= polyblep_naive(ph % (2.0 * np.pi), dt)
        else:  # pulse
            xs[i] = 1.0 if (ph % (2.0 * np.pi)) < 2.0 * np.pi * duty else -1.0
            xs[i] += polyblep_naive((ph % (2.0 * np.pi)), dt)       # +edge
            xs[i] -= polyblep_naive((ph % (2.0 * np.pi)) + np.pi, dt)  # -edge
        phi += dt
        if phi > 2.0 * np.pi:
            phi -= 2.0 * np.pi
    xs, (lp, bp) = svf_lowpass(xs, fc, reso, sr, (lp, bp))

    lv = (vel / 127.0) ** 0.7
    y = gp * ep * xp * lv + gs * es * xs * lv
    y -= np.mean(y[:max(1, int(0.01 * sr))])   # DC block
    return np.tanh(y * 1.2).astype(np.float32)  # safety soft clip
```

For polyphony, each UnitMatrix voice calls `render_la_note` per cell with its own partial pair, preset, and section parameter cluster $\theta_s$.

### Preset atlas (D-50 archetypes)

```python
PRESETS = {
    "pluck":  dict(wave="saw", cutoff0=3000, cutoff1=900, reso=0.3, balance_style="bloom", b_attack=0.08),
    "stab":   dict(wave="saw", cutoff0=2200, cutoff1=2200, reso=0.5, balance_style="stab"),
    "pad":    dict(wave="pulse", duty=0.5, cutoff0=900, cutoff1=3600, reso=0.2, balance_style="pad"),
    "breath": dict(wave="pulse", duty=0.25, cutoff0=500, cutoff1=1500, reso=0.4, balance_style="bloom", b_attack=0.25),
    "fantasia": dict(wave="saw", cutoff0=1200, cutoff1=5200, reso=0.35, balance_style="bloom", b_attack=0.15),
}
```

## Musical Elements Framework

### PITCH
One $f_0$ drives both the synth accumulator and the PCM read rate — transient and body are born in tune (the D-50's central trick). Pitch envelope $\Pi(n)$ scoops/chirps both layers together. Key tracking keeps brightness register-consistent. Partial detune ($\pm 3$–8 cents) adds slow beating = ensemble thickness.

### RHYTHM
TVA attack/release IS articulation: 5–20 ms attack + fast release = stab; slow attack + long release = pad. The one-shot transient gives every onset a physical identity (hammer/pick/breath), so rhythmic parts read as performed. The balance envelope is a **within-note gesture** (transient-forward attack blooming into body) — micro-rhythmic phrasing inside each held note. Velocity → peak level + filter opening = natural accent hierarchy.

### HARMONY
Per-voice LA tones sum at chord frequencies. The classic "Fantasia" stack: PCM partial carries a pitch-specific transient (plucked 5th), synth partials carry the sustained chord; per-voice detune choruses the stack. Looped embellishment partials add inharmonic cycles (SP-063 ring-mod / SP-017 metallic character) *under* consonant bodies — controlled inharmonicity in a harmonic context.

### STRUCTURE
Macro-form = per-section schedule over (balance style, $f_{c1}$, key-track, duty, embellishment on/off): Intro = stabs (balance pinned PCM); Verse = hybrid bloom; Chorus = pads + wide filter + embellishment; Bridge = dark narrow cutoff; Outro = stabs again. The balance axis alone is a tension arc: transient-forward = percussive/tense, body-forward = warm/resolved.

### TEXTURE
Texture = balance position $b$: $b\to0$ pointillistic/plucked, $b\to1$ sustained/string, in-between layered hybrid. Embellishment loop = second stratum (breath/shimmer). Detune + SP-059 chorus = ensemble texture; per-voice independent $b$ trajectories = stratified textural counterpoint.

## UnitMatrix Integration

- **Voices** = rows: one LA tone per voice (PCM partial id + loop points, synth wave/duty, TVA/TVF shapes, balance style, detune, key-track, seedable LFO phase).
- **Sections** = columns: parameter cluster $\theta_s$ = ($f_{c1}$, $k_t$, balance style, duty target, embellishment id/level, TVA shape). Transitions interpolate $\theta$ over 8–64 samples.
- **Cells** = `MusicUnit`s: pitch → $f_0$; velocity → $L_\text{peak}$ + TVF amount; duration → TVA release; articulation → balance style. Per-cell block render into the voice buffer; zero-drift invariant untouched (MIDI events unchanged; audio buffers padded to `section_len` exactly as SP-029/SP-110).
- **Post-chain**: SP-009/SP-032 reverb (space), SP-007 M/S EQ, SP-053 VBAP panning, SP-059 chorus (ensemble).

## Pitfalls

1. **Naive PCM interpolation** aliases/zippers at high $r$; linear min, cubic recommended; mipmap (SP-041) beyond $r>2$.
2. **One-shot truncation click**: TVA must close before table end, or balance hands fully to S first.
3. **Linear balance dip** (~3 dB hole): use the equal-power cosine/sine law.
4. **Aliased sustain body**: PolyBLEP required (SP-029/SP-110 convention) — don't repeat the D-50's era artifacts.
5. **Filter zipper**: one-pole-smooth $f_c$; apply key tracking or bass is disproportionately bright.
6. **Envelope shapes**: linear-in-dB TVA (exponential), linear-in-Hz TVF; linear-in-amplitude sounds lumpy.
7. **Transient/body tuning drift**: shared $\Pi(n)$ for read rate AND oscillator, or the attack detunes audibly from the body.
8. **Per-cell state policy**: per-cell (fresh, seedable) vs voice-continuous LFO/balance phase — either passes the zero-drift gate (it governs MIDI, not audio); document per voice.
9. **Not a sampler**: long notes rest on body + embellishment loop; SP-059 chorus hides loop sameness, SP-009/032 verb glues transient into space.

## References

[1] Wikipedia contributors. "Linear arithmetic synthesis." *Wikipedia, The Free Encyclopedia.* — definition, D-50 (1987), partial/tone/patch hierarchy, LA32 chip, hardware list.
[2] Roland Corporation. *D-50 Owner's Manual* + *D-50 Structure Diagram*. — canonical signal flow (P= PCM partials, S= synth partials), TVA/TVF, balance, pitch envelope, 3 LFOs, chorus/reverb.
[3] Vail, M. (2014). *The Synthesizer: A Comprehensive Guide…*. Oxford University Press, pp. 53–54 — "Trend Setting All-Stars: Linear Arithmetic".
[4] Russ, M. (1987). "Roland D-50 (Parts 1 & 2): Is the Future Linear?" *Sound On Sound*, May/June.
[5] SoundBridge (2023). "Linear Arithmetic (LA) Synthesis." soundbridge.io — attack-transient perception argument, piano-imitation rationale, three-component model.
[6] Munt — *MT-32 Emulator* (open-source LA32 reimplementation) — chip-faithful reference for partial summing, TVA/TVF rate tables, PCM interpolation.
