# coding=utf-8
from __future__ import absolute_import

from .FilamentEntity import FilamentEntity
from .TemperatureEntity import TemperatureEntity

TABLE_NAME = "printJobEntity"
COLUMN_DATABASE_ID = "id"
COLUMN_USERNAME = "userName"
COLUMN_FILE_NAME = "fileName"
COLUMN_FILE_PATHNAME = "filePathName"
COLUMN_FILE_SIZE = "fileSize"
COLUMN_PRINT_START_DATETIME = "printStartDateTime"
COLUMN_PRINT_END_DATETIME = "printEndDateTime"
COLUMN_PRINT_STATUS_RESULT = "printStatusResult"
COLUMN_NOTE_TEXT = "noteText"
COLUMN_NOTE_DELTA = "noteDelta"
COLUMN_NOTE_HTML = "noteHTML"
COLUMN_PRINTED_LAYERS = "printedLayers"
COLUMN_PRINTED_HEIGHT = "printedHeight"


class PrintJobEntity():

	def __init__(self):
		self.databaseId = None
		self.userName = None
		self.fileName = None
		self.filePathName = None
		self.fileSize = None
		self.printStartDateTime = None
		self.printEndDateTime = None
		self.printStatusResult = None
		self.noteText = None
		self.noteDelta = None
		self.noteHtml = None
		self.printedLayers = None
		self.printedHeight = None

		self.filamentEntity = None
		self.temperatureEntities = []	#array

	########################################################################################### private static functions
	@staticmethod
	def _createItemFromRow(row):
		result = None
		if row != None:
			result = PrintJobEntity()
			result.databaseId = row[0]
			result.userName = row[1]
			result.fileName = row[2]
			result.fileNamePath = row[3]
			result.fileSize = row[4]
			result.printStartDateTime = row[5]
			result.printEndDateTime = row[6]
			result.printStatusResult = row[7]
			result.noteText = row[8]
			result.noteDelta = row[9]
			result.noteHtml = row[10]
			result.printedLayers = row[11]
			result.printedHeight = row[12]
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
			   + COLUMN_FILE_PATHNAME + " TEXT DEFAULT \"\", " \
			   + COLUMN_FILE_SIZE + " INTEGER NOT NULL DEFAULT \"0\", " \
			   + COLUMN_PRINT_START_DATETIME + " timestamp NOT NULL, " \
			   + COLUMN_PRINT_END_DATETIME + " timestamp NOT NULL, " \
			   + COLUMN_PRINT_STATUS_RESULT + " TEXT NOT NULL, " \
			   + COLUMN_NOTE_TEXT + " TEXT," \
			   + COLUMN_NOTE_DELTA + " TEXT," \
			   + COLUMN_NOTE_HTML + " TEXT," \
			   + COLUMN_PRINTED_LAYERS + " TEXT, " \
			   + COLUMN_PRINTED_HEIGHT + " TEXT " \
			 ");"

	@staticmethod
	def loadAll(cursor):
		result = []
		cursor.execute("SELECT * FROM " + TABLE_NAME + "")
		result_set = cursor.fetchall()
		for row in result_set:
			job = PrintJobEntity._createItemFromRow(row)
			# load all assos
			filamentEntity = FilamentEntity.loadByPrintJob(cursor, job.databaseId)
			job.filamentEntity = filamentEntity

			tempEntities = TemperatureEntity.loadByPrintJob(cursor, job.databaseId)
			job.temperatureEntities = tempEntities

			# - TODO
			result.append(job)
		return result

	@staticmethod
	def load(cursor, databaseId):

		cursor.execute("SELECT * FROM " + TABLE_NAME + " where id = ?", (str(databaseId)))
		row = cursor.fetchone()
		result = PrintJobEntity._createItemFromRow(row)

		return result

	@staticmethod
	def delete(cursor, databaseId):

		cursor.execute("DELETE FROM " + TABLE_NAME + " WHERE id = ?", (str(databaseId)))
		row = cursor.fetchone()
		pass

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
			  + COLUMN_NOTE_TEXT + ", " \
			  + COLUMN_NOTE_DELTA + ", " \
			  + COLUMN_NOTE_HTML + ", " \
			  + COLUMN_PRINTED_LAYERS + ", " \
			  + COLUMN_PRINTED_HEIGHT + " " \
			  ") " \
			  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
		return sql

	def _createUpdateSQL(self, databaseId):
		sql = "UPDATE " + TABLE_NAME + " SET " \
									 + COLUMN_USERNAME + " = ?," \
									 + COLUMN_FILE_NAME + " = ?," \
									 + COLUMN_FILE_PATHNAME + " = ?," \
									 + COLUMN_FILE_SIZE + " = ?," \
									 + COLUMN_PRINT_START_DATETIME + " = ?," \
									 + COLUMN_PRINT_END_DATETIME + " = ?," \
									 + COLUMN_PRINT_STATUS_RESULT + " = ?," \
									 + COLUMN_NOTE_TEXT + " = ?," \
									 + COLUMN_NOTE_DELTA + " = ?," \
									 + COLUMN_NOTE_HTML + " = ?," \
									 + COLUMN_PRINTED_LAYERS + " = ?," \
									 + COLUMN_PRINTED_HEIGHT + " = ? " \
								   	 + "WHERE " + COLUMN_DATABASE_ID + " = " + str(databaseId)
		return sql


	################################################################################################### public functions

	def insertOrUpdate(self, cursor):
		sql = ""

		if self.databaseId == None:
			sql = self._createInsertSQL()
		else:
			sql = self._createUpdateSQL(self.databaseId)
		print(sql)
		cursor.execute(sql, (self.userName,
							 self.fileName,
							 self.filePathName,
							 self.fileSize,
							 self.printStartDateTime,
							 self.printEndDateTime,
							 self.printStatusResult,
							 self.noteText,
							 self.noteDelta,
							 self.noteHtml,
							 self.printedLayers,
							 self.printedHeight
							 ))

		if self.databaseId == None:
			self.databaseId = cursor.lastrowid

		return self.databaseId
