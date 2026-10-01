import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

from src.scraper import scrape_listing
from src.cleaner import clean_books

books = scrape_listing()            # كل الصفحات (سريع بسبب الكاش)
clean, rejected = clean_books(books)

print(len(books), len(clean), len(rejected))
if clean:
    print(clean[0])
else:
    print("قائمة clean فارغة. لا توجد بيانات صالحة.")
    print("البيانات المرفوضة وأسباب الرفض:")
    print(rejected)