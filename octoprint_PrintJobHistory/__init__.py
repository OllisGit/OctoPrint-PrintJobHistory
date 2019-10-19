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
import math

from .common.SettingsKeys import SettingsKeys
from .api.PrintJobHistoryAPI import PrintJobHistoryAPI

from .entities.PrintJobEntity import PrintJobEntity
from .entities.FilamentEntity import FilamentEntity
from .entities.TemperatureEntity import TemperatureEntity
from .DatabaseManager import DatabaseManager
from .CameraManager import CameraManager


class PrintJobHistoryPlugin(
							PrintJobHistoryAPI,
							octoprint.plugin.SettingsPlugin,
                            octoprint.plugin.AssetPlugin,
                            octoprint.plugin.TemplatePlugin,
							octoprint.plugin.StartupPlugin,
							octoprint.plugin.EventHandlerPlugin,
							#octoprint.plugin.SimpleApiPlugin
							):


	def initialize(self):
		self._preHeatPluginImplementation = None
		self._filamentManagerPluginImplementation = None
		self._displayLayerProgressPluginImplementation = None

		pluginDataBaseFolder = self.get_plugin_data_folder()

		self._databaseManager = DatabaseManager()
		databasePath = os.path.join(pluginDataBaseFolder, "printJobHistory.db")
		self._databaseManager.initDatabase(databasePath)

		pluginBaseFolder = self._basefolder
		self._cameraManager = CameraManager()
		streamUrl = self._settings.global_get(["webcam", "stream"])
		snapshotUrl =  self._settings.global_get(["webcam", "snapshot"])

		snapshotStorage = pluginDataBaseFolder + "/snapshots"
		if not os.path.exists(snapshotStorage):
			os.makedirs(snapshotStorage)

		self._cameraManager.initCamera(streamUrl, snapshotUrl, snapshotStorage, pluginBaseFolder)


		self._currentPrintJobEntity = None


	################################################################################################## private functions
	def _sendDataToClient(self, payloadDict):

		self._plugin_manager.send_plugin_message(self._identifier,
												 payloadDict)


	def _checkForMissingPluginInfos(self):
		missingMessage = ""
		if self._preHeatPluginImplementation == None:
			missingMessage = "<li>PreHeat</li>"

		if self._filamentManagerPluginImplementation == None:
			missingMessage = missingMessage + "<li>FilamentManager</li>"

		if self._displayLayerProgressPluginImplementation == None:
			missingMessage = missingMessage + "<li>DisplayLayerProgress</li>"

		if missingMessage != "":
			missingMessage = "<ul>" + missingMessage + "</ul>"
			self._sendDataToClient(dict(action="missingPlugin",
									    message=missingMessage))


	# Graps all informations for the filament attributes
	def _createAndAssignFilamentEntity(self, printJob, payload):
		filemanentEntity  = FilamentEntity()

		fileData = self._file_manager.get_metadata(payload["origin"], payload["file"])
		filamentLength = None
		if "analysis" in fileData:
			if "filament" in fileData["analysis"]:
				if "tool0" in fileData["analysis"]["filament"]:
					filamentLength = fileData["analysis"]["filament"]["tool0"]['length']

		filemanentEntity.calculatedLength = filamentLength

		if self._filamentManagerPluginImplementation != None:

			filemanentEntity.usedLength = self._filamentManagerPluginImplementation.filamentOdometer.totalExtrusion[0]
			selectedSpool = self._filamentManagerPluginImplementation.filamentManager.get_all_selections(self._filamentManagerPluginImplementation.client_id)
			if  selectedSpool != None and len(selectedSpool) > 0:
				spoolData = selectedSpool[0]["spool"]
				spoolName = spoolData["name"]
				spoolCost = spoolData["cost"]
				spoolCostUnit = self._filamentManagerPluginImplementation._settings.get(["currencySymbol"])
				spoolWeight = spoolData["weight"]

				profileData = selectedSpool[0]["spool"]["profile"]
				diameter = profileData["diameter"]
				material = profileData["material"]
				vendor = profileData["vendor"]
				density = profileData["density"]

				filemanentEntity.spoolName = spoolName
				filemanentEntity.spoolCost = spoolCost
				filemanentEntity.spoolCostUnit = spoolCostUnit
				filemanentEntity.spoolWeight = spoolWeight

				filemanentEntity.profileVendor = vendor
				filemanentEntity.diameter = diameter
				filemanentEntity.density = density
				filemanentEntity.material = material

				radius = diameter / 2;
				volume = filemanentEntity.usedLength * math.pi * radius * radius / 1000;
				usedWeight = volume * density

				filemanentEntity.usedWeight = usedWeight
				filemanentEntity.usedCost = spoolCost / spoolWeight * usedWeight

		printJob.filamentEntity = filemanentEntity
		pass

	def _updatePrintJobEntityWithLayerHeightInfos(self, payload):
		totalLayers = payload["totalLayer"]
		currentLayer = payload["currentLayer"]
		self._currentPrintJobEntity.printedLayers = currentLayer + "/" + totalLayers

		totalHeightWithExtrusion = payload["totalHeightWithExtrusion"]
		currentHeight = payload["currentHeight"]
		self._currentPrintJobEntity.printedHeight = currentHeight + "/" + totalHeightWithExtrusion

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
			tempEntity = TemperatureEntity()
			tempEntity.sensorName = "tool0"
			tempEntity.sensorValue = nozzel
			self._currentPrintJobEntity.temperatureEntities.append(tempEntity)

			if "bed" in preHeatTemperature:
				bed = preHeatTemperature["bed"]
				tempEntity = TemperatureEntity()
				tempEntity.sensorName = "bed"
				tempEntity.sensorValue = bed
				self._currentPrintJobEntity.temperatureEntities.append(tempEntity)

			#self._currentPrintJobEntity.temperatureNozzel = nozzel
			#self._currentPrintJobEntity.temperatureBed = bed
			pass

	def _printJobFinished(self, printStatus, payload):
		# HACK after canceled a failed event is send, so if currentJob is already stored -> do nothing
		if self._currentPrintJobEntity.databaseId != None:
			return

		self._currentPrintJobEntity.printEndDateTime = datetime.datetime.now()
		self._currentPrintJobEntity.printStatusResult = printStatus

		# TODO take a picture
		# FilamentInformations e.g. length
		self._createAndAssignFilamentEntity(self._currentPrintJobEntity, payload)

		# store everything in the database
		self._databaseManager.insertNewPrintJob(self._currentPrintJobEntity)

		# inform client for a reload
		self._sendDataToClient(dict(action="printFinished"
									))



	######################################################################################### Hooks and public functions

	def on_after_startup(self):

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
			if self._settings.get_boolean([SettingsKeys.SETTINGS_KEY_PLUGIN_DEPENDENCY_CHECK]):
				self._checkForMissingPluginInfos()

		elif Events.PRINT_STARTED == event:
			self._createPrintJobEntity(payload)

		elif "DisplayLayerProgress_layerChanged" == event or event == "DisplayLayerProgress_heightChanged":
			self._updatePrintJobEntityWithLayerHeightInfos(payload)

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

		settings = dict()
		settings[SettingsKeys.SETTINGS_KEY_PLUGIN_DEPENDENCY_CHECK] = False
		return settings
