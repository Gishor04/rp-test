from flask import Flask, request, jsonify
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

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
    except Exception:
        return None

def get_best_summary(query):
    urls = search_duckduckgo(query)
    for url in urls:
        summary = get_meaningful_paragraph(url)
        if summary:
            return {
                "query": query,
                "source": url,
                "summary": summary
            }
    return {
        "query": query,
        "error": "No good content found"
    }

@app.route('/')
def home():
    return "👋 Welcome to the Dog Health Info API. Use /search?query=your_disease"

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400
    result = get_best_summary(query)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
