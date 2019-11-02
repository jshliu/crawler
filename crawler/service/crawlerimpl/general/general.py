# -*- coding: utf-8 -*-
import re
from lxml import etree, html
from datetime import datetime

from context.context import Context

Crawler = Context().get("Crawler")
export = Context().get("export")
Handler = Context().get("Handler")
SearchArticleModel = Context().get("SearchArticleModel")
ZjldArticleModel = Context().get("ZjldArticleModel")
Readability = Context().get("Readability")
htmlutil = Context().get("htmlutil")
clear_space = Context().get("textutil.clear_space")
new_time = Context().get("datetimeutil.new_time")
fmt_time = Context().get("datetimeutil.fmt_time") 
local2utc = Context().get("datetimeutil.local2utc") 
Field = Context().get("Field") 
Url = Context().get("Url") 
join_path = Context().get("pathutil.join_path")
getTag = Context().get("bosonutil.getTag")


PROXIES = {
	"http": "http://192.168.1.165:8888",
	"https": "http://192.168.1.191:8888"
}

def find_field(name, fields):
	for i in fields:
		if i.name == name:
			return i

class SearchContentCrawler(Crawler):
	"""
	通用的元搜索内容爬虫。

	除了content与tag由通用算法解析获得，其余信息均由任务传递获得。

	"""

	type = "general.search_content"

	def __init__(self, task):
		super(SearchContentCrawler, self).__init__(task)

	def crawl(self):
		url = str(self.key)
		if self.data["source"] == "google":
			response = htmlutil.get_response(url, proxies=PROXIES)
		else:
			response = htmlutil.get_response(url)
		soup = Readability(response.text, url)
		comment = {
			'count': str(self.data.get('count','')),
		}
		if self.data.get('industry'):
			comment.update({'industry': self.data.get('industry')})

		tag = str(getTag(clear_space(htmlutil.extract_text(soup.content))))

		crawl_data = {
			'title': self.data['title'],
			'pubtime': self.data.get('pubtime', datetime.utcnow),
			'source': self.data['source'],
			'publisher': self.data.get('publisher', ''),
			'origin_source': self.data.get('origin_source', ''),
			'url': url,
			'key': self.data.get('key', ''),
			'content': soup.content,
			'tag': tag,
			'comment': comment,
			'producer_id': self.task.producer_id,
			'category': self.task.category,
			'application': self.task.application,
		}
		crawl_data.update(new_time())
		if crawl_data['content']:
			model = SearchArticleModel(crawl_data)
			export(model)


