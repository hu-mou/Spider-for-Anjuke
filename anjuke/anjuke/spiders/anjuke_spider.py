from scrapy.spiders import Spider
from scrapy.http import Request
from bs4 import BeautifulSoup
import requests
from anjuke.items import AnjukeItem


class AnjukeSpider(Spider):

    name = "anjuke_spider"                                 #爬虫识别名
    def start_requests(self):           #初始准备
        star_url = 'http://cd.zu.anjuke.com/'            #初始页面
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
        }
        rawdata = requests.get(star_url, headers=headers)
        soup = BeautifulSoup(rawdata.text, 'lxml')
        indexlist = []                                     #创建储存大区域url的list
        urls=[]                                            #创建储存小区域url的list
        catalogLinks = soup.find('div', class_='items').find_all('a')
        for l in catalogLinks:
            indexlist.append(l.get('href'))
        for index in indexlist:                            #遍历大区域
            currentpage = index
            district_data = requests.get(index, headers=headers)
            soup = BeautifulSoup(district_data.text, 'lxml')
            if soup.find('div', class_='sub-items') == None:     #判断是否存在小区域
                urls.append(currentpage)
            else:
                district_Links = soup.find('div', class_='sub-items').find_all('a')
                for m in district_Links:
                    urls.append(m.get('href'))
        for url in urls:                                    #遍历小区域
            yield Request(url, callback=self.parse, dont_filter=True)

    def parse(self, response):   #解析页面

        item = AnjukeItem()
        Houses = response.css("#list-content > div.zu-itemmod")
        for eachHouse in Houses:

            title = eachHouse.css("div.zu-info > h3 > a::text").extract()
            address = eachHouse.css("div.zu-info > address > a::text").extract()+eachHouse.css("div.zu-info > address::text").extract()   #拼接地址
            detail = eachHouse.css("div.zu-info > p.details-item.tag::text").extract()
            price = eachHouse.css("div.zu-side > p > strong::text").extract()
            address = "".join(address)               #将list中字符串提取出来

            yield {
                'title': title,
                'address': address.replace(' ', '').replace('\n', ''),
                'detail': detail,
                'price': price,
                }
        nextLink = response.css("div.page-content > div.multi-page > a.aNxt::attr(href)")      #寻找下一页的url
        if len(nextLink) != 0:
            nextLink = nextLink.extract()
            nextLink = "".join(nextLink)                 #将list中的字符串提取出来
            yield Request(nextLink, callback=self.parse, dont_filter=True)
        else:
            return