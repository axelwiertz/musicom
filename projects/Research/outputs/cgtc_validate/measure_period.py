"""Measure true preperiod/period of Dawson's Kayles Grundy sequence (empirical)."""
from functools import lru_cache

def mex(S):
    s = set(S); m = 0
    while m in s: m += 1
    return m

@lru_cache(maxsize=None)
def dawsons(n):
    if n <= 0: return 0
    return mex(dawsons(i) ^ dawsons(n - i - 2) for i in range(n - 1))

N = 400
dq = [dawsons(n) for n in range(N)]

# find period p such that seq is periodic with period p from index pre onward
found = None
for pre in range(0, 200):
    for p in range(1, 120):
        if all(dq[i] == dq[i + p] for i in range(pre, N - p)):
            found = (pre, p)
            break
    if found:
        break
print("measured (preperiod, period):", found)
# verify 34 specifically at various preperiods
for pre in range(45, 60):
    ok = all(dq[i] == dq[i + 34] for i in range(pre, N - 34))
    print(f"period 34 from index {pre}: {ok}")
# spot-check some known literature values
print("g(50..70):", dq[50:71])
print("g(100..120):", dq[100:121])
print("g(150..170):", dq[150:171])
print("g(200..220):", dq[200:221])
