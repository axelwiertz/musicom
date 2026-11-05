import json, sys, glob, re
for f in sys.argv[1:]:
    try:
        d = json.load(open(f))
    except Exception as e:
        print(f, "ERR", e); continue
    if 'query' in d:
        for p in d['query']['pages'].values():
            t = p.get('extract', '')
            print("="*30, f, p.get('title'), len(t))
            print(t[:2500])
