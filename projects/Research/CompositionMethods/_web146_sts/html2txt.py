import re
import html as htmlmod

raw = open("/opt/data/projects/Research/CompositionMethods/_web146_sts/texstat_html.html",
           encoding="utf-8", errors="ignore").read()
raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
raw = re.sub(r"<math[^>]*alttext=\"([^\"]*)\"[^>]*>.*?</math>", r" \1 ", raw, flags=re.S)
raw = re.sub(r"<[^>]+>", " ", raw)
txt = htmlmod.unescape(raw)
txt = re.sub(r"[ \t]+", " ", txt)
txt = re.sub(r"\n\s*\n+", "\n\n", txt)
open("/opt/data/projects/Research/CompositionMethods/_web146_sts/texstat.txt", "w").write(txt)
print(len(txt))
