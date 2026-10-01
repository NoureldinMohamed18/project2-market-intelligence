import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_price(text):
    """'£51.77' (أو 'Â£51.77' لو الترميز باظ) -> 51.77"""
    match = re.search(r"\d+(?:\.\d+)?", text or "")
    return float(match.group()) if match else None


def parse_rating(text):
    return RATING_MAP.get(text)


def clean_books(books):
    clean, rejected = [], []
    seen_urls = set()
    scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for book in books:
        # 1) تكرار (نفس اللينك)
        if book["url"] in seen_urls:
            continue
        seen_urls.add(book["url"])

        price = parse_price(book.get("price_text"))
        rating = parse_rating(book.get("rating_text"))
        title = (book.get("title") or "").strip()

        # 2) رفض الصفوف الناقصة مع السبب
        reason = None
        if not title:
            reason = "MISSING_TITLE"
        elif price is None or price <= 0:
            reason = "INVALID_PRICE"
        elif rating is None:
            reason = "INVALID_RATING"

        if reason:
            rejected.append({**book, "reject_reason": reason})
            continue

        clean.append({
            "title": title,
            "url": book["url"],
            "price_gbp": price,
            "rating": rating,
            "in_stock": "in stock" in book.get("availability", "").lower(),
            "scraped_at": scraped_at,
            "category": book.get("category"),
        })

    logger.info("Cleaned: %d ok | %d rejected | %d duplicates dropped",
                len(clean), len(rejected),
                len(books) - len(clean) - len(rejected))
    return clean, rejected

def add_egp_prices(books, rate):
    for book in books:
        book["fx_rate"] = rate
        book["price_egp"] = round(book["price_gbp"] * rate, 2) if rate else None
    return books