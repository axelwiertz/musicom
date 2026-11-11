#!/usr/bin/env python3
"""Extract DDG results."""
import re, html as htmllib

raw = open('/tmp/ddg1.html', encoding='utf-8', errors='ignore').read()
text = re.sub(r'<[^>]+>', '\n', raw)
text = htmllib.unescape(text)
lines = [l.strip() for l in text.splitlines() if l.strip()]
for l in lines:
    if any(k in l.lower() for k in ('walstijn', 'avanzini', 'double reed', 'result', 'no results', 'ism')):
        print(l[:220])
