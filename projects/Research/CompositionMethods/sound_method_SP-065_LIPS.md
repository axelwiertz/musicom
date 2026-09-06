# Sound Production Method SP-065 — Brass Lip-Reed Physical Modeling (LIPS)

**ID:** SP-065  **Acronym:** LIPS (Lip-Reed Instrument Physical Synthesis)
**Layer:** **absolute** (sound production — renders symbolic note events to raw audio).
**Category:** Synthesis Engines (physical modeling — exciter–resonator).
**Candidate code path:** `sound/synthesis/lip_reed.py` (new module alongside `bowed.py`, `modal.py`, `karplus_strong.py`). Consumes a `MusicUnit`'s `{PITCH, RHYTHM, STRUCTURE}` (one note per onset) and renders a mono/stereo audio buffer per event; sums into the section bus.

---

## 1. Abstract

Brass-instrument timbre (trumpet, trombone, horn, tuba) is produced by a **nonlinear self-oscillating valve** — the player's two lips — coupled to an **acoustic resonator** — a flaring duct (a length of tube terminating in a bell). The sound is not the lips' buzz alone and not the tube's resonance alone: it is the *emergent oscillation* of the two locked together. LIPS models both halves and their coupling directly:

1. **Exciter** — a lip-reed model. A two-mass (or, in the simplest case, single-mass) spring–damping element is driven open/closed by the pressure difference between the mouth (blowing pressure $p_m$) and the mouthpiece cup (pressure $p$). Air flows through the opening by Bernoulli's law; the flow in turn drives the mouthpiece pressure. This loop is *nonlinear* and is the source of all harmonic richness.
2. **Resonator** — a digital waveguide / reflection-function model of the flaring brass tube, terminating in a bell whose reflection/transmission is frequency-dependent (the bell acts as a high-pass radiator: low frequencies reflect back into the bore, highs radiate).

The result is a physically faithful brass voice with correct pitch (set by tube length → resonances), correct attack (the characteristic "brass bite" from the lips' auto-oscillation build-up), correct dynamic-dependent brightness (louder = more harmonics, because blowing pressure controls the nonlinearity strength), and realistic mute/microphone coloration (the bell reflection).

LIPS fills the **brass slot** in the physical-model instrument family: SP-023 = clarinet (single *beating* reed + cylindrical bore), SP-024 = bowed string (stick-slip friction + string), SP-040 = struck plates/bars, SP-011/SP-033/SP-048 = plucked/struck strings. Brass is the last common Western acoustic family without a dedicated SP method.

---

## 2. Physical principle: why brass oscillates

A brass instrument is a **feedback oscillator**:

```
 mouth pressure p_m ──► [lip valve] ──flow u──► [mouthpiece ─ bore ─ bell] ──► radiated sound
                            ▲                                              │
                            └──────────── mouthpiece pressure p ◄──────────┘
```

The lips open when $p_m - p$ exceeds a threshold and close against the mouthpiece when the pressure collapses. The bore returns a delayed, filtered copy of the mouthpiece pressure. When the round-trip phase and the lip's mechanical resonance align, the loop gain exceeds unity and the system self-oscillates — at a frequency the *tube resonances* select (this is why a trumpet plays the notes of its harmonic series: only near a bore resonance does the returning pressure sustain the cycle). The player "bends" pitch by changing lip tension (mechanical resonance) and blowing pressure.

This is the **striking-reed / inward-swinging valve** family (like the human larynx), as opposed to the clarinet's **outward-swinging** reed. The distinction matters: the sign of the valve's response to mouthpiece pressure is reversed, which changes which bore-resonance alignment sustains oscillation.

### 2.1 The lip valve (exciter)

Model the lip as a mass $m_r$ on a spring $k_r$ with damping $r_r$, displacement $y(t)$ (positive = open). The driving force is the pressure difference across the lip times an effective area $S$:

$$
m_r\,\ddot y + r_r\,\dot y + k_r\,(y - y_0) = (p_m - p)\,S
$$

with $y \ge 0$ (the lips cannot pass through the mouthpiece — a one-sided / *unilateral* contact constraint; clamp $y = \max(y, 0)$ and zero the inward velocity on contact, optionally with a restitution coefficient).

The airflow through the opening is (turbulent, Bernoulli):

$$
u(t) = w\,y(t)\,\sqrt{\frac{2\,|p_m - p|}{\rho}}\;\mathrm{sgn}(p_m - p)
$$

where $w$ = effective lip-slit width, $\rho$ = air density. This is the crucial **nonlinearity**: flow $\propto$ opening $\times$ $\sqrt{\Delta p}$. Even a perfectly sinusoidal lip motion produces a non-sinusoidal (pulse-like) flow → a harmonic-rich spectrum → the brass "buzz."

### 2.2 The bore and bell (resonator)

The flaring duct is a waveguide. Two equivalent formulations:

**(a) Digital waveguide (traveling-wave).** Decompose pressure into right-going $p^+$ and left-going $p^-$ waves. Propagation down the bore = a pair of delay lines (bidirectional); the flare and bell impose a **reflection function** $r(t)$ (an FIR filter) and a transmission/radiation filter. At the mouthpiece the flow continuity equation closes the loop:

$$
p = Z_c\,(u^+ - u^-), \qquad u = u^+ + u^- \;\Rightarrow\; p = p^+ + p^- ,\quad u = \frac{p^+ - p^-}{Z_c}
$$

with $Z_c = \rho c / S_0$ the bore characteristic impedance. The lip injects $u$; the returned $p^-$ is the bore's delayed/filtered echo of $p^+$.

**(b) Modal / input-impedance (frequency-domain).** The bore presents an input impedance $Z(\omega)$ with peaks at the resonances. The mouthpiece pressure is the convolution of the flow with the bore impulse response $h(t) = \mathcal{F}^{-1}\{Z\}$:

$$
p(t) = (h * u)(t)
$$

Form (b) is the **reflection-function / convolution** method (Agulló, Barjau; used in many real-time brass models) and is the simplest in NumPy: precompute one FIR $h[n]$ for the bore+bell, then $p[n] = \sum_k h[k]\,u[n-k]$ per sample.

The **bell** shapes the timbre decisively: it reflects low frequencies (keeping them in the bore to sustain the standing wave) and radiates high frequencies. Net effect on the radiated sound = a gentle high-pass + the resonance peaks; on a muted brass ( Harmon / cup / straight mute) an additional resonant cavity/filter colors the tone (wah-wah).

### 2.3 The coupled discrete-time system (one time-step)

Per sample $n$:

1. $p^-[n]$ = returned bore pressure (delay line + bell filter), or $p = (h*u)[n]$.
2. Compute mouthpiece pressure from flow continuity and the valve:
   - Explicit/iterative: solve for $u[n],\,p[n]$ jointly because $u$ depends on $p_m - p$ and $p$ depends on $u$. Use a **one-step Newton** or a fixed-point iteration (2–4 iterations), or the **table-lookup** trick (Cook) that precomputes the nonlinear junction.
3. Update lip dynamics: integrate the lip ODE with the new $(p_m - p)$ force (semi-implicit Euler / Verlet), enforce $y \ge 0$ unilateral contact.
4. Inject $u$ into the bore (advance delay lines / append to convolution history).
5. Radiated output = bell transmission filter applied to $p$ (the high-pass radiation).

Stability: the explicit coupling can go unstable at high blowing pressure; use the iterative/lookup junction and/or a small amount of numerical damping. Sample rate $\ge 44.1$ kHz; the lip ODE is stiff at realistic $k_r$ → use an implicit or symplectic integrator.

---

## 3. Mathematical formulation (compact)

**Lip (single mass, normalized):**
$$
\ddot y + \frac{\omega_r}{Q_r}\dot y + \omega_r^2 (y - y_0) = \frac{S}{m_r}(p_m - p),\qquad y \ge 0
$$
- $\omega_r = \sqrt{k_r/m_r}$ = lip mechanical resonance (player-set; ~ note fundamental for brass).
- $Q_r$ = lip quality factor (lip damping; controls how "free-buzzing" vs "tight").

**Flow (valve):**
$$
u = w\,y\,\sqrt{\frac{2|p_m-p|}{\rho}}\,\mathrm{sgn}(p_m-p)
$$

**Bore (reflection-function):**
$$
p[n] = \sum_{k=0}^{M-1} h[k]\,u[n-k], \qquad h = \mathcal{F}^{-1}\{Z_{\text{in}}(\omega)\}
$$
Bore resonances of an ideal open/closed cylinder at $f_k \approx (2k+1)c/(4L)$ (closed at mouthpiece); the flare+bell lower and compress these into the brass harmonic series and add the radiation high-pass.

**Radiated sound:**
$$
p_{\text{out}} = g_{\text{bell}} * p \quad (\text{bell transmission FIR, high-pass} + \text{mute filter})
$$

**Pitch control:** fundamental $\approx$ the bore resonance nearest the lip resonance; $f_0 \propto 1/L$ (slide/valves change $L$); player bends via $\omega_r$ and $p_m$.

**Brightness control:** $p_m$ (blowing pressure) → stronger nonlinearity → more high harmonics. This is the physical origin of *fortissimo = brighter*.

---

## 4. NumPy implementation sketch

```python
import numpy as np

def lip_reed_brass(f0, dur, sr=44100, p_m=3000.0, wr_res=None, Qr=4.0,
                   bore_len=None, flare=0.5, mute=None, n_iter=3):
    """Render one brass note via coupled lip-valve + bore reflection function.

    f0       : target fundamental (Hz)  -> sets lip resonance & bore length
    dur      : seconds
    p_m      : blowing (mouth) pressure, Pa  -> brightness/loudness
    wr_res   : lip resonance Hz (default ~ f0)
    Qr       : lip quality factor
    bore_len : tube length m (default c/(2*f0) open-equiv)
    flare    : bell flare factor -> radiation high-pass corner
    mute     : None | 'straight' | 'harmon' | 'cup' -> extra cavity filter
    n_iter   : fixed-point iterations at the nonlinear junction
    """
    N = int(dur * sr)
    c, rho = 343.0, 1.2
    L = bore_len if bore_len else c / (2.0 * f0)
    w_r = 2*np.pi*(wr_res if wr_res else f0)
    dt = 1.0/sr
    # bore impulse response h: resonances + bell high-pass (placeholder FIR)
    M = int(0.05*sr)
    n = np.arange(M)
    res = np.array([(2*k+1)*c/(4*L) for k in range(6)])           # closed-pipe modes
    h = sum(np.exp(-n*sr*0.0005*(1+k))*np.cos(2*np.pi*fr*n/sr) for k,fr in enumerate(res))
    h *= 1.0/np.abs(h).max()
    hist = np.zeros(M)
    y = np.array([0.0, 0.0])     # lip displacement & velocity
    out = np.zeros(N)
    S, m_r, w = 1e-4, 1e-5, 2e-3
    y0 = 1e-4                    # lip rest opening
    for i in range(N):
        p = float(np.dot(hist, h))         # mouthpiece pressure from bore
        for _ in range(n_iter):            # solve nonlinear junction
            u = w*max(y[0],0.0)*np.sqrt(2*abs(p_m-p)/rho)*np.sign(p_m-p)
            p = float(np.dot(hist, h)) + 0.5*u*rho*c/S  # crude impedance closure
        # lip dynamics (semi-implicit Euler) + unilateral contact
        acc = (S/m_r)*(p_m - p) - (w_r/Qr)*y[1] - w_r**2*(y[0]-y0)
        y[1] += acc*dt; y[0] += y[1]*dt
        if y[0] < 0.0: y[0], y[1] = 0.0, max(y[1], 0.0)   # lips hit mouthpiece
        hist = np.roll(hist, 1); hist[0] = u               # inject flow into bore
        out[i] = p
    # bell radiation high-pass + optional mute filter, then normalize
    return out / (np.abs(out).max() + 1e-12)
```

*(Sketch only — production version uses a measured bore reflection function, a proper junction solver, and a bell/mute FIR bank.)*

---

## 5. Musical Elements Framework

| Element | LIPS mechanism | Musical output |
|---|---|---|
| **PITCH** | bore length $L$ sets resonance series; lip resonance $\omega_r$ + blowing pressure $p_m$ select & bend the mode | the harmonic series of the tube; valves/slide = change $L$; lip-bend = continuous portamento; multiphonics = blowing between modes |
| **RHYTHM** | per-note onset = raise $p_m$ from 0 (tongue = brief $p_m$ interrupt = articulation); sustain = hold $p_m$ | attack "bite," tongued staccato, slur (hold $p_m$, move $\omega_r$), breath phrase length |
| **HARMONY** | each voice = one bore; chord = multiple bores/lips (polyphony = multiple LIPS instances); mute = spectral filter per voice | brass choir; Harmon-mute "wah" harmony; open vs muted contrast |
| **STRUCTURE** | per-section bore/mute/pressure schedule; crescendo = $p_m$ ramp; doits/falls = $\omega_r$ glide at note end | section-level brass arrangement: open fanfare → muted verse → fortissimo climax |
| **TEXTURE** | $p_m$ (dynamic→brightness), $Q_r$ (free/tight buzz), flare/mute (radiation), unison detune of multiple instances | solo lead, tight section, warm section (low $p_m$), brassy fortissimo (high $p_m$) |

---

## 6. UnitMatrix Integration

- **Rows (Voices)** = one LIPS instance per voice row (trumpet 1, trumpet 2, trombone, tuba). Each row's notes are rendered independently then summed. Polyphony = N parallel exciter+bore pairs (cost scales linearly with voices).
- **Columns (Sections)** = per-section *performance* parameters: `{STRUCTURE}` carries mute on/off, section dynamic ($p_m$ baseline), and section articulation (tongued vs slurred). A muted A-section → open B-section is a one-parameter change.
- **Cells (MusicUnit)** = each note cell carries `{PITCH}` (→ bore length + lip resonance), `{RHYTHM}` (onset/duration → $p_m$ envelope), `{TEXTURE}` (velocity → $p_m$ peak → brightness; mute type). Velocity maps *physically* to blowing pressure, so a loud note is automatically brighter — matching real brass (a built-in, free "velocity→filter" that sample libraries fake with key-switches).
- **Flow**: `lip_reed_brass(note_spec)` per note → accumulate into the section buffer → mix under other voices → post-FX (SP-007 EQ, SP-008 DRC, SP-009/SP-032 reverb). It is a **note-event consumer** (unlike SP-064's continuous pad). Deterministic per seed → zero-drift gate unaffected (audio layer, no MIDI).

---

## 7. Pitfalls

1. **Explicit junction instability** — solving $u(p_m-p)$ and $p(u)$ in one explicit step oscillates/blows up at high $p_m$. Fix: 2–4 fixed-point iterations, a one-step Newton, or Cook's precomputed nonlinear table lookup.
2. **Stiff lip ODE** — realistic $k_r$ makes $\omega_r$ high → explicit Euler unstable. Fix: semi-implicit/symplectic integrator, or solve the lip in closed form per sample (it is a driven SHO between contacts).
3. **Wrong valve sign** — brass lips are *inward-swinging* (+1 valve); coding them like a clarinet's outward-swinging reed (−1 valve) gives no sustained oscillation or wrong mode. Check the sign of the $(p_m-p)$ term and the flow coupling.
4. **No oscillation / no note** — if $p_m$ is below the oscillation threshold, or the bore resonance is too far from $\omega_r$, the loop gain < 1 and you get noise/puffs. Fix: raise $p_m$, tune $\omega_r$ near a bore mode, ensure the bore reflection is strong enough.
5. **Unilateral contact clicks** — hard clamping $y \ge 0$ injects broadband clicks. Fix: soft-contact (penalty) model or smooth the velocity reversal; low-pass the lip force.
6. **Aliasing from the $\sqrt{\cdot}$ nonlinearity** — the valve generates harmonics above Nyquist. Fix: oversample the exciter (2–4×) or use SP-062 ADAA on the junction; the bore filter removes some but not all.
7. **Bore length vs lip resonance mismatch = wrong pitch** — the played note is set by the *bore*, but beginners set pitch by $\omega_r$ alone. Fix: always derive bore length from the target $f_0$ and set $\omega_r \approx f_0$; let $\omega_r$ only *bend* around it.
8. **Static timbre** — holding $p_m$, $\omega_r$ constant sounds like an organ, not brass. Fix: add slow $p_m$ vibrato/swell, attack transient on $p_m$, and per-note random micro-variation (SP-006-style humanization at the audio layer).

---

## 8. Comparison with related methods

| Method | Exciter | Resonator | Valve type | Family | Cost |
|---|---|---|---|---|---|
| SP-023 clarinet | single reed | cylindrical bore | outward-swinging (−1) | woodwind | low |
| SP-024 bowed string | stick-slip friction | string (bi-dir waveguide) | contact | string | low |
| SP-011/048 string | pluck/strike | string + body | — | string | very low |
| SP-040 struck plate | hammer | plate modes/FDTD | — | percussion | high |
| **SP-065 brass** | **lip valve (2-mass)** | **flaring bore + bell** | **inward-swinging (+1)** | **brass** | **low–med** |
| SP-045 DDSP | neural f0/loudness | harmonic+noise | learned | neural | med |

---

## 9. References

- McIntyre, M. E., Schumacher, R. T., & Woodhouse, J. (1981). "Aperiodicity in bowed-string motion" / "On the oscillations of musical instruments." *J. Acoust. Soc. Am.* 69(5), 1325–1345; 74(5), 1325–1345 (1983). (General self-sustained oscillator framework for reed/lip/bow.)
- Adachi, S., & Sato, M. (1996). "Trumpet sound simulation using a two-dimensional lip vibration model." *J. Acoust. Soc. Am.* 99(2), 1200–1209. (Two-mass lip model.)
- Adachi, S., & Sato, M. (1995). "Time-domain simulation of sound production in the brass instrument." *J. Acoust. Soc. Am.* 97(6), 3850–3861.
- Vergez, C., & Rodet, X. (2000). "Trumpet and trumpet player: model and simulation in a musical context." *Proc. ICMC*. (Real-time lip+bore model.)
- Cook, P. R. (1993). "Bone, a bore model for brass instruments" / *SPASM* singer and brass instruments. (Table-lookup nonlinear junction; real-time.)
- Fletcher, N. H., & Rossing, T. D. (1998). *The Physics of Musical Instruments*, 2nd ed., Springer. (Brass acoustics, bell radiation, impedance.)
- Agulló, J., Barjau, A., & Martínez, J. (1988). "On the time-domain simulation of brass instruments." (Reflection-function method.)
- de Bruyn, ... / Causse, R., Kergomard, J., & Lurton, X. (1984). "Input impedance of brass musical instruments." *J. Acoust. Soc. Am.* 75(1), 241–254. (Measured input impedance → reflection function.)
- Msallam, R., Dequidt, S., Causse, R., & Tassart, S. (2000). "Physical model of the trombone including nonlinear propagation." *Acta Acustica* 86. (Nonlinear wave steepening → brassy "brassiness" at fortissimo.)
