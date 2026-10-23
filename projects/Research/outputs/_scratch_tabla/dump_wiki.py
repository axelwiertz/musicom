import json, glob, os
for f in sorted(glob.glob('/tmp/tb/*.json')):
    try:
        d = json.load(open(f))
    except Exception as e:
        print('=' * 20, os.path.basename(f), 'BADJSON', e)
        continue
    print('=' * 20, os.path.basename(f))
    for p in d['query']['pages'].values():
        t = p.get('extract', '')
        print(t if t else 'MISSING:' + p.get('title', ''))
        print()
