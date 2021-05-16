# coding=utf-8
from __future__ import absolute_import

import datetime

from peewee import Model, DateTimeField, PrimaryKeyField, AutoField


# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage.

def make_table_name(model_class):
    model_name = model_class.__name__
    return "pjh_" + model_name.lower()

class BaseModel(Model):

	databaseId = AutoField()
	created = DateTimeField(default=datetime.datetime.now)

	# def __init__(self):
	# 	# try:
	# 	# 	self.initialize()
	# 	# except AttributeError as ae:
	# 	# 	errorMessage = str(ae)
	# 	# 	if ("object has no attribute \'initialize\'" in errorMessage):
	# 	# 		raise NotImplemented("You need to implement initialize-methode in your database model classes")
	# 	# 	else:
	# 	# 		raise ae
	# 	# 	pass
	# 	pass


	class Meta:
		table_function = make_table_name
		pass
