# coding=utf-8
from __future__ import absolute_import

import logging
import os
import sqlite3

from octoprint_PrintJobHistory.WrappedLoggingHandler import WrappedLoggingHandler
from octoprint_PrintJobHistory.models.FilamentModel import FilamentModel
from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from octoprint_PrintJobHistory.models.PluginMetaDataModel import PluginMetaDataModel
from octoprint_PrintJobHistory.models.TemperatureModel import TemperatureModel
from peewee import *


FORCE_CREATE_TABLES = False
SQL_LOGGING = True

CURRENT_DATABASE_SCHEME_VERSION = 1

# List all Models
MODELS = [PluginMetaDataModel, PrintJobModel, FilamentModel, TemperatureModel]


class DatabaseManager(object):

	def __init__(self, parentLogger):
		self._logger = logging.getLogger(parentLogger.name + "." + self.__class__.__name__)
		self._sqlLogger = logging.getLogger(parentLogger.name + "." + self.__class__.__name__ + ".SQL")

		self._database = None
		self._databaseFileLocation = None
		self._sendDataToClient = None

	################################################################################################## private functions

	def _createOrUpgradeSchemeIfNecessary(self):
		schemeVersionFromDatabaseModel = None
		try:
			schemeVersionFromDatabaseModel = PluginMetaDataModel.get(PluginMetaDataModel.key == PluginMetaDataModel.KEY_DATABASE_SCHEME_VERSION)
			pass
		except Exception as e:
			errorMessage = e.message
			if errorMessage.startswith("no such table"):

				self._logger.info("Create database-table, because didn't exists")
				self._createDatabaseTables()
			else:
				self._logger.error(str(e))

		if not schemeVersionFromDatabaseModel == None:
			currentDatabaseSchemeVersion = int(schemeVersionFromDatabaseModel.value)
			if (currentDatabaseSchemeVersion < CURRENT_DATABASE_SCHEME_VERSION):
				# evautate upgrade steps (from 1-2 , 1...6)
				self._logger.info("We need to upgrade the database scheme from: '" + str(currentDatabaseSchemeVersion) + "' to: '" + str(CURRENT_DATABASE_SCHEME_VERSION) + "'")
				self._logger.info("...not needed/implemented...")
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
		self._logger.info("Database tables created")

	################################################################################################### public functions
	# datapasePath '/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory'
	def initDatabase(self, databasePath, sendErrorMessageToClient):
		self._logger.info("Init DatabaseManager")
		self.sendErrorMessageToClient = sendErrorMessageToClient
		self._databaseFileLocation = os.path.join(databasePath, "printJobHistory.db")

		self._logger.info("Creating database in: " + str(self._databaseFileLocation))
		if SQL_LOGGING == True:
			import logging
			logger = logging.getLogger('peewee')
			# we need only the single logger without parent
			logger.parent = None
			# logger.addHandler(logging.StreamHandler())
			# activate SQL logging on PEEWEE side and on PLUGIN side
			logger.setLevel(logging.DEBUG)
			self._sqlLogger.setLevel(logging.DEBUG)

			wrappedHandler = WrappedLoggingHandler(self._sqlLogger)
			logger.addHandler(wrappedHandler)


		self._database = SqliteDatabase(self._databaseFileLocation)
		DatabaseManager.db = self._database
		self._database.bind(MODELS)

		if FORCE_CREATE_TABLES:
			self._logger.info("Creating new database-tables, because FORCE == TRUE!")
			self._createDatabaseTables()
		else:
			# check, if we need an scheme upgrade
			self._logger.info("Check if database-scheme upgrade needed.")
			self._createOrUpgradeSchemeIfNecessary()
		self._logger.info("Done DatabaseManager")
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
				self._logger.exception("Could not insert printJob into database:" + str(e))

				self.sendErrorMessageToClient("DatabaseManager", "Could not insert the printjob into the database. See OctoPrint.log for details!")
			pass

		return databaseId

	def updatePrintJob(self, printJobModel):
		with self._database.atomic() as transaction:  # Opens new transaction.
			try:
				printJobModel.save()
				databaseId = printJobModel.get_id()
				# save all relations
				# - Filament
				for filamentModel in printJobModel.getFilamentModels():
					filamentModel.save()

				# # - Temperature
				# for temperatureModel in printJobModel.getTemperatureModels():
				# 	temperatureModel.printJob = printJobModel
				# 	temperatureModel.save()
			except Exception as e:
				# Because this block of code is wrapped with "atomic", a
				# new transaction will begin automatically after the call
				# to rollback().
				transaction.rollback()
				self._logger.exception("Could not update printJob into database:" + str(e))
				self.sendErrorMessageToClient("DatabaseManager", "Could not update the printjob ('"+ printJobModel.fileName +"') into the database. See OctoPrint.log for details!")
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
				self._logger.exception("Could not delete printJob from database:" + str(e))

				self.sendErrorMessageToClient("DatabaseManager", "Could not update the printjob ('"+ str(databaseId) +"') into the database. See OctoPrint.log for details!")
			pass
