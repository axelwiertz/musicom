import re, html

def clean(f):
    t = open(f, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t

for f in ["hb_sound.html", "hb_build.html"]:
    t = clean(f)
    open(f.replace(".html", ".txt"), "w").write(t)
    print("=====", f, len(t))
    print(t[:6000])
