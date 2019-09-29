# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
from octoprint.events import Events

import os
import datetime


from .entities.PrintJobEntity import PrintJobEntity
from .entities.FilamentEntity import FilamentEntity
from .DatabaseManager import DatabaseManager

################## SETTINGS - KEYS
SETTINGS_KEY_ACTIVATED = "activated"

class PrintJobHistoryPlugin(octoprint.plugin.SettingsPlugin,
                            octoprint.plugin.AssetPlugin,
                            octoprint.plugin.TemplatePlugin,
							octoprint.plugin.StartupPlugin,
							octoprint.plugin.EventHandlerPlugin,
							octoprint.plugin.SimpleApiPlugin):



	def initialize(self):
		self._preHeatPluginImplementation = None
		self._filamentManagerPluginImplementation = None
		self._displayLayerProgressPluginImplementation = None

		self._databaseManager = DatabaseManager()
		databasePath = os.path.join(self.get_plugin_data_folder(), "printJobHistory.db")
		self._databaseManager.initDatabase(databasePath)

		self._currentPrintJobEntity = None


	################################################################################################## private functions
	def _checkForMissingPluginInfos(self):
		missingMessage = ""
		if self._preHeatPluginImplementation == None:
			missingMessage = "<li>PreHeat</li>"

		if self._filamentManagerPluginImplementation == None:
			missingMessage = missingMessage + "<li>Filamentmanager</li>"

		if self._displayLayerProgressPluginImplementation == None:
			missingMessage = missingMessage + "<li>DisplayLayeerProgress</li>"

		if missingMessage != "":
			missingMessage = "<ul>" + missingMessage + "</ul>"

			self._plugin_manager.send_plugin_message(self._identifier,
													 dict(action = "missingPlugin",
														  message = missingMessage))

	def _createAndAssignFilamentEntity(self, printJob, payload):
		filemanentEntity  = FilamentEntity()

		fileData = self._file_manager.get_metadata(payload["origin"], payload["file"])
		filamentLength = None
		if "analysis" in fileData:
			if "filament" in fileData["analysis"]:
				if "tool0" in fileData["analysis"]["filament"]:
					filamentLength = fileData["analysis"]["filament"]["tool0"]['length']

		filemanentEntity.usedLength = filamentLength

		if self._filamentManagerPluginImplementation != None:
			selectedSpool = self._filamentManagerPluginImplementation.filamentManager.get_all_selections(self._filamentManagerPluginImplementation.client_id)
			if  selectedSpool != None:
				spoolData = selectedSpool[0]["spool"]
				spoolName = spoolData["name"]
				spoolCost = spoolData["cost"]
				spoolWeight = spoolData["weight"]

				profileData = selectedSpool[0]["spool"]["profile"]
				diameter = profileData["diameter"]
				material = profileData["material"]
				vendor = profileData["vendor"]
				density = profileData["density"]

				filemanentEntity.spoolName = spoolName
				filemanentEntity.spoolCost = spoolCost
				filemanentEntity.spoolWeight = spoolWeight

				filemanentEntity.profileVendor = vendor
				filemanentEntity.diameter = diameter
				filemanentEntity.density = density
				filemanentEntity.material = material

		printJob.filamentEntity = filemanentEntity
		pass

	def _updatePrintJobEntityWithLayerInfos(self, payload):
		totalLayers = payload["totalLayer"]
		currentLayer = payload["currentLayer"]
		self._currentPrintJobEntity.printedLayers = currentLayer + "/" + totalLayers

	def _createPrintJobEntity(self, payload):
		self._currentPrintJobEntity = PrintJobEntity()
		self._currentPrintJobEntity.printStartDateTime = datetime.datetime.now()
		self._currentPrintJobEntity.fileName = payload["filename"]
		self._currentPrintJobEntity.filePathName = payload["path"]
		self._currentPrintJobEntity.userName = payload["owner"]
		self._currentPrintJobEntity.fileSize = payload["size"]

		if self._preHeatPluginImplementation != None:
			filename = payload["path"]
			destination = payload["origin"]
			path_on_disk = octoprint.server.fileManager.path_on_disk(destination, filename)

			preHeatTemperature = self._preHeatPluginImplementation.read_temperatures_from_file(path_on_disk)
			nozzel = preHeatTemperature["tool0"]
			bed = preHeatTemperature["bed"]
			self._currentPrintJobEntity.temperatureNozzel = nozzel
			self._currentPrintJobEntity.temperatureBed = bed
			pass

	def _printJobFinished(self, printStatus, payload):

		self._currentPrintJobEntity.printEndDateTime = datetime.datetime.now()
		self._currentPrintJobEntity.printStatusResult = printStatus

		# TODO take a picture
		# FilamentInformations e.g. length
		self._createAndAssignFilamentEntity(self._currentPrintJobEntity, payload)

		# store everything in the database
		self._databaseManager.insertNewPrintJob(self._currentPrintJobEntity)

	######################################################################################### Hooks and public functions

	def on_after_startup(self):
		value = self._settings.global_get(["webcam", "snapshot"])
		plugin = self._plugin_manager.plugins["preheat"]
		if plugin != None and plugin.enabled == True:
			self._preHeatPluginImplementation = plugin.implementation
		plugin = self._plugin_manager.plugins["filamentmanager"]
		if plugin != None and plugin.enabled == True:
			self._filamentManagerPluginImplementation = plugin.implementation
		plugin = self._plugin_manager.plugins["DisplayLayerProgress"]
		if plugin != None and plugin.enabled == True:
			self._displayLayerProgressPluginImplementation = plugin.implementation

	def on_event(self, event, payload):

		if Events.CLIENT_OPENED == event:
			# Check if all needed Plugins are available, if not modale dilog to User
			self._checkForMissingPluginInfos()

		elif Events.PRINT_STARTED == event:
			self._createPrintJobEntity(payload)

		elif "DisplayLayerProgress_layerChanged" == event:
			self._updatePrintJobEntityWithLayerInfos(payload)


		elif Events.PRINT_DONE == event:
			self._printJobFinished("success", payload)
		elif Events.PRINT_FAILED == event:
			self._printJobFinished("failed", payload)
		elif Events.PRINT_CANCELLED == event:
			self._printJobFinished("canceled", payload)

		pass

	def on_settings_save(self, data):
		# default save function
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)


	# to allow the frontend to trigger an GET call
	def on_api_get(self, request):
		if len(request.values) != 0:
			action = request.values["action"]
		pass

	##~~ SettingsPlugin mixin
	def get_settings_defaults(self):
		return dict(
			# put your plugin's default settings here
		)
	##~~ TemplatePlugin mixin
	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=True)
		]

	##~~ AssetPlugin mixin
	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/PrintJobHistory.js"],
			css=["css/PrintJobHistory.css"],
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


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "PrintJobHistory Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PrintJobHistoryPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}



