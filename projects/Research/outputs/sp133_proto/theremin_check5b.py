"""SP-133 check 5b: octave-per-0.01 pF at a ~10 pF antenna-tank operating point.

The Wikipedia claim "0.01 pF -> a full octave of frequency shift" applies when the
antenna capacitance dominates the tank (C2 ~ 10 pF). With a fat 40 pF tank the same
0.01 pF yields only ~1.35x (measured). This is the same physics:  df/f = -dC/(2*C2).
"""
import numpy as np

EPS0 = 8.854e-12
PI = np.pi

def C_antenna(h=0.5, d=0.01, k=0.4):
    return 2 * PI * EPS0 * h / (np.log(2 * h / d) - k)

def dC_hand(x, h=0.5, d=0.01):
    return PI * EPS0 * h / (10 * np.log(4 * x / d))

def f_pitch(x, L, C1, C_fix):
    C2 = C_fix + C_antenna() + dC_hand(x)
    C_eq = C1 * C2 / (C1 + C2)
    return 1.0 / (2 * PI * np.sqrt(L * C_eq))

# ~10 pF tank:  C_fix = 3.4 pF + C_A 6.6 pF + hand 0.2-0.5 pF  ->  C2 ~ 10.2-10.6 pF
# tune L so f_pitch ~ 1 MHz at x = 1 m
C1 = 220e-12
C_fix = 3.4e-12
f_at_1m = f_pitch(1.0, 100e-6, C1, C_fix)
L = 1.0 / ((2 * PI * 1e6) ** 2 * (C1 * (C_fix + C_antenna() + dC_hand(1.0)) / (C1 + C_fix + C_antenna() + dC_hand(1.0))))
F_REF = f_pitch(1.0, L, C1, C_fix)
print(f"L = {L*1e3:.1f} mH, F_REF = {F_REF/1e3:.0f} kHz")

# operating point: beat = 500 Hz
import scipy.optimize as so
def beat(x):
    return F_REF - f_pitch(x, L, C1, C_fix)
x0 = so.brentq(lambda x: beat(x) - 500.0, 0.1, 1.0)
C2a = C_fix + C_antenna() + dC_hand(x0)
C2b = C2a + 0.01e-12
Ceq_a = C1 * C2a / (C1 + C2a); Ceq_b = C1 * C2b / (C1 + C2b)
fa = 1.0 / (2 * PI * np.sqrt(L * Ceq_a)); fb = 1.0 / (2 * PI * np.sqrt(L * Ceq_b))
print(f"op x0 = {x0:.3f} m, C2 = {C2a*1e12:.2f} pF")
print(f"beat 500.0 -> {F_REF-fb:.0f} Hz after +0.01 pF  (ratio {(F_REF-fb)/500:.3f}, want ~2.0)")
# raw-law beat range with this tank (documented trade-off: too hot for 1 m playing range)
xs = np.linspace(0.06, 1.0, 100)
bt = np.array([beat(x) for x in xs])
print(f"raw-law beat range over [0.06, 1.0] m: {bt.min():.0f} .. {bt.max():.0f} Hz "
      f"(linearizing coil needed for a usable 0-8 kHz air-keyboard)")
