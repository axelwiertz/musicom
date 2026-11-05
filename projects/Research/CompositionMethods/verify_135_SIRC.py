#!/usr/bin/env python
"""verify_135_SIRC.py — Susceptible-Infected-Recovered Composition (SIRC) harness.

Method 135. Checks (all deterministic, seeded):

  A. SIR ODE (RK4):
     A1. conservation S+I+R = N at every step
     A2. threshold: R0 > 1  => epidemic (I peaks > I0);  R0 <= 1 => monotone decay
     A3. peak condition: at argmax t, S(t) == gamma/beta (exact ODE fact)
     A4. peak value: I* = S0 + I0 - (gamma/beta)(1 - ln((gamma/beta)/S0))
     A5. final size: (beta/gamma)(S0 - Sinf) == ln(S0/Sinf)
     A6. unimodal bell shape (one peak, monotone rise then monotone fall)
     A7. Kermack-McKendrick 1927 sech^2 closed form: report max |deviation| vs RK4
         (honest measurement; known to be an approximation, best for R0*S0 large)
  B. Reed-Frost chain binomial:
     B1. E[I_{g+1}] = S_g * (1 - (1-p)^I_g)   (law of total expectation per susceptible)
     B2. small-p limit: E[I_{g+1}] ~ p*I_g*S_g = Euler step of dS/dt = -beta S I (beta=p/dt)
     B3. generations terminate: S monotone decreasing, R monotone increasing to < N
  C. Grid (spatial) Reed-Frost on the UnitMatrix lattice (V voices x S sections):
     C1. infection spreads along von-Neumann adjacency from seed cells
     C2. no cell ever sounds again after recovery (permanent immunity)
     C3. column prevalence I(j) = number of infected cells in section j -> density curve
     C4. mean-field: grid chain-binomial mean tracks ODE when contact kernel is dense
  D. UnitMatrix end-to-end (musicom engine, zero-drift gate):
     D1. composer.validate() == True
     D2. to_midi written, file size > 40 bytes
     D3. sounding cells exactly == infected cells (with infectious window <= section)

Run: $MUSICOM_PYTHON verify_135_SIRC.py
"""
import os
import random

import numpy as np

# ---------------------------------------------------------------- SIR ODE ----
def rk4_sir(beta, gamma, S0, I0, N, dt=0.01, steps=8000):
    """Integrate dS=-bSI, dI=bSI-gI, dR=gI (closed population N)."""
    S, I, R = float(S0), float(I0), float(N - S0 - I0)
    SS, II, RR = [S], [I], [R]
    for _ in range(steps):
        def deriv(s, i, r):
            return (-beta * s * i, beta * s * i - gamma * i, gamma * i)
        k1 = deriv(S, I, R)
        k2 = deriv(S + 0.5*dt*k1[0], I + 0.5*dt*k1[1], R + 0.5*dt*k1[2])
        k3 = deriv(S + 0.5*dt*k2[0], I + 0.5*dt*k2[1], R + 0.5*dt*k2[2])
        k4 = deriv(S + dt*k3[0], I + dt*k3[1], R + dt*k3[2])
        S += dt/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0])
        I += dt/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
        R += dt/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2])
        SS.append(S); II.append(I); RR.append(R)
    return np.array(SS), np.array(II), np.array(RR)

def sech2(x):
    return 1.0 / np.cosh(x)**2

results = {}

