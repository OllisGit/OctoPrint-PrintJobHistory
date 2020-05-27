# coding=utf-8
from __future__ import absolute_import

import shutil
import tempfile
import threading

import octoprint.plugin
from flask import jsonify, request, make_response, Response, send_file
import flask

import json

import os

from datetime import datetime
from datetime import timedelta

from werkzeug.datastructures import Headers

from octoprint_PrintJobHistory import PrintJobModel, TemperatureModel, FilamentModel
from octoprint_PrintJobHistory.api import TransformPrintJob2JSON

from octoprint_PrintJobHistory.common.SettingsKeys import SettingsKeys

from octoprint_PrintJobHistory.CameraManager import CameraManager
from octoprint_PrintJobHistory.common import CSVExportImporter

#############################################################
# Internal API for all Frontend communications
#############################################################
class PrintJobHistoryAPI(octoprint.plugin.BlueprintPlugin):


	def _updatePrintJobFromJson(self, printJobModel,  jsonData):

		# changable...
		printJobModel.noteText = self._getValueFromDictOrNone("noteText", jsonData)
		printJobModel.noteDeltaFormat = json.dumps(self._getValueFromDictOrNone("noteDeltaFormat", jsonData))
		printJobModel.noteHtml = self._getValueFromDictOrNone("noteHtml", jsonData)
		printJobModel.printedLayers = self._getValueFromDictOrNone("printedLayers", jsonData)
		printJobModel.printedHeight = self._getValueFromDictOrNone("printedHeight", jsonData)

		filamentModel = printJobModel.loadFilamentFromAssoziation()
		filamentModel.profileVendor = self._getValueFromDictOrNone("spoolVendor", jsonData)
		filamentModel.spoolName = self._getValueFromDictOrNone("spoolName", jsonData)
		filamentModel.material = self._getValueFromDictOrNone("material", jsonData)
		filamentModel.usedLength = self._convertM2MM(self._getValueFromDictOrNone("usedLengthFormatted", jsonData))
		filamentModel.calculatedLength = self._convertM2MM(self._getValueFromDictOrNone("calculatedLengthFormatted", jsonData))
		filamentModel.usedWeight = self._getValueFromDictOrNone("usedWeight", jsonData)
		filamentModel.usedCost = self._getValueFromDictOrNone("usedCost", jsonData)

		# temperatureModel = TemperatureModel

		return printJobModel

	def _getValueFromDictOrNone(self, key, values):
		if key in values:
			return values[key]
		return None

	#  convert m to mm
	def _convertM2MM(self, value):
		if (value == None or value == ""):
			return 0.0
		floatValue = float(value)
		return floatValue * 1000.0


	def _sendCSVUploadStatusToClient(self, importStatus, currenLineNumber, backupFilePath, backupSnapshotFilePath, successMessages, errorCollection):
		self._sendDataToClient(dict(action="csvImportStatus",
									importStatus=importStatus,
									currenLineNumber = currenLineNumber,
									backupFilePath = backupFilePath,
									backupSnapshotFilePath = backupSnapshotFilePath,
									successMessages=successMessages,
									errorCollection = errorCollection
									)
							   )

	def _createSamplePrintModel(self):
		p1 = PrintJobModel()
		p1.userName = "Olli"
		p1.printStatusResult = "success"
		p1.printStartDateTime = datetime.now()
		p1.printEndDateTime = datetime.now() + timedelta(minutes=123)
		p1.duration = (p1.printEndDateTime - p1.printStartDateTime).total_seconds()
		p1.fileName = "OllisBenchy.gcode"
		p1.filePathName = "/_archive/OllisBenchy.gcode"
		p1.fileSize = 123456
		p1.printedLayers = "45 / 45"
		p1.printedHeight = "0.4 / 23.8"
		p1.noteText = "Geiles Teil!!"

		t1 = TemperatureModel()
		t1.sensorName = "bed"
		t1.sensorValue = "53"
		p1.addTemperatureModel(t1)
		t2 = TemperatureModel()
		t2.sensorName = "tool0"
		t2.sensorValue = "210"
		p1.addTemperatureModel(t2)

		f1 = FilamentModel()
		f1.profileVendor = "OllisFactory"
		f1.spoolName = "My best spool"
		f1.material = "PLA"
		f1.diameter = 1.75
		f1.density = 1.24
		f1.usedLength = 1345.0
		f1.calculatedLength = 1456.0
		f1.usedWeight = 321.0
		f1.usedCost = 1.34
		f1.spoolCostUnit = "" # no cost-unit
		p1.addFilamentModel(f1)

		return p1

