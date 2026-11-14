#!/usr/bin/env python3
import re, html
t = open('szabo_live.html', encoding='utf-8', errors='ignore').read()
links = re.findall(r'href="([^"]+)"', t)
hits = [html.unescape(l) for l in links if re.search(r'supersaw|\.pdf', l, flags=re.I)]
print("HITS:", sorted(set(hits)))
txt = re.sub(r'<script.*?</script>', '', t, flags=re.S)
txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
txt = re.sub(r'<[^>]+>', ' ', txt)
txt = html.unescape(txt)
txt = re.sub(r'\s+', ' ', txt)
i = txt.lower().find('supersaw')
print("CTX:", txt[max(0,i-300):i+500] if i >= 0 else "no mention")
