# Market Intelligence Pipeline

Scrapes a competitor bookstore, enriches prices with a live exchange rate from
a public API, stores the data in MongoDB, and generates pricing reports.

Target site: [books.toscrape.com](https://books.toscrape.com), a sandbox site
built for scraping practice.

## Problem
A retailer wants to monitor competitor prices without an official API, in
a currency their management understands (EGP).

## Architecture
books.toscrape.com --scrape--> clean --+--> MongoDB (books, books_rejected) --> report
exchange-rate API  --------------------+

## Features
- Walks every category and follows pagination via the "next" link, so it
  adapts if the site grows or shrinks
- Polite scraping: 1s delay between requests, timeout, retry with exponential backoff
- Local HTML cache: re-runs are instant and do not hit the site again
- A malformed book is logged and skipped; it never crashes the run
- Cleans price/rating text, drops duplicates, rejects invalid rows with a reason
- Stores `price_gbp`, `fx_rate` and `price_egp`, so price changes can be told
  apart from exchange-rate changes
- Idempotent load: upsert on `url`, with `first_seen_at` kept via `$setOnInsert`
- If the exchange-rate API fails the run continues with an empty `price_egp`
- MongoDB aggregation reports (average price by category, most expensive,
  best value)
- Unit tests that need neither network nor database

## Project Structure
(paste your tree here)

## How to Run
Requires Python 3.10+ and a local MongoDB (default `mongodb://localhost:27017`).

    pip install -r requirements.txt
    python -m src.main
    python -m pytest -v

Use another database by setting the `MONGO_URI` environment variable.

## Design Decisions
- Raw scraping and cleaning are separate modules, so a site layout change
  only touches the scraper.
- The exchange rate is cached per day because the API updates once daily
  and is rate limited.
- `url` is the unique key because a book has no other stable identifier.

## Limitations
- Scrapes one site; selectors are tied to its HTML
- Exchange rate is a daily reference rate, not a live trading rate

## Tech Stack
Python, requests, BeautifulSoup, MongoDB (PyMongo), pytest

## Attribution
Exchange rates by [Exchange Rate API](https://www.exchangerate-api.com).