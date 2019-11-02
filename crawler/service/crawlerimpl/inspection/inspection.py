#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
root_mod = '/home/jshliu/Project/zjld/fix/common/crawler'
sys.path.append(root_mod)

import re
import urllib
from HTMLParser import HTMLParser
from datetime import datetime
from lxml import etree

from context.context import Context

Url = Context().get("Url") 
fmt_time = Context().get("datetimeutil.fmt_time") 
local2utc = Context().get("datetimeutil.local2utc") 
convert_escape = clear_space = Context().get("textutil.convert_escape")
join_path = Context().get("pathutil.join_path")
ArticleContentCrawler = Context().get("ArticleContentCrawler")
FatherCrawler = Context().get("FatherCrawler")
Field = Context().get("Field") 
extract_xml = Context().get("htmlutil.extract_xml")
extract_html = Context().get("htmlutil.extract_html") 
Handler = Context().get("Handler")


class AhaicCrawler(FatherCrawler):
    type = "ahaic.inspection"

    item = Field(name="item", path=r"urls\[i\]=.*?imgstrs\[i\]=.*?;")
    url = Field(name="key", path=r"urls\[i\]='(.*?)';", type=Url)
    pubtime = Field(name="pubtime", path=r"year\[i\]='(\d{2,4})';.*?month\[i\]='(\d{1,2})';.*?day\[i\]='(\d{1,2})';", type=datetime)
    province = Field(name="province", value=u"安徽")
    publisher = Field(name="publisher", value=u"安徽省工商行政管理局")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, "\
                      "like Gecko) Chrome/42.0.2311.135 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "xxgk.ahaic.gov.cn",
        "Pragma": "no-cache",
    }
    xpath = {
        "title": "//td[@class='bt_content']/../preceding-sibling::tr[1]/td/div",
        "content": "//div[@id='san_txt']",
    }
    child = ArticleContentCrawler
    export_fields = [pubtime, province, publisher]


    def get_url(self, key, page):
        return "http://xxgk.ahaic.gov.cn/col/col166/index.html"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        url = value.group(1).strip()
        return join_path(current_url, url)

    def dehydrate_pubtime(self, value, current_url):
        pubtime = fmt_time(value.group(1)+" "+value.group(2)+" "+value.group(3))
        return local2utc(pubtime) if pubtime else None


# class AhqiCrawler(FatherCrawler):
#     type = "ahqi.inspection"

#     item = Field(name="item", path="//tr")
#     url = Field(name="key", path="td[1]/a/@href", type=Url)
#     pubtime = Field(name="pubtime", path="td[2]", type=datetime)
#     province = Field(name="province", value=u"安徽")
#     publisher = Field(name="publisher", value=u"安徽省质量技术监督局")

#     headers = {
#         "Cookie": "ant_stream_4ef1fcfab1d2a=1441121679/2659902512;"\
#             " ASPSESSIONIDSCDCTTSD=IPHKENDCABBCABDOFPPLKBLN; bow_s"\
#             "tream_4ef1fcfab1d2a=13",
#     }
#     xpath = {
#         "title": "/html/body/table/tr[1]/td",
#         "content": "/html/body/table/tr[4]/td/div",
#     }
#     export_fields = [pubtime, province, publisher]
#     child = ArticleContentCrawler
#     current_url = "http://www.ahqi.gov.cn/site/cpzlc/ahzj_site_newslist.html"


#     def get_url(self, key, page):
#         return "http://www.ahqi.gov.cn/inc/sitenewslist.asp?lid=241&sid=8&page=%s" % str(page)

#     def get_tree(self, response):
#         text = urllib.unquote(convert_escape(response.text))
#         return etree.HTML(text)

#     def dehydrate_key(self, value, current_url):
#         match = re.search(r"tid=(\d+)", value)
#         if not match:
#             raise RuntimeError("url is error!")
#         return "http://www.ahqi.gov.cn/inc/jdcccontent.asp?tid=%s" % match.group(1)


