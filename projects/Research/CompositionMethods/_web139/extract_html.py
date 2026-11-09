#!/usr/bin/env python3
"""Extract readable text from downloaded Wikipedia HTML for research notes."""
import re, sys, html

def extract(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        raw = f.read()
    # strip <script>/<style>
    raw = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', raw)
    # drop tags, keep paragraph breaks
    raw = re.sub(r'(?i)</(p|h[1-6]|li|tr|div|table)>', '\n', raw)
    raw = re.sub(r'<[^>]+>', ' ', raw)
    raw = html.unescape(raw)
    raw = re.sub(r'[ \t]+', ' ', raw)
    raw = re.sub(r'\n\s*\n+', '\n', raw)
    return raw

if __name__ == '__main__':
    for p in sys.argv[1:]:
        print(f'===== {p} =====')
        print(extract(p))
