# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.common import StringUtils
from octoprint_PrintJobHistory.models.BaseModel import BaseModel
# DO NOT IMPORT  from octoprint_PrintJobHistory.models.FilamentModel import FilamentModel


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

	allTemperatures = None

	filamentModelsByToolId = {}

	costModel = None
	# def initialize(self):
	# 	#  initialize with some a default
	# 	filamentModel = FilamentModel()
	# 	filamentModel.toolId
	# 	print("PrintJobModel.initialize")
	# 	pass

	def getCosts(self):
		if (self.costModel == None):
			# load costs from database
			if (self.costs != None and len(self.costs) > 0):
				self.costModel = self.costs[0]
		return self.costModel

	def setCosts(self, costModel):
		costModel.printJob = self
		self.costModel = costModel

	def addFilamentModel(self, filamentModel):
		#  check preconditions
		if (filamentModel == None):
			return
		if (StringUtils.isEmpty(filamentModel.toolId)):
			raise AttributeError("You can only add a FilamentModel with an toolId")

		filamentModel.printJob = self
		if (self.filamentModelsByToolId == None or len(self.filamentModelsByToolId) == 0):
			self._loadFilamentModels()

		self.filamentModelsByToolId[filamentModel.toolId] = filamentModel
		pass

	def getFilamentModels(self, withoutTotal = False):
		if (self.filamentModelsByToolId == None or len(self.filamentModelsByToolId) == 0):
			self._loadFilamentModels()
		allFilamentModels = self.filamentModelsByToolId.values()
		if (withoutTotal):
			newAllFilamentModels = []
			for filamentModel in allFilamentModels:
				if filamentModel.toolId != "total":
					newAllFilamentModels.append(filamentModel)
			allFilamentModels = newAllFilamentModels
			pass
		return allFilamentModels


	def getFilamentModelByToolId(self, toolId):
		# load and init dict
		if (self.filamentModelsByToolId == None or len(self.filamentModelsByToolId) == 0):
			self._loadFilamentModels()

		if (toolId in self.filamentModelsByToolId):
			return self.filamentModelsByToolId[toolId]
		return None


	def _loadFilamentModels(self):
		# clear and build up
		self.filamentModelsByToolId = {}
		# load from database
		allFilaments = self._getFilamentModelsFromAsso()
		if (allFilaments != None and len(allFilaments) > 0):
			for filament in allFilaments:
				self.filamentModelsByToolId[filament.toolId] = filament

	def _getFilamentModelsFromAsso(self):
		return self.filaments	# fieldname from 'backref' in FilamentModel-Class



	# Because I don't know how to add relation-models to peewee I use a temp-array
	def addTemperatureModel(self, temperatureModel):
		if self.allTemperatures == None:
			self.allTemperatures = []
		temperatureModel.printJob = self
		self.allTemperatures.append(temperatureModel)
		pass

	def getTemperatureModels(self):
		if (self.allTemperatures == None):
			self.allTemperatures = []

		tempAssos = self._getTemperatureModelsFromAsso()
		for temps in tempAssos:
			self.allTemperatures.append(temps)

		return self.allTemperatures

	def _getTemperatureModelsFromAsso(self):
		# all temperatures from asso
		allTemps = self.temperatures # fieldname from 'backref' in TemperatureModel-Class
		return allTemps
