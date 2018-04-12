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
    doi_object_id = scrapy.Field()  # 主键
    year = scrapy.Field()
    type = scrapy.Field()
    abstract = scrapy.Field()
    keyword = scrapy.Field()
    # author_info = scrapy.Field()
    fund = scrapy.Field()
    publisher = scrapy.Field()
    # imfact_factor = scrapy.Field()
    cite_num = scrapy.Field()
    cited_num = scrapy.Field()
    cited_180 = scrapy.Field()
    cited_2013 = scrapy.Field()
    crawl_time = scrapy.Field()
    update_time = scrapy.Field()

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql="""
                    insert into literature(
                    url, title, author, source, source_info, doi, year, type, 
                    abstract, keyword, fund, publisher, cited_num, cite_num, cited_180, cited_2013, 
                    crawl_time, update_time
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE cited_num=VALUES(cited_num), cite_num=VALUES(cite_num), cited_180=VALUES(cited_180),
                      cited_2013=VALUES(cited_2013), update_time=VALUES(update_time)
                """

        url = self['url']
        title = self['title']
        author = self['author']
        source = self['source']
        source_info = self['source_info']
        doi = self['doi']
        year = self['year']
        type = self['type']
        abstract = self['abstract']
        keyword = self['keyword']
        fund = self['fund']
        publisher = self['publisher']
        cited_num = self['cited_num']
        cite_num = self['cite_num']
        cited_180 = self['cited_180']
        cited_2013 = self['cited_2013']
        crawl_time = self['crawl_time']
        update_time = self['update_time']

        params = (
            url, title, author, source, source_info, doi, year, type,
            abstract, keyword, fund, publisher, cited_num, cite_num, cited_180, cited_2013,
            crawl_time, update_time
        )

        return insert_sql, params
