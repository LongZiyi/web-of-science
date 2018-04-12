# -*- coding: utf-8 -*-
import scrapy
import requests
import re
import datetime
from urllib import parse
from scrapy.loader import ItemLoader
from WebOfScienceSpider.items import LiteratureItem
from WebOfScienceSpider.settings import SQL_DATETIME_FORMAT

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

        # 标题
        title = response.css(".l-content .title value::text").extract_first('')
        # 提取作者
        authors = response.xpath("//div[@class='l-content']//div[@class='block-record-info']/p[@class='FR_field']/span[@class='hitHilite']/text()").extract_first('')
        author_list = response.xpath("//div[@class='l-content']//div[@class='block-record-info']/p[@class='FR_field']/text()").extract()
        for i in author_list:
            if i != '\n' and i != '; ':
                res=re.search('^ \(.*\)$', i)
                if res is not None:
                    author = res.group().replace('(', '').replace(')', '').replace(' ', '')
                    authors = authors + '; ' + author
        # 期刊名
        source = response.css(".sourceTitle_txt value::text").extract_first('')
        # 期刊信息
        info_list = response.css('.block-record-info-source-values p')
        source_info = ''
        for i in info_list:
            num = i.css('value::text').extract_first('')
            name = i.css('span::text').extract_first('')
            if name == '卷:':
                source_info = source_info + num + '卷'
            if name == '期:':
                source_info = source_info + num + '期'
            if name == '页:':
                source_info = source_info + num + '页'
        # doi、出版年、文献类型
        rsp_list = response.xpath("//div[@class='block-record-info block-record-info-source']/p[@class='FR_field']")
        for i in rsp_list:
            name = i.xpath('span/text()').extract_first('')
            value = i.xpath('value/text()').extract_first('')
            if name == 'DOI:':
                doi = value
            if name == '出版年:':
                res = re.search('\d{4}', value)
                year = int(res.group())
            if name == '文献类型:':
                values = i.xpath('text()').extract()
                for value in values:
                    if value != '\n':
                        type = value
        # 摘要
        rsp_list = response.css(".l-content .block-record-info")
        for i in rsp_list:
            if i.css(".title3::text").extract_first('') == '摘要':
                abstract = i.css(".FR_field::text").extract_first('')
        # 关键词、出版商
        rsp_list = response.xpath("//div[@class='l-content']//div[@class='block-record-info']")
        keyword = ''
        for i in rsp_list:
            name = i.xpath("div[@class='title3']/text()").extract()
            for j in name:
                if j == '关键词':
                    key = i.xpath("p[@class='FR_field']/span[@class='FR_label']/text()").extract()
                    for k in key:
                        if k == '作者关键词:':
                            value = i.xpath("p[@class='FR_field']/a[@title='查找此作者关键词的更多记录']/text()").extract_first()
                            keyword = keyword + '作者关键词: ' + value + '; '
                        if k == 'KeyWords Plus:':
                            value = i.xpath("p[@class='FR_field']/a[@title='查找此扩展关键词的更多记录']/text()").extract_first()
                            keyword = keyword + 'KeyWords Plus: ' + value
                if j == '出版商':
                    publisher = i.xpath("p[@class='FR_field']/value/text()").extract_first()
        # 基金
        funds = ''
        rsp_list = response.xpath("//tr[@class='fr_data_row']")
        for i in rsp_list:
            fund = i.xpath("td/text()").extract_first()
            funds = funds + fund + ','
            fund_nums = i.xpath("td/div/text()").extract()
            for num in fund_nums:
                if j != '':
                    funds = funds + '(' + num + '); '
        # 被引频次、参考文献数量、最近180天、2013年至今
        rsp_list = response.xpath("//span[@class='large-number']/text()").extract()
        cited_2013 = int(rsp_list.pop())
        cited_180 = int(rsp_list.pop())
        cite_num = int(rsp_list.pop())
        cited_num = int(rsp_list.pop())
        # 爬取时间、更新时间
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        item_loader = ItemLoader(item=LiteratureItem(), response=response)
        item_loader.add_value('url', response.url)
        item_loader.add_value('title', title)
        item_loader.add_value('author', authors)
        item_loader.add_value('source', source)
        item_loader.add_value('source_info', source_info)
        item_loader.add_value('doi', doi)
        item_loader.add_value('year', year)
        item_loader.add_value('type', type)
        item_loader.add_value('abstract', abstract)
        item_loader.add_value('keyword', keyword)
        # item_loader.add_css('author_info')
        item_loader.add_value('fund', funds)
        item_loader.add_value('publisher', publisher)
        # item_loader.add_css('imfact_factor')
        item_loader.add_value('cite_num', cite_num)
        item_loader.add_value('cited_num', cited_num)
        item_loader.add_value('cited_180', cited_180)
        item_loader.add_value('cited_2013', cited_2013)
        item_loader.add_value('crawl_time', crawl_time)
        item_loader.add_value('update_time', update_time)

        literature_item = item_loader.load_item()
        yield literature_item

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
