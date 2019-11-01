# coding=utf-8
from __future__ import absolute_import

import os
import sqlite3

from octoprint_PrintJobHistory.models.FilamentModel import FilamentModel
from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from octoprint_PrintJobHistory.models.PluginMetaDataModel import PluginMetaDataModel
from octoprint_PrintJobHistory.models.TemperatureModel import TemperatureModel
from peewee import *

from peewee import BackrefAccessor

from .entities.PrintJobEntity import PrintJobEntity
from .entities.FilamentEntity import FilamentEntity
from .entities.TemperatureEntity import TemperatureEntity
from .entities.PluginMetaDataEntity import PluginMetaDataEntity

from datetime import datetime

FORCE_CREATE_TABLES = False
SQL_LOGGING = True

CURRENT_DATABASE_SCHEME_VERSION = 1

# List all Models
MODELS = [PluginMetaDataModel, PrintJobModel, FilamentModel, TemperatureModel]


class DatabaseManager(object):

	def __init__(self):
		self._database = None
		self._databaseFileLocation = None

	################################################################################################## private functions

	def _createOrUpgradeSchemeIfNecessary(self):
		schemeVersionFromDatabaseModel = None
		try:
			schemeVersionFromDatabaseModel = PluginMetaDataModel.get(PluginMetaDataModel.key == PluginMetaDataModel.KEY_DATABASE_SCHEME_VERSION)
			pass
		except Exception as e:
			errorMessage = e.message
			if errorMessage.startswith("no such table"):
				self._createDatabaseTables()
			else:
				print(str(e))

		if not schemeVersionFromDatabaseModel == None:
			currentDatabaseSchemeVersion = int(schemeVersionFromDatabaseModel.value)
			if (currentDatabaseSchemeVersion < CURRENT_DATABASE_SCHEME_VERSION):
				# evautate upgrade steps (from 1-2 , 1...6)
				print("We need to upgrade the database scheme from: '" + str(currentDatabaseSchemeVersion) + "' to: '" + str(CURRENT_DATABASE_SCHEME_VERSION) + "'")
				pass
		pass

		# databaseSchemeVersion = PluginMetaDataEntity.getDatabaseSchemeVersion(cursor)
		# if databaseSchemeVersion == None or FORCE_CREATE_TABLES == True:
		# 	self._createCurrentTables(cursor, FORCE_CREATE_TABLES)
		# else:
		# 	# check from which version we need to upgrade
		# 	#	sql
		# 	pass
	def _createDatabaseTables(self):
		self._database.connect(reuse_if_open=True)
		self._database.drop_tables(MODELS)
		self._database.create_tables(MODELS)

		PluginMetaDataModel.create(key=PluginMetaDataModel.KEY_DATABASE_SCHEME_VERSION, value=CURRENT_DATABASE_SCHEME_VERSION)
		self._database.close()

	################################################################################################### public functions
	# datapasePath '/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory'
	def initDatabase(self, databasePath):

		self._databaseFileLocation = os.path.join(databasePath, "printJobHistory.db")

		if SQL_LOGGING == True:
			import logging
			logger = logging.getLogger('peewee')
			# logger.addHandler(logging.StreamHandler())
			logger.setLevel(logging.DEBUG)

		self._database = SqliteDatabase(self._databaseFileLocation)
		DatabaseManager.db = self._database
		self._database.bind(MODELS)

		if FORCE_CREATE_TABLES:
			self._createDatabaseTables()
		else:
			# check, if we need an scheme upgrade
			self._createOrUpgradeSchemeIfNecessary()
		pass

	def getDatabaseFileLocation(self):
		return self._databaseFileLocation


	def insertPrintJob(self, printJobModel):
		databaseId = None
		with self._database.atomic() as transaction:  # Opens new transaction.
			try:
				printJobModel.save()
				databaseId = printJobModel.get_id()
				# save all relations
				# - Filament
				for filamentModel in printJobModel.getFilamentModels():
					filamentModel.printJob = printJobModel
					filamentModel.save()
				# - Temperature
				for temperatureModel in printJobModel.getTemperatureModels():
					temperatureModel.printJob = printJobModel
					temperatureModel.save()
				# do expicit commit
				transaction.commit()
			except Exception as e:
				# Because this block of code is wrapped with "atomic", a
				# new transaction will begin automatically after the call
				# to rollback().
				transaction.rollback()
				print(str(e))
				# 	TODO do something usefull
			pass

		return databaseId

	def updatePrintJob(self, printJobModel):
		with self._database.atomic() as transaction:  # Opens new transaction.
			try:
				printJobModel.save()
				databaseId = printJobModel.get_id()
				# save all relations
				# - Filament
				# for filamentModel in printJobModel.getFilamentModels():
				# 	filamentModel.printJob = printJobModel
				# 	filamentModel.save()
				# # - Temperature
				# for temperatureModel in printJobModel.getTemperatureModels():
				# 	temperatureModel.printJob = printJobModel
				# 	temperatureModel.save()
			except:
				# Because this block of code is wrapped with "atomic", a
				# new transaction will begin automatically after the call
				# to rollback().
				transaction.rollback()
				# 	TODO do something usefull
			pass




	def countPrintJobsByQuery(self, tableQuery):

		filterName = tableQuery["filterName"]

		myQuery = PrintJobModel.select()
		if (filterName == "onlySuccess"):
			myQuery = myQuery.where(PrintJobModel.printStatusResult == "success")
		elif (filterName == "onlyFailed"):
			myQuery = myQuery.where(PrintJobModel.printStatusResult != "success")

		return myQuery.count()


	def loadPrintJobsByQuery(self, tableQuery):
		offset = int(tableQuery["from"])
		limit = int(tableQuery["to"])
		sortColumn = tableQuery["sortColumn"]
		sortOrder = tableQuery["sortOrder"]
		filterName = tableQuery["filterName"]

		myQuery = PrintJobModel.select().offset(offset).limit(limit)
		if (filterName == "onlySuccess"):
			myQuery = myQuery.where(PrintJobModel.printStatusResult == "success")
		elif (filterName == "onlyFailed"):
			myQuery = myQuery.where(PrintJobModel.printStatusResult != "success")

		if ("printStartDateTime" == sortColumn):
			if ("desc" == sortOrder):
				myQuery = myQuery.order_by(PrintJobModel.printStartDateTime.desc())
			else:
				myQuery = myQuery.order_by(PrintJobModel.printStartDateTime)
		if ("fileName" == sortColumn):
			if ("desc" == sortOrder):
				myQuery = myQuery.order_by(PrintJobModel.fileName.desc())
			else:
				myQuery = myQuery.order_by(PrintJobModel.fileName)
		return myQuery

	def loadAllPrintJobs(self):
		return PrintJobModel.select().order_by(PrintJobModel.printStartDateTime.desc())

		# return PrintJobModel.select().offset(offset).limit(limit).order_by(PrintJobModel.printStartDateTime.desc())
		# all = PrintJobModel.select().join(FilamentModel).switch(PrintJobModel).join(TemperatureModel).order_by(PrintJobModel.printStartDateTime.desc())
		# allDict = all.dicts()
		# result = prefetch(allJobsQuery, FilamentModel)
		# return result
		# return allDict

	def loadPrintJob(self, databaseId):
		return PrintJobModel.get_by_id(databaseId)

	def deletePrintJob(self, databaseId):


		with self._database.atomic() as transaction:  # Opens new transaction.
			try:
				# first delete relations
				n = FilamentModel.delete().where(FilamentModel.printJob == databaseId).execute()
				n = TemperatureModel.delete().where(TemperatureModel.printJob == databaseId).execute()

				PrintJobModel.delete_by_id(databaseId)
			except Exception as e:
				# Because this block of code is wrapped with "atomic", a
				# new transaction will begin automatically after the call
				# to rollback().
				transaction.rollback()
				# 	TODO do something usefull
				print('DELETE FAILED: ' + str(e))
			pass


