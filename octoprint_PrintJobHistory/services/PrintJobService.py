# coding=utf-8
from __future__ import absolute_import

# from octoprint_PrintJobHistory import PrintJobModel
from octoprint_PrintJobHistory.models.FilamentModel import FilamentModel
from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel


class PrintJobService(object):

	def __init__(self, databaseManager):
		self.databaseManager = databaseManager
		pass

	def createWithDefaults(self):
		newPrintJobModel = PrintJobModel()
		totalFilament = FilamentModel()
		totalFilament.toolId = "total"
		newPrintJobModel.addFilamentModel(totalFilament)
		return newPrintJobModel


	def savePrintJob(self, printJobModel):
		if (printJobModel.databaseId == None):
			return self.databaseManager.insertPrintJob(printJobModel)
		else:
			return self.databaseManager.updatePrintJob(printJobModel)

	def loadPrintJob(self, databaseId):
		if (databaseId == None):
			return None
		printJobModel = self.databaseManager.loadPrintJob(databaseId)
		return printJobModel
