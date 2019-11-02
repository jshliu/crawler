#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    author:jshliu
    time: 2015-8-10
    vision: v.1.0
    rebark: amzazon   爬虫代码编写  
'''
import sys
import requests
import uuid
import socket
import time
import random
import re

root_mod = '/home/jshliu/Project/ecommerce/common'
sys.path.append(root_mod)
from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce import EcBasicModel, EcDetailModel, EcCommentModel
from processdata import extract_title, extract_category, extract_text,get_ctime,\
    convert_price, get_brand, get_version, get_series, get_address, for_time
import pymongo
from datetime import datetime, timedelta
import time
import json

from settings import MONGO_CONN_STR

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

'''
    说明:获取亚马逊一级分类
'''
reload(sys)
# 解决utf-8乱码问题
sys.setdefaultencoding("utf-8")  # @UndefinedVariable

# ''' 
#     系统初始化，获取10个动态代理ip
# '''
# listips = {}
# ipindex = 0
# '''
#     获取网页的流数据，如果出现异常，可以在爬取一次
# '''

COOKIE = ""

class ProcessData():

    @staticmethod
    def str_datetime(str_time):
        str_time = str_time.strip()
        time_format = '%Y-%m-%d %H:%M:%S'
        times = datetime.strptime(str_time, time_format) - timedelta(hours=8)
        return times

    @staticmethod
    def get_web_data(url):
        # 设置浏览器访问
        i_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
                     "Referer": 'http://www.amazon.cn',
                     "Cookie": COOKIE,
        }
        count = 0
        html_stream = {}
        while count < 3:
            try:
                html_stream = requests.get(url, timeout=5, headers=i_headers)
            except requests.exceptions.Timeout:
                time.sleep(random.randint(1,5))
                count += 1 
            except socket.timeout:
                time.sleep(random.randint(1,5))
                count += 1
            except:
                return {}
            else:
                break
        return html_stream

    '''
    动态获取代理ip 
    '''

    def getIP(self, size):
        # ip列表
        ips = {}

        # 爬取的网站
        url = "http://www.kjson.com/proxy/search/1/?sort=down&by=asc&t=highavailable"
        # 获取流
        html_stream = requests.get(url, timeout=5)

#
# 获取html
        html = etree.HTML(html_stream.text)

        content = "//table[@id='proxy_table']/tr"

        iplist = html.xpath(content)

        for ipitem in iplist:

            # 获取端口
            status = ipitem.xpath("td[@class='enport']/text()")

            prot = "0"

            if status != None and status != [] and status[0] == "DCA":
                prot = "80"

                # 值获取http类型
                type = ipitem.xpath("td[3]/text()")
                if type[0] == "HTTP":

                    # if len(ips) < size :

                    # 获取ip
                    ip = ipitem.xpath("td[1]/text()")
                    # print ip[0]+"   "+prot
                    # tmplist={"http":"http://"+ip[0]+":"+prot}
                    tmplist = {"http://" + ip[0] + ":" + prot: "http"}
                    ips.update(tmplist)

        return ips

'''
    获取一级二级三级分类信息,把分类信息存储到mongodb中
'''


