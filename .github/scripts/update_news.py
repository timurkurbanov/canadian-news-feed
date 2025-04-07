import os
import json
import feedparser
import openai
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

# RSS Feeds per category
rss_feeds = {
    "Politics": [
        "https://www.cbc.ca/cmlink/rss-politics",
        "https://globalnews.ca/feed/section/politics/",
        "https://www.ctvnews.ca/rss/ctvnews-politics-public-rss-1.822285"
    ],
    "Business": [
        "https://www.cbc.ca/cmlink/rss-business",
        "https://globalnews.ca/feed/section/money/",
        "https://www.ctvnews.ca/rss/ctvnews-business-public-rss-1.822288"
    ],
    "Sports": [
        "https://www.cbc.ca/cmlink/rss-sports",
        "https://globalnews.ca/feed/section/sports/",
        "https://www.ctvnews.ca/rss/ctvnews-sports-public-rss-1.822289"
    ],
    "Weather": [
        "https://weather.gc.ca/rss/city/on-118_e.xml"
    ]
}

# Logos by source
source_logos = {
    "cbc": "https://upload.wikimedia.org/wikipedia/commons/c/cb/CBC_Logo_2020.svg",
    "global": "https://upload.wikimedia.org/wikipedia/commons/2/24/Global_News_logo.svg",
    "ctv": "https://upload.wikimedia.org/wikipedia/commons/3/35/CTV_logo.svg",
    "weather.gc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/images.png?v=1743940410"
}

def rewrite_headline(original):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rephrases headlines for clarity and SEO."},
                {"role": "user", "content": f"Rewrite this Canadian news headline for clarity and SEO: {original}"}
            ],
            temperature=0.7,
            max_tokens=60
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"⚠️ Rewrite failed: {e}")
        return original

def parse_and_classify():
    all_news = []

    for category, feeds in rss_feeds.items():
        print(f"🔍 Fetching {category} news...")
        items = []

        for url in feeds:
            try:
                feed = feedparser.parse(url)
                print(f"✅ Fetched {len(feed.entries)} items from {url}")
                for entry in feed.entries:
                    title = entry.get("title", "").strip()
                    link = entry.get("link", "").strip()
                    if not title or not link:
                        continue

                    source_key = "weather.gc" if "weather.gc" in url else (
                        "cbc" if "cbc.ca" in url else
                        "global" if "globalnews.ca" in url else
                        "ctv" if "ctvnews.ca" in url else "unknown"
                    )
                    logo = source_logos.get(source_key, "")

                    rewritten = rewrite_headline(title)

                    items.append({
                        "source": source_key,
                        "logo": logo,
                        "headline": rewritten,
                        "url": link,
                        "category": category
                    })

            except Exception as e:
                print(f"❌ Failed to parse feed {url}: {e}")

        with open(f"docs/{category.lower()}.json", "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

        all_news.extend(items)

    with open("docs/canada-news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    print("🔄 Updating Canadian news...")
    parse_and_classify()
    print("✅ All feeds updated!")
