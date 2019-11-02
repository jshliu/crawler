#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
# root_mod = '/home/xxguo/Project/crawler'
root_mod = '/home/jshliu/Project/ecommerce/common'
sys.path.append(root_mod)
import uuid
import re
from lxml import etree
from scheduler.crawler import Crawler, export, Scheduler
from models.ecommerce import EcBasicModel,\
    EcDetailModel, EcCommentModel 
from processdata import ProcessData,\
    extract_title, extract_category, extract_text,\
    get_ctime, get_brand, get_version, get_series,for_time

class FirstCrawler(Crawler):
    type = "ecommerce.yhd.firstlvl"

    @staticmethod
    def init(conf=None):
        pass
        # Scheduler.schedule(FirstCrawler.type, interval=86400)

    def crawl(self):
        url = "http://interface.m.yhd.com/ \
               mcategory/servlet/CentralMobileFacadeJsonServlet/ \
               getNavCategoryWithKeywordByRootCategoryId? \
               rootCategoryId=0&categoryNavId=0&provinceId=1"
        try:
            jsons = ProcessData.get_json_data(url.replace(' ',''))
            data = jsons['data']
        except Exception,e:
            self.logger.error(url)
            self.logger.error(e)            
            print 'error ',url
        for item in data:
            categoryName1 = item['categoryName']
            for child in item['childCategoryVOList']:
                if not child.has_key('boundCategoryId'):continue
                priorcategory = []
                categoryName2 = child['categoryName']
                priorcategory.extend([categoryName1,categoryName2])
                self.handle(child['id'],priorcategory)

    def handle(self,id,priorcategory):
        data = {
            'priorcategory':priorcategory
        }

        Scheduler.schedule(ThirdCrawler.type, key=id, data=data)
       

class ThirdCrawler(Crawler):
    type = "ecommerce.yhd.thirdlvl"

    def crawl(self):
        cid = str(self.key)
        categorys = self.data['priorcategory']
        url = "http://interface.m.yhd.com/\
               mcategory/servlet/CentralMobileFacadeJsonServlet/\
               getNavCategoryWithKeywordByRootCategoryId?rootCategoryId=\
               %s&categoryNavId=0&provinceId=1" %(cid)
        try:
            jsons = ProcessData.get_json_data(url.replace(' ',''))
            data = jsons['data']
        except Exception,e:
            self.logger.error(url)
            self.logger.error(e)
            print 'error ',url
        for item in data:
            priorcategory = []
            priorcategory.extend(categorys)
            priorcategory.append(item['categoryName'])            
            if item.has_key('boundCategoryId'):
                keys = item['boundCategoryId']
            else:
                continue
            data = {
                'priorcategory':priorcategory,
            }  
            # if priorcategory[2] != u"冰箱" and priorcategory[2] != u"空调":
            #     continue 
            Scheduler.schedule(ListCrawler.type, key=keys, data=data, interval=86400)