class FirstCrawler(Crawler):

    type = "ecommerce.amazon.firstlvl"

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(FirstCrawler.type, interval=86400)
        # 获取10个动态ip
        # global listips
        # listips = ProcessData().getIP(10)

    def crawl(self):

        url = "http://www.amazon.cn/gp/site-directory"
        # 获取该url的流信息
        html_stream = ProcessData.get_web_data(url)
        html_stream.encoding= "utf-8"
        # 获取html 信息
        html = etree.HTML(html_stream.text)

        # 整个一级二级三级分类的xpath
        xpath = "//div[@id='siteDirectory']/div[@class='a-row']/div[@class='a-row a-spacing-small a-spacing-top-medium']"

        dom = html.xpath(xpath)


        # 获取一级分类
        onexpath = "div[@class='a-row a-spacing-extra-large a-spacing-top-small']/span/a"

        # binali
        tmp = "div[@class='a-row a-spacing-none a-spacing-top-mini sd-addPadding']/div[@class='a-column a-span3 sd-colMarginRight']"

        # 获取二级分类
        twoxpath = "div[@class='a-column a-span12 sd-columnSize']/div[@class='a-row a-spacing-small']/span[@class='sd-fontSizeL2 a-text-bold']/a"

        threexpath = "div[@class='a-column a-span12 sd-columnSize']/div[@class='a-row a-spacing-small']/div[@class='a-row']/ul/li/span/span/a"

        # 连接mongodb
        conmn = pymongo.Connection(MONGO_CONN_STR)

        for item in dom:
            # 获取一级分类  a-row a-spacing-extra-large a-spacing-top-small
            oneitem = item.xpath(onexpath)
            oneinfo = ""

            # print oneitem

            for one in oneitem:
                oneinfo += one.text + ";"

            # 获取一级分类
            oneinfo = oneinfo[:-1]

            tmpxpath = item.xpath(tmp)

            for itemtmp in tmpxpath:
                twoitem = itemtmp.xpath(twoxpath)
                i = 0
                for two in twoitem:
                    threeitem = itemtmp.xpath(
                        "div[@class='a-column a-span12 sd-columnSize']/div[@class='a-row a-spacing-small']/div[@class='a-row']")
                    tmpc = threeitem[i].xpath("ul/li/span/span/a")
                    for t in tmpc:   
                        # if t.text != u"空调" and t.text != u"冰箱":
                        #     continue     
                        # 执行列表
                        Scheduler.schedule(ListCrawler.type, key=t.get("href"), data={
                            'priorcategory': [oneinfo, two.text, t.text]}, interval=86400)
                    i += 1


