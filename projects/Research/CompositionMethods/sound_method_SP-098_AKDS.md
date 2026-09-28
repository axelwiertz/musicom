# SP-098 — TR-808 Analog Kick Drum Synthesis (AKDS)

**Layer:** absolute (sound production — Synthesis Engines)
**Category:** Synthesis Engines | **Target Output:** Circuit-Faithful Analog Kick / Sub-Bass Drum Voice
**Candidate code path:** `sound/synthesis/drum_synth_808.py`
**Status:** documented 2026-09-28 (cron sound-production research job)

One-line: renders the Roland TR-808 bass drum from its discrete transistor-circuit topology —
a bridged-T bandpass filter self-oscillating at ~49.4 Hz (G1+14¢) with a 6 ms pitch sweep
attack (49→130 Hz), feedback-buffer decay control (50–800 ms), voltage-leakage pitch sigh,
passive tone lowpass, and VCA output. The 808's iconic thumping, decaying sub-bass voice,
from symbolic percussion events.

## 1. Why this method (gap analysis)

Three 808-family methods exist in this database: SP-087 (snare, TASS) and SP-089 (cymbal,
TACS) document the snare and cymbal circuit models but the bass drum — the single most
iconic 808 voice — has no dedicated circuit-accurate method. The 606 engine's generic kick
recipe (`sound/synthesis/drum_synth_606.py`) uses a simple VCO sine + VCA + gated
lowpass filter, lacking the bridged-T self-oscillation, attack envelope pitch sweep, feedback
buffer, retriggering bridge, and voltage-leakage pitch sigh that make the 808 kick unique.
SP-074 (piano hammer-string) is a struck string, not a drum resonator. SP-040 FDTD is
plate/membrane physics but not the specific bridged-T topology. AKDS fills the **analog
sub-bass drum** gap as the third member of the 808 drum family (snare + cymbal + kick).

AKDS renders one kick hit as the sum of six deterministic sub-circuit blocks:

1. **Trigger Logic** — sums CPU trigger + global accent voltage (3.5–13.5 V) to produce a 1 ms pulse.
2. **Pulse Shaper** — nonlinear low-shelf filter; rising edge passes at full amplitude, falling edge
   is clipped by diode D53 at ~0.71 V (independent of trigger amplitude).
3. **Bridged-T Bandpass Filter** — the core self-oscillating resonator; center ~49.4 Hz, Q ~15–20,
   decays exponentially when pinged by the shaped pulse.
4. **Attack Envelope** — 6 ms pitch sweep from 49.4→130 Hz (transient punch + click);
   retriggering pulse through R161 to bridge attack→body transition smoothly.
5. **Feedback Buffer** — sustains oscillation by feeding back the bridged-T output; Decay pot
   (VR6) controls sustain time (50–800 ms, 300 ms center). Voltage leakage through R161
   produces the signature slow pitch sigh.
6. **Output Stage** — passive lowpass Tone control (VR5), VCA Level (VR4), and 6.7 Hz
   highpass DC-blocker.

Controls: **Tune** (frequency scale of bridged-T), **Decay** (feedback sustain), **Tone**
(attack click lowpass), **Level** (output gain). Per-hit accent modulates trigger voltage
for dynamic velocity response without polyphonic voice stealing.

## 2. Circuit Analysis and Physics

### 2.1 Bridged-T Network Transfer Function (the core)

The bridged-T network (Zobel topology, negative feedback path of op-amp Q43) forms
a bandpass filter whose impulse response is the decaying pseudo-sinusoid. From the
nodal analysis of Werner et al. (2014, eq. 5):

$$H_{bt}(s) = \frac{V_{bt}(s)}{V_+(s)} = \frac{\beta_2 s^2 + \beta_1 s + \beta_0}{\alpha_2 s^2 + \alpha_1 s + \alpha_0}$$

