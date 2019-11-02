# -*- coding: utf-8 -*-
import sys
# root_mod = '/home/liyang/Documents/shendu-ecommerce-crawler'
# root_mod = '/home/xxguo/Project/crawler'
root_mod = '/home/jshliu/Project/ecommerce/common'
sys.path.append(root_mod)
reload(sys)
sys.setdefaultencoding('utf8')

import requests
import json
import pymongo
from urllib import quote,unquote
from datetime import datetime
#import lxml.html.soupparser as soupparser
from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce import EcBasicModel,\
    EcDetailModel, EcCommentModel 
from processdata import ProcessData,\
    extract_title, extract_category, extract_text,\
    check_encoding,get_ctime,get_version,get_brand,get_series
import re
import uuid


def parse_html(html_data,xpath):
    return etree.HTML(html_data).xpath(xpath)


class FirstCrawler(Crawler):
    type = "ecommerce.gome.firstlvl"
    
    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(FirstCrawler.type, interval=86400)

    def crawl(self):
        url = "http://mobile.gome.com.cn/mobile/product/allCategorys.jsp"
        jsons = ProcessData.get_json_data(url)
        if jsons == {}:
            return {} 
        category1 = jsons['firstLevelCategories']
        for first_item in category1:
            name1 = first_item['goodsTypeName']   #1 lev name
            try :
                category2 = first_item['goodsTypeList']
            except:
                pass
            for second_item in category2:
                name2 = second_item['goodsTypeName']
                try :
                    category3 = second_item['goodsTypeList']
                except:
                    pass
                for third_item in category3:
                    try: 
                        third_id = third_item['goodsTypeId']
                        name3 = third_item['goodsTypeLongName']
                    except:
                        pass
                    priorcategory = []
                    priorcategory.append(name1)
                    priorcategory.append(name2)
                    priorcategory.append(name3)
                    data = {
                        'priorcategory': priorcategory
                        }
                    # if name3 != u"冰箱" and name3 != u"空调":
                    #     continue
                    Scheduler.schedule(ListCrawler.type, key=third_id, data=data, interval=86400)


class ListCrawler(Crawler):
    type = "ecommerce.gome.goodslist"   
    def get_url(self,catId,currentPage):
        front = "http://mobile.gome.com.cn/mobile/product/search/keywordsSearch.jsp?body="
        body = {
            "pageSize":10,
            "searchType":"0",
            "sortBy":"7",
            "regionID":"11010200"}
        body['catId'] = catId
        body['currentPage'] = currentPage
        url = front + quote(str(body).replace("\'","\""))
        return url

    def get_page(self,catId):
        json =ProcessData.get_json_data(self.get_url(catId,1))
        try:
            totalpage = json['totalPage']
        except Exception,e:
            self.logger.error(e)
            print "totalPage fail!"
            return 0
        return totalpage

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

    def extract_adword(self, adword):
        adword = adword.strip()
        if not adword:
            return ""
        regex_str = "<\D*?.*?>|<\D.*?/>|&nbsp;"
        adword = re.sub(regex_str, "", adword)
        return adword

    def crawl(self):
        catId = str(self.key) 

        category_data = extract_category(self)
        totalpage = self.get_page(catId)
        if totalpage == 0:
            return {}
        for i in range(1,totalpage+1):
            url = self.get_url(catId,i)
            jsons = ProcessData.get_json_data(url)
            try:
                goodsList = jsons['goodsList']
            except Exception,e:
                self.logger.error(url)
                self.logger.error(e)
                print "get goodsList fail"

            for j in range(len(goodsList)):
                goods = goodsList[j]
                goodsNo = goods['goodsNo']
                goodsName = goods['goodsName']
                skuID = goods['skuID']

                goods_find = self.has_goods(goodsNo)
                if not goods_find:
                    data = {
                        'priorcategory': self.data['priorcategory'],
                        'skuID': skuID,
                    }
                    Scheduler.schedule(DetailCrawler.type, key=goodsNo, data=data)
                    continue   
                adword = self.extract_adword(goods['ad'])       
                crawl_data = {
                    'id': goods_find['uuid'],
                    'source_id': goodsNo,
                    'source': self.data.get('source'),
                    'title': goods['goodsName'],
                    'adword': adword,
                    'status': goods_find['status'],
                    'price': float(goods['lowestSalePrice']),
                    'brand': goods_find['brand'],
                    'version': goods_find['version'],
                    'series': goods_find['series'],
                    'comment': {
                        'is_Bbc': goods_find['isBbc'],
                        'skuId': goods_find['skuID'],
                    },
                }
                crawl_data.update(category_data)
                crawl_data.update(get_ctime())
                model = EcBasicModel(crawl_data)
                export(model)


class CommentCrawler(Crawler):
    type = "ecommerce.gome.goodscomment"

    def get_url(self,goodsNo,currentPage):
        front = "http://mobile.gome.com.cn/mobile/product/goodsAppraise.jsp?body="
        body = {
            "appraiseType":"0",
            "pageSize":"10",
            }
        body["goodsNo"] = goodsNo
        body["currentPage"] = currentPage
        url = front + quote(str(body).replace("\'","\""))
        return url 

    def get_page(self,goodsNo):
        json = ProcessData.get_json_data(self.get_url(goodsNo,1))
        try:
            totalpage = int(json['totalPage'])
        except Exception,e:
            self.logger.error(e)
            print "totalPage fail!"
        return totalpage

    def crawl(self):
        ecid =  self.data['uuid']
        goodsNo = str(self.key)
        category_data = extract_category(self)
        totalpage = int(self.get_page(goodsNo))    
        if totalpage == 0:
            return
        for i in range(totalpage+1):
            url = self.get_url(goodsNo,i)
            json = ProcessData.get_json_data(url)
            appraise = json['appraiseArray']

            for item in appraise:
                commentid = item['id']
                summary = item['summary']
                score = item['appraiseGrade']
                userorderid = item['appraiseName']
                commenttime = ProcessData.str_datetime(item['appraiseTime'])
                comment_data={
                    'eid': ecid,        #commodity table foreign key
                    'source_id': goodsNo,
                    'source': self.data.get('source'),
                    'comment_id': item['id'],  #review id
                    'score': item['appraiseGrade'],         #commodity score
                    'pubtime': ProcessData.str_datetime(item['appraiseTime']),
                    'user_name': item['appraiseName'],
                    'content': item['summary'],
                    'brand': self.data['brand'],
                    'version': self.data['version'],
                    'series': self.data['series'],
                    'comment': {
                        'is_Bbc': self.data['is_Bbc'],
                        'skuID': self.data['skuID'],
                    }
                }
                comment_data.update(category_data)
                comment_data.update(get_ctime())
                model = EcCommentModel(comment_data)
                export(model)


