# coding=utf-8
from __future__ import absolute_import

import csv
import StringIO

def transform2CSV(allJobsDict):

	result = None
	si = StringIO.StringIO()

	headers = ['User', 'Result', 'Start Date', 'End Date', 'Duration', 'File Name', 'File Path', 'File Size', 'Layers', 'Note', 'Temperatures', 'Spool Name', 'Material', 'Diameter', 'Used Length', 'Calculated Length', 'Used Weight', 'Used Filament Cost']

	writer = csv.writer(si, quoting=csv.QUOTE_ALL)
	writer.writerow(headers)
	for job in allJobsDict:
		row = _convertPrintJobHistoryEntityToList(job)
		writer.writerow(row)
	result = si.getvalue()

	return result


def _convertPrintJobHistoryEntityToList(jobAsDict):
	result = list()

	fields = ['userName', 'printStatusResult', 'printStartDateTimeFormatted', 'printEndDateTimeFormatted', 'durationFormatted', 'fileName', 'filePathName', 'fileSize', 'printedLayers', 'noteText']
	for field in fields:
		value = jobAsDict[field]
		result.append(value if value is not None else '-')
	tempValue = str()
	for tempValues in jobAsDict["temperatureModels"]:
		sensorName = tempValues["sensorName"]
		sensorValue = str(tempValues["sensorValue"])
		tempValue = " " + tempValue + sensorName + ":" + sensorValue
	result.append(tempValue)

	filamentAsDict = jobAsDict["filamentModel"]
	fields = ['spoolName', 'material', 'diameter', 'usedLength', 'calculatedLength', 'usedWeight', 'usedCost']
	for field in fields:
		value = filamentAsDict[field]
		result.append(value if value is not None else '-')

	return result
