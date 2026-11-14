#!/usr/bin/env python3
"""Parse fetched web pages for the SP-141 supersaw research."""
import re, html, json, sys

def strip_html(t):
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t)
    return t

out = {}

# --- Bing results ---
try:
    b = open('bing1.html', encoding='utf-8', errors='ignore').read()
    links = re.findall(r'<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>', b)
    res = []
    for url, title in links[:15]:
        t = strip_html(title)
        # find snippet after this anchor: crude - take text near it
        res.append({'url': url, 'title': t})
    out['bing_links'] = res
    # fallback: all external urls
    if not res:
        urls = re.findall(r'href="(https?://[^"]+)"', b)
        seen = []
        for u in urls:
            if 'bing.com' not in u and 'microsoft' not in u and 'bing.net' not in u and u not in seen:
                seen.append(u)
        out['bing_urls_fallback'] = seen[:20]
except Exception as e:
    out['bing_err'] = str(e)

# --- Wikipedia JP-8000 ---
try:
    w = open('wiki_jp8000.html', encoding='utf-8', errors='ignore').read()
    txt = strip_html(w)
    i = txt.lower().find('supersaw')
    out['wiki_supersaw_ctx'] = txt[max(0, i-500):i+1500] if i >= 0 else 'NO MATCH'
    # also search 'feedback'
    j = txt.lower().find('feedback')
    out['wiki_feedback_ctx'] = txt[max(0, j-300):j+500] if j >= 0 else 'NO MATCH'
except Exception as e:
    out['wiki_err'] = str(e)

# --- CCRMA index ---
try:
    c = open('ccrma_index.html', encoding='utf-8', errors='ignore').read()
    links = re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>', c)
    out['ccrma_links'] = [{'href': h, 'text': strip_html(t)[:80]} for h, t in links if h.startswith('/') or h.startswith('http')]
except Exception as e:
    out['ccrma_err'] = str(e)

print(json.dumps(out, indent=1)[:6000])