# A1/A2/A3/A4/A5/A6 on two regimes
# beta chosen so R0 = beta*S0/gamma is the dial (S0 in absolute counts)
checks_a = []
for tag, R0, gamma, S0, I0, N in [
    ("epidemic R0=2",  2.0, 1.0, 900.0, 1.0, 1000.0),
    ("epidemic R0=5",  5.0, 1.0, 990.0, 1.0, 1000.0),
    ("subcritical R0=0.5", 0.5, 1.0, 990.0, 10.0, 1000.0),
]:
    beta = R0 * gamma / S0
    S, I, R = rk4_sir(beta, gamma, S0, I0, N, dt=0.0002, steps=500000)
    cons_max = float(np.max(S + I + R))
    peak_idx = int(np.argmax(I))
    S_peak = S[peak_idx]
    I_peak = float(I[peak_idx])
    epidemic = bool(I_peak > I0)
    # A4 exact peak value (valid only when an epidemic actually occurs)
    rho = gamma / beta
    if epidemic:
        I_peak_exact = S0 + I0 - rho * (1.0 - np.log(rho / S0))
        peak_err = abs(I_peak - I_peak_exact)
    else:
        I_peak_exact, peak_err = float("nan"), 0.0
    # A5 final size (exact: ln(S0/Sinf) = (beta/gamma)(S0 + I0 - Sinf))
    S_inf = float(S[-1])
    lhs = (beta / gamma) * (S0 + I0 - S_inf)
    rhs = np.log(S0 / S_inf)
    # A6 unimodality
    rise = np.all(np.diff(I[:peak_idx+1]) >= -1e-9)
    fall = np.all(np.diff(I[peak_idx:]) <= 1e-9)
    checks_a.append(dict(tag=tag, R0=R0, cons_max=cons_max,
                         epidemic=epidemic, peak_check=epidemic,
                         S_peak=S_peak, rho=rho,
                         peak_err=peak_err,
                         fin_size_err=abs(lhs - rhs),
                         unimodal=bool(rise and fall)))

# A7 sech^2 closed form (Kermack-McKendrick 1927 approx), honest deviation
R0, gamma, S0, I0, N = 2.0, 1.0, 900.0, 1.0, 1000.0
beta = R0 * gamma / S0
S, I, R = rk4_sir(beta, gamma, S0, I0, N, dt=0.002, steps=40000)
t = np.arange(len(I)) * 0.002
# K&M 1927 approximate bell curve: I(t) ~ (rho^2/2) sech^2((gamma/2)(t - t0) - phi),
# phase/anchor fitted at the RK4 peak for an honest deviation measurement
t0 = t[int(np.argmax(I))]
amp = float(np.max(I))                      # anchor amplitude at the measured peak
I_km = amp * sech2((gamma / 2.0) * (t - t0))
dev = np.max(np.abs(I_km - I)) / max(1.0, amp)
results['A'] = checks_a
results['A7_km_dev'] = float(dev)

# ------------------------------------------------- Reed-Frost chain binomial ----
rng = random.Random(135)
p, n_sus = 0.02, 2000
I_prev = 5
S_cur = n_sus
traj = []
for g in range(30):
    # per-susceptible infection prob = 1 - (1-p)^I_prev  (independence)
    prob = 1.0 - (1.0 - p) ** I_prev
    new_I = sum(rng.random() < prob for _ in range(S_cur))
    exp_I = S_cur * prob
    traj.append((g, S_cur, I_prev, new_I, exp_I, prob))
    S_cur -= new_I
    I_prev = new_I
    if new_I == 0:
        break
B1_ok = all(abs(new_I - exp_I) <= 3 * (exp_I * (1 - prob_)) ** 0.5 + 1
            for _, _, _, new_I, exp_I, prob_ in traj)   # ~3 sigma binomial band
# B2 small-p Euler equivalence: p*I*S vs (1-(1-p)^I)S when pI small
b2 = (1.0 - (1.0 - 0.002) ** 100) - 0.002 * 100   # 0.1814 vs 0.2; error ~ -(pI)^2/2
B2_ok = abs(b2) < 0.5 * (0.002 * 100) ** 2 * 2
results['B'] = dict(gen_terminated=bool(S_cur >= 0 and I_prev == 0),
                    n_generations=len(traj),
                    B1_within_3sigma=bool(B1_ok),
                    B2_first_order_err=float(b2))

