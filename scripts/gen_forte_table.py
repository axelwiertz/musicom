# -*- coding: utf-8 -*-
"""BUILD-TIME generator for rules/forte_table.py (not imported at runtime).

music21 is the authoritative source of Forte set-class names. This script
enumerates all 220 set classes with the repo's own kernel, matches them to
music21's table by a convention-neutral Tn/TnI key, and emits a literal
Python module so the kernel stays free of any music21 dependency.

Regenerate with:
    /opt/data/micromamba/envs/musicom/bin/python scripts/gen_forte_table.py
"""

import sys
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from rules.set_theory import prime_form, interval_vector  # noqa: E402
from music21.chord import tables as CT  # noqa: E402

CARD_RANGE = range(2, 11)


def set_class_key(pcs):
    """Convention-neutral Tn/TnI-invariant key.

    Lexicographically smallest sorted tuple across all 12 transpositions of
    the set and of its inversion. Independent of which representative a
    given library chooses for a set class — necessary because Forte's own
    normal-order rule differs from the modern Rahn/Straus rule for 6 sets.
    """
    s = sorted(set(p % 12 for p in pcs))
    if not s:
        return ()
    best = None
    for t in range(12):
        for variant in (s, sorted((12 - x) % 12 for x in s)):
            cand = tuple(sorted((x + t) % 12 for x in variant))
            if best is None or cand < best:
                best = cand
    return best


# ---- music21 side -------------------------------------------------------
m21 = {}
for card in CARD_RANGE:
    for idx, entry in enumerate(CT.FORTE[card]):
        if entry is None or idx == 0:
            continue
        key = set_class_key(entry[0])
        assert key not in m21, f"duplicate music21 class {card}-{idx}"
        m21[key] = (card, idx, entry[3], tuple(entry[0]))
print("music21 set classes indexed:", len(m21))

# ---- kernel side --------------------------------------------------------
by_card = {}
for k in CARD_RANGE:
    classes = {}
    for combo in combinations(range(12), k):
        classes.setdefault(tuple(prime_form(list(combo))), None)
    by_card[k] = sorted(classes)
print("kernel set classes:", sum(len(v) for v in by_card.values()))
assert not [pf for k in CARD_RANGE for pf in by_card[k]
            if set_class_key(pf) not in m21], "unmatched kernel classes"

names, diffs = {}, []
for k in CARD_RANGE:
    for pf in by_card[k]:
        card, idx, zidx, m21pf = m21[set_class_key(pf)]
        assert card == k
        names[pf] = f"{card}-Z{idx}" if zidx else f"{card}-{idx}"
        if tuple(pf) != m21pf:
            diffs.append((pf, m21pf, names[pf]))

print(f"Forte/Rahn representative differences: {len(diffs)}")
for pf, m21pf, nm in diffs:
    print(f"   kernel {pf}  vs  Forte {m21pf}   -> {nm}")

# ---- Z-group cross-check ------------------------------------------------
kernel_z = 0
for k in CARD_RANGE:
    groups = {}
    for pf in by_card[k]:
        groups.setdefault(tuple(interval_vector(list(pf))), []).append(pf)
    for icv, pfs in groups.items():
        if len(pfs) > 1:
            kernel_z += 1
            idxs = [m21[set_class_key(p)][1] for p in pfs]
            assert all(m21[set_class_key(p)][2] in idxs for p in pfs), pfs
print("Z-groups verified mutual:", kernel_z)

# ---- emit ---------------------------------------------------------------
out = [
    '# -*- coding: utf-8 -*-',
    '"""Static Forte set-class name table — GENERATED, do not hand-edit.',
    '',
    'Source: music21 %s Forte table, matched against this repo\'s kernel' % CT.__name__.split(".")[0],
    'enumerated all 220 set classes. Regenerate with:',
    '',
    '    /opt/data/micromamba/envs/musicom/bin/python scripts/gen_forte_table.py',
    '',
    'Keys are the repo kernel\'s canonical prime forms (modern Rahn/Straus',
    'normal order), sorted. For 6 set classes the Forte original picks a',
    'different representative; the name is authoritative, the key is ours',
    '(see the discrepancy list in scripts/gen_forte_table.py output).',
    '',
    'Pure data: no imports, no side effects. Import-safe and dependency-free.',
    '"""',
    '',
    '# prime form (as tuple) -> Forte name',
    'FORTE_NAMES = {',
]
for k in CARD_RANGE:
    out.append(f"    # --- cardinality {k} ({len(by_card[k])} classes) ---")
    for pf in by_card[k]:
        tup = ", ".join(str(p) for p in pf)
        if len(pf) == 1:
            tup += ","
        out.append(f"    ({tup}): {names[pf]!r},")
out.append("}")
out.append("")
out.append("# Forte name -> prime form tuple (inverse of the above)")
out.append("FORTE_PRIME_FORMS = {v: k for k, v in FORTE_NAMES.items()}")
out.append("")
out.append("__all__ = [\"FORTE_NAMES\", \"FORTE_PRIME_FORMS\"]")
out.append("")

dest = REPO / "rules" / "forte_table.py"
dest.write_text("\n".join(out))
print(f"\nwrote {dest} ({len(out)} lines)")
