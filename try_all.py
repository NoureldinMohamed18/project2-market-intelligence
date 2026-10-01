import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

from src.scraper import scrape_all
from src.cleaner import clean_books, add_egp_prices
from src.api_client import get_gbp_to_egp

books = scrape_all()                   # أول مرة هياخد دقيقتين تقريباً بسبب الـ delay
clean, rejected = clean_books(books)

rate = get_gbp_to_egp()
clean = add_egp_prices(clean, rate)

print(len(books), len(clean), len(rejected))
print(clean[0])