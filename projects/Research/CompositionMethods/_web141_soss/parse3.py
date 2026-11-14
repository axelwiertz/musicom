#!/usr/bin/env python3
"""Extract wiki supersaw section body text."""
import re, html

def strip_html(t):
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t)
    return t

w = open('wiki_jp8000.html', encoding='utf-8', errors='ignore').read()
txt = strip_html(w)
idxs = [m.start() for m in re.finditer(r'[Ss]uper ?[Ss]aw', txt)]
# print context around the main body mentions (the section body is around idx 4524-7460)
for i, ix in enumerate(idxs):
    if 4000 < ix < 8000:
        print(f"--- mention {i} @ {ix} ---")
        print(txt[max(0, ix-250):ix+900])
        print()
