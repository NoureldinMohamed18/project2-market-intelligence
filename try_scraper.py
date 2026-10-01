import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

from src.scraper import scrape_listing

books = scrape_listing()       # 3 صفحات للتجربة بس
print(len(books))
print(books[0])
print(books[-1])