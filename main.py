import sys
import os
from scrapy.cmdline import execute


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# os.path.abspath(__file__) 获取当前模块路径
# os.path.dirname（） 获取父路径
# sys.path.append（） 把模块的路径添加到程序中

execute(['scrapy', 'crawl', 'webOfScience'])
