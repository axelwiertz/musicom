import json
for f in ['Helmholtz_resonance.json','Ocarina.json','Udu.json','Bass_reflex.json','End_correction.json']:
    d = json.load(open(f))
    pg = list(d['query']['pages'].values())[0]
    t = pg.get('extract', '')
    print('=' * 20, f, len(t))
    print(t[:3000])
    print()
