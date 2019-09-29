# coding=utf-8
from __future__ import absolute_import

DATABASE_SCHEME_VERSION = 1

TABLE_NAME = "pluginMetaDataEntity"
COLUMN_DATABASE_ID = "id"
COLUMN_SCHEMEVERSION = "schemeVersion"

class PluginMetaDataEntity(object):

	def __init__(self):
		self.databaseId = None
		self.pluginDatavaseSchemeVersion = None

	@staticmethod
	def dropTableSQL():
		return "DROP TABLE IF EXISTS " + TABLE_NAME

	@staticmethod
	def createTableSQLScript():
		return "" \
			   "CREATE TABLE IF NOT EXISTS " + TABLE_NAME + " (" \
			   + COLUMN_DATABASE_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " \
			   + COLUMN_SCHEMEVERSION + " INTEGER NOT NULL DEFAULT \"" + str(DATABASE_SCHEME_VERSION) + "\"" \
			   + "); " \
			  +"INSERT INTO " + TABLE_NAME + " (" + COLUMN_SCHEMEVERSION + ") VALUES (" + str(DATABASE_SCHEME_VERSION) + ")"

	@staticmethod
	def getDatabaseSchemeVersion(cursor):
		currentVersion = None
		sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + TABLE_NAME + "';"
		cursor.execute(sql)
		row = cursor.fetchone()
		if row != None:
			sql = "SELECT " + COLUMN_SCHEMEVERSION + " FROM " + TABLE_NAME + ";"
			cursor.execute(sql)
			row = cursor.fetchone()
			currentVersion = row[0]
		return currentVersion

	@staticmethod
	def getCurrentDatabaseSchemeVersion():
		return DATABASE_SCHEME_VERSION

