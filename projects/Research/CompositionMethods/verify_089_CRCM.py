"""Final verification for Method 089 CRCM (Change-Ringing Combinatorial Method).
All claims below are checked by execution, not assumed.
"""
from collections import Counter

N = 6
ROUNDS = tuple(range(1, N + 1))


def is_adjacent_transposition(a, b):
    """b = a composed with disjoint adjacent swaps only (change-ringing law)."""
    diffs = [i for i in range(len(a)) if a[i] != b[i]]
    if not diffs:
        return False
    runs, cur = [], [diffs[0]]
    for d in diffs[1:]:
        if d == cur[-1] + 1:
            cur.append(d)
        else:
            runs.append(cur)
            cur = [d]
    runs.append(cur)
    for r in runs:
        if len(r) % 2 != 0:
            return False
        for k in range(0, len(r), 2):
            i0, i1 = r[k], r[k + 1]
            if i1 != i0 + 1 or a[i0] != b[i1] or a[i1] != b[i0]:
                return False
    return True


def plain_bob_minor_course():
    """Plain Bob Minor plain course. All bells plain-hunt; every 12th change
    (treble lying at lead) positions 1-2 hold while (3,4) and (5,6) dodge."""
    rows = [ROUNDS]
    for step in range(60):
        nxt = list(rows[-1])
        slot = step % 12
        if slot < 11:
            pairs = [(0, 1), (2, 3), (4, 5)] if slot % 2 == 0 else [(1, 2), (3, 4)]
        else:
            pairs = [(2, 3), (4, 5)]
        for i, j in pairs:
            nxt[i], nxt[j] = nxt[j], nxt[i]
        rows.append(tuple(nxt))
    return rows


if __name__ == "__main__":
    rows = plain_bob_minor_course()

    # 1. legality + uniqueness + closure
    adj = all(is_adjacent_transposition(rows[i], rows[i + 1]) for i in range(60))
    uniq = len(set(rows[:-1])) == 60
    rounds_end = rows[-1] == ROUNDS
    print(f"[1] adjacent-swaps-only={adj}  60-unique-rows={uniq}  returns-to-rounds={rounds_end}")
    assert adj and uniq and rounds_end

    # 2. lead-head cycle
    lh = ["".join(map(str, rows[i])) for i in range(0, 61, 12)]
    print(f"[2] lead heads: {lh}")
    assert lh == ["123456", "135264", "156342", "164523", "142635", "123456"]

    # 3. treble plain-hunt ostinato
    tp = [r.index(1) + 1 for r in rows[:12]]
    print(f"[3] treble positions lead 1: {tp}")
    assert tp == [1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1]

    # 4. half-lead mirror symmetry (plain-hunt half); lead-end rows break it
    mirror = all(rows[6 + k] == tuple(reversed(rows[k])) for k in range(0, 6))
    print(f"[4] half-lead mirror rows[6+k]==reverse(rows[k]) k=0..5: {mirror}")
    assert mirror

    # 5. per-bell voice leading: every bell moves at most one POSITION per blow
    #    (=> at most one scale step per blow in the position-degree mapping)
    leaps = 0
    for b in range(1, 7):
        p = [row.index(b) + 1 for row in rows[:-1]]
        leaps += sum(1 for x, y in zip(p, p[1:]) if abs(x - y) > 1)
    print(f"[5] per-bell position jumps >1 across whole course: {leaps}")
    assert leaps == 0

    # 6. per-bell degree-path interval histogram (bell k -> degree 6-k, C major)
    deg = {b: 6 - b for b in range(1, 7)}
    MAJ = [0, 2, 4, 5, 7, 9, 11]
    hist = Counter()
    for b in range(1, 7):
        p = [deg[row.index(b) + 1] for row in rows[:-1]]
        for a, c in zip(p, p[1:]):
            ic = abs(MAJ[a] - MAJ[c]) % 12
            hist[min(ic, 12 - ic)] += 1
    tot = sum(hist.values())
    print(f"[6] per-bell degree-path IC histogram (360 steps): {dict(sorted(hist.items()))}")
    print(f"    unisons {hist[0]/tot:.1%} | 2nds {hist[1]+hist[2]}/{tot} = {(hist[1]+hist[2])/tot:.1%} | "
          f"3rds {hist[3]/tot:.1%} | leaps>=ic4 {(hist[4]+hist[5])/tot:.1%}")

    # 7. Mapping A (authentic peal): verticalities = change rows; count distinct
    vert = len(set(rows[:-1]))
    print(f"[7] distinct vertical sonority sets (mapping A): {vert}/60")

    print("first 12 changes:", [" ".join(map(str, r)) for r in rows[:12]])
