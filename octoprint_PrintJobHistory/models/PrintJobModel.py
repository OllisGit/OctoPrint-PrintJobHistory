# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.models.BaseModel import BaseModel

from peewee import CharField, Model, DecimalField, FloatField, DateField, DateTimeField, TextField, ForeignKeyField, \
	ManyToManyField, IntegerField


class PrintJobModel(BaseModel):

	userName = CharField(null=True)
	fileName = CharField(null=True)
	filePathName = CharField(null=True)
	fileSize = IntegerField(null=True)
	printStartDateTime = DateTimeField(null=True)
	printEndDateTime = DateTimeField(null=True)
	duration = IntegerField(null=True)
	printStatusResult = CharField(null=True)
	noteText = CharField(null=True)
	noteDeltaFormat = CharField(null=True)
	noteHtml = CharField(null=True)
	printedLayers = CharField(null=True)
	printedHeight = CharField(null=True)

	allFilaments = None
	allTemperatures = None

	# Because I don't know how to add relation-models to peewee I use a temp-array
	def addFilamentModel(self, filamentModel):
		if self.allFilaments == None:
			self.allFilaments = []
		self.allFilaments.append(filamentModel)
		pass

	def getFilamentModels(self):
		return self.allFilaments

	# Current UI implementation could only handle one filament-spool, but databasemodel support multiple spools
	def getFilamentFromAssoziation(self):
		result = None
		allFilaments = self.filaments
		allFilamentsCount = len(allFilaments)
		if allFilamentsCount != 0:
			for filament in allFilaments:
				result = filament
				break
		return result


	# Because I don't know how to add relation-models to peewee I use a temp-array
	def addTemperatureModel(self, temperatureModel):
		if self.allTemperatures == None:
			self.allTemperatures = []
		self.allTemperatures.append(temperatureModel)
		pass

	def getTemperatureModels(self):
		return self.allTemperatures

	def getTemperaturesFromAssoziation(self):
		result = []
		allTemps = self.temperatures
		allTemperaturesCount = len(allTemps)
		if allTemperaturesCount != 0:
			for temps in allTemps:
				result.append(temps)
		return result
