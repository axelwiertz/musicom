import re
t = open("hb_sound.html", encoding="utf-8", errors="ignore").read()
for l in re.findall(r'href="([^"]+)"', t):
    if "hibberts" in l and any(k in l.lower() for k in ["tuning", "pitch", "strike", "warble", "doublet", "intro"]):
        print(l)
