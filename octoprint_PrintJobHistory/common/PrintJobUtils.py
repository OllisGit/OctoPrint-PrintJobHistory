# coding=utf-8
from __future__ import absolute_import
from octoprint.filemanager import FileDestinations
from octoprint_PrintJobHistory.common import StringUtils

def isPrintJobReprintable(fileManager, fileOrigin, filePathName, fileName):
	resultPrintJobPrintable = {}

	isRePrintable = False
	fullFileLocation = ""
	filePath = filePathName if StringUtils.isNotEmpty(filePathName) else fileName

	if (fileOrigin == None):
		# could be during csv import, assumption it is local
		fileOrigin = FileDestinations.LOCAL

	if (fileOrigin == FileDestinations.LOCAL):
		# local filesystem
		fullFileLocation = fileManager.path_on_disk(fileOrigin, filePath)
		isRePrintable = _isFileReadable(fullFileLocation)
		pass
	else:
		# sd-card
		# - no readable check (positiv thinking)
		isRePrintable = True
		fullFileLocation = fileOrigin + ":/" + filePath

	resultPrintJobPrintable["isRePrintable"] = isRePrintable
	resultPrintJobPrintable["fullFileLocation"] = fullFileLocation
	return resultPrintJobPrintable




def _isFileReadable(fullFileLocation):
	result = False
	try:
		with open(fullFileLocation) as fp:
			result = True
	except IOError as err:
		print ("Error reading the file {0}: {1}".format(fullFileLocation, err))
	return result
