#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division
import sys

root_mod = '/home/jshliu/Project/ecommerce/common'
sys.path.append(root_mod)

import pymongo
import math
import uuid
from urllib import quote,unquote
from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce import EcBasicModel,EcDetailModel,EcCommentModel
from processdata import ProcessData,extract_title,extract_category,extract_text,\
    get_ctime, get_brand, get_version, get_series, get_address, for_time, local2utc

class FirstCrawler(Crawler):
    type = "ecommerce.newegg.firstlvl"

    def crawl(self):
        url = 'http://www.ows.newegg.com.cn/category.egg'
        jsons = ProcessData.get_json_data(url)
        for item1 in jsons:
            CatName1 = item1['CatName'].replace(" ", "")
            for item2 in item1['SubCategories']:
                CatName2 = item2['CatName'].replace(" ", "")
                for item3 in item2['SubCategories'] :
                    priorcategory = []
                    priorcategory.extend([CatName1,CatName2,item3['CatName'].replace(" ", "")])
                    self.handle(item3['CatID'],priorcategory)
                          
    def handle(self,CatID,priorcategory):
        data = {
            'priorcategory':priorcategory
        }
        Scheduler.schedule(ListCrawler.type, key=CatID, data=data)


class ListCrawler(Crawler):
    type = "ecommerce.newegg.goodslist"

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

    def get_response(self, CatID, pages):
        url = 'http://www.ows.newegg.com.cn/cat/%s'%(str(CatID))
        list_urls = {
            'page': str(pages),
            'pagesize': 20,
            'sort': 10
            }
        return ProcessData.get_json_data(url, parameter=list_urls)

    def get_page_count(self, data):
        count = int(data["PageInfo"]["TotalCount"])
        page_size = int(data["PageInfo"]["PageSize"])
        if count%page_size == 0:
            return int(count/page_size)
        else:
            return int(count/page_size) + 1
      
    def crawl(self):
        CatID = self.key
        category_data = extract_category(self)
        page = 1
        page_count = 1
        while page<=page_count:
            jsons = self.get_response(CatID,page)
            if page==1: page_count = self.get_page_count(jsons)
            for goods in jsons['ProductListItems']:
                source_id = goods["Code"]
                task_data = self.has_goods(source_id)
                if task_data:   
                    crawl_data = {
                        "id": task_data["uuid"],
                        "title": goods["Title"],
                        "price": goods["Price"]["CurrentPrice"],
                        "source_id": source_id,
                        "source": self.data["source"],
                        "status": task_data["status"],
                        "brand": task_data["brand"],
                        "version": task_data["version"],
                        "series": task_data["series"],
                        "comment": {
                            "is_Bbc": task_data["isBbc"],
                        },
                    }
                    crawl_data.update(category_data)
                    crawl_data.update(get_ctime())
                    model = EcBasicModel(crawl_data)
                    export(model)
                else:
                    detail_data = {
                        "priorcategory": self.data["priorcategory"],
                    }
                    Scheduler.schedule(DetailCrawler.type, key=source_id, data=detail_data)
            page += 1


class DetailCrawler(Crawler):
    type = "ecommerce.newegg.goodsdetail"

    xpath = {
        "name": "//div[@id='productTitle']/h1/text()",
        "images": "//ul[@class='goods_prev_list moveable']/li/a/img/@src2",
        "summary": "//div[@id='tab3']/div/div[@class='pro_table_t1 mb40']/"\
            "table/tr",
        "intro_img": "//div[@class='goods_detail_info']/div[@align='left']"\
            "//div[@class='wm-psDivLargeText']/img/@src",
    }

    def get_url(self, key):
        return "http://www.newegg.cn/Product/%s.htm" % key

    def get_json_url(self, key):
        return "http://www.ows.newegg.com.cn/Products.egg/%s" % key

    def get_response(self, key):
        url = self.get_url(key)
        return ProcessData.get_web_data(url)

    def get_name(self, tree):
        name = tree.xpath(self.xpath["name"])
        if name:
            return name[0].strip()
        return ""

    def get_images(self, tree):
        imgs = tree.xpath(self.xpath["images"])
        for img in imgs:
            imgs[imgs.index(img)] = str(img)
        return imgs

    def get_summary(self, tree):
        tr_list = tree.xpath(self.xpath["summary"])
        summary = {}
        for tr in tr_list:
            if tr.find("td") is None:
                continue
            key = tr.findtext("th")
            if key:
                value = tr.findtext("td")
                summary[key.strip()] = value
        return summary

    def get_intro_img(self, tree):
        imgs = tree.xpath(self.xpath["intro_img"])
        for img in imgs:
            imgs[imgs.index(img)] = str(img)
        return imgs

    def get_is_Bbc(self, data):
        if int(data["VendorInfo"]["VendorSysno"]) == 1:
            return "N"
        return "Y"

    def get_status(self, data):
        if int(data["OnLineQty"]) == 0:
            return 0
        return 1

    def get_info(self, tree):
        name = self.get_name(tree)
        images = self.get_images(tree)
        summary = self.get_summary(tree)
        intro_img = self.get_intro_img(tree)
        info = {
            "name": name,
            "images": images,
            "summary": summary,
            "brand": get_brand(summary, {}),
            "version": get_version(summary, {}),
            "series": get_series(summary, {}),
            "address": get_address(summary, {}),
            "intro_img": intro_img,
        }
        return info

    def crawl(self):
        json_data = ProcessData.get_json_data(self.get_json_url(self.key))
        is_Bbc = self.get_is_Bbc(json_data)
        status = self.get_status(json_data)
        response = self.get_response(self.key)
        tree = etree.HTML(response.text)
        info = self.get_info(tree)
        crawl_data = {
            "source": self.data["source"],
            "source_id": self.key,
            "status": status,
            "comment": {
                "is_Bbc": is_Bbc,
            },
        }
        crawl_data.update(info)
        crawl_data.update(extract_category(self))
        crawl_data.update(get_ctime())
        model = EcDetailModel(crawl_data)
        export(model)

        comment_data = {
            "uuid": model["id"],
            "status": model["status"],
            "version": model["version"],
            "series": model["series"],
            "brand": model["brand"],
            "is_Bbc": model["comment"]["is_Bbc"],
        }
        Scheduler.schedule(CommentCrawler.type, key=self.key, data=comment_data)


