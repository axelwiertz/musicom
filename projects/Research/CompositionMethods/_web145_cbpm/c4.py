import re, html

def clean(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t

for f in ["hb_basic-principles-of-bell-tuning.html", "hb_the-strike-note-of-bells.html"]:
    raw = open(f, encoding="utf-8", errors="ignore").read()
    t = clean(raw)
    open(f.replace(".html", ".txt"), "w").write(t)
    print("=====", f)
    print(t[1200:9000])
    print("--- links ---")
    for l in re.findall(r'href="([^"]+)"', raw):
        if "hibberts" in l and any(k in l.lower() for k in ["warb", "doublet", "tuning", "strike", "pitch", "sound"]):
            print(l)