class ArticleContentCrawler(Crawler):
	"""
	通用的文章内容爬虫。

	tag由通用算法解析获得，content可由任务传递的xpath或者通用算法解析获得，
	title可由任务传递的xpath或者通用算法解析获得，也可由任务直接传递赋值 ，
	pubtime可由任务传递的xpath解析获得或者由任务直接传递赋值。

	"""

	type = "general.article_content"

	def __init__(self, task):
		super(ArticleContentCrawler, self).__init__(task)
		self.xpath = self.data.get("xpath", {})
		self.header = self.data.get("headers", {})
		self.post_data = self.data.get("post_data")

	def get_text(self, tree, text):
		if self.data.get(text):
			return self.data[text]
		elif self.xpath.get(text):
			return htmlutil.get_text(tree, self.xpath[text])
		else:
			return ""

	def get_pubtime(self, tree):
		if self.data.get("pubtime"):
			return self.data["pubtime"]
		elif self.xpath.get("pubtime"):
			pubtime = htmlutil.get_datetime(tree, self.xpath["pubtime"])
			return local2utc(pubtime) if pubtime else datetime.utcnow()
		else:
			return datetime.utcnow()

	def get_content(self, tree, url):
		if self.xpath.get("content"):
			content_list = tree.xpath(self.xpath["content"])
			if len(content_list) > 0:
				content_all = html.tostring(content_list[0], encoding=unicode)
				content_text = content_list[0].xpath("string(.)").strip()
				content_all = htmlutil.clear_label(content_all, url)
				content_text = clear_space(content_text)
				return {
					"content_all": content_all,
					"content_text": content_text,
				}
		return {
			"content_all": "",
			"content_text": "",
		}

	def get_info(self, tree):
		content_info = self.get_content(tree, self.key)
		return {
			"title": self.get_text(tree, "title"),
			"pubtime": self.get_pubtime(tree),
			"author": self.get_text(tree, "author"),
			"content_all": content_info["content_all"],
			"content_text": content_info["content_text"],
		}

	def get_tree(self, response):
		tree = etree.HTML(response.text)
		if not tree:
			match = htmlutil.extract_html(response.text)
			if not match:
				match = htmlutil.extract_xml(response.text)
			tree = etree.HTML(match)
		return tree

	def crawl(self):
		response = htmlutil.get_response(self.key, data=self.post_data, headers=self.header)
		info = self.get_info(self.get_tree(response))
		if not info["content_all"] or not info["title"]:
			soup = Readability(response.text, self.key)
			if not info["content_all"]:
				info["content_all"] = soup.content
				info["content_text"] = clear_space(info["content_all"])
			if not info["title"]:
				info["title"] = soup.title
		if not info['content_all'] and not info["title"]:
			return
			
		tag = str(getTag(info["content_text"]))
		crawl_data = {
			'url': self.key,
			'province': self.data.get("province", ""),
			'city': self.data.get("city", ""),
			'district': self.data.get("district", ""),
			'title': info["title"],
			'content': info["content_all"],
			'pubtime': info["pubtime"],
			'author': info["author"],
			'source': self.data["source"],
			'publisher': self.data.get("publisher", ""),
			'tag': tag,
			'comment': {},
			'producer_id': self.task.producer_id,
			'category': self.task.category,
			'application': self.task.application,
		}
		crawl_data.update(new_time())
		model = ZjldArticleModel(crawl_data)
		export(model)