'''
    获取商品列表
'''
class ListCrawler(Crawler):

    type = "ecommerce.amazon.goodslist"

    xpath = {
        "item": "//div[@id='mainResults']/div[@class='fstRowGrid prod celwidget']|"\
            "//div[@id='mainResults']/div[@class='rsltGrid prod celwidget']|//ul[@"\
            "id='s-results-list-atf']/li|//div[@id='btfResults']/ul/li|//div[@id='m"\
            "ainResults']/div[@class='fstRow prod celwidget']|//div[@id='mainResults']"\
            "/div[@class='rslt prod celwidget']",
        "title1": "h3[@class='newaps']/a/span/text()",
        "title2": "div/div[@class='a-row a-spacing-mini']/div[@class='a-row a-spacing-none']/a/h2/text()",
        "url1": "h3[@class='newaps']/a/@href",
        "url2": "div/div[@class='a-row a-spacing-mini']/div[@class='a-row a-spacing-none']/a/@href",
        "original_price1": "ul[@class='rsltGridList grey']/li[@class='newp']/div/a/del[@class='grey']/text()",
        "original_price2": "div/div[@class='a-row a-spacing-mini']/div[@class='a-row a-spacing-none']/span"\
            "[@class='a-size-small a-color-secondary a-text-strike']/text()",
        "price1": "ul[@class='rsltGridList grey']/li[@class='newp']/div/a/span/text()",
        "price2": "div/div[@class='a-row a-spacing-mini']/div[@class='a-row a-spacing-none'][1]/a"\
            "/span[@class='a-size-base a-color-price a-text-bold']/text()",
        "price3": "div/div[@class='a-row a-spacing-mini']/div[@class='a-row a-spacing-none'][1]/a"\
            "/span[@class='a-size-base a-color-price s-price a-text-bold']/text()",
        "price4": "ul[@class='rsltGridList grey']/li[@class='med grey mkp2']/a/span[@class='price bld']/text()",
        "score1": "div/div[@class='a-row a-spacing-none']/span/span/a/i/span[@class='a-icon-alt']/text()",
        "score2": "ul[@class='rsltGridList grey']/li[@class='rvw']/span[@class='rvwCnt']/a/@alt",
        "source_id": "@name|@data-asin",
    }

    def get_url(self, keyid, page):
        start_url = "http://www.amazon.cn"
        match = re.search("page=\d+?", keyid)
        if match:
            end_url = re.sub("page=\d+?", "page=%s" % str(page), keyid)
        else:
            end_url = keyid + "&page=%s" % str(page)
        return start_url+end_url

    def getPageSize(self, tree):
        size = 1
        cont = "//div[@id='pagn']/span[@class='pagnDisabled']/text()"
        sizestr = tree.xpath(cont)
        if sizestr != None and sizestr != []:
            size = int(sizestr[0])
        return size

    def is_first(self, key):
        terms = {
            "type": ListCrawler.type,
            "key": key,
            "lastrun": datetime.min,
        }
        result = Scheduler.find_one(ListCrawler.type,terms)
        return True if result else False

    def is_detail_done(self):
        terms = {
            "type": DetailCrawler.type,
            "$or": [{"status": 1},{"status": 0}],
        }
        result = Scheduler.find_one(DetailCrawler.type, terms)
        return False if result else True

    def has_goods(self, key):
        terms = {
            "type": CommentCrawler.type,
            "key": key,
            "$and":[
                {"data.brand": {"$exists": True}},
            ],
        }
        result = Scheduler.find_one(CommentCrawler.type, terms)
        return result["data"] if result else None

    def get_good_url(self, tree):
        url = tree.xpath(self.xpath["url1"])
        if not url:
            url = tree.xpath(self.xpath["url2"])
        if url:
            return url[0].strip()
        return ""

    def get_title(self, tree):
        title = tree.xpath(self.xpath["title1"])
        if not title:
            title = tree.xpath(self.xpath["title2"])
        if title:
            return title[0].strip()
        return ""

    def get_price(self, tree):
        price = tree.xpath(self.xpath["price1"])
        if not price:
            price = tree.xpath(self.xpath["price2"])
        if not price:
            price = tree.xpath(self.xpath["price3"])
        if not price:
            price = tree.xpath(self.xpath["price4"])
        if price:
            return convert_price(price[0])
        return 0.0

    def get_source_id(self, tree):
        source_id = tree.xpath(self.xpath["source_id"])
        if source_id:
            return source_id[0].strip()
        return ""

    def get_original_price(self, tree):
        price = tree.xpath(self.xpath["original_price1"])
        if not price:
            price = tree.xpath(self.xpath["original_price2"])
        if price:
            return convert_price(price[0])
        return 0.0

    def get_score(self, tree):
        score_list = tree.xpath(self.xpath["score1"])
        if not score_list:
            score_list = tree.xpath(self.xpath["score2"])
        if score_list:
            score_str = score_list[0].strip()
            match = re.search(ur"平均(\d+?\.?\d*).*?星", score_str)
            if match:
                return float(match.group(1))
        return 0.0

    def get_info(self, tree):
        title = self.get_title(tree)
        price = self.get_price(tree)
        original_price = self.get_original_price(tree)
        score = self.get_score(tree)
        source_id = self.get_source_id(tree)
        info = {
            "title": title,
            "price": price,
            "original_price": original_price,
            "score": score,
        }
        return info

    def remove_task(self, key):
        term = {
            "type": ListCrawler.type,
            "key": key,
        }
        Scheduler.remove(term)

    def crawl(self):
        global COOKIE
        keyid = self.key
        category_data = extract_category(self)
        priorcategory = self.data["priorcategory"]
        count = 3
        page = 1  # 从第一页开始
        while page <= count:
            url = self.get_url(keyid, page)
            html_stream = ProcessData.get_web_data(url)
            if COOKIE != html_stream.headers.get("set-cookie", ""):
                COOKIE = html_stream.headers.get("set-cookie", "")
            html = etree.HTML(html_stream.content)
            if page == 1:
                count = self.getPageSize(html)
            items = html.xpath(self.xpath["item"])
            if not len(items):
                if html.xpath("//input[@id='captchacharacters']"):
                    time.sleep(random.randint(1,3))
                    continue
                else:
                    self.remove_task(keyid)
                    
            for item in items:
                source_id = self.get_source_id(item)
                task_data = self.has_goods(source_id)  
                if not task_data:
                    data = {
                        'priorcategory': priorcategory,
                    }
                    Scheduler.schedule(
                        DetailCrawler.type, key=source_id, data=data) 
                else:  
                    info = self.get_info(item)                           
                    crawl_data = {
                        'id': task_data["uuid"],
                        'source_id': source_id,
                        'source': "amazon",
                        'brand': task_data["brand"],
                        'version': task_data["version"],
                        'series': task_data["series"],
                        'status': task_data["status"],
                        "comment": {
                            "is_Bbc": task_data["is_Bbc"],
                        }
                    }
                    crawl_data.update(info)
                    crawl_data.update(category_data)
                    crawl_data.update(get_ctime())
                    model = EcBasicModel(crawl_data)
                    export(model)
            page += 1


'''
    获取具体的商品信息,把信息存储到cassandra中--电脑方面信息,具备产品参数和技术参数
'''

class DetailCrawler(Crawler):
    type = "ecommerce.amazon.goodsdetail"

    xpath = {
        "name": "//span[@id='productTitle']/text()",
        "images": "//div[@id='altImages']/ul/li[@class='a-spacing-small item']//img/@src",
        "summary1": "//div[@id='prodDetails']/div[@class='wrapper CNlocale']/div[@class='"\
            "container']//tbody/tr|//div[@id='prodDetails']/div[@class='wrapper CNlocale'"\
            "]/div[@class='column col2 ']//tbody/tr",
        "summary2": "//div[@id='detail_bullets_id']//div[@class='content']/ul/li",
        "brand": "//a[@id='brand']/text()",
        "is_Bbc": "//span[@id='ddmMerchantMessage']/text()",
    }

    def get_url(self, key):
        return "http://www.amazon.cn/dp/%s/ref=cm_cr_pr_product_top?ie=UTF8" % key

    def get_response(self, key):
        url = self.get_url(key)
        html_stream = ProcessData.get_web_data(url)
        html_stream.encoding = "utf-8"
        return html_stream

    def get_name(self, tree):
        name = tree.xpath(self.xpath["name"])
        if name:
            return name[0].strip()
        return ""

    def convert_img(self, img):
        new_img = re.sub(r"(?<=)\._.*?_(?=\.(jpg|gif|png|jepg))", "", img.strip())
        return new_img

    def get_images(self, tree):
        images = tree.xpath(self.xpath["images"])
        for img in images:
            new_img = self.convert_img(img)
            images[images.index(img)] = new_img
        return images

    def get_summary(self, tree):
        tr_list = tree.xpath(self.xpath["summary1"])
        summary = {}
        for tr in tr_list:
            key = tr.findtext("td[@class='label']")
            if key:
                key = key.strip()
                if key == u"用户评分":
                    value = tr.findtext("td[@class='value']//div[@id='averageCustomerReviewRating']")
                elif key == u"亚马逊热销商品排名":
                    value = tr.find("td[@class='value']").xpath("string(.)")
                    value = re.sub(r"\n| ","", value).replace("(查看销售排行榜)","\n")
                else:
                    value = tr.findtext("td[@class='value']")
                if value:
                    summary[key] = value.strip()
        if not summary:
            li_list = tree.xpath(self.xpath["summary2"])
            for li in li_list:
                key = li.findtext("b")
                if key:
                    key = key.strip().split(":")[0]
                    if key == u"用户评分":
                        value = li.findtext("span[@class='crAvgStars']/span[@class='asinReviewsSummary']"\
                                "/a/span/span")
                    elif key == u"亚马逊热销商品排名":
                        value = li.xpath("string(.)")
                        value = re.sub(r"\n| |\.zg_hrsr.*}", "", value).replace("(查看小家电商品销售排行榜)", "\n").split(":")[1]
                    else:
                        value = li.xpath("text()")
                        if value:
                            value = value[0]
                    if value:
                        summary[key] = value.strip()
        return summary

    def get_brand(self, tree):
        brand = tree.xpath(self.xpath["brand"])
        if brand:
            return brand[0].strip()
        return ""

    def get_is_Bbc(self, tree):
        is_Bbc_list = tree.xpath(self.xpath["is_Bbc"])
        is_Bbc_str = ""
        if is_Bbc_list:
            is_Bbc_str = is_Bbc_list[0].strip()
        if is_Bbc_str == u"由亚马逊直接销售和发货。":
            return "N"
        return "Y"

    def get_info(self, tree):
        name = self.get_name(tree)
        images = self.get_images(tree)
        summary = self.get_summary(tree)
        brand = self.get_brand(tree)
        is_Bbc = self.get_is_Bbc(tree)
        info = {
            "name": name,
            "images": images,
            "summary": summary,
            "brand": brand if brand else get_brand(summary, {}),
            "version": get_version(summary, {}),
            "series": get_series(summary, {}),
            "address": get_address(summary, {}),
            "comment": {
                "is_Bbc": is_Bbc,
            },
        }
        return info

    def crawl(self):
        global COOKIE
        category_data = extract_category(self)
        response = self.get_response(self.key)
        if COOKIE != response.headers.get("set-cookie", ""):
            COOKIE = response.headers.get("set-cookie", "")
        tree = etree.HTML(response.text)
        info = self.get_info(tree)

        crawl_data = {
            'source': "amazon",
            'source_id': self.key,
            'status': 1,
        }

        crawl_data.update(info)
        crawl_data.update(category_data)
        crawl_data.update(get_ctime())
        model = EcDetailModel(crawl_data)
        export(model)
        comment_data = {
            "uuid": model["id"],
            "brand": model["brand"],
            "version": model["version"],
            "series": model["series"],
            "is_Bbc": model["comment"]["is_Bbc"],
            'status': model["status"],
        }
        Scheduler.schedule(CommentCrawler.type, key=self.key, data=comment_data)