class AqsiqCrawler(FatherCrawler):
    type = "aqsiq.inspection"

    item = Field(name="item", path="/html/body/table[4]/tr/td[2]/table[1]/tr")
    url = Field(name="key", path="td[1]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[2]/font", type=datetime)
    province = Field(name="province", value=u"国家")
    publisher = Field(name="publisher", value=u"国家质量监督检验检疫总局")

    xpath = {
        "title": "/html/body/table[3]/tr/td/table[1]/tr/td/h1",
        "content": "//div[@class='TRS_Editor']",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler


    def get_url(self, key, page):
        return "http://www.aqsiq.gov.cn/xxgk_13386/jlgg_12538/ccgg/2015/"


class BdszjjCrawler(FatherCrawler):
    type = "bdszjj.inspection"

    item = Field(name="item", path="/html/body/table/tr/td[2]/table[2]/tr/td/table/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime)
    province = Field(name="province", value=u"河北")
    city = Field(name="city", value=u"保定")
    publisher = Field(name="publisher", value=u"保定市质量技术监督局")

    xpath = {
        "title": "//td[@class='t_15_gray']",
        "content": "//td[@class='w_13_gray']",
    }
    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler


    def get_url(self, key, page):
        if page == 1:
            return "http://www.bdszjj.com/fagui/zlcc/index.htm"
        return "http://www.bdszjj.com/fagui/zlcc/index_%s.htm" % str(page)


class BjtsbCrawler(FatherCrawler):
    type = "bjtsb.inspection"

    item = Field(name="item", path="//td[@class='td-dotline']")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path=".", type=datetime)
    city = Field(name="city", value=u"北京")
    publisher = Field(name="publisher", value=u"北京市质量技术监督局")

    xpath = {
        "title": "//div[@class='article-title']",
        "content": "//div[@id='zoom']",
    }
    export_fields = [pubtime, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.bjtsb.gov.cn/index.asp?page=%s&KindID=1422&LKindID=4&ClassID=" % str(page)


# class BqtsCrawler(FatherCrawler):
#     type = "bqts.inspection"

#     item = Field(name="item", path="//div[@id='right_1']/div[@class='border_no_top']/div[@class='list_out']")
#     url = Field(name="key", path="table/tr/td[1]/a/@href", type=Url)
#     pubtime = Field(name="pubtime", path="table/tr/td[4]", type=datetime)
#     province = Field(name="province", value=u"山西")
#     publisher = Field(name="publisher", value=u"山西省质量技术监督局")

#     headers = {
#          "Cookie": "PHPSESSID=r44pg8jecq2s4cd9icluj97jf3",
#     }
#     xpath = {
#         "title": "//div[@class='msg_sub']",
#         "content": "//div[@class='msg_content']",
#     }
#     export_fields = [pubtime, province, publisher]
#     child = ArticleContentCrawler


#     def get_url(self, key, page):
#         return "http://www.bqts.gov.cn/list.php?id=372&pageid=%s" % str(page)


class BxqiCrawler(FatherCrawler):
    type = "bxqi.inspection"

    item = Field(name="item", path="/html/body/table/tr/td/table/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    title = Field(name="title", path="td[2]/a", type=str)
    pubtime = Field(name="pubtime", path="td[3]/font", type=datetime, must=True)
    province = Field(name="province", value=u"辽宁")
    city = Field(name="city", value=u"本溪")
    publisher = Field(name="publisher", value=u"本溪市质量技术监督局")

    xpath = {
        "content": "/html/body/table/tr/td/table/tr[6]",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.bxqi.gov.cn/bxpro/bxqi/moreview.php?tiaojian=lb=%27%27&page=%s&v_jh=5" % str(page)

    def dehydrate_key(self, value, current_url):
        match = re.search(r'javascript:openwin\("(.*?)"\)', value.strip())
        if match:
            return match.group(1)
        return None        

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False 


class ChengduCrawler(FatherCrawler):
    type = "chengdu.inspection"

    item = Field(name="item", path="//tbody[@id='tbodyid']/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime)
    province = Field(name="province", value=u"四川")
    city = Field(name="city", value=u"成都")
    publisher = Field(name="publisher", value=u"成都市质量技术监督局")

    xpath = {
        "title": "//div[@class='msg_sub']",
        "content": "//div[@class='msg_content']",
    }
    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler


    def get_url(self, key, page):
        return "http://www.zjj.chengdu.gov.cn/cdzj/ztzl/ztzl_jdcc/"


# class CqnCrawler(FatherCrawler):
#     type = "cqn.inspection"

#     item = Field(name="item", path="//div[@class='Article_List_C_D']/li")
#     url = Field(name="key", path="a/@href", type=Url)
#     province = Field(name="province", value=u"全国")
#     publisher = Field(name="publisher", value=u"中国质量新闻网")

#     headers = {
#     }

#     xpath = {
#         "title": "//div[@class='Index_ShowDetail_Title']/h1",
#         "pubtime": "div[@class='Index_ShowDetail_Time']",
#         "content": "//div[@class='Index_ShowDetail_Content']",
#     }
#     export_fields = [province, publisher]
#     child = ArticleContentCrawler


#     def get_url(self, key, page):
#         return "http://www.cqn.com.cn/news/xfpd/ccgg/Index.html"


class CqzjCrawler(FatherCrawler):
    type = "cqzj.inspection"

    item = Field(name="item", path="//ul[@class='conright']")
    url = Field(name="key", path="li[@class='tit']/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="li[@class='last']", type=datetime)
    city = Field(name="city", value=u"重庆")
    publisher = Field(name="publisher", value=u"重庆市质量技术监督局")

    xpath = {
        "title": "//span[@id='Contentontrol_lblTitle']",
        "content": "//div[@class='con']",
    }
    export_fields = [pubtime, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.cqzj.gov.cn/ZJ_Page/List_All.aspx?levelid=1826&page=%s" % str(page)


class CzqtsCrawler(FatherCrawler):
    type = "czqts.inspection"

    item = Field(name="item", path="//div[@class='newslist']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    title = Field(name="title", path="a/text()", type=str)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"江苏")
    city = Field(name="city", value=u"常州")
    publisher = Field(name="publisher", value=u"常州市质量技术监督局")

    xpath = {
        "content": "//div[@id='content']",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.czqts.gov.cn/news_20_1.html"

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False 


class FjqiCrawler(FatherCrawler):
    type = "fjqi.inspection"

    item = Field(name="item", path="//div[@id='gl_content']/ul[@class='list']/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime)
    province = Field(name="province", value=u"福建")
    publisher = Field(name="publisher", value=u"福建省质量技术监督局")

    xpath = {
        "title": "//div[@class='xl_content']/h1",
        "content": "//div[@id='doc_content']",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.fjqi.gov.cn/xxgk/ccgg/fjccgg/"


class Fszj365Crawler(FatherCrawler):
    type = "fszj365.inspection"

    item = Field(name="item", path="//div[@id='NewsList']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"辽宁")
    city = Field(name="city", value=u"抚顺")
    publisher = Field(name="publisher", value=u"抚顺市质量技术监督局")

    xpath = {
        "title": "//div[@class='NewsTitle']",
        "content": "//div[@class='NewsContent']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.fszj365.gov.cn/list2.asp?t=1&s=26"


class GdqtsCrawler(FatherCrawler):
    type = "gdqts.inspection"

    item = Field(name="item", path="//div[@id='newsList']/div/table/tr")
    url = Field(name="key", path="td[@class='list_item align_LM']/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[@class='list_item align_CM']", type=datetime)
    province = Field(name="province", value=u"广东")
    publisher = Field(name="publisher", value=u"广东省质监局")

    xpath = {
        "title": "//div[@id='cTitle']",
        "content": "//div[@id='zoomcon']/div[@class='Custom_UnionStyle']",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(GdqtsCrawler.type, data={'source_type': u'抽检信息', "last_info": {"pubtime": datetime(2015,7,20)}
             #, "source": "gdqts"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.gdqts.gov.cn/zjxx/jdcctb/"


class GszlCrawler(FatherCrawler):
    type = "gszl.inspection"

    item = Field(name="item", path="//ul[@class='list']/li")
    url = Field(name="key", path="a[2]/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime)
    province = Field(name="province", value=u"甘肃")
    publisher = Field(name="publisher", value=u"甘肃省质量技术监督局")

    xpath = {
        "title": "//div[@class='content']/h1",
        "content": "//div[@id='content']",
    }
    start_page = 0
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 0:
            return "http://www.gszl.gov.cn/tzgg/ccgg/index.html"
        return "http://www.gszl.gov.cn/tzgg/ccgg/index%s.html" % str(page)


class GuangzhouaicCrawler(FatherCrawler):
    type = "guangzhouaic.inspection"

    item = Field(name="item", path="//table[@class='tbbg']/tr/td[2]/table/tr[2]/td[1]/table[1]/tr")
    url = Field(name="key", path="td[1]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[2]", type=datetime)
    province = Field(name="province", value=u"广东")
    city = Field(name="city", value=u"广州")
    publisher = Field(name="publisher", value=u"广州市工商行政管理局")

    xpath = {
        "title": "//td[@class='content-title']",
        "content": "//td[@class='content-gray14-top']",
    }
    start_page = 0
    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 0:
            return "http://www.gzaic.gov.cn/jrgs/sfjs/index.htm"
        return "http://www.gzaic.gov.cn/jrgs/sfjs/index_%s.htm" % str(page)


class GxqtsCrawler(FatherCrawler):
    type = "gxqts.inspection"

    item = Field(name="item", path="//form[@name='PageForm']/table/tr")
    url = Field(name="key", path="td[1]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[2]/p", type=datetime)
    province = Field(name="province", value=u"广西壮族自治区")
    publisher = Field(name="publisher", value=u"广西壮族自治区质量技术监督局")

    xpath = {
        "title": "//td[@class='title2']",
        "content": "//font[@id='zoom']",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(GxqtsCrawler.type, data={'source_type': u'抽检信息', "last_info": {"pubtime": datetime(2015,7,20)}
             #, "source": "gxqts"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.gxqts.gov.cn/new/cata2.php?cata2_id=33&act=1"


class GzaicCrawler(FatherCrawler):
    type = "gzaic.inspection"

    item = Field(name="item", path="//table[@class='tbstyle']/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime)
    title = Field(name="title", path="td[2]/a/text()", must=True)
    province = Field(name="province", value=u"贵州")
    publisher = Field(name="publisher", value=u"贵州省工商行政管理局")

    xpath = {
        "title": "//div[@class='newsShow']/h1",
        "content": "//div[@class='newsConts']",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.gzaic.org.cn/html/xxgkListData.jsp?sort=10&m=77&page=%s" % str(page)


    def dehydrate_title(self, value, current_url):
        if not re.search(ur"抽|查", value):
            return None
        else:
            return value


class GzqCrawler(FatherCrawler):
    type = "gzq.inspection"

    item = Field(name="item", path="//div[@class='user_message_list']/table/tr")
    url = Field(name="key", path="td[@class='td1']/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[@class='td2']", type=datetime)
    province = Field(name="province", value=u"广东")
    city = Field(name="city", value=u"广州")
    publisher = Field(name="publisher", value=u"广州市质量技术监督局")

    xpath = {
        "title": "//div[@class='mai']/div[@class='top']",
        "content": "//div[@id='new_content_txt']",
    }
    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.gzq.gov.cn/public/message_list.jsp?catid=825|835|847"

    def get_req_data(self, key, page):
        return {"pageno": page, "catid": "825|835|847",}


class GzqtsCrawler(FatherCrawler):
    type = "gzqts.inspection"

    item = Field(name="item", path="//div[@class='listCont']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime)
    province = Field(name="province", value=u"贵州")
    publisher = Field(name="publisher", value=u"贵州省质量技术监督局")

    xpath = {
        "title": "//div[@class='contTextBox']/h3",
        "content": "//div[@class='detail_main_content']",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 1:
            return "http://www.gzqts.gov.cn/zjxw/zjgg/ccgg/index.shtml"
        return "http://www.gzqts.gov.cn/zjxw/zjgg/ccgg/index_%s.shtml" % str(page)


class HaaicCrawler(FatherCrawler):
    type = "haaic.inspection"

    item = Field(name="item", path="//div[@id='86173']/div/div/table")
    url = Field(name="key", path="tr/td/a[@class='bt_link']/@href", type=Url)
    pubtime = Field(name="pubtime", path="tr/td[4]", type=datetime)
    province = Field(name="province", value=u"河南")
    publisher = Field(name="publisher", value=u"河南省工商行政管理局")

    xpath = {
        "title": "//td[@class='txt_bt']",
        "content": "//div[@id='zoom']",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.haaic.gov.cn/col/col20/index.html"


class HainanCrawler(FatherCrawler):
    type = "hainan.inspection"

    item = Field(name="item", path="//dt[@class='ny_news']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime)
    province = Field(name="province", value=u"海南")
    publisher = Field(name="publisher", value=u"海南省质监局")

    xpath = {
        "title": "//div[@class='ny_bt']",
        "content": "//div[@class='TRS_Editor']",
    }
    export_fields = [pubtime, province, publisher]
    start_page = 0
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 0:
            return "http://qtsb.hainan.gov.cn/qtsb/yw_pd/sjcs/zfyjdc/dtxx/index.html"
        return "http://qtsb.hainan.gov.cn/qtsb/yw_pd/sjcs/zfyjdc/dtxx/index_%s.html" % str(page)


class HaqiCrawler(FatherCrawler):
    type = "haqi.inspection"

    item = Field(name="item", path="//td[@class='xin2zuo']/table/tr[@height='20']")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime)
    province = Field(name="province", value=u"河南")
    publisher = Field(name="publisher", value=u"河南省质量技术监督局")

    xpath = {
        "title": "//div[@class='title7']",
        "content": "//font[@id='zoom']",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.haqi.gov.cn/getHtmlInDivNormal.do?ajaxform"

    def get_req_data(self, key, page):
        return {
            "gwcsCode": "undefined",
            "divId": "402881f92229ce2b012229d1d5ad0001pagelist",
            "requestUrl": "http://www.haqi.gov.cn/viewCmsCac.do",
            "affairCategory": "",
            "cacId": "ff808081257bb6fa01257cc52a1e02c2",
            "cdid": "",
            "key": "",
            "offset": 0,
        }


class Hd315Crawler(FatherCrawler):
    type = "hd315.inspection"

    item = Field(name="item", path="//div[@class='bor8']/table[@class='listtb']/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]/span", type=datetime)
    city = Field(name="city", value=u"北京")
    publisher = Field(name="publisher", value=u"北京工商局")

    xpath = {
        "title": "//td[@class='title21']",
        "content": "//table[@class='dt14l26']",
    }
    export_fields = [pubtime, city, publisher]
    start_page = 0
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 0:
            return "http://www.hd315.gov.cn/xxgk/spzlgs/index.htm"
        return "http://www.hd315.gov.cn/xxgk/spzlgs/index_%s.htm" % str(page)


class HebqtsCrawler(FatherCrawler):
    type = "hebqts.inspection"

    item = Field(name="item", path="/html/body/div[2]/table/tr/td[1]/table/tr/td/div/table[1]/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime)
    province = Field(name="province", value=u"河北")
    publisher = Field(name="publisher", value=u"河北省质量技术监督局")

    xpath = {
        "title": "//td[@class='biaoti']",
        "content": "//td[@class='zhengwen']",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.hebqts.gov.cn/xxgk/zlcc/index.shtml?pageNo=%s" % str(page)


class HefeiCrawler(FatherCrawler):
    type = "hefei.inspection"

    item = Field(name="item", path="/html/body/table[6]/tbody/tr/td[2]/table[2]/tbody/tr[1]/td/table/tbody/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"安徽")
    city = Field(name="city", value=u"合肥")
    publisher = Field(name="publisher", value=u"合肥市质量技术监督局")

    start_page = 0
    xpath = {
        "title": "//td[@class='news_font']",
        "content": "//td[@class='news_font']/../../following-sibling::table[1]/tr[1]/td[@class='news_font2']",
    }
    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 0:
            return "http://zjj.hefei.gov.cn/10239/10243/"
        return "http://zjj.hefei.gov.cn/10239/10243/index_%s.html" % str(page)


class Hld12365Crawler(FatherCrawler):
    type = "hld12365.inspection"

    item = Field(name="item", path="//ul[@class='c_l']/li")
    url = Field(name="key", path="a/@href", type=Url)
    title = Field(name="title", path="a/@title", type=str)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"辽宁")
    city = Field(name="city", value=u"葫芦岛")
    publisher = Field(name="publisher", value=u"葫芦岛市质量技术监督局")

    xpath = {
        "content": "//div[@class='pagecon']",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.hld12365.gov.cn/list.asp?cid=4358"

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False


class HljqtsCrawler(FatherCrawler):
    type = "hljqts.inspection"

    item = Field(name="item", path="/html/body/table[1]/tr/td/table/tr/td[2]/table[3]/tr[2]/td/table/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    title = Field(name="title", path="td[2]/a/@title", must=True)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"黑龙江")
    publisher = Field(name="publisher", value=u"黑龙江省质量技术监督局")

    xpath = {
        "title": "//h1[@class='style6']",
        "content": "/html/body/div[2]/table[3]/tr[2]/td",
    }
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.hljqts.gov.cn/zwxx/zjxx/qwfb/zlcc/"

    def dehydrate_title(self, value, current_url):
        if not re.search(ur"抽|查", value):
            return None
        else:
            return value


class Hn315Crawler(FatherCrawler):
    type = "hn315.inspection"

    item = Field(name="item", path="//INFO")
    url = Field(name="key", path="InfoURL/text()", type=Url)
    pubtime = Field(name="pubtime", path="PublishedTime/text()", type=datetime, must=True)
    province = Field(name="province", value=u"湖南")
    publisher = Field(name="publisher", value=u"湖南省质量技术监督局")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "\
                      "(KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
    }
    xpath = {
        "title": "//div[@id='contenttitle']",
        "content": "//div[@id='content']",
    }
    current_url = "http://www.hn315.gov.cn/publicfiles/business/htmlfiles/"
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.hn315.gov.cn/publicfiles//business/htmlfiles/hnzjj/s179/index.html"

    def get_tree(self, response):
        tree = etree.fromstring(extract_xml(response.content))
        return tree


class Hnaicrawler(FatherCrawler):
    type = "hnaic.inspection"

    item = Field(name="item", path="//div[@id='biaoge']/ul/li[@class='biaotou3']")
    url = Field(name="key", path="preceding-sibling::li[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path=".", type=datetime, must=True)
    province = Field(name="province", value=u"湖南")
    publisher = Field(name="publisher", value=u"湖南省工商行政管理局")

    xpath = {
        "title": "//div[@id='read_center']/div[@class='yuedu_kuangzi']/"\
            "div[@class='yuedu_biaoti']",
        "content": "//div[@id='content']",
    }
    current_url = "http://www.hnaic.net.cn/visit/placard/a/viewhnaic?placardId=257&unitecodeIndex=430000"
    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.hnaic.net.cn/visit/board/a/listhnaicplacards?"\
            "boardId=106&unitecodeIndex=430000&currentP=%s" % str(page)

    def get_tree(self, response):
        tree = etree.HTML(extract_html(response.text))
        return tree


class Hnyy12365crawler(FatherCrawler):
    type = "hnyy12365.inspection"

    item = Field(name="item", path="//ul[@id='tr']/li")
    url = Field(name="key", path="a/@href", type=Url)
    title = Field(name="title", path="a/@title", type=str)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"湖南")
    city = Field(name="city", value=u"益阳")
    publisher = Field(name="publisher", value=u"益阳市质监局")

    xpath = {
        "title": "//li[@class='index_1_1']",
        "content": "//li[@id='astCont']",
    }
    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.hnyy12365.gov.cn/NewsList.aspx?Categoryid=3964A082-C62D-47DA-9A7A-3D378F1B1A1B"

    def filter(self, key, data):
        if re.search(ur"抽|查", data["title"]):
            return True
        return False


class HszjjCrawler(FatherCrawler):
    type = "hszjj.inspection"

    item = Field(name="item", path="//td[@class='lanmutab3']/table/tr")
    url = Field(name="key", path="td[@class='hei']/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[@class='hei']", type=datetime, must=True)
    province = Field(name="province", value=u"河北")
    city = Field(name="city", value=u"衡水")
    publisher = Field(name="publisher", value=u"衡水市质量技术监督网")

    xpath = {
        "title": "//td[@class='neiyetab']/table/tr[3]/td/h2/font",
        "content": "//td[@class='neirong']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.hszjj.gov.cn/zlcc/index.shtml"


class JhbtsCrawler(FatherCrawler):
    type = "jhbts.inspection"

    item = Field(name="item", path="//td[@class='biankuan']/table/tr[@class='l-dian1']")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"金华")
    publisher = Field(name="publisher", value=u"金华市质量技术监督局")

    xpath = {
        "title": "//td[@class='title']",
        "content": "//div[@id='article']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.jhbts.gov.cn/column.asp?/=2,16&page=%s" % str(page)


class JiangxizjCrawler(FatherCrawler):
    type = "jiangxizj.inspection"

    item = Field(name="item", path="//div[@class='sub_list']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="i", type=datetime, must=True)
    province = Field(name="province", value=u"江西")
    publisher = Field(name="publisher", value=u"江西省质量技术监督局")

    xpath = {
        "title": "//li[@class='show_title']",
        "content": "//div[@id='zoom']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.jxzj.gov.cn/jxzj/lanmu4two/zwgk_zlcc.jsp?tag=mynav2&"\
            "id=1000010004&pn=%s" % str(page)


class JlqiCrawler(FatherCrawler):
    type = "jlqi.inspection"

    item = Field(name="item", path="//table[@class='tdBorderfb812a']/tr/td/table[2]/tr")
    title = Field(name="title", path="td[2]/a/text()", must=True)
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"吉林")
    publisher = Field(name="publisher", value=u"吉林省质量技术监督局")

    xpath = {
        "title": "//div[@class='infoDetailTitle']",
        "content": "//div[@id='infoDetail0']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.jlqi.gov.cn/index/infoList1.jsp?nodeID=798&DICA=%BC%E0%B6%BD"

    def dehydrate_title(self, value, current_url):
        if not re.search(ur"方案", value):
            return value
        else:
            return None


class JnqtsCrawler(FatherCrawler):
    type = "jnqts.inspection"

    item = Field(name="item", path="urls\[i\]=.*?imgstrs\[i\]=.*?;")
    url = Field(name="key", path="urls\[i\]='(.*?)';", type=Url)
    pubtime = Field(name="pubtime", path="year\[i\]='(\d{2,4})';.*?month\[i\]='(\d{1,2})';.*?day\[i\]='(\d{1,2})';", type=datetime, must=True)
    province = Field(name="province", value=u"山东")
    city = Field(name="city", value=u"济南")
    publisher = Field(name="publisher", value=u"济南市质量技术监督局")

    xpath = {
        "title": "//table[@id='article']/tr[2]/td",
        "content": "//td[@id='zoom']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.jnqts.gov.cn/col/col57/index.html"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            url = value.group(1).strip()
            return join_path(current_url, url)
        return None

    def dehydrate_pubtime(self, value, current_url):
        if value:
            pubtime = fmt_time(value.group(1)+" "+value.group(2)+" "+value.group(3))
            return local2utc(pubtime) if pubtime else None
        return None

#content has problem !
class JsqtsCrawler(FatherCrawler):
    type = "jsqts.inspection"

    item = Field(name="item", path="//table[@id='MoreinfoList1_DataGrid1']/tr[not(@align)]")
    url = Field(name="key", path="td[1]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"江苏")
    publisher = Field(name="publisher", value=u"江苏质监信息网")

    headers = {
        "Cookie": "ASP.NET_SessionId=nsuw5c55hnwygv55jx3ory45; __CSRFCOOKIE=b0a7b49f-c4f4-4ae8-9dc8-a0b454ab240e",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
        "Referer": "http://www.jsqts.gov.cn/zjxx/GovInfoPub/Department/moreinfo.aspx?categoryNum=001010",
    }
    xpath = {
        "title": "//span[@id='InfoDetail1_lblTitle']",
        "content_url": "//iframe[@id='navFrameContent']/@src",
        "content": "//span[@id='spnContent']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_req_data(self, key, page):
        return {
            "__CSRFTOKEN": "/wEFJGIwYTdiNDlmLWM0ZjQtNGFlOC05ZGM4LWEwYjQ1NGFiMjQwZQ==",
            "__VIEWSTATE": "Pjlw1CGDCbtVLV+LZoVt41BaF8ihweGq",
            "MoreinfoList1$syh": "",
            "MoreinfoList1$xxname": "",
            "MoreinfoList1$year": u"请选择",
            "MoreinfoList1$select1": u"请选择",
            "__EVENTTARGET": "MoreinfoList1$Pager",
            "__EVENTARGUMENT": page,
            "__VIEWSTATEENCRYPTED": "",
        }

    def get_url(self, key, page):
        return "http://www.jsqts.gov.cn/zjxx/GovInfoPub/Department/moreinfo.aspx?categoryNum=001010"


class JxzjCrawler(FatherCrawler):
    type = "jxzl.inspection"

    item = Field(name="item", path="//div[@class='news_title']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    title = Field(name="title", path="a/text()", must=True)
    pubtime = Field(name="pubtime", path="div[1]", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"嘉兴")
    publisher = Field(name="publisher", value=u"嘉兴市质量技术监督局")

    xpath = {
        "title": "//div[@class='big_tit']",
        "content": "//div[@class='content_box']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 1:
            return "http://www.jxzl.gov.cn/notice.htm"
        return "http://www.jxzl.gov.cn/notice_%s.htm" % str(page)

    def dehydrate_title(self, value, current_url):
        if not re.search(ur"抽|查", value):
            return None
        else:
            return value


class LanzhouCrawler(FatherCrawler):
    type = "lanzhou.inspection"

    item = Field(name="item", path="//ul[@class='list']/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"甘肃")
    city = Field(name="city", value=u"兰州")
    publisher = Field(name="publisher", value=u"兰州质监局")

    xpath = {
        "title": "//div[@class='content']/h1",
        "content": "//div[@id='content']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://zjj.lanzhou.gov.cn/nsjg/jcc_4022/tzwj_4024/"


class LnzjCrawler(FatherCrawler):
    type = "lnzj.inspection"

    item = Field(name="item", path="//table[@id='hbTable3']/tbody/tr[@height='21']")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"辽宁")
    publisher = Field(name="publisher", value=u"辽宁省质量技术监督局")

    xpath = {
        "title": "//td[@class='font131']",
        "content": "//td[@id='Zoom']",
    }

    export_fields = [pubtime, province, publisher]
    start_page = 0
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 0:
            return "http://www.12365.ln.cn/zljd/jdccgg/index.html"
        return "http://www.12365.ln.cn/zljd/jdccgg/index_%s.html" % str(page)


class NjzjCrawler(FatherCrawler):
    type = "njzj.inspection"

    item = Field(name="item", path="//div[@id='12068']/div/table")
    url = Field(name="key", path="tr/td[2]/a/@href", type=Url)
    title = Field(name="title", path="tr/td[2]/a/text()", type=str)
    pubtime = Field(name="pubtime", path="tr/td[@class='bt_time']", type=datetime, must=True)
    province = Field(name="province", value=u"江苏")
    city = Field(name="city", value=u"南京")
    publisher = Field(name="publisher", value=u"南京质监门户网站")

    xpath = {
        "content": "//div[@id='zoom']",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.njzj.gov.cn/col/col1887/index.html"

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False


class NmgzjjCrawler(FatherCrawler):
    type = "nmgzjj.inspection"

    item = Field(name="item", path="//div[@class='cont_01 border01']/div[1]/table/tr[@height='60']")
    url = Field(name="key", path="td[4]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[6]", type=datetime, must=True)
    province = Field(name="province", value=u"内蒙古自治区")
    publisher = Field(name="publisher", value=u"内蒙古自治区质量技术监督局")

    xpath = {
        "title": "//div[@class='div_2']/h2",
        "content": "//div[@id='ma_wangyanjie']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.nmgzjj.gov.cn/open/directory/171/%s" % str(page)


class NxzjCrawler(FatherCrawler):
    type = "nxzj.inspection"

    item = Field(name="item", path="/html/body/table[6]/tr/td[2]/table/tr/td/table/tr")
    url = Field(name="key", path="td[1]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[2]", type=datetime, must=True)
    province = Field(name="province", value=u"宁夏")
    publisher = Field(name="publisher", value=u"宁夏质量技术监督局")

    xpath = {
        "title": "/html/body/table[4]/tr[2]/td/table/tr[1]/td/font",
        "content": "/html/body/table[4]/tr[2]/td/table/tr[3]/td/table/tr/td",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.nxzj.gov.cn/listinfo.asp?colid=27"


class QdqtsCrawler(FatherCrawler):
    type = "qdqts.inspection"

    item = Field(name="item", path="//table[@class='tb_kuang']/tr/td/table[3]/tr/td/table/tr/td/table[1]/tr/td")
    url = Field(name="key", path="a/@href", type=Url)
    title = Field(name="title", path="a/text()", type=str)
    pubtime = Field(name="pubtime", path=".", type=datetime, must=True)
    province = Field(name="province", value=u"山东")
    city = Field(name="city", value=u"青岛")
    publisher = Field(name="publisher", value=u"青岛金质网")

    xpath = {
        "content": "//table[@class='tb_kuang']/tr/td/table[3]/tr/td/table/tr/td/table/tr[2]",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.qdqts.gov.cn/news.asp?page=%s&newstype=3" % str(page)

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False


class QzbtsCrawler(FatherCrawler):
    type = "qzbts.inspection"

    item = Field(name="item", path="//table[@class='dottedsubject']/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    title = Field(name="title", path="td[2]/a/@title", type=str)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"衡州")
    publisher = Field(name="publisher", value=u"衡州市质监局")

    xpath = {
        "content": "//td[@class='table3']/table[2]/tr/td/table/tr[3]/td",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.qzbts.gov.cn/article.asp?c_id=71&page=%s" % str(page)

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False 


class SaicCrawler(FatherCrawler):
    type = "saic.inspection"

    item = Field(name="item", path="//div[@class='filterchangeindex']/table[2]/\
        tr/td[2]/table/tr/td/table[2]/tr[3]/td/table/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]/font", type=datetime, must=True)
    province = Field(name="province", value=u"全国")
    publisher = Field(name="publisher", value=u"中华人民共和国国家国家工商行政管理总局")

    xpath = {
        "title": "//td[@class='blue_dzi']",
        "content": "//td[@id='zoom']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 0:
            return "http://www.saic.gov.cn/jgzf/spzljg/index.html"
        return "http://www.saic.gov.cn/jgzf/spzljg/index_%s.html" % str(page)


class ScaicCrawler(FatherCrawler):
    type = "scaic.inspection"

    item = Field(name="item", path="//div[@id='wzlm']/ul[@class='list']/li")
    url = Field(name="key", path="a/@href", type=Url)
    title = Field(name="title", path="a/text()", must=True)
    pubtime = Field(name="pubtime", path="span[@class='more']", type=datetime, must=True)
    province = Field(name="province", value=u"四川")
    publisher = Field(name="publisher", value=u"四川省工商行政管理局")

    xpath = {
        "title": "//div[@class='nr_content']/h2",
        "content": "//div[@class='nr_content']/div[@class='con']",
    }

    export_fields = [pubtime, province, publisher]
    start_page = 0;
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 0:
            return "http://www.scaic.gov.cn/zwgk/gsgg/zcgg/index.html"
        return "http://www.scaic.gov.cn/zwgk/gsgg/zcgg/index_%s.html" % str(page)

    def dehydrate_title(self, value, current_url):
        if not re.search(ur"抽|查", value):
            return None
        else:
            return value


class SczjCrawler(FatherCrawler):
    type = "sczj.inspection"

    item = Field(name="item", path="//ul[@class='f14']/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"四川")
    publisher = Field(name="publisher", value=u"四川省质量技术监督局")

    xpath = {
        "title": "//div[@id='p_dis_wiap']/div[@class='contMain']/h1[@class='f24 red']",
        "content": "//div[@id='cmsArticleContent']",
    }

    export_fields = [pubtime, province, publisher]
    start_page = 0
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 0:
            return "http://www.sczj.gov.cn/mcaf_1/jdjc/"
        return "http://www.sczj.gov.cn/mcaf_1/jdjc/index_%s.html" % str(page)


class SdaicCrawler(FatherCrawler):
    type = "sdaic.inspection"

    item = Field(name="item", path="//div[@class='ty_body']/table[2]/tbody/tr/td/table/tbody/tr/td/table/tbody/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[4]", type=datetime, must=True)
    province = Field(name="province", value=u"山东")
    city = Field(name="city", path="td[3]/text()")
    publisher = Field(name="publisher", value=u"山东省工商行政管理局")

    xpath = {
        "title": "//div[@id='p_dis_wiap']/div[@class='contMain']/h1[@class='f24 red']",
        "content": "//div[@id='cmsArticleContent']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.sdaic.gov.cn/sdgsj/gsgg/spcjjggs/10467-%s.html" % str(page)

    def dehydrate_city(self, value, current_url):
        return value.strip().replace(u"市", "").replace(u"工商局", "")


class SdqtsCrawler(FatherCrawler):
    type = "sdqts.inspection"

    item = Field(name="item", path="//div[@class='second_rightbod_box']/table/tbody/tr[1]/td/table/tbody/tr/td/table/tbody/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"山东")
    publisher = Field(name="publisher", value=u"山东省质量技术监督局")

    xpath = {
        "title": "//table[@class='normal']/tbody/tr[2]/td/h1",
        "content": "//div[@id='Zoom']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 1:
            return "http://www.sdqts.gov.cn/sdzj/%s.html" % (self.key[0:-4] + "index")
        return "http://www.sdqts.gov.cn/sdzj/%s.html" % (self.key + "-" + str(page))


class SgsCrawler(FatherCrawler):
    type = "sgs.inspection"

    item = Field(name="item", path="//div[@class='infoList']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    city = Field(name="city", value=u"上海")
    publisher = Field(name="publisher", value=u"上海市工商行政管理局")

    xpath = {
        "title": "//div[@id='ivs_title']/h1",
        "content": "//div[@id='ivs_content']",
    }

    export_fields = [pubtime, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.sgs.gov.cn/shaic/html/govpub/spzljc_index_addition.html"


class ShzjCrawler(FatherCrawler):
    type = "shzj.inspection"

    item = Field(name="item", path="//record")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    city = Field(name="city", value=u"上海")
    publisher = Field(name="publisher", value=u"上海市质量技术监督局")

    xpath = {
        "title": "//div[@id='ivs_title']",
        "content": "//div[@id='zoom']",
    }

    export_fields = [pubtime, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.shzj.gov.cn/col/col358/index.html"

    def get_tree(self, response):
        return etree.HTML(HTMLParser().unescape(response.text))


class Sjz12365Crawler(FatherCrawler):
    type = "sjz12365.inspection"

    item = Field(name="item", path="//ul[@class='dotlist']/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"河北")
    city = Field(name="city", value=u"石家庄")
    publisher = Field(name="publisher", value=u"石家庄市质量技术监督局")

    xpath = {
        "title": "//h1",
        "content": "//div[@class='TRS_Editor']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 1:
            return "http://www.sjz12365.gov.cn/ZWGK/ZLCC/index.html"
        return "http://www.sjz12365.gov.cn/ZWGK/ZLCC/index_%s.html" % str(page)


class SnqiCrawler(FatherCrawler):
    type = "snqi.inspection"

    item = Field(name="item", path="//div[@class='c1-body']/div[@class='c1-bline']")
    url = Field(name="key", path="div[@class='f-left']/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="div[@class='f-right']", type=datetime, must=True)
    province = Field(name="province", value=u"陕西")
    publisher = Field(name="publisher", value=u"陕西省质量技术监督局")

    xpath = {
        "title": "//div[@class='list pic_news']/div[@class='ctitle ctitle1']",
        "content": "//div[@class='list pic_news']/div[@class='pbox']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.snqi.gov.cn/ccgg/index_%s.htm" % str(page)


class SxzjjCrawler(FatherCrawler):
    type = "sxzjj.inspection"

    item = Field(name="item", path="//div[@id='8944']/div/table/tbody/tr")
    url = Field(name="key", path="td[1]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[2]", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"绍兴")
    publisher = Field(name="publisher", value=u"绍兴市质监局")

    xpath = {
        "title": "//head/title",
        "content": "//div[@id='zoom']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.sxzjj.gov.cn/col/col5894/index.html"


class SyzjCrawler(FatherCrawler):
    type = "syzj.inspection"

    item = Field(name="item", path="//div[@id='_ctl0_newPanel']/table/tr[2]/td/table/tr/td[2]/table/tr/td/table/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]/font", type=datetime, must=True)
    province = Field(name="province", value=u"辽宁")
    city = Field(name="city", value=u"沈阳")
    publisher = Field(name="publisher", value=u"沈阳市质监局")

    xpath = {
        "title": "//div[@id='article']/table/tr[1]/td/b",
        "content": "//div[@id='_ctl0_infocontent']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.syzj.gov.cn/board.aspx?bid=19&p=%s" % str(page)


class SzqtsCrawler(FatherCrawler):
    type = "szqts.inspection"

    item = Field(name="item", path="//ul[@class='list']/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"江苏")
    city = Field(name="city", value=u"苏州")
    publisher = Field(name="publisher", value=u"苏州质量技术监督网")

    xpath = {
        "title": "//h2[@id='content_title']",
        "content": "//div[@id='content_body']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.szqts.gov.cn/zhiliangchoucha!%s.html" % str(page)


class SzscjgCrawler(FatherCrawler):
    type = "szscjg.inspection"

    item = Field(name="item", path="//div[@class='xx_l_r']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"广东")
    city = Field(name="city", value=u"深圳")
    publisher = Field(name="publisher", value=u"深圳市市场监督管理局")

    xpath = {
        "title": "//div[@class='news_cont_c']/h1",
        "content": "//div[@class='TRS_Editor']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler
    start_page = 0

    def get_url(self, key, page):
        if page == 0:
            return "http://www.szscjg.gov.cn/xxgk/qt/tzgg/zljd/index.htm"
        return "http://www.szscjg.gov.cn/xxgk/qt/tzgg/zljd/index_%s.htm" % str(page)


class TjmqaCrawler(FatherCrawler):
    type = "tjmqa.inspection"

    item = Field(name="item", path="//ul[@class='info_list']/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    city = Field(name="city", value=u"天津")
    publisher = Field(name="publisher", value=u"天津市市场和质量监督管理委员会")

    xpath = {
        "title": "//div[@class='news_title']",
        "content": "//div[@class='news_content']",
    }

    export_fields = [pubtime, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.tjmqa.gov.cn/jgdt/zlccbg/index.html"


class TzzjjCrawler(FatherCrawler):
    type = "tzzjj.inspection"

    item = Field(name="item", path="//div[@class='ullist']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    title = Field(name="title", path="a/text()", type=str)
    pubtime = Field(name="pubtime", path=".", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"台州")
    publisher = Field(name="publisher", value=u"台州市质监局")

    xpath = {
        "content": "//div[@class='content textbody']",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.tzzjj.gov.cn/s93p%s.html" % str(page)

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False


class WhbtsCrawler(FatherCrawler):
    type = "whbts.inspection"

    item = Field(name="item", path="//table[@class='neibk']/tr[4]/td/table/tr[1]/td[2]/table/tr[3]/td/table/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    title = Field(name="title", path="td[2]/a/text()", must=True)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"湖北")
    city = Field(name="city", value=u"武汉")
    publisher = Field(name="publisher", value=u"武汉市质量技术监督局")

    xpath = {
        "title": "//td[@class='btbj']/table/tr[2]/td/h3",
        "content": "//td[@class='font14']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 1:
            return "http://www.whbts.gov.cn/news/tzgg2/index.html"
        return "http://www.whbts.gov.cn/news/tzgg2/index_%s.html" % str(page)

    def dehydrate_title(self, value, current_url):
        if not re.search(ur"抽|查", value):
            return None
        else:
            return value


class WzmsaCrawler(FatherCrawler):
    type = "wzmsa.inspection"

    item = Field(name="item", path="//ul[@class='List']/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="a/span", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"温州")
    publisher = Field(name="publisher", value=u"温州市场监管局")

    xpath = {
        "title": "//div[@class='detail_title']",
        "content": "//div[@class='detail_c']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 1:
            return "http://www.wzmsa.gov.cn/jyjcjggs/ltspjygs/index.shtml"
        return "http://www.wzmsa.gov.cn/jyjcjggs/ltspjygs/index_%s.shtml" % str(page)


class WzzjCrawler(FatherCrawler):
    type = "wzzj.inspection"

    item = Field(name="item", path="//div[@class='zwgk_ws_lbym1']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    title = Field(name="title", path="a/@title", type=str)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"温州")
    publisher = Field(name="publisher", value=u"温州市质监局")

    xpath = {
        "content": "//article[@id='div_content']",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.wzzl.gov.cn/list.aspx?kindid=10105&page=%s" % str(page)

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False


class XazjCrawler(FatherCrawler):
    type = "xazj.inspection"

    item = Field(name="item", path="//div[@class='main2']/table/tr/td/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    province = Field(name="province", value=u"陕西")
    city = Field(name="city", value=u"西安")
    publisher = Field(name="publisher", value=u"西安市质量技术监督局")

    xpath = {
        "title": "//div[@class='main']/table/tr[1]/td/h3",
        "pubtime": "//div[@class='main']/table/tr[2]/td",
        "content": "//div[@class='main']/table/tr[4]/td",
    }

    export_fields = [province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.xazj.gov.cn/Front/ZhuanLanXiLie497.html"


class XjzjCrawler(FatherCrawler):
    type = "xjzj.inspection"

    item = Field(name="item", path="//div[@class='lisiBox']/ul[1]/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"新疆维吾尔族自治区")
    publisher = Field(name="publisher", value=u"新疆维吾尔族自治区质量技术监督局")

    xpath = {
        "title": "//div[@class='article-title']/h2",
        "content": "//div[@class='article-box']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.xjzj.gov.cn/info/iList.jsp?cat_id=10084&cur_page=%s" % str(page)


class XmzjjCrawler(FatherCrawler):
    type = "xmzjj.inspection"

    item = Field(name="item", path="//td[@class='border_fwsy_zwxx']/table[2]/tr/td/table/tr")
    url = Field(name="key", path="td[2]/a/@href", type=Url)
    pubtime = Field(name="pubtime", path="td[3]", type=datetime, must=True)
    province = Field(name="province", value=u"福建")
    city = Field(name="city", value=u"厦门")
    publisher = Field(name="publisher", value=u"厦门市质量技术监督局")

    xpath = {
        "title": "//td[@class='zgc_contact_title']",
        "content": "//td[@class='p12']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        if page == 1:
            return "http://www.xmzjj.gov.cn/xxgk/chchgg/"
        return "http://www.xmzjj.gov.cn/xxgk/chchgg/index_%s.htm" % str(page)


class XtzjjCrawler(FatherCrawler):
    type = "xtzjj.inspection"

    item = Field(name="item", path="//div[@id='div_right']/div[2]/table/tr/td//div[@class='div_article']")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="a", type=datetime, must=True)
    province = Field(name="province", value=u"河北")
    city = Field(name="city", value=u"邢台")
    publisher = Field(name="publisher", value=u"邢台市质量技术监督局")

    xpath = {
        "title": "//div[@id='div_Article']/div[@class='div_title']",
        "content": "//div[@id='div_content']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.xtzjj.gov.cn/Contents.aspx?ColumnId=A215fWbAeyc7s"\
               "A1nMCPP6ag_D_D&ParId=AOTDYUQBOh6N30ilVgtkoXg_D_D&Type=An8mH_JhZgC6tgjTGhmjhwkQ_D_D"


class YkzjjCrawler(FatherCrawler):
    type = "ykzjj.inspection"

    item = Field(name="item", path="//div[@class='containerb']/table/tr/td/table/tr")
    url = Field(name="key", path="td[1]/a/@href", type=Url)
    title = Field(name="title", path="td[1]/a", type=str)
    pubtime = Field(name="pubtime", path="td[2]", type=datetime, must=True)
    province = Field(name="province", value=u"辽宁")
    city = Field(name="city", value=u"营口")
    publisher = Field(name="publisher", value=u"营口市质量技术监督局")

    xpath = {
        "content": "//div[@class='containerb']/table/tr/td/table[10]/tr/td/span",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.ykzjj.gov.cn/news.php?sid=84"

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False 


class YnqiCrawler(FatherCrawler):
    type = "ynqi.inspection"

    item = Field(name="item", path="//ul[@class='newsList infoListA']/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"云南")
    publisher = Field(name="publisher", value=u"云南省质量技术监督局")

    xpath = {
        "title": "//h2[@class='title']",
        "content": "//div[@id='fontzoom']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.ynqi.gov.cn/NewsList.aspx?ClassID=C0D65C23-4CDD-4363-A928-259B499F68BA"


class YnqiCrawler(FatherCrawler):
    type = "ynqi.inspection"

    item = Field(name="item", path="//ul[@class='newsList infoListA']/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"云南")
    publisher = Field(name="publisher", value=u"云南省质量技术监督局")

    xpath = {
        "title": "//h2[@class='title']",
        "content": "//div[@id='fontzoom']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.ynqi.gov.cn/NewsList.aspx?ClassID=C0D65C23-4CDD-4363-A928-259B499F68BA"


class ZjbtsCrawler(FatherCrawler):
    type = "zjbts.inspection"

    item = Field(name="item", path="//div[@id='NewsList']/ul/li")
    url = Field(name="key", path="a/@href", type=Url)
    pubtime = Field(name="pubtime", path="span", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    publisher = Field(name="publisher", value=u"浙江省质量技术监督局")

    xpath = {
        "title": "//div[@class='contaner_bt']",
        "content": "//div[@class='contaner_nr']",
    }

    export_fields = [pubtime, province, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.zjbts.gov.cn/cctg/%s.htm" % str(page)

class ZjdyCrawler(FatherCrawler):
    type = "zjdy.inspection"

    item = Field(name="item", path="//div[@class='main_right']/table/tr")
    url = Field(name="key", path="td/a[1]/@href", type=Url)
    title = Field(name="title", path="td/a[1]/@title", type=str)
    pubtime = Field(name="pubtime", path="td/a[2]", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"东阳")
    publisher = Field(name="publisher", value=u"东阳市质监局")

    xpath = {
        "content": "//div[@class='list_content']",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.zjdy.gov.cn/news/Main.asp?page=%s&typeid=85&keywords=" % str(page)

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False 


class ZsscjgCrawler(FatherCrawler):
    type = "zsscjg.inspection"

    item = Field(name="item", path="//ul[@class='ul_content_right']/li")
    url = Field(name="key", path="a/@href", type=Url)
    title = Field(name="title", path="a/@title", type=str)
    pubtime = Field(name="pubtime", path="a/span[2]", type=datetime, must=True)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"舟山")
    publisher = Field(name="publisher", value=u"舟山市场监管局")

    xpath = {
        "content": "//div[@id='div_real_content']",
    }

    export_fields = [pubtime, province, city, title, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.zsscjg.gov.cn/NewsList.aspx?pageIndex=%s&TYPE=SY007" % str(page)

    def filter(self, key, data):
        if re.search(ur"抽|查|检", data["title"]):
            return True
        return False 


class ZzgsCrawler(FatherCrawler):
    type = "zzgs.inspection"

    item = Field(name="item", path=r"urls\[i\]=.*?imgstrs\[i\]=.*?;")
    url = Field(name="key", path=r"urls\[i\]='(.*?)';", type=Url)
    pubtime = Field(name="pubtime", path=r"year\[i\]='(\d{2,4})';.*?month\[i\]='(\d{1,2})';.*?day\[i\]='(\d{1,2})';", type=datetime, must=True)
    province = Field(name="province", value=u"河南")
    city = Field(name="city", value=u"郑州")
    publisher = Field(name="publisher", value=u"郑州市工商行政管理局")

    xpath = {
        "title": "//td[@class='text_biaoti']",
        "content": "//div[@id='zoom']",
    }

    export_fields = [pubtime, province, city, publisher]
    child = ArticleContentCrawler

    def get_url(self, key, page):
        return "http://www.zzgs.gov.cn/col/col6101/index.html"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        url = value.group(1).strip()
        return join_path(current_url, url)

    def dehydrate_pubtime(self, value, current_url):
        pubtime = fmt_time(value.group(1)+" "+value.group(2)+" "+value.group(3))
        return local2utc(pubtime) if pubtime else None


if __name__ == '__main__':
    Handler.handle(YkzjjCrawler.type, data={"last_info": {"pubtime": datetime(2015, 1,1)}}, 
        producer_id=1, category=u'抽检信息',
        application='yqj')