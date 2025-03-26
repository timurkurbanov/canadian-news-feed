import feedparser
import openai
import json
import random
import os
import time
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

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

def fetch_with_retries(url, retries=3, delay=3):
    for attempt in range(retries):
        try:
            return feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(delay)
    print(f"❌ Failed to fetch feed after {retries} attempts: {url}")
    return feedparser.FeedParserDict(entries=[])

def guess_category(title):
    title = title.lower()
    if any(word in title for word in ["election", "minister", "government", "parliament", "policy"]):
        return "Politics"
    elif any(word in title for word in ["business", "economy", "inflation", "trade", "market"]):
        return "Business"
    elif any(word in title for word in ["sport", "game", "team", "tournament", "score"]):
        return "Sports"
    elif any(word in title for word in ["weather", "storm", "climate", "environment"]):
        return "Weather"
    elif any(word in title for word in ["art", "music", "festival", "film", "celebrity"]):
        return "Entertainment"
    else:
        return "General"

def get_headlines():
    items = []
    for source, url in feeds.items():
        feed = fetch_with_retries(url)
        for entry in feed.entries[:5]:
            category = guess_category(entry.title)
            items.append({
                "source": source,
                "logo": logos[source],
                "original": entry.title,
                "url": entry.link,
                "category": category
            })
    return items

def main():
    headlines = get_headlines()
    selected = random.sample(headlines, min(5, len(headlines)))

    rewritten_news = []
    for item in selected:
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": f"Rewrite this news headline to make it more SEO-friendly and unique: {item['original']}"
                    }
                ],
                temperature=0.7,
            )
            new_headline = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Failed to rewrite headline: {item['original']}")
            print(e)
            new_headline = item['original']

        rewritten_news.append({
            "source": item["source"],
            "logo": item["logo"],
            "headline": new_headline,
            "url": item["url"],
            "category": item["category"]
        })

    with open("canada-news.json", "w", encoding="utf-8") as f:
        json.dump(rewritten_news, f, indent=2, ensure_ascii=False)

    print("✅ canada-news.json updated successfully!")

if __name__ == "__main__":
    main()

