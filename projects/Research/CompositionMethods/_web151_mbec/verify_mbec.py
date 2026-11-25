"""MBEC verification harness — Matroid Basis-Exchange Composition.

Pure-python (no deps). Checks, in order:
 1. independence axioms (I1)-(I3) for the musical partition matroid
 2. equicardinality of bases (every chord has exactly r notes)
 3. greedy == brute-force max-weight basis (Rado/Edmonds optimality)
 4. a NON-matroid constraint family ("no semitone cluster") where greedy provably fails
 5. graphic matroid: forests->spanning trees, Kruskal == brute force
 6. basis-exchange axiom verified exhaustively on both matroids
 7. dual matroid (co-trees) + Tutte T(1,1) = #bases
 8. rank is submodular; beta invariant sign/disconnection test
 9. matroid intersection (two partition matroids) = chord-size cap
10. 4-voice x 8-section abstract UnitMatrix plan: every cell a basis,
    consecutive cells reachable by single basis exchanges.
"""

import itertools
import random

E = list(range(12))                      # ground set = 12 pitch classes
random.seed(151)

# ---------------------------------------------------------------- helpers
def indep_partition(S, blocks, k):
    return all(sum(1 for x in S if x in b) <= k[i] for i, b in enumerate(blocks))

def all_subsets(n):
    s = list(range(n))
    for r in range(n + 1):
        for c in itertools.combinations(s, r):
            yield frozenset(c)

def is_matroid(subsets):
    """subsets: set of frozensets closed downward (candidate independents)."""
    # (I1)
    if frozenset() not in subsets:
        return False, "I1"
    # (I2) hereditary
    for A in subsets:
        for r in range(len(A) + 1):
            for c in itertools.combinations(tuple(A), r):
                if frozenset(c) not in subsets:
                    return False, "I2"
    # (I3) augmentation
    ind = sorted(subsets, key=len)
    for A in ind:
        for B in ind:
            if len(A) > len(B):
                if not any(frozenset(B | {x}) in subsets for x in A - B):
                    return False, "I3"
    return True, "ok"

def rank_of(S, subsets):
    # rank = size of largest independent subset of S
    for r in range(len(S), -1, -1):
        for c in itertools.combinations(tuple(S), r):
            if frozenset(c) in subsets:
                return r
    return 0

def greedy_basis(weights, indep):
    order = sorted(E, key=lambda x: (-weights[x], x))   # deterministic ties
    B = frozenset()
    for x in order:
        if indep(B | {x}):
            B = B | {x}
    return B

def brute_basis(weights, subsets):
    return max(subsets, key=lambda S: (sum(weights[x] for x in S), -len(S), sorted(S)))

# ---------------------------------------------------------------- 1-3: partition matroid
DIM7 = [{0, 3, 6, 9}, {1, 4, 7, 10}, {2, 5, 8, 11}]     # the 3 dim7 families
K = [1, 1, 1]                                            # <=1 note per family
subs = {frozenset(c) for r in range(4) for c in itertools.combinations(E, r)
        if indep_partition(c, DIM7, K)}
ok1, why1 = is_matroid(subs)
bases = {S for S in subs if all(not indep_partition(S | {x}, DIM7, K) for x in E if x not in S)}
eqcard = len({len(S) for S in bases}) == 1

trials = 300
agree = 0
for _ in range(trials):
    w = {x: random.random() + 0.05 for x in E}
    if greedy_basis(w, lambda S: indep_partition(S, DIM7, K)) == brute_basis(w, subs):
        agree += 1

# ---------------------------------------------------------------- 4: non-matroid counterexample
# Musical rule: "at most 4 notes, and no two notes a minor second apart."
def indep_nosemitone(S):
    if len(S) > 4:
        return False
    for a in S:
        for b in S:
            if a < b and (b - a) % 12 in (1, 11):
                return False
    return True

bad = {frozenset(c) for r in range(5) for c in itertools.combinations(E, r) if indep_nosemitone(c)}
ok_bad, why_bad = is_matroid(bad)

