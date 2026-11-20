import sys
from pypdf import PdfReader

for path in sys.argv[1:]:
    try:
        r = PdfReader(path)
        txt = []
        for p in r.pages:
            txt.append(p.extract_text() or "")
        out = path.rsplit(".", 1)[0] + ".txt"
        with open(out, "w") as f:
            f.write("\n".join(txt))
        print(path, "pages", len(r.pages), "chars", sum(len(t) for t in txt), "->", out)
    except Exception as e:
        print("ERR", path, e)