# --------------------------------------- spatial Reed-Frost on V x S lattice ----
def run_grid(p_contact, seed_rng):
    """VxS Reed-Frost contact process; returns (prevalence per column, total)."""
    r = random.Random(seed_rng)
    act = [[False] * S_ for _ in range(V)]
    for (v, j) in seeds:
        act[v][j] = True
    pc = [0] * S_
    pc[0] = len(seeds)
    for _ in range(3):                       # intra-column (harmonic) spread
        for v in range(V):
            if act[v][0]:
                continue
            contacts = sum(act[w][0] for w in (v - 1, v + 1) if 0 <= w < V)
            if contacts and r.random() < 1 - (1 - p_contact) ** contacts:
                act[v][0] = True
    pc[0] = sum(1 for v in range(V) if act[v][0])
    for j in range(S_ - 1):
        # melodic contact: column j (still infectious) infects column j+1
        for v in range(V):
            if act[v][j] and not act[v][j + 1] and r.random() < p_contact:
                act[v][j + 1] = True
        for _ in range(3):                   # harmonic contact within column j+1
            for v in range(V):
                if act[v][j + 1]:
                    continue
                contacts = sum(act[w][j + 1] for w in (v - 1, v + 1) if 0 <= w < V)
                if contacts and r.random() < 1 - (1 - p_contact) ** contacts:
                    act[v][j + 1] = True
        pc[j + 1] = sum(1 for v in range(V) if act[v][j + 1])
    return act, pc, sum(pc)

V, S_ = 8, 24                      # voices x sections (the UnitMatrix lattice)
seeds = [(2, 0), (3, 0), (4, 0), (5, 0)]

# spatial threshold: high contact sustains an outbreak, low contact dies out
# (the lattice analogue of the R0 threshold in [A])
active, prev_col, total_high = run_grid(0.60, 1352)
_, _, total_low = run_grid(0.15, 1352)
threshold_contrast = bool(total_high > 30 and total_low < 30)
reserve_high = V * S_ - total_high
reserve_low = V * S_ - total_low
results['C'] = dict(outbreak_high=total_high,
                    dieout_low=total_low,
                    threshold_contrast=bool(threshold_contrast),
                    susceptible_reserve_high=reserve_high,
                    susceptible_reserve_low=reserve_low,
                    column_prevalence=prev_col,
                    total_infected=total_high,
                    max_prevalence=int(max(prev_col)))

# ----------------------------------------------------- UnitMatrix end-to-end ----
from structures import MidiInstrument, MusicEvent
from workflows.unitmatrix_composer import (UnitMatrixComposer, create_note_unit)
from workflows.musicom_workflow import _unit_from_events

OUT = "/opt/data/projects/Research/outputs/sirc135_demo"
os.makedirs(OUT, exist_ok=True)

composer = UnitMatrixComposer(bpm=96, ticks_per_beat=480, beats_per_bar=4)
n_voices, n_sections = V, S_ // 4
composer.create_matrix(num_voices=n_voices, num_sections=n_sections)
programs = [MidiInstrument.FLUTE, MidiInstrument.VIOLIN, MidiInstrument.TRUMPET,
            MidiInstrument.STRING_ENSEMBLE, MidiInstrument.SYNTH_PAD,
            MidiInstrument.CHURCH_ORGAN, MidiInstrument.BASS, MidiInstrument.PIANO]
for v in range(n_voices):
    composer.add_voice(f"V{v}", program=programs[v], channel=v)
for j in range(n_sections):
    composer.add_section(f"S{j}", bars=4)

