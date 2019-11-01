# coding=utf-8
from __future__ import absolute_import

import os
import sqlite3

from peewee import *
from octoprint_PrintJobHistory.models.FilamentModel import FilamentModel
from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from peewee import BackrefAccessor

from .entities.PrintJobEntity import PrintJobEntity
from .entities.FilamentEntity import FilamentEntity
from .entities.TemperatureEntity import TemperatureEntity
from .entities.PluginMetaDataEntity import PluginMetaDataEntity

from datetime import datetime

FORCE_CREATE_TABLES = True

CURRENT_DATABASE_SCHEME_VERSION = 1
MODELS = [PrintJobModel, FilamentModel]

class DatabaseManager(object):

	def __init__(self):
		self._databasePath = None
		self._database = None


	def savePrintJob(self):

		with self._database.atomic() as transaction:  # Opens new transaction.
			pj = None
			try:
				pj = PrintJobModel()
				pj.fileName = "MyFilename"
				printJobId = pj.save()
				f = pj.getFilament()

				fil1 = FilamentModel()
				fil1.spoolName = "mySpoolName1"
				fil1.printJob = pj
				f = pj.getFilament()
				fil1.save()
				f = pj.getFilament()
				fil2 = FilamentModel()
				fil2.spoolName = "mySpoolName2"
				fil2.printJob = pj
				fil2.save()
				f = pj.getFilament()
			except:
				# Because this block of code is wrapped with "atomic", a
				# new transaction will begin automatically after the call
				# to rollback().
				transaction.rollback()
				error_saving = True
			f = pj.getFilament()

			pass
		pass
	################################################################################################## NEW STUFFFF

	def initDatabase(self, databasePath):

		databasePath = os.path.join(databasePath, "printJobHistory.db")

		self._database = SqliteDatabase(databasePath)
		DatabaseManager.db = self._database
		self._database.bind(MODELS)


		# check, if we need an scheme upgrade
		# self._createOrUpgradeSchemeIfNecessary(cursor)


		if FORCE_CREATE_TABLES:
			self._database.connect()
			self._database.drop_tables(MODELS)
			self._database.create_tables(MODELS)
			self._database.close()

		self.savePrintJob()





		for i in PrintJobModel.select():
			allF = i.filaments
			for f in allF:
				name = f.spoolName
				pass
			pass



		pass




	################################################################################################## private functions

	def _createCurrentTables(self, cursor, dropTables):
		if dropTables == True:
			sql = PluginMetaDataEntity.dropTableSQL()
			cursor.executescript(sql)
			sql = FilamentEntity.dropTableSQL()
			cursor.executescript(sql)
			sql = TemperatureEntity.dropTableSQL()
			cursor.executescript(sql)
			sql = PrintJobEntity.dropTableSQL()
			cursor.executescript(sql)

		# create all Tables
		sql = PluginMetaDataEntity.createTableSQLScript()
		cursor.executescript(sql)

		sql = PrintJobEntity.createTableSQL()
		cursor.execute(sql)

		sql = FilamentEntity.createTableSQLScript()
		cursor.executescript(sql)

		sql = TemperatureEntity.createTableSQLScript()
		cursor.executescript(sql)

		# TODO ...all other tables as well

	def _createOrUpgradeSchemeIfNecessary(self, cursor):
		databaseSchemeVersion = PluginMetaDataEntity.getDatabaseSchemeVersion(cursor)
		if databaseSchemeVersion == None or FORCE_CREATE_TABLES == True:
			self._createCurrentTables(cursor, FORCE_CREATE_TABLES)
		else:
			# check from which version we need to upgrade
			#	sql
			pass

	def _createConnection(self):
		return sqlite3.connect(self._databasePath,
								detect_types = sqlite3.PARSE_DECLTYPES |
					   			sqlite3.PARSE_COLNAMES)

	################################################################################################### public functions

	# datapasePath '/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/prinJobHistory.db'
	def initDatabase_old(self, databasePath):
		self._databasePath = databasePath

		# TODO ExceptionHandling
		connection = self._createConnection()
		cursor = connection.cursor()

		# check, if we need an scheme upgrade
		self._createOrUpgradeSchemeIfNecessary(cursor)

		cursor.close()
		connection.commit()
		connection.close()

	def insertNewPrintJob(self, printJobEntity):
		connection = self._createConnection()
		cursor = connection.cursor()

		printJobEntity.insertOrUpdate(cursor)

		# store assoziations
		if printJobEntity.filamentEntity != None:
			printJobEntity.filamentEntity.printjob_id = printJobEntity.databaseId
			# simple, delete old one and insert new filament entity
			FilamentEntity.deleteByPrintJob(cursor, printJobEntity.databaseId)
			printJobEntity.filamentEntity.insertOrUpdate(cursor)

		if printJobEntity.temperatureEntities != None and len(printJobEntity.temperatureEntities) != 0:
			for temp in printJobEntity.temperatureEntities:
				temp.printjob_id = printJobEntity.databaseId
				temp.insertOrUpdate(cursor)

		cursor.close()
		connection.commit()
		connection.close()



	def loadAllPrintJobs(self):
		connection = self._createConnection()
		cursor = connection.cursor()

		allPrintJobs = PrintJobEntity.loadAll(cursor)

		cursor.close()
		connection.commit()
		connection.close()

		return allPrintJobs

	def loadPrintJob(self, databaseId):
		connection = self._createConnection()
		cursor = connection.cursor()

		printJobEntity = PrintJobEntity.load(cursor, databaseId)

		cursor.close()
		connection.commit()
		connection.close()

		return printJobEntity

	def deletePrintJob(self, databaseId):
		connection = self._createConnection()
		cursor = connection.cursor()

		PrintJobEntity.delete(cursor, databaseId)
		allPrintJobs = PrintJobEntity.loadAll(cursor)

		cursor.close()
		connection.commit()
		connection.close()

		return allPrintJobs

#data = DatabaseManager()
#data.initDatabase("/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/printJobHistory.db")
#printJob = PrintJobEntity()
