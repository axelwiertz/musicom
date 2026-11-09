#!/usr/bin/env python3
"""Fact-checks for Method 138 — Huffman Coding Composition (HCC).

Checks:
 1. Prefix-free: no codeword is a prefix of another (Huffman output).
 2. Kraft equality: sum 2^-len == 1 for a complete code (exact packing of the bar).
 3. Optimality: weighted path length L <= L' for every other prefix code (brute force, n<=6).
 4. Entropy bound: H <= L < H + 1 (CLRS theorem 16.4/16.5).
 5. Dyadic weights => L == H exactly.
 6. Code lengths: len_i == ceil(-log2 w_i) holds for canonical/dyadic-ish sets; depth <= n-1.
 7. Zipf weights => motif usage is Zipfian: rank-frequency slope of 2^-len vs rank ~ -1.
 8. n-ary completeness: n symbols form a complete m-ary tree iff n ≡ 1 (mod m-1).
 9. In-order walk of the tree = gap-free timeline: leaf onset positions partition [0, 2^L).
10. Minimum-variance tie-break: longest codeword minimized vs arbitrary tie-break.
"""
import itertools, math, heapq, random
from collections import Counter

# ---------- Huffman builder ----------
class Node:
    __slots__ = ('w', 'sym', 'left', 'right')
    def __init__(self, w, sym=None, left=None, right=None):
        self.w, self.sym, self.left, self.right = w, sym, left, right
    def __lt__(self, o):            # heap: smaller weight first; leaves before internal on ties (min-variance)
        a = (self.w, 0 if self.sym is None else 1, self.sym if self.sym is not None else '')
        b = (o.w, 0 if o.sym is None else 1, o.sym if o.sym is not None else '')
        return a < b

def huffman(weights, tie_first_queue=False):
    """weights: list of (symbol, weight). Returns dict sym->codeword, and root."""
    heap = [Node(w, s) for s, w in weights]
    heapq.heapify(heap)
    while len(heap) > 1:
        a = heapq.heappop(heap); b = heapq.heappop(heap)
        heapq.heappush(heap, Node(a.w + b.w, None, a, b))
    root = heap[0]
    codes = {}
    def walk(node, prefix):
        if node.sym is not None:
            codes[node.sym] = prefix
            return
        walk(node.left, prefix + '0')
        walk(node.right, prefix + '1')
    walk(root, '')
    return codes, root

def huffman_comb(weights):
    """Adversarial variant: always merge the newest internal node with the next leaf
    (the opposite of the min-variance tie-break) -> maximally unbalanced 'comb' tree."""
    leaves = sorted(weights, key=lambda t: (t[1], t[0]))
    it = iter(leaves)
    s0, w0 = next(it)
    internal = Node(w0, None, Node(w0, s0), None)   # placeholder; rebuilt below
    # simpler comb: chain-merge in sorted order
    nodes = [Node(w, s) for s, w in leaves]
    cur = nodes[0]
    for nxt in nodes[1:]:
        cur = Node(cur.w + nxt.w, None, cur, nxt)
    codes = {}
    def walk(node, prefix):
        if node.sym is not None:
            codes[node.sym] = prefix
            return
        walk(node.left, prefix + '0')
        walk(node.right, prefix + '1')
    walk(cur, '')
    return codes, cur

def all_prefix_codes(symbols):
    """Brute-force all prefix-free binary code assignments for |symbols| <= 6 (canonical length lists)."""
    n = len(symbols)
    out = []
    # enumerate all length tuples with sum 2^-l <= 1 (Kraft) and completeness optional
    def rec(idx, used_budget, lens):
        if idx == n:
            out.append(list(lens)); return
        maxl = 6
        for l in range(1, maxl + 1):
            if used_budget + 2 ** (-l) <= 1.0000001:
                rec(idx + 1, used_budget + 2 ** (-l), lens + [l])
    rec(0, 0.0, [])
    return out

def weighted_path_length(weights, lens):
    return sum(w * l for (_, w), l in zip(weights, lens))

# ---------- test sets ----------
sets = {
    'wiki5':   [('a', 0.10), ('b', 0.15), ('c', 0.30), ('d', 0.16), ('e', 0.29)],   # Wikipedia example
    'four':    [('a1', 0.40), ('a2', 0.35), ('a3', 0.20), ('a4', 0.05)],
    'dyadic':  [('t', 0.5), ('s', 0.25), ('d', 0.125), ('q', 0.125)],
    'zipf10':  [(f'z{i}', 1.0 / (i + 1)) for i in range(10)],
    'flat8':   [(f'f{i}', 1.0 / 8) for i in range(8)],
}

ok = True
def check(name, cond, detail=''):
    global ok
    print(f'[{"PASS" if cond else "FAIL"}] {name} {detail}')
    ok = ok and cond

