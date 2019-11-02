# -*- coding: utf-8 -*-


class Field(object):

	def __init__(self, name=None, path=None, type=None, widget=None, 
			value=None, must=False, multiValued=False):
		self.name = name
		self.path = path
		self.type = type
		self.widget = widget
		self.value = value
		self.must = must
		self.multiValued = multiValued


class Url(str):
	pass
