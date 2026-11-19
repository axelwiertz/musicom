import re, html

def clean(t):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t

for f in ["hb2_doublets-or-warble-in-bells.html", "hb_the-strike-note-of-bells.html"]:
    t = clean(open(f, encoding="utf-8", errors="ignore").read())
    open(f.replace(".html", ".txt"), "w").write(t)
    print("=====", f, len(t))
    print(t[:7000])
