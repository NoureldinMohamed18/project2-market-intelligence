from pathlib import Path
import requests
from bs4 import BeautifulSoup

URL="https://books.toscrape.com/"
response=requests.get(URL,timeout=10,headers={'User-AGENT':"Mozilla/5.0(learning project)"})

print("status code:",response.status_code)
response.raise_for_status()
response.encoding='utf-8'
Path('data/cache').mkdir(parents=True,exist_ok=True)
Path('data/cache/page1.html').write_text(response.text,encoding='utf-8')

soup=BeautifulSoup(response.text,'lxml')
books=soup.select('article.product_pod')
print('books on page :',len(books))

first=books[0]
print('title:',first.h3.a['title'])
print('price:',first.select_one('p.price_color').text)
print('rating class:',first.select_one('p.star-rating')['class'])
print('available:',first.select_one('p.availability').text.strip())
print('url:',first.h3.a['href'])