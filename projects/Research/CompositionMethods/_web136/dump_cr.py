import json, sys
d = json.load(open(sys.argv[1]))
for it in d['message']['items']:
    au = ", ".join((a.get('family','') ) for a in it.get('author', [])[:4])
    print("-", it.get('title', [''])[0][:110])
    print("   ", au, "|", (it.get('container-title') or [''])[0][:60], "|", it.get('issued',{}).get('date-parts',[['?']])[0], "|", it.get('DOI'))
