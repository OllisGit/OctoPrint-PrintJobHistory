# coding=utf-8
from __future__ import absolute_import

import requests
from io import open as i_open
#from PIL import ImageFile
from PIL import Image
from PIL import ImageFile

class WebCamHelper(object):

	def __init__(self):
		self._snapshotUrl = None
		self._snapshotStoragePath = None

	def initWebCam(self, snapshotUrl, snapshotStoragePath):
		self._snapshotUrl = snapshotUrl
		self._snapshotStoragePath = snapshotStoragePath

	def createSnapshot(self, printjobId, gcodeFilename):

		snapshotFilename = self._snapshotStoragePath + str(printjobId) + gcodeFilename + ".jpg"
		snapshotThumbnailFilename = self._snapshotStoragePath + str(printjobId) + gcodeFilename + "-thumbnail.jpg"
		response = requests.get(self._snapshotUrl, verify=not True,timeout=float(120))
		if response.status_code == requests.codes.ok:

			with i_open(snapshotFilename, 'wb') as snapshot_file:
				for chunk in response.iter_content(1024):
					if chunk:
						snapshot_file.write(chunk)
				print("image downloaded")

				# without this I get errors during load (happens in resize, where the image is actually loaded)
				ImageFile.LOAD_TRUNCATED_IMAGES = True

				# create a thumbnail of the image
				basewidth = 50
				img = Image.open(snapshotFilename)
				wpercent = (basewidth / float(img.size[0]))
				hsize = int((float(img.size[1]) * float(wpercent)))
				img = img.resize((basewidth, hsize), Image.ANTIALIAS)
				img.save(snapshotThumbnailFilename, "JPEG")

print("hallo welt")
url = "http://192.168.178.44:8080/shot.jpg"
targetPath = "/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/"
targetPathThumb = "/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/myImage-Thumb.jpg"

cam = WebCamHelper()
cam.initWebCam(url, targetPath)
cam.createSnapshot(815, "bild.gcode")

