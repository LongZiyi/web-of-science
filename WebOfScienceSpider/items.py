# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WebofsciencespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class LiteratureItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    source = scrapy.Field()
    source_info = scrapy.Field()
    doi = scrapy.Field()
    year = scrapy.Field()
    type = scrapy.Field()
    abstract = scrapy.Field()
    keyword = scrapy.Field()
    author_info = scrapy.Field()
    fund = scrapy.Field()
    publisher = scrapy.Field()
    imfact_factor = scrapy.Field()
    cite_num = scrapy.Field()
    cited_num = scrapy.Field()
    cited_180 = scrapy.Field()
    cited_2013 = scrapy.Field()
    crawl_time = scrapy.Field()
    update_time = scrapy.Field()

