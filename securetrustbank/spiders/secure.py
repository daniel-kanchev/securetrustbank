import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from securetrustbank.items import Article


class SecureSpider(scrapy.Spider):
    name = 'secure'
    start_urls = ['https://www.securetrustbank.com/our-news']

    def parse(self, response):
        links = response.xpath('//p[@class="readmore"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@title="Next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = response.xpath('//time/text()').get().strip()
        date = datetime.strptime(date, '%d %B %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@itemprop="articleBody"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
