import json
d = json.load(open('Helmholtz_resonance.json'))
t = list(d['query']['pages'].values())[0]['extract']
i = t.find('==')
print(t[t.find('== ', 2000):][:6000])
print('---- OCARINA acoustic ----')
o = json.load(open('Ocarina.json'))
to = list(o['query']['pages'].values())[0]['extract']
for kw in ['Helmholtz', 'acoustic', 'octave', 'frequency']:
    j = to.find(kw)
    print(kw, j, to[max(0, j-400):j+700] if j > 0 else '')
