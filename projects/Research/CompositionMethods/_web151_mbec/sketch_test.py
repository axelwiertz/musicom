"""Runs the standalone doc's reference sketch verbatim (extracted from method_151_MBEC.md)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mbec_sketch import Matroid, partition_matroid, greedy_basis, exchange_path, dual

DIM7 = [{0, 3, 6, 9}, {1, 4, 7, 10}, {2, 5, 8, 11}]
M = partition_matroid(DIM7, [1, 1, 1])
B_all = M.bases()
assert len(B_all) == 64, len(B_all)
assert {len(b) for b in B_all} == {3}
print("bases:", len(B_all), "circuits:", len(M.circuits()))
assert len(M.circuits()) == 18, len(M.circuits())   # any 2 notes of one family: C(4,2)*3

w = {pc: ((pc * 7) % 12) / 12.0 for pc in range(12)}
A = greedy_basis(M, w)
assert A in B_all
B = frozenset({0, 4, 8})
assert B in B_all
path = exchange_path(M, A, B)
assert path[0] == A and path[-1] == B
assert all(M.is_indep(p) for p in path)
assert len(path) - 1 == len(A - B) == len(B - A), (len(path) - 1, A, B)
print("greedy basis:", sorted(A), "path length:", len(path) - 1)
Md = dual(M)
print("dual rank of E:", Md.rank(M.E), "= m - r =", 12 - M.rank(M.E))
assert Md.rank(M.E) == 9
print("standalone sketch: OK")
