#!/usr/bin/env python3
"""Parse fetched web pages for SP-141 supersaw research (round 2)."""
import re, html, json

def strip_html(t):
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S)
    t = re.sub(r'<style.*?</style>', '', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'\s+', ' ', t)
    return t

out = {}

# --- Wikipedia: full supersaw section ---
try:
    w = open('wiki_jp8000.html', encoding='utf-8', errors='ignore').read()
    txt = strip_html(w)
    # find all "Supersaw" mentions with context
    idxs = [m.start() for m in re.finditer(r'[Ss]uper ?[Ss]aw', txt)]
    out['wiki_mentions'] = len(idxs)
    # the section content: locate '== Supersaw' in raw? Use rendered: look for the paragraph after the section header
    # In rendered HTML the section is: <h2><span class="mw-headline" id="Supersaw">Supersaw</span></h2>
    m = re.search(r'<h2><span class="mw-headline" id="Supersaw">(.*?)</span></h2>(.*?)<h2', w, flags=re.S)
    if m:
        sec = strip_html(m.group(2))
        out['wiki_supersaw_section'] = sec[:3000]
    else:
        out['wiki_supersaw_section'] = 'HEADER NOT FOUND; mentions at: ' + str(idxs[:20])
except Exception as e:
    out['wiki_err'] = str(e)

# --- Bing: b_algo blocks ---
try:
    b = open('bing1.html', encoding='utf-8', errors='ignore').read()
    blocks = re.findall(r'<li class="b_algo".*?</li>', b, flags=re.S)
    res = []
    for bl in blocks[:12]:
        u = re.search(r'<a[^>]+href="([^"]+)"', bl)
        t = re.search(r'<h2[^>]*>(.*?)</h2>', bl, flags=re.S)
        sn = re.search(r'<p[^>]*>(.*?)</p>', bl, flags=re.S)
        res.append({
            'url': html.unescape(u.group(1)) if u else '',
            'title': strip_html(t.group(1))[:120] if t else '',
            'snippet': strip_html(sn.group(1))[:300] if sn else '',
        })
    out['bing_algo'] = res
    if not res:
        # page might have a consent/redirect; dump first <title> and any http links
        tt = re.search(r'<title>(.*?)</title>', b, flags=re.S)
        out['bing_title'] = tt.group(1) if tt else ''
        out['bing_has_captcha'] = 'captcha' in b.lower() or 'challenge' in b.lower()
except Exception as e:
    out['bing_err'] = str(e)

print(json.dumps(out, indent=1)[:8000])
