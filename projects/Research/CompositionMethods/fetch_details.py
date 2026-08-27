import requests
from bs4 import BeautifulSoup
import re

def clean(text):
    return re.sub(r'\s+', ' ', text).strip()

def get_details(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        paragraphs = [p.text for p in soup.find_all('p')]
        print(f"\n=== DETAILS: {url} ===")
        print(clean("\n".join(paragraphs[:8]))[:1500])
    except Exception as e:
        print("Error:", e)

get_details('https://www.synthtopia.com/content/2026/07/15/free-browser-based-instrument-puntone-glides-chords-theremin-style/')
