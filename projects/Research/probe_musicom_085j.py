# -*- coding: utf-8 -*-
"""Abstract layer dev probe: fixed names min7x/dom7x/maj7x are triads.

min7x/min7y are TRIADS on roots 7/10 (naming: min<root> for triads collides
with tetrad intent). Tetrads exist only as min7{0-11}? NO — check:
standard_patterns appends triads for all 12 roots with prefixes maj/min/dim/aug
then tetrads maj7/min7/dom7 for all roots. So:
  maj7{0-11} = MAJOR-7TH TETRADS, e.g. maj70 = {0,4,7,11}? but earlier probe
  printed maj7 -> [2,7,11] — meaning 'maj7' WITHOUT digit is the 12th triad
  'maj' + root 7? No: 'maj7' parses as maj + root 7 = TRIAD Bb {2,7,11}!!
That is the bug in my probes: pattern ids are PREFIX+ROOT digits, so
'maj7' == maj triad on pc 7, NOT a major-7 tetrad. Tetrad on root 0 =
'maj70'. Same for min7 (min triad on pc 7) vs min70 (min7 tetrad on 0).
"""
from rules.subset_network import standard_patterns
lib = {p.id: p for p in standard_patterns()}
for pid in ("maj0","maj70","maj7","min0","min70","min7","dom70","dom7","dom75"):
    p = lib.get(pid)
    print(pid, sorted(p.subset) if p else "MISSING", round(p.tension,1) if p else "")
