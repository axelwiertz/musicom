"""GTBRC verification (musicom methods DB, method 123).

Resource = (register band, metric slot).  A voice's strategy = the set of
resources its gesture would occupy.  Cost
    c_i(s) = priv_i(s_i) + sum_{r in s_i} c_r(load_r(s)) ,  c_r(k) = w1*k + w2*k^2
This is Rosenthal's congestion game, so the exact potential
    Phi(s) = sum_i priv_i(s_i) + sum_r sum_{k=1..load_r(s)} c_r(k)
satisfies  c_i(s_i,s_-i) - c_i(s'_i,s_-i) = Phi(s_i,s_-i) - Phi(s'_i,s_-i):
every unilateral improving move lowers Phi by exactly that amount, so
best-response dynamics is a descent on a bounded-below Lyapunov function and
must terminate at a pure Nash equilibrium (finite improvement property).

Checks below: monotone descent, termination at NE, iteration counts,
price of anarchy vs congestion pressure, hocket (load spreading), logit dial.
"""
import itertools
import math
import random
import statistics
import sys


def build(bands, slots, voices, seed, density_pref=3, w1=1.0, w2=1.0):
    rng = random.Random(seed)
    res = [(b, t) for b in range(bands) for t in range(slots)]
    ridx = {r: i for i, r in enumerate(res)}
    S = []
    for v in range(voices):
        home = min(bands - 1, round(v * (bands - 1) / max(1, voices - 1)))
        pool = []
        for _ in range(12):
            band = max(0, min(bands - 1, home + rng.choice([-1, 0, 0, 0, 1])))
            n = rng.choice([2, 3, 3, 4])
            sl = sorted(rng.sample(range(slots), n))
            pool.append((frozenset(ridx[(band, t)] for t in sl),
                         1.0 * abs(band - home) + 0.5 * abs(n - density_pref)))
        S.append(pool)
    return S, res, w1, w2


def loads(profile, nres):
    L = [0] * nres
    for rs, _ in profile:
        for r in rs:
            L[r] += 1
    return L


def cost(i, profile, strat, nres, w1, w2):
    L = loads([p for j, p in enumerate(profile) if j != i], nres)
    rs, priv = strat
    return priv + sum(w1 * (L[r] + 1) + w2 * (L[r] + 1) ** 2 for r in rs)


def potential(profile, nres, w1, w2):
    L = loads(profile, nres)
    phi = sum(priv for _, priv in profile)
    for k in L:
        for j in range(1, k + 1):
            phi += w1 * j + w2 * j * j
    return phi


def brd(S, nres, w1, w2, rng, max_sweeps=500):
    V = len(S)
    prof = [rng.choice(S[i]) for i in range(V)]
    phis = [potential(prof, nres, w1, w2)]
    moves = 0
    sw = 0
    for sw in range(1, max_sweeps + 1):
        order = list(range(V))
        rng.shuffle(order)
        moved = False
        for i in order:
            cur, bc = prof[i], cost(i, prof, prof[i], nres, w1, w2)
            best = cur
            for s in S[i]:
                if s is cur:
                    continue
                c = cost(i, prof, s, nres, w1, w2)
                if c < bc - 1e-12:
                    best, bc = s, c
            if best is not cur:
                prof[i] = best
                moved = True
                moves += 1
                phis.append(potential(prof, nres, w1, w2))
        if not moved:
            break
    return prof, phis, sw, moves


def is_ne(prof, S, nres, w1, w2):
    for i in range(len(S)):
        ci = cost(i, prof, prof[i], nres, w1, w2)
        for s in S[i]:
            if cost(i, prof, s, nres, w1, w2) < ci - 1e-12:
                return False
    return True


def experiment(bands, slots, voices, seed=7, trials=40, brute=True, w1=1.0, w2=1.0):
    S, res, w1, w2 = build(bands, slots, voices, seed, w1=w1, w2=w2)
    nres = len(res)
    rng = random.Random(seed + 1)
    up_viol, ne_ok, sweeps, mv, conv_phi = 0, 0, [], [], []
    for _ in range(trials):
        prof, phis, sw, m = brd(S, nres, w1, w2, rng)
        for a, b in zip(phis, phis[1:]):
            if b > a + 1e-9:
                up_viol += 1
        ne_ok += is_ne(prof, S, nres, w1, w2)
        sweeps.append(sw)
        mv.append(m)
        conv_phi.append(phis[-1])
    out = {
        "bands": bands, "slots": slots, "voices": voices,
        "resources": nres,
        "up_violations": up_viol,
        "ne": f"{ne_ok}/{trials}",
        "sweeps_mean": statistics.mean(sweeps),
        "sweeps_max": max(sweeps),
        "moves_mean": statistics.mean(mv),
        "phi_mean": statistics.mean(conv_phi),
    }
    if brute and 12 ** voices <= 30000:
        combos = list(itertools.product(*[range(12) for _ in range(voices)]))
        best, nes = None, []
        for combo in combos:
            p = [S[i][combo[i]] for i in range(voices)]
            ph = potential(p, nres, w1, w2)
            best = ph if best is None or ph < best else best
            if is_ne(p, S, nres, w1, w2):
                nes.append(ph)
        nes.sort()
        out["opt"] = best
        out["ne_count"] = len(nes)
        out["poa_worst"] = nes[-1] / best if nes else float("nan")
        out["poa_mean"] = statistics.mean(nes) / best if nes else float("nan")
    return out


def maxload(prof, nres):
    return max(loads(prof, nres))


print("== A. validity of the potential (descent + termination) ==")
a = experiment(4, 16, 4)
print(a)

print("\n== B. price of anarchy vs congestion pressure (V voices, 3 bands, 8 slots) ==")
for V in (2, 3, 4, 5):
    r = experiment(3, 8, V, trials=30)
    if "opt" in r:
        print(f"V={V}  resources={r['resources']}  NE={r['ne']}  "
              f"sweeps mean/max={r['sweeps_mean']:.2f}/{r['sweeps_max']}  "
              f"Phi(OPT)={r['opt']:.2f}  PoA worst={r['poa_worst']:.3f} "
              f"mean={r['poa_mean']:.3f}  pure-NE count={r['ne_count']}")
    else:
        print(f"V={V}  resources={r['resources']}  NE={r['ne']}  "
              f"sweeps mean/max={r['sweeps_mean']:.2f}/{r['sweeps_max']}  "
              f"(brute force skipped: 12^{V} profiles)")

print("\n== B2. same, scarce registers (2 bands) and steep congestion (w2=3) ==")
for V in (3, 4):
    r = experiment(2, 8, V, trials=30, w2=3.0)
    print(f"V={V}  resources={r['resources']}  NE={r['ne']}  "
          f"sweeps mean/max={r['sweeps_mean']:.2f}/{r['sweeps_max']}  "
          f"Phi(OPT)={r['opt']:.2f}  PoA worst={r['poa_worst']:.3f} "
          f"mean={r['poa_mean']:.3f}  pure-NE count={r['ne_count']}")

print("\n== C. hocket: load spreading, converged vs random ==")
for V in (3, 4, 5):
    S, res, w1, w2 = build(3, 8, V, 7)
    nres = len(res)
    rng = random.Random(11)
    conv = [maxload(brd(S, nres, w1, w2, rng)[0], nres) for _ in range(60)]
    rnd = [maxload([rng.choice(S[i]) for i in range(V)], nres) for _ in range(60)]
    print(f"V={V}  max per-resource load: equilibrium={statistics.mean(conv):.2f} "
          f"random={statistics.mean(rnd):.2f}")

print("\n== D. logit / quantal-response rationality dial (V=4, 4 bands) ==")
S, res, w1, w2 = build(4, 16, 4, 7)
nres = len(res)
rng = random.Random(3)
prof = brd(S, nres, w1, w2, rng)[0]
for lam in (0.0, 0.25, 0.5, 1.0, 2.0, 5.0, 20.0):
    ent = 0.0
    for i in range(4):
        cs = [cost(i, prof, s, nres, w1, w2) for s in S[i]]
        m = min(cs)
        w = [math.exp(-lam * (c - m)) for c in cs]
        Z = sum(w)
        ent += -sum((x / Z) * math.log(x / Z) for x in w if x > 0)
    print(f"lambda={lam:5.2f}  strategy entropy={ent:.3f} nats")
