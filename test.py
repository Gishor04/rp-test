from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

def search_duckduckgo(query, max_results=5):
    with DDGS() as ddgs:
        results = ddgs.text(query)
        urls = []
        for r in results:
            url = r.get("href") or r.get("url")
            if url and "wikipedia.org" not in url and url.startswith("http"):
                urls.append(url)
            if len(urls) >= max_results:
                break
    return urls

def get_meaningful_paragraph(url, min_len=60, max_total=800):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        paragraphs = soup.find_all("p")

        summary = ""
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) >= min_len and "cookie" not in text.lower():
                summary += text + "\n\n"
            if len(summary) > max_total:
                break

        return summary.strip()
    except Exception as e:
        return None

def get_best_summary(query):
    urls = search_duckduckgo(query)
    for url in urls:
        print(f"🔗 Trying: {url}")
        summary = get_meaningful_paragraph(url)
        if summary:
            return f"📖 From: {url}\n\n{summary}"
    return f"❌ No good content found for: {query}"

# 🔬 Search Queries
queries = [
    "dog fungal infections",
    "dog hypersensitivity allergic dermatosis",
    "dog bacterial dermatosis",
    "healthy dog skin"
]

for query in queries:
    print(f"\n🔍 Searching: {query}")
    print(get_best_summary(query))
    print("=" * 140)
