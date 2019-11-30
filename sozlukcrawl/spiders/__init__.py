# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider
from scrapy.exceptions import CloseSpider
import time

from ..utils import is_request_seen


class GenericSozlukSpider(Spider):
    """
    Her sozluk spider'inda ortak olan isleri burada topla.

    Yeni bir sozluk eklenmesi gerektigi zaman bu class'in genisletilip parse() methodunun
    yazilmasi yeterli.
    """


    def __init__(self, **kwargs):
        super(GenericSozlukSpider, self).__init__(**kwargs)

        if 'baslik' not in kwargs:
            raise CloseSpider('Baslik should be given to scrape')

        self.urls = kwargs['baslik'].split(',')
        self.allowed_domains = []

    def start_requests(self):
        self.logger.warning('Eliminating already seen web pages. If you think crawler is not working '
                 'please check "seen" table in the database')

        for i in self.urls:
            if not is_request_seen(scrapy.Request(url=i, callback=self.parse)):
                yield scrapy.Request(url=i, callback=self.parse, errback=self.error)
                        
                        
                
    def parse(self, response):
        raise NotImplementedError

    def error(self, response):
        raise NotImplementedError
