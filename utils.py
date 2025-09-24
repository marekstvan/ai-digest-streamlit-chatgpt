import configparser
import feedparser
import requests
from bs4 import BeautifulSoup

CONFIG_FILE = "config.txt"

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
def fetch_articles_from_rss(urls, keywords, blacklist, newest_date, oldest_date, max_articles=100):
    """
    urls: seznam URL (např. ['www.zive.cz', 'www.root.cz'])
    keywords: seznam klíčových slov
    blacklist: seznam slov pro vyloučení
    newest_date, oldest_date: datetime.date
    """
    articles = []

    for url in urls:
        rss_url = f"https://{url}/rss"  # jednoduché, ne vždy přesné
        try:
            feed = feedparser.parse(rss_url)
        except Exception:
            continue

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "") or entry.get("description", "")
            link = entry.get("link", "")
            pub_date = entry.get("published", "") or entry.get("updated", "")

            # konverze na date
            try:
                from dateutil import parser
                pub_date_dt = parser.parse(pub_date).date()
            except Exception:
                pub_date_dt = None

            if pub_date_dt:
                if pub_date_dt > newest_date or pub_date_dt < oldest_date:
                    continue

            text = f"{title} {summary}".lower()
            if any(bl.lower() in text for bl in blacklist):
                continue
            if not any(kw.lower() in text for kw in keywords):
                continue

            # Náhled obrázku
            image = None
            if "media_content" in entry:
                image = entry.media_content[0]["url"]
            else:
                # pokus získat obrázek z HTML
                try:
                    resp = requests.get(link, timeout=5)
                    soup = BeautifulSoup(resp.content, "html.parser")
                    img_tag = soup.find("img")
                    if img_tag:
                        image = img_tag.get("src")
                except Exception:
                    image = None

            articles.append({
                "source": url,
                "title": title,
                "perex": summary[:500],  # prvních 500 znaků, pokud perex chybí
                "url": link,
                "image": image
            })

            if len(articles) >= max_articles:
                break

    return articles
