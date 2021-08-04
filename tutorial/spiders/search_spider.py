import scrapy
import json
import logging
import json
from bs4 import BeautifulSoup

class SearchSpider(scrapy.Spider):
    name = 'search'
    keyword = ''
    Q = None

    def __init__(self, **kwargs):
        self.base_url = 'https://www.mercari.com'
        self.count = 0
        # self.keyword = 'CHANEL'
        
        super().__init__(**kwargs)

    def start_requests(self):
        self.Q.put('Start')
        yield self.mercari_scapy_request()
        
    def mercari_scapy_request(self):
        return scrapy.Request(
            '{}{}/'.format('https://www.mercari.com/jp/search/?keyword=', self.keyword),
            method="GET",
            callback=self.parse,
            dont_filter = True
        )
    def parse(self, response):
        div_item = '//section[has-class("items-box")]'

        items = response.xpath(div_item).getall()
        for item in items:
            pItem = BeautifulSoup(item, 'html.parser')
            vName = pItem.select_one('.items-box-name').get_text()
            vPrice = pItem.select_one('.items-box-price').get_text()
            vPhoto = pItem.select_one('.items-box-photo img')['data-src']
            vLink = '{}{}'.format(self.base_url, pItem.select_one('a')['href'])
            self.Q.put(json.dumps(
                {
                    'name': vName,
                    'link': vLink,
                    'price': vPrice,
                    'image': vPhoto
                }
            ))
            # yield {
            #     'name': vName,
            #     'link': vLink,
            #     'price': vPrice,
            #     'image': vPhoto
            # }
        yield self.mercari_scapy_request()
    def close(self, reason):
        self.Q.put('Stop')