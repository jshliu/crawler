#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

import sys
# root_mod = '/home/xxguo/Project/crawler'
root_mod = '/home/jshliu/Project/ecommerce/common'
sys.path.append(root_mod)
reload(sys)
sys.setdefaultencoding('utf8')

import pymongo
import math
import uuid
import re
from datetime import datetime
from time import sleep
from urllib import quote, unquote
from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce import EcBasicModel,\
    EcDetailModel, EcCommentModel 
from processdata import ProcessData,\
    extract_title, extract_category, extract_text,\
    get_ctime, convert_imgs, get_brand, get_version, get_series,\
    get_address


class FirstCrawler(Crawler):
    type = "ecommerce.jd.firstlvl"

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(FirstCrawler.type, interval=86400)

    def crawl(self):
        start_urls = "http://gw.m.360buy.com/client.action?functionId=catelogy&body="
        sencond_urls = {
            'catelogyId': '0',
            'isDescription': 'true',
            'isIcon': 'true',
            'level': '0'
        }

        url = start_urls + quote(str(sencond_urls))
        try:
            jsons = ProcessData.get_json_data(url)
            lists = jsons['catelogyList']
        except Exception,e:
            self.logger.error(url)
            self.logger.error(e)
            print 'error ',url
            return
        for i in range(len(lists)):

            cid = lists[i]['cid']
            priorcategory = []
            priorcategory.append(extract_title(lists[i]['name']))
            data = {
                'priorcategory':priorcategory,
            }

            Scheduler.schedule(SecondCrawler.type, key=cid, data=data)


class SecondCrawler(Crawler):
    type = "ecommerce.jd.secondlvl"

    def crawl(self):
        fid = self.key
        categorys = self.data['priorcategory']

        start_urls = "http://gw.m.360buy.com/client.action?functionId=catelogy&body="
        sencond_urls = {
            'catelogyId': str(fid),
            'isDescription': 'true',
            'isIcon': 'true',
            'level':'1'
        }
        url = start_urls + quote(str(sencond_urls))
        try:
            jsons = ProcessData.get_json_data(url)
            lists = jsons['catelogyList']
        except:
            print 'error ',url
            return
        if lists == []:
            return {}
        for i in range(len(lists)):
            cid = lists[i]['cid']
            priorcategory = []
            priorcategory.extend(categorys)
            priorcategory.append(extract_title(lists[i]['name']).replace(" ", ""))
            data = {
                'priorcategory':priorcategory,
            }
            
            Scheduler.schedule(ThirdCrawler.type, key=cid, data=data)


class ThirdCrawler(Crawler):
    type = "ecommerce.jd.thirdlvl"

    def crawl(self):
        fid = self.key
        categorys = self.data['priorcategory']

        start_urls = "http://gw.m.360buy.com/client.action?functionId=catelogy&body="
        thrid_urls = {
            'catelogyId':str(fid),
            'isDescription':'false',
            'isIcon':'false',
            'level':'2'
        }
        url = start_urls + quote(str(thrid_urls))

        try:
            jsons = ProcessData.get_json_data(url)
            lists = jsons['catelogyList']
        except Exception,e:
            self.logger.error(url)
            self.logger.error(e)
            print 'error ',url
            return
        if lists == []:
            return {}
        for i in range(len(lists)):
            cid = lists[i]['cid']
            priorcategory = []
            priorcategory.extend(categorys)
            priorcategory.append(extract_title(lists[i]['name']).replace(" ", ""))
            data = {
                'priorcategory':priorcategory,
            }
            # if lists[i]['name'] != u"冰箱" and lists[i]['name'] != u"空调":
            #     continue
            Scheduler.schedule(ListCrawler.type, key=cid, data=data, interval=86400)


