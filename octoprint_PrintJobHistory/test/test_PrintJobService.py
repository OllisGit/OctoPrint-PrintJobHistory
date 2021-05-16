import unittest

from octoprint_PrintJobHistory.common import StringUtils, DateTimeUtils
from octoprint_PrintJobHistory.services.PrintJobService import PrintJobService
import logging
from octoprint_PrintJobHistory import DatabaseManager, FilamentModel, TemperatureModel


class PrintJobServiceTestCase(unittest.TestCase):
	databaselocation = "/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/"

	def setUp(self):
		self.init_database()
		self.printJobService = PrintJobService(self.databaseManager)
		self.rollBackPrintJobs = []


	def _clientOutput(message1, message2):
		print(message1)
		print(message2)

	def init_database(self):
		logging.basicConfig(level=logging.DEBUG)
		testLogger = logging.getLogger("testLogger")
		logging.info("Start Database-Test")
		self.databaseManager = DatabaseManager(testLogger, True)
		self.databaseManager.initDatabase(self.databaselocation, self._clientOutput)



	def test_createPrintJob(self):
		self.databaseManager.deletePrintJob(1011)

		newPrintJob = self.printJobService.createWithDefaults()
		# check
		# - databaseId
		# - filament total
		self.assertEqual(newPrintJob.databaseId, None, "Model already persistence!")
		totalFilament = newPrintJob.getFilamentModelByToolId("total")
		self.assertEqual(totalFilament.toolId, "total")

		# create data
		newPrintJob.userName = "Olli"
		newPrintJob.fileOrigin = "local"
		newPrintJob.fileName = "OllisBenchy.gcode"
		newPrintJob.filePathName = "archive/OllisBenchy.gcode"
		newPrintJob.fileSize = 1234
		newPrintJob.printStartDateTime = StringUtils.transformToDateTimeOrNone("12.03.2013 14:45")
		newPrintJob.printEndDateTime = StringUtils.transformToDateTimeOrNone("12.03.2013 16:45")
		newPrintJob.duration = DateTimeUtils.calcDurationInSeconds(newPrintJob.printEndDateTime, newPrintJob.printStartDateTime)
		newPrintJob.printStatusResult = "failed"
		newPrintJob.noteText = "Hello World"
		newPrintJob.noteDeltaFormat = "Something"
		newPrintJob.noteHtml = "<p>Hello World</p>"
		newPrintJob.printedLayers = "10 / 133"
		newPrintJob.printedHeight = "1.3 / 143.3"
		newPrintJob.slicerSettingsAsText = "dummy slicer settings"

		newFilamentModel = FilamentModel()
		newFilamentModel.toolId = "tool0"
		newPrintJob.addFilamentModel(newFilamentModel)

		newTemperatureModel = TemperatureModel()
		newTemperatureModel.sensorName = "tool0"
		newTemperatureModel.sensorValue = "123C"
		newPrintJob.addTemperatureModel(newTemperatureModel)

		# store
		self.printJobService.savePrintJob(newPrintJob)
		databaseId = newPrintJob.databaseId
		self.rollBackPrintJobs.append(databaseId)

		# load again and check if everything is in
		loadedPrintJobModel = self.printJobService.loadPrintJob(databaseId)
		self.assertEqual(loadedPrintJobModel.databaseId, newPrintJob.databaseId)
		self.assertEqual(loadedPrintJobModel.userName, newPrintJob.userName)
		self.assertEqual(loadedPrintJobModel.fileOrigin, newPrintJob.fileOrigin)
		self.assertEqual(loadedPrintJobModel.fileName, newPrintJob.fileName)
		self.assertEqual(loadedPrintJobModel.filePathName, newPrintJob.filePathName)
		self.assertEqual(loadedPrintJobModel.fileSize, newPrintJob.fileSize)
		self.assertEqual(loadedPrintJobModel.printStartDateTime, newPrintJob.printStartDateTime)
		self.assertEqual(loadedPrintJobModel.printEndDateTime, newPrintJob.printEndDateTime)
		self.assertEqual(loadedPrintJobModel.duration, newPrintJob.duration)
		self.assertEqual(loadedPrintJobModel.printStatusResult, newPrintJob.printStatusResult)
		self.assertEqual(loadedPrintJobModel.noteText, newPrintJob.noteText)
		self.assertEqual(loadedPrintJobModel.noteDeltaFormat, newPrintJob.noteDeltaFormat)
		self.assertEqual(loadedPrintJobModel.noteHtml, newPrintJob.noteHtml)
		self.assertEqual(loadedPrintJobModel.printedLayers, newPrintJob.printedLayers)
		self.assertEqual(loadedPrintJobModel.slicerSettingsAsText, newPrintJob.slicerSettingsAsText)
		# check-assos
		# - allFilaments
		allFilamentModels = loadedPrintJobModel.getFilamentModels()
		self.assertEqual(len(allFilamentModels), 2, "'total' and 'tool0' filamentModel expected")
		# - allTemperatures
		allTemperatureModels = loadedPrintJobModel.getTemperatureModels()
		self.assertEqual(len(allTemperatureModels), 1, "temperatureModels expected")

		#  - allTemperatures



		# do test-cleanup
		for printJobDatabaseId in self.rollBackPrintJobs:
			self.databaseManager.deletePrintJob(printJobDatabaseId)



if __name__ == '__main__':
	unittest.main()
	print("TEST FINISHED")
