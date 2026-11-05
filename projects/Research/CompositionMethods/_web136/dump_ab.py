import json, sys, re, html
for f in sys.argv[1:]:
    d = json.load(open(f))['message']
    print("="*20, f)
    print(d.get('title', [''])[0])
    print("DOI:", d.get('DOI'), "|", (d.get('container-title') or [''])[0], "|", d.get('issued',{}).get('date-parts'))
    ab = d.get('abstract', '')
    ab = re.sub(r'<[^>]+>', ' ', ab)
    print(html.unescape(re.sub(r'\s+', ' ', ab))[:1800])