class ListCrawler(Crawler):
    type = "ecommerce.yhd.goodslist"

    def search_list_xpath(self,xpath):
        data = {
            'list': "//div[@class='mod_search_pro']",
            'page_count' : "//input[@id='pageCountPage']/@value",
            'title': "div[@class='itemBox']/p[@class='proName clearfix']/a[1]/text()",
            'adword': "div[@class='itemBox']/p[@class='proName clearfix']/a[2]/text()",
            'price': "div[@class='itemBox']/p[@class='proPrice']/em/text()",
            'source_id': "div[@class='itemBox']/p[@class='proPrice']/em/@productid",
        }
        return data.get(xpath,'""')

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
            "$and":[
                {"data.source_id": key},
                {"data.brand": {"$exists": True}},
            ],
        }
        result = Scheduler.find_one(CommentCrawler.type, terms)
        return result["data"] if result else None

    def mackining(self,name):
        data = ''
        for item in name:
            data += item.strip()
        return data

    def get_url(self, key, pages, more):
        url = "http://list.yhd.com/searchPage/c%s-0-0/"\
                "b/a-s1-v4-p%s-price-d0-f0-m1-rt0-pid-mid0-k/"\
                "?isGetMoreProducts=%s&isLargeImg=0&fashionCateType=1"
        return url % (key, str(pages), str(more))

    def parse_data(self, item):
        crawl_data = {}
        craw = [
            'title','adword',
            'price','original_price',
        ]
        for value in craw: 
            crawl_data[value] = self.mackining(item.xpath(self.search_list_xpath(value)))
        crawl_data['price'] = float(crawl_data['price'])  
        crawl_data['adword'] = self.extract_adword(crawl_data['adword'])
        return crawl_data

    def get_init_list(self, key, page):
        url = self.get_url(key, page, 0)
        json_data = ProcessData.get_json_data(url)
        tree = etree.HTML(json_data['value'])
        dom = tree.xpath(self.search_list_xpath('list'))
        return dom

    def get_more_list(self, key, page):
        url = self.get_url(key, page, 1)
        json_data = ProcessData.get_json_data(url)
        tree = etree.HTML(json_data['value'])
        dom = tree.xpath(self.search_list_xpath('list'))
        return dom

    def get_crawl_data(self, item, **args):
        crawl_data = self.parse_data(item)
        task_data = args['task_data']
        crawl_data['id'] = task_data['uuid']
        crawl_data['status'] = task_data['status']
        crawl_data['brand'] = task_data['brand']
        crawl_data['series'] = task_data['series']
        crawl_data['version'] = task_data['version']
        crawl_data['comment'] = {
            'is_Bbc': task_data['is_Bbc'],
        }
        crawl_data['source_id'] = args['source_id']
        crawl_data.update(args['category_data'])
        crawl_data['source'] = self.data['source']
        crawl_data.update(get_ctime())
        return crawl_data

    def save_list(self, items, **args):
        for item in items:
            source_id = self.mackining(item.xpath(self.search_list_xpath('source_id')))
            if not source_id:
                continue
            task_data = self.has_goods(source_id)
            if not task_data:
                data = {
                    'priorcategory': self.data['priorcategory'],
                }
                Scheduler.schedule(DetailCrawler.type, key=source_id, data=data)
                continue                

            crawl_data = self.get_crawl_data(item, category_data=args['category_data']
                , source_id=source_id, task_data=task_data)
            model = EcBasicModel(crawl_data)
            export(model)

    def extract_adword(self, adword):
        adword = adword.strip()
        if not adword:
            return ""
        regex_str = "<\D*?.*?>|<\D.*?/>|&nbsp;"
        adword = re.sub(regex_str, "", adword)
        return adword

    def crawl(self): 
        key = str(self.key)

        category_data = extract_category(self)
        page = 1 #从第一页开始
        while True:
            items = self.get_init_list(key, page)
            if not items: 
                break
            self.save_list(items, category_data=category_data)

            more_items = self.get_more_list(key, page)
            self.save_list(more_items, category_data=category_data)

            page += 1
     

