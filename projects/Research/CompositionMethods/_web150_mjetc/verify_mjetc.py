"""verify_mjetc.py — Method 150 MJETC numerical verification (v2).

Checks (all deterministic, numpy only):
  1.  Escape-radius theorem (|z|>2 => divergence) on samples.
  2.  Smooth-coloring continuity across the |z|=2 boundary.
  3.  Period detection: cardioid 0.2+0.1i -> 1; -1.0 -> 2; -0.8+0.1i -> 2;
      -0.1226+0.7449i -> 3; -1.7549 -> 3 (real "airplane").
  4.  Period-doubling cascade on the real axis: -0.75->2, -1.25->4, -1.3680989->8,
      -1.3940462->16; Feigenbaum point -1.401155: no small period.
  5.  Symmetry: tau(cbar) == tau(c).
  6.  Julia sets: connected iff critical orbit bounded (Fatou–Julia);
      filled-set fraction: in-M >> out-M.
  7.  Mandelbrot membership spot checks.
  8.  Self-similarity: period-3 mini-Mandelbrot near -1.7549 (escape-time spike).
  9.  Orbit gravity: real cardioid orbit converges monotonically to the fixed point;
      c=-1 enters the 2-cycle {0,-1} exactly.
 10.  UnitMatrix-shaped escape-time field (voices x sections texture table).
"""
import warnings
import numpy as np

warnings.filterwarnings("ignore", category=RuntimeWarning)
results = []

def escape_time(c_arr, max_iter=256, R=2.0, smooth=False):
    c = c_arr.astype(np.complex128).ravel()
    z = np.zeros_like(c)
    n = np.zeros(c.shape, dtype=np.int32)
    alive = np.ones(c.shape, dtype=bool)
    for _ in range(max_iter):
        z[alive] = z[alive] ** 2 + c[alive]
        alive &= (np.abs(z) <= R)
        n[alive] += 1
    if smooth:
        out = n.astype(np.float64) + 1.0
        safe = np.abs(z) > 0
        out[safe] += 1.0 - np.log2(np.log(np.abs(z[safe])) / np.log(R))
        return out
    return n

# --- 1. escape radius theorem ---
rng = np.random.default_rng(42)
cs = rng.uniform(-2, 2, 2000) + 1j * rng.uniform(-2, 2, 2000)
tau = escape_time(cs, max_iter=64)
ok1 = True
for c, t in zip(cs, tau):
    if t < 64:
        z = 0j
        for _ in range(int(t) + 1):
            z = z * z + c
        if abs(z) <= 2.0:
            ok1 = False
            break
results.append(("1 escape-radius |z|>2 => divergence (2000 samples)", ok1))

# --- 2. Green's function continuity: G(c) = lim log|z_n|/2^n is the capacity potential of M
#         (Douady–Hubbard), continuous in c; raw escape time is staircased (integer bands).
#         Overflow-safe: stop at |z|>1e100 (log|z|/2^n is already converged there). ---
c_line = np.linspace(0.9 + 0.1j, 1.1 + 0.1j, 20001)
c = c_line.astype(np.complex128)
z = np.zeros_like(c)
Gn = np.zeros(c.shape)
big = np.zeros(c.shape, dtype=bool)
for n in range(1, 513):
    z = z * z + c
    huge = np.abs(z) > 1e100
    new = huge & ~big
    Gn[new] = np.log(np.abs(z[new])) / (2.0 ** n)
    big |= huge
    if big.all():
        break
# any non-big survivors: interior points (log|z| -> -inf, G -> 0 in the limit)
Gn[~big] = 0.0
g_jumps = np.abs(np.diff(Gn))
# G varies smoothly (a gentle linear slope is fine); the test is the ABSENCE of outlier jumps:
# max |dG| must be ~mean |dG| (ratio ~1 = pure slope, no staircase discontinuities)
ok2 = (g_jumps.max() < 1e-4) and (g_jumps.max() < 5.0 * g_jumps.mean() + 1e-9)
results.append(("2 Green's function continuity (max |dG| %.2e, mean %.2e, ratio %.2f over 20k pts)"
                % (g_jumps.max(), g_jumps.mean(), g_jumps.max() / g_jumps.mean()), ok2))

# --- 3. period detection via orbit cycle detection ---
def orbit_period(c, max_iter=4096, tol=1e-7):
    """Period of the attracting cycle for critical orbit z0=0; 0 if escapes; -1 if aperiodic."""
    z = 0j
    hist = [0j]
    for i in range(1, max_iter):
        z = z * z + c
        if abs(z) > 2.0:
            return 0
        # compare against recent history (skip transient)
        lo = max(i - 256, 0)
        for j in range(lo, i):
            if abs(z - hist[j]) < tol:
                return i - j
        hist.append(z)
    return -1

per = {c: orbit_period(c) for c in [0.2 + 0.1j, -1.0, -0.8 + 0.1j, -0.1226 + 0.7449j, -1.7549]}
ok3 = (per[0.2 + 0.1j] == 1 and per[-1.0] == 2 and per[-0.8 + 0.1j] == 2
       and per[-0.1226 + 0.7449j] == 3 and per[-1.7549] == 3)
results.append(("3 bulb periods %s" % str(per), ok3))

# --- 4. period-doubling cascade: superstable centers found numerically ---
def superstable_center(p, lo, hi, steps=40000):
    """c minimizing |f^p_c(0)| on [lo,hi] (the superstable center of the period-p bulb)."""
    cg = np.linspace(lo, hi, steps).astype(np.complex128)
    z = np.zeros_like(cg)
    for _ in range(p):
        z = z * z + cg
    return cg[np.argmin(np.abs(z))]

centers = {2: -1.0, 4: superstable_center(4, -1.35, -1.25),
           8: superstable_center(8, -1.40, -1.36), 16: superstable_center(16, -1.405, -1.395)}
per_casc = [orbit_period(centers[p], max_iter=4096) for p in (2, 4, 8, 16)]
per_feig = orbit_period(-1.4011551890920506, max_iter=8192, tol=1e-9)
ok4 = (per_casc == [2, 4, 8, 16]) and (per_feig == -1 or per_feig > 64)
results.append(("4 cascade superstable centers %s -> periods %s; Feigenbaum pt period %s"
                % ({p: round(c.real, 7) for p, c in centers.items()}, per_casc, per_feig), ok4))

# --- 5. symmetry ---
tau_a = escape_time(cs, max_iter=128)
tau_b = escape_time(np.conj(cs), max_iter=128)
ok5 = bool(np.array_equal(tau_a, tau_b))
results.append(("5 symmetry tau(cbar)==tau(c) on 2000 samples", ok5))

# --- 6. Julia sets: connected iff critical orbit bounded (Fatou–Julia) ---
def critical_bounded(c, max_iter=2048):
    z = 0j
    for _ in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return False
    return True

def filled_frac(c, n=6000, max_iter=256, R=2.0):
    z0 = rng.uniform(-1.5, 1.5, n) + 1j * rng.uniform(-1.5, 1.5, n)
    z = z0.copy()
    for _ in range(max_iter):
        z = z * z + c
    return float(np.mean(np.abs(z) <= R))

conn_in = critical_bounded(-1.1)     # c in M -> J connected
conn_out = critical_bounded(1.1)     # c not in M -> J Cantor dust
f_inside = filled_frac(-1.1)
f_outside = filled_frac(1.1)
ok6 = conn_in and (not conn_out) and (f_inside > 5 * f_outside)
results.append(("6 Julia: crit-orbit bounded c=-1.1:%s c=1.1:%s; filled frac %.3f vs %.5f"
                % (conn_in, conn_out, f_inside, f_outside), ok6))

# --- 7. Mandelbrot membership spot checks ---
def in_mandelbrot(c, max_iter=1024):
    return escape_time(np.array([c]), max_iter=max_iter)[0] == max_iter

in_pts = [0.2 + 0.1j, -0.8 + 0.1j, -1.7549, 0.1 + 0.1j, -1.0]
out_pts = [1.1, -2.1, 0.3 + 0.6j, 0.5 + 0.5j]
m_in = [in_mandelbrot(x) for x in in_pts]
m_out = [in_mandelbrot(x) for x in out_pts]
ok7 = all(m_in) and not any(m_out)
results.append(("7 M membership: in %s -> %s; out %s -> %s" % (in_pts, m_in, out_pts, m_out), ok7))

# --- 8. self-similarity: mini-Mandelbrot near -1.7549 ---
grid = np.linspace(-1.7565, -1.7533, 401) + 1j * np.linspace(0.0, 0.0032, 33)[:, None]
tau_mini = escape_time(grid.ravel(), max_iter=300).reshape(grid.shape)
ok8 = bool(tau_mini.max() >= 300)
results.append(("8 period-3 mini-Mandelbrot near -1.7549: max escape time %d (cap 300)" % tau_mini.max(), ok8))

# --- 9. orbit gravity ---
# c=0.2 (real, cardioid): monotone convergence to attracting fixed point fp=(1-sqrt(1-4c))/2
c_home = 0.2
fp = (1 - np.sqrt(1 - 4 * c_home)) / 2
z = 0j
dists = []
for _ in range(40):
    z = z * z + c_home
    dists.append(abs(z - fp))
dists = np.array(dists)
mono = bool(np.all(np.diff(dists) < 0))
conv = bool(dists[-1] < 1e-8)
# c=-1: enters the 2-cycle {0,-1} exactly at n=1
z2 = 0j
orb2 = [0j]
for _ in range(4):
    z2 = z2 * z2 - 1.0
    orb2.append(z2)
cycle_hit = bool(orb2[1] == -1 and orb2[2] == 0 and orb2[3] == -1)
ok9 = mono and conv and cycle_hit
results.append(("9 gravity: dist-to-fixedpoint tail %.2e, monotone %s, conv %s; c=-1 cycle %s"
                % (dists[-1], mono, conv, orb2[1:4]), ok9))

# --- 10. UnitMatrix-shaped escape-time field (voices x sections) ---
c_julia = -0.8 + 0.1j
z0s = rng.uniform(-1.5, 1.5, 64) + 1j * rng.uniform(-1.5, 1.5, 64)
z = z0s.copy()
field = np.zeros((64, 64), dtype=bool)
for t in range(64):
    z = z * z + c_julia
    field[:, t] = (np.abs(z) <= 2.0)
row_activity = field.sum(axis=1)
ok10 = field.shape == (64, 64) and bool(row_activity.min() < row_activity.max())
results.append(("10 UnitMatrix texture field 64x64, row activity range [%d,%d]"
                % (row_activity.min(), row_activity.max()), ok10))

# --- report ---
print("=" * 78)
print("MJETC verification — %d checks" % len(results))
for i, (name, ok) in enumerate(results, 1):
    print("%2d. [%s] %s" % (i, "PASS" if ok else "FAIL", name))
npass = sum(ok for _, ok in results)
print("=" * 78)
print("RESULT: %d/%d checks pass" % (npass, len(results)))
