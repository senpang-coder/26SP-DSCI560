import requests
from bs4 import BeautifulSoup

URL = "https://www.cnbc.com/world/?region=world"
OUT_PATH = "../data/raw_data/web_data.html"

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("Fetching webpage...")
resp = requests.get(URL, headers=headers, timeout=20)
resp.raise_for_status()

print("HTTP status code:", resp.status_code)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(resp.text)

print("Saved HTML to:", OUT_PATH)

soup = BeautifulSoup(resp.text, "html.parser")
latest_news_text = soup.find(string=lambda s: s and "Latest News" in s)
print("Found 'Latest News' text?:", bool(latest_news_text))


