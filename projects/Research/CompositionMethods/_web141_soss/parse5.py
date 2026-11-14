#!/usr/bin/env python3
"""Parse Google basic-HTML results."""
import re, html, json

t = open('google1.html', encoding='utf-8', errors='ignore').read()
out = {}
out['title'] = re.search(r'<title>(.*?)</title>', t, flags=re.S).group(1)[:200] if '<title>' in t else ''
# /url?q= links (Google redirect wrapper)
urls = re.findall(r'/url\?q=([^&"]+)', t)
dec = []
for u in urls:
    u = html.unescape(u)
    if not re.search(r'google\.|gstatic|youtube\.com/cookie', u):
        dec.append(u)
out['urls'] = sorted(set(dec))[:25]
# visible text snippets: h3 titles
titles = re.findall(r'<h3[^>]*>(.*?)</h3>', t, flags=re.S)
out['h3'] = [re.sub(r'<[^>]+>', '', html.unescape(x))[:100] for x in titles[:12]]
print(json.dumps(out, indent=1))
