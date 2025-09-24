import configparser
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

CONFIG_FILE = "config.txt"

# Ruční mapování RSS feedů
RSS_MAP = {
    "www.zive.cz": "https://www.zive.cz/rss/",
    "www.root.cz": "https://www.root.cz/rss",
    "www.cnews.cz": "https://www.cnews.cz/rss",
    "www.pctuning.cz": "https://www.pctuning.cz/rss",
    "www.seznam.cz": "https://www.seznam.cz/rss",
    "www.seznamzpravy.cz": "https://www.seznamzpravy.cz/rss",
    "www.novinky.cz": "https://www.novinky.cz/rss",
    "www.idnes.cz": "https://rss.idnes.cz/",
    "www.aktualne.cz": "https://www.aktualne.cz/rss",
    "www.hn.cz": "https://www.ihned.cz/rss",
    "www.denik.cz": "https://www.denik.cz/rss",
    "www.ceskatelevize.cz": "https://www.ceskatelevize.cz/rss",
    "www.nova.cz": "https://www.nova.cz/rss",
    "www.iprima.cz": "https://www.iprima.cz/rss"
}

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")
    if "DEFAULT" not in config:
        return {}
    return dict(config["DEFAULT"])

def save_config(values: dict):
    config = configparser.ConfigParser()
    config["DEFAULT"] = values
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        config.write(f)

# ----------------------------
# Funkce pro načtení článků
# ----------------------------
def fetch_articles(urls, keywords, blacklist, newest_date, oldest_date, max_articles=100):
    """
    urls: seznam URL (např. ['www.zive.cz', 'www.root.cz'])
    keywords: seznam klíčových slov
    blacklist: seznam slov pro vyloučení
    newest_date, oldest_date: datetime.date
    """
    articles = []

    for url in urls:
        rss_url = RSS_MAP.get(url)
        if not rss_url:
            continue
        try:
            feed = feedparser.parse(rss_url)
        except Exception:
            continue

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "") or entry.get("description", "")
            link = entry.get("link", "")

            # Datum článku
            pub_date_str = entry.get("published", "") or entry.get("updated", "")
            pub_date_dt = None
            try:
                pub_date_dt = datetime(*entry.published_parsed[:6]).date()
            except Exception:
                try:
                    from dateutil import parser
                    pub_date_dt = parser.parse(pub_date_str).date()
                except Exception:
                    pub_date_dt = None

            if pub_date_dt:
                if pub_date_dt > newest_date or pub_date_dt < oldest_date:
                    continue

            # Filtrování textu
            text = f"{title} {summary}".lower()
            if any(bl.lower() in text for bl in blacklist):
                continue
            if not any(kw.lower() in text for kw in keywords):
                continue

            # Obrázek článku
            image = None
            if "media_content" in entry:
                image = entry.media_content[0].get("url")
            else:
                try:
                    resp = requests.get(link, timeout=5)
                    soup = BeautifulSoup(resp.content, "html.parser")
                    img_tag = soup.find("img")
                    if img_tag:
                        image = img_tag.get("src")
                except Exception:
                    image = None

            # Perex: RSS summary nebo prvních 5 řádků HTML
            perex = summary.strip()
            if not perex:
                try:
                    resp = requests.get(link, timeout=5)
                    soup = BeautifulSoup(resp.content, "html.parser")
                    paragraphs = soup.find_all("p")
                    perex = " ".join([p.get_text() for p in paragraphs[:5]])
                except Exception:
                    perex = ""

            articles.append({
                "source": url,
                "title": title,
                "perex": perex,
                "url": link,
                "image": image
            })

            if len(articles) >= max_articles:
                break

    return articles