class ListCrawler(Crawler):
    type = "ecommerce.jd.goodslist"

    def get_url(self,fid,pages):
        one_urls = "http://gw.m.360buy.com/client.action?functionId=searchCatelogy&body="
        list_urls = {
            'isLoadPromotion': 'true',
            'pagesize': '100',
            'isLoadAverageScore': 'true',
            'sort': '5',
            'page': str(pages),
            'userLocation': '114.40398301322374_30.452138106281158',
            'catelogyId': str(fid),
            'multi_suppliers': 'yes',
            }

        return one_urls + quote(str(list_urls))

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
        fid = self.key

        category_data = extract_category(self)
        count = 3 #页数初始值为3
        pages = 1 #从第一页开始
        while pages <= count:
            url = self.get_url(fid,pages)
            try:
                jsons = ProcessData.get_json_data(url)
                if pages==1 : count = math.ceil(int(jsons['wareCount'])/100)
                lists = jsons['wareInfo']
            except Exception,e:
                self.logger.error(url)
                self.logger.error(e)
                print 'error ',url
                return
            if lists == []:
                return {}
            for i in range(len(lists)):
                wareId = lists[i]['wareId']
                try:
                    f = lambda x: int(x[:-1])/100.00
                    ecsumscores = float(f(lists[i]['good'])) #商品总评分
                except:
                    ecsumscores = 0
                goods_find = self.has_goods(wareId)
                if not goods_find:
                    data = {
                        'priorcategory': self.data['priorcategory'],
                    }
                    Scheduler.schedule(DetailCrawler.type, key=wareId, data=data)
                    continue 

                adword = self.extract_adword(lists[i]['adword'])                  
                crawl_data = {
                    'id': goods_find['uuid'],
                    'source_id': wareId,
                    'source': self.data.get('source'),
                    'title': lists[i]['wname'],
                    'adword': adword,
                    'status': goods_find['status'],
                    'price': float(lists[i]['jdPrice']),
                    'original_price': float(lists[i]['martPrice']),
                    'score': ecsumscores,
                    'brand': goods_find['brand'],
                    'version': goods_find['version'],
                    'series': goods_find['series'],
                    'comment': {
                        'is_Bbc': goods_find['is_Bbc'],
                    }
                }
                crawl_data.update(category_data)
                crawl_data.update(get_ctime())
                model = EcBasicModel(crawl_data)
                export(model)
            pages += 1


# class CommentCrawler(Crawler):
#     type = "ecommerce.jd.goodscomment"

#     def get_url(self,fid,pages):
#         one_urls = "http://gw.m.360buy.com/client.action?functionId=comment&body="
#         comment_urls = {
#             'score':'0',
#             'pagesize':'10',
#             'version':'new',
#             'wareId':str(fid),
#             'page':str(pages)

#         }
#         return one_urls + quote(str(comment_urls))

#     def crawl(self):

#         # wareId = '1229271'
#         # priorcategory = ["家居家装","清洁用品","衣物清洁"]
#         # presentcategory = ['1','2','3']
#         # ecid = '124'
#         wareId = self.key
#         ecid =  self.data['uuid']
#         category_data = extract_category(self)

#         count = 1 #页数初始值为1
#         pages = 1 #从第一页开始
#         while pages <= count:
#             number = 0 #去重
#             url = self.get_url(wareId,pages)
#             try:
#                 jsons = ProcessData.get_json_data(url)
#                 groups = jsons['commentInfoList']
#             except Exception,e:
#                 self.logger.error(e)
#                 print 'error ',url
#                 return

#             if groups == []:
#                 break
#             if pages == 1: count = math.ceil(int(groups[0]['totalCount']))
#             for i in range(len(groups)):

#                 attribute = groups[i]['attribute']
#                 for i in range(len(attribute)):
#                     if attribute[i][0]['k'] == u'心得':
#                         commentContent = attribute[0][0]['v']
#                     elif attribute[i][0]['k'] == u'购买日期':
#                         buyTime = attribute[-1][0]['v']

#                 comment_data={
#                     # 'uuid': uuid.uuid1(),         #primary key
#                     'ecid': ecid,        #commodity table foreign key
#                     'source_id': wareId,
#                     'source': self.data.get('source'),
#                     'comment_id': groups[i]['commentId'],  #review id
#                     'score': groups[i]['score'],         #commodity score
#                     'pubtime': ProcessData.str_datetime(groups[i]['creationTime']),
#                     'buytime': ProcessData.str_datetime(buyTime),
#                     'user_id': groups[i]['userId'],
#                     # 'usernickName': groups[i]['usernickName'],
#                     'useful': int(groups[i]['usefulVoteCount']),
#                     'reply': int(groups[i]['replyCount']),
#                     'content': commentContent

#                 }
#                 comment_data.update(category_data)
#                 model = EcCommentModel(comment_data)
#                 export(model)