class FatherCrawler(Crawler):
	"""
	通用的一级爬虫类，大部分需要生成任务的爬虫可以继承此类。

	使用方法：
		1. 每一个需要传递的字段都是一个Field对象，该对象可以直接赋值,也可以赋予解析规则，目前只支持正则与xpath。
		2. 需要指定哪些些字段需要传递到下一爬虫，为成员属性export_fields赋值即可。
		3. 需要指定生成的任务由哪一爬虫执行，为成员属性child赋值即可。
		4. 可以指定请求头信息，headers，可以以指定开始爬取的页数，start_page。
		5. 想要对解析后的字段进行加工可以定义自定义方法，方法名为dehydrate_Field.name。

	具体详细使用参见元搜索爬虫编写代码。

	"""

	start_page = 1
	export_fields = []
	export_key = False
	child = None
	headers = None
	xpath = {}
	current_url = ""
	this_info = {}

	def __init__(self, task):
		super(FatherCrawler, self).__init__(task)
		self.last_info = self.data.get("last_info", {}).copy()
		self.init_instance()


	def get_url(self, key, page):
		raise NotImplementedError("method get_url must be implemented!")

	def get_req_data(self, key, page):
		return None

	def get_key(self):
		for i in self.fields:
			if i.name == "key":
				return i
		raise ValueError("must have a Field which name is key!")

	def init_instance(self):
		self.fields = self.get_fields()
		self.key_field = self.get_key()
		if self.export_fields:
			return self.export_fields
		else:
			for i in self.fields:
				if i.name != self.key_field.name and i.name != "item" and i.name != "page_size":
					self.export_fields.append(i)

	def is_last_node(self, data):
		flag = False
		if self.last_info:
			for i in self.last_info.keys():
				if isinstance(self.last_info[i], datetime):
					if self.last_info[i] > data[i]:
						return True
					elif self.last_info[i] == data[i]:
						continue
				if self.last_info[i] != data[i]:
					return False
				else:
					flag = True
		return flag

	def get_page_size(self, tree, current_url):
		field = find_field("page_size", self.fields)
		if field:
			if field.value:
				return field.value
			else:
				value = htmlutil.get_text(tree, field.path)
			res = self.dehydrate_field(field, value, current_url)
			return int(res)
		return 0

	def dehydrate_field(self, field, value, current_url):
		method = getattr(self, "dehydrate_%s" % field.name, None)
		if method:
			return method(value, current_url)
		else:
			return value

	def get_fields(self):
		items = []
		for i in dir(self):
			if not i.endswith("__"):
				attr = getattr(self, i)
				if isinstance(attr, Field):
					items.append(attr)
		return items

	def get_info(self, tree, current_url):
		info = {
			"key": self.crawl_data(self.key_field, tree, current_url),
			"data": {},
		}
		if not info["key"]:
			return None
		for i in self.fields:
			value = self.crawl_data(i, tree, current_url)
			if i.must:
				if not value:
					return None
			info["data"].update({i.name: value})
		return info

	def crawl_data(self, field, tree, current_url=None):
		if field.value:
			value = field.value
		else:
			if field.multiValued:
				value = htmlutil.get_list(tree, field.path)
			if isinstance(tree, etree._Element):
				value = self.crawl_data_xpath(field, tree, current_url)
			elif isinstance(tree, basestring):
				value = self.crawl_data_regex(field, tree, current_url)
			else:
				return None
		return value

	def crawl_data_xpath(self, field, tree, current_url):
		value = htmlutil.get_text(tree, field.path)
		value = self.dehydrate_field(field, value, current_url)
		if field.type and value:
			if field.type == Url:
				value = join_path(current_url, value)
			elif field.type == datetime:
				value = fmt_time(value)
		return value

	def crawl_data_regex(self, field, tree, current_url):
		value = re.search(field.path, tree, re.S)
		value = self.dehydrate_field(field, value, current_url)
		return value

	def get_export_data(self, data):
		res = {}
		for i in self.export_fields:
			res.update({i.name: data[i.name]})
		res.update({"source": self.data["source"]})
		res.update({"headers": self.headers})
		res.update({"xpath": self.xpath})
		if self.data.get("industry"):
			res.update({"industry": self.data.get("industry")})
		if self.export_key:
			res.update({"key": self.key})
		return res

	def filter(self, key, data):
		return True

	def update_last_info(self, data):
		if self.data.get("last_info", {}) and data:
			for i in self.last_info.keys():
				self.last_info[i] = data[i]

	def get_tree(self, response):
		return etree.HTML(response.text)

	def get_items(self, tree):
		return htmlutil.get_list(tree, find_field("item", self.fields).path)

	def handle(self):
		page = self.start_page
		page_size = page
		while page <= page_size:
			homepage = self.get_url(self.key, page)
			response = htmlutil.get_response(homepage, headers=self.headers,
				data=self.get_req_data(self.key, page))
			tree = self.get_tree(response)
			if page == 1:
				page_size = self.get_page_size(tree, self.current_url if self.current_url else homepage)
			items = self.get_items(tree)

			if not items:
				return
			for item in items:
				info = self.get_info(item, self.current_url if self.current_url else homepage)
				if info:
					if self.filter(info["key"], info["data"]):
						if self.is_last_node(info["data"]):
							return
						Handler.handle(self.child.type ,key=info["key"],data=self.get_export_data(info["data"]), 
							producer_id=self.task.producer_id, category=self.task.category,
							application=self.task.application)
						if page == self.start_page and items.index(item) == 0:
							self.this_info = info["data"]
			page += 1

	def crawl(self):
		if not self.child:
			raise ValueError("child crawler must be specified!")
		self.handle()
		self.update_last_info(self.this_info)


if __name__ == '__main__':
	pass