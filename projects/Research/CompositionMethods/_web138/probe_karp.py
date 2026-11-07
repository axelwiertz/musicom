import itertools, random
NEG = float('-inf')

def F_table(A, s, forward=True):
    n = len(A)
    F = [[NEG] * n for _ in range(n + 1)]
    if forward:
        F[0][s] = 0
        for k in range(1, n + 1):
            for j in range(n):
                F[k][j] = max((F[k - 1][i] + A[i][j] for i in range(n) if F[k - 1][i] > NEG), default=NEG)
    else:
        F[0][s] = 0
        for k in range(1, n + 1):
            for i in range(n):
                F[k][i] = max((A[i][j] + F[k - 1][j] for j in range(n) if F[k - 1][j] > NEG), default=NEG)
    return F

def variants(A, s=0):
    n = len(A)
    out = {}
    for fwd in (True, False):
        F = F_table(A, s, fwd)
        for mode in ("minmax", "maxmin"):
            cand = []
            for v in range(n):
                if F[n][v] == NEG:
                    continue
                ks = [(F[n][v] - F[k][v]) / (n - k) for k in range(n) if F[k][v] > NEG]
                if not ks:
                    continue
                cand.append((v, max(ks), min(ks)))
            if not cand:
                out[(fwd, mode)] = None
                continue
            out[(fwd, mode)] = (min(c[1] for c in cand) if mode == "minmax"
                                else max(c[2] for c in cand))
    return out

def brute(A):
    n = len(A); best = NEG
    for L in range(1, n + 1):
        for path in itertools.permutations(range(n), L):
            w = sum(A[path[t]][path[(t + 1) % L]] for t in range(L))
            best = max(best, w / L)
    return best

random.seed(11)
score = {}
trials = 0
for _ in range(300):
    n = random.choice([3, 3, 4])
    A = [[random.randint(-6, 9) for _ in range(n)] for _ in range(n)]
    b = brute(A)
    trials += 1
    for k, v in variants(A).items():
        score.setdefault(k, 0)
        if v is not None and abs(v - b) < 1e-9:
            score[k] += 1
print("trials", trials)
for k, c in sorted(score.items(), key=lambda x: -x[1]):
    print(k, c)
