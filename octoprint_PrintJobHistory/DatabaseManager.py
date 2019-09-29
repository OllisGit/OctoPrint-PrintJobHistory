# coding=utf-8
from __future__ import absolute_import

import sqlite3

from .entities.PrintJobEntity import PrintJobEntity
from .entities.FilamentEntity import FilamentEntity
from .entities.PluginMetaDataEntity import PluginMetaDataEntity

from datetime import datetime

FORCE_CREATE_TABLES = True


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
			sql = PrintJobEntity.dropTableSQL()
			cursor.executescript(sql)

		# create all Tables
		sql = PluginMetaDataEntity.createTableSQLScript()
		cursor.executescript(sql)

		sql = PrintJobEntity.createTableSQL()
		cursor.execute(sql)

		sql = FilamentEntity.createTableSQLScript()
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

	################################################################################################### public functions

	# datapasePath '/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/prinJobHistory.db'
	def initDatabase(self, databasePath):
		self._databasePath = databasePath

		# TODO ExceptionHandling
		connnection = sqlite3.connect(databasePath)
		cursor = connnection.cursor()

		# check, if we need an scheme upgrade
		self._createOrUpgradeSchemeIfNecessary(cursor)

		datetime_str = '09/19/18 13:55:26'
		datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')

		p = PrintJobEntity()
		p.userName = "Olaf"
		p.fileName = "3DBenchy.gcode"
		p.filePathName = "/path/3DBenchy.gcode"
		p.fileSize = 123
		p.printStartDateTime = datetime_object
		p.printEndDateTime = datetime_object
		p.printStatusResult = "fail"
		p.printedLayers = "13/1234"

		# p.insertOrUpdate(cursor)
		# newP = p.load(cursor, 2)
		allP = p.loadAll(cursor)

		cursor.close()
		connnection.commit()
		connnection.close()

	def insertNewPrintJob(self, printJobEntity):
		connnection = sqlite3.connect(self._databasePath)
		cursor = connnection.cursor()

		printJobEntity.insertOrUpdate(cursor)

		# store assoziations
		printJobEntity.filamentEntity.printjob_id = printJobEntity.databaseId
		printJobEntity.filamentEntity.insertOrUpdate(cursor)

		cursor.close()
		connnection.commit()
		connnection.close()


#data = DatabaseManager()
#data.initDatabase("/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/printJobHistory.db")
#printJob = PrintJobEntity()
