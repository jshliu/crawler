# -*- coding: utf-8 -*-

import sys
root_mod = '/home/jshliu/Project/zjld/fix/common/crawler'
sys.path.append(root_mod)
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.development");
django.setup()
import re
from datetime import datetime

from context.context import Context

Url = Context().get("Url")
SearchContentCrawler = Context().get("SearchContentCrawler")
FatherCrawler = Context().get("FatherCrawler")
Field = Context().get("Field") 


class BaiduCrawler(FatherCrawler):
    """
    百度新闻搜索爬虫，继承了通用一级爬虫类。

    """

    type = "baidu.news" #该爬虫的唯一标识符。

    child = SearchContentCrawler #指定生成的任务由哪一爬虫执行。

    item = Field(name="item", path="//div[@id='content_left']/div/div[@class='result']") #需要解析的字段，name为‘item’为特殊含义，不能被占用。
    pubtime = Field(name="pubtime", path="div//p[@class='c-author']/text()", type=datetime)
    url = Field(name="key", path="h3[@class='c-title']/a/@href", type=Url) #name为‘key’的字段是为下一爬虫找到指定网页的特征码，通常为url。
    title = Field(name="title", path="h3[@class='c-title']", type=str)
    publisher = Field(name="publisher", path="div//p[@class='c-author']/text()", type=str)
    count = Field(name="count", path="div//span[@class='c-info']/a[@class='c-more_link']/text()", type=str)
    page_size = Field(name="page_size", path="//span[@class='nums']/text()") #name为‘page_size’的字段是要爬取的总页数。
    origin_source = Field(name="origin_source", value=u"百度新闻搜索") #字段也可以不通过解析，直接被赋值。

    export_fields = [pubtime, title, publisher, count, origin_source] #要传递给下一爬虫的字段。
    export_key = True #是否要把name为‘key’的字段传递给下一爬虫

    def get_url(self, key, page):
        """
        获取要爬取网页的url。
        
        """
        if page == 1:
            return "http://news.baidu.com/ns?ct=0&rn=20&ie=utf-8&bs="+key+"&"\
                        "rsv_bp=1&sr=0&cl=2&f=8&prevct=no&tn=news&word="+key
        return "http://news.baidu.com/ns?word=%s&pn=%s&cl=2&ct=0&tn=news&rn="\
            "20&ie=utf-8&bt=0&et=0" % (key, str((page-1)*20))

    def dehydrate_publisher(self, value, current_url):
        """
        对解析后的字段进行加工。
        """
        return value.split(u"  ")[0].strip()

    def dehydrate_page_size(self, value, current_url):
        if value:
            value = value.replace(",", "")
            match = re.search(ur"找到相关新闻约(\d+)篇", value)
            if match:
                news_count = int(match.group(1))
                if news_count%10 == 0:
                    page_size = news_count/20
                else:
                    page_size = news_count/20 + 1
                if page_size > 38:
                    page_size = 38
                return page_size
        return 1 

    def dehydrate_count(self, value, current_url):
        try:
            count = int(count_str.split(u'条相同新闻',1)[0]) if count_str else 0
            return str(count)
        except:
            return 0

    @staticmethod
    def init(conf=None):
        pass
        # from xlutils.copy import copy
        # import xlrd
        # import os
        # SRC_PATH = os.path.dirname(__file__)
        # bk = xlrd.open_workbook(os.path.join(SRC_PATH,
        #                          "../../file/event.xls"))
        # sh = bk.sheet_by_name('Sheet1')
        # nrows = sh.nrows
        # ncols = sh.ncols
        # for i in xrange(1,nrows):

        #     source_type = sh.cell_value(i,1).strip()
        #     if source_type == '':
        #         continue
        #     data = {
        #         'source_type': source_type,
        #     }
            
        #     key = sh.cell_value(i,0).strip()
        #     Scheduler.schedule(EventCrawler.type ,key=str(key), 
        #                         data=data, interval=7200, reset=True)
        #     sogou_news = "sogou.newstitle"
        #     Scheduler.schedule(sogou_news ,key=str(key), 
        #                         data=data, interval=7200, reset=True)
        #     weibo = "weibo.newstitle"
        #     Scheduler.schedule(weibo ,key=str(key), 
        #                         data=data, interval=21600, reset=True)
        #     weixin = "sogou.keywords"
        #     Scheduler.schedule(weixin ,key=str(key), 
        #                         data=data, interval=7200, reset=True)


class SogouCrawler(FatherCrawler):

    type = "sogou.news"

    child = SearchContentCrawler

    item = Field(name="item", path="//div[@class='results']/div")
    pubtime = Field(name="pubtime", path="div/div[@class='news-detail']/div"\
            "[@class='news-info']/p[@class='news-from']/text()", type=datetime)
    url = Field(name="key", path="div/h3/a/@href", type=Url)
    title = Field(name="title", path="div/h3/a", type=str)
    publisher = Field(name="publisher", path="div/div[@class='news-detail']/"\
            "div[@class='news-info']/p[@class='news-from']/text()", type=str)
    count = Field(name="count", path="div/div[@class='news-detail']/div[@class"\
            "='news-info']/p[@class='news-txt']/a/text()", type=str)
    page_size = Field(name="page_size", path="//div[@class='mun']/text()")
    origin_source = Field(name="origin_source", value=u"搜狗新闻搜索")

    export_fields = [pubtime, title, publisher, count, origin_source]
    export_key = True

    @staticmethod
    def init(conf=None):
        pass

    def get_url(self, key, page):
        url = "http://news.sogou.com/news?mode=1&media=&"\
            "query=%s&time=0&clusterId=&sort=1&page=%s" % (key, str(page))
        return url

    def dehydrate_count(self, value, current_url):
        if value:
            value = value.split(u"条相同新闻")[0]
            value = value.split(">>")[1]
            count = int(value)
            return count
        return 0

    def dehydrate_page_size(self, value, current_url):
        if value:
            value = value.replace(",", "")
            match = re.search(ur"找到约(\d+)条结果", value)
            if match:
                news_count = int(match.group(1))
                if news_count%10 == 0:
                    page_size = news_count/10
                else:
                    page_size = news_count/10 + 1
                if page_size > 100:
                    page_size = 100
                return page_size 
        return 0
    
    def dehydrate_publisher(self, value, current_url):
        if value:
            return value.strip().split(" ")[0]
        return ""


if __name__ == "__main__":
    from apps.base.models import Task
    from json import dumps
    t = Task(key=u"杭州煤气汽车爆炸 1人死亡", data=dumps({"last_info": {"pubtime": "2015-1-1 00:00:00"}}), crawler="sogou.news", producer_id=1, category="event", application="yqj")
    t.save()
    # BaiduCrawler(t).crawl()
    # SogouCrawler(key="it168", data={"source": "sogou"}).crawl()