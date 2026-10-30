import json, sys, urllib.request, urllib.parse

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "musicom-research/1.0 (mailto:research@example.org)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

dois = [
    "10.1098/rspa.1998.0193",
    "10.1142/S1793536909000047",
    "10.1109/LSP.2003.821662",
    "10.1109/ICASSP.2011.5947265",
    "10.21437/interspeech.2004-395",
    "10.17743/jaes.2022.0067",
]
for d in dois:
    try:
        m = fetch("https://api.crossref.org/works/" + urllib.parse.quote(d))["message"]
        auth = "; ".join((a.get("family", "") + ", " + a.get("given", "")) for a in m.get("author", [])[:5])
        print("DOI:", d)
        print("  TITLE:", m.get("title", [""])[0])
        print("  AUTH :", auth)
        print("  VENUE:", (m.get("container-title") or [""])[0], "| vol", m.get("volume", ""), "| iss", m.get("issue", ""), "| pp", m.get("page", ""))
        print("  DATE :", m.get("issued", {}).get("date-parts"))
    except Exception as e:
        print("DOI:", d, "-> ERROR", e)
