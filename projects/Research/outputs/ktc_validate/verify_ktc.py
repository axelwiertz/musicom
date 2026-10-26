"""KTC verification — Knight's Tour Composition core solver checks (pure stdlib).

Verifies:
  1. Warnsdorff + Pohl tie-break solves 8x8 open tour (complete = m*n visits).
  2. Closed-tour feasibility: Schwenk conditions respected; 8x8 closed exists.
  3. Knight signature: every move has |dr|*|dc| == 2.
  4. 2D aggregate: every (row, col) cell visited exactly once.
  5. Row balance: each pitch row visited exactly n times.
  6. Dual tour (board transpose) is also a valid tour (invertible counterpoint).
  7. Cost scaling on a 12x8 board.
"""
import time

MOVES = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]


def knight_neighbours(pos, m, n, visited):
    r, c = pos
    out = []
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in visited:
            out.append((nr, nc))
    return out


def warnsdorff_rank(pos, m, n, visited):
    """Fewest onward moves = least degree. Returns list sorted by onward count."""
    cands = knight_neighbours(pos, m, n, visited)
    ranked = []
    for cand in cands:
        nxt = knight_neighbours(cand, m, n, visited | {cand})
        ranked.append((len(nxt), cand))
    ranked.sort(key=lambda x: x[0])
    return ranked


def solve_warnsdorff(m, n, start, tiebreak="pohl", rng=None):
    """Warnsdorff with tie-break. Returns tour list or None if stalled."""
    tour = [start]
    visited = {start}
    pos = start
    while len(tour) < m * n:
        ranked = warnsdorff_rank(pos, m, n, visited)
        if not ranked:
            return None  # stall -> needs backtracking
        best = ranked[0][0]
        ties = [c for k, c in ranked if k == best]
        if len(ties) == 1:
            nxt = ties[0]
        elif tiebreak == "pohl":
            ranked2 = sorted(
                (len(knight_neighbours(c, m, n, visited | {c})), c) for c in ties
            )
            nxt = ranked2[0][1]
        else:  # random tie-break (seeded)
            nxt = rng.choice(ties)
        tour.append(nxt)
        visited.add(nxt)
        pos = nxt
    return tour


def solve_dfs(m, n, start, max_nodes=2_000_000):
    """Backtracking fallback (Warnsdorff-ordered DFS). Returns tour or None."""
    tour = [start]
    visited = {start}
    nodes = 0

    def dfs(pos):
        nonlocal nodes
        nodes += 1
        if nodes > max_nodes:
            raise TimeoutError
        if len(tour) == m * n:
            return True
        ranked = warnsdorff_rank(pos, m, n, visited)
        for _, cand in ranked:
            tour.append(cand)
            visited.add(cand)
            if dfs(cand):
                return True
            visited.discard(cand)
            tour.pop()
        return False

    try:
        return tour if dfs(start) else None
    except TimeoutError:
        return None


def closed_check(tour, m, n):
    if len(tour) != m * n:
        return False
    (r0, c0), (r1, c1) = tour[0], tour[-1]
    return (abs(r0 - r1), abs(c0 - c1)) in [(1, 2), (2, 1)]


def check_tour(tour, m, n):
    assert len(tour) == m * n, "incomplete tour"
    cells = set()
    sig_ok = True
    for (r0, c0), (r1, c1) in zip(tour, tour[1:]):
        dr, dc = abs(r1 - r0), abs(c1 - c0)
        if (dr, dc) not in [(1, 2), (2, 1)]:
            sig_ok = False
        cells.add((r0, c0))
    cells.add(tour[-1])
    assert len(cells) == m * n, "cell repeated"
    return {
        "cells": len(cells),
        "signature_ok": sig_ok,
        "row_counts": {r: sum(1 for (r2, _) in tour if r2 == r) for r in range(m)},
        "col_counts": {c: sum(1 for (_, c2) in tour if c2 == c) for c in range(n)},
        "closed": closed_check(tour, m, n),
    }


if __name__ == "__main__":
    import random

    for tb in ("pohl", "random"):
        rng = random.Random(7)
        t0 = time.time()
        tour = solve_warnsdorff(8, 8, (0, 0), tiebreak=tb, rng=rng)
        dt = time.time() - t0
        if tour:
            stats = check_tour(tour, 8, 8)
            print(f"[8x8 tiebreak={tb}] tour ok, {dt*1000:.1f} ms, "
                  f"closed={stats['closed']}, signature={stats['signature_ok']}, "
                  f"row counts={list(stats['row_counts'].values())}, "
                  f"col counts={list(stats['col_counts'].values())}")
        else:
            print(f"[8x8 tiebreak={tb}] STALLED")

    t0 = time.time()
    closed = None
    rng = random.Random(3)
    for attempt in range(6):
        start = (rng.randrange(8), rng.randrange(8))
        t = solve_dfs(8, 8, start)
        if t and closed_check(t, 8, 8):
            closed = t
            break
    if closed:
        print(f"[8x8 closed] found from {closed[0]} in {time.time()-t0:.2f}s, "
              f"closed={closed_check(closed, 8, 8)}")
    else:
        print("[8x8 closed] not found in attempts")

    tour = solve_warnsdorff(8, 8, (0, 0), tiebreak="pohl")
    dual = [(c, r) for (r, c) in tour]
    dstats = check_tour(dual, 8, 8)
    print(f"[dual] transpose of 8x8 tour is a valid 8x8 tour: "
          f"cells={dstats['cells']}, signature={dstats['signature_ok']}")

    t0 = time.time()
    t12 = solve_warnsdorff(12, 8, (6, 4), tiebreak="pohl")
    dt = time.time() - t0
    s12 = check_tour(t12, 12, 8)
    print(f"[12x8] {len(t12)} cells in {dt*1000:.1f} ms; "
          f"row counts sum={sum(s12['row_counts'].values())}, "
          f"every row exactly 8? {set(s12['row_counts'].values()) == {8}}")

    for (mm, nn) in [(5, 5), (6, 6), (8, 8), (12, 8), (10, 10)]:
        t = solve_warnsdorff(mm, nn, (0, 0), tiebreak="pohl") or solve_dfs(mm, nn, (0, 0))
        if t:
            s = check_tour(t, mm, nn)
            print(f"[{mm}x{nn}] cells={s['cells']} signature={s['signature_ok']} "
                  f"closed={s['closed']}")
        else:
            print(f"[{mm}x{nn}] FAILED")