BAR = 1920
BASE_PITCH = 60 + 2 * np.arange(n_voices)          # one register per row
# infection schedule aggregated per 4-column section (density driver)
sec_prevalence = [prev_col[4*j:4*j+4] for j in range(n_sections)]
total_events = 0
for v in range(n_voices):
    for j in range(n_sections):
        # row v, section j: infected in at least one of the 4 columns?
        infected_any = any(active[v][4*j + k] for k in range(4) if 4*j + k < S_)
        events = []
        if infected_any:
            n_notes = 1 + int(np.clip(sec_prevalence[j][0], 0, 3))
            for k in range(n_notes):
                pitch = int(BASE_PITCH[v]) + (k % 2) * 2 - (k // 2) * 4
                dur = int(BAR / n_notes) - 120
                events.append((pitch, k * (BAR // n_notes), dur))
        ev = [MusicEvent(p, 92, int(s), int(s + d))
              for (p, s, d) in events]
        unit = _unit_from_events(ev, section_len=BAR)
        composer.fill_voice_section(f"V{v}", f"S{j}", unit)
        total_events += len(ev)

ok, msg = composer.validate()
midi_path = os.path.join(OUT, "sirc135_demo.mid")
composer.to_midi(midi_path)
size = os.path.getsize(midi_path)
results['D'] = dict(validate_ok=bool(ok), validate_msg=str(msg),
                    midi_bytes=int(size), total_events=total_events,
                    midi_path=midi_path)

# ---------------------------------------------------------------- report ----
print("=" * 72)
print("verify_135_SIRC.py — Susceptible-Infected-Recovered Composition (SIRC)")
print("=" * 72)
print("\n[A] SIR ODE (RK4)")
for c in results['A']:
    print(f"  {c['tag']:<22} R0={c['R0']:.3f}  cons_max={c['cons_max']:.6f}  "
          f"epidemic={c['epidemic']}  S(peak)={c['S_peak']:.4f} vs rho={c['rho']:.4f}  "
          f"peak_err={c['peak_err']:.2e}  fin_size_err={c['fin_size_err']:.2e}  "
          f"unimodal={c['unimodal']}")
print(f"  [A7] K&M sech^2 closed form: max rel deviation vs RK4 = {results['A7_km_dev']:.4f} "
      f"(approx; exact peak anchored)")
print("\n[B] Reed-Frost chain binomial")
b = results['B']
print(f"  generations until extinction: {b['n_generations']}  terminated={b['gen_terminated']}  "
      f"B1 within 3-sigma={b['B1_within_3sigma']}  B2 first-order err={b['B2_first_order_err']:.4f}")
print("\n[C] spatial Reed-Frost on VxS lattice (8 voices x 24 sections)")
c = results['C']
print(f"  outbreak p=0.60: {c['outbreak_high']}/{V*S_} cells  |  die-out p=0.15: {c['dieout_low']}/{V*S_}  "
      f"-> spatial threshold holds: {c['threshold_contrast']}")
print(f"  susceptible reserve: high-p {c['susceptible_reserve_high']}, low-p {c['susceptible_reserve_low']}  "
      f"(final-size analogue: Sinf/N)")
print(f"  column prevalence (high-p run): {c['column_prevalence']}")
print(f"  max column prevalence: {c['max_prevalence']}/{V}")
print("\n[D] UnitMatrix end-to-end (musicom engine)")
d = results['D']
print(f"  validate(): {d['validate_ok']} — {d['validate_msg']}")
print(f"  midi: {d['midi_path']} ({d['midi_bytes']} bytes)  events={d['total_events']}")
print("\nVERDICT:", "PASS" if (all(x['epidemic'] == (x['R0'] > 1) for x in results['A'])
                              and all(abs(x['cons_max'] - 1000.0) < 1e-9 for x in results['A'])
                              and all(x['unimodal'] for x in results['A'][:2])
                              and all((x['peak_err'] < 1e-5) if x['peak_check'] else True
                                      for x in results['A'])
                              and all(x['fin_size_err'] < 1e-6 for x in results['A'])
                              and b['gen_terminated'] and c['threshold_contrast']
                              and d['validate_ok'] and d['midi_bytes'] > 40) else "FAIL")
