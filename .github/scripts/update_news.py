import feedparser
import json
import random
import os
import time
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

feeds_by_category = {
    "Politics": [
        "https://www.cbc.ca/cmlink/rss-politics",
        "https://globalnews.ca/tag/canadian-politics/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-politics-public-rss-1.822289",
        "https://nationalpost.com/tag/canadian-politics/feed/",
        "https://ipolitics.ca/feed/"
    ],
    "Business": [
        "https://www.cbc.ca/cmlink/rss-business",
        "https://www.bnnbloomberg.ca/polopoly_fs/1.1182991!/menu/rss/rss-bnn-news",
        "https://financialpost.com/category/business/feed/",
        "https://globalnews.ca/tag/business/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-business-public-rss-1.822285"
    ],
    "Sports": [
        "https://www.cbc.ca/cmlink/rss-sports",
        "https://www.tsn.ca/rss",
        "https://www.sportsnet.ca/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-sports-public-rss-1.822291",
        "https://globalnews.ca/tag/sports/feed/"
    ],
    "Weather": [
        "https://www.theweathernetwork.com/rss/weather",
        "https://weather.gc.ca/rss/city/on-143_e.xml",
        "https://globalnews.ca/tag/weather/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-sci-tech-public-rss-1.822293"
    ]
}

logos = {
    "cbc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/cbc.png?v=1742728178",
    "global": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/global_news.png?v=1742728177",
    "ctv": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/ctv.png?v=1742728179",
    "default": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/news.png?v=default"
}

def fetch_with_retries(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(delay)
    return feedparser.FeedParserDict(entries=[])

def detect_source_from_url(url):
    if "cbc.ca" in url:
        return "cbc"
    elif "globalnews.ca" in url:
        return "global"
    elif "ctvnews.ca" in url:
        return "ctv"
    else:
        return "default"

def get_headlines():
    categorized_news = {"Politics": [], "Business": [], "Sports": [], "Weather": []}
    for category, feed_urls in feeds_by_category.items():
        for url in feed_urls:
            feed = fetch_with_retries(url)
            for entry in feed.entries[:3]:
                source = detect_source_from_url(entry.link)
                categorized_news[category].append({
                    "source": source,
                    "logo": logos.get(source, logos["default"]),
                    "original": entry.title,
                    "url": entry.link,
                    "category": category
                })
    return categorized_news

def rewrite_headline(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"Rewrite this Canadian news headline to make it more SEO-friendly and unique: {text}"
            }],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Failed to rewrite: {text}\n{e}")
        return text

def main():
    categorized = get_headlines()
    output = {}

    for category, items in categorized.items():
        rewritten = []
        sample = random.sample(items, min(5, len(items)))
        for item in sample:
            headline = rewrite_headline(item["original"])
            rewritten.append({
                "source": item["source"],
                "logo": item["logo"],
                "headline": headline,
                "url": item["url"],
                "category": category
            })
        output[category] = rewritten

    with open("docs/canada-news.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("✅ docs/canada-news.json updated with categorized blocks!")

if __name__ == "__main__":
    main()


