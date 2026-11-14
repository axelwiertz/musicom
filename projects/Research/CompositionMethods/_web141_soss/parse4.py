#!/usr/bin/env python3
"""Find supersaw PDF links on the Szabo homepage snapshot."""
import re, html, json

t = open('szabo_home.html', encoding='utf-8', errors='ignore').read()
# all hrefs containing supersaw or pdf
links = re.findall(r'href="([^"]+)"', t)
hits = []
for l in links:
    if re.search(r'supersaw|super.?saw|\.pdf', l, flags=re.I):
        hits.append(html.unescape(l))
print("SUPERSAW/PDF LINKS:")
for h in sorted(set(hits)):
    print(" ", h)
# also dump visible text around 'supersaw'
txt = re.sub(r'<script.*?</script>', '', t, flags=re.S)
txt = re.sub(r'<style.*?</style>', '', txt, flags=re.S)
txt = re.sub(r'<[^>]+>', ' ', txt)
txt = html.unescape(txt)
txt = re.sub(r'\s+', ' ', txt)
i = txt.lower().find('supersaw')
print("\nCTX:", txt[max(0,i-400):i+600] if i >= 0 else "no supersaw in text")
