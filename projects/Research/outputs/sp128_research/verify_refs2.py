import json, time, urllib.request, urllib.parse

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "musicom-research/1.0 (mailto:research@example.org)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

dois = ["10.1142/S1793536909000047"]
for d in dois:
    for attempt in range(3):
        try:
            m = fetch("https://api.crossref.org/works/" + urllib.parse.quote(d))["message"]
            auth = "; ".join((a.get("family", "") + ", " + a.get("given", "")) for a in m.get("author", [])[:5])
            print("DOI:", d)
            print("  TITLE:", m.get("title", [""])[0])
            print("  AUTH :", auth)
            print("  VENUE:", (m.get("container-title") or [""])[0], "| vol", m.get("volume", ""), "| iss", m.get("issue", ""), "| pp", m.get("page", ""))
            print("  DATE :", m.get("issued", {}).get("date-parts"))
            break
        except Exception as e:
            print("  retry", attempt, e)
            time.sleep(6)

# bibliographic queries
for q in ["Boudraa Cexus EMD-based signal filtering IEEE Transactions Instrumentation Measurement",
          "Hilbert-Huang transform and its applications Huang Shen",
          "empirical mode decomposition music synthesis timbre morphing"]:
    try:
        url = ("https://api.crossref.org/works?rows=3&select=title,author,container-title,issued,DOI&query.bibliographic="
               + urllib.parse.quote(q))
        for it in fetch(url)["message"]["items"]:
            a = "; ".join(x.get("family", "") for x in it.get("author", [])[:4])
            print("Q:", q[:40], "|", it.get("title", [""])[0][:95], "|", a, "|", it.get("DOI"), "|",
                  (it.get("container-title") or [""])[0][:45], it.get("issued", {}).get("date-parts"))
    except Exception as e:
        print("Q err", q, e)
    time.sleep(4)
