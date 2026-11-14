#!/usr/bin/env python3
"""Fix double-escaped LaTeX backslashes in the SP-141 section (lines 31424-31499).

BS*2 (backslash backslash) -> BS (single backslash);
BS*4 (case-branch separator) -> BS*2 (LaTeX newline stays doubled);
BS + quote (escaped quote) -> plain quote.
Only the SP-141 section is touched; pre-existing artifacts elsewhere stay.
"""
path = '/opt/data/projects/Research/CompositionMethods/methods_db.md'
lines = open(path, encoding='utf-8').read().split('\n')

BS = chr(92)  # single backslash
lo, hi = 31424, 31499  # 1-indexed inclusive
fixed = 0
for i in range(lo - 1, hi):
    s = lines[i]
    t = s
    t = t.replace(BS * 4, '@@NL@@')   # 4 -> placeholder
    t = t.replace(BS * 2, BS)         # 2 -> 1  (drop one backslash)
    t = t.replace('@@NL@@', BS * 2)   # placeholder -> 2 (LaTeX newline)
    t = t.replace(BS + '"', '"')
    if t != s:
        fixed += 1
    lines[i] = t

open(path, 'w', encoding='utf-8').write('\n'.join(lines))
print(f"fixed {fixed} lines in SP-141 section")
