from datetime import datetime
import json,feedparser,requests


def get_news(ticker):
    url = f'https://news.google.com/rss/search?q={ticker}.&hl=id&gl=ID&ceid=ID:id'
    feed = feedparser.parse(url)
    news_items = []
    now = datetime.now()
    for entry in feed.entries[:3]:
      if hasattr(entry, 'published_parsed'):
        pub = entry.published_parsed
        if pub.tm_mon == now.month and pub.tm_year == now.year:
            news_items.append({'title': entry.title, 'link': entry.link, 'published': entry.published})
    return news_items
