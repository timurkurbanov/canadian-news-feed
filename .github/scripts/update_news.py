import feedparser
import json
import random
import os
import time
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# Category-specific RSS feeds
feeds_by_category = {
    "Politics": [
        "https://www.cbc.ca/cmlink/rss-politics",
        "https://globalnews.ca/politics/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-politics-public-rss-1.822295",
        "https://www.hilltimes.com/feed/",
        "https://www.nationalnewswatch.com/feed/"
    ],
    "Business": [
        "https://www.cbc.ca/cmlink/rss-business",
        "https://globalnews.ca/business/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-business-public-rss-1.822292",
        "https://financialpost.com/feed/",
        "https://www.bnnbloomberg.ca/polopoly_fs/1.1329711!/feed.xml"
    ],
    "Sports": [
        "https://www.cbc.ca/cmlink/rss-sports",
        "https://globalnews.ca/sports/feed/",
        "https://www.ctvnews.ca/rss/ctvnews-ca-sports-public-rss-1.822300",
        "https://www.sportsnet.ca/feed/",
        "https://www.tsn.ca/rss"
    ],
    "Weather": [
        "https://www.theweathernetwork.com/rss/weather/caon0696",  # Toronto
        "https://rss.accuweather.com/rss/liveweather_rss.asp?locCode=CAXX0504",  # Ottawa
        "https://weather.gc.ca/rss/city/on-118_e.xml",  # Toronto
        "https://weather.gc.ca/rss/city/qc-147_e.xml",  # Montreal
        "https://weather.gc.ca/rss/city/bc-74_e.xml"  # Vancouver
    ]
}

logos = {
    "cbc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/cbc.png?v=1742728178",
    "global": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/global_news.png?v=1742728177",
    "ctv": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/ctv.png?v=1742728179",
    "default": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/canada_news.png?v=1"
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

def identify_source(link):
    if "cbc.ca" in link:
        return "cbc"
    elif "globalnews.ca" in link:
        return "global"
    elif "ctvnews.ca" in link:
        return "ctv"
    else:
        return "default"

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
        print(f"⚠️ Failed to rewrite: {text} → {e}")
        return text

def collect_category_news():
    final_news = []
    for category, urls in feeds_by_category.items():
        seen_titles = set()
        collected = []
        random.shuffle(urls)
        for feed_url in urls:
            if len(collected) >= 5:
                break
            feed = fetch_with_retries(feed_url)
            for entry in feed.entries:
                if len(collected) >= 5:
                    break
                if entry.title not in seen_titles:
                    seen_titles.add(entry.title)
                    source = identify_source(entry.link)
                    headline = rewrite_headline(entry.title)
                    collected.append({
                        "source": source,
                        "logo": logos.get(source, logos["default"]),
                        "headline": headline,
                        "url": entry.link,
                        "category": category
                    })
        final_news.extend(collected)
    return final_news

def main():
    news = collect_category_news()
    with open("docs/canada-news.json", "w", encoding="utf-8") as f:
        json.dump(news, f, indent=2, ensure_ascii=False)
    print("✅ Saved categorized news to docs/canada-news.json")

if __name__ == "__main__":
    main()