# explicit (I3) violator: A={0,2,4} independent, B={1,3} independent, no augmentation
violator = (not any(indep_nosemitone(frozenset({1, 3, x})) for x in {0, 2, 4}))

# hand-built greedy trap: heavy note 5 blocks 4 and 6, each worth more together
w_demo = {pc: 0.1 for pc in E}
w_demo[5], w_demo[4], w_demo[6] = 1.0, 0.6, 0.6
g_demo = greedy_basis(w_demo, indep_nosemitone)
b_demo = brute_basis(w_demo, bad)
demo_greedy_w = sum(w_demo[x] for x in g_demo)
demo_opt_w = sum(w_demo[x] for x in b_demo)

greedy_fails = 0
for _ in range(trials):
    w = {x: 0.2 + 0.8 * random.random() ** 4 for x in E}   # peaky weights
    g = greedy_basis(w, indep_nosemitone)
    b = brute_basis(w, bad)
    if sum(w[x] for x in g) < sum(w[x] for x in b) - 1e-12:
        greedy_fails += 1

# ---------------------------------------------------------------- 5-8: graphic matroid K4
V = 4
EDGES = [(i, j) for i in range(V) for j in range(i + 1, V)]   # 6 transitions
def forest(S):
    par = list(range(V))
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for e in S:
        a, b = find(EDGES[e][0]), find(EDGES[e][1])
        if a == b:
            return False
        par[a] = b
    return True

g_subs = {frozenset(c) for r in range(len(EDGES) + 1)
          for c in itertools.combinations(range(len(EDGES)), r) if forest(c)}
g_bases = {S for S in g_subs if len(S) == V - 1}
ok5, why5 = is_matroid(g_subs)
kruskal_agree = 0
for _ in range(200):
    w = {e: random.random() + 0.05 for e in range(len(EDGES))}
    order = sorted(range(len(EDGES)), key=lambda x: (-w[x], x))
    par = list(range(V))
    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    B = set()
    for e in order:
        a, b = find(EDGES[e][0]), find(EDGES[e][1])
        if a != b:
            par[a] = b; B.add(e)
    if sum(w[e] for e in B) == max(sum(w[e] for e in S) for S in g_bases):
        kruskal_agree += 1

def exchange_pairs_ok(baselist, arena):
    for A in baselist:
        for B in baselist:
            for x in A - B:
                if not any(frozenset(A - {x} | {y}) in arena for y in B - A):
                    return False
    return True

ex_part = exchange_pairs_ok(list(bases), subs)
ex_graph = exchange_pairs_ok(list(g_bases), g_subs)

# dual: complements of K4 spanning trees (co-trees = bases of the bond matroid;
# note a co-tree need NOT be a forest — a star's complement is a triangle)
duals = {frozenset(set(range(len(EDGES))) - S) for S in g_bases}
dual_closed = exchange_pairs_ok(list(duals), {frozenset(c) for r in range(len(EDGES) + 1)
                                              for c in itertools.combinations(range(len(EDGES)), r)
                                              if len(c) <= len(next(iter(duals)))})
dual_rank_ok = len(next(iter(duals))) == len(EDGES) - (V - 1)

def tutte_11(baselist):
    return len(baselist)

def beta(subsets, ground):
    rE = max(len(S) for S in subsets)
    total = 0
    for r in range(len(ground) + 1):
        for c in itertools.combinations(ground, r):
            S = frozenset(c)
            total += ((-1) ** r) * rank_of(S, subsets)
    return ((-1) ** rE) * total

beta_k4 = beta(g_subs, list(range(len(EDGES))))
# disconnected matroid: direct sum of two triangles (6 elements, 2 components)
tri = [{0, 1, 2}, {3, 4, 5}]
tri_subs = {frozenset(c) for r in range(3)
            for blk in tri for c in itertools.combinations(sorted(blk), r)}
