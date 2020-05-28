# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.CameraManager import CameraManager
from octoprint_PrintJobHistory.common import StringUtils



def transformPrintJobModel(job):
	jobAsDict = job.__data__

	jobAsDict["printStartDateTimeFormatted"] = job.printStartDateTime.strftime('%d.%m.%Y %H:%M')
	if (job.printEndDateTime):
		jobAsDict["printEndDateTimeFormatted"] = job.printEndDateTime.strftime('%d.%m.%Y %H:%M')
	# # Calculate duration
	# duration = job.printEndDateTime - job.printStartDateTime
	duration = job.duration
	durationFormatted = StringUtils.secondsToText(duration)
	jobAsDict["durationFormatted"] = durationFormatted

	allFilaments = job.loadFilamentFromAssoziation()
	if allFilaments != None:
		filamentDict = allFilaments.__data__
		filamentDict["usedWeight"] = StringUtils.formatFloatSave("{:.02f}", filamentDict["usedWeight"], "")

		filamentDict["usedLengthFormatted"] = StringUtils.formatFloatSave("{:.02f}", _convertMM2M(filamentDict["usedLength"]), "")
		filamentDict["calculatedLengthFormatted"] = StringUtils.formatFloatSave("{:.02f}", _convertMM2M(filamentDict["calculatedLength"]), "")

		filamentDict["usedCost"] = StringUtils.formatFloatSave("{:.02f}", filamentDict["usedCost"], "")
		filamentDict["spoolVendor"] = filamentDict["profileVendor"]

		jobAsDict['filamentModel'] = filamentDict

	allTemperatures = job.getTemperaturesFromAssoziation()
	if not allTemperatures == None and len(allTemperatures) > 0:
		allTempsAsList = list()

		for temp in allTemperatures:
			tempAsDict = dict()
			tempAsDict["sensorName"] = temp.sensorName
			tempAsDict["sensorValue"] = temp.sensorValue
			allTempsAsList.append(tempAsDict)

		jobAsDict["temperatureModels"] = allTempsAsList

	jobAsDict["snapshotFilename"] = CameraManager.buildSnapshotFilename(job.printStartDateTime)
	# remove timedelta object, because could not transfered to client
	del jobAsDict["printStartDateTime"]
	del jobAsDict["printEndDateTime"]
	del jobAsDict["created"]
	del jobAsDict["filamentModel"]["created"]

	return jobAsDict

def transformAllPrintJobModels(allJobsModels):

	result = []
	for job in allJobsModels:
		jobAsDict = transformPrintJobModel(job)
		result.append(jobAsDict)

	return result

#  convert mm to m
def _convertMM2M(value):
	if (value == None or not isinstance(value, float)):
		return ""
	floatValue = float(value)
	return floatValue / 1000.0






