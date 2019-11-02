#coding=utf8
import os
from lxml.etree import ElementTree
from django.conf import settings 


class Context(object):

	"""
	处理模块动态加载的类。

	使用方法：需要在配置文件中配置需要加载模块、属性，在想要导入的模块中调用get(),
	与import module | from module import attr 作用相同。
	"""

	def __init__(self):
		if not hasattr(self, "properties"):
			super(Context, self).__init__()
			self.file = os.path.join(settings.BASE_DIR, "settings/conf/context.xml")
			self.properties = {}
			self.load()

	def __new__(cls, *args, **kwargs):
		if not hasattr(cls, "_instance"):
		 	orig = super(Context, cls)  
			cls._instance = orig.__new__(cls, *args, **kwargs)
		return cls._instance

	def load(self):
		"""
		加载配置文件信息。

		"""
		tree = ElementTree(file=self.file)
		for i in tree.getroot().iterfind("object"):
			self.properties[i.get("id")] = {"module": i.get("module"), "attr": i.get("attr")}

	def get(self, text):
		"""
		@text：要导入的模块或属性的id。
		"""
		data = self.properties.get(text)
		return self.import_by_str(data["module"], data["attr"])

	def import_by_str(self, module, attr):
		"""
		对__import__方法的封装。

		@module：模块名。
		@attr：属性名。
		"""
		if attr:
			return getattr(__import__(module, {}, {}, [module]), attr)
		else:
			return __import__(module, {}, {}, [module])


if __name__ == '__main__':
	print Context().properties["ZjldArticleModel"]
	
