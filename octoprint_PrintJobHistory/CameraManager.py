# coding=utf-8
from __future__ import absolute_import

import requests
from io import open as i_open
#from PIL import ImageFile
from PIL import Image
from PIL import ImageFile

import os.path

class CameraManager(object):

	def __init__(self):

		self._streamUrl = None
		self._snapshotUrl = None

		self._snapshotStoragePath = None

	def initCamera(self, streamUrl, snapshotUrl, snapshotStoragePath, pluginBaseFolder):
		self._streamUrl = streamUrl
		self._snapshotUrl = snapshotUrl
		self._snapshotStoragePath = snapshotStoragePath
		self._pluginBaseFolder = pluginBaseFolder

	@staticmethod
	def buildSnapshotFilename(startDateTime):
		dateTimeThumb = startDateTime.strftime("%Y%m%d-%H%M%S") + ".jpg"
		return dateTimeThumb


	def buildSnapshotFilenameLocation(self, snapshotFilename, returnDefaultImage = True):
		if str(snapshotFilename).endswith(".jpg"):
			imageLocation = self._snapshotStoragePath + "/" + snapshotFilename
		else:
			imageLocation = self._snapshotStoragePath + "/" + snapshotFilename + ".jpg"

		if os.path.isfile(imageLocation):
			return imageLocation
		if returnDefaultImage:
			defaultImageSnapshotName = self._pluginBaseFolder + "/static/images/no-photo-icon.jpg"
			# defaultImageSnapshotName = self._pluginBaseFolder + "/static/images/no-image-icon.png"
			return defaultImageSnapshotName
		return imageLocation


	def deleteSnapshot(self, snapshotFilename):
		imageLocation= self.buildSnapshotFilenameLocation(snapshotFilename, False)

		if os.path.isfile(imageLocation):
			os.remove(imageLocation)

	def takeSnapshot(self, snapshotFilename):
		snapshotFilename = self._snapshotStoragePath + "/" +snapshotFilename+ ".jpg"
		snapshotThumbnailFilename = self._snapshotStoragePath + "/" +snapshotFilename+ "-thumbnail.jpg"

		response = requests.get(self._snapshotUrl, verify=not True,timeout=float(120))
		if response.status_code == requests.codes.ok:

			with i_open(snapshotFilename, 'wb') as snapshot_file:
				for chunk in response.iter_content(1024):
					if chunk:
						snapshot_file.write(chunk)
				print("image downloaded")

				# without this I get errors during load (happens in resize, where the image is actually loaded)
				ImageFile.LOAD_TRUNCATED_IMAGES = True

				# create a snapshot of the image
				# TODO not used at the moment
				# basewidth = 50
				# img = Image.open(snapshotFilename)
				# wpercent = (basewidth / float(img.size[0]))
				# hsize = int((float(img.size[1]) * float(wpercent)))
				# img = img.resize((basewidth, hsize), Image.ANTIALIAS)
				# img.save(snapshotThumbnailFilename, "JPEG")


calc = 5065.81694999996
# %.02fm"
# {:06.2f}
mystring = "{:.02f}m".format(calc)
print(mystring)

# print("hallo welt")
# url = "http://192.168.178.44:8080/shot.jpg"
# targetPath = "/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/"
# targetPathThumb = "/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/myImage-Thumb.jpg"
""""
cam = CameraManager()
cam.initWebCam(url, targetPath)
cam.createSnapshot(815, "bild.gcode")
"""
