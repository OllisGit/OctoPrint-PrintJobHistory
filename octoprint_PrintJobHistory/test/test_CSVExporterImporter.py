import logging

from octoprint_PrintJobHistory.api import TransformPrintJob2JSON
from octoprint_PrintJobHistory.common.CSVExportImporter import importCSV, transform2CSV

###################################
## IMPORT
print("START IMPORT")
errorCollection = list()
csvFile4Import = "/Users/o0632/0_Projekte/3DDruck/OctoPrint/OctoPrint-PrintJobHistory/testdata/sample.csv"
result = importCSV(csvFile4Import, errorCollection, logging)
print("END IMPORT")



###################################
# EXPORT CSV TEST with single MOCK-Object
singleJob = {
	"userName": "Olaf",
	# "printStartDateTimeFormatted": datetime.datetime(2019, 12, 11, 14, 53),
	"printStartDateTimeFormatted": "2019-12-11 14:53",
	"printStatusResult": "success",
	"duration": 0,
	"fileSize": 3123,
	"temperatureModels": [
		{"sensorName": "bed", "sensorValue": 123.3},
		{"sensorName": "tool0", "sensorValue": 321.1}
	],
	"filamentModel": {
		"spoolName": "My Best Spool",
		"material": "PETG",
		"diameter": 1.234,
		"density": 1.25,
		"usedLength": 9.24,
		"calculatedLength": 100.24,
		"usedWeight": 6.06,
		"usedCost": 0.04
	}
}

# NOT WORKING
# allJobsModels = list()
# allJobsModels.append(singleJob)
# allJobsDict = TransformPrintJob2JSON.transformAllPrintJobModels(allJobsModels)
# csvResult = transform2CSV(allJobsDict)
#
# print(csvResult)
