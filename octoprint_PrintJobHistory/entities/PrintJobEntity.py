# coding=utf-8
from __future__ import absolute_import

TABLE_NAME = "printJobEntity"
COLUMN_DATABASE_ID = "id"
COLUMN_USERNAME = "userName"
COLUMN_FILE_NAME = "fileName"
COLUMN_FILE_PATHNAME = "filePathName"
COLUMN_FILE_SIZE = "fileSize"
COLUMN_PRINT_START_DATETIME = "printStartDateTime"
COLUMN_PRINT_END_DATETIME = "printEndDateTime"
COLUMN_PRINT_STATUS_RESULT = "printStatusResult"
COLUMN_NOTE = "note"
COLUMN_PRINTED_LAYERS = "printedLayers"
COLUMN_TEMPERATURE_BED = "temperatureBed"
COLUMN_TEMPERATURE_NOZZEL = "temperatureNozzel"


class PrintJobEntity(object):

	def __init__(self):
		self.databaseId = None
		self.userName = None
		self.fileName = None
		self.filePathName = None
		self.fileSize = None
		self.printStartDateTime = None
		self.printEndDateTime = None
		self.printStatusResult = None
		self.note = None
		self.printedLayers = None
		self.temperatureBed = None
		self.temperatureNozzel = None

		self.filamentEntity = None




	########################################################################################### private static functions
	@staticmethod
	def _createItemFromRow(row):
		result = None
		if row != None:
			result = PrintJobEntity()
			result.databaseId = row[0]
			result.fileName = row[1]
			result.fileNamePath = row[2]
			result.fileSize = row[3]
			result.printStartDateTime = row[4]
			result.printEndDateTime = row[5]
			result.printStatusResult = row[6]
			result.note = row[7]
			result.printedLayers = row[8]
			result.temperatureBed = row[9]
			result.temperatureNozzel = row[10]
		return result

	################################################################################################### static functions
	@staticmethod
	def dropTableSQL():
		return "DROP TABLE IF EXISTS " + TABLE_NAME

	@staticmethod
	def createTableSQL():
		return "" \
			   "CREATE TABLE IF NOT EXISTS " + TABLE_NAME + " (" \
			   + COLUMN_DATABASE_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " \
			   + COLUMN_USERNAME + " TEXT NOT NULL DEFAULT \"\", " \
			   + COLUMN_FILE_NAME + " TEXT NOT NULL DEFAULT \"\", " \
			   + COLUMN_FILE_PATHNAME + " TEXT NOT NULL DEFAULT \"\", " \
			   + COLUMN_FILE_SIZE + " INTEGER NOT NULL DEFAULT \"0\", " \
			   + COLUMN_PRINT_START_DATETIME + " DATETIME NOT NULL, " \
			   + COLUMN_PRINT_END_DATETIME + " DATETIME NOT NULL, " \
			   + COLUMN_PRINT_STATUS_RESULT + " TEXT NOT NULL, " \
			   + COLUMN_NOTE + " TEXT," \
			   + COLUMN_PRINTED_LAYERS + " TEXT, " \
			   + COLUMN_TEMPERATURE_BED + " INTEGER, " \
			   + COLUMN_TEMPERATURE_NOZZEL + " INTEGER " \
			 ");"

	@staticmethod
	def loadAll(cursor):
		result = []
		cursor.execute("SELECT * FROM " + TABLE_NAME + "")
		result_set = cursor.fetchall()
		for row in result_set:
			item = PrintJobEntity._createItemFromRow(row)
			result.append(item)
		return result

	@staticmethod
	def load(cursor, databaseId):

		cursor.execute("SELECT * FROM " + TABLE_NAME + " where id = ?", (str(databaseId)))
		row = cursor.fetchone()
		result = PrintJobEntity._createItemFromRow(row)

		return result

	################################################################################################## private functions
	def _createInsertSQL(self):
		sql = "INSERT INTO " + TABLE_NAME + " (" \
			  + COLUMN_USERNAME + ", " \
			  + COLUMN_FILE_NAME + ", " \
			  + COLUMN_FILE_PATHNAME + ", "\
			  + COLUMN_FILE_SIZE + ", " \
			  + COLUMN_PRINT_START_DATETIME + ", " \
			  + COLUMN_PRINT_END_DATETIME + ", " \
			  + COLUMN_PRINT_STATUS_RESULT + ", " \
			  + COLUMN_NOTE + ", " \
			  + COLUMN_PRINTED_LAYERS + ", " \
			  + COLUMN_TEMPERATURE_BED + ", " \
			  + COLUMN_TEMPERATURE_NOZZEL + " " \
			  ") " \
			  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
		return sql

	# TODO
	def _createUpdateSQL(self):
		sql = "UPDATE " + TABLE_NAME + " SET key= ?"
		return sql


	################################################################################################### public functions

	def insertOrUpdate(self, cursor):
		sql = ""

		if self.databaseId == None:
			sql = self._createInsertSQL()
		else:
			sql = self._createUpdateSQL()
		print(sql)
		cursor.execute(sql, (self.userName,
							 self.fileName,
							 self.filePathName,
							 self.fileSize,
							 self.printStartDateTime,
							 self.printEndDateTime,
							 self.printStatusResult,
							 self.note,
							 self.printedLayers,
							 self.temperatureBed,
							 self.temperatureNozzel
							 ))

		if self.databaseId == None:
			self.databaseId = cursor.lastrowid