class CommentCrawler(Crawler):
    type = "ecommerce.jd.goodscomment"

    xpaths = {
        "item": "//div[@id='comments-list']/div[@class='mc']/div[@class='item']",
        "toofast": "//div[@id='refresh']",
        "address":"div/span/span[@class='u-address']/text()",
        "name":"div[@class='i-item']/@data-nickname",
        "url":"div[@class='user']/div[@class='u-name']/a/@href",
        "score":"div[@class='i-item']/div[@class='o-topic']/span/@class",
        "tags": "div[@class='i-item']/div[@class='comment-content']/dl/dd/span[@class='comm-tags']/span/text()",
        "show_pic": "div[@class='i-item']/div[@class='comment-content']//div[@class='comment-show-pic']"\
            "/table//td/a/img/@src",
        "buytime":"div[@class='i-item']/div[@class='comment-content']/div[@class='dl-extra']/dl[last()]/dd/text()",
        "commenttime":"div[@class='i-item']/div[@class='o-topic']/span[@class='date-comment']/a/text()",
        "comment":"div[@class='i-item']/div[@class='comment-content']/dl/dd/text()",
        "comment1":"div[@class='i-item']/div[@class='comment-content']/dl[2]/dd/text()",
        "title":"div[@class='i-item']/div[@class='comment-content']/dl/dd/span/span/text()",
        "commentid":"div[@class='i-item']/div[@class='o-topic']/span[@class='date-comment']/a/@href",
        "useful":"div[@class='i-item']/div[@class='btns']/div[@class='useful']/a/@title",
        "reply": "div[@class='i-item']/div[@class='btns']/a[@class='btn-reply']/@title",
    }
    
    def get_url(self , fid ,pages):
        url = 'http://club.jd.com/review/%s-3-%s-0.html'%(str(fid),str(pages))
        return url

    def mackining(self, name, datas):
        xpath = self.xpaths[name]
        res = datas.xpath(xpath)
        if res:
            return res[0].strip()
        return ""

    def get_show_pic(self, name, datas):
        xpath = self.xpaths[name]
        res = datas.xpath(xpath)
        for i in res:
            res[res.index(i)] = str(i)
        return res

    def get_tags(self, name, datas):
        xpath = self.xpaths[name]
        res = datas.xpath(xpath)
        for i in res:
            res[res.index(i)] = str(i)
        return res             

    def handle(self,datas):
        address = self.mackining('address',datas)
        name = self.mackining('name',datas)
        url = self.mackining('url',datas)
        score = self.mackining('score',datas)
        tags = self.get_tags('tags', datas)
        SCORES = re.search(u'\s*([0-5])\s*',score)
        score = int(SCORES.group(1)) if SCORES else ''
        show_pic = self.get_show_pic('show_pic', datas)
        title = self.mackining('title',datas)
        if tags:
            comment = self.mackining('comment1', datas)
        else:
            comment = self.mackining('comment',datas)
        commentid = self.mackining('commentid',datas)
        buytime = self.mackining('buytime',datas)
        useful = int(self.mackining('useful',datas))
        reply = int(self.mackining('reply',datas))
        buytime = ProcessData.str_datetime(buytime)
        commenttime = self.mackining('commenttime',datas)
        commenttime = ProcessData.str_datetime(commenttime)

        return {
            'address': address,
            'name': name,
            'tags': tags,
            'url': url,
            'score': score,
            'title': title,
            'comment': comment,
            'commentid': commentid,
            'buytime': buytime,
            'commenttime': commenttime,
            'province': address,
            'city': '',
            'useful': useful,
            'reply': reply,
            'show_pic': show_pic,
            # 'city': city
        }

    def crawl(self):
        wareId = self.key
        ecid =  self.data['uuid']
        category_data = extract_category(self)
        pages = 1
        while True: 
            number = 0    #去重
            url = self.get_url(wareId,pages)
            html_stream = ProcessData.get_web_data(url)
            tree = etree.HTML(html_stream.text)
            dom = tree.xpath(self.xpaths["item"])
            if dom == []:
                toofast = tree.xpath(self.xpaths["toofast"])
                if toofast:
                    sleep(1)
                    continue
                return

            for item in dom:
                datas = self.handle(item)
                comment_data={
                    'eid': ecid,        #commodity table foreign key
                    'source_id': wareId,
                    'source': self.data.get('source'),
                    'comment_id': datas['commentid'],  #review id
                    'score': datas['score'],         #commodity score
                    'pubtime': datas['commenttime'],
                    'buytime': datas['buytime'],
                    'user_id': datas['url'],
                    'user_name': datas['name'],
                    'tags': datas['tags'],
                    # 'usernickName': groups[i]['usernickName'],
                    'useful': datas['useful'],
                    'show_pic': datas['show_pic'],
                    'reply': datas['reply'],
                    'content': datas['comment'],
                    'province': datas['province'],
                    'brand': self.data['brand'],
                    'series': self.data['series'],
                    'version': self.data['version'],
                    'comment': {
                        'is_Bbc': self.data['is_Bbc'],
                    }
                }
                comment_data.update(category_data)
                comment_data.update(get_ctime())
                model = EcCommentModel(comment_data)
                export(model)
            pages += 1


