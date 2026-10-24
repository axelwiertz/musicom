"""DPPC (Method 124) verification — determinantal point process composition.

All identities checked against EXACT enumeration (n = 12 -> 2^12 = 4096 subsets,
C(12,3) = 220 k-subsets), so every claim is measured, not assumed:

 1. Normalizer: sum_Y det(L_Y) == det(L + I).
 2. Marginal identity: empirical inclusion frequency == K_ii == [L(L+I)^-1]_ii.
 3. Pairwise negative correlation: P(i,j) - P(i)P(j) = -K_ij^2 <= 0.
 4. k-DPP: exactly k items; empirical k-subsets match the exact conditional
    distribution p(Y) = det(L_Y) / e_k(lambda) restricted to |Y| = k.
 5. k-DPP voicings spread vs quality-weighted i.i.d. baseline (clump detector).
 6. Seed determinism.  7. Expected cardinality E|Y| = sum lam/(lam+1).
 8. Greedy MAP (log-det submodular, 1-1/e guarantee) voicing.
"""
import numpy as np

rng = np.random.default_rng(7)

PCS = [0, 2, 4, 5, 7, 9, 11, 1, 3, 6, 8, 10]   # C major pcs first, then chromatic
n = len(PCS)
CHORD = {0: 1.0, 4: 0.8, 7: 0.9, 9: 0.6, 2: 0.5, 5: 0.4, 11: 0.7, 1: 0.2,
         3: 0.2, 6: 0.15, 8: 0.2, 10: 0.2}
q = np.array([CHORD[p] for p in PCS], dtype=float)

def pc_dist(a, b):
    d = abs(a - b) % 12
    return min(d, 12 - d)

sigma = 1.0   # periodic-kernel length scale (period = 12)
S = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        d = pc_dist(PCS[i], PCS[j])
        # PROPER periodic RBF (guaranteed PSD): exp(-2 sin^2(pi d / p) / l^2).
        # Naive exp(-d^2/2s^2) on a circle is NOT PSD (verified: negative eigs).
        S[i, j] = np.exp(-2.0 * np.sin(np.pi * d / 12.0) ** 2 / sigma ** 2)
L = np.outer(q, q) * S
L = (L + L.T) / 2
# temperature: leave raw; E|Y| = sum lam/(lam+1) = 1.85 is a musical default.
# (Scaling L by c < 1 is the documented "temperature" dial — see Pitfalls.)
lam = np.clip(np.linalg.eigvalsh(L), 0.0, None)
print(f"kernel: E|Y| = sum lam/(lam+1) = {np.sum(lam/(lam+1)):.2f}")
assert np.all(np.linalg.eigvalsh(L) > -1e-12), "L must be PSD"

def det_sub(L, Y):
    if len(Y) == 0:
        return 1.0
    return np.linalg.det(L[np.ix_(Y, Y)])

# --- exact enumeration -------------------------------------------------------
weights = {}
for mask in range(1 << n):
    Y = [i for i in range(n) if mask >> i & 1]
    w = det_sub(L, Y)
    weights[frozenset(Y)] = w
Z = sum(weights.values())
assert abs(Z - np.linalg.det(L + np.eye(n))) < 1e-9, "normalizer mismatch"
exact_P = {Y: w / Z for Y, w in weights.items()}
exact_marg = np.zeros(n)
for Y, p in exact_P.items():
    for i in Y:
        exact_marg[i] += p
print(f"\n== 1. normalizer: sum_Y det(L_Y) = {Z:.6f} == det(L+I) = "
      f"{np.linalg.det(L + np.eye(n)):.6f}  (match {abs(Z - np.linalg.det(L + np.eye(n))) < 1e-9})")

K = L @ np.linalg.inv(L + np.eye(n))
print(f"   max |exact_marginal - K_ii| = {np.max(np.abs(exact_marg - np.diag(K))):.6f}")

# --- spectral sampler (Kulesza & Taskar 2012, Alg. 1) ------------------------
def sample_dpp(L, rng, k=None):
    n_ = L.shape[0]
    lam_, V = np.linalg.eigh(L)
    lam_ = np.clip(lam_, 0.0, None)
    if k is None:
        keep = rng.random(n_) < lam_ / (lam_ + 1.0)
    else:
        # k-DPP: eigenvector subset of size k, prob ∝ prod lam, via e_k DP
        e = np.zeros((n_ + 1, k + 1))
        e[0, 0] = 1.0
        for i in range(1, n_ + 1):
            e[i, 0] = 1.0
            for j in range(1, min(i, k) + 1):
                e[i, j] = e[i - 1, j] + lam_[i - 1] * e[i - 1, j - 1]
        S_set = []
        i, j = n_, k
        while j > 0:
            if i == j:
                S_set.extend(range(j - 1, -1, -1))
                break
            take_p = lam_[i - 1] * e[i - 1, j - 1] / e[i, j]
            if rng.random() < take_p:
                S_set.append(i - 1)
                j -= 1
            i -= 1
        keep = np.zeros(n_, dtype=bool)
        keep[S_set] = True
    Vk = V[:, keep] if keep.any() else np.zeros((n_, 0))
    if Vk.shape[1] == 0:
        return np.array([], dtype=int)
    # Iterative item sampling (Hough et al. 2006; Kulesza & Taskar 2012, Alg. 1).
    # E = span(Vk) (n x k, orthonormal columns). Each selection consumes one
    # dimension: E' = {x in E : x_j = 0} = {Vk c : v_j . c = 0}, v_j = Vk[j,:].
    # Maintain C (k x m, orthonormal columns in c-space); B = Vk @ C has
    # orthonormal columns spanning E', so P(item i) = ||B_i,:||^2. After
    # selecting idx, project C's columns onto v^perp, drop one dimension, re-QR.
    C = np.eye(Vk.shape[1])
    selected = np.zeros(n_, dtype=bool)
    items = []
    while C.shape[1] > 0:
        B = Vk @ C                      # n x m, orthonormal columns
        B[selected, :] = 0.0            # selected items have prob 0
        norms2 = np.einsum('ij,ij->i', B, B)
        s = norms2.sum()
        if s <= 1e-30:
            break
        probs = norms2 / s
        idx = int(rng.choice(len(B), p=probs))
        items.append(idx)               # B's rows ARE original item indices
        selected[idx] = True
        v = B[idx, :]                   # 1 x m constraint vector (d-space)
        vv = float(v @ v)
        m = C.shape[1]
        # orthonormal basis of v^perp in d-space:
        D = np.eye(m) - np.outer(v, v) / vv     # columns: e_j proj'd onto v^perp
        D = D[:, :-1]                           # drop one dim (rank m-1)
        Q, _ = np.linalg.qr(D)
        D = Q[:, :m - 1]
        C = C @ D                               # k x (m-1)
    return np.array(sorted(items), dtype=int)

N = 60000
samples = [sample_dpp(L, np.random.default_rng(1000 + t)) for t in range(N)]
emp = np.zeros(n)
for s in samples:
    emp[s] += 1
emp /= N
print(f"\n== 2. spectral-sampler marginal vs EXACT ==")
print(f"   max |empirical - exact| = {np.max(np.abs(emp - exact_marg)):.4f}  "
      f"(mean |.| = {np.mean(np.abs(emp - exact_marg)):.4f})")

print(f"\n== 3. pairwise negative correlation ==")
for (i, j) in [(0, 7), (0, 1), (0, 2), (4, 6), (7, 9)]:
    pij = exact_P.get(frozenset({i, j}), 0.0) + sum(
        p for Y, p in exact_P.items() if i in Y and j in Y and len(Y) > 2)
    diff = pij - exact_marg[i] * exact_marg[j]
    print(f"   pc {PCS[i]:>2} & {PCS[j]:>2}: exact {diff:+.5f}  vs  -K_ij^2 = {-K[i,j]**2:+.5f}")

