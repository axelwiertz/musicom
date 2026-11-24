"""Extract plain text from fetched HTML reference pages for citation snippets."""
import html
import re
import sys

def extract(path, out, maxlen=80000):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    # drop script/style
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    # strip tags
    txt = re.sub(r"(?s)<[^>]+>", " ", raw)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n\n", txt)
    open(out, "w", encoding="utf-8").write(txt[:maxlen])
    print(out, len(txt), "chars")

extract("wiki_mandelbrot.html", "wiki_mandelbrot.txt")
extract("wiki_julia.html", "wiki_julia.txt")
extract("mathworld_mandelbrot.html", "mathworld_mandelbrot.txt")
