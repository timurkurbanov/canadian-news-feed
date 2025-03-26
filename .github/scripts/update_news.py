import feedparser
import json
import os
from datetime import datetime

feeds = {
    "cbc": "https://www.cbc.ca/cmlink/rss-topstories",
    "global": "https://globalnews.ca/feed/",
    "ctv": "https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009"
}

logos = {
    "cbc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/cbc.png?v=1742728178",
    "global": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/global_news.png?v=1742728177",
    "ctv": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/ctv.png?v=1742728179"
}

# Keywords for each category
categories = {
    "Politics": ["election", "minister", "government", "parliament", "policy", "bill"],
    "Business": ["business", "economy", "inflation", "trade", "market", "stock", "investment"],
    "Sports": ["sport", "game", "team", "match", "score", "tournament", "league"],
    "Weather": ["weather", "storm", "climate", "temperature", "environment", "rain", "snow"]
}

def fetch_entries():
    entries = []
    for source, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            entries.append({
                "source": source,
                "logo": logos[source],
                "original": entry.title,
                "url": entry.link
            })
    return entries

def categorize_entry(title):
    title_lower = title.lower()
    for cat, keywords in categories.items():
        if any(word in title_lower for word in keywords):
            return cat
    return "General"

def main():
    all_entries = fetch_entries()
    sorted_news = []

    # Loop through categories and grab 5 for each
    for cat in list(categories.keys()):
        matched = [
            {
                "source": e["source"],
                "logo": e["logo"],
                "headline": e["original"],
                "url": e["url"],
                "category": cat
            }
            for e in all_entries
            if categorize_entry(e["original"]) == cat
        ]
        sorted_news.extend(matched[:5])

    # If still under 5 for a category, add some Generals to make sure the All tab is populated
    general = [
        {
            "source": e["source"],
            "logo": e["logo"],
            "headline": e["original"],
            "url": e["url"],
            "category": "General"
        }
        for e in all_entries
        if categorize_entry(e["original"]) == "General"
    ]
    sorted_news.extend(general[:5])

    # Save
    with open("docs/canada-news.json", "w", encoding="utf-8") as f:
        json.dump(sorted_news, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(sorted_news)} categorized headlines to docs/canada-news.json")

if __name__ == "__main__":
    main()
