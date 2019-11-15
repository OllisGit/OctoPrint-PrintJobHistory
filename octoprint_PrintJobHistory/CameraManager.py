# coding=utf-8
from __future__ import absolute_import

import threading

import requests
from io import open as i_open
from PIL import Image
from PIL import ImageFile

import logging
import os.path
import StringIO


class CameraManager(object):

	def __init__(self, parentLogger):
		self._logger = logging.getLogger(parentLogger.name + "." + self.__class__.__name__)
		self._streamUrl = None
		self._snapshotUrl = None

		self._snapshotStoragePath = None

	@staticmethod
	def doSomething():
		print("Hello World")

	@staticmethod
	def buildSnapshotFilename(startDateTime):
		dateTimeThumb = startDateTime.strftime("%Y%m%d-%H%M%S") + ".jpg"
		return dateTimeThumb


	# def initCamera(self, enabled, streamUrl, snapshotUrl, snapshotStoragePath, pluginBaseFolder, rotate = None, flipH = None, flipV = None):
	def initCamera(self, pluginDataBaseFolder, pluginBaseFolder, globalSettings):
		self._logger.info("Init CameraManager")

		snapshotStoragePath = pluginDataBaseFolder + "/snapshots"
		if not os.path.exists(snapshotStoragePath):
			os.makedirs(snapshotStoragePath)
		self._logger.info("Snapshot-Folderr:"+snapshotStoragePath)

		self._snapshotStoragePath = snapshotStoragePath
		self._pluginBaseFolder = pluginBaseFolder
		self._globalSettings = globalSettings

		self._logger.info("Done CameraMenager")


	def getSnapshotFileLocation(self):
		return self._snapshotStoragePath


	# NOT WORKING IN 1.3.10
	# def isVideoStreamEnabled(self):
	# 	self._globalSettings.global_get(["webcam", "webcamEnabled"])


	def buildSnapshotFilenameLocation(self, snapshotFilename, returnDefaultImage = True):
		if str(snapshotFilename).endswith(".jpg"):
			imageLocation = self._snapshotStoragePath + "/" + snapshotFilename
		else:
			imageLocation = self._snapshotStoragePath + "/" + snapshotFilename + ".jpg"

		if os.path.isfile(imageLocation):
			return imageLocation
		if returnDefaultImage:
			# defaultImageSnapshotName = self._pluginBaseFolder + "/static/images/no-photo-icon.jpg"
			defaultImageSnapshotName = self._pluginBaseFolder + "/static/images/no-image-icon-big.png"
			return defaultImageSnapshotName
		return imageLocation


	def deleteSnapshot(self, snapshotFilename):
		imageLocation= self.buildSnapshotFilenameLocation(snapshotFilename, False)

		if os.path.isfile(imageLocation):
			os.remove(imageLocation)
		self._logger.info("Snapshot '" + imageLocation + "' deleted")

	def takeSnapshot(self, snapshotFilename):
		if str(snapshotFilename).endswith(".jpg"):
			snapshotFilename = self._snapshotStoragePath + "/" +snapshotFilename
		else:
			snapshotFilename = self._snapshotStoragePath + "/" +snapshotFilename + ".jpg"

		snapshotThumbnailFilename = self._snapshotStoragePath + "/" +snapshotFilename+ "-thumbnail.jpg"


		# streamUrl = self._settings.global_get(["webcam", "stream"])
		snapshotUrl =  self._globalSettings.global_get(["webcam", "snapshot"])
		self._logger.info("Try taking snapshot '" + snapshotFilename + "' from '" + snapshotUrl + "'")
		if (snapshotUrl == None or snapshotUrl == ""):
			return

		rotate = self._globalSettings.global_get(["webcam", "rotate90"])
		flipH = self._globalSettings.global_get(["webcam", "flipH"])
		flipV = self._globalSettings.global_get(["webcam", "flipV"])

		response = requests.get(snapshotUrl, verify=not True,timeout=float(120))
		if response.status_code == requests.codes.ok:
			self._logger.info("Process snapshot image")
			with i_open(snapshotFilename, 'wb') as snapshot_file:
				for chunk in response.iter_content(1024):
					if chunk:
						snapshot_file.write(chunk)

			# adjust orientation
			if flipH or flipV or rotate:
				image = Image.open(snapshotFilename)
				if flipH:
					image = image.transpose(Image.FLIP_LEFT_RIGHT)
				if flipV:
					image = image.transpose(Image.FLIP_TOP_BOTTOM)
				if rotate:
					# image = image.transpose(Image.ROTATE_270)
					image = image.transpose(Image.ROTATE_90)
				# output = StringIO.StringIO()
				image.save(snapshotFilename, format="JPEG")
				self._logger.info("Image stored to '" + snapshotFilename + "'")
				# data = output.getvalue()
				# output.close()

			# without this I get errors during load (happens in resize, where the image is actually loaded)
			ImageFile.LOAD_TRUNCATED_IMAGES = True

			############################################## create a snapshot of the image
			# TODO not used at the moment
			# basewidth = 50
			# img = Image.open(snapshotFilename)
			# wpercent = (basewidth / float(img.size[0]))
			# hsize = int((float(img.size[1]) * float(wpercent)))
			# img = img.resize((basewidth, hsize), Image.ANTIALIAS)
			# img.save(snapshotThumbnailFilename, "JPEG")
		else:
			self._logger.error("Invalid response code from snapshot-url. Code:" + str(response.status_code))

	def takeSnapshotAsync(self, snapshotFilename):
		thread = threading.Thread(name='TakeSnapshot', target=self.takeSnapshot, args=(snapshotFilename,))
		thread.daemon = True
		thread.start()