class CommentCrawler(Crawler):
    type = "ecommerce.newegg.goodscomment"

    def get_response(self, key, page):
        url = "http://www.ows.newegg.com.cn/GroupReviewV1.egg"
        data = {
            "ScoreType": 0,
            "PageSize": 20,
            "Tag": None,
            "PageNumber": str(page),
            "ProductID": key,
        }
        return ProcessData.get_json_post(url, data=data)

    def get_page_count(self, data):
        return int(data["PageInfo"]["TotalPage"])

    def get_area(self, data):
        area = data["CustomerInfo"]["RegionName"]
        area = area.strip() if area else area
        info = {}
        if area:
            if (area == u"北京") | (area == u"上海") |\
                (area == u"天津") | (area == u"重庆"):
                info["city"] = area
            else:
                info["province"] = area
        return info

    def get_pubtime(self, data):
        return local2utc(for_time(data["InDate"]))

    def get_user_id(self, data):
        return "http://space.newegg.cn/%s/Review.htm" % data["CustomerInfo"]["ID"].strip()

    def get_info(self, data):
        area = self.get_area(data)
        info = {
            "comment_id": data["SysNo"],
            "content": data["Content"],
            "user_name": data["CustomerInfo"]["Name"],
            "user_id": self.get_user_id(data),
            "pubtime": self.get_pubtime(data),
            "score": data["Score"],
            "show_pic": data["Images"],
            "tags": data["Tags"],
            "useful": data["UsefulCount"],
            "reply": data["ReplyCount"],
        }
        info.update(area)
        return info

    def crawl(self):
        category_data = extract_category(self)
        page = 1
        page_count = 1
        while page<=page_count:
            json_data = self.get_response(self.key, page)
            if page==1: page_count = self.get_page_count(json_data)
            for item in json_data["ProductReviewList"]:
                review = item["ReviewDetail"]
                info = self.get_info(review)
                crawl_data = {
                    "eid": self.data["uuid"],
                    "brand": self.data["brand"],
                    "version": self.data["version"],
                    "series": self.data["series"],
                    "source": self.data["source"],
                    "source_id": self.key,
                    "status": self.data["status"],
                    "comment": {
                        "is_Bbc": self.data["is_Bbc"],
                    },
                }
                crawl_data.update(info)
                crawl_data.update(category_data)
                crawl_data.update(get_ctime())
                model = EcCommentModel(crawl_data)
                export(model)
            page += 1

        

if __name__ == "__main__":
    # f = DetailCrawler()
    # f.crawl()
    data = {
        'source': 'newegg',
        "priorcategory" : [  "电视家用电器",  "冰/洗/空",  "空调" ],
        'uuid':uuid.uuid1(),
        'series': 'series',
        'brand': 'brand',
        'version': 'version',
        'status': 1,
        'is_Bbc': 'N', 
    }
    # FirstCrawler(key='2405',data=data).crawl() 
    # ListCrawler(key='966', data=data).crawl()
    # DetailCrawler(key="A51-285-1DH", data=data).crawl()
    CommentCrawler(key="A28-800-6AP-02", data=data).crawl()
