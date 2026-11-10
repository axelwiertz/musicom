#!/usr/bin/env python3
"""Final citation checks for SP-138."""
import json, urllib.request

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 research'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode('utf-8', 'replace')

# SPM paper biblio
d = json.loads(get("https://api.openalex.org/works/doi:10.1109/msp.2018.2872349?select=biblio,publication_year,title,authorships"))
print("SPM:", d.get('title'), "| year", d.get('publication_year'), "| biblio", d.get('biblio'))
for a in d.get('authorships', []):
    print("   -", a['author']['display_name'])

# MDPI pickup nonlinearity paper biblio + authors
d = json.loads(get("https://api.openalex.org/works/doi:10.3390/app7010050?select=biblio,publication_year,title,authorships,primary_location"))
print("\nPickup:", d.get('title'), "| year", d.get('publication_year'), "| biblio", d.get('biblio'))
for a in d.get('authorships', []):
    print("   -", a['author']['display_name'])

# JASA paper biblio (should be 148(5), 3052)
d = json.loads(get("https://api.openalex.org/works/doi:10.1121/10.0002002?select=biblio,publication_year,title"))
print("\nJASA:", d.get('title'), "| year", d.get('publication_year'), "| biblio", d.get('biblio'))
