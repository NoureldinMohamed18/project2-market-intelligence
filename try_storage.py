import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

from src.scraper import scrape_all
from src.cleaner import clean_books, add_egp_prices
from src.api_client import get_gbp_to_egp
from src.storage import save

books = scrape_all()
clean, rejected = clean_books(books)
clean = add_egp_prices(clean, get_gbp_to_egp())

save(clean, rejected)
save(clean, rejected)        # مرتين عن قصد!