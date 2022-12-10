import scrapy
from bs4 import BeautifulSoup
from urllib.parse import urlparse

count = 0


class ConcordiaSpider(scrapy.Spider):
    name = "concordia"
    start_urls = ['https://www.concordia.ca/ginacody.html']

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        page = urlparse(response.url)
        filename = "test_html/" + page.path[10:].replace("/", "_")
        with open(filename, 'wb') as f:
            f.write(response.body)

        # Obeying robots apart from robots.txt Look at tag
        robot_tag = soup.find("meta", attrs={'name': 'robots'})

        links = soup.findAll('a', href=True)
        for link in links:
            if link is not None:
                url = link['href']
                if url.startswith("/ginacody") and robot_tag['content'] == "index,follow":
                    next_link = response.urljoin(url)
                    yield {
                        'Next link': next_link,
                        'url': url,
                        'robots_tag': robot_tag['content']
                    }
                    yield scrapy.Request(url=next_link, callback=self.parse)
