# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.models.BaseModel import BaseModel

from peewee import CharField, Model, DecimalField, FloatField, DateField, DateTimeField, TextField, ForeignKeyField, \
	ManyToManyField, IntegerField


class PrintJobModel(BaseModel):

	userName = CharField(null=True)
	fileOrigin = CharField(null=True)	#new since db-scheme2
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
	slicerSettingsAsText = TextField(null=True)

	allFilaments = None
	allTemperatures = None

	filamentModelsByToolId = {}

	def printFila(self):
		for f in self.filaments:
			print(f)

	# Because I don't know how to add relation-models to peewee I use a temp-array
	def addFilamentModel(self, filamentModel):
		if self.allFilaments == None:
			self.allFilaments = []
		self.allFilaments.append(filamentModel)
		self.filamentModelsByToolId[filamentModel.toolId] = filamentModel
		pass


	def getFilamentModelByToolId(self, toolId):
		# load and init dict
		if (len(self.filamentModelsByToolId) == 0):
			self.loadFilamentsFromAssoziation()
		if (toolId in self.filamentModelsByToolId):
			return self.filamentModelsByToolId[toolId]
		return None

	def getFilamentModels(self):
		if self.allFilaments == None:
			self.allFilaments = []
		return self.allFilaments

	def getFilamentModelsFromAsso(self):
		return self.filaments	# fieldname from 'backref' in FilamentModel-Class

	# Current UI implementation could only handle one filament-spool, but databasemodel support multiple spools
	def loadFilamentsFromAssoziation(self):
		self.filamentModelsByToolId = {}
		allFilaments = self.filaments
		allFilamentsCount = len(allFilaments)
		if allFilamentsCount != 0:
			for filament in allFilaments:
				result = filament
				self.addFilamentModel(result)
		return self.allFilaments


	# Because I don't know how to add relation-models to peewee I use a temp-array
	def addTemperatureModel(self, temperatureModel):
		if self.allTemperatures == None:
			self.allTemperatures = []
		self.allTemperatures.append(temperatureModel)
		pass

	def getTemperatureModels(self):
		if self.allTemperatures == None:
			self.allTemperatures = []
		return self.allTemperatures

	def loadTemperaturesFromAssoziation(self):
		result = []
		allTemps = self.temperatures
		allTemperaturesCount = len(allTemps)
		if allTemperaturesCount != 0:
			for temps in allTemps:
				result.append(temps)
		return result