class DetailCrawler(Crawler):
    type = "ecommerce.gome.goodsdetail"
    def get_basic_url(self,goodsNo):
        front = "http://mobile.gome.com.cn/mobile/product/productShow.jsp?body="
        body = {"skuID":"1119570510"}
        body['goodsNo'] = goodsNo
        url = front + quote(str(body).replace("\'","\""))
        return url 

    def get_price_url(self, number,goodsNo, skuID):
        url = "http://g.gome.com.cn/ec/homeus/browse/store.jsp?callback="\
            "jQuery171024960047309286892_1435734826629&goodsNo=%s&sid=%s"\
            "&pid=%s" % (number, goodsNo, skuID)
        return url

    def get_detail_url(self,goodsNo):
        # url = "http://m.gome.com.cn/product_des-%s-.html?from=cat10000" %(goodsNo)
        url = "http://item.gome.com.cn/%s.html" %(goodsNo)
        return url 
        

    def parse_intr(self, tree, xpath):
        dom = tree.xpath(xpath)
        introduce = {}
        temporary = ''
        for item in dom:
            item = item.strip()
            if item == '':
                continue
            elif item.find('：') >0:
                item = item.split('：',1)
                if item[1] == '':
                    temporary = extract_title(item[0])
                else:
                    introduce[extract_title(item[0])] = extract_text(item[1])
            else:
                if temporary != '':
                    introduce[temporary] = extract_text(item)
                    temporary = ''
                else:
                    continue

        if introduce != '':
            return introduce
        else:
            return ''

    def parse_summary(self, tree, xpath):
        dom = tree.xpath(xpath)
        specifications = {}
        temporary = ''
        i = 0
        for item in dom:
            item = item.strip()
            if item == '':
                continue
            if i%2 ==0:
                specifications[item] = ''
                temporary = extract_title(item)
            else:
                specifications[temporary] = extract_text(item)
            i += 1
        return specifications

    def parse_number(self, tree, xpath):
        number_str = tree.xpath(xpath)[0].strip()
        number = ""
        try:
            number = number_str.split("：")[1]
        except:
            number = number_str.split(":")[1]

        return number

    def crawl(self):
        skulist = []
        goodsNo = str(self.key)
        category_data = extract_category(self)
        url = self.get_detail_url(goodsNo)
        html = ProcessData.get_web_data(url)
        tree = etree.HTML(html.text)
        xpath = {
            "introduce": "//div[@class='guigecanshu']/text()",
            "summary": "//ul[@id='prd_data']/li[2]/ul/li/span/text()",
            # "number": "//span[@class='fr ccc']/text()"
        }

        summary = self.parse_summary(tree, xpath["summary"])
        introduce = self.parse_intr(tree, xpath["introduce"])  
        # number =  self.parse_number(tree, xpath["number"])

        version = get_version(summary, introduce)
        series = get_series(summary, introduce)
        brand = get_brand(summary, introduce)

        json = ProcessData.get_json_data(self.get_basic_url(goodsNo))
        isBbc_str = json["isBbc"]
        isBbc = "Y" if isBbc_str == "Y" or isBbc_str == "y" else "N"
        status_str = json["onSale"]
        status =0 if status_str == "N" or status_str == "n" else 1

        skulist = json['skuList']
        for sku in skulist:
            ecname = sku['skuName']
            ecimglist = sku['skuSourceImgUrl']

        detail_data = {
            'source': self.data.get('source'),
            'source_id': goodsNo,
            'summary': summary,
            'introduce': introduce,
            'name': ecname,
            'images': ecimglist,
            'status': status,
            'brand': brand,
            'version': version,
            'series': series,
            'comment': {
                'is_Bbc': isBbc,
                'skuID': self.data['skuID'],
            },
        }
        detail_data.update(category_data)
        detail_data.update(get_ctime())
        model = EcDetailModel(detail_data)
        export(model)
        comment_data = {
            'uuid': model["id"],
            'brand': brand,
            'version': version,
            'series': series,
            'is_Bbc': isBbc,
            'status': status,
            'priorcategory': self.data['priorcategory'],
            'skuID': self.data['skuID'],
        }
        Scheduler.schedule(CommentCrawler.type, key=goodsNo, data=comment_data)




if __name__ == "__main__1":
    test = GOMEHandler()
    test = FirstCategory()
    #test.wareComment()
    #test.wareInformation()

if __name__ == "__main__":
    pass
    data = {
        'source': 'gome',
        "priorcategory" : ["冰箱 洗衣机 空调","空调/商用","家用空调"],
        'brand': "A",
        'version': "B",
        'series': "C",
        'is_Bbc': "Y", 
        "skuID": "1118730042",
        "uuid": uuid.uuid1(),
    }
    # data = {'source':'gome'}
    FirstCrawler(data={'source':'gome'}).crawl()
    # DetailCrawler(key='9133210303',data = data).crawl()
    # CommentCrawler(key='9133023740',data = data).crawl()
    # ListCrawler(key='cat10000062',data = data).crawl()

