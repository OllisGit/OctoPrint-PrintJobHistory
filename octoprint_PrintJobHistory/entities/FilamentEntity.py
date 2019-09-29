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
COLUMN_SPOOL_WEIGHT = "spoolWeight"

COLUMN_USED_LENGTH = "usedLength"

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
		self.spoolWeight = None

		self.usedLength = None

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
			   + COLUMN_SPOOL_WEIGHT + " TEXT, " \
			   + COLUMN_USED_LENGTH + " REAL, " \
			   + "FOREIGN KEY(" + COLUMN_PRINTJOB_ID + ") REFERENCES printJobEntity(" + COLUMN_DATABASE_ID + ") " \
			   + "); "

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
			  + COLUMN_SPOOL_WEIGHT + ", " \
			  + COLUMN_USED_LENGTH + " " \
			 ") " \
			  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
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
							 self.spoolWeight,
							 self.usedLength,
							 ))

		if self.databaseId == None:
			self.databaseId = cursor.lastrowid
