#coding=utf-8
import os
from lxml.etree import ElementTree


class Config(object):
	
	properties = {}

	def __init__(self, file):
		super(Config, self).__init__()
		self.file = file
		self.load()

	def load(self):
		tree = ElementTree(file=self.file)
		for i in tree.getroot().iterfind("property"):
			name = i.findtext("name")
			if name:
				self.properties[name] = i.findtext("value")

	def get(self, key, default=None):
		return self.properties.get(key, default)




if __name__ == '__main__':
	print Config("core-site.xml").properties
