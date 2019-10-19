# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import tornado
from flask import jsonify, request, make_response, Response, send_file
import flask

import json
import csv
import StringIO
import os

import cv2

from datetime import datetime

from octoprint_PrintJobHistory import CameraManager
from octoprint_PrintJobHistory.common import StringUtils
from octoprint_PrintJobHistory.common.SettingsKeys import SettingsKeys
from octoprint_PrintJobHistory.entities.FilamentEntity import FilamentEntity
from octoprint_PrintJobHistory.entities.TemperatureEntity import TemperatureEntity
from octoprint_PrintJobHistory.entities.PrintJobEntity import PrintJobEntity


class HtmlPageHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self, file_name="index.html"):
		pass

import time

class StreamHandler(tornado.web.RequestHandler):
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
        while True:
            # Generating images for mjpeg stream and wraps them into http resp
            # if self.get_argument('fd') == "true":
            #     img = cam.get_frame(True)
            # else:
            #     img = cam.get_frame(False)

            self.cap = cv2.VideoCapture("http://192.168.178.44:8080/video")
            # self.cap = cv2.VideoCapture("http://192.168.178.44:8080/shot.jpg")
            ret, frame = self.cap.read()
            img = frame

            ret, jpeg = cv2.imencode('.jpg', frame)
            data = jpeg.tobytes()
            # Record video
            # if self.is_record:
            #     if self.out == None:
            #         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            #         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))

            #     ret, frame = self.cap.read()
            #     if ret:
            #         self.out.write(frame)
            # else:
            #     if self.out != None:
            #         self.out.release()
            #         self.out = None

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

class PrintJobHistoryAPI(octoprint.plugin.BlueprintPlugin):

	# def get(self):
	# 	self.write("Hello, world")
	#
	def _convertPrintJobHistoryEntitiesToDict(self, allJobsEntities):
		result = []
		for job in allJobsEntities:
			jobAsDict = job.__dict__

			jobAsDict["printStartDateTimeFormatted"] =  job.printStartDateTime.strftime('%d.%m.%Y %H:%M')
			jobAsDict["printEndDateTimeFormatted"] =  job.printEndDateTime.strftime('%d.%m.%Y %H:%M')
			# Calculate duration
			duration = job.printEndDateTime - job.printStartDateTime
			durationFormatted = StringUtils.compactTimeDeltaFormatter(duration)
			jobAsDict["durationFormatted"] =  durationFormatted

			if job.filamentEntity != None:
				filamentDict = job.filamentEntity.__dict__
				del jobAsDict['filamentEntity']
				filamentDict["usedLength"] = "{:.02f}".format(filamentDict["usedLength"])
				filamentDict["usedWeight"] = "{:.02f}".format(filamentDict["usedWeight"])
				filamentDict["usedCost"] = "{:.02f}".format(filamentDict["usedCost"])
				filamentDict["calculatedLength"] = "{:.02f}".format(filamentDict["calculatedLength"])
				jobAsDict['filamentEntity'] = filamentDict

			if job.temperatureEntities != None and len(job.temperatureEntities) != 0:
				tempList = []

				for temp in job.temperatureEntities:
					tempDict = temp.__dict__
					tempList.append(tempDict)

				del jobAsDict["temperatureEntities"]
				jobAsDict["temperatureEntities"] = tempList

			jobAsDict["snapshotFilename"] = self._cameraManager.buildSnapshotFilename(job.printStartDateTime)

			result.append(jobAsDict)
		return result

	def _convertPrintJobHistoryEntityToList(self, jobAsDict):
		result = list()

		fields = ['userName', 'printStatusResult', 'printStartDateTimeFormatted', 'printEndDateTimeFormatted', 'durationFormatted', 'fileName', 'filePathName','fileSize','printedLayers', 'noteText']
		for field in fields:
			value = jobAsDict[field]
			result.append(value if value is not None else '-')
		# TODO Temp and Filament
		tempValue = str()
		for tempValues in jobAsDict["temperatureEntities"]:
			sensorName = tempValues["sensorName"]
			sensorValue = str(tempValues["sensorValue"])
			tempValue = " " + tempValue + sensorName + ":" + sensorValue
		result.append(tempValue)

		filamentAsDict = jobAsDict["filamentEntity"]
		fields = ['spoolName', 'material', 'diameter', 'usedLength', 'calculatedLength', 'usedWeight', 'usedCost']
		for field in fields:
			value = filamentAsDict[field]
			result.append(value if value is not None else '-')

		return result

	def _convertPrintJobHistoryEntitiesToCSV(self, allJobsDict):
		result = None
		si = StringIO.StringIO()

		headers = ['User', 'Result', 'Start Date', 'End Date', 'Duration', 'File Name', 'File Path','File Size', 'Layers', 'Note', 'Temperatures', 'Spool Name', 'Material', 'Diameter', 'Used Length', 'Calculated Length', 'Used Weight', 'Used Filament Cost']

		writer = csv.writer(si, quoting=csv.QUOTE_ALL)
		writer.writerow(headers)
		for job in allJobsDict:
			row = self._convertPrintJobHistoryEntityToList(job)
			writer.writerow(row)
		result = si.getvalue()

		return result

	def _convertJsonToPrintJobEntity(self, jsonData):
		printJobEntity = PrintJobEntity()
		printJobEntity.databaseId = self._getValueFromDictOrNone("databaseId", jsonData)
		printJobEntity.userName = self._getValueFromDictOrNone("userName", jsonData)

		printJobEntity.printStartDateTime = datetime.strptime(jsonData["printStartDateTimeFormatted"],"%d.%m.%Y %H:%M")
		printJobEntity.printEndDateTime = datetime.strptime(jsonData["printEndDateTimeFormatted"],"%d.%m.%Y %H:%M")

		printJobEntity.printStatusResult = self._getValueFromDictOrNone("printStatusResult", jsonData)
		printJobEntity.fileName = self._getValueFromDictOrNone("fileName", jsonData)
		printJobEntity.filePathName = self._getValueFromDictOrNone("filePathName", jsonData)
		printJobEntity.fileSize = self._getValueFromDictOrNone("fileSize", jsonData)
		printJobEntity.noteText = self._getValueFromDictOrNone("noteText", jsonData)
		printJobEntity.noteDelta = json.dumps(  self._getValueFromDictOrNone("noteDelta", jsonData) )
		printJobEntity.noteHtml =  self._getValueFromDictOrNone("noteHtml", jsonData)
		printJobEntity.printedLayers = self._getValueFromDictOrNone("printedLayers", jsonData)
		printJobEntity.printedHeight = self._getValueFromDictOrNone("printedHeight", jsonData)

		filamentEntity = FilamentEntity()
		filamentEntity.profileVendor = self._getValueFromDictOrNone("profileVendor", jsonData)
		filamentEntity.diameter = self._getValueFromDictOrNone("diameter", jsonData)
		filamentEntity.density = self._getValueFromDictOrNone("density", jsonData)
		filamentEntity.material = self._getValueFromDictOrNone("material", jsonData)
		filamentEntity.spoolName = self._getValueFromDictOrNone("spoolName", jsonData)
		filamentEntity.spoolCost = self._getValueFromDictOrNone("spoolCost", jsonData)
		filamentEntity.spoolCostUnit = self._getValueFromDictOrNone("spoolCostUnit", jsonData)
		filamentEntity.spoolWeight = self._getValueFromDictOrNone("spoolWeight", jsonData)
		filamentEntity.usedLength = self._getValueFromDictOrNone("usedLength", jsonData)
		filamentEntity.usedCost = self._getValueFromDictOrNone("usedCost", jsonData)
		filamentEntity.calculatedLength = self._getValueFromDictOrNone("calculatedLength", jsonData)
		filamentEntity.printjob_id = printJobEntity.databaseId
		printJobEntity.filamentEntity = filamentEntity

		# temperatureEntity = TemperatureEntity

		return printJobEntity

	def _getValueFromDictOrNone(self, key, values):
		if key in values:
			return values[key]
		return None

################################################### APIs

	def get_frame(self):

		self.cap = cv2.VideoCapture("http://192.168.178.44:8080/video")
		# self.cap = cv2.VideoCapture("http://192.168.178.44:8080/shot.jpg")
		ret, frame = self.cap.read()

		if ret:
			ret, jpeg = cv2.imencode('.jpg', frame)

			# Record video
			# if self.is_record:
			#     if self.out == None:
			#         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
			#         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))

			#     ret, frame = self.cap.read()
			#     if ret:
			#         self.out.write(frame)
			# else:
			#     if self.out != None:
			#         self.out.release()
			#         self.out = None

			return jpeg.tobytes()

		else:
			return None

	global_frame = None


	def video_stream(self):
		from time import sleep
		global video_camera
		global global_frame

		# while True:
		yield "1"
		sleep(4)
		yield "2"
		sleep(4)
		yield "3"
		# if video_camera == None:
		# 	video_camera = VideoCamera()

		# while True:
		# frame = self.get_frame()
		#
		# if frame != None:
		# 	global_frame = frame
		# 	yield (b'--frame\r\n'
		# 		   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
		# else:
		# 	yield (b'--frame\r\n'
		# 		   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

	from flask import stream_with_context, request, Response



	@octoprint.plugin.BlueprintPlugin.route('/stream')
	def streamed_response(self):


		# app = tornado.web.Application([
		# 	(r'/', HtmlPageHandler),
		# 	(r'/videofeed', StreamHandler)
		# ])
		# app.listen(9090)
		# pass

		def generate():
			from time import sleep
			yield "1"
			sleep(4)
			yield "2"
			sleep(4)
			yield "3"
		return Response(generate(),mimetype='text/event-stream')

	@octoprint.plugin.BlueprintPlugin.route("/myvideo")
	def video_feed(self):
		# return the response generated along with the specific media
		# type (mime type)
		return Response(self.video_stream(),
						mimetype="text/plain")
						# mimetype='multipart/x-mixed-replace; boundary=frame')


	@octoprint.plugin.BlueprintPlugin.route("/printJobSnapshot/<string:snapshotFilename>", methods=["GET"])
	def get_snapshot(self, snapshotFilename):
		absoluteFilename = self._cameraManager.buildSnapshotFilenameLocation(snapshotFilename)
		return send_file(absoluteFilename, mimetype='image/jpg')


	@octoprint.plugin.BlueprintPlugin.route("/takeSnapshot/<string:snapshotFilename>", methods=["PUT"])
	def put_snapshot(self, snapshotFilename):

		self._cameraManager.takeSnapshot(snapshotFilename)

		return flask.jsonify({
			"snapshotFilename": snapshotFilename
		})


	@octoprint.plugin.BlueprintPlugin.route("/upload/snapshot/<string:snapshotFilename>", methods=["POST"])
	def post_snapshot(self, snapshotFilename):

		input_name = "file"
		input_upload_path = input_name + "." + self._settings.global_get(["server", "uploads", "pathSuffix"])

		if input_upload_path in flask.request.values:
			# file to restore was uploaded
			sourceLocation = flask.request.values[input_upload_path]
			targetLocation = self._cameraManager.buildSnapshotFilenameLocation(snapshotFilename, False)
			os.rename(sourceLocation, targetLocation)
			pass

		return flask.jsonify({
			"snapshotFilename": snapshotFilename
		})	\

	@octoprint.plugin.BlueprintPlugin.route("/deleteSnapshotImage/<string:snapshotFilename>", methods=["DELETE"])
	def delete_snapshot(self, snapshotFilename):

		self._cameraManager.deleteSnapshot(snapshotFilename)

		# input_name = "file"
		# input_upload_path = input_name + "." + self._settings.global_get(["server", "uploads", "pathSuffix"])
		#
		# if input_upload_path in flask.request.values:
		# 	# file to restore was uploaded
		# 	sourceLocation = flask.request.values[input_upload_path]
		# 	targetLocation = self._cameraManager.buildSnapshotFilenameLocation(snapshotFilename)
		# 	os.rename(sourceLocation, targetLocation)
		# 	pass

		return flask.jsonify({
			"snapshotFilename": snapshotFilename
		})


	@octoprint.plugin.BlueprintPlugin.route("/exportPrintJobHistory/<string:exportType>", methods=["GET"])
	def exportPrintJobHistoryData(self, exportType):

		if exportType == "CSV":
			allJobsEntities = self._databaseManager.loadAllPrintJobs()
			allJobsDict = self._convertPrintJobHistoryEntitiesToDict(allJobsEntities)

			csvContent = self._convertPrintJobHistoryEntitiesToCSV(allJobsDict)

			response = flask.make_response(csvContent)
			response.headers["Content-type"] = "text/csv"
			response.headers["Content-Disposition"] = "attachment; filename=OctoprintPrintJobHistory.csv" # TODO add timestamp


			return response
		else:
			print("BOOOMM not supported type")

		pass

	@octoprint.plugin.BlueprintPlugin.route("/loadPrintJobHistory", methods=["GET"])
	def get_printjobhistory(self):
		allJobsEntities = self._databaseManager.loadAllPrintJobs()
		allJobsAsDict = self._convertPrintJobHistoryEntitiesToDict(allJobsEntities)

		return flask.jsonify(allJobsAsDict)


	@octoprint.plugin.BlueprintPlugin.route("/removePrintJob/<int:databaseId>", methods=["DELETE"])
	def delete_printjob(self, databaseId):
		allJobsEntities = self._databaseManager.deletePrintJob(databaseId)
		allJobsAsDict = self._convertPrintJobHistoryEntitiesToDict(allJobsEntities)
		# TODO delete snapshot from disc as well. CameraManager.deleteSnapshot(databaseId)
		return flask.jsonify(allJobsAsDict)


	@octoprint.plugin.BlueprintPlugin.route("/updatePrintJob/<int:databaseId>", methods=["PUT"])
	def put_printjob(self, databaseId):

		jsonData = request.json
		printJobEntity = self._convertJsonToPrintJobEntity(jsonData)

		self._databaseManager.insertNewPrintJob(printJobEntity)

		response = self.get_printjobhistory()
		return response


	@octoprint.plugin.BlueprintPlugin.route("/deactivatePluginCheck", methods=["PUT"])
	def put_pluginDependencyCheck(self):
		self._settings.setBoolean([SettingsKeys.SETTINGS_KEY_PLUGIN_DEPENDENCY_CHECK], False)
		self._settings.save()

		return flask.jsonify([])





datetime_str = '09/19/18 13:55:26'
datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')



p = PrintJobEntity()
p.userName = "Olaf"
#p.fileName = "3DBenchy.gcode"
#p.filePathName = "/path/3DBenchy.gcode"
#p.fileSize = "123"
#p.printStartDateTime = "datetime_object"
#p.printEndDateTime = "datetime_object"
#p.printStatusResult = "fail"
#p.printedLayers = "13/1234"

# p.insertOrUpdate(cursor)
# newP = p.load(cursor, 2)
p.databaseId = "123"
#p.filamentEntity = "321"
#p.printedHeight = "myNote"
#p.temperatureBed = "myNote"
#p.temperatureNozzel = "myNote"

a = json.dumps(p.__dict__)

print(a)


