import feedparser
import openai
import json
import random
import os
from datetime import datetime

# Set your OpenAI API key from the GitHub secret\openai.api_key = os.getenv("OPENAI_API_KEY")

# Define RSS feeds
feeds = {
    "cbc": "https://www.cbc.ca/cmlink/rss-topstories",
    "global": "https://globalnews.ca/feed/",
    "ctv": "https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009"
}

logos = {
    "cbc": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/cbc.png?v=1742728178",
    "global": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/global_news.png?v=1742728177",
    "ctv": "https://cdn.shopify.com/s/files/1/0649/5997/1534/files/ctv.png?v=1742728177"
}

# Pull top headlines from each feed
def get_headlines():
    items = []
    for source, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:  # Limit to top 5
            items.append({
                "source": source,
                "logo": logos[source],
                "original": entry.title,
                "url": entry.link
            })
    return items

# Rewrite headline using OpenAI
async def rewrite_headline(headline):
    prompt = f"Rewrite this news headline to make it more SEO-friendly and unique: {headline}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a headline optimization assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return headline  # Fallback

# Main function to process and write
async def generate():
    raw_items = get_headlines()
    random.shuffle(raw_items)
    selected = raw_items[:5]  # Pick 5 from mixed sources

    rewritten = []
    for item in selected:
        new_title = await rewrite_headline(item["original"])
        rewritten.append({
            "source": item["source"],
            "logo": item["logo"],
            "headline": new_title,
            "url": item["url"]
        })

    with open("canada-news.json", "w") as f:
        json.dump(rewritten, f, indent=2)

# Run script
if __name__ == "__main__":
    import asyncio
    asyncio.run(generate())
