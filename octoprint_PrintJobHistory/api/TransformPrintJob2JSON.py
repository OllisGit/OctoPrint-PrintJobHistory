# coding=utf-8
from __future__ import absolute_import


from octoprint_PrintJobHistory.CameraManager import CameraManager
from octoprint_PrintJobHistory.common import StringUtils
from octoprint_PrintJobHistory.common import PrintJobUtils

def transformPrintJobModel(job, fileManager, deleteDateTimeFromDict = True):
	jobAsDict = job.__data__

	jobAsDict["printStartDateTimeFormatted"] = job.printStartDateTime.strftime('%d.%m.%Y %H:%M')
	if (job.printEndDateTime):
		jobAsDict["printEndDateTimeFormatted"] = job.printEndDateTime.strftime('%d.%m.%Y %H:%M')
	# # Calculate duration
	# duration = job.printEndDateTime - job.printStartDateTime
	duration = job.duration
	durationFormatted = StringUtils.secondsToText(duration)
	jobAsDict["durationFormatted"] = durationFormatted

	fileSize = job.fileSize
	fileSizeFormatted = StringUtils.get_formatted_size(fileSize)
	jobAsDict["fileSizeFormatted"] = fileSizeFormatted
	# -- filament
	allFilaments = job.getFilamentModels()
	if allFilaments != None:
		allFilamentDict = {}
		for filament in allFilaments:

			filamentDict = filament.__data__
			filamentDict["usedWeight"] = StringUtils.formatFloatSave("{:.02f}", filamentDict["usedWeight"], "")

			filamentDict["usedLengthFormatted"] = StringUtils.formatFloatSave("{:.02f}", convertMM2M(filamentDict["usedLength"]), "")
			filamentDict["calculatedLengthFormatted"] = StringUtils.formatFloatSave("{:.02f}", convertMM2M(filamentDict["calculatedLength"]), "")

			filamentDict["usedCost"] = StringUtils.formatFloatSave("{:.02f}", filamentDict["usedCost"], "")
			# remove datetime, because not json serializable
			if (deleteDateTimeFromDict):
				del filamentDict["created"]
			# put to overall model
			allFilamentDict[filamentDict["toolId"]] = filamentDict

		jobAsDict['filamentModels'] = allFilamentDict
	# -- temperatures
	allTemperatures = job.getTemperatureModels()
	if not allTemperatures == None and len(allTemperatures) > 0:
		allTempsAsList = list()

		for temp in allTemperatures:
			tempAsDict = dict()
			tempAsDict["sensorName"] = temp.sensorName
			tempAsDict["sensorValue"] = temp.sensorValue
			allTempsAsList.append(tempAsDict)

		jobAsDict["temperatureModels"] = allTempsAsList
	# -- costs
	isCostsAvailable = False
	costs = job.getCosts()
	if (costs != None):
		costsAsDict = costs.__data__
		del costsAsDict["created"]
		jobAsDict["costs"] = costsAsDict
		isCostsAvailable = True
	jobAsDict["isCostsAvailable"] = isCostsAvailable
	# -- images
	jobAsDict["snapshotFilename"] = CameraManager.buildSnapshotFilename(job.printStartDateTime)
	# remove timedelta object, because could not transfered to client
	if (deleteDateTimeFromDict):
		del jobAsDict["printStartDateTime"]
		del jobAsDict["printEndDateTime"]
		del jobAsDict["created"]

	# not the best approach to check this value here
	printJobReprintable = PrintJobUtils.isPrintJobReprintable(fileManager, job.fileOrigin, job.filePathName, job.fileName)

	jobAsDict["isRePrintable"] = printJobReprintable["isRePrintable"]
	jobAsDict["fullFileLocation"] = printJobReprintable["fullFileLocation"]

	return jobAsDict

def transformAllPrintJobModels(allJobsModels, fileManager, deleteDateTimeFromDict = True):

	result = []
	for job in allJobsModels:
		jobAsDict = transformPrintJobModel(job, fileManager, deleteDateTimeFromDict)
		result.append(jobAsDict)

	return result

#  convert mm to m
def convertMM2M(value):
	if (value == None or not isinstance(value, float)):
		return ""
	floatValue = float(value)
	return floatValue / 1000.0






