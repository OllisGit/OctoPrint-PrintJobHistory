# coding=utf-8
from __future__ import absolute_import

import sqlite3

from .entities.PrintJobEntity import PrintJobEntity
from .entities.FilamentEntity import FilamentEntity
from .entities.TemperatureEntity import TemperatureEntity
from .entities.PluginMetaDataEntity import PluginMetaDataEntity

from datetime import datetime

FORCE_CREATE_TABLES = False


class DatabaseManager(object):

	def __init__(self):
		self._databasePath = None

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
	def initDatabase(self, databasePath):
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
