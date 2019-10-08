# coding=utf-8
from __future__ import absolute_import

TABLE_NAME = "temperatureEntity"
COLUMN_DATABASE_ID = "id"
COLUMN_PRINTJOB_ID = "printjob_id"

# could be bed, nozzel0, nozzel1, encloser, whatever
COLUMN_SENSOR_NAME = "sensorName"
COLUMN_SENSOR_VALUE = "sensorValue"

class TemperatureEntity(object):

	def __init__(self):
		self.databaseId = None
		self.printjob_id = None

		self.sensorName = None
		self.sensorValue = None

	########################################################################################### private static functions

	@staticmethod
	def _createItemFromRow(row):
		result = None
		if row != None:
			result = TemperatureEntity()
			result.databaseId = row[0]
			result.printjob_id = row[1]
			result.sensorName = row[2]
			result.sensorValue = row[3]
		return result

	################################################################################################### static functions

	@staticmethod
	def dropTableSQL():
		return "DROP TABLE IF EXISTS " + TABLE_NAME

	@staticmethod
	def createTableSQLScript():
		return "" \
			   "CREATE TABLE IF NOT EXISTS " + TABLE_NAME + " (" \
			   + COLUMN_DATABASE_ID + " INTEGER PRIMARY KEY AUTOINCREMENT, " \
			   + COLUMN_PRINTJOB_ID + " INTEGER NOT NULL, " \
			   + COLUMN_SENSOR_NAME + " TEXT, " \
			   + COLUMN_SENSOR_VALUE + " REAL, " \
			   + "FOREIGN KEY(" + COLUMN_PRINTJOB_ID + ") REFERENCES printJobEntity(" + COLUMN_DATABASE_ID + ") " \
			   + "); "

	@staticmethod
	def loadByPrintJob(cursor, databaseId):
		cursor.execute("SELECT * FROM " + TABLE_NAME + " where " + COLUMN_PRINTJOB_ID + " = ?", (str(databaseId)))

		result = []
		rows = cursor.fetchall()
		for row in rows:
			tempEntity = TemperatureEntity._createItemFromRow(row)
			result.append(tempEntity)
		return result

	################################################################################################## private functions
	def _createInsertSQL(self):
		sql = "INSERT INTO " + TABLE_NAME + " (" \
			  + COLUMN_PRINTJOB_ID + ", " \
			  + COLUMN_SENSOR_NAME + ", "\
			  + COLUMN_SENSOR_VALUE + " " \
			 ") " \
			  "VALUES (?, ?, ?)"
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
		cursor.execute(sql, (self.printjob_id,
							 self.sensorName,
							 self.sensorValue,
							 ))

		if self.databaseId == None:
			self.databaseId = cursor.lastrowid
