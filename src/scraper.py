import hashlib
import logging
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://books.toscrape.com/"
CACHE_DIR = Path("data/cache")
HEADERS = {"User-Agent": "Mozilla/5.0 (learning project)"}
DELAY_SECONDS = 1      # نستنى ثانية بين كل طلبين (أدب مع الموقع)
MAX_RETRIES = 3


def fetch(url):
    """يرجّع HTML الصفحة من الكاش لو موجودة، وإلا من النت. يرجّع None لو فشل."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / (hashlib.md5(url.encode()).hexdigest() + ".html")

    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            cache_file.write_text(resp.text, encoding="utf-8")
            time.sleep(DELAY_SECONDS)
            return resp.text
        except requests.RequestException as e:
            logger.warning("Attempt %d/%d failed for %s: %s",
                           attempt, MAX_RETRIES, url, e)
            time.sleep(2 ** attempt)          # 2، 4، 8 ثواني (backoff)

    logger.error("Giving up on %s", url)
    return None


def parse_book(article, page_url):
    """يطلّع بيانات كتاب واحد. يرجّع None لو الـ HTML مش بالشكل المتوقع."""
    try:
        link = article.h3.a
        return {
            "title": link["title"],
            "url": urljoin(page_url, link["href"]),
            "price_text": article.select_one("p.price_color").text.strip(),
            "rating_text": article.select_one("p.star-rating")["class"][1],
            "availability": article.select_one("p.availability").text.strip(),
        }
    except (AttributeError, TypeError, KeyError, IndexError) as e:
        logger.warning("Could not parse a book on %s: %s", page_url, e)
        return None


def scrape_listing(start_url=BASE_URL, max_pages=None):
    """يمشي على صفحات القائمة بالـ pagination ويرجّع كل الكتب."""
    books = []
    url = start_url
    pages = 0

    while url:
        html = fetch(url)
        if html is None:
            break

        soup = BeautifulSoup(html, "lxml")
        for article in soup.select("article.product_pod"):
            book = parse_book(article, url)
            if book:
                books.append(book)

        pages += 1
        logger.info("Scraped page %d (%d books so far)", pages, len(books))
        if max_pages and pages >= max_pages:
            break

        next_link = soup.select_one("li.next a")
        url = urljoin(url, next_link["href"]) if next_link else None

    return books

def get_categories(base_url=BASE_URL):
    """يرجّع [(اسم التصنيف, لينكه)] من القائمة الجانبية."""
    html = fetch(base_url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "lxml")
    links = soup.select("div.side_categories ul.nav-list > li > ul > li > a")
    return [(a.get_text(strip=True), urljoin(base_url, a["href"])) for a in links]


def scrape_all(max_categories=None):
    """يمشي على كل تصنيف، ويضيف اسم التصنيف لكل كتاب."""
    books = []
    for name, url in get_categories()[:max_categories]:
        items = scrape_listing(url)
        for book in items:
            book["category"] = name
        logger.info("Category %-20s -> %d books", name, len(items))
        books.extend(items)
    return books