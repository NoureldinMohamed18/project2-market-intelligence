from src.cleaner import add_egp_prices, clean_books, parse_price, parse_rating


def book(**overrides):
    base = {
        "title": "Test Book",
        "url": "https://books.toscrape.com/catalogue/test_1/index.html",
        "price_text": "£10.00",
        "rating_text": "Three",
        "availability": "In stock",
        "category": "Travel",
    }
    base.update(overrides)
    return base


def test_parse_price_handles_pound_sign():
    assert parse_price("£51.77") == 51.77


def test_parse_price_handles_broken_encoding():
    assert parse_price("Â£51.77") == 51.77


def test_parse_price_returns_none_for_garbage():
    assert parse_price("free") is None
    assert parse_price(None) is None


def test_parse_rating_words():
    assert parse_rating("One") == 1
    assert parse_rating("Five") == 5
    assert parse_rating("Six") is None


def test_valid_book_is_cleaned():
    clean, rejected = clean_books([book()])
    assert len(clean) == 1 and not rejected
    assert clean[0]["price_gbp"] == 10.0
    assert clean[0]["rating"] == 3
    assert clean[0]["in_stock"] is True
    assert clean[0]["category"] == "Travel"


def test_duplicate_urls_are_dropped():
    clean, _ = clean_books([book(), book()])
    assert len(clean) == 1


def test_invalid_rows_are_rejected_with_reason():
    other = "https://books.toscrape.com/catalogue/other_2/index.html"
    clean, rejected = clean_books([
        book(rating_text="Six"),
        book(url=other + "a", price_text="n/a"),
        book(url=other + "b", title="  "),
    ])
    assert len(clean) == 0
    reasons = {r["reject_reason"] for r in rejected}
    assert reasons == {"INVALID_RATING", "INVALID_PRICE", "MISSING_TITLE"}


def test_out_of_stock_flag():
    clean, _ = clean_books([book(availability="Out of stock")])
    assert clean[0]["in_stock"] is False


def test_egp_price_is_calculated_and_rate_is_kept():
    clean, _ = clean_books([book(price_text="£10.00")])
    result = add_egp_prices(clean, 60.0)
    assert result[0]["price_egp"] == 600.0
    assert result[0]["fx_rate"] == 60.0


def test_missing_rate_leaves_egp_empty_without_crashing():
    clean, _ = clean_books([book()])
    result = add_egp_prices(clean, None)
    assert result[0]["price_egp"] is None