import re, html, sys, os

for f in ["wiki_bell.html", "wiki_strike.html", "wiki_founding.html"]:
    if not os.path.exists(f):
        continue
    t = open(f, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t)
    out = f.replace(".html", ".txt")
    open(out, "w").write(t)
    print(f, len(t))

# print partial-related extracts
t = open("wiki_bell.txt", encoding="utf-8", errors="ignore").read()
for kw in ["hum", "tierce", "nominal", "partial", "strike tone", "warble", "beating"]:
    for m in re.finditer(kw, t, re.I):
        s = max(0, m.start() - 300)
        print("\n---", kw, "---\n", t[s:m.start() + 500])
        break