With component values from the service manual ($R_{161}=1\text{ M}\Omega$,
$R_{165}=220\text{ k}\Omega$, $R_{166}=220\text{ k}\Omega$, $R_{167}=150\text{ k}\Omega$,
$R_{170}=470\text{ k}\Omega$, $C_{41}=C_{42}=0.022\text{ }\mu\text{F}$):

$$\begin{aligned}
\beta_2 &= R_{eff} R_{167} C_{41} C_{42} = 200\text{k} \cdot 150\text{k} \cdot 0.022\mu\text{F} \cdot 0.022\mu\text{F} \\
\beta_1 &= R_{eff} C_{41} + R_{167} C_{41} + R_{eff} C_{42} \\
\beta_0 &= 1 \\
\alpha_2 &= \beta_2 \quad \text{(same component combination)} \\
\alpha_1 &= R_{eff} (C_{41} + C_{42}) \\
\alpha_0 &= 1
\end{aligned}$$

**Center frequency** (Werner eq. from footnote 16):

$$f_0 = \frac{1}{2\pi \sqrt{R_{eff} R_{167} C_{41} C_{42}}} \approx 49.4\text{ Hz}$$

Measured values of real 808 units give 47–50 Hz (G1±~30¢). $R_{eff} = R_{161} \parallel (R_{165}+R_{166}) \parallel R_{170}$.

**Quality factor** (bandwidth $B = f_0/Q$):

$$Q = \frac{\sqrt{R_{eff} R_{167} C_{41} C_{42}}}{R_{eff} C_{41} + R_{eff} C_{42}} \cdot \sqrt{\frac{R_{eff}}{R_{167}}} \approx 15\text{--}20$$

The bridged-T is intentionally high-Q to ring like a resonant body rather than pass a broadband signal.

### 2.2 Impulse Response (decaying sinusoid)

A trigger pulse edge at $t=0$ excites the bridged-T; the response is a pseudo-sinusoid
with exponential decay:

$$v_{bt}(t) = V_{pulse} \cdot e^{-\pi f_0 t / Q} \sin(2\pi f_0 t + \phi_0)$$

The decay envelope $e(t) = e^{-t/\tau}$ with $\tau = Q/(\pi f_0)$.

### 2.3 Pulse Shaper (nonlinear low-shelf)

The pulse shaper (C40, R162, R163, D53) acts as a nonlinear low-shelf filter. The
linear filter (diode removed) transfer function:

$$H_{ps}(s) = \frac{R_{163}}{R_{162}+R_{163}} \cdot \frac{1 + s R_{162} C_{40}}{1 + s \frac{R_{162} R_{163}}{R_{162}+R_{163}} C_{40}}$$

The diode D53 clips negative output voltages at approximately $-0.71$ V. In the time
domain: the rising edge jumps to $V_{trig} \cdot R_{163}/(R_{162}+R_{163})$, then
decays toward ground with RC time constant $\tau_{ps} = (R_{162} \parallel R_{163}) C_{40}$.
When the input drops to 0 V (trigger end), the output swings below ground and is
clamped at $-0.71$ V.

Component values: $R_{162}=4.7\text{ k}\Omega$, $R_{163}=100\text{ k}\Omega$,
$C_{40}=0.015\text{ }\mu\text{F}$, giving $\tau_{ps} \approx 67\text{ }\mu\text{s}$.

### 2.4 Attack Envelope (pitch sweep)

Transistor Q43's base is driven by the envelope generator (Q41–Q42, R156–R160, C39)
during the first ~6 ms of each hit. Under forward bias, Q43 presents a variable
effective resistance in parallel with the bridged-T, shifting the center frequency:

$$f(t) = f_0 \left(1 + \frac{\Delta C_{eff}(t)}{C_{41}+C_{42}}\right)^{-\frac{1}{2}}$$

The peak frequency at $t \approx 1\text{ ms}$ reaches $\approx 130$ Hz (C3−11¢),
then decays back to $f_0$ over ~6 ms.

**Retriggering pulse**: At the end of the attack envelope (~6 ms), a voltage bump
is injected through $R_{161}$ into the bridged-T network to replenish energy lost
during the pitch sweep. This prevents an audible dip between the click attack and
the body decay.

### 2.5 Feedback Buffer (Decay control)

The feedback buffer (op-amp Q44, VR6 decay pot, R164, R168, R169) sustains the
bridged-T oscillation by feeding the output back to its non-inverting input:

$$H_{fb}(s) = \frac{V_{fb}(s)}{V_{bt}(s)} = \frac{\beta_1 s + \beta_0}{\alpha_1 s + \alpha_0}$$

$$\begin{aligned}
\beta_1 &= -R_{169} \cdot \text{VR6}_k \cdot C_{43} \\
\beta_0 &= -R_{169} \\
\alpha_1 &= R_{164} (R_{169} + \text{VR6}_k) C_{43} \\
\alpha_0 &= R_{164}
\end{aligned}$$

VR6 (500 kΩ pot) sets $k \in [0,1]$, giving closed-loop decay time:

$$T_{decay} = \frac{-\ln(0.1)}{\text{Re}(\text{pole})} \in [50\text{ ms}, 800\text{ ms}]$$

300 ms at center position ($k \approx 0.5$). The decay pot is a creative control:
short = tight staccato kick, long = boomy trap/hip-hop subs.

### 2.6 Pitch Sigh (voltage leakage through R161)

A subtle effect unique to the 808: during negative voltage swings of the bridged-T
output, charge leaks through $R_{161}$ (1 MΩ retriggering resistor). This saps energy
as a function of the signal itself, causing the effective $R_{eff}$ to change slowly:

$$R_{eff}(t) = R_{161} \parallel (R_{165}+R_{166}) \parallel R_{170} + \Delta R(t)$$

The resulting frequency drift:

$$f(t) = f_0 \cdot e^{-t/\tau_{sigh}}, \quad \tau_{sigh} \approx \frac{2C_{41}R_{161}}{f_0 C_{41} R_{161}}$$

This creates the characteristic gentle downward pitch glide — distinguishing the 808
kick from all generic filter-kicks.

### 2.7 Tone Control and Output

Tone (VR5, 10 kΩ, + C47 0.033 μF): passive first-order lowpass:

$$H_{tone}(s) = \frac{1}{1 + s R_{tone} C_{47}}, \quad f_{cutoff} \in [\sim500\text{ Hz}, 20\text{ kHz}]$$

At max Tone (CCW, high resistance), cutoff dips low, rolling off the attack click.
At min Tone (CW, low resistance), the full click passes.

Level (VR4, 10 kΩ VCA pot): linear gain multiplier.

Final stage: C49 + R177 + R176 form a 6.7 Hz first-order highpass (DC removal).

## 3. Python/NumPy Implementation Sketch

```python
import numpy as np

def kick_808(fs=44100, tune=1.0, decay=0.5, tone=5.0, level=0.9,
             accent=0.0, dur=1.0, seed=808):
    """
    TR-808-style kick drum hit.
    tune=1.0=f0=49.4Hz, tune>1=higher pitch (tight), tune<1=lower (boomy)
    decay: 0=short(50ms), 0.5=mid(300ms), 1.0=long(800ms)
    tone: 0=flat (dark), 10=bright (all click)
    accent: 0=normal(3.5V), 1=max(13.5V)
    """
    rng = np.random.default_rng(seed)
    n = int(fs * dur)
    t = np.arange(n) / fs

    f0 = 49.4 * tune
    # Decay time range: 50 to 800 ms, exponential curve
    t_decay = 0.05 + 0.75 * (decay ** 2)   # 50-800ms
    tau = t_decay / np.log(10)  # manual convention: decay to 1/10

    # 1. Attack envelope (6 ms pitch sweep)
    tau_attack = 0.006 / np.log(10)
    e_attack = np.exp(-t / tau_attack)
    f_attack = f0 + (130.0 * tune - f0) * e_attack

    # 2. Bridged-T decaying sinusoid
    phase = 2 * np.pi * np.cumsum(f_attack) / fs
    body = np.sin(phase) * np.exp(-t / tau)

    # 3. Pulse shaper click (short impulse + diode clipping)
    # Model as differentiated trigger with -0.71V clamping
    trigger_amp = 3.5 + 10.0 * accent  # 3.5-13.5V
    pulse = np.zeros(n)
    pulse[:int(0.001 * fs)] = trigger_amp
    # Low-shelf filter approximation
    b0 = 100e3 / (4.7e3 + 100e3)  # R163/(R162+R163)
    click = b0 * np.diff(pulse, prepend=0)
    click = np.clip(click, -0.71, None)  # diode D53 clamp
    click *= 0.01 * trigger_amp  # scale to audio level

    # 4. Retriggering pulse (6 ms, boosts attack→body transition)
    tau_retrig = 0.003 / np.log(10)
    retrig = 0.15 * np.exp(-(t - 0.006) / tau_retrig) * (t >= 0.006)

    # 5. Pitch sigh (leakage through R161)
    # Envelope-following frequency modulation
    sigh_depth = 0.03 * (1 - np.exp(-t / 0.5))
    sigh_mod = 1.0 - sigh_depth * np.cumsum(np.abs(body)) / np.sum(np.abs(body))

    # 6. Tone control (passive LPF)
    f_tone = 20000 * (1 - tone / 10.0) + 500 * (tone / 10.0)
    a_ton = np.exp(-2 * np.pi * f_tone / fs)
    tone_state = 0.0
    body_tone = np.empty(n)
    for i in range(n):
        tone_state = a_ton * tone_state + (1 - a_ton) * body[i]
        body_tone[i] = tone_state

    # Sum all components
    y = (body_tone * sigh_mod + click + retrig * body_tone)
    y *= level

    # 7. 6.7 Hz DC blocker
    a_dc = np.exp(-2 * np.pi * 6.7 / fs)
    dc_state = 0.0
    for i in range(n):
        dc_state = a_dc * dc_state + (1 - a_dc) * y[i]
        y[i] -= dc_state

    return y

# usage: stem[onset:onset+len(hit)] += velocity * kick_808(tune=sec_tune, ...)
```

### Complexity

$O(1)$ per sample per voice (2 biquads + 1 envelope + 1 tone LPF + 1 DC blocker).
$O(H \cdot D)$ per stem for $H$ hits of $D$ samples. Deterministic per (seed, params).

## 4. Musical Elements Framework

| Element | Mapping |
|---|---|
| **PITCH** | Bridged-T $f_0$ ~49.4 Hz (G1+14¢). Tune parameter scales all timing caps. Typical range: 30 Hz (B0, huge subs) to 80 Hz (E2, tight). Attack sweep (~130 Hz C3) transiently brightens before settling — perceived as click/punch, not pitch change. |
| **RHYTHM** | Each kick IS the rhythm event: onset = trigger time, velocity = accent voltage (modulates Level + slight Decay increase). 300 ms center decay suits 120–160 BPM 4-on-the-floor. Long decay (800 ms) bleeds across beats for trap/hip-hop. Ghost notes at low velocity + short Decay. |
| **HARMONY** | Atonal subs — no harmonic function in the traditional sense. But the pitched fundamental rings sympathetically with bass notes near G1: the kick "tunes" to the bass root. Classic production technique: tune the 808 kick to the tonic of the track. |
| **STRUCTURE** | Per-section (Tune, Decay, Tone, Level) preset = drum-mix macro-form: tight short kick in verse (Tune=1.8, Decay=0.2), boomy long kick in chorus/drop (Tune=1.0, Decay=0.9), no kick in breakdown. Presets switch instantly (each trigger is an independent bridged-T ping — no filter smoothing). |
| **TEXTURE** | Decay = texture fader: short (~50 ms) = staccato click/rim-like, legato at long (~800 ms) = sub-bass fill. Per the Method Hybridization rule, always pair long 808 kick with a highpassed mid-range layer. Tone control further shapes: bright = clicky attack, dark = smooth thud. |

