# coding=utf-8
from __future__ import absolute_import

import shutil
import sqlite3
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

from octoprint_PrintJobHistory.common import StringUtils
from octoprint_PrintJobHistory.common.SettingsKeys import SettingsKeys

from octoprint_PrintJobHistory.CameraManager import CameraManager
from octoprint_PrintJobHistory.common import CSVExportImporter

#############################################################
# Internal API for all Frontend communications
#############################################################
class PrintJobHistoryAPI(octoprint.plugin.BlueprintPlugin):


	def _updatePrintJobFromJson(self, printJobModel,  jsonData):
		# transfer header values
		printJobModel.fileName = self._getValueFromJSONOrNone("fileName", jsonData)
		# printJobModel.filePathName = self._getValueFromJSONOrNone("fileName", jsonData) # pech
		printJobModel.printStartDateTime = StringUtils.transformToDateTimeOrNone(self._getValueFromJSONOrNone("printStartDateTimeFormatted", jsonData))
		printJobModel.printEndDateTime = StringUtils.transformToDateTimeOrNone(self._getValueFromJSONOrNone("printEndDateTimeFormatted", jsonData))
		printJobModel.duration = self._getValueFromJSONOrNone("duration", jsonData)
		printJobModel.printedHeight = self._getValueFromJSONOrNone("printedHeight", jsonData)
		printJobModel.printedLayers = self._getValueFromJSONOrNone("printedLayers", jsonData)

		# changable...
		printJobModel.printStatusResult = self._getValueFromJSONOrNone("printStatusResult", jsonData)
		printJobModel.noteText = self._getValueFromJSONOrNone("noteText", jsonData)
		printJobModel.noteDeltaFormat = json.dumps(self._getValueFromJSONOrNone("noteDeltaFormat", jsonData))
		printJobModel.noteHtml = self._getValueFromJSONOrNone("noteHtml", jsonData)
		printJobModel.printedLayers = self._getValueFromJSONOrNone("printedLayers", jsonData)
		printJobModel.printedHeight = self._getValueFromJSONOrNone("printedHeight", jsonData)

		if (printJobModel.databaseId != None):
			filamentModel = printJobModel.loadFilamentFromAssoziation()
		else:
			filamentModel = printJobModel.allFilaments[0]
		filamentModel.profileVendor = self._getValueFromJSONOrNone("spoolVendor", jsonData)
		filamentModel.spoolName = self._getValueFromJSONOrNone("spoolName", jsonData)
		filamentModel.material = self._getValueFromJSONOrNone("material", jsonData)
		filamentModel.usedLength = self._convertM2MM(self._getValueFromJSONOrNone("usedLengthFormatted", jsonData))
		filamentModel.calculatedLength = self._convertM2MM(self._getValueFromJSONOrNone("calculatedLengthFormatted", jsonData))
		filamentModel.usedWeight = self._getValueFromJSONOrNone("usedWeight", jsonData)
		filamentModel.usedCost = self._getValueFromJSONOrNone("usedCost", jsonData)

		# temperatureModel = TemperatureModel
		if (printJobModel.databaseId != None):
			allTemperaturesModels = printJobModel.loadTemperaturesFromAssoziation()
		else:
			allTemperaturesModels = printJobModel.allTemperatures
		for tempModel in allTemperaturesModels:
			sensorName = StringUtils.to_native_str(tempModel.sensorName)
			if (sensorName == "bed"):
				newBedTemp = self._getValueFromJSONOrNone("temperatureBed", jsonData)
				tempModel.sensorValue = newBedTemp
				continue
			if (sensorName.startswith("tool")):
				newToolTemp = self._getValueFromJSONOrNone("temperatureNozzle", jsonData)
				tempModel.sensorValue = newToolTemp

		return printJobModel

	def _getValueFromJSONOrNone(self, key, values):
		if key in values:
			return values[key]
		return None

	def _toIntFromJSONOrNone(self, key, json):
		value = self._getValueFromJSONOrNone(key, json)
		if (value != None):
			if (StringUtils.isNotEmpty(value)):
				try:
					value = int(value)
				except Exception as e:
					errorMessage = str(e)
					self._logger.error("could not transform value '"+str(value)+"' for key '"+key+"' to int:" + errorMessage)
					value = None
			else:
				value = None
		return value

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


	#######################################################################################   LOAD STATISTIC BY QUERY
	@octoprint.plugin.BlueprintPlugin.route("/loadStatisticByQuery", methods=["GET"])
	def get_statisticByQuery(self):

		tableQuery = flask.request.values
		statistic = self._databaseManager.calculatePrintJobsStatisticByQuery(tableQuery)

		return flask.jsonify(statistic)

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

		allJobsModels = []
		if "databaseIds" in flask.request.values:
			selectedDatabaseIds = flask.request.values["databaseIds"]
			allJobsModels = self._databaseManager.loadSelectedPrintJobs(selectedDatabaseIds)
		else:
			allJobsModels.append(self._databaseManager.loadPrintJob(databaseId))

		for printJob in allJobsModels:
			self._databaseManager.deletePrintJob(printJob.databaseId)
			snapshotFilename = CameraManager.buildSnapshotFilename(printJob.printStartDateTime)
			self._cameraManager.deleteSnapshot(snapshotFilename)

		return flask.jsonify()

	#######################################################################################   UPDATE JOB
	@octoprint.plugin.BlueprintPlugin.route("/storePrintJob/<databaseId>", methods=["PUT"])
	def put_printjob(self, databaseId):
		jsonData = request.json

		printJobModel = None
		oldStartDateTimeIfChanged = None
		newStartDateTime = None
		if (databaseId == 'null'):
			printJobModel = PrintJobModel()

			filemanentModel = FilamentModel()
			printJobModel.addFilamentModel(filemanentModel)

			tempModel = TemperatureModel()
			tempModel.sensorName = "bed"
			printJobModel.addTemperatureModel(tempModel)

			tempModel = TemperatureModel()
			tempModel.sensorName = self._settings.get([SettingsKeys.SETTINGS_KEY_DEFAULT_TOOL_ID])
			printJobModel.addTemperatureModel(tempModel)

		else:
			printJobModel = self._databaseManager.loadPrintJob(databaseId)
			# check if the startDate is changed, if true -> change snapshot image as well
			currentStartDateTime = printJobModel.printStartDateTime
			newStartDateTime = StringUtils.transformToDateTimeOrNone(self._getValueFromJSONOrNone("printStartDateTimeFormatted", jsonData))
			changed = currentStartDateTime != newStartDateTime
			if (changed):
				oldStartDateTimeIfChanged = currentStartDateTime
				try:
					self._cameraManager.renameSnapshotFilename(oldStartDateTimeIfChanged, newStartDateTime)
				except (Exception) as error:
					self._logger.error(error)
					message = errorMessage = str(error)
					self._sendDataToClient(dict(action="errorPopUp",
												title= "could not rename snapshot image to new startdatetime",
												message=message))


		def imageRollbackHandler():
			if (oldStartDateTimeIfChanged != None):
				# do rollback on snapshotimage filename
				try:
					self._cameraManager.renameSnapshotFilename(newStartDateTime, oldStartDateTimeIfChanged)
				except (Exception) as error:
					self._logger.error(error)
					message = errorMessage = str(error)
					self._sendDataToClient(dict(action="errorPopUp",
												title= "could not rename snapshot image to new startdatetime",
												message=message))
				pass
			pass


		# transfer values from ui to the model
		self._updatePrintJobFromJson(printJobModel, jsonData)

		if (databaseId == 'null'):
			self._databaseManager.insertPrintJob(printJobModel)
		else:

			self._databaseManager.updatePrintJob(printJobModel, imageRollbackHandler)

		return flask.jsonify()

	#######################################################################################   FORCE CLOSE EDIT DIALOG
	@octoprint.plugin.BlueprintPlugin.route("/forceCloseEditDialog", methods=["PUT"])
	def put_forceCloseEditDialog(self):

		# Inform all Browser to close the EditDialog
		self._sendDataToClient(dict(action="closeEditDialog"))

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
			shutil.move(sourceLocation, targetLocation)
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
			if "databaseIds" in flask.request.values:
				selectedDatabaseIds = flask.request.values["databaseIds"]
				allJobsModels = self._databaseManager.loadSelectedPrintJobs(selectedDatabaseIds)
			else:
				allJobsModels = self._databaseManager.loadAllPrintJobs()

			return Response(CSVExportImporter.transform2CSV(allJobsModels),
							mimetype='text/csv',
							headers={'Content-Disposition': 'attachment; filename=OctoprintPrintJobHistory.csv'}) # TODO add timestamp

		else:
			if (exportType == "legacyPrintHistory"):
				return self.exportPrintHistoryData()

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

		if (len(errorCollection) != 0):
			successMessage = "Some error(s) occurs during parsing! No jobs imported!"
			sendCSVUploadStatusToClient("finished", "", "", "", successMessage, errorCollection)
			return

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

	###################################################################################### EXPORT of PrintHistory.db
	# @octoprint.plugin.BlueprintPlugin.route("/exportPrintHistory", methods=["GET"])
	def exportPrintHistoryData(self):

		allJobsModels = list()


		history_db_path = self.get_plugin_data_folder()+"/../printhistory/history.db"

		conn = sqlite3.connect(history_db_path)
		cur = conn.cursor()
		cur.execute("SELECT * FROM print_history ORDER BY timestamp")

		for row in cur.fetchall():
			printJob = PrintJobModel()
			filamentModel = FilamentModel()
			isFilamentValuesPresent = False
			for i, value in enumerate(row):
				# id, fileName, note, spool, filamentVolume (float), filamentLength (float), printTime (float), success (int), timestamp (float), user (unicode), parameters (json-string)
				fieldName = cur.description[i][0]
				if (fieldName == "fileName"):
					printJob.fileName = value
					continue
				if (fieldName == "note"):
					printJob.noteText = value
					continue
				if (fieldName == "spool"):
					isFilamentValuesPresent = True
					filamentModel.spoolName = value
					continue
				if (fieldName == "filamentVolume"):
					# isFilamentValuesPresent = True
					# filamentModel.spoolName = value
					continue # just ignore
				if (fieldName == "filamentLength"):
					isFilamentValuesPresent = True
					filamentModel.usedLength = value
					filamentModel.calculatedLength = value
					continue
				if (fieldName == "printTime"):
					printJob.duration = int(value)
					continue
				if (fieldName == "success"):
					if (value == 1):
						printJob.printStatusResult = "success"
					else:
						printJob.printStatusResult = "failed"
					continue
				if (fieldName == "timestamp"):
					startPrintDataTime = datetime.fromtimestamp(value)
					printJob.printStartDateTime = startPrintDataTime
					continue
				if (fieldName == "user"):
					printJob.userName = value
					continue

				if (fieldName == "parameters"):
					continue # just ignore
				pass

			if (isFilamentValuesPresent == True):
				printJob.addFilamentModel(filamentModel)

			# Calculate endtime
			endDateTime = printJob.printStartDateTime + timedelta(seconds=printJob.duration)
			printJob.printEndDateTime = endDateTime

			allJobsModels.append(printJob)
		# history_dict = [dict(
		# 						(cur.description[i][0], value) \
		# 					 for i, value in enumerate(row)
		# 					) for row in cur.fetchall()]

		conn.close()

		return Response(CSVExportImporter.transform2CSV(allJobsModels),
						mimetype='text/csv',
						headers={'Content-Disposition': 'attachment; filename=PrintHistory.csv'})
