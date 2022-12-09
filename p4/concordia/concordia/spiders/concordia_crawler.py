import scrapy
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

count = 0


class ConcordiaSpider(scrapy.Spider):
    name = "concordia"
    allowed_domains = ['concordia.ca/ginacody']
    start_urls = ['https://www.concordia.ca/ginacody.html']

    def parse(self, response):
        # soup = BeautifulSoup(response.text, 'lxml')
        page = urlparse(response.url)
        filename = "test_html/" + page.path
        with open(filename, 'wb') as f:
            f.write(response.body)

        # links = soup.findAll('a', href=True)
        # for link in links:
        #     yield {
        #         'link': link['href']
        #     }