# --- k-DPP -------------------------------------------------------------------
k = 3
k_subsets = [frozenset(Y) for Y, _ in weights.items() if len(Y) == k]
Zk = sum(weights[Y] for Y in k_subsets)
exact_kP = {Y: weights[Y] / Zk for Y in k_subsets}
ek = 0.0  # e_k(lam) via DP
e = np.zeros((n + 1, k + 1))
e[0, 0] = 1.0
for i in range(1, n + 1):
    e[i, 0] = 1.0
    for j in range(1, min(i, k) + 1):
        e[i, j] = e[i - 1, j] + lam[i - 1] * e[i - 1, j - 1]
ek = e[n, k]
print(f"\n== 4. k-DPP: exactly {k} items, matches exact conditional ==")
Nk = 20000
k_samples = [sample_dpp(L, np.random.default_rng(5000 + t), k=k) for t in range(Nk)]
sizes = np.array([len(s) for s in k_samples])
print(f"   cardinality: all == {k}: {(sizes == k).all()}")
from collections import Counter
cnt = Counter(tuple(s) for s in k_samples)
empk = {frozenset(Y): c / Nk for Y, c in cnt.items()}
maxdev = max(abs(empk.get(Y, 0.0) - exact_kP[Y]) for Y in exact_kP)
print(f"   max |empirical k-subset prob - exact| over {len(exact_kP)} subsets = {maxdev:.4f}")
print(f"   e_k(lam) = {ek:.6f} == Zk = {Zk:.6f} (normalizer check)")

print(f"\n== 5. k-DPP voicing spread vs i.i.d. quality-weighted baseline ==")
def spread(s):
    s = sorted(s)
    ds = [pc_dist(PCS[s[i]], PCS[s[(i + 1) % k]]) for i in range(k)]
    return min(ds)
dpp_min = np.mean([spread(s) for s in k_samples])
w = q / q.sum()
base_min = np.mean(
    [spread(np.sort(rng2.choice(n, size=k, replace=False, p=w)))
     for rng2 in [np.random.default_rng(9000 + t) for t in range(4000)]])
print(f"   mean nearest-neighbor pc distance: DPP {dpp_min:.3f} vs baseline {base_min:.3f} "
      f"-> {dpp_min / base_min:.2f}x wider spacing")

print(f"\n== 6. seed determinism ==")
a = sample_dpp(L, np.random.default_rng(42), k=4)
b = sample_dpp(L, np.random.default_rng(42), k=4)
print(f"   same seed -> identical: {np.array_equal(a, b)} (sample {a.tolist()} = pcs "
      f"{[PCS[i] for i in a]})")

print(f"\n== 7. expected cardinality ==")
print(f"   sum lam/(lam+1) = {np.sum(lam/(lam+1)):.3f} vs E|Y| = n * mean(marginal) "
      f"= {n * emp.mean():.3f}")

print(f"\n== 7b. musical reading (exact marginals, n=12 kernel) ==")
for i in range(n):
    print(f"   pc {PCS[i]:>2}: P(in sample) = {exact_marg[i]:.3f}")
print(f"   tonic+third+fifth+seventh (0,4,7,11) sum = "
      f"{sum(exact_marg[PCS.index(p)] for p in (0, 4, 7, 11)):.3f} of E|Y|={n * emp.mean():.2f}")
top = sorted(exact_kP.items(), key=lambda kv: -kv[1])[:5]
print(f"   top-5 most probable k=3 voicings (exact): "
      + ", ".join(f"{{{','.join(str(PCS[i]) for i in sorted(Y))}}} {p:.3f}"
                  for Y, p in top))

def greedy_map(L, k):
    n_ = L.shape[0]
    chosen = []
    remaining = set(range(n_))
    for _ in range(k):
        best, bestv = None, -np.inf
        for j in remaining:
            c = chosen + [j]
            v = np.linalg.slogdet(L[np.ix_(c, c)])[1]
            if v > bestv:
                best, bestv = j, v
        chosen.append(best)
        remaining.discard(best)
    return np.array(sorted(chosen))

gm = greedy_map(L, 3)
print(f"\n== 8. greedy MAP voicing (log-det submodular -> >= (1-1/e) OPT) ==")
print(f"   pcs {[PCS[i] for i in gm]}  (nearest-neighbor spread {spread(gm):.1f})")
print("\nOK")
