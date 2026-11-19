import re
t = open("hibbert_home.html", encoding="utf-8", errors="ignore").read()
links = re.findall(r'href="([^"]+)"', t)
for l in links:
    if any(k in l.lower() for k in ["bell", "tuning", "partial", "acoust", "strike", "wobble", "measure"]):
        print(l)
print("---- text ----")
txt = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
txt = re.sub(r"<[^>]+>", "\n", txt)
txt = re.sub(r"\n\s*\n+", "\n", txt)
print(txt[:3000])
