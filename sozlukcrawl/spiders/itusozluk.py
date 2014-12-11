# -*- coding: utf-8 -*-

from scrapy import Spider
from scrapy import log
from scrapy.http import Request
from scrapy.exceptions import CloseSpider

from ..items import Girdi
from ..utils import is_request_seen

class ItusozlukBaslikSpider(Spider):
    name = "itusozluk"

    def __init__(self, **kwargs):
        super(ItusozlukBaslikSpider, self).__init__(**kwargs)

        if 'urls' not in kwargs:
            raise CloseSpider('URL should be given to scrape')

        self.urls = kwargs['urls'].split(',')
        self.allowed_domains = ["itusozluk.com"]

    def start_requests(self):
        self.log('Eliminating already seen web pages. If you think crawler is not working '
                 'please check "seen" table in the database', level=log.WARNING)

        return [Request(i) for i in self.urls if not is_request_seen(Request(i))]

    def parse(self, response):
        self.log("PARSING: %s" % response.request.url, level=log.INFO)
        for sel in response.xpath('//*[@id="entries"]/li/article'):
            girdi_id = sel.xpath('./footer/div[@class="entrymenu"]/@data-info').extract()[0].split(',')[0]
            baslik_id = response.xpath('//*[@id="canonical_url"]/@value').re(r'--(\d*)')[0]
            baslik = response.xpath('//*[@id="title"]/a/text()').extract()[0]
            date = sel.xpath('./footer/div[2]/time/a/text()').re(r'\d{2}[.]\d{2}[.]\d{4}')[0]
            time = sel.xpath('./footer/div[2]/time/a/text()').re(r'\d{2}[:]\d{2}')[0]
            text = sel.xpath('string(./div)').extract()[0]
            nick = sel.css('a.yazarlink').xpath('text()').extract()[0]

            item = Girdi()
            item['source'] = self.name
            item['baslik'] = baslik
            item['girdi_id'] = girdi_id
            item['baslik_id'] = baslik_id

            # GG.AA.YYYY formatini YYYY.AA.GG formatina cevir. Veritabani bu formatta bekliyor.
            # DateTime modulu kullanilarak da yapilabilir ama ugrasmayalim simdi.
            reverse_date = date.split('.')
            reverse_date.reverse()
            item['date'] = '.'.join(reverse_date)

            item['time'] = time
            item['text'] = text
            item['nick'] = nick

            yield item

        current_url = response.request.url.split('/sayfa')[0]

        title_re = response.xpath('//title').re(r'sayfa (\d*)')
        current_page = int(title_re[0]) if title_re else 1

        page_count = int(response.xpath('//a[@rel="last"]')[0].xpath('text()').extract()[0])

        next_page = current_page + 1
        # if page_count >= next_page:
        if current_page < 2:
            yield Request('%s/sayfa/%s' % (current_url, next_page))