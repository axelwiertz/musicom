#!/usr/bin/env python3
"""Query Crossref for double-reed / bagpipe references."""
import json, subprocess, sys, time

def query(bib, outfile):
    url = ("https://api.crossref.org/works?query.bibliographic="
           + bib.replace(' ', '+') + "&rows=6&select=title,author,issued,container-title,DOI")
    r = subprocess.run(["curl", "-s", "--max-time", "30", "-A",
                        "Mozilla/5.0 (research; mailto:agent@musicom.local)", url, "-o", outfile],
                       capture_output=True)
    try:
        d = json.load(open(outfile))
    except Exception:
        print(f"  [parse fail] {outfile}"); return
    print(f"--- {bib}")
    for i in d.get("message", {}).get("items", []):
        t = (i.get("title") or [""])[0][:120]
        y = (i.get("issued", {}).get("date-parts") or [[None]])[0][0]
        auth = ", ".join(a.get("family", "?") for a in (i.get("author") or [])[:4])
        print(f"  {y} | {t} | {auth} | {i.get('DOI')}")
    time.sleep(1)

for bib, out in [
    ("Walstijn modeling mechanical response double reed ISMA 2007", "cr10.json"),
    ("Coyle oboe-like physical model thesis McGill", "cr11.json"),
    ("Guillemain oboe double reed model synthesis", "cr12.json"),
    ("Ducasse physical model wind instrument double reed bore", "cr13.json"),
]:
    query(bib, "/tmp/" + out)