class DetailCrawler(Crawler):

    type = "ecommerce.yhd.goodsdetail"

    def get_brand(self, summary, introduce, tree):
        dom = tree.xpath(self.ware_xpath("brand"))
        if dom:
            brand = dom[0].strip()
            return brand
        brand = get_brand(summary, introduce)
        return brand

    def ware_xpath(self,xpath):
        data = {
            'introduce': "//dl[@class='des_info clearfix']/dd/text()",
            'specifications': "//div[@tabindex='1']/dl[@class='standard']",
            'product_id': "//input[@id='productId]/@value",
            'item': "dd/text()",
            'label': "dd/label/text()",
            'brand': "//a[@id='brand_relevance']/text()",
            'images': "//div[@id='jsproCrumb']/div[@class='hideBox']//img/@src",
            'name': "//h1[@id='productMainName']/text()",
            'is_Bbc': "//dl[@id='detaiThreeAreasDl']//p[@class='add_02']/text()",
            'status': "//p[@class='sorry sorryMt']",
            'intro_img': "//div[@class='desbox']/table/tbody/tr/td/img[@style='width: 750px;display: block;']/@original",
        }
        return data[xpath]

    def parse_introduce(self, tree):
        introduce = tree.xpath(self.ware_xpath('introduce'))
        introd = {}
        for item in introduce:
            item = item.strip()
            if item == '': continue
            item = item.split(u'：',1)
            try:
                introd[item[0]] = item[1]
            except:
                pass
        return introd

    def parse_summary(self, tree):
        specifications = tree.xpath(self.ware_xpath('specifications'))      
        summary = {}
        for item in specifications:
            label = item.xpath(self.ware_xpath('label'))
            names = []
            values = []
            for i in label:
                i = i.strip()
                if i.strip() == '':  continue
                names.append(i)
            dd = item.xpath(self.ware_xpath('item'))
            for i in dd:
                i = i.strip()
                if i.strip() == '':  continue        
                values.append(i)
            summary.update(map(lambda x,y:[x,y],names,values))
        return summary

    def parse_images(self, tree):
        images = tree.xpath(self.ware_xpath('images'))
        return images

    def parse_intro_img(self, tree):
        intro_img = tree.xpath(self.ware_xpath('intro_img'))
        return intro_img

    def parse_name(self, tree):
        name = tree.xpath(self.ware_xpath('name'))
        if name:
            return name[0].strip()
        return ""

    def parse_is_Bbc(self, tree):
        is_Bbc_list = tree.xpath(self.ware_xpath('is_Bbc'))
        if is_Bbc_list:
            is_Bbc_str = is_Bbc_list[0]
            index = is_Bbc_str.find(u"1号店自营")
            return "Y" if index == -1 else "N"
        return "not sure"

    def parse_status(self, tree):
        sorry_dom = tree.xpath(self.ware_xpath('status'))
        if not sorry_dom:
            return 1
        return 0

    def parse_productId(self, tree):
        product_id_list = tree.xpath(self.ware_xpath('product_id'))
        product_id = ""
        if not product_id_list:
            product_id = product_id_list[0].strip()
        return product_id

    def get_info(self, tree):
        summary = self.parse_summary(tree)
        introduce = self.parse_introduce(tree)
        images = self.parse_images(tree)
        name = self.parse_name(tree)
        is_Bbc = self.parse_is_Bbc(tree)
        status = self.parse_status(tree)
        intro_img = self.parse_intro_img(tree)

        info = {
            "summary": summary,
            "introduce": introduce,
            'images': images,
            'name': name,
            'is_Bbc': is_Bbc,
            'status': status,
            'intro_img': intro_img,
            'product_id': product_id,
        }
        return info

    def convert_img(self, imgs):
        imgs_new = []
        regex_str = r"(?<=)_\d*?x\d*?(?=\.(jpg|png|gif))"
        for img in imgs:
            img_new = re.sub(regex_str, "", img)
            imgs_new.append(img_new)
        return imgs_new

    def crawler_data(self,tree):
        category_data = extract_category(self)      
        info = self.get_info(tree)
        summary = info["summary"]
        introduce = info["introduce"]
        images = info["images"]
        images = self.convert_img(images)
        brand = self.get_brand(summary, introduce, tree)
        version = get_version(summary, introduce)
        series = get_series(summary, introduce)      

        crawl_data = {
            'source': self.data.get('source'),
            'source_id': str(self.key),
            'name': info['name'],
            'images': images,
            'intro_img': info['intro_img'],
            'summary': summary,
            'introduce': introduce,
            'status': info['status'],
            'version': version,
            'brand': brand,
            'series': series,
            'comment': {
                'is_Bbc': info['is_Bbc'],
            },
        }
        crawl_data.update(category_data)
        crawl_data.update(get_ctime())
        return crawl_data

    def crawl(self):
        wareId = str(self.key)
        url = "http://item.yhd.com/item/%s"%wareId
        html_stream = ProcessData.get_web_data(url)
        tree = etree.HTML(html_stream.text)
        crawl_data = self.crawler_data(tree)
        product_id = self.parse_productId(tree)
        model = EcDetailModel(crawl_data)
        export(model)

        comment_data = {
            'uuid': model['id'],
            'status': crawl_data['status'],
            'brand': brand,
            'series': series,
            'version': version,
            'is_Bbc': crawl_data['comment']['is_Bbc'],
            'priorcategory': self.data['priorcategory'],
            'source_id': wareId,
        }
        Scheduler.schedule(CommentCrawler.type, key=product_id, data=comment_data)