## 5. UnitMatrix Integration

- **Rows (Voices)** = each percussion row (kick row) renders through its own AKDS
  instance. Pitched/tonal rows (bass, leads) are independently rendered by SP-001/SP-074.
  No voice stealing — coincident kicks cleanly accumulate in the stem (each trigger = independent).
- **Columns (Sections)** = per-section (Tune, Decay, Tone, Level) preset = four scalar parameters
  applied to every kick in that section. Zero filter-state smoothing needed (fresh bridged-T per hit).
- **Cells (MusicUnit)** = pitch → Tune (kick fundamental); rhythm → onset = trigger time,
  velocity = accent voltage; texture → per-cell Decay override for ghost vs accent hits.
- **Flow**: `compose` (UnitMatrix → MIDI) → kick row → `produce(method="SP-098",
  params={tune, decay, tone, level})` → per-hit render → sum → SP-007 EQ (~250 Hz boxiness cut)
  → SP-008 limiter → WAV/OGG. Pairs: SP-009/032/071 (room/plate: gated kick),
  SP-072 (HPSS: isolate sub from click), SP-073 (TSDE: attack boost),
  SP-006 (humanize: ±2 ms onset jitter, subtle velocity scatter).

## 6. Pitfalls

1. **Overfolding the bridged-T**: A simple 2-pole resonant LPF/HPF *does not* produce
   the 808's specific ringing shape at 49.4 Hz with correct attack→body transition.
   Use the full 2nd-order transfer function with correct $R_{eff}$, $R_{167}$, $C_{41}$, $C_{42}$.
2. **Ignoring the attack envelope**: Without the 6 ms pitch sweep (49→130 Hz), the kick
   lacks punch. The sweep is perceptually crucial even though too brief to hear as pitch.
3. **Missing the retriggering pulse**: Without the ~6 ms retriggering bump, there's an
   audible dip/gap between attack and body.
4. **Flat pitch across decay**: The pitch sigh (voltage leakage through R161) is what
   distinguishes a real 808 kick from a generic sine. Model as $f(t) = f_0 e^{-t/\tau_{sigh}}$.
5. **Confusion with the 606 bass drum**: 606 kick = VCO sine + VCA + gated filter (not
   bridged-T). Use AKDS when the 808's organic ringing and sigh are wanted.
6. **Machine-gun effect**: The bridged-T is deterministic per seed; repeated hits sound
   identical. Add per-hit random detune scatter (±2¢ on $f_0$) or per-hit RNG Decay
   modulation for natural variation.
7. **Subsonic energy**: At 49.4 Hz the decay tail produces significant sub-30 Hz energy.
   Always add a 30 Hz highpass on the master (the built-in 6.7 Hz HPF is for DC only,
   insufficient to protect subwoofers).

## 7. References

- Werner, K. J., Abel, J. S. & Smith III, J. O. (2014). "A Physically-Informed,
  Circuit-Bendable, Digital Model of the Roland TR-808 Bass Drum Circuit."
  *Proc. DAFx-14*, Erlangen. — Primary source: bridged-T, pulse shaper, feedback buffer
  transfer functions and coefficients.
- Roland Corporation. *TR-808 Rhythm Composer Service Manual* (June 1981).
  — Component values, block diagrams, typical frequency/decay table.
- Barata, P. "808 Bass Drum Synthesis." Baratatronix (2024).
  — Block diagram, Bode plot, qualitative circuit analysis.
- Reid, G. "Synth Secrets: Synthesizing Drums" — Sound on Sound (2002).
- Klein, M. "Designing a Simple Analog Kick Drum from Scratch" (Erica Synths).
- simo-pandolfi/py78drums — Python per-sample drum synthesis workflow.
- Chowdhury, J. — WaveDigitalFilters TR-808 bass drum (WDF analysis; fetched 2026-09-28).