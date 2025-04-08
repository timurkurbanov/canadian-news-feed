import os
import json
import hashlib
import feedparser
from openai import OpenAI
from datetime import datetime

# ✅ OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ RSS feeds
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

# ✅ Logos
source_logos = {
    "cbc": "https://upload.wikimedia.org/wikipedia/commons/c/cb/CBC_Logo_2020.svg",
    "global": "https://upload.wikimedia.org/wikipedia/commons/2/24/Global_News_logo.svg",
    "ctv": "https://upload.wikimedia.org/wikipedia/commons/3/35/CTV_logo.svg",
    "weather.gc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/images.png?v=1743940410"
}

# ✅ Load cache
CACHE_FILE = "docs/news_cache.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = set(json.load(f))
else:
    cache = set()

# ✅ Rewrite headline
def rewrite_headline(original):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that rephrases headlines for clarity and SEO."},
                {"role": "user", "content": f"Rewrite this Canadian news headline for clarity and SEO: {original}"}
            ],
            temperature=0.7,
            max_tokens=60
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Rewrite failed: {e}")
        return original

# ✅ Main logic
def parse_and_classify():
    all_news = []
    updated_cache = set(cache)

    for category, feeds in rss_feeds.items():
        print(f"\n🔍 Fetching {category} news...")
        items = []

        for url in feeds:
            try:
                feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
                print(f"✅ Fetched {len(feed.entries)} items from {url}")

                for entry in feed.entries:
                    headline = entry.get("title", "")
                    link = entry.get("link", "")
                    published = entry.get("published", "") or entry.get("updated", "")
                    published_dt = None

                    try:
                        published_dt = datetime(*entry.published_parsed[:6])
                        published_str = published_dt.isoformat()
                    except Exception:
                        published_str = ""

                    # ✅ Hash the link or headline to detect duplicates
                    key = hashlib.md5((headline + link).encode('utf-8')).hexdigest()
                    if key in cache:
                        continue  # Skip duplicates

                    source = (
                        "weather.gc" if "weather.gc" in url else
                        "cbc" if "cbc.ca" in url else
                        "global" if "globalnews.ca" in url else
                        "ctv" if "ctvnews.ca" in url else
                        "unknown"
                    )

                    rewritten = rewrite_headline(headline)
                    logo = source_logos.get(source, "")

                    item = {
                        "source": source,
                        "logo": logo,
                        "headline": rewritten,
                        "url": link,
                        "category": category,
                        "published_at": published_str
                    }
                    items.append(item)
                    updated_cache.add(key)

            except Exception as e:
                print(f"❌ Failed to parse feed {url}: {e}")

        # ✅ Sort by date (newest first)
        items.sort(key=lambda x: x.get("published_at", ""), reverse=True)

        # ✅ Save category file
        with open(f"docs/{category.lower()}.json", "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

        all_news.extend(items)

    # ✅ Save combined news
    with open("docs/canada-news.json", "w", encoding="utf-8") as f:
        json.dump(all_news, f, indent=2, ensure_ascii=False)

    # ✅ Save updated cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(updated_cache), f)

# ✅ Run
if __name__ == "__main__":
    print("🔄 Updating Canadian news...")
    parse_and_classify()
    print("✅ All feeds updated!")