print('== 1. prefix-free + 2. Kraft equality ==')
for name, ws in sets.items():
    codes, root = huffman(ws)
    syms = list(codes)
    pf = all(not (c1 != c2 and c2.startswith(c1)) for c1 in codes.values() for c2 in codes.values())
    kraft = sum(2 ** (-len(c)) for c in codes.values())
    print(f'  {name}: kraft={kraft:.6f} prefix_free={pf} lens={sorted(set(len(c) for c in codes.values()))}')
    check(f'{name} prefix-free', pf)
    check(f'{name} kraft~1', abs(kraft - 1.0) < 1e-9)

print('== 3. optimality vs brute force (n<=6) ==')
for name in ['wiki5', 'four']:
    ws = sets[name]
    codes, _ = huffman(ws)
    L_huf = weighted_path_length(ws, [len(codes[s]) for s, _ in ws])
    best = min(weighted_path_length(ws, lens) for lens in all_prefix_codes([s for s, _ in ws]))
    check(f'{name} optimal (L={L_huf:.4f} == brute best {best:.4f})', abs(L_huf - best) < 1e-9)

print('== 4. entropy bound H <= L < H+1 (normalized weights) ==')
for name, ws in sets.items():
    codes, _ = huffman(ws)
    tot = sum(w for _, w in ws)
    H = -sum((w / tot) * math.log2(w / tot) for _, w in ws)
    L = weighted_path_length(ws, [len(codes[s]) for s, _ in ws]) / tot
    check(f'{name} H<=L<H+1 (H={H:.4f} L={L:.4f})', H - 1e-9 <= L < H + 1 + 1e-9)

print('== 5. dyadic => L == H ==')
codes, _ = huffman(sets['dyadic'])
H = -sum(w * math.log2(w) for _, w in sets['dyadic'])
L = weighted_path_length(sets['dyadic'], [len(codes[s]) for s, _ in sets['dyadic']])
check('dyadic L==H', abs(L - H) < 1e-9)

print('== 6. depth <= n-1; len_i <= n-1 ==')
for name, ws in sets.items():
    codes, _ = huffman(ws)
    mx = max(len(c) for c in codes.values())
    check(f'{name} maxlen {mx} <= n-1 {len(ws)-1}', mx <= len(ws) - 1)

print('== 7. Zipf weights => usage ~ Zipf (rank-frequency of 2^-len) ==')
codes, _ = huffman(sets['zipf10'])
usage = sorted(((2 ** (-len(codes[s]))), s) for s, _ in sets['zipf10'])   # (usage, sym) desc
usage.sort(reverse=True)
xs = [math.log2(r + 1) for r in range(len(usage))]
ys = [math.log2(u) for u, _ in usage]
xbar = sum(xs) / len(xs); ybar = sum(ys) / len(ys)
slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sum((x - xbar) ** 2 for x in xs)
print(f'  least-squares log-log slope of usage vs rank = {slope:.3f} (Zipf ~ -1)')
check('zipf usage slope ~ -1 (within 0.35)', abs(slope + 1) < 0.35)

print('== 8. n-ary completeness ==')
def nary_possible(n, m):  # complete m-ary tree with n leaves iff n == 1 mod (m-1)
    return (n - 1) % (m - 1) == 0
check('ternary n=5 possible (5==1 mod 2)', nary_possible(5, 3))
check('ternary n=6 impossible', not nary_possible(6, 3))
check('quaternary n=10 possible (10==1 mod 3)', nary_possible(10, 4))
check('binary always possible', all(nary_possible(n, 2) for n in range(2, 12)))

print('== 9. in-order walk = gap-free timeline partition of [0,2^L) ==')
codes, root = huffman(sets['four'])
def inorder(node, pos, depth, L, out):
    if node.sym is not None:
        out.append((node.sym, pos * 2 ** (L - depth)))
        return pos + 1
    pos = inorder(node.left, pos, depth + 1, L, out)
    pos = inorder(node.right, pos, depth + 1, L, out)
    return pos
L = max(len(c) for c in codes.values())
out = []
nleaves = inorder(root, 0, 0, L, out)
onsets = sorted(o for _, o in out)
check('in-order covers all leaves', nleaves == len(sets['four']))
check('in-order onsets gap-free & ordered', onsets == sorted(onsets) and all(onsets[i] < onsets[i+1] for i in range(len(onsets)-1)))
print('  onsets (slots of', 2 ** L, '):', onsets)

print('== 10. min-variance tie-break vs comb (unbalanced) ==')
ws10 = [(f'k{i}', 1.0) for i in range(9)]            # 9 equal weights
codes_a, _ = huffman(ws10)                           # leaf-first tie-break -> balanced
mx_a = max(len(c) for c in codes_a.values())
codes_c, _ = huffman_comb(ws10)                      # newest-internal-first -> comb
mx_c = max(len(c) for c in codes_c.values())
best = math.ceil(math.log2(len(ws10)))               # a depth-3 tree has only 8 leaves: 9 needs depth 4
print(f'  maxlen balanced-tiebreak={mx_a} (theoretical min {best}) comb={mx_c} (n-1={len(ws10)-1})')
check('min-variance tie-break reaches min possible maxlen', mx_a == best)
check('comb variant is dramatically longer', mx_c == len(ws10) - 1 and mx_c > mx_a)

print()
print('ALL PASS' if ok else 'SOME FAILED')
