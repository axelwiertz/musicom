#!/usr/bin/env python3
"""Extract text snippets from cached Wikipedia HTML for CDRB research."""
import re, html as htmllib

def extract(path, needles, span=450):
    raw = open(path, encoding='utf-8', errors='ignore').read()
    text = re.sub(r'<[^>]+>', ' ', raw)
    text = htmllib.unescape(re.sub(r'\s+', ' ', text))
    low = text.lower()
    print(f"===== {path} =====")
    for n in needles:
        idx = low.find(n.lower())
        if idx < 0:
            print(f"  [{n}] NO MATCH")
            continue
        print(f"  [{n}] ...{text[max(0,idx-80):idx+span]}...")
        print()

extract('/tmp/oboe.html', [
    'double reed',
    'conical bore',
    'harmonic series',
    'blowing pressure',
])
extract('/tmp/bassoon.html', ['double reed', 'conical bore', 'blowing pressure'])
extract('/tmp/reed.html', ['double reed', 'two blades', 'Bernoulli', 'beating'])
extract('/tmp/bagpipe.html', ['chanter', 'double reed', 'conical'])
