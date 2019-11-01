# coding=utf-8
from __future__ import absolute_import

TABLE_NAME = "filamentEntity"
COLUMN_DATABASE_ID = "id"
COLUMN_PRINTJOB_ID = "printjob_id"

COLUMN_PROFILE_VENDOR = "profileVendor"
COLUMN_DIAMETER = "diameter"
COLUMN_DENSITY = "density"
COLUMN_MATERIAL = "material"

COLUMN_SPOOL_NAME = "spoolName"
COLUMN_SPOOL_COST = "spoolCost"
COLUMN_SPOOL_COST_UNIT = "spoolCostUnit"
COLUMN_SPOOL_WEIGHT = "spoolWeight"

COLUMN_USED_LENGTH = "usedLength"
COLUMN_CALCULATED_LENGTH = "calculatedLength"

COLUMN_USED_WEIGHT = "usedWeight"
COLUMN_USED_COST = "usedCost"


class FilamentEntity(object):

	def __init__(self):
		self.databaseId = None
		self.printjob_id = None
		self.profileVendor = None
		self.diameter = None
		self.density = None
		self.material = None

		self.spoolName = None
		self.spoolCost = None
		self.spoolCostUnit = None
		self.spoolWeight = None

		self.usedLength = None
		self.calculatedLength = None

		self.usedWeight = None
		self.usedCost = None



	########################################################################################### private static functions

	@staticmethod
	def _createItemFromRow(row):
		result = None
		if row != None:
			result = FilamentEntity()
			result.databaseId = row[0]
			result.printjob_id = row[1]
			result.profileVendor = row[2]
			result.diameter = row[3]
			result.density = row[4]
			result.material = row[5]
			result.spoolName = row[6]
			result.spoolCost = row[7]
			result.spoolCostUnit = row[8]
			result.spoolWeight = row[9]
			result.usedLength = row[10]
			result.calculatedLength = row[11]
			result.usedWeight = row[12]
			result.usedCost = row[13]
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
			   + COLUMN_PROFILE_VENDOR + " TEXT, " \
			   + COLUMN_DIAMETER + " REAL, " \
			   + COLUMN_DENSITY + " REAL, " \
			   + COLUMN_MATERIAL + " TEXT, " \
			   + COLUMN_SPOOL_NAME + " TEXT, " \
			   + COLUMN_SPOOL_COST + " TEXT, " \
			   + COLUMN_SPOOL_COST_UNIT + " TEXT, " \
			   + COLUMN_SPOOL_WEIGHT + " TEXT, " \
			   + COLUMN_USED_LENGTH + " REAL, " \
			   + COLUMN_CALCULATED_LENGTH + " REAL, " \
			   + COLUMN_USED_WEIGHT + " REAL, " \
			   + COLUMN_USED_COST + " REAL, " \
			   + "FOREIGN KEY(" + COLUMN_PRINTJOB_ID + ") REFERENCES printJobEntity(" + COLUMN_DATABASE_ID + ") " \
			   + "); "

	@staticmethod
	def loadByPrintJob(cursor, databaseId):
		cursor.execute("SELECT * FROM " + TABLE_NAME + " where " + COLUMN_PRINTJOB_ID + " = ?", (str(databaseId)))
		row = cursor.fetchone()
		result = FilamentEntity._createItemFromRow(row)

		return result	\

	@staticmethod
	def deleteByPrintJob(cursor, databaseId):
		cursor.execute("DELETE FROM " + TABLE_NAME + " where " + COLUMN_PRINTJOB_ID + " = ?", str(databaseId))
		row = cursor.fetchone()
		pass

	################################################################################################## private functions
	def _createInsertSQL(self):
		sql = "INSERT INTO " + TABLE_NAME + " (" \
			  + COLUMN_PRINTJOB_ID + ", " \
			  + COLUMN_PROFILE_VENDOR + ", "\
			  + COLUMN_DIAMETER + ", " \
			  + COLUMN_DENSITY + ", " \
			  + COLUMN_MATERIAL + ", " \
			  + COLUMN_SPOOL_NAME + ", " \
			  + COLUMN_SPOOL_COST + ", " \
			  + COLUMN_SPOOL_COST_UNIT + ", " \
			  + COLUMN_SPOOL_WEIGHT + ", " \
			  + COLUMN_USED_LENGTH + ", " \
			  + COLUMN_CALCULATED_LENGTH + ", " \
			  + COLUMN_USED_WEIGHT + ", " \
			  + COLUMN_USED_COST + " " \
			 ") " \
			  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
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
							 self.profileVendor,
							 self.diameter,
							 self.density,
							 self.material,
							 self.spoolName,
							 self.spoolCost,
							 self.spoolCostUnit,
							 self.spoolWeight,
							 self.usedLength,
							 self.calculatedLength,
							 self.usedWeight,
							 self.usedCost
							 ))

		if self.databaseId == None:
			self.databaseId = cursor.lastrowid