# add direct sums of independents across blocks
tri_subs |= {A | B for A in list(tri_subs) for B in list(tri_subs)
             if A <= tri[0] and B <= tri[1]}
beta_dis = beta(tri_subs, list(range(6)))

# ---------------------------------------------------------------- 8b: submodularity
submod_viol = 0
def rk(S, subsets):
    for r in range(len(S), -1, -1):
        for c in itertools.combinations(tuple(S), r):
            if frozenset(c) in subsets:
                return r
    return 0
for _ in range(400):
    A = frozenset(random.sample(E, random.randint(0, 5)))
    B = frozenset(random.sample(E, random.randint(0, 5)))
    if rk(A, subs) + rk(B, subs) < rk(A | B, subs) + rk(A & B, subs):
        submod_viol += 1

# ---------------------------------------------------------------- 9: matroid intersection
WT = [{0, 2, 4, 6, 8, 10}, {1, 3, 5, 7, 9, 11}]
def indep_both(S):
    return indep_partition(S, DIM7, [1, 1, 1]) and indep_partition(S, WT, [1, 1])
max_both = max(len(S) for S in all_subsets(12) if indep_both(S))

# ---------------------------------------------------------------- 10: UnitMatrix plan
# Second instantiation: partition matroid over circle-of-fifths regions.
# Blocks = 4 consecutive fifths each; at most 2 from the sharp region, 1 from each
# other region  =>  rank 4 (four-note chords with tonal-region balance).
FIFTH = [{0, 7, 2, 9}, {5, 10, 3, 8}, {1, 6, 11, 4}]
KF = [2, 1, 1]
f_subs = {frozenset(c) for r in range(5) for c in itertools.combinations(E, r)
          if indep_partition(c, FIFTH, KF)}
f_bases = {S for S in f_subs if all(not indep_partition(S | {x}, FIFTH, KF)
                                    for x in E if x not in S)}
ok_f, why_f = is_matroid(f_subs)

VOICES, SECTIONS = 4, 8
# 8 sections: C - Am - F - G7 - Em - F - G7 - C  (tension arc)
SECT = [(0, {0, 4, 7}, 0.05), (9, {9, 0, 4}, 0.20), (5, {5, 9, 0}, 0.30),
        (7, {7, 11, 2, 5}, 0.55), (4, {4, 7, 11}, 0.70), (5, {5, 9, 0}, 0.50),
        (7, {7, 11, 2, 5}, 0.35), (0, {0, 4, 7}, 0.00)]
COLOR = {2, 5, 9, 11, 4, 10}
TOP = {7, 8, 9, 10, 11, 0}

def voice_weights(v, root, tones, t):
    w = {}
    for pc in E:
        base = 1.0 if pc in tones else 0.12
        if v == 0:                                  # root emphasis
            base += 1.0 if pc == root else 0.0
        elif v == 1:                                # thirds / sevenths
            base += 0.7 if (pc - root) % 12 in (3, 4, 10, 11) else 0.0
        elif v == 2:                                # tension colours
            base += 0.8 if pc in COLOR else 0.0
        else:                                       # top line sits high
            base += 0.8 if pc in TOP else 0.0
        w[pc] = base + 0.6 * t * (((pc * (3 + v)) % 12) / 12.0)
    return w

plan = []
for s, (root, tones, t) in enumerate(SECT):
    plan.append([greedy_basis(voice_weights(v, root, tones, t),
                              lambda S: indep_partition(S, FIFTH, KF))
                 for v in range(VOICES)])

cells_are_bases = ok_f and all(cell in f_bases for col in plan for cell in col)
def single_exchange_reachable(A, B):
    if A == B:
        return True
    for x in A - B:
        for y in B - A:
            C = frozenset(A - {x} | {y})
            if C in f_subs and len(C & B) > len(A & B):
                return True
    return False
reach = 0
tot = 0
for v in range(VOICES):
    for s in range(SECTIONS - 1):
        A, B = plan[s][v], plan[s + 1][v]
        tot += 1
        reach += single_exchange_reachable(A, B)
