# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.CameraManager import CameraManager
from octoprint_PrintJobHistory.common import StringUtils



def transformPrintJobModel(job):
	jobAsDict = job.__data__

	jobAsDict["printStartDateTimeFormatted"] = job.printStartDateTime.strftime('%d.%m.%Y %H:%M')
	jobAsDict["printEndDateTimeFormatted"] = job.printEndDateTime.strftime('%d.%m.%Y %H:%M')
	# # Calculate duration
	# duration = job.printEndDateTime - job.printStartDateTime
	duration = job.duration
	durationFormatted = StringUtils.secondsToText(duration)
	jobAsDict["durationFormatted"] = durationFormatted

	allFilaments = job.loadFilamentFromAssoziation()
	if allFilaments != None:
		filamentDict = allFilaments.__data__
		filamentDict["usedLength"] = StringUtils.formatFloatSave("{:.02f}", filamentDict["usedLength"], "")
		filamentDict["usedWeight"] = StringUtils.formatFloatSave("{:.02f}", filamentDict["usedWeight"], "")
		filamentDict["usedCost"] = StringUtils.formatFloatSave("{:.02f}", filamentDict["usedCost"], "")
		filamentDict["calculatedLength"] = StringUtils.formatFloatSave("{:.02f}", filamentDict["calculatedLength"], "")
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
	# remove timedelta
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






