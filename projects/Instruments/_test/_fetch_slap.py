# -*- coding: utf-8 -*-
"""Fetch Wikipedia slap bass article and dump plain text for research grounding."""
import re
import html
import urllib.request

url = "https://en.wikipedia.org/wiki/Slap_bass"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) musicom-research/1.0"})
try:
    with urllib.request.urlopen(req, timeout=25) as r:
        t = r.read().decode("utf-8", errors="ignore")
except Exception as e:
    print("FETCH FAILED:", e)
    raise SystemExit(0)

t = re.sub(r"<[^>]+>", " ", t)
t = html.unescape(t)
t = re.sub(r"\s+", " ", t)
i = t.find("Slap bass")
print(t[i:i + 4200])
