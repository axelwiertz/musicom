import requests
from bs4 import BeautifulSoup
import re

def clean(text):
    return re.sub(r'\s+', ' ', text).strip()

def search_synthtopia_main():
    print("--- SYNTHETOPIA MAIN ---")
    try:
        r = requests.get('https://www.synthtopia.com/', headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        articles = soup.find_all('article')[:12]
        for art in articles:
            title_tag = art.find(['h1', 'h2', 'h3', 'a'], class_=re.compile('title|entry-title'))
            if not title_tag:
                title_tag = art.find('h2')
            if title_tag:
                link = title_tag.find('a') if title_tag.name != 'a' else title_tag
                title_text = title_tag.text if not link else link.text
                url = link.get('href') if link else ""
                print(f"Title: {clean(title_text)}")
                print(f"URL: {url}")
                summary = art.find(class_=re.compile('summary|content|entry-summary|excerpt'))
                if not summary:
                    summary = art.find('p')
                if summary:
                    print(f"Snippet: {clean(summary.text[:200])}...")
                print()
    except Exception as e:
        print("Synthtopia error:", e)

search_synthtopia_main()
