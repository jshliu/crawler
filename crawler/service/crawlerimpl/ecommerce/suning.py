#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    author:jshliu
    time: 2015-8-12
    vision: v.1.0
    rebark: suning   爬虫代码编写  
'''

import sys
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
    check_encoding, get_ctime, get_version, get_brand, get_series,\
    get_address, get_press_time, for_time
import re
import uuid


class FirstCrawler(Crawler):
	type = "ecommerce.suning.firstlvl"

	@staticmethod
	def init(conf=None):
		# pass
		Scheduler.schedule(FirstCrawler.type)

	url = "http://api.m.suning.com/mts-web/appbuy/public/getShopKindsInfo.do?channelId=&appId=1&isShowTopic=1&"

	def crawl(self):
		response = ProcessData.get_json_data(self.url)
		first_objs = response["shopKindInfo"]
		for first_obj in first_objs:
			for second_obj in first_obj["kindList2"]:
				for third_obj in second_obj["kindList3"]:
					key = third_obj["ci"]
					first_cat = first_obj["kindName"].replace(" ", "")
					second_cat = second_obj["kindName"].replace(" ", "")
					third_cat = third_obj["kindName"].replace(" ", "")
					data = {
						"priorcategory": [first_cat,second_cat,third_cat,]
					}
					# if second_cat != u"冰箱" and second_cat != u"空调":
					# 	continue
					Scheduler.schedule(ListCrawler.type, key=key, data=data, interval=86400)


class ListCrawler(Crawler):
	type = "ecommerce.suning.goodslist"

	def get_url(self, key, page):
		return "http://search.suning.com/emall/mobile/mobileSearch.jsonp"\
			"?unsale=1&channelId=MOBILE&st=14&ct=-1&yuyue=-1&cp=%s&ps=10&i"\
			"fhf=0&set=5&jz=1&cityId=9173&iv=-1&ci=%s&" % (str(page), key)

	def get_page_size(self, data):
		count = int(data["goodsCount"])
		if count % 10 == 0:
			return count/10 - 1 
		else:
			return count/10

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
		page_size = 0
		page = 0
		while page <= page_size:
			url = self.get_url(self.key, page)
			json_data = ProcessData.get_json_data(url)
			if page == 0:
				page_size = self.get_page_size(json_data)
			for goods in json_data["goods"]:
				source_id = goods["partnumber"]
				task_data = self.has_goods(self.key)
				if not task_data:
					data = {
						"priorcategory": self.data["priorcategory"],
						"status": 1 if int(goods["saleStatus"]) == 0 else 0,
					}
					Scheduler.schedule(DetailCrawler.type, key=source_id, data=data)
				else:
					crawl_data = {
						"id": task_data["uuid"],
						"source": self.data["source"],
						"source_id": source_id,
						"title": goods["catentdesc"],
						"adword": extract_adword(goods.get("auxdescription", "")),
						"price": float(goods["price"]),
						'status': task_data['status'],
						'brand': task_data['brand'],
						'version': task_data['version'],
						'series': task_data['series'],
						'comment': {
							'is_Bbc': task_data['is_Bbc'],
						},
					}
					crawl_data.update(category_data)
					crawl_data.update(get_ctime())
					model = EcBasicModel(crawl_data)
					export(model)
			page += 1


class DetailCrawler(Crawler):
	type = "ecommerce.suning.goodsdetail"

	xpath = {
		"name": "//h1[@id='itemDisplayName']/text()",
		"images": "//div[@class='imgzoom-thumb-main']/ul/li//img/@src-large",
		"introduce": "//div[@id='kernelParmeter']/ul[@class='cnt clearfix']/li",
		"summary": "//div[@id='J-procon-param']/div[@class='procon-param']/tab"\
			"le/tbody/tr",
		"intro_img": "//div[@id='productDetail']//img/@src2",
		"shop_name": "//span[@id='curShopName']",
	}

	def get_url(self, key):
		return "http://product.suning.com/%s.html" % key

	def get_response(self, key):
		url = self.get_url(key)
		response = ProcessData.get_web_data(url)
		return response

	def get_name(self, tree):
		name = tree.xpath(self.xpath["name"])
		if name:
			return name[0].strip()
		return ""

	def get_images(self, tree):
		imgs = tree.xpath(self.xpath["images"])
		for img in imgs:
			imgs[imgs.index(img)] = self.convert_img(img)
		return imgs

	def convert_img(self, img):
		return re.sub(r"(?<=)_\d*?x\d*?(?=\.(jpg|png|gif))", "", img)

	def get_introduce(self, tree):
		li_list = tree.xpath(self.xpath["introduce"])
		introduce = {}
		for li in li_list:
			li_str = li.xpath("string(.)")
			key, value = li_str.split("：")
			introduce[key] = value
		return introduce

	def get_summary(self, tree):
		tr_list = tree.xpath(self.xpath["summary"])
		summary = {}
		for tr in tr_list:
			key = tr.findtext("td[@class='name']/div[@class='name-inner']/span")
			if not key:
				key = tr.findtext("td[@class='name']")
			if key:
				value = tr.findtext("td[@class='val']")
				summary[key.strip()] = value
		return summary

	def get_intro_img(self, tree):
		imgs = tree.xpath(self.xpath["intro_img"])
		for img in imgs:
			imgs[imgs.index(img)] = str(img)
		return imgs

	def get_is_Bbc(self, key):
		url = "http://www.suning.com/emall/psl_10052_10051_000000000"\
			"%s_9135_11082" % key
		data = ProcessData.get_json_data(url)
		isCShop = data["shopList"][0]["isCShop"]
		if int(isCShop) == 1:
			return "N"
		return "Y"

	def get_info(self, tree):
		name = self.get_name(tree)
		images = self.get_images(tree)
		introduce = self.get_introduce(tree)
		summary = self.get_summary(tree)
		intro_img = self.get_intro_img(tree)
		info = {
			"name": name,
			"images": images,
			"introduce": introduce,
			"summary": summary,
			"brand": get_brand(summary, introduce),
			"series": get_series(summary, introduce),
			"version": get_version(summary, introduce),
			"address": get_address(summary, introduce),
			"intro_img": intro_img,
		}
		return info

	def crawl(self):
		response = self.get_response(self.key)
		tree = etree.HTML(response.text)
		info = self.get_info(tree)
		is_Bbc = self.get_is_Bbc(self.key)
		category_data = extract_category(self)
		crawl_data = {
			"source": self.data["source"],
			"source_id": self.key,
			"status": self.data["status"],
			"comment": {
				"is_Bbc": is_Bbc,
			},
		}
		crawl_data.update(info)
		crawl_data.update(category_data)
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
	type = "ecommerce.suning.goodscomment"

	def get_url(self, key, page):
		return "http://review.suning.com/mobile/getReviewList/general-000000000"\
			"%s--total-%s-default-10-----.htm" % (key, str(page))

	def get_page_size(self, key):
		url = "http://review.suning.com/mobile/getReviewCnt/general-000000000"\
			"%s------.htm" % key
		json_data = ProcessData.get_json_data(url)
		count = int(json_data["reviewCounts"][0].get("totalCount", "0"))
		if count%10 == 0:
			return count/10
		else:
			return count/10 + 1

	def get_comment_id(self, data):
		return "http://review.suning.com/detail_review/%s-%s-1.htm"\
			% (data["commodityReviewId"], self.key)

	def get_tags(self, data):
		objs = data["labelNames"]
		tags = []
		for obj in objs:
			tags.append(obj["labelName"])
		return tags

	def get_show_pic(self, data):
		objs = data.get("picVideInfo", {}).get("imageInfo", [])
		imgs = []
		for obj in objs:
			imgs.apped("http://image.suning.cn/uimg/ZR/share_order/%s.jpg" % obj["url"])
		return imgs

	def get_pubtime(self, data):
		time_str = data["publishTime"]
		return for_time(time_str)

	def crawl(self):
		category_data = extract_category(self)
		page_size = self.get_page_size(self.key)
		page = 1
		while page <= page_size:
			json_data = ProcessData.get_json_data(self.get_url(self.key, page))
			reviews = json_data.get("commodityReviews", [])
			if not reviews:
				return
			for review in reviews:
				crawl_data = {
					"comment_id": self.get_comment_id(review),
					"content": review["content"],
					"tags": self.get_tags(review),
					"show_pic": self.get_show_pic(review),
					"pubtime": self.get_pubtime(review),
					"score": float(review["qualityStar"]),
					"useful": int(review["usefulCnt"]),
					"reply": 1 if review.get("replyInfo", {}) else 0,
					"user_name": review.get("userInfo", {}).get("nickName", ""),
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
				crawl_data.update(category_data)
				crawl_data.update(get_ctime())
				model = EcCommentModel(crawl_data)
				export(model)
			page += 1


if __name__ == '__main__':
	FirstCrawler().crawl()
	# data={
	# 	"uuid": uuid.uuid1(),
	# 	"priorcategory": ["家用电器", "空调", "家用空调",],
	# 	"source": "suning",
	# 	"status": 1,
	# 	"brand": "brand",
	# 	"version": "version",
	# 	"series": "series",
	# 	"is_Bbc": "N",
	# }
	# # key = "431505"
	# key = "129564647"
	# # ListCrawler(key=key, data=data).crawl()
	# # DetailCrawler(key=key, data=data).crawl()
	# CommentCrawler(key=key, data=data).crawl()