# -*- coding: utf-8 -*-
__author__ = 'Eren Turkay <turkay.eren@gmail.com>'

import scrapy
from scrapy.exceptions import CloseSpider

from datetime import datetime

from . import GenericSozlukSpider
from ..items import Girdi
import time


class EksisozlukBaslikSpider(GenericSozlukSpider):
    name = 'eksisozluk'

    def __init__(self, **kwargs):
        super(EksisozlukBaslikSpider, self).__init__(**kwargs)

        self.allowed_domains = ['eksisozluk.com']
    
    def error(self, response):
        self.logger.info(response.request.url)
        self.logger.info("Retrying...")
        time.sleep(5)
        yield scrapy.Request(response.request.url, callback=self.parse, errback=self.error)


    def parse(self, response):
        self.logger.info("PARSING: %s" % response.request.url)

        items_to_scrape = response.xpath('//*[@id="topic"]/ul[@id="entry-item-list"]/li')
        if len(items_to_scrape) == 0:
            self.logger.error("!!! No item to parse found. It may indicate a problem with HTML !!!")
            raise CloseSpider('no_item_found')

        for sel in items_to_scrape:
            girdi_id = sel.xpath('./@data-id').extract()[0]
            baslik_id = response.xpath('//*[@id="title"]/a/@href').re(r'--(\d*)')[0]
            baslik = response.xpath('//*[@id="title"]/a/span/text()').extract()[0]
            date = sel.xpath('./footer/div[@class="info"]/a[@class="entry-date permalink"]/text()').re(r'\d{2}[.]\d{2}[.]\d{4} \d{2}[:]\d{2}')[0]
            text = sel.xpath('string(./div)').extract()[0]
            nick = sel.xpath('./footer/div[@class="info"]/a[@class="entry-author"]/text()').extract()[0]

            item = Girdi()
            item['source'] = self.name
            item['baslik'] = baslik
            item['girdi_id'] = girdi_id
            item['baslik_id'] = baslik_id
            item['datetime'] = datetime.strptime(date, '%d.%m.%Y %H:%M')
            item['text'] = text
            item['nick'] = nick

            yield item

        # Sozluk sayfalamayi javascript ile yapiyor, dolayisi ile sayfa linkini XPath ile alamiyoruz ancak kacinci
        # sayfada oldugumuz ve son sayfa html icerisinde yer aliyor. Bu bilgileri kullanarak crawl edilecek bir
        # sonraki sayfanin adresini belirle. SSG degistirmez umarim :(
        current_page = int(response.xpath('//*[@id="topic"]/div[@class="pager"]/@data-currentpage').extract()[0])
        page_count = int(response.xpath('//*[@id="topic"]/div[@class="pager"]/@data-pagecount').extract()[0])

        current_url = response.request.url.split('&p')[0]

        next_page = current_page + 1
        if page_count >= next_page:
        # if current_page < 1:
            yield scrapy.Request(url='%s&p=%s' % (current_url, next_page), callback=self.parse, errback=self.error)
