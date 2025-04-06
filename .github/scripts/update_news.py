import feedparser
import json
import random
import os
import time
from openai import OpenAI

# Initialize OpenAI client
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# RSS feeds grouped by category
rss_feeds = {
    "Politics": [
        "https://www.cbc.ca/cmlink/rss-politics",
        "https://globalnews.ca/politics/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-politics-public-rss-1.6238634"
    ],
    "Business": [
        "https://www.cbc.ca/cmlink/rss-business",
        "https://globalnews.ca/business/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-business-public-rss-1.6238632"
    ],
    "Sports": [
        "https://www.cbc.ca/cmlink/rss-sports",
        "https://globalnews.ca/sports/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-sports-public-rss-1.6238630"
    ],
    "Weather": [
        "https://www.theweathernetwork.com/rss/weather/caon0696",
        "https://weather.gc.ca/rss/city/on-118_e.xml"
    ]
}

# Logos for each source
logos = {
    "cbc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/cbc.png?v=1742728178",
    "global": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/global_news.png?v=1742728177",
    "ctv": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/ctv.png?v=1742728179",
    "weathernetwork": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/weather.png?v=1742728180",
    "weather.gc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/environment_canada.png?v=1742728181"
}

def fetch_with_retries(url, retries=3, delay=3):
    for attempt in range(retries):
        try:
            return feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(delay)
    return feedparser.FeedParserDict(entries=[])

def rewrite_headline(original):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Rewrite this Canadian news headline to make it more SEO-friendly and unique: {original}"
            }],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Failed to rewrite headline: {original}\n{e}")
        return original

def extract_source(link):
    if "cbc.ca" in link:
        return "cbc"
    elif "globalnews.ca" in link:
        return "global"
    elif "ctvnews.ca" in link:
        return "ctv"
    elif "theweathernetwork.com" in link:
        return "weathernetwork"
    elif "weather.gc.ca" in link:
        return "weather.gc"
    return "cbc"  # fallback

def get_category_news(category, feeds):
    all_items = []
    seen_titles = set()

    for url in feeds:
        feed = fetch_with_retries(url)
        for entry in feed.entries[:10]:
            title = entry.title.strip()
            if title not in seen_titles:
                seen_titles.add(title)
                source = extract_source(entry.link)
                rewritten = rewrite_headline(title)
                all_items.append({
                    "source": source,
                    "logo": logos.get(source, ""),
                    "headline": rewritten,
                    "url": entry.link,
                    "category": category
                })

    return all_items

def main():
    os.makedirs("docs", exist_ok=True)
    combined = []

    for category, feeds in rss_feeds.items():
        print(f"🔎 Processing category: {category}")
        items = get_category_news(category, feeds)
        with open(f"docs/{category.lower()}.json", "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        combined.extend(items)

    # ✅ Shuffle to avoid repeated CBC dominance
    random.shuffle(combined)

    with open("docs/all.json", "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

    print("✅ All feeds updated!")


if __name__ == "__main__":
    main()