class CommentCrawler(Crawler):
    type = "ecommerce.yhd.goodscomment"

    xpath = {
        "count": "//input[@id='pageCountPage']/@value",
        "item": "//div[@class='main']/div[@class='item good-comment']",
        "user_id": "div[@class='face']/a/@href",
        "user_name": "div[@class='nameBox']/span[@class='name']/text()",
        "score": "dl/dt[@class='user_info']/span[3]/@class",
        "tags": "dl/dd[@class='label clearfix']/span[@class='title']/i/text()",
        "content": "dl/dd[@class='clearfix']/span[@class='text']/a[@class='btn']/text()",
        "comment_id": "dl/dd[@class='clearfix']/span[@class='text']/a[@class='btn']/@href",
        "show_pic": "dl/dd[@class='pro_show']/div[@class='thumb_box clearfix']/"\
            "ul[@class='clearfix']/li/img/@src",
        "pubtime": "dl/dd[@class='replyBtn_con clearfix']/span[@class='date']/text()",
        "tags": "dl/dd[@class='label clearfix']/span[@class='title']/i/text()",
    }

    def convert_img(self, imgs):
        imgs_new = []
        regex_str = r"(?<=)_\d*?x\d*?(?=\.(jpg|png|gif))"
        for img in imgs:
            img_new = re.sub(regex_str, "", img)
            imgs_new.append(img_new)
        return imgs_new

    def get_response(self, key, page):
        url = "http://club.yhd.com/review/%s-%s.html" % (key,str(page))
        response = ProcessData.get_web_data(url)
        response.encoding = "utf-8"
        return response

    def get_count(self, tree):
        count = tree.xpath(self.xpath["count"])
        if count:
            try:
                return int(count[0])
            except:
                return 10
        return 0

    def get_userId(self, tree):
        user_id = tree.xpath(self.xpath["user_id"]) 
        if user_id:
            return user_id[0]  
        return ""

    def get_userName(self, tree):
        user_name = tree.xpath(self.xpath["user_name"]) 
        if user_name:
            return user_name[0].strip()
        return ""  

    def get_score(self, tree):
        score = tree.xpath(self.xpath["score"])
        if score:
            score = float(score[0].strip()[-1])
            return score
        return 0.0

    def get_tags(self, datas):
        xpath = self.xpath["tags"]
        res = datas.xpath(xpath)
        for i in res:
            res[res.index(i)] = i.strip()
        return res 

    def get_content(self, tree):
        content = tree.xpath(self.xpath["content"])
        if content:
            content = content[0].strip()
            return content
        return u""

    def get_showPic(self, tree):
        show_pic = tree.xpath(self.xpath["show_pic"])
        show_pic = self.convert_img(show_pic)
        return show_pic
        
    def get_pubtime(self, tree):
        pubtime = tree.xpath(self.xpath["pubtime"])[0]
        pubtime = for_time(pubtime)
        return pubtime

    def get_commentId(self, tree):
        comment_id = tree.xpath(self.xpath["comment_id"])
        if comment_id:
            return comment_id[0].strip()
        return ""

    def get_info(self, tree):
        user_id = self.get_userId(tree)
        user_name = self.get_userName(tree)
        score = self.get_score(tree)
        tags = self.get_tags(tree)
        content = self.get_content(tree)
        show_pic = self.get_showPic(tree)
        pubtime = self.get_pubtime(tree)
        comment_id = self.get_commentId(tree)
        
        info = {}
        info["user_id"] = user_id
        info["user_name"] = user_name
        info["score"] = score
        info["tags"] = tags
        info["content"] = content
        info["show_pic"] = show_pic
        info["pubtime"] = pubtime
        info["comment_id"] = comment_id
        return info

    def crawl(self):
        key = self.key
        category_data = extract_category(self)
        count = 3
        page = 1
        while page <= count:
            response = self.get_response(key, page)
            tree = etree.HTML(response.text)
            if page == 1:
                count = self.get_count(tree)
            items = tree.xpath(self.xpath["item"])
            for item in items:
                info = self.get_info(item)
                crawl_data = {
                    'eid': self.data['uuid'],
                    'source_id': self.data['source_id'],
                    'brand': self.data['brand'],
                    'series': self.data['series'],
                    'version': self.data['version'],
                    'source': self.data['source'],
                    'status': self.data["status"],
                    'comment': {
                        'is_Bbc': self.data['is_Bbc'],
                    }
                }
                crawl_data.update(info)
                crawl_data.update(category_data)
                crawl_data.update(get_ctime())
                model = EcCommentModel(crawl_data)
                export(model)

            page += 1


if __name__ == "__main__":
    data = {
        'source': 'yhd',
        # "priorcategory" : ["大小家电、汽车","大家电", "空调"],
        "priorcategory" : ["大小家电、汽车","大家电"],
    #     'uuid':uuid.uuid1(),
    #     'series': 'series',
    #     'brand': 'brand',
    #     'version': 'version',
    #     'source_id': '32683163',
    #     'is_Bbc': 'N', 
    }   
    ThirdCrawler(key="52899", data=data).crawl()
    # keys = 'http://list.yhd.com/c23021-0-0/'
    # ListCrawler(key ="21368",data=data).crawl()
    # ListCrawler(key ="21369",data=data).crawl()
    # DetailCrawler(key ='48886114',data=data).crawl()
    # f = FirstCrawler()
    # f.crawl()
    # ThirdCrawler(key='53957',data=data).crawl()
    # CommentCrawler(key='27806086',data=data).crawl()