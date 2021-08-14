import scrapy
import json
import logging
import json
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from urllib.parse import parse_qs
from twisted.internet import reactor
from twisted.internet.defer import Deferred

class SearchSpider(scrapy.Spider):
    name = 'search'
    keyword = ''
    Q = None

    def __init__(self, **kwargs):
        self.base_url = 'https://www.mercari.com'
        self.count = 0
        self.page = 1
        self.max_page = 1
        self.firstScan = True
        self.oldItems = []
        
        super().__init__(**kwargs)

    def start_requests(self):
        self.Q.put('Start')
        yield self.mercari_scapy_request()
        
    def mercari_scapy_request(self):
        return scrapy.Request(
            'https://www.mercari.com/jp/search/?sort_order=created_desc&keyword={}'.format(self.keyword),
            method="GET",
            callback=self.parse,
            dont_filter = True
        )
    def parse(self, response):
        div_item = '//section[has-class("items-box")]'
        div_search_result = response.xpath('//div[has-class("search-result-number")]').get()
        if div_search_result is not None:
            items = response.xpath(div_item).getall()
            for item in items:
                pItem = BeautifulSoup(item, 'html.parser')
                vName = pItem.select_one('.items-box-name').get_text()
                vPrice = pItem.select_one('.items-box-price').get_text()
                vPhoto = pItem.select_one('.items-box-photo img')['data-src']
                vLink = '{}{}'.format(self.base_url, pItem.select_one('a')['href'])
                newItem = {
                    'name': vName,
                    'link': vLink,
                    'price': vPrice,
                    'image': vPhoto
                }
                self.Q.put(json.dumps(newItem))
            # yield self.mercari_scapy_request()
        self.Q.put('Scrapped')
        self.firstScan = False
    def close(self, reason):
        self.Q.put('Stop')