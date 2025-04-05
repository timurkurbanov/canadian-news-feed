import feedparser
import json
import random
import os
import time
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# RSS Feeds grouped by category
category_feeds = {
    "Politics": [
        "https://www.cbc.ca/cmlink/rss-politics",
        "https://globalnews.ca/politics/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-politics-public-rss-1.867925"
    ],
    "Business": [
        "https://www.cbc.ca/cmlink/rss-business",
        "https://globalnews.ca/business/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-business-public-rss-1.867931"
    ],
    "Sports": [
        "https://www.cbc.ca/cmlink/rss-sports",
        "https://globalnews.ca/sports/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-sports-public-rss-1.867933"
    ],
    "Weather": [
        "https://www.theweathernetwork.com/rss/public/rss10/canada.xml",
        "https://www.cbc.ca/cmlink/rss-canada",  # catch regional weather
        "https://www.ctvnews.ca/rss/ctvnews-ca-sci-tech-public-rss-1.867936"
    ]
}

logos = {
    "cbc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/cbc.png?v=1742728178",
    "global": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/global_news.png?v=1742728177",
    "ctv": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/ctv.png?v=1742728179",
    "weathernetwork": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/weather.png?v=1742728180"
}

def fetch_feed(url, retries=3):
    for _ in range(retries):
        try:
            return feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
        except:
            time.sleep(2)
    return feedparser.FeedParserDict(entries=[])

def detect_source(url):
    if "cbc" in url:
        return "cbc"
    elif "global" in url:
        return "global"
    elif "ctv" in url:
        return "ctv"
    elif "weathernetwork" in url:
        return "weathernetwork"
    else:
        return "cbc"

def rewrite_headline(original):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Rewrite this Canadian news headline to be SEO-friendly and unique:\n\n{original}"
            }],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Rewrite failed: {original} – {e}")
        return original

def process_category(category, urls):
    articles = []
    for url in urls:
        feed = fetch_feed(url)
        for entry in feed.entries[:10]:
            source = detect_source(entry.link)
            rewritten = rewrite_headline(entry.title)
            articles.append({
                "source": source,
                "logo": logos[source],
                "headline": rewritten,
                "url": entry.link,
                "category": category
            })
    return random.sample(articles, min(5, len(articles)))

def main():
    data = {
        "all": [],
        "politics": [],
        "business": [],
        "sports": [],
        "weather": []
    }

    for cat in category_feeds:
        headlines = process_category(cat, category_feeds[cat])
        data["all"].extend(headlines)
        data[cat.lower()] = headlines

    with open("docs/canada-news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ News data saved to docs/canada-news.json")

if __name__ == "__main__":
    main()


