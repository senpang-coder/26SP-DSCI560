from bs4 import BeautifulSoup
import csv
import os

HTML_PATH = "../data/raw_data/web_data.html"
MARKET_CSV = "../data/processed_data/market_data.csv"
NEWS_CSV = "../data/processed_data/news_data.csv"


def clean_text(x):
    return " ".join(x.split()) if x else ""


def extract_market_data(soup):
    """
    Try to find market cards using class names mentioned in the assignment:
    marketCard_symbol, marketCard_stockPosition, marketCard-changePct
    """
    symbols = soup.select(".marketCard_symbol")
    positions = soup.select(".marketCard_stockPosition")
    changes = soup.select(".marketCard-changePct")

    rows = []
    n = min(len(symbols), len(positions), len(changes))
    for i in range(n):
        rows.append({
            "marketCard_symbol": clean_text(symbols[i].get_text()),
            "marketCard_stockPosition": clean_text(positions[i].get_text()),
            "marketCard-changePct": clean_text(changes[i].get_text()),
        })
    return rows


def extract_latest_news(soup):
    """
    CNBC page structure changes often. We'll do a robust approach:
    - Find any link whose surrounding text includes "Latest News" section
    - Collect candidate news items: <a> with a headline-like text and href
    - Try to capture timestamp if present near the link
    """
    news_rows = []

    # find a node containing "Latest News"
    latest_header = soup.find(string=lambda s: s and "Latest News" in s)
    if not latest_header:
        return news_rows

    # search within a reasonable container around that header
    container = latest_header
    for _ in range(6):
        if getattr(container, "parent", None) is None:
            break
        container = container.parent

    links = container.find_all("a", href=True)
    seen = set()

    for a in links:
        title = clean_text(a.get_text())
        href = a["href"]

        if not title or len(title) < 10:
            continue

        # normalize href
        if href.startswith("/"):
            href = "https://www.cnbc.com" + href

        key = (title, href)
        if key in seen:
            continue
        seen.add(key)

        # try to find a nearby time tag
        ts = ""
        t = a.find_previous("time")
        if t and t.get("datetime"):
            ts = t["datetime"]
        else:
            # sometimes timestamp is in a span
            span = a.find_previous("span")
            ts = clean_text(span.get_text()) if span else ""

        news_rows.append({
            "LatestNews-timestamp": ts,
            "title": title,
            "link": href
        })

    return news_rows


def write_csv(path, fieldnames, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main():
    print("Reading HTML:", HTML_PATH)
    if not os.path.exists(HTML_PATH):
        raise FileNotFoundError(f"Missing file: {HTML_PATH}. Run web_scraper.py first.")

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    print("Filtering Market banner fields...")
    market_rows = extract_market_data(soup)
    print(f"Market rows found: {len(market_rows)}")
    write_csv(MARKET_CSV,
              ["marketCard_symbol", "marketCard_stockPosition", "marketCard-changePct"],
              market_rows)
    print("Market CSV created:", MARKET_CSV)

    print("Filtering Latest News fields...")
    news_rows = extract_latest_news(soup)
    print(f"News rows found: {len(news_rows)}")
    write_csv(NEWS_CSV,
              ["LatestNews-timestamp", "title", "link"],
              news_rows)
    print("News CSV created:", NEWS_CSV)

    print("Done.")


if __name__ == "__main__":
    main()
