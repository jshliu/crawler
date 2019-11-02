# -*- coding: utf-8 -*-
import re

from context.context import Context

join_path = Context().get("pathutil.join_path")
Field = Context().get("Field") 
Url = Context().get("Url") 
ArticleContentCrawler = Context().get("ArticleContentCrawler")
FatherCrawler = Context().get("FatherCrawler")
is_url = Context().get("htmlutil.is_url")


class AqsiqCrawler(FatherCrawler):
    type = "aqsiq.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r".*", type=Url)
    province = Field(name="province", value=u"全国")
    publisher = Field(name="publisher", value=u"国家质量监督检验检疫总局")

    xpath = {
        'title': "//tr/td[@align='center']/h1",
        'pubtime': "//tr/td[@align='center']/h1/../../following-sibling::tr[1]/td/text()",
        'content': "//div[@class='TRS_Editor']",
    }
    child = ArticleContentCrawler
    export_fields = [province, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(AqsiqCrawler.type, data={"source": "aqsiq"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.aqsiq.gov.cn/"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        value = value.group(0)
        if is_url(value):
            return join_path(current_url, value)
        else:
            return None


class BjtsbCrawler(FatherCrawler):
    type = "bjtsb.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=ur"^(http).+(infoview).+\d{3,8}$", type=Url)
    city = Field(name="city", value=u"北京")
    publisher = Field(name="publisher", value=u"北京质监局")

    xpath = {
        'title': "//div[@class='article-title']/text()",
        'pubtime': "//tr/td[@class='grey-bg']/text()",
        'content': "//div[@id='zoom']"
    }
    child = ArticleContentCrawler
    export_fields = [city, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(BjtsbCrawler.type, data={"source": "bjtsb"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.bjtsb.gov.cn/"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class CqnCrawler(FatherCrawler):
    type = "cqn.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r"^(http|https).+(news)\/(zjpd|xfpd|zhuanti|zgzlb).+\d\.(htm|html|net)$", type=Url)
    province = Field(name="province", value=u"全国")
    publisher = Field(name="publisher", value=u"中国质量新闻网")

    xpath = {
        'title': "//div[@class='Index_ShowDetail_Title']/h1/text()",
        'pubtime': "//div[@class='Index_ShowDetail_Time']//text()",
        'content': "//div[@class='Index_ShowDetail_Content']",
    }
    child = ArticleContentCrawler
    export_fields = [province, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(CqnCrawler.type, key="http://www.cqn.com.cn/news/zjpd/zljd/Index.html",
        #     data={"source": "cqn"}, interval=10800, reset=True)
        # Scheduler.schedule(CqnCrawler.type, key="http://www.cqn.com.cn/news/xfpd/ccgg/Index.html",
        #     data={"source": "cqn"}, interval=10800, reset=True)
        # Scheduler.schedule(CqnCrawler.type, key="http://www.cqn.com.cn/news/zjpd/zjdt/Index.html",
        #     data={"source": "cqn"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return key

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class FjqiCrawler(FatherCrawler):
    type = "fjqi.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r".*", type=Url)
    province = Field(name="province", value=u"福建")
    publisher = Field(name="publisher", value=u"福建质监局")

    xpath = {
        'title': "//div[@class='xl_content']/h1/text()",
        'pubtime': "//div[@class='xl_content']/div[@class='time']/text()",
        'content': "//div[@id='doc_content']",
    }
    child = ArticleContentCrawler
    export_fields = [province, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(FjqiCrawler.type, data={"source": "fjqi"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.fjqi.gov.cn/"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class FsjsjdCrawler(FatherCrawler):
    type = "fsjsjd.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r".*", type=Url)
    province = Field(name="province", value=u"广东")
    city = Field(name="city", value=u"佛山")
    publisher = Field(name="publisher", value=u"广东佛山质监局")

    xpath = {
        'title': "//div[@id='right-title_d']//text()",
        'pubtime': "//div[@class='article']/p[@class='info']/span/text()",
        'content': "//div[@class='right-text_d']",
    }
    child = ArticleContentCrawler
    export_fields = [province, city, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(FsjsjdCrawler.type, data={"source": "fsjsjd"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.fsjsjd.gov.cn/"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class GdqtsCrawler(FatherCrawler):
    type = "gdqts.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r".*", type=Url)
    province = Field(name="province", value=u"广东")
    publisher = Field(name="publisher", value=u"广东质监局")

    xpath = {
        'title': "//div[@id='cTitle']/text()",
        'pubtime': "//tr/td[@align='center']/text()",
        'content': "//div[@class='Custom_UnionStyle']",
    }
    child = ArticleContentCrawler
    export_fields = [province, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(GdqtsCrawler.type, data={"source": "gdqts"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.gdqts.gov.cn/"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class GzqCrawler(FatherCrawler):
    type = "gzq.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r"^(http|https).+(public).+.+\d$", type=Url)
    province = Field(name="province", value=u"广东")
    city = Field(name="city", value=u"广州")
    publisher = Field(name="publisher", value=u"广东广州质监局")

    xpath = {
        'title': "//tr/td[@class='content-title']/div/text()",
        'pubtime': "//tr/td[@class='bottom-line-gray']/text()",
        'content': "//div[@id='new_content_txt']",
    }
    child = ArticleContentCrawler
    export_fields = [province, city, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(GzqCrawler.type, data={"source": "gzq"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.gzq.gov.cn/public/message_list.jsp?catid=825|836"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class HbzljdCrawler(FatherCrawler):
    type = "hbzljd.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r".*", type=Url)
    province = Field(name="province", value=u"湖北")
    publisher = Field(name="publisher", value=u"湖北质监局")

    xpath = {
        'title': "//div[@class='article']/h2/text()|//h3/text()",
        'pubtime': "//div[@class='article']/p[@class='info']/span/text()",
        'content': "//div[@class='files']",
    }
    child = ArticleContentCrawler
    export_fields = [province, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(HbzljdCrawler.type, data={"source": "hbzljd"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.hbzljd.gov.cn/"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class HzqtsCrawler(FatherCrawler):
    type = "hzqts.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r"^(http|https).+(zwpd|qypd|smpd).+[^(Index)]\.(htm|html|net)$", type=Url)
    province = Field(name="province", value=u"浙江")
    city = Field(name="city", value=u"杭州")
    publisher = Field(name="publisher", value=u"浙江杭州质监局")

    xpath = {
        'title': "//tr/td[@class='dhz']/span/text()",
        'pubtime': "//td/table/tbody/tr/td[@align='center']/span/text()",
    }
    child = ArticleContentCrawler
    export_fields = [province, city, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(HzqtsCrawler.type, data={"source": "hzqts"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.hzqts.gov.cn/zwpd/index.htm"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class JiangxizjCrawler(FatherCrawler):
    type = "jiangxizj.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r"^(http|https).+(news).+\.(htm|html|net)$", type=Url)
    province = Field(name="province", value=u"江西")
    publisher = Field(name="publisher", value=u"江西质监局")

    xpath = {
        'title': "//ul/li[@class='show_title']/text()",
        'pubtime': "//ul/li[@class='show_date']/text()",
        'content': "//li[@class='show_con']",
    }
    child = ArticleContentCrawler
    export_fields = [province, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(JiangxizjCrawler.type, data={"source": "jiangxizj"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.jxzj.gov.cn/jxzj/index.html"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class SdqtsCrawler(FatherCrawler):
    type = "sdqts.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r"^(http|https).+(sdzj).+\/(\d){2,8}.+\.(htm|html|net)$", type=Url)
    province = Field(name="province", value=u"山东")
    publisher = Field(name="publisher", value=u"山东质监局")

    xpath = {
        'title': "//tr/td/p[@class='sub_title']/preceding-sibling::h1/text()",
        'pubtime': "//table[@class='normal']/tbody/tr[3]/td/text()",
        'content': "//div[@id='Zoom']",
    }
    child = ArticleContentCrawler
    export_fields = [province, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(SdqtsCrawler.type, data={"source": "sdqts"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.sdqts.gov.cn/"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class ZhqcCrawler(FatherCrawler):
    type = "zhqc.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r"^(http|https).+(newsid).+\d$", type=Url)
    province = Field(name="province", value=u"山东")
    city = Field(name="city", value=u"珠海")
    publisher = Field(name="publisher", value=u"广东珠海质监局")

    xpath = {
        'title': "//tr/td[@class='info10']/text()",
        'pubtime': "//tr/td[@align='center']/font/text()",
    }
    child = ArticleContentCrawler
    export_fields = [province, city, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(ZhqcCrawler.type, data={"source": "zhqc"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.zhqc.gov.cn/"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


class ZjbtsCrawler(FatherCrawler):
    type = "zjbts.news"

    item = Field(name="item", path=r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')")
    url = Field(name="key", path=r"^(http|https).+(HTML).+[^(Index)]\.(htm|html|net)$", type=Url)
    province = Field(name="province", value=u"浙江")
    publisher = Field(name="publisher", value=u"浙江质监局")

    xpath = {
        'title': "//div[@class='contaner']/div[@class='contaner_bt']/text()",
        'pubtime': "//div[@class='contaner']/div[@class='contaner_ly']/text()",
        'content': "//div[@class='contaner_nr']",
    }
    child = ArticleContentCrawler
    export_fields = [province, publisher]

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(ZjbtsCrawler.type, data={"source": "zjbts"}, interval=10800, reset=True)

    def get_url(self, key, page):
        return "http://www.zjbts.gov.cn/"

    def get_tree(self, response):
        return response.text

    def dehydrate_key(self, value, current_url):
        if value:
            return value.group(0)
        else:
            return None


if __name__ == '__main__':
    ZjbtsCrawler(data={"source": "zjbts"}).crawl()
