# coding=utf-8
from __future__ import absolute_import

import threading
import time

import octoprint.plugin
from octoprint.events import Events

import datetime
import math
import flask
import os
import shutil
import tempfile
import json

from octoprint_PrintJobHistory.common import CSVExportImporter
from octoprint_PrintJobHistory.models.FilamentModel import FilamentModel
from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from octoprint_PrintJobHistory.models.TemperatureModel import TemperatureModel
from peewee import DoesNotExist

from .common.SettingsKeys import SettingsKeys
from .common.SlicerSettingsParser import SlicerSettingsParser
from .api.PrintJobHistoryAPI import PrintJobHistoryAPI
from .api import TransformPrintJob2JSON
from .DatabaseManager import DatabaseManager
from .CameraManager import CameraManager

from octoprint_PrintJobHistory.common import StringUtils


class PrintJobHistoryPlugin(
	PrintJobHistoryAPI,
	octoprint.plugin.SettingsPlugin,
	octoprint.plugin.AssetPlugin,
	octoprint.plugin.TemplatePlugin,
	octoprint.plugin.StartupPlugin,
	octoprint.plugin.EventHandlerPlugin,
	octoprint.plugin.SimpleApiPlugin
):

	def initialize(self):
		self._preHeatPluginImplementation = None
		self._preHeatPluginImplementationState = None
		self._filamentManagerPluginImplementation = None
		self._filamentManagerPluginImplementationState = None
		self._displayLayerProgressPluginImplementation = None
		self._displayLayerProgressPluginImplementationState = None
		self._spoolManagerPluginImplementation = None
		self._spoolManagerPluginImplementationState = None
		self._ultimakerFormatPluginImplementation = None
		self._ultimakerFormatPluginImplementationState = None
		self._prusaSlicerThumbnailsPluginImplementation = None
		self._prusaSlicerThumbnailsPluginImplementationState = None
		self._printHistoryPluginImplementation = None
		self._isMultiSpoolManagerPluginsAvailable = False

		pluginDataBaseFolder = self.get_plugin_data_folder()

		self._logger.info("Start initializing")
		# DATABASE
		sqlLoggingEnabled = self._settings.get_boolean([SettingsKeys.SETTINGS_KEY_SQL_LOGGING_ENABLED])
		self._databaseManager = DatabaseManager(self._logger, sqlLoggingEnabled)
		self._databaseManager.initDatabase(pluginDataBaseFolder, self._sendErrorMessageToClient)

		# CAMERA
		self._cameraManager = CameraManager(self._logger)
		pluginBaseFolder = self._basefolder

		self._cameraManager.initCamera(pluginDataBaseFolder, pluginBaseFolder, self._settings)

		# Init values for initial settings view-page
		self._settings.set([SettingsKeys.SETTINGS_KEY_DATABASE_PATH], self._databaseManager.getDatabaseFileLocation())
		self._settings.set([SettingsKeys.SETTINGS_KEY_SNAPSHOT_PATH], self._cameraManager.getSnapshotFileLocation())
		self._settings.save()

		# OTHER STUFF
		self._currentPrintJobModel = None

		self.alreadyCanceled = False

		self._logger.info("Done initializing")

	################################################################################################## private functions
	def _sendDataToClient(self, payloadDict):
		self._plugin_manager.send_plugin_message(self._identifier,
												 payloadDict)

	def _sendErrorMessageToClient(self, title, message):
		self._sendDataToClient(dict(action="errorPopUp",
									title=title,
									message=message))

	def _sendReloadTableToClient(self, shouldSend=True):
		if (shouldSend == True):
			payload = {
				"action": "reloadTableItems"
			}
			self._sendDataToClient(payload)

	def _checkForMissingPluginInfos(self, sendToClient=False):

		pluginInfo = self._getPluginInformation("preheat")
		self._preHeatPluginImplementationState = pluginInfo[0]
		self._preHeatPluginImplementation = pluginInfo[1]

		pluginInfo = self._getPluginInformation("filamentmanager")
		self._filamentManagerPluginImplementationState = pluginInfo[0]
		self._filamentManagerPluginImplementation = pluginInfo[1]

		pluginInfo = self._getPluginInformation("DisplayLayerProgress")
		self._displayLayerProgressPluginImplementationState = pluginInfo[0]
		self._displayLayerProgressPluginImplementation = pluginInfo[1]

		pluginInfo = self._getPluginInformation("SpoolManager")
		self._spoolManagerPluginImplementationState = pluginInfo[0]
		self._spoolManagerPluginImplementation = pluginInfo[1]

		pluginInfo = self._getPluginInformation("UltimakerFormatPackage")
		self._ultimakerFormatPluginImplementationState = pluginInfo[0]
		self._ultimakerFormatPluginImplementation = pluginInfo[1]

		pluginInfo = self._getPluginInformation("prusaslicerthumbnails")
		self._prusaSlicerThumbnailsPluginImplementationState = pluginInfo[0]
		self._prusaSlicerThumbnailsPluginImplementation = pluginInfo[1]

		pluginInfo = self._getPluginInformation("printhistory")
		if ("enabled" == pluginInfo[0]):
			self._printHistoryPluginImplementation = pluginInfo[1]
		else:
			self._printHistoryPluginImplementation = None


		isSpoolManagerInstalledAndEnabled = True if self._spoolManagerPluginImplementation != None and self._spoolManagerPluginImplementationState == "enabled" else False
		isFilamentManagerInstalledAndEnabled = True if self._filamentManagerPluginImplementation != None and self._filamentManagerPluginImplementationState == "enabled" else False

		if (isSpoolManagerInstalledAndEnabled and isFilamentManagerInstalledAndEnabled):
			self._isMultiSpoolManagerPluginsAvailable = True
		else:
			# which one is choosen for tracking, maybe it was deinstalled
			filamentTrackerBySettings = self._settings.get([SettingsKeys.SETTINGS_KEY_SELECTED_FILAMENTTRACKER_PLUGIN])
			filamentTrackerByInstallation = SettingsKeys.KEY_SELECTED_SPOOLMANAGER_PLUGIN if self._spoolManagerPluginImplementation != None and self._spoolManagerPluginImplementationState == "enabled" else SettingsKeys.KEY_SELECTED_FILAMENTMANAGER_PLUGIN

			if (filamentTrackerBySettings != filamentTrackerByInstallation):
				self._settings.set([SettingsKeys.SETTINGS_KEY_SELECTED_FILAMENTTRACKER_PLUGIN], filamentTrackerByInstallation)
				self._settings.save()

		if ( (isSpoolManagerInstalledAndEnabled == False) and (isFilamentManagerInstalledAndEnabled == False) ):
				self._settings.set([SettingsKeys.SETTINGS_KEY_SELECTED_FILAMENTTRACKER_PLUGIN], SettingsKeys.KEY_SELECTED_NONE_PLUGIN)
				self._settings.save()


		self._logger.info("Plugin-State: "
						  "PreHeat=" + self._preHeatPluginImplementationState + " "
						  "DisplayLayerProgress=" + self._displayLayerProgressPluginImplementationState + " "
						  "SpoolManager=" + self._spoolManagerPluginImplementationState + " "
						  "filamentmanager=" + self._filamentManagerPluginImplementationState + " "
																																																																											"PrusaSlicerThumbnails=" + self._ultimakerFormatPluginImplementationState)

		if sendToClient == True:
			missingMessage = ""

			if self._preHeatPluginImplementation == None:
				missingMessage = missingMessage + "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/preheat/'>PreHeat Button</a> (<b>" + self._preHeatPluginImplementationState + "</b>)</li>"

			if self._spoolManagerPluginImplementation == None:
				missingMessage = missingMessage + "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/SpoolManager/'>SpoolManager </a>(<b>" + self._spoolManagerPluginImplementationState + "</b>)</li>"

			if self._filamentManagerPluginImplementation == None:
				missingMessage = missingMessage + "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/filamentmanager/'>FilamentManager</a> (<b>" + self._filamentManagerPluginImplementationState + "</b>)</li>"

			if self._displayLayerProgressPluginImplementation == None:
				missingMessage = missingMessage + "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/DisplayLayerProgress/'>DisplayLayerProgress</a> (<b>" + self._displayLayerProgressPluginImplementationState + "</b>)</li>"

			if self._ultimakerFormatPluginImplementation == None:
				missingMessage = missingMessage + "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/UltimakerFormatPackage/'>Cura Thumbnails</a> (<b>" + self._ultimakerFormatPluginImplementationState + "</b>)</li>"

			if self._prusaSlicerThumbnailsPluginImplementation == None:
				missingMessage = missingMessage + "<li><a target='_newTab' href='https://plugins.octoprint.org/plugins/prusaslicerthumbnails/'>PrusaSlicer Thumbnails</a> (<b>" + self._prusaSlicerThumbnailsPluginImplementationState + "</b>)</li>"

			if missingMessage != "":
				missingMessage = "<ul>" + missingMessage + "</ul>"
				self._sendDataToClient(dict(action="missingPlugin",
											message=missingMessage))

	# get the plugin with status information
	# [0] == status-string
	# [1] == implementaiton of the plugin
	def _getPluginInformation(self, pluginKey):

		status = None
		implementation = None

		if pluginKey in self._plugin_manager.plugins:
			plugin = self._plugin_manager.plugins[pluginKey]
			if plugin != None:
				if (plugin.enabled == True):
					status = "enabled"
					# for OP 1.4.x we need to check agains "icompatible"-attribute
					if (hasattr(plugin, 'incompatible')):
						if (plugin.incompatible == False):
							implementation = plugin.implementation
						else:
							status = "incompatible"
					else:
						# OP 1.3.x
						implementation = plugin.implementation
					pass
				else:
					status = "disabled"
		else:
			status = "missing"

		return [status, implementation]

	# Grabs all informations for the filament attributes
	def _createAndAssignFilamentModel(self, printJob, payload):

		filePath = payload["path"]
		fileData = self._file_manager.get_metadata(payload["origin"], filePath)

		# - grab calcualted data for each tool
		# - grap measured data for each tool
		filamentCalculatedDict = self._readCalculatedFilamentMetaData(fileData)
		filamentExtrusionArray = self._readMeasuredFilament()
		selectedSpoolDataDict = self._getSelectedSpools()
		# isMultiToolPrint = len(filamentCalculatedDict) > 1

		# - add always "total"
		calculatedTotalLength = 0.0

		totalFilamentModel = FilamentModel()
		totalFilamentModel.toolId = "total"
		printJob.addFilamentModel(totalFilamentModel)

		# - assign calculated values
		if (filamentCalculatedDict != None):

			for toolId in filamentCalculatedDict:
				filamentModel = FilamentModel()
				filamentModel.toolId = toolId

				calculatedLength = filamentCalculatedDict[toolId]["length"]
				# not needed calculatedVolumne = filamentCalculatedDict[toolId]["volume"]

				filamentModel.calculatedLength = calculatedLength
				calculatedTotalLength = calculatedTotalLength + calculatedLength
				printJob.addFilamentModel(filamentModel)
				pass

		totalFilamentModel.calculatedLength = calculatedTotalLength

		# - assign measured values
		if (filamentExtrusionArray != None):
			usedTotalLength = 0.0
			usedTotaWeight = 0.0
			usedTotalCost = 0.0
			toolIndex = 0
			for usedLength in filamentExtrusionArray:
				toolId = "tool" + str(toolIndex)
				filamentModel = printJob.getFilamentModelByToolId(toolId)
				if (filamentModel == None):
					filamentModel = FilamentModel()
					filamentModel.toolId = toolId
					printJob.addFilamentModel(filamentModel)

				filamentModel.toolId = toolId
				filamentModel.usedLength = usedLength
				usedTotalLength = usedTotalLength + usedLength
				# get spool data, if available
				if (selectedSpoolDataDict != None and toolId in selectedSpoolDataDict):
					spoolData = selectedSpoolDataDict[toolId]

					filamentModel.spoolName = spoolData["spoolName"]
					filamentModel.vendor = spoolData["vendor"]
					filamentModel.material = spoolData["material"]
					filamentModel.diameter = spoolData["diameter"]
					# filamentModel.spoolCostUnit = TODO
					filamentModel.density = spoolData["density"]
					filamentModel.usedWeight = self._calculateFilamentWeightForLength(usedLength, filamentModel.diameter, filamentModel.density)
					usedTotaWeight = usedTotaWeight + filamentModel.usedWeight

					filamentModel.spoolCost = spoolData["spoolCost"]
					filamentModel.weight = spoolData["weight"]
					filamentModel.usedCost = filamentModel.spoolCost / filamentModel.weight * filamentModel.usedWeight
					usedTotalCost = usedTotalCost + filamentModel.usedCost

				toolIndex = toolIndex + 1
			# - add total values
			filamentModel = printJob.getFilamentModelByToolId("total")
			if (filamentModel == None):
				filamentModel = FilamentModel()
				filamentModel.toolId = "total"
				printJob.addFilamentModel(filamentModel)

			filamentModel.usedLength = usedTotalLength
			filamentModel.usedWeight = usedTotaWeight
			filamentModel.usedCost = usedTotalCost
			# - assign all spool informations to total
			allSpoolNames = ""
			allVendors = ""
			allMaterials = ""
			allFilamentsWithoutTotal = printJob.getFilamentModels(withoutTotal=True)
			for filament in allFilamentsWithoutTotal:
				if ((filament.spoolName in allSpoolNames) == False):
					if (allSpoolNames != ""):
						allSpoolNames = allSpoolNames + ", "
					allSpoolNames = allSpoolNames + filament.spoolName

				if ((filament.vendor in allVendors) == False):
					if (allVendors != ""):
						allVendors = allVendors + ", "
					allVendors = allVendors + filament.vendor

				if ((filament.material in allMaterials) == False):
					if (allMaterials != ""):
						allMaterials = allMaterials + ", "
					allMaterials = allMaterials + filament.material

			filamentModel.spoolName = allSpoolNames
			filamentModel.vendor = allVendors
			filamentModel.material = allMaterials




	# read the total extrusion of each tool, like this
	# return [123.123, 234.234, 0, 0]
	def _readMeasuredFilament(self):
		result = None
		# get some data from the selected filament tracker plugin
		filamentTrackerPlugin = self._settings.get([SettingsKeys.SETTINGS_KEY_SELECTED_FILAMENTTRACKER_PLUGIN])
		if (SettingsKeys.KEY_SELECTED_SPOOLMANAGER_PLUGIN == filamentTrackerPlugin):
			# get data from SPOOLMANAGER
			result = self._spoolManagerPluginImplementation.myFilamentOdometer.getExtrusionAmount()
			pass
		elif (SettingsKeys.KEY_SELECTED_FILAMENTMANAGER_PLUGIN == filamentTrackerPlugin):
			# myFilamentOdometer, since FilamentManager V1.7.2
			result = self._filamentManagerPluginImplementation.myFilamentOdometer.getExtrusionAmount()
			pass
		else:
			self._logger.info("There is no plugin for filament tracking available. Installed and Enabled?")
		return result

	# dict of this
	# {u'tool4': {u'volume': 185.20129656279946, u'length': 76997.75167999369},
	#  u'tool3': {u'volume': 0.0, u'length': 0.0}, u'tool2': {u'volume': 0.0, u'length': 0.0},
	#  u'tool1': {u'volume': 0.0, u'length': 0.0}, u'tool0': {u'volume': 0.0, u'length': 0.0}}

	def _readCalculatedFilamentMetaData(self, fileData):
		filamentAnalyseDict = None
		if "analysis" in fileData:
			if "filament" in fileData["analysis"]:
				filamentAnalyseDict = fileData["analysis"]["filament"]
		if (filamentAnalyseDict == None):
			self._logger.info("There is no calculated filament data in meta-file?")
		return filamentAnalyseDict

	# read the selected tools
	# return  {
	# 'tool0': {'databaseId': 4711, 'spoolName': 'NewSpool', 'weight': 2000.0, 'spoolCost': 123.2, 'material': 'PLA', 'vendor: 'MaterMost', 'density': 4.25, 'diameter': 1.75, },
	# 'tool1': {}
	# },
	def _getSelectedSpools(self):
		result = None
		# get some data from the selected filament tracker plugin
		filamentTrackerPlugin = self._settings.get([SettingsKeys.SETTINGS_KEY_SELECTED_FILAMENTTRACKER_PLUGIN])
		if (SettingsKeys.KEY_SELECTED_SPOOLMANAGER_PLUGIN == filamentTrackerPlugin):
			# get data from SPOOLMANAGER

			# TODO
			pass
		elif (SettingsKeys.KEY_SELECTED_FILAMENTMANAGER_PLUGIN == filamentTrackerPlugin):
			# myFilamentOdometer, since FilamentManager V1.7.2
			selectedSpools = self._filamentManagerPluginImplementation.filamentManager.get_all_selections(self._filamentManagerPluginImplementation.client_id)
			if selectedSpools != None and len(selectedSpools) > 0:
				result = {}
				for currentSpoolData in selectedSpools:
					toolId = "tool" + str(currentSpoolData["tool"])
					spoolData = currentSpoolData["spool"]
					databaseId = spoolData["id"]
					spoolName = spoolData["name"]
					weight = spoolData["weight"]
					spoolCost = spoolData["cost"]

					profileData = spoolData["profile"]
					material = profileData["material"]
					vendor = profileData["vendor"]
					density = profileData["density"]
					diameter = profileData["diameter"]

					result[toolId] = {
						"databaseId": databaseId,
						"spoolName": spoolName,
					    "material": material,
					    "vendor":  vendor,
					    "density": density,
					  	"diameter":  diameter,
						"spoolCost": spoolCost,
						"weight": weight
					}

					pass
			pass
		else:
			self._logger.info("There is no plugin for spool selection. Installed and Enabled?")
		return result

	def _calculateFilamentWeightForLength(self, usedLength, diameter, density):
		result = 0.0
		if (usedLength != None and diameter != None and density != None):
			radius = diameter / 2.0
			volume = usedLength * math.pi * radius * radius / 1000.0
			result = volume * density
		return result


	def _updatePrintJobModelWithLayerHeightInfos(self, dlpPayload):
		totalLayers = dlpPayload["totalLayer"]
		currentLayer = dlpPayload["currentLayer"]
		self._currentPrintJobModel.printedLayers = currentLayer + " / " + totalLayers

		totalHeight = dlpPayload["totalHeightFormatted"]
		currentHeight = dlpPayload["currentHeightFormatted"]
		self._currentPrintJobModel.printedHeight = currentHeight + " / " + totalHeight


	def _createPrintJobModel(self, payload):
		self._currentPrintJobModel = PrintJobModel()
		self._currentPrintJobModel.printStartDateTime = datetime.datetime.now()

		self._currentPrintJobModel.fileOrigin = payload["origin"]
		self._currentPrintJobModel.fileName = payload["name"]
		self._currentPrintJobModel.filePathName = payload["path"]

		# self._file_manager.path_on_disk()
		if "owner" in payload:
			self._currentPrintJobModel.userName = payload["owner"]
		else:
			self._currentPrintJobModel.userName = "John Doe"
		self._currentPrintJobModel.fileSize = payload["size"]

		tempFound = False
		toolId = self._settings.get([SettingsKeys.SETTINGS_KEY_DEFAULT_TOOL_ID])
		tempTool = -1
		tempBed = 0

		shouldReadTemperatureFromPreHeat = self._settings.get_boolean(
			[SettingsKeys.SETTINGS_KEY_TAKE_TEMPERATURE_FROM_PREHEAT])
		if (shouldReadTemperatureFromPreHeat == True):
			self._logger.info("Try reading Temperature from PreHeat-Plugin...")

			if (self._preHeatPluginImplementation != None):
				path_on_disk = octoprint.server.fileManager.path_on_disk(self._currentPrintJobModel.fileOrigin,
																		 self._currentPrintJobModel.filePathName)

				preHeatTemperature = self._preHeatPluginImplementation.read_temperatures_from_file(path_on_disk)
				if preHeatTemperature != None:
					if "bed" in preHeatTemperature:
						tempBed = preHeatTemperature["bed"]
						tempFound = True
					if toolId in preHeatTemperature:
						tempTool = preHeatTemperature[toolId]  # "tool0"
						tempFound = True
					else:
						self._logger.warn(
							"... PreHeat-Temperatures does not include default Extruder-Tool '" + toolId + "'")
				pass
			else:
				self._logger.warn("... PreHeat Button Plugin not installed/enabled")

		if (tempFound == True):
			self._logger.info(
				"... Temperature found '" + str(tempBed) + "' Tool '" + toolId + "' '" + str(tempTool) + "'")
			self._addTemperatureToPrintModel(self._currentPrintJobModel, tempBed, toolId, tempTool)
		else:
			# readTemperatureFromPrinter
			# because temperature is 0 at the beginning, we need to wait a couple of seconds (maybe 3)
			self._readAndAssignCurrentTemperatureDelayed(self._currentPrintJobModel)


	def _readCurrentTemperatureFromPrinterAsync(self, printer, printJobModel, addTemperatureToPrintModel):
		dealyInSeconds = self._settings.get_int([SettingsKeys.SETTINGS_KEY_DELAY_READING_TEMPERATURE_FROM_PRINTER])
		time.sleep(dealyInSeconds)

		currentTemps = printer.get_current_temperatures()
		if (currentTemps != None and "bed" in currentTemps and "tool0" in currentTemps):
			tempBed = currentTemps["bed"]["target"]
			# Maybe an other tool should be used.
			toolId = self._settings.get([SettingsKeys.SETTINGS_KEY_DEFAULT_TOOL_ID])  # "tool0"
			tempTool = -1
			try:
				tempTool = currentTemps[toolId]["target"]
			except Exception as e:
				self._logger.error("Could not read temperature from Tool '" + toolId + "'", e)

			self._logger.info(
				"Temperature from Printer '" + str(tempBed) + "' Tool '" + toolId + "' '" + str(tempTool) + "'")
			addTemperatureToPrintModel(printJobModel, tempBed, toolId, tempTool)


	def _readAndAssignCurrentTemperatureDelayed(self, printJobModel):
		thread = threading.Thread(name='ReadCurrentTemperature',
								  target=self._readCurrentTemperatureFromPrinterAsync,
								  args=(self._printer, printJobModel, self._addTemperatureToPrintModel,))
		thread.daemon = True
		thread.start()
		pass


	def _addTemperatureToPrintModel(self, printJobModel, bedTemp, toolId, toolTemp):
		tempModel = TemperatureModel()
		tempModel.sensorName = "bed"
		# tempModel.sensorValue = bedTemp if bedTemp != None else"-"
		tempModel.sensorValue = bedTemp if bedTemp != None else "-"
		printJobModel.addTemperatureModel(tempModel)

		tempModel = TemperatureModel()
		tempModel.sensorName = toolId  # "tool0"
		tempModel.sensorValue = toolTemp if toolTemp != None else "-"
		printJobModel.addTemperatureModel(tempModel)


	#### print job finished
	# printStatus = "success", "failed", "canceled"
	def _printJobFinished(self, printStatus, payload):
		captureMode = self._settings.get([SettingsKeys.SETTINGS_KEY_CAPTURE_PRINTJOBHISTORY_MODE])
		if (captureMode == SettingsKeys.KEY_CAPTURE_PRINTJOBHISTORY_MODE_NONE):
			return

		captureThePrint = False
		if (captureMode == SettingsKeys.KEY_CAPTURE_PRINTJOBHISTORY_MODE_ALWAYS):
			captureThePrint = True
		else:
			# check status is neccessary
			if (printStatus == "success"):
				captureThePrint = True

		self._logger.info("Print result:" + printStatus + ", CaptureMode:" + captureMode)
		# capture the print
		if (captureThePrint == True):
			self._logger.info("Start capturing print job")

			# - Core Data
			self._currentPrintJobModel.printEndDateTime = datetime.datetime.now()
			self._currentPrintJobModel.duration = (
					self._currentPrintJobModel.printEndDateTime - self._currentPrintJobModel.printStartDateTime).total_seconds()
			self._currentPrintJobModel.printStatusResult = printStatus

			# - Slicer Settings
			selectedFilename = payload.get("path")
			selectedFile = self._file_manager.path_on_disk(payload.get("origin"), selectedFilename)
			slicerSettingsExpressions = self._settings.get([SettingsKeys.SETTINGS_KEY_SLICERSETTINGS_KEYVALUE_EXPRESSION])
			if (slicerSettingsExpressions != None and len(slicerSettingsExpressions) != 0):
				slicerSettings = SlicerSettingsParser(self._logger).extractSlicerSettings(selectedFile, slicerSettingsExpressions)
				if (slicerSettings.settingsAsText != None and len(slicerSettings.settingsAsText) != 0):
					self._currentPrintJobModel.slicerSettingsAsText = slicerSettings.settingsAsText

			# - Image / Thumbnail
			self._grabImage(payload)

			# - FilamentInformations e.g. length
			self._createAndAssignFilamentModel(self._currentPrintJobModel, payload)

			# store everything in the database
			databaseId = self._databaseManager.insertPrintJob(self._currentPrintJobModel)
			if (databaseId == None):
				self._logger.error("PrintJob not captured, see previous error log!")
				return
			printJobItem = None
			if self._settings.get_boolean([SettingsKeys.SETTINGS_KEY_SHOW_PRINTJOB_DIALOG_AFTER_PRINT]):

				self._settings.set_int([SettingsKeys.SETTINGS_KEY_SHOW_PRINTJOB_DIALOG_AFTER_PRINT_JOB_ID], databaseId)
				self._settings.save()

				# inform client to show job edit dialog
				printJobModel = self._databaseManager.loadPrintJob(databaseId)

				# check the correct status (redundent code, see event client_open)
				printJobItem = None
				showDisplayAfterPrintMode = self._settings.get(
					[SettingsKeys.SETTINGS_KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE])
				printJobModelStatus = printJobModel.printStatusResult

				if (showDisplayAfterPrintMode == SettingsKeys.KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE_SUCCESSFUL):
					# show only when succesfull
					if ("success" == printJobModelStatus):
						printJobItem = TransformPrintJob2JSON.transformPrintJobModel(printJobModel)
				elif (showDisplayAfterPrintMode == SettingsKeys.KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE_FAILED):
					if ("failed" == printJobModelStatus or "canceled" == printJobModelStatus):
						printJobItem = TransformPrintJob2JSON.transformPrintJobModel(printJobModel)

				else:
					# always
					printJobItem = TransformPrintJob2JSON.transformPrintJobModel(printJobModel)

			# inform client for a reload (and show dialog)
			payload = {
				"action": "printFinished",
				"printJobItem": printJobItem  # if present then the editor dialog is shown
			}
			self._sendDataToClient(payload)
		else:
			self._logger.info("PrintJob not captured, because not activated!")


	def _grabImage(self, payload):
		isCameraPresent = self._cameraManager.isCamaraSnahotURLPresent()

		takeSnapshotAfterPrint = self._settings.get_boolean([SettingsKeys.SETTINGS_KEY_TAKE_SNAPSHOT_AFTER_PRINT])
		takeSnapshotOnGCode = self._settings.get_boolean([SettingsKeys.SETTINGS_KEY_TAKE_SNAPSHOT_ON_GCODE_COMMAND])
		takeThumbnailAfterPrint = self._settings.get_boolean(
			[SettingsKeys.SETTINGS_KEY_TAKE_PLUGIN_THUMBNAIL_AFTER_PRINT])

		preferedSnapshot = self._settings.get(
			[SettingsKeys.SETTINGS_KEY_PREFERED_IMAGE_SOURCE]) == SettingsKeys.KEY_PREFERED_IMAGE_SOURCE_CAMERA
		preferedThumbnail = self._settings.get(
			[SettingsKeys.SETTINGS_KEY_PREFERED_IMAGE_SOURCE]) == SettingsKeys.KEY_PREFERED_IMAGE_SOURCE_THUMBNAIL

		isThumbnailPresent = self._isThumbnailPresent(payload)

		# - No Image
		if (takeSnapshotAfterPrint == False and takeSnapshotOnGCode == False and takeThumbnailAfterPrint == False):
			self._logger.info("no image should be taken")
			return
		# - Only Thumbnail
		if (takeThumbnailAfterPrint == True and takeSnapshotAfterPrint == False and takeSnapshotOnGCode == False):
			# Try to take the thmbnail
			self._takeThumbnailImage(payload)
			return
		if (takeThumbnailAfterPrint == True and isThumbnailPresent == True and preferedThumbnail == True):
			self._takeThumbnailImage(payload)
			return
		# - Only Camera
		if ((takeSnapshotAfterPrint == True or takeSnapshotOnGCode == True) and takeThumbnailAfterPrint == False):
			if (isCameraPresent == False):
				self._logger.info("Camera Snapshot is selected but no camera url is available")
				return
			self._cameraManager.takeSnapshotAsync(
				CameraManager.buildSnapshotFilename(self._currentPrintJobModel.printStartDateTime),
				self._sendErrorMessageToClient,
				self._sendReloadTableToClient
			)

			return
		# - Camera
		if (isCameraPresent == True and takeSnapshotAfterPrint == True):
			self._cameraManager.takeSnapshotAsync(
				CameraManager.buildSnapshotFilename(self._currentPrintJobModel.printStartDateTime),
				self._sendErrorMessageToClient,
				self._sendReloadTableToClient
			)


	def _isThumbnailPresent(self, payload):
		return self._takeThumbnailImage(payload, storeImage=False)


	def _takeThumbnailImage(self, payload, storeImage=True):
		thumbnailPresent = False
		metadata = self._file_manager.get_metadata(payload["origin"], payload["path"])
		# check if available
		if ("thumbnail" in metadata):
			thumbnailPresent = self._cameraManager.takePluginThumbnail(
				CameraManager.buildSnapshotFilename(self._currentPrintJobModel.printStartDateTime),
				metadata["thumbnail"],
				storeImage=storeImage
			)
		else:
			self._logger.warn("Thumbnail not found in print metadata")

		return thumbnailPresent


	#######################################################################################   OP - HOOKs
	def on_after_startup(self):
		# check if needed plugins were available
		self._checkForMissingPluginInfos()


	# Listen to all  g-code which where already sent to the printer (thread: comm.sending_thread)
	def on_sentGCodeHook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		# take snapshot an gcode command
		if (self._settings.get_boolean([SettingsKeys.SETTINGS_KEY_TAKE_SNAPSHOT_ON_GCODE_COMMAND])):
			gcodePattern = self._settings.get([SettingsKeys.SETTINGS_KEY_TAKE_SNAPSHOT_GCODE_COMMAND_PATTERN])
			commandAsString = StringUtils.to_native_str(cmd)
			if (commandAsString.startswith(gcodePattern)):
				self._logger.info("M117 mesaage for taking snapshot detected. Try to capture image!")
				self._cameraManager.takeSnapshotAsync(
					CameraManager.buildSnapshotFilename(self._currentPrintJobModel.printStartDateTime),
					self._sendErrorMessageToClient
				)
			pass
		pass


	def on_event(self, event, payload):
		# WebBrowser opened
		if Events.CLIENT_OPENED == event:
			# Send plugin storage information
			## Storage
			if (hasattr(self, "_databaseManager") == True):
				databaseFileLocation = self._databaseManager.getDatabaseFileLocation()
				snapshotFileLocation = self._cameraManager.getSnapshotFileLocation()

				self._sendDataToClient(dict(action="initalData",
											databaseFileLocation=databaseFileLocation,
											snapshotFileLocation=snapshotFileLocation,
											isPrintHistoryPluginAvailable=self._printHistoryPluginImplementation != None,
											isMultiSpoolManagerPluginsAvailable = self._isMultiSpoolManagerPluginsAvailable
											))
			# Check if all needed Plugins are available, if not modale dialog to User
			if self._settings.get_boolean([SettingsKeys.SETTINGS_KEY_PLUGIN_DEPENDENCY_CHECK]):
				self._checkForMissingPluginInfos(True)

			# Show last Print-Dialog
			if self._settings.get_boolean([SettingsKeys.SETTINGS_KEY_SHOW_PRINTJOB_DIALOG_AFTER_PRINT]):
				printJobId = self._settings.get_int([SettingsKeys.SETTINGS_KEY_SHOW_PRINTJOB_DIALOG_AFTER_PRINT_JOB_ID])
				if (not printJobId == None):
					try:
						printJobModel = self._databaseManager.loadPrintJob(printJobId)

						# check the correct status
						printJobItem = None
						showDisplayAfterPrintMode = self._settings.get([SettingsKeys.SETTINGS_KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE])
						printJobModelStatus = printJobModel.printStatusResult

						if (showDisplayAfterPrintMode == SettingsKeys.KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE_SUCCESSFUL):
							# show only when succesfull
							if ("success" == printJobModelStatus):
								printJobItem = TransformPrintJob2JSON.transformPrintJobModel(printJobModel)
						elif (showDisplayAfterPrintMode == SettingsKeys.KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE_FAILED):
							if ("failed" == printJobModelStatus or "canceled" == printJobModelStatus):
								printJobItem = TransformPrintJob2JSON.transformPrintJobModel(printJobModel)
						else:
							# always
							printJobItem = TransformPrintJob2JSON.transformPrintJobModel(printJobModel)

						payload = {
							"action": "showPrintJobDialogAfterClientConnection",
							"printJobItem": printJobItem
						}
						self._sendDataToClient(payload)
					except DoesNotExist as e:
						self._settings.remove([SettingsKeys.SETTINGS_KEY_SHOW_PRINTJOB_DIALOG_AFTER_PRINT_JOB_ID])

		elif Events.PRINT_STARTED == event:
			self.alreadyCanceled = False
			self._createPrintJobModel(payload)

		elif "DisplayLayerProgress_layerChanged" == event or event == "DisplayLayerProgress_heightChanged":
			self._updatePrintJobModelWithLayerHeightInfos(payload)

		elif Events.PRINT_DONE == event:
			self._printJobFinished("success", payload)
		elif Events.PRINT_FAILED == event:
			if self.alreadyCanceled == False:
				self._printJobFinished("failed", payload)
		elif Events.PRINT_CANCELLED == event:
			self.alreadyCanceled = True
			self._printJobFinished("canceled", payload)

		pass


	def on_settings_save(self, data):
		# default save function
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		# reinitialize some fields
		sqlLoggingEnabled = self._settings.get_boolean([SettingsKeys.SETTINGS_KEY_SQL_LOGGING_ENABLED])
		self._databaseManager.showSQLLogging(sqlLoggingEnabled)



	# to allow the frontend to trigger an GET call
	def on_api_get(self, request):
		if len(request.values) != 0:
			action = request.values["action"]

			# deceide if you want the reset function in you settings dialog
			if "isResetSettingsEnabled" == action:
				return flask.jsonify(enabled="true")

			if "resetSettings" == action:
				self._settings.set([], self.get_settings_defaults())
				self._settings.save()
				return flask.jsonify(self.get_settings_defaults())
		pass


	##~~ SettingsPlugin mixin
	def get_settings_defaults(self):
		settings = dict()
		## General
		settings[SettingsKeys.SETTINGS_KEY_PLUGIN_DEPENDENCY_CHECK] = True
		settings[SettingsKeys.SETTINGS_KEY_SHOW_PRINTJOB_DIALOG_AFTER_PRINT] = True
		settings[SettingsKeys.SETTINGS_KEY_SHOW_PRINTJOB_DIALOG_AFTER_PRINT_JOB_ID] = None
		settings[SettingsKeys.SETTINGS_KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE] = SettingsKeys.KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE_SUCCESSFUL
		settings[SettingsKeys.SETTINGS_KEY_CAPTURE_PRINTJOBHISTORY_MODE] = SettingsKeys.KEY_CAPTURE_PRINTJOBHISTORY_MODE_SUCCESSFUL
		# settings[SettingsKeys.SETTINGS_KEY_SELECTED_FILAMENTTRACKER_PLUGIN] = SettingsKeys.KEY_SELECTED_SPOOLMANAGER_PLUGIN
		settings[SettingsKeys.SETTINGS_KEY_SELECTED_FILAMENTTRACKER_PLUGIN] = SettingsKeys.KEY_SELECTED_FILAMENTMANAGER_PLUGIN
		settings[SettingsKeys.SETTINGS_KEY_SLICERSETTINGS_KEYVALUE_EXPRESSION] = ";(.*)=(.*)\n;   (.*),(.*)"

		## Camera
		settings[SettingsKeys.SETTINGS_KEY_TAKE_SNAPSHOT_AFTER_PRINT] = True
		settings[SettingsKeys.SETTINGS_KEY_TAKE_PLUGIN_THUMBNAIL_AFTER_PRINT] = True
		settings[SettingsKeys.SETTINGS_KEY_TAKE_SNAPSHOT_ON_GCODE_COMMAND] = False
		settings[SettingsKeys.SETTINGS_KEY_TAKE_SNAPSHOT_GCODE_COMMAND_PATTERN] = "M117 Snap"
		settings[SettingsKeys.SETTINGS_KEY_PREFERED_IMAGE_SOURCE] = SettingsKeys.KEY_PREFERED_IMAGE_SOURCE_THUMBNAIL

		## Temperature
		settings[SettingsKeys.SETTINGS_KEY_DEFAULT_TOOL_ID] = "tool0"
		settings[SettingsKeys.SETTINGS_KEY_TAKE_TEMPERATURE_FROM_PREHEAT] = True
		settings[SettingsKeys.SETTINGS_KEY_DELAY_READING_TEMPERATURE_FROM_PRINTER] = 60

		## Export / Import
		settings[SettingsKeys.SETTINGS_KEY_IMPORT_CSV_MODE] = SettingsKeys.KEY_IMPORTCSV_MODE_APPEND

		settings["datbaseSettings"] = {
			"useExternal": "true",
			"type": "postgres",
			"host": "localhost",
			"port": 5432,
			"databaseName": "PrintJobDatabase",
			"user": "Olli",
			"password": "illO"
		}

		## Debugging
		settings[SettingsKeys.SETTINGS_KEY_SQL_LOGGING_ENABLED] = False

		# ## Storage
		# if (hasattr(self,"_databaseManager") == True):
		# 	settings[SettingsKeys.SETTINGS_KEY_DATABASE_PATH] = self._databaseManager.getDatabaseFileLocation()
		# 	settings[SettingsKeys.SETTINGS_KEY_SNAPSHOT_PATH] = self._cameraManager.getSnapshotFileLocation()
		# else:
		# 	settings[SettingsKeys.SETTINGS_KEY_DATABASE_PATH] = ""
		# 	settings[SettingsKeys.SETTINGS_KEY_SNAPSHOT_PATH] = ""

		return settings


	##~~ TemplatePlugin mixin
	def get_template_configs(self):
		return [
			dict(type="tab", name="Print Job History"),
			dict(type="settings", custom_bindings=True, name="Print Job History")
		]


	def get_template_vars(self):
		return dict(
			apikey=self._settings.global_get(["api", "key"])
		)


	##~~ AssetPlugin mixin
	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/PrintJobHistory.js",
				"js/PrintJobHistory-APIClient.js",
				"js/PrintJobHistory-PluginCheckDialog.js",
				"js/PrintJobHistory-EditJobDialog.js",
				"js/PrintJobHistory-ImportDialog.js",
				"js/PrintJobHistory-StatisticDialog.js",
				"js/PrintJobHistory-SettingsCompareDialog.js",
				"js/PrintJobHistory-ComponentFactory.js",
				"js/quill.min.js",
				"js/jquery.datetimepicker.full.min.js",
				"js/TableItemHelper.js",
				"js/ResetSettingsUtilV3.js"],
			css=[
				"css/PrintJobHistory.css",
				"css/jquery.datetimepicker.min.css",
				"css/quill.snow.css"],
			less=["less/PrintJobHistory.less"]
		)


	##~~ Softwareupdate hook
	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			PrintJobHistory=dict(
				displayName="PrintJobHistory Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="OllisGit",
				repo="OctoPrint-PrintJobHistory",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/OllisGit/OctoPrint-PrintJobHistory/releases/latest/download/master.zip"
			)
		)


	# Increase upload-size (default 100kb) for uploading images
	def bodysize_hook(self, current_max_body_sizes, *args, **kwargs):
		return [("POST", r"/upload/", 20 * 1024 * 1024)]  # size in bytes


	# # For Streaming I need a special ResponseHandler
	# def route_hook(self, server_routes, *args, **kwargs):
	# 	from octoprint.server.util.tornado import LargeResponseHandler, UrlProxyHandler, path_validation_factory
	# 	from octoprint.util import is_hidden_path
	#
	# 	return [
	# 		# (r'myvideofeed', StreamHandler, dict(url=self._settings.global_get(["webcam", "snapshot"]),
	# 		# 									 as_attachment=True)),
	# 		(r"mysnapshot", UrlProxyHandler, dict(url=self._settings.global_get(["webcam", "snapshot"]),
	# 											 as_attachment=True))
	# 	]


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
# Name is used in the left Settings-Menue
__plugin_name__ = "PrintJobHistory"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PrintJobHistoryPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		# "octoprint.server.http.routes": __plugin_implementation__.route_hook,
		"octoprint.comm.protocol.gcode.sent": __plugin_implementation__.on_sentGCodeHook,
		"octoprint.server.http.bodysize": __plugin_implementation__.bodysize_hook,
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

# # filamentAnalyseDict = fileData["analysis"]["filament"]
# filamentAnalyseDict = {u'tool4': {u'volume': 185.20129656279946, u'length': 76997.75167999369},
#  u'tool3': {u'volume': 0.0, u'length': 0.0}, u'tool2': {u'volume': 0.0, u'length': 0.0},
#  u'tool1': {u'volume': 0.0, u'length': 0.0}, u'tool0': {u'volume': 0.0, u'length': 0.0}}
# #
# print (len(filamentAnalyseDict))
# for toolId in filamentAnalyseDict:
# 	# print(toolId)
# 	length = filamentAnalyseDict[toolId]["length"]
# 	volumne = filamentAnalyseDict[toolId]["volume"]
# 	print(toolId + " " + str(length))



