# -*- coding: utf-8 -*-
import scrapy
import requests
import re
from urllib import parse
from scrapy.loader import ItemLoader
from WebOfScienceSpider.items import LiteratureItem

HEADERS = {
    'Origin': 'https://apps.webofknowledge.com',
    'Referer': 'https://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=R1ZsJrXOFAcTqsL6uqh&preferencesSaved=',
    'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    'Content-Type': 'application/x-www-form-urlencoded'
}
FORM_DATA = {
    'fieldCount': '2',    # 两条数据
    'action': 'search',
    'product': 'UA',
    'search_mode': 'GeneralSearch',
    # 'SID': sid,
    'max_field_count': '25',
    'formUpdated': 'true',
    # 'value(input1)': 'zhigui',
    # 'value(select1)': 'AU',
    # 'value(hidInput1)': '',
    # 'value(bool_1_2)': 'AND',
    # 'value(input2)': 'yangzhou',
    # 'value(select2)': 'AD',
    # 'value(hidInput2)': '',
    'limitStatus': 'collapsed',
    'ss_lemmatization': 'On',
    'ss_spellchecking': 'Suggest',
    'SinceLastVisit_UTC': '',
    'SinceLastVisit_DATE': '',
    'period': 'Range Selection',
    'range': 'ALL',
    'startYear': '1950',
    'endYear': '2018',
    'update_back2search_link_param': 'yes',
    'ssStatus': 'display:none',
    'ss_showsuggestions': 'ON',
    'ss_query_language': 'auto',
    'ss_numDefaultGeneralSearchFields': '1',
    'rs_sort_by': 'PY.D;LD.D;SO.A;VL.D;PG.A;AU.A'
}
ROOT_URL = 'https://apps.webofknowledge.com/WOS_GeneralSearch.do'


class WebofscienceSpider(scrapy.Spider):
    name = "webOfScience"
    allowed_domains = ["apps.webofknowledge.com/"]
    start_urls = ['http://apps.webofknowledge.com//']
    n = 0

    def __init__(self):
        self.hearders = HEADERS.copy()
        self.form_data = FORM_DATA.copy()
        self.root_url = ROOT_URL
        # self.seesion = requests.Session()

    def start_requests(self):
        name, school = self._get_condition()
        self.form_data.update({
            'SID': self._get_sid(),
            'value(input1)': name,
            'value(select1)': 'AU',
            'value(hidInput1)': '',
            'value(bool_1_2)': 'AND',
            'value(input2)': school,
            'value(select2)': 'AD',
            'value(hidInput2)': '',
        })
        return [scrapy.FormRequest(
            url=self.root_url,
            headers=self.hearders,
            formdata=self.form_data,
            callback=self.parse
        )]

    def parse(self, response):
        '''
        分析搜索结果页面的url，
        论文url传到parse_detail（）解析，
        如果有下一页，则访问下一页url，并传到parse（）分析下一页搜索结果页面的url。
        :param response:
        :return:
        '''
        urls = response.css('.smallV110::attr(href)').extract()
        next_page = response.css('.paginationNext::attr(href)').extract_first('')
        hearder = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Host': 'apps.webofknowledge.com',
            'Referer': response.url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
        }
        for url in urls:
            yield scrapy.Request(url=parse.urljoin(response.url, url), headers=hearder, dont_filter=True,
                callback=self.parse_detail)
        if next_page != 'javascript: void(0)':
            yield scrapy.Request(url=parse.urljoin(response.url, next_page), headers=hearder, dont_filter=True,
                callback=self.parse)

    def parse_detail(self, response):
        '''
        提取论文具体字段
        :param response:
        :return:
        '''
        with open('e:/a4.html', 'wb')as f:
            f.write(response.text.encode('utf-8'))
        WebofscienceSpider.n += 1
        print(WebofscienceSpider.n)

        # item_loader = ItemLoader(item=LiteratureItem, response=response)
        # item_loader.add_value('url', response.url)
        # item_loader.add_css('title', '.l-content .title value')
        # item_loader.add_css('author')
        # item_loader.add_css('source')
        # item_loader.add_css('source_info')
        # item_loader.add_css('doi')
        # item_loader.add_css('year')
        # item_loader.add_css('type')
        # item_loader.add_css('abstract')
        # item_loader.add_css('keyword')
        # item_loader.add_css('author_info')
        # item_loader.add_css('fund')
        # item_loader.add_css('publisher')
        # item_loader.add_css('imfact_factor')
        # item_loader.add_css('cite_num')
        # item_loader.add_css('cited_num')
        # item_loader.add_css('cited_180')
        # item_loader.add_css('cited_2013')
        # item_loader.add_css('crawl_time')
        # item_loader.add_css('update_time')


    def _get_condition(self):
        '''
        获取要爬的人名，学校名
        :return: name, school
        '''
        name = 'zhigui'
        school = 'yangzhou'
        return name, school

    def _get_sid(self):
        '''
        获取sid
        :return: sid
        '''
        url = 'http://www.webofknowledge.com/'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        response = requests.get(url=url, headers=headers)
        sid = re.findall('SID=\w+[^&]', response.url)[0].replace('SID=', '')
        return sid
