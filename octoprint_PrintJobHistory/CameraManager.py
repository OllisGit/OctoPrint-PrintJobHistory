# coding=utf-8
from __future__ import absolute_import

import shutil
import threading
import datetime
import requests
from io import open as i_open
from PIL import Image
from PIL import ImageFile

import logging
import os.path
import os
import zipfile
from io import StringIO

SNAPSHOT_BACKUP_FILENAME = "snapshots-backup-{timestamp}.zip"

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
		self._logger.info("Snapshot-Folder:"+snapshotStoragePath)

		self._snapshotStoragePath = snapshotStoragePath
		self._pluginDataBaseFolder = pluginDataBaseFolder
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


	def backupAllSnapshots(self, targetBackupFolder):

		now = datetime.datetime.now()
		currentDate = now.strftime("%Y%m%d-%H%M")
		backupZipFileName = SNAPSHOT_BACKUP_FILENAME.format(timestamp=currentDate)
		backupZipFilePath = os.path.join(targetBackupFolder, backupZipFileName)

		self._createZipFile(backupZipFilePath, self._snapshotStoragePath)

		return backupZipFilePath

	def reCreateSnapshotFolder(self):
		# delete current folder and recreate the folder

		shutil.rmtree(self._snapshotStoragePath)
		os.makedirs(self._snapshotStoragePath)


	def _createZipFile(self, zipname, path):
		# function to create a zip file
		# Parameters: zipname - name of the zip file; path - name of folder/file to be put in zip file

		zipf = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
		zipf.setpassword(b"password")  # if you want to set password to zipfile

		# checks if the path is file or directory
		if os.path.isdir(path):
			for files in os.listdir(path):
				zipf.write(os.path.join(path, files), files)

		elif os.path.isfile(path):
			zipf.write(os.path.join(path), path)
		zipf.close()


	# def _zipdir(self, path, zipfile_handle):
	# 	# walk over all files an add it to the zip
	# 	for root, dirs, files in os.walk(path):
	# 		for file in files:
	# 			# zipfile_handle.write(os.path.join(root, file))
	# 			zipfile_handle.write(os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))


	def takeSnapshot(self, snapshotFilename, sendErrorMessageToClientFunction):

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

		try:
			response = requests.get(snapshotUrl, verify=not True,timeout=float(60))
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
		except (Exception) as error:
			sendErrorMessageToClientFunction("Take Snapshot", "Unable to get snapshot from URL: " + snapshotUrl)
			self._logger.error(error)

	def takeSnapshotAsync(self, snapshotFilename, sendErrorMessageToClientFunction):
		thread = threading.Thread(name='TakeSnapshot', target=self.takeSnapshot, args=(snapshotFilename, sendErrorMessageToClientFunction,))
		thread.daemon = True
		thread.start()


	def takePluginThumbnail(self, snapshotFilename, thumbnailLocation):
		if str(snapshotFilename).endswith(".jpg"):
			snapshotFilename = self._snapshotStoragePath + "/" + snapshotFilename
		else:
			snapshotFilename = self._snapshotStoragePath + "/" + snapshotFilename + ".jpg"

		# clear timestamp in path
		thumbnailLocation = thumbnailLocation.split("?", 1)[0]

		# url path in format plugin/{plugin_folder}/thumbnail/{image_path}
		splitPath = thumbnailLocation.split("/", 3)

		if (len(splitPath) != 4):
			self._logger.warning("Can not split thumbnail path '" + thumbnailLocation + "'")
			return

		pluginFolder = splitPath[1]
		thumbnailName = splitPath[3]

		thumbnailLocation = self._pluginDataBaseFolder + "/../" + pluginFolder + "/" + thumbnailName

		if os.path.isfile(thumbnailLocation):
			# Convert png to jpg and save in printjobhistory storage

			self._logger.info("Try converting thumbnail '" + thumbnailLocation + "' to '" + snapshotFilename + "'")

			im = Image.open(thumbnailLocation)
			rgb_im = im.convert('RGB')
			rgb_im.save(snapshotFilename)

			self._logger.info("Converting successfull!")

		else:
			self._logger.warning("Thumbnail doesn't exists in: '"+thumbnailLocation+"'")

	def takeThumbnailAsync(self, snapshotFilename, thumbnailLocation):
		thread = threading.Thread(name='TakeThumbnail', target=self.takePluginThumbnail, args=(snapshotFilename,thumbnailLocation))
		thread.daemon = True
		thread.start()