class DetailCrawler(Crawler):
    type = "ecommerce.jd.goodsdetail"

    def get_detail_data(self, wareId):
        url = 'http://item.jd.com/%s.html'%(str(wareId))
        html_stream = ProcessData.get_web_data(url)
        html_stream.encoding = 'gb2312'
        tree = etree.HTML(html_stream.text)   
        return tree 

    def get_desc_data(self, wareId):
        url = 'http://d.3.cn/desc/%s?callback=showdesc'%(str(wareId))
        html_stream = ProcessData.get_web_data(url)
        html_stream.encoding = 'gb2312'
        tree = etree.HTML(html_stream.text)   
        return tree

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

    def parse_is_Bbc(self, tree, xpath):
        jd_sell = tree.xpath(xpath)
        is_Bbc = "N" if jd_sell else "Y" 
        return is_Bbc

    def parse_intro_img(self, tree, xpath):
        intro_img = tree.xpath(xpath)
        return intro_img

    def convert_intro_img(self, imgs):
        imgs_new = []
        for img in imgs:
            img_new = re.search(r"http.*?\.(jpg|png|gif)", img)
            if img_new:
                imgs_new.append(img_new.group(0))
        return imgs_new

    def convert_img(self, imgs):
        imgs_new = []
        for img in imgs:
            img_new = img.replace("/n5/", "/n0/")
            imgs_new.append(img_new)
        return imgs_new

    def parse_status(self, tree, xpath):
        is_remove = tree.xpath(xpath)
        if is_remove:
            return 0
        return 1

    def parse_name(self, tree, xpath):
        name_list = tree.xpath(xpath)
        if name_list:
           return name_list[0].strip()
        return ""

    def get_info(self, wareId):
        tree = self.get_detail_data(wareId)
        xpath = {
            "introduce": "//div[@id='product-detail-1']/div/ul[@class='p-parameter-list']/li//text()",
            "summary": "//table[@class='Ptable']/tr/td/text()",
            "images": "//div[@id='spec-list']/div/ul/li/img/@src",
            "is_Bbc": "//div[@class='seller-infor']/em[@class='u-jd']",
            "intro_img": """//div[@class='\\"formwork_img\\"']//img/@data-lazyload""",
            "status": "//div[@class='m-itemover']",
            "name": "//div[@id='name']/h1/text()",
        }
        introduce = self.parse_intr(tree, xpath["introduce"])
        summary = self.parse_summary(tree, xpath["summary"])
        images = tree.xpath(xpath["images"])
        images = self.convert_img(images)
        is_Bbc = self.parse_is_Bbc(tree, xpath["is_Bbc"])
        status = self.parse_status(tree, xpath["status"])
        name = self.parse_name(tree, xpath["name"])

        desc_tree = self.get_desc_data(wareId)
        intro_img = self.parse_intro_img(desc_tree, xpath["intro_img"])
        intro_img = self.convert_intro_img(intro_img)

        info = {}
        info["introduce"] = introduce
        info["summary"] = summary
        info["images"] = convert_imgs(images)
        info["is_Bbc"] = is_Bbc
        info["intro_img"] = intro_img
        info["status"] = status
        info["name"] = name
        return info

    def crawl(self):
        wareId = self.key
        category_data = extract_category(self)

        info = self.get_info(wareId)
        introduce = info["introduce"]
        summary = info["summary"]
        name = info["name"]
        brand = get_brand(summary, introduce)
        series = get_series(summary, introduce)
        version = get_version(summary, introduce)
        address = get_address(summary, introduce)

        crawl_data = {
            'source': self.data.get('source'),
            'source_id': wareId,
            'summary': summary,
            'introduce': introduce,
            'intro_img': info['intro_img'],
            'address': address,
            'images': info['images'],
            'name': name,
            'status': info['status'],
            'brand': brand,
            'series': series,
            'version': version,
            'comment': {
                "is_Bbc": info['is_Bbc'],
            }
        }
        crawl_data.update(category_data)
        crawl_data.update(get_ctime())
        model = EcDetailModel(crawl_data)
        export(model)

        comment_data = {
            'uuid': model['id'],
            'brand': brand,
            'series': series,
            'version': version,
            'is_Bbc': info['is_Bbc'],
            'status': crawl_data['status'],
            'priorcategory': self.data['priorcategory'],
        }
        Scheduler.schedule(CommentCrawler.type, key=wareId, data=comment_data)


class UserCrawler(Crawler):
    type = "ecommerce.jd.userinfo"

    def cralw(self):
        pass


if __name__ == "__main__":
    # t = uuid.uuid1()
    
    data = {
        'source': 'jd',
        # 'priorcategory' :["家用电器", "大家电", "空调"],
        'priorcategory' :["家用电器", "大家电"],
        }
    ThirdCrawler(key="794", data=data).crawl()
    # ListCrawler(key='870',data=data).crawl()
    # ListCrawler(key='878',data=data).crawl()

    # t = uuid.uuid1()
    data = {
        'source': 'jd',
        'priorcategory' :["家居家装","清洁用品","衣物清洁"],
        'brand': 'a',
        'version': 'b',
        'series': 'c',
        'is_Bbc': 'Y',
        'status:': 1,
        'uuid': uuid.uuid1(),
        }
    # ListCrawler().is_first("11053")
    # CommentCrawler(key='1078040',data=data).crawl()
    # DetailCrawler(key='1366436',data=data).crawl()