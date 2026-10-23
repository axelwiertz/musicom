import re, sys, html

limit = int(sys.argv[1])

def strip(fn):
    s = open(fn, encoding='utf-8', errors='ignore').read()
    s = re.sub(r'(?is)<(script|style|svg|nav|footer|header)[^>]*>.*?</\1>', ' ', s)
    s = re.sub(r'(?is)<br\s*/?>', '\n', s)
    s = re.sub(r'(?is)</(p|div|li|h[1-6]|tr)>', '\n', s)
    s = re.sub(r'(?s)<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s.strip()

for fn in sys.argv[2:]:
    print('#' * 30, fn)
    print(strip(fn)[:limit])
    print()