#		return dict(
#			# put your plugin's default settings here
#			pluginCheckActivated = True
#		)


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
			js=["js/PrintJobHistory.js",
				"js/PrintJobHistory-APIClient.js",
				"js/PrintJobHistory-PluginCheckDialog.js",
				"js/PrintJobHistory-EditJobDialog.js",
				"js/quill.min.js"],
			css=["css/PrintJobHistory.css",
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
		return [("POST", r"/upload/", 5 * 1024 * 1024)]	# size in bytes

	# For Streaming I need a special ResponseHandler
	def route_hook(self, server_routes, *args, **kwargs):
		from octoprint.server.util.tornado import LargeResponseHandler, UrlProxyHandler, path_validation_factory
		from octoprint.util import is_hidden_path

		return [
			(r'myvideofeed', StreamHandler, dict(url=self._settings.global_get(["webcam", "snapshot"]),
													as_attachment=True)),
			(r"myforward", UrlProxyHandler, dict(url=self._settings.global_get(["webcam", "snapshot"]),
													as_attachment=True))
		]

import cv2
import tornado
import time
import imutils
from pyzbar import pyzbar

class StreamHandler(tornado.web.RequestHandler):

	def initialize(self, url=None, as_attachment=False, basename=None, access_validation=None):
		tornado.web.RequestHandler.initialize(self)
		self._url = url
		self._as_attachment = as_attachment
		self._basename = basename
		self._access_validation = access_validation

	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self):
		ioloop = tornado.ioloop.IOLoop.current()

		self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
		self.set_header( 'Pragma', 'no-cache')
		self.set_header( 'Content-Type', 'multipart/x-mixed-replace;boundary=--jpgboundary')
		self.set_header('Connection', 'close')

		self.served_image_timestamp = time.time()
		my_boundary = "--jpgboundary"
		found = set()
		while True:
			# Generating images for mjpeg stream and wraps them into http resp
			# if self.get_argument('fd') == "true":
			#     img = cam.get_frame(True)
			# else:
			#     img = cam.get_frame(False)

			self.cap = cv2.VideoCapture("http://192.168.178.44:8080/video")
			# self.cap = cv2.VideoCapture("http://192.168.178.44:8080/shot.jpg")
			ret, frame = self.cap.read()

			frameData = frame
			frameData = imutils.resize(frameData, width=600)
			barcodes = pyzbar.decode(frameData)
			for barcode in barcodes:
				(x, y, width, height) = barcode.rect
				cv2.rectangle(frameData, (x, y), (x + width, y + height), (0, 0, 255), 2)
				barcodeData = barcode.data.decode("utf-8")
				barcodeType = barcode.type
				textData = "{} ({})".format(barcodeData, barcodeType)
				cv2.putText(frameData, textData, (x, y - 10),
							cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
				if barcodeData not in found:
					print("BBBBBBBEEEEEEEEEEPPPPPPPP")


			img = frameData

			ret, jpeg = cv2.imencode('.jpg', frameData)
			data = jpeg.tobytes()

			interval = 0.1
			if self.served_image_timestamp + interval < time.time():
				self.write(my_boundary)
				self.write("Content-type: image/jpeg\r\n")
				self.write("Content-length: %s\r\n\r\n" % len(data))
				self.write(data)
				self.served_image_timestamp = time.time()
				yield tornado.gen.Task(self.flush)
			else:
				yield tornado.gen.Task(ioloop.add_timeout, ioloop.time() + interval)





# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "PrintJobHistory Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PrintJobHistoryPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.server.http.routes": __plugin_implementation__.route_hook,
		"octoprint.server.http.bodysize": __plugin_implementation__.bodysize_hook,
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}