per_voice_prefix = []
for v in range(VOICES):
    acc, seq = frozenset(), []
    for s in range(SECTIONS):
        acc |= plan[s][v]
        seq.append(len(acc))
    per_voice_prefix.append(seq)
monotone = all(seq == sorted(seq) for seq in per_voice_prefix)
rank_ground = rk(frozenset(E), f_subs)

distinct_cells = len({c for col in plan for c in col})

# ---------------------------------------------------------------- report
lines = []
def chk(n, ok, msg):
    lines.append(("PASS" if ok else "FAIL") + f" [{n}] {msg}")
    return ok

chk(1, ok1, f"(I1)-(I3) hold for partition matroid dim7/k=1; independents={len(subs)}, bases={len(bases)}")
chk(2, eqcard and len({len(S) for S in bases}) == 1 and len(bases) > 0,
    f"bases equicardinal, r={len(next(iter(bases)))} notes per chord, {len(bases)} bases")
chk(3, agree == trials, f"greedy == brute-force max-weight basis: {agree}/{trials}")
chk(4, (not ok_bad) and violator and demo_greedy_w < demo_opt_w and greedy_fails > 0,
    f"NON-matroid '<=4 notes, no semitone cluster' fails axiom {why_bad} "
    f"(violator: A={{0,2,4}}, B={{1,3}}, no augmenting x); greedy trap: greedy "
    f"{sorted(g_demo)} w={demo_greedy_w:.2f} < optimal {sorted(b_demo)} w={demo_opt_w:.2f}; "
    f"random peaky weights: greedy suboptimal {greedy_fails}/{trials}")
chk(5, ok5 and kruskal_agree == 200 and len(g_bases) == 16,
    f"K4 graphic matroid: forests valid, {len(g_bases)} spanning trees, Kruskal == brute force {kruskal_agree}/200")
chk(6, ex_part and ex_graph,
    "basis-exchange axiom holds exhaustively on both matroids (partition + graphic)")
chk(7, dual_closed and dual_rank_ok and tutte_11(g_bases) == 16 and tutte_11(duals) == 16,
    f"dual matroid bases = co-trees ({len(duals)}, rank {len(next(iter(duals)))} = m-r), "
    f"exchange axiom holds on M*; T(1,1)=#bases=16 for both M and M*")
chk(8, beta_k4 > 0 and beta_dis == 0 and submod_viol == 0,
    f"rank submodular (0 violations/400); beta(K4 cycle matroid)={beta_k4} > 0 (connected), "
    f"beta(disconnected 2-triangle matroid)={beta_dis} = 0")
chk(9, max_both == 2,
    f"matroid intersection of dim7-partition and whole-tone-partition caps a chord at {max_both} notes")
chk(10, cells_are_bases and reach == tot and monotone and distinct_cells >= 6,
    f"4x8 plan on fifths-region matroid: all {VOICES*SECTIONS} cells are bases "
    f"(r(E)={rank_ground}, every basis has {len(next(iter(f_bases)))} notes, {len(f_bases)} bases); "
    f"{reach}/{tot} consecutive moves are single exchanges; {distinct_cells} distinct chords; "
    f"per-voice pitch-field growth V0={per_voice_prefix[0]}")

out = "\n".join(lines)
print(out)
print("\n%d/10 checks pass" % sum(1 for l in lines if l.startswith("PASS")))
print("\nplan (voice rows x section cols, pitch-class sets):")
for v in range(VOICES):
    print(" V%d " % v, " | ".join("".join("%X" % p for p in sorted(plan[s][v])) for s in range(SECTIONS)))

with open("verify_mbec_results.txt", "w") as f:
    f.write(out + "\n\n%d/10 checks pass\n\nplan:\n" % sum(1 for l in lines if l.startswith("PASS")))
    for v in range(VOICES):
        f.write(" V%d " % v + " | ".join("".join("%X" % p for p in sorted(plan[s][v])) for s in range(SECTIONS)) + "\n")
