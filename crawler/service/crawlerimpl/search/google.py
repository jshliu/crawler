#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
import re
from json import loads
from lxml import etree
from datetime import datetime
from HTMLParser import HTMLParser
from service.scheduler.crawler import Crawler
from service.scheduler.handler import Handler
from utils.readability import Readability
from utils import htmlutil
from utils.datetimeutil import local2utc
from service.crawlerimpl.general.general import SearchContentCrawler, PROXIES


class EventCrawler(Crawler):
	type = "google.newstitle"

	__xpath = {
		"item": "//ol/li[@class='g']/table/tr/td[1]",
		"title": "h3[@class='r']/a",
		"url": "h3[@class='r']/a/@href",
		"publisher": "div[@class='slp']/span[@class='f']/text()",
		"pubtime": "div[@class='slp']/span[@class='f']/text()",
		"page_size": "//div[@id='resultStats']/text()",
	}

	def __init__(self, **kwargs):
		super(EventCrawler, self).__init__(key=kwargs.get('key', ""), data=kwargs.get('data', {}))
		self.last_pubtime = self.data.get("last_pubtime")
		self.last_url = self.data.get("last_url")
		self.temp_pubtime = datetime.min

	@staticmethod
	def init(conf=None):
		pass

	def get_url(self, keyword, page):
		url = "https://www.google.com.sg/search?q="\
			"%s&biw=1600&bih=487&tbs=sbd:1&tbm=nws"\
			"&ei=9nb2Vb_DFdPnuQTUhamwDg&start=%s&s"\
			"a=N&bav=on.2,or.&fp=4156eba20fd7f44f&"\
			"tch=1&ech=1&psi=BHX2VZ3dGIqKuASO2J_4D"\
			"Q.1442215609288.7s" % (keyword, str(page-1)*10)
		return url

	def get_href(self, tree):
		url_str = htmlutil.get_text(tree, self.__xpath["url"])
		if url_str:
			match = re.match(r"/url\?q=(.*?)&", url_str)
			if match:
				return match.group(1)
		return ""

	def get_publisher(self, tree):
		pbler_str = htmlutil.get_text(tree, self.__xpath["publisher"])
		if pbler_str:
			return pbler_str.split("-")[0].strip()
		return ""

	def get_info(self, tree):
		title = htmlutil.get_text(tree, self.__xpath["title"])
		publisher = self.get_publisher(tree)
		pubtime = htmlutil.get_datetime(tree, self.__xpath["pubtime"])
		pubtime = local2utc(pubtime) if pubtime else pubtime
		info = {
			"title": title,
			"publisher": publisher,
			"pubtime": pubtime,
			"source_type": self.data.get("source_type", ""),
			"key": self.key,
			"source": self.data["source"],
			"origin_source": u"谷歌新闻搜索",
		}
		return info

	def is_last_node(self, pubtime, url):
		if self.last_pubtime:
			if self.last_pubtime > pubtime:
				return True
			if self.last_pubtime == pubtime:
				if self.last_url == url:
					return True
		return False

	def get_page_size(self, tree):
		page_str = htmlutil.get_text(tree, self.__xpath["page_size"])
		if page_str:
			page_str = page_str.replace(",", "")
			match = re.search(r"\d+", page_str)
			if match:
				news_count = int(match.group(0))
				if news_count%10 == 0:
					return news_count/10
				else:
					return news_count/10 + 1
		return 1

	def get_html(self, text):
		text = text.split('/*""*/')[1]
		json_data = loads(text)
		parser = HTMLParser()
		html_text = parser.unescape(json_data["d"])
		return html_text

	def handle(self):
		page = 1
		page_size = 3
		while page <= page_size:
			url = self.get_url(self.key, page)
			response = htmlutil.get_response(url, proxies=PROXIES)
			tree = etree.HTML(self.get_html(response.text))
			if page == 1:
				page_size = self.get_page_size(tree)
			items = tree.xpath(self.__xpath["item"])
			for item in items:
				crawl_data = self.get_info(item)
				pubtime = crawl_data["pubtime"]
				url = self.get_href(item)
				if not pubtime:
					continue
				if self.is_last_node(pubtime, url):
					return
				crawl_data["key"] = self.key
				Scheduler.schedule(SearchContentCrawler.type, key=url,
					data=crawl_data)
				if self.temp_pubtime < pubtime:
					self.temp_pubtime = pubtime
					self.last_url = url

			if not self.last_pubtime:
				break
			page += 1

	def crawl(self):
		self.handle()
		if self.last_pubtime:
			if self.temp_pubtime < self.last_pubtime:
				self.temp_pubtime = self.last_pubtime
		self.data.update({"last_pubtime": self.temp_pubtime, "last_url": self.last_url})

"""


