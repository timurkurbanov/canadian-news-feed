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
            return feedparser.parse(url)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(delay)
    print(f"❌ Failed to fetch feed after {retries} attempts: {url}")
    return feedparser.FeedParserDict(entries=[])

def get_headlines():
    items = []
    for source, url in feeds.items():
        feed = fetch_with_retries(url)
        for entry in feed.entries[:5]:
            items.append({
                "source": source,
                "logo": logos[source],
                "original": entry.title,
                "url": entry.link
            })
    return items

def main():
    headlines = get_headlines()
    selected = random.sample(headlines, min(5, len(headlines)))

    rewritten_news = []
    for item in selected:
        try:
            rewritten = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": f"Rewrite this news headline to make it more SEO-friendly and unique: {item['original']}"}
                ],
                temperature=0.7,
            )
            new_headline = rewritten['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"⚠️ Failed to rewrite headline: {item['original']}")
            print(e)
            new_headline = item['original']

        rewritten_news.append({
            "source": item["source"],
            "logo": item["logo"],
            "headline": new_headline,
            "url": item["url"]
        })

    with open("canada-news.json", "w", encoding="utf-8") as f:
        json.dump(rewritten_news, f, indent=2, ensure_ascii=False)

    print("✅ canada-news.json updated successfully!")

if __name__ == "__main__":
    main()
