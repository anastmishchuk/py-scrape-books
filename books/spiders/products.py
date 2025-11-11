from urllib.parse import urljoin

import scrapy
from scrapy.http import Response

from books.items import BookItem


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]


    def parse(self, response: Response, **kwargs):
        for book_sel in response.css("article.product_pod h3 a"):
            book_url = book_sel.attrib["href"]
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            next_page_url = urljoin(response.url, next_page)
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_book(self, response):
        item = BookItem()
        item["title"] = response.css("div.product_main h1::text").get().strip()
        item["price"] = response.css("p.price_color::text").get().strip()
        avail_text = response.css("p.availability::text").getall()
        avail_text = [t.strip() for t in avail_text if t.strip()]
        if avail_text:
            item["amount_in_stock"] = avail_text[0]
        else:
            item["amount_in_stock"] = ""

        rating_class = response.css("p.star-rating").attrib.get("class", "")
        rating = rating_class.replace("star-rating", "").strip()
        item["rating"] = rating

        item["category"] = response.css("ul.breadcrumb li a::text").getall()[-1].strip()

        desc = response.xpath('//div[@id="product_description"]/following-sibling::p/text()').get()
        item["description"] = desc.strip() if desc else ""

        item["upc"] = response.xpath('//th[text()="UPC"]/following-sibling::td/text()').get().strip()

        yield item
