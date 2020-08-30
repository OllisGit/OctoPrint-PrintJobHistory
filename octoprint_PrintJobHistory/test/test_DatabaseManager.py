import pprint
import unittest

from octoprint_PrintJobHistory import DatabaseManager
from octoprint_PrintJobHistory.api import TransformPrintJob2JSON
from octoprint_PrintJobHistory.common import StringUtils
import logging

class TestDatabase(unittest.TestCase):

	databaselocation = "/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/"

	def setUp(self):
		self.init_database()

	def _clientOutput(message1, message2):
		print(message1)
		print(message2)

	def init_database(self):
		logging.basicConfig(level=logging.DEBUG)
		testLogger = logging.getLogger("testLogger")
		logging.info("Start Database-Test")
		self.databaseManager = DatabaseManager(testLogger, True)
		self.databaseManager.initDatabase(self.databaselocation, self._clientOutput)

	# TimeFrameSelection
	def _test_queryJobs(self):
		tableQuery = {
			"from": 0,
			"to": 10,
			"sortColumn": "filename",
			"sortOrder": "asc",
			"filterName": "all",
			"startDate": "20.08.2020",
			"endDate": "20.08.2020",
		}

		allJobsModels = self.databaseManager.loadPrintJobsByQuery(tableQuery)
		print(allJobsModels)
		allJobsAsList = TransformPrintJob2JSON.transformAllPrintJobModels(allJobsModels)

		pp = pprint.PrettyPrinter(indent=2)
		# pp.pprint(allJobsAsDict)
		for jobItem in allJobsAsList:
			print(str(jobItem["databaseId"]) + "  " + str(jobItem["printStartDateTimeFormatted"]) + "  " + str(jobItem["printEndDateTimeFormatted"]))

		pass


	# Statistic
	def _test_statistics(self):
		tableQuery = {
			"from": 0,
			"to": 100,
			"sortColumn": "filename",
			"sortOrder": "asc",
			"filterName": "all",
			# "startDate": "20.08.2020",
			# "endDate": "20.08.2020",
		}

		stats = self.databaseManager.calculatePrintJobsStatisticByQuery(tableQuery)
		print(stats)
		# allJobsAsList = TransformPrintJob2JSON.transformAllPrintJobModels(allJobsModels)
		#
		# pp = pprint.PrettyPrinter(indent=2)
		# # pp.pprint(allJobsAsDict)
		# for jobItem in allJobsAsList:
		# 	print(str(jobItem["databaseId"]) + "  " + str(jobItem["printStartDateTimeFormatted"]) + "  " + str(jobItem["printEndDateTimeFormatted"]))

		pass

	def test_loadSelected(self):
		selectedDatabaseIds = "17,3,21,23,20"
		allJobsModels = self.databaseManager.loadSelectedPrintJobs(selectedDatabaseIds)
		print(allJobsModels)
		allJobsAsList = TransformPrintJob2JSON.transformAllPrintJobModels(allJobsModels)

		pp = pprint.PrettyPrinter(indent=2)
		# pp.pprint(allJobsAsDict)
		for jobItem in allJobsAsList:
			print(str(jobItem["databaseId"]) + "  " + str(jobItem["printStartDateTimeFormatted"]) + "  " + str(jobItem["printEndDateTimeFormatted"]))

		pass

if __name__ == '__main__':
	print("Start DatabaseManager Test")
	unittest.main()
	print("Finished")

#
# type = "ppostgres"
# host="localhost"
# port="5432"
# databaseName="rainbow_database"
# username = "unicorn_user"
# password = "magical_password"
# result = databaseManager.testConnection(type, host, port, databaseName, username, password)
# print(result)


# printJob = databaseManager.loadPrintJob(1)
# # python2 -> unicode
# # python3 -> str (es gibt kein unicode)
# fileName = printJob.fileName
# convert(fileName)
# fileSize = printJob.fileSize
# convert(fileSize)
# printStartDateTime = printJob.printStartDateTime
# convert(printStartDateTime)
# diameter = printJob.loadFilamentFromAssoziation().diameter
# convert(diameter)

# currentScheme = 1
# targetScheme = 5
#
# databaseManager._upgradeDatabase(currentScheme, targetScheme)
