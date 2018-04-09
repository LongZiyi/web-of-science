from lxml import etree

with open('e:/a4.html', 'rb') as f:
    html = f.read().decode('utf-8')
s = etree.HTML(html)
ss =s.xpath("//div[@class='p-shop']/span/a")[0]
ss.values()[2]	# values有多个值