################################################### APIs


	#######################################################################################   DEACTIVATE PLUGIN CHECK
	@octoprint.plugin.BlueprintPlugin.route("/deactivatePluginCheck", methods=["PUT"])
	def put_pluginDependencyCheck(self):
		self._settings.setBoolean([SettingsKeys.SETTINGS_KEY_PLUGIN_DEPENDENCY_CHECK], False)
		self._settings.save()

		return flask.jsonify([])


	#######################################################################################   LOAD ALL JOBS BY QUERY
	@octoprint.plugin.BlueprintPlugin.route("/loadPrintJobHistoryByQuery", methods=["GET"])
	def get_printjobhistoryByQuery(self):

		tableQuery = flask.request.values
		allJobsModels = self._databaseManager.loadPrintJobsByQuery(tableQuery)
		# allJobsAsDict = self._convertPrintJobHistoryModelsToDict(allJobsModels)
		allJobsAsDict = TransformPrintJob2JSON.transformAllPrintJobModels(allJobsModels)

		totalItemCount = self._databaseManager.countPrintJobsByQuery(tableQuery)
		return flask.jsonify({
								"totalItemCount": totalItemCount,
								"allPrintJobs": allJobsAsDict
							})

	#######################################################################################   DELETE JOB
	@octoprint.plugin.BlueprintPlugin.route("/removePrintJob/<int:databaseId>", methods=["DELETE"])
	def delete_printjob(self, databaseId):
		printJob = self._databaseManager.loadPrintJob(databaseId)
		snapshotFilename = CameraManager.buildSnapshotFilename(printJob.printStartDateTime)
		self._cameraManager.deleteSnapshot(snapshotFilename)
		self._databaseManager.deletePrintJob(databaseId)
		return flask.jsonify()

	#######################################################################################   UPDATE JOB
	@octoprint.plugin.BlueprintPlugin.route("/updatePrintJob/<int:databaseId>", methods=["PUT"])
	def put_printjob(self, databaseId):
		jsonData = request.json
		printJobModel = self._databaseManager.loadPrintJob(databaseId)
		self._updatePrintJobFromJson(printJobModel, jsonData)
		self._databaseManager.updatePrintJob(printJobModel)
		# response = self.get_printjobhistory()
		# return response
		return flask.jsonify()

	#######################################################################################   GET SNAPSHOT
	@octoprint.plugin.BlueprintPlugin.route("/printJobSnapshot/<string:snapshotFilename>", methods=["GET"])
	def get_snapshot(self, snapshotFilename):
		absoluteFilename = self._cameraManager.buildSnapshotFilenameLocation(snapshotFilename)
		return send_file(absoluteFilename, mimetype='image/jpg', cache_timeout=1)

	#######################################################################################   TAKE SNAPSHOT
	@octoprint.plugin.BlueprintPlugin.route("/takeSnapshot/<string:snapshotFilename>", methods=["PUT"])
	def put_snapshot(self, snapshotFilename):
		self._cameraManager.takeSnapshot(snapshotFilename, self._sendErrorMessageToClient)
		return flask.jsonify({
			"snapshotFilename": snapshotFilename
		})

	#######################################################################################   UPLOAD SNAPSHOT
	@octoprint.plugin.BlueprintPlugin.route("/upload/snapshot/<string:snapshotFilename>", methods=["POST"])
	def post_snapshot(self, snapshotFilename):

		input_name = "file"
		input_upload_path = input_name + "." + self._settings.global_get(["server", "uploads", "pathSuffix"])

		if input_upload_path in flask.request.values:
			# file was uploaded
			sourceLocation = flask.request.values[input_upload_path]
			targetLocation = self._cameraManager.buildSnapshotFilenameLocation(snapshotFilename, False)
			os.rename(sourceLocation, targetLocation)
			pass

		return flask.jsonify({
			"snapshotFilename": snapshotFilename
		})	\

	#######################################################################################   DELETE SNAPSHOT
	@octoprint.plugin.BlueprintPlugin.route("/deleteSnapshotImage/<string:snapshotFilename>", methods=["DELETE"])
	def delete_snapshot(self, snapshotFilename):

		self._cameraManager.deleteSnapshot(snapshotFilename)

		return flask.jsonify({
			"snapshotFilename": snapshotFilename
		})


	#######################################################################################   DOWNLOAD DATABASE-FILE
	@octoprint.plugin.BlueprintPlugin.route("/downloadDatabase", methods=["GET"])
	def download_database(self):
		return send_file(self._databaseManager.getDatabaseFileLocation(),
						 mimetype='application/octet-stream',
						 attachment_filename='printJobHistory.db',
						 as_attachment=True)


	#######################################################################################   DELETE DATABASE
	@octoprint.plugin.BlueprintPlugin.route("/deleteDatabase", methods=["DELETE"])
	def delete_database(self):

		self._databaseManager.reCreateDatabase()

		return flask.jsonify({
			"result": "success"
		})

	#######################################################################################   EXPORT DATABASE as CSV
	@octoprint.plugin.BlueprintPlugin.route("/exportPrintJobHistory/<string:exportType>", methods=["GET"])
	def exportPrintJobHistoryData(self, exportType):

		if exportType == "CSV":
			allJobsModels = self._databaseManager.loadAllPrintJobs()

			return Response(CSVExportImporter.transform2CSV(allJobsModels),
							mimetype='text/csv',
							headers={'Content-Disposition': 'attachment; filename=OctoprintPrintJobHistory.csv'}) # TODO add timestamp

		else:
			print("BOOOMM not supported type")
		pass


	@octoprint.plugin.BlueprintPlugin.route("/sampleCSV", methods=["GET"])
	def get_sampleCSV(self):

		allJobsModels = list()

		printModel = self._createSamplePrintModel()
		allJobsModels.append(printModel)

		# allJobsModels = self._databaseManager.loadAllPrintJobs()
		# allJobsDict = TransformPrintJob2JSON.transformAllPrintJobModels(allJobsModels)
		# csvContent = Transform2CSV.transform2CSV(allJobsDict)
		# csvContent = CSVExportImporter.transform2CSV(allJobsModels)



		return Response(CSVExportImporter.transform2CSV(allJobsModels),
						mimetype='text/csv',
						headers={'Content-Disposition': 'attachment; filename=PrintJobHistory-SAMPLE.csv'})



	######################################################################################   UPLOAD CSV FILE (in Thread)

	def _processCSVUploadAsync(self, path, importCSVMode, databaseManager, cameraManager, backupFolder, sendCSVUploadStatusToClient, logger):
		errorCollection = list()

		# - parsing
		# - backup
		# - append or replace

		def updateParsingStatus(lineNumber):
			# importStatus, currenLineNumber, backupFilePath, backupSnapshotFilePath, successMessages, errorCollection
			sendCSVUploadStatusToClient("running", lineNumber, "", "", "", errorCollection)


		resultOfPrintJobs = CSVExportImporter.parseCSV(path, updateParsingStatus, errorCollection, logger)

		importModeText = "append"
		backupDatabaseFilePath = None
		backupSnapshotFilePath = None
		if (len(resultOfPrintJobs) > 0):
			# we could import some jobs

			# - backup
			backupDatabaseFilePath = databaseManager.backupDatabaseFile(backupFolder)
			backupSnapshotFilePath = cameraManager.backupAllSnapshots(backupFolder)

			# - import mode append/replace
			if (SettingsKeys.KEY_IMPORTCSV_MODE_REPLACE == importCSVMode):
				# delete old database and init a clean database
				databaseManager.reCreateDatabase()
				cameraManager.reCreateSnapshotFolder()

				importModeText = "fully replaced"

			# - insert all printjobs in database
			currentPrintJobNumber = 0
			for printJob in resultOfPrintJobs:
				currentPrintJobNumber = currentPrintJobNumber + 1
				updateParsingStatus(currentPrintJobNumber)
				databaseManager.insertPrintJob(printJob)
				# print(printJob)
			pass
		else:
			errorCollection.append("Nothing to import!")

		successMessage = ""
		if (len(errorCollection) == 0):
			successMessage = "All data is successful " + importModeText + " with '" + str(len(resultOfPrintJobs)) + "' print jobs."
		else:
			successMessage = "Some error(s) occurs! Maybe you need to manually rollback the database!"

		sendCSVUploadStatusToClient("finished","", backupDatabaseFilePath, backupSnapshotFilePath, successMessage, errorCollection)
		pass


	@octoprint.plugin.BlueprintPlugin.route("/importCSV", methods=["POST"])
	def post_csvUpload(self):

		input_name = "file"
		input_upload_path = input_name + "." + self._settings.global_get(["server", "uploads", "pathSuffix"])

		if input_upload_path in flask.request.values:

			importMode = flask.request.form["importCSVMode"]
			# file was uploaded
			sourceLocation = flask.request.values[input_upload_path]

			# because we process in seperate thread we need to create our own temp file, the uploaded temp file will be deleted after this request-call
			archive = tempfile.NamedTemporaryFile(delete=False)
			archive.close()
			shutil.copy(sourceLocation, archive.name)
			sourceLocation = archive.name


			thread = threading.Thread(target=self._processCSVUploadAsync,
									  args=(sourceLocation,
											importMode,
											self._databaseManager,
											self._cameraManager,
											self.get_plugin_data_folder(),
											self._sendCSVUploadStatusToClient,
											self._logger))
			thread.daemon = True
			thread.start()

			# targetLocation = self._cameraManager.buildSnapshotFilenameLocation(snapshotFilename, False)
			# os.rename(sourceLocation, targetLocation)
			pass
		else:
			return flask.make_response("Invalid request, neither a file nor a path of a file to restore provided", 400)


		return flask.jsonify(started=True)