'''
    评论信息存储
'''


class CommentCrawler(Crawler):

    type = "ecommerce.amazon.goodscomment"

    xpath = {
        "item": "//div[@id='cm_cr-review_list']/div[@class='a-section review']",
        "count": "//div[@id='cm_cr-product_info']/div/div[1]//span[@class='a-size-medium totalReviewCount']/text()",
        "score": "div[2]/a[@class='a-link-normal']//span[@class='a-icon-alt']/text()",
        "comment_id": "div[2]/a[@class='a-link-normal']/@href",
        "user_name": "div[3]/span[@class='a-size-base a-color-secondary review-byline']/a"\
            "[@class='a-size-base a-link-normal author']/text()",
        "user_id": "div[3]/span[@class='a-size-base a-color-secondary review-byline']/a"\
            "[@class='a-size-base a-link-normal author']/@href",
        "pubtime": "div[3]/span[@class='a-size-base a-color-secondary review-date']/text()",
        "content": "div[@class='a-row review-data']/span[@class='a-size-base review-text']/text()",
        "show_pic": "div[@class='a-section a-spacing-medium a-spacing-top-medium review-image-container']"\
            "/div[@class='review-image-tile-section']/img[@class='review-image-tile']/@src",
        "useful": "div[@class='a-row helpful-votes-count']/span[@class='a-size-small a-color-second"\
            "ary review-votes']/text()",

    }
    def get_url(self, key, page):
        return "http://www.amazon.cn/product-reviews/" + key + "/ref=cm_cr_dp_"\
            "see_all_summary?ie=UTF8&showViewpoints=1&sortBy=recent&pageNumber=" + str(page)

    def get_PageSize(self, tree):
        count_list = tree.xpath(self.xpath["count"])
        if count_list:
            count = int(count_list[0].strip())
            if count % 10 == 0:
                return count/10
            return count/10 + 1
        return 1

    def get_score(self, tree):
        score = tree.xpath(self.xpath["score"])
        if score:
            return float(score[0].strip())
        return 0

    def get_comment_id(self, tree):
        comment_id = tree.xpath(self.xpath["comment_id"])
        if comment_id:
            comment_id = comment_id[0].strip()
            if comment_id.startswith("/"):
                return "http://www.amazon.cn" + comment_id
        return ""

    def get_user_name(self, tree):
        user_name = tree.xpath(self.xpath["user_name"])
        if user_name:
            return user_name[0].strip()
        return ""

    def get_user_id(self, tree):
        user_id = tree.xpath(self.xpath["user_id"])
        if user_id:
            user_id = user_id[0].strip()
            if user_id.startswith("/"):
                return "http://www.amazon.cn" + user_id 
        return ""

    def get_pubtime(self, tree):
        pubtime_list = tree.xpath(self.xpath["pubtime"])
        if pubtime_list:
            pubtime_str = pubtime_list[0].strip()
            return for_time(pubtime_str)
        return None

    def get_content(self, tree):
        content = tree.xpath(self.xpath["content"])
        if content:
            return content[0].strip()
        return ""

    def convert_img(self, img):
        new_img = re.sub(r"(?<=)\._.*?_(?=\.(jpg|gif|png|jepg))", "", img.strip())
        return new_img

    def get_show_pic(self, tree):
        imgs = tree.xpath(self.xpath["show_pic"])
        for img in imgs:
            imgs[imgs.index(img)] = self.convert_img(img)
        return imgs

    def get_useful(self, tree):
        useful_list = tree.xpath(self.xpath["useful"])
        if useful_list:
            useful_str = useful_list[0].strip().replace(" ", "")
            useful = re.search(ur"(?<=人中有)(\d+?)(?=人认为以下评论非常有用)", useful_str)
            if useful:
                if useful.group(1):
                    return 1
        return 0

    def get_reply(self, tree):
        useful_list = tree.xpath(self.xpath["useful"])
        if useful_list:
            useful_str = useful_list[0].strip().replace(" ", "")
            reply = re.search(ur"(?<=)(\d+?)(?=人中有\d+?人认为以下评论非常有用)", useful_str)
            if reply:
                return int(reply.group(1))
        return 0        

    def get_info(self, tree):
        score = self.get_score(tree)
        comment_id = self.get_comment_id(tree)
        user_name = self.get_user_name(tree)
        user_id = self.get_user_id(tree)
        pubtime = self.get_pubtime(tree)
        content = self.get_content(tree)
        show_pic = self.get_show_pic(tree)
        useful = self.get_useful(tree)
        reply = self.get_reply(tree)
        info = {
            "score": score,
            "comment_id": comment_id,
            "user_name": user_name,
            "user_id": user_id,
            "pubtime": pubtime,
            "content": content,
            "show_pic": show_pic,
            "useful": useful,
            "reply": reply, 
        }
        return info

    def crawl(self):
        global COOKIE
        category_data = extract_category(self)
        page = 1  # 从第一页开始
        pageSize = 5
        while page <= pageSize:
            newurl = self.get_url(self.key, page)
            html_stream = ProcessData.get_web_data(newurl)
            if COOKIE != html_stream.headers.get("set-cookie", ""):
                COOKIE = html_stream.headers.get("set-cookie", "")
            html = etree.HTML(html_stream.content)
            if page == 1:
                pageSize = self.get_PageSize(html)
            items = html.xpath(self.xpath["item"])
            for item in items:
                info = self.get_info(item)
                crawl_data = {
                    "eid": self.data["uuid"],
                    "brand": self.data["brand"],
                    "version": self.data["version"],
                    "series": self.data["series"],
                    "source": self.data["source"],
                    "status": self.data["status"],
                    "source_id": self.key,
                    "comment": {
                        "is_Bbc": self.data["is_Bbc"],
                    }
                }
                crawl_data.update(info)
                crawl_data.update(category_data)
                crawl_data.update(get_ctime())

                model = EcCommentModel(crawl_data)
                export(model)
            page += 1


''' 
 获取商品url列表的页数
'''





if __name__ == "__main__":
    # FirstCrawler.init()
    FirstCrawler().crawl()
    # key = "/b/ref=sd_allcat_applia_l3_b81948071/480-3044690-7789729?ie=UTF8&node=81948071"
    key = "/b/ref=sd_allcat_applia_l3_b2121145051/480-3044690-7789729?ie=UTF8&node=2121145051"
    data =  { "priorcategory" : [  "家用电器",  "大家电 ",  "空调" ],
              # "priorcategory" : [  "家用电器",  "大家电 ",  "冰箱" ],
              "uuid": uuid.uuid1(),
              "brand": "a",
              "version": "b",
              "series": "c",
              "source": "amazon",
              "is_Bbc": "N", 
    }
    # ListCrawler(key=key, data=data).crawl()
    # DetailCrawler(key="B00EIA6QGA", data=data).crawl()
    # CommentCrawler(key="B00EIA6QGA", data=data).crawl()

