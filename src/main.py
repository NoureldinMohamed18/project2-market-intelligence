import logging
import sys
from pathlib import Path

from src.api_client import get_gbp_to_egp
from src.cleaner import add_egp_prices, clean_books
from src.report import print_report
from src.scraper import scrape_all
from src.storage import save


def setup_logging(log_dir="logs"):
    Path(log_dir).mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(f"{log_dir}/pipeline.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def run():
    logger = logging.getLogger("pipeline")
    logger.info("=== Pipeline started ===")

    books = scrape_all()
    if not books:
        raise RuntimeError("Scraper returned no books")

    clean, rejected = clean_books(books)

    rate = get_gbp_to_egp()
    if rate is None:
        logger.warning("No exchange rate: price_egp will be empty this run")
    clean = add_egp_prices(clean, rate)

    save(clean, rejected)
    print_report()
    logger.info("=== Pipeline finished successfully ===")


if __name__ == "__main__":
    setup_logging()
    try:
        run()
    except Exception:
        logging.getLogger("pipeline").exception("Pipeline failed")
        sys.exit(1)