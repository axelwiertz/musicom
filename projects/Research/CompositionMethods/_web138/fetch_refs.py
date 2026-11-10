#!/usr/bin/env python3
"""Fetch and summarize references for SP-138 research."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 research'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode('utf-8', 'replace')

# 1. OpenAlex: more Rhodes works by Gabrielli
d = json.loads(get("https://api.openalex.org/works?search=Rhodes%20piano%20Gabrielli&per-page=6&select=title,publication_year,doi"))
print("=== OpenAlex 'Rhodes piano Gabrielli' ===")
for w in d.get('results', []):
    print("-", w.get('publication_year'), "|", w.get('title'), "|", w.get('doi'))

# 2. SPM 2018 paper authors
d = json.loads(get("https://api.openalex.org/works/doi:10.1109/msp.2018.2872349?select=title,authorships,publication_year"))
print("\n=== SPM 2018 ===")
print(d.get('title'), d.get('publication_year'))
for a in d.get('authorships', []):
    print("  -", a['author']['display_name'])

# 3. Search: other electric-piano physical modeling works
d = json.loads(get("https://api.openalex.org/works?search=electric%20piano%20synthesis%20tine&per-page=8&select=title,publication_year,doi"))
print("\n=== OpenAlex 'electric piano synthesis tine' ===")
for w in d.get('results', []):
    print("-", w.get('publication_year'), "|", w.get('title'), "|", w.get('doi'))
