from bs4 import BeautifulSoup

from src.scraper import parse_book

HTML = """
<article class="product_pod">
  <p class="star-rating Four"></p>
  <h3><a href="catalogue/some-book_1/index.html" title="Some Book">Some Bo...</a></h3>
  <div class="product_price">
    <p class="price_color">£23.50</p>
    <p class="instock availability">In stock</p>
  </div>
</article>
"""

PAGE = "https://books.toscrape.com/"


def test_parse_book_extracts_raw_fields():
    article = BeautifulSoup(HTML, "lxml").select_one("article.product_pod")
    book = parse_book(article, PAGE)
    assert book["title"] == "Some Book"
    assert book["price_text"] == "£23.50"
    assert book["rating_text"] == "Four"
    assert book["availability"] == "In stock"


def test_relative_link_becomes_absolute():
    article = BeautifulSoup(HTML, "lxml").select_one("article.product_pod")
    book = parse_book(article, PAGE)
    assert book["url"] == "https://books.toscrape.com/catalogue/some-book_1/index.html"


def test_broken_html_returns_none_instead_of_crashing():
    article = BeautifulSoup("<article class='product_pod'></article>", "lxml").select_one("article")
    assert parse_book(article, PAGE) is None