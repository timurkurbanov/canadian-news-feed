import feedparser
import json
import random
import os
import time
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define categorized RSS feeds
feeds = {
    "Politics": [
        "https://www.cbc.ca/cmlink/rss-politics",
        "https://globalnews.ca/politics/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-politics-public-rss-1.822285"
    ],
    "Business": [
        "https://www.cbc.ca/cmlink/rss-business",
        "https://globalnews.ca/business/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-business-public-rss-1.822284"
    ],
    "Sports": [
        "https://www.cbc.ca/cmlink/rss-sports",
        "https://globalnews.ca/sports/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-sports-public-rss-1.822291"
    ],
    "Weather": [
        "https://www.theweathernetwork.com/rss/weather",
        "https://www.cbc.ca/cmlink/rss-canada",
        "https://www.ctvnews.ca/rss/ctvnews-ca-canada-public-rss-1.822287"
    ]
}

logos = {
    "cbc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/cbc.png?v=1742728178",
    "global": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/global_news.png?v=1742728177",
    "ctv": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/ctv.png?v=1742728179",
    "weathernetwork": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/weather.png?v=1742728180"
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

def classify_category_ai(title):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user",
                "content": f"""Classify this Canadian news headline into one of the following categories:
Politics, Business, Sports, Weather, or General.

Respond with only the category name.

Headline: "{title}"
"""
            }],
            temperature=0,
        )
        category = response.choices[0].message.content.strip().capitalize()
        print(f"🧠 Classified → '{title}' → {category}")
        return category if category in ["Politics", "Business", "Sports", "Weather", "General"] else "General"
    except Exception as e:
        print(f"⚠️ Failed to classify headline: {title}\n{e}")
        return "General"

def identify_source(url):
    if "cbc.ca" in url:
        return "cbc"
    elif "globalnews.ca" in url:
        return "global"
    elif "ctvnews.ca" in url:
        return "ctv"
    elif "weathernetwork" in url:
        return "weathernetwork"
    else:
        return "cbc"

def get_headlines():
    all_items = []
    for category, urls in feeds.items():
        selected_urls = random.sample(urls, min(2, len(urls)))
        for url in selected_urls:
            feed = fetch_with_retries(url)
            for entry in feed.entries[:10]:
                source = identify_source(entry.link)
                classified = classify_category_ai(entry.title)
                all_items.append({
                    "source": source,
                    "logo": logos[source],
                    "original": entry.title,
                    "url": entry.link,
                    "category": classified
                })
    return all_items

def main():
    all_headlines = get_headlines()

    categories = ["Politics", "Business", "Sports", "Weather", "General"]
    final_news = []

    for cat in categories:
        cat_items = [item for item in all_headlines if item["category"] == cat]
        final_news.extend(random.sample(cat_items, min(5, len(cat_items))))

    rewritten_news = []
    for item in final_news:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": f"Rewrite this Canadian news headline to make it more SEO-friendly and unique: {item['original']}"
                }],
                temperature=0.7,
            )
            new_headline = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Failed to rewrite headline: {item['original']}\n{e}")
            new_headline = item['original']

        rewritten_news.append({
            "source": item["source"],
            "logo": item["logo"],
            "headline": new_headline,
            "url": item["url"],
            "category": item["category"]
        })

    with open("docs/canada-news.json", "w", encoding="utf-8") as f:
        json.dump(rewritten_news, f, indent=2, ensure_ascii=False)

    print("✅ docs/canada-news.json updated successfully!")

if __name__ == "__main__":
    main()


