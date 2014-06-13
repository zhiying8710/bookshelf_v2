# encoding: utf-8
# Created on 2014-6-12
# @author: binge
from scrapy.selector import Selector
from spiders import base_spider, respotitory_info, analysis_spider_info
import logging
from util.item_helper import ItemHelper
from util import common, settings
import datetime

class qidian(base_spider):

    def __init__(self, **kwargs):
        base_spider.__init__(self)
        self.name = 'qidian'
        self.fn = kwargs['fn']
        self.url = kwargs['url']

        self.source_name = u'起点中文网'
        self.domain = 'http://www.qidian.com'
        now = datetime.datetime.now()
        self.year = str(now.year)
        self.month = str(now.month)
        self.day = str(now.day)
        self.gene_next_crawl_time = lambda (t) : (str(t.year) + '-' + str(t.month) + '-' + str(t.day) + ' ' + t.strftime('%X'))

        last_crawl_time_str = common.get_last_crawl_time(self.name)
        if not last_crawl_time_str:
            self.last_crawl_time = '%s-%s-%s 00:00:00' % (self.year, self.month, self.day)
            self.last_crawl_time_2 = '%s-%s-%s 00:00:00' % (self.year, self.month if len(self.month) == 2 else ('0' + self.month), self.day)
        else:
            self.last_crawl_time = last_crawl_time_str
            s_month = self.last_crawl_time.split('-')[1]
            if len(s_month) == 2:
                self.last_crawl_time_2 = self.last_crawl_time
            else:
                self.last_crawl_time_2 = self.last_crawl_time.replace(self.year + '-' + s_month, self.year + '-0' + s_month)
        self.source_short_name = 'qd'
        self.cls = 'spiders.qidian.qidian'

    @common.analysis()
    def start(self):
        hxs = Selector(text=self.content)
        book_nodes = hxs.xpath('//div[@class="sw1"] | //div[@class="sw2"]')
        is_continue = True
        if not book_nodes:
            self.log(message='can not get book nodes from %s start url.' % (self.name,), level=logging.WARNING)
            is_continue = False
        else:
            for bn in book_nodes:
                u_time = self.year[:2] + bn.xpath('div[@class="swe"]/child::text()').extract()[0] + ":00"
                if u_time >= self.last_crawl_time or u_time >= self.last_crawl_time_2:
                    source_tmp = bn.xpath('div[@class="swb"]/span[@class="swbt"]/a/@href').extract()[0]  # first link
                    source = source_tmp if source_tmp.startswith('http://') else (self.domain + source_tmp)
                    name = bn.xpath('div[@class="swb"]/span[@class="swbt"]/a/child::text()').extract()[0]  # book name
                    author = bn.xpath('div[@class="swd"]/a/child::text()').extract()[0]

                    yield respotitory_info(ItemHelper.gene_book_item(name, source, author, self.source_name, self.name, self.source_short_name))
                    yield analysis_spider_info(url = source, referer=self.url, _exec='%s.home' % self.cls)
                else:
                    is_continue = False  # if the section publish time is less than last crawl time, can't continue.
                    break
        if is_continue:
            next_page_nodes = hxs.xpath('//div[@class="storelistbottom"]/a[@class="f_s"]/following-sibling::a')
            if next_page_nodes:
                next_page = next_page_nodes[0].xpath('@href').extract()[0]
                yield analysis_spider_info(url=next_page, referer=self.url, _exec='%s.start' % self.cls, level=settings.spider_info_level_top)
            else:
                self.log(message='%s spider cannot get next page.' % (self.name, ), level=logging.WARNING)
        else:
            self.log(message='%s spider sleep wait for next round.' % self.name, level=logging.INFO)
            next_crawl_time = self.gene_next_crawl_time(datetime.datetime.now() - datetime.timedelta(minutes=settings.every_crawl_timedelta_mins))
            common.set_next_crawl_time(self.name, next_crawl_time)
            self.log('spider %s sleep %d seconds for next round.' % (self.name, settings.source_spider_sleep_secs))
            self.sleep(settings.source_spider_sleep_secs)
            yield analysis_spider_info(url=self.url, referer=None, _exec='%s.start' % self.cls)

    @common.analysis()
    def home(self):
        hxs = Selector(text=self.content)
