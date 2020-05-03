import io
from io import StringIO
import csv
import datetime
import os
import re

from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from octoprint_PrintJobHistory.models.TemperatureModel import TemperatureModel
from octoprint_PrintJobHistory.models.FilamentModel import FilamentModel
from octoprint_PrintJobHistory.common import StringUtils

FORMAT_DATETIME = "%d.%m.%Y %H:%M"

COLUMN_USER = "User"
COLUMN_PRINT_RESULT = "Print result [success canceled failed]"
COLUMN_START_DATETIME = "Start Datetime [dd.mm.yyyy hh:mm]"
COLUMN_END_DATETIME = "End Datetime [dd.mm.yyyy hh:mm]"
COLUMN_DURATION = "Duration"
COLUMN_FILE_NAME = "File Name"
COLUMN_FILE_PATH = "File Path"
COLUMN_FILE_SIZE = "File Size [bytes]"
COLUMN_LAYERS = "Layers [current / total]"
COLUMN_NOTE = "Note"
COLUMN_TEMPERATURES = "Temperatures [bed:temp tool0:temp]"
COLUMN_SPOOL_VENDOR = "Spool Vendor"
COLUMN_SPOOL_NAME = "Spool Name"
COLUMN_MATERIAL = "Material"
COLUMN_DIAMETER = "Diameter [mm]"
COLUMN_DENSITY = "Density [g/cm3]"
COLUMN_USED_LENGTH = "Used Length [mm]"
COLUMN_CALCULATED_LENGTH = "Calculated Length [mm]"
COLUMN_USED_WEIGHT = "Used Weight [g]"
COLUMN_USED_FILAMENT_COSTS = "Used Filament Cost"

#############################################################################################################
class CSVColumn:
	fieldName = ""
	columnLabel = ""
	description = ""
	formattorParser = None

	def __init__(self, fieldName, columnLabel, description, formattorParser):
		self.fieldName = fieldName
		self.columnLabel = columnLabel
		self.description = description
		self.formattorParser = formattorParser

	def getCSV(self, printJobModel):
		columnValue =  self.formattorParser.formatValue(printJobModel, self.fieldName)
		if isinstance(columnValue, float):
			pass
		columnValue = str(columnValue)
		# columnValue = columnValue.encode("utf-8")
		return columnValue

	def parseAndAssignFieldValue(self, fieldValue, printJobModel, errorCollection, lineNumber):
		try:
			self.formattorParser.parseAndAssignFieldValue(self.columnLabel, self.fieldName, fieldValue, printJobModel, errorCollection, lineNumber)
		except Exception as e:
			errorMessage = str(e)
			errorCollection.append("[" + str(
				lineNumber) + "]" + "Error parsing value '" + fieldValue + "' for field '" + self.columnLabel + "': " + errorMessage)


############################################################################################## ALL FORMATTOR AND PARSERS


class DefaultCSVFormattorParser:

	def formatValue(self, printJob, fieldName):
		if (hasattr(printJob, fieldName) == False):
			return "-"
		valueToFormat = getattr(printJob, fieldName)

		adjustedValue = valueToFormat if valueToFormat is not None else '-'
		if (type(adjustedValue) is int or type(adjustedValue) is float or type(adjustedValue) is str or type(adjustedValue) is unicode):
			adjustedValue = str(adjustedValue)
			adjustedValue = adjustedValue.replace('\n', ' ').replace('\r', '')
		else:
			# print("BOOOOOOMMMMM!!!!!  "+str(type(adjustedValue)))
			adjustedValue = "#"		# workaround to identify not correct mapped values
		return adjustedValue

	def parseAndAssignFieldValue(self, fieldLabel, fieldName, fieldValue, printJobModel, errorCollection, lineNumber):
		if ("" == fieldValue or "-" == fieldValue or fieldValue == None):
			# check if mandatory
			return
		setattr(printJobModel, fieldName, fieldValue)

class PrintStatusCSVFormattorParser:

	def formatValue(self, printJob, fieldName):
		if (hasattr(printJob, fieldName) == False):
			return "-"
		valueToFormat = getattr(printJob, fieldName)

		adjustedValue = valueToFormat if valueToFormat is not None else '-'
		if (type(adjustedValue) is int or type(adjustedValue) is float):
			adjustedValue = str(adjustedValue)

		adjustedValue = adjustedValue.replace('\n', ' ').replace('\r', '')

		return adjustedValue

	def parseAndAssignFieldValue(self, fieldLabel, fieldName, fieldValue, printJobModel, errorCollection, lineNumber):
		if ("" == fieldValue or "-" == fieldValue or fieldValue == None):
			# check if mandatory
			return
		SUCCESS = "success"
		CANCEL = "cancel"
		FAILED = "failed"
		if (SUCCESS == fieldValue or CANCEL == fieldValue or FAILED == fieldValue):
			setattr(printJobModel, fieldName, fieldValue)
		elif("0" == fieldValue):
			setattr(printJobModel, fieldName, CANCEL)
		elif("1" == fieldValue):
			setattr(printJobModel, fieldName, SUCCESS)
		elif("2" == fieldValue):
			setattr(printJobModel, fieldName, FAILED)
		else:
			errorCollection.append("["+str(lineNumber)+"]"+" Wrong print job status type '"+fieldValue+"'. Allowed: '"+SUCCESS+"' or 1, '"+CANCEL+"' or 0, '"+FAILED+"' or 2")
		pass

class DateTimeCSVFormattorParser:

	def formatValue(self, printJob, fieldName):
		if (hasattr(printJob, fieldName) == False):
			return "-"
		valueToFormat = getattr(printJob, fieldName)

		if valueToFormat is None or "" == valueToFormat:
			return "-"
		adjustedValue = valueToFormat.strftime(FORMAT_DATETIME)
		valueToFormat = adjustedValue
		return valueToFormat

	def parseAndAssignFieldValue(self, fieldLabel, fieldName, fieldValue, printJobModel, errorCollection, lineNumber):
		if ("" == fieldValue or "-" == fieldValue or fieldValue == None):
			# check if mandatory
			return
		if (":" in fieldValue):
			# looks like timestamp in format 19.12.2019 10:07
			fieldDateTime = datetime.datetime.strptime(fieldValue, FORMAT_DATETIME)
			setattr(printJobModel, fieldName, fieldDateTime)
			pass
		else:
			fieldDateTime = datetime.datetime.fromtimestamp(float(fieldValue))
			setattr(printJobModel, fieldName, fieldDateTime)
			pass
		pass

class DurationCSVFormattorParser:

	def formatValue(self, printJob, fieldName):
		if (hasattr(printJob, fieldName) == False):
			return "-"
		valueToFormat = getattr(printJob, fieldName)

		if valueToFormat is None or "" == valueToFormat:
			return "-"
		adjustedValue = StringUtils.secondsToText(valueToFormat)
		return adjustedValue

	def parseAndAssignFieldValue(self, fieldLabel, fieldName, fieldValue, printJobModel, errorCollection, lineNumber):
		if ("" == fieldValue or "-" == fieldValue or fieldValue == None):
			# check if mandatory
			return
		try:
			if ("." in fieldValue):
				# looks like timestamp in format 22.340769225993427
				durationInSeconds = int(fieldValue)
				setattr(printJobModel, fieldName, durationInSeconds)
				pass
			else:
				# looks like timestamp in format 1m3s
				durationInSeconds = StringUtils.durationToSeconds(fieldValue)
				setattr(printJobModel, fieldName, durationInSeconds)
				pass
		except Exception as e:
			errorMessage = str(e)
			errorCollection.append("["+str(lineNumber)+"]"+" Error parsing value '"+fieldValue+"' for field '"+fieldName+"': "+errorMessage)
		pass

class TemperaturCSVFormattorParser:

	tempPattern = re.compile("bed:([0-9]*\.?[0-9]*) tool[0-9]:([0-9]*\.?[0-9]*)")

	def formatValue(self, printJob, fieldName):
		if (hasattr(printJob, fieldName) == False):
			return "-"

		valueToFormat = getattr(printJob, fieldName)

		if (valueToFormat == None):
			valueToFormat = printJob.temperatures

		if valueToFormat is None:
			return "-"

		tempValue = ""
		for tempValues in valueToFormat:
			sensorName = tempValues.sensorName
			sensorValue = str(tempValues.sensorValue)
			tempValue = tempValue + sensorName + ":" + sensorValue + " "
		return tempValue

	def parseAndAssignFieldValue(self, fieldLabel, fieldName, fieldValue, printJobModel, errorCollection, lineNumber):

		if ("" == fieldValue or "-" == fieldValue or fieldValue == None):
			# check if mandatory
			return
		matched = self.tempPattern.match(fieldValue)
		if (matched):
			bedTemp = float(matched.group(1))
			toolTemp = float(matched.group(2))

			tempModel = TemperatureModel()
			tempModel.sensorName = "bed"
			tempModel.sensorValue = bedTemp
			printJobModel.addTemperatureModel(tempModel)

			tempModel = TemperatureModel()
			tempModel.sensorName = "tool0"
			tempModel.sensorValue = toolTemp
			printJobModel.addTemperatureModel(tempModel)
			pass
		else:
			errorCollection.append("[" + str(
				lineNumber) + "]" + " Wrong temperature format. Allowed: 'bed:60.0 tool0:200.0'")
		pass

class FilamentCSVFormattorParser:

	def formatValue(self, printJob, fieldNames):

		if (hasattr(printJob, fieldNames[0]) == False):
			return "-"
		allFilamentModels = getattr(printJob, fieldNames[0])
		if (allFilamentModels is None):
			allFilamentModels = printJob.filaments

		if (allFilamentModels is None or len(allFilamentModels) == 0):
			return "-"
		# only support for one model
		filamentModel = allFilamentModels[0]
		if (hasattr(filamentModel, fieldNames[1]) == False):
			return "-"
		valueToFormat = getattr(filamentModel, fieldNames[1])

		# append unit to value
		if ("usedCost" == fieldNames[1] and valueToFormat != None and valueToFormat != ""):
			if (hasattr(filamentModel, "spoolCostUnit") == True and filamentModel.spoolCostUnit != None):
				valueToFormat = StringUtils.formatFloatSave(StringUtils.FLOAT_DEFAULT_FORMAT, valueToFormat, "-")
				if (valueToFormat != "-"):
					if (isinstance(filamentModel.spoolCostUnit, str)):
						valueToFormat = valueToFormat + filamentModel.spoolCostUnit
					else:
						valueToFormat = valueToFormat + filamentModel.spoolCostUnit.encode("utf-8")

		if ("usedLength" == fieldNames[1] or
			"calculatedLength" == fieldNames[1] or
			"usedWeight" == fieldNames[1]):

			if (valueToFormat != None and valueToFormat != "" and valueToFormat != "-"):
				valueToFormat = StringUtils.formatFloatSave(StringUtils.FLOAT_DEFAULT_FORMAT, valueToFormat, "-")

		if valueToFormat is None or "" == valueToFormat:
			return "-"

		return valueToFormat

	def parseAndAssignFieldValue(self, fieldLabel, fieldName, fieldValue, printJobModel, errorCollection, lineNumber):
		if ("" == fieldValue or "-" == fieldValue or fieldValue == None):
			# check if mandatory
			return

		filemanentModel = None
		allFilemanentModel  = printJobModel.getFilamentModels()
		if (allFilemanentModel != None and len(allFilemanentModel) > 0):
			filemanentModel = allFilemanentModel[0]
		else:
			filemanentModel  = FilamentModel()
			printJobModel.addFilamentModel(filemanentModel)

		if (COLUMN_SPOOL_VENDOR == fieldLabel):
			filemanentModel.profileVendor = fieldValue
			pass
		elif (COLUMN_SPOOL_NAME == fieldLabel):
			filemanentModel.spoolName = fieldValue
			pass
		elif (COLUMN_MATERIAL == fieldLabel):
			filemanentModel.material = fieldValue
			pass
		elif (COLUMN_DIAMETER == fieldLabel):
			filemanentModel.diameter = float(fieldValue)
			pass
		elif (COLUMN_DENSITY == fieldLabel):
			filemanentModel.density = float(fieldValue)
			pass
		elif (COLUMN_USED_LENGTH == fieldLabel):
			filemanentModel.usedLength = float(fieldValue)
			pass
		elif (COLUMN_CALCULATED_LENGTH == fieldLabel):
			filemanentModel.calculatedLength = float(fieldValue)
			pass
		elif (COLUMN_USED_WEIGHT == fieldLabel):
			filemanentModel.usedWeight = float(fieldValue)
			pass
		elif (COLUMN_USED_FILAMENT_COSTS == fieldLabel):
			costUnit = fieldValue[-1]
			if (costUnit.isdigit()):
				filemanentModel.spoolCost = float(fieldValue)
			else:
				costValue = fieldValue[:-1]
				filemanentModel.spoolCost = float(costValue)
				filemanentModel.spoolCostUnit = costUnit
			pass
		pass

######################################################################################################################

ALL_COLUMNS_SORTED = [
	COLUMN_USER,
	COLUMN_PRINT_RESULT,
	COLUMN_START_DATETIME,
	COLUMN_END_DATETIME,
	COLUMN_DURATION,
	COLUMN_FILE_NAME,
	COLUMN_FILE_PATH,
	COLUMN_FILE_SIZE,
	COLUMN_LAYERS,
	COLUMN_NOTE,
	COLUMN_TEMPERATURES,
	COLUMN_SPOOL_NAME,
	COLUMN_MATERIAL,
	COLUMN_DIAMETER,
	COLUMN_DENSITY,
	COLUMN_USED_LENGTH,
	COLUMN_CALCULATED_LENGTH,
	COLUMN_USED_WEIGHT,
	COLUMN_USED_FILAMENT_COSTS
]

ALL_COLUMNS = {
	COLUMN_USER: CSVColumn("userName", COLUMN_USER, "", DefaultCSVFormattorParser()),
	COLUMN_PRINT_RESULT: CSVColumn("printStatusResult", COLUMN_PRINT_RESULT, "", PrintStatusCSVFormattorParser()),
	COLUMN_START_DATETIME: CSVColumn("printStartDateTime", COLUMN_START_DATETIME, "", DateTimeCSVFormattorParser()),
	COLUMN_END_DATETIME: CSVColumn("printEndDateTime", COLUMN_END_DATETIME, "", DateTimeCSVFormattorParser()),
	COLUMN_DURATION: CSVColumn("duration", COLUMN_DURATION, "", DurationCSVFormattorParser()),
	COLUMN_FILE_NAME: CSVColumn("fileName", COLUMN_FILE_NAME, "", DefaultCSVFormattorParser()),
	COLUMN_FILE_PATH: CSVColumn("filePathName", COLUMN_FILE_PATH, "", DefaultCSVFormattorParser()),
	COLUMN_FILE_SIZE: CSVColumn("fileSize", COLUMN_FILE_SIZE, "", DefaultCSVFormattorParser()),
	COLUMN_LAYERS: CSVColumn("printedLayers", COLUMN_LAYERS, "", DefaultCSVFormattorParser()),
	COLUMN_NOTE: CSVColumn("noteText", COLUMN_NOTE, "", DefaultCSVFormattorParser()),
	COLUMN_TEMPERATURES: CSVColumn("allTemperatures", COLUMN_TEMPERATURES, "", TemperaturCSVFormattorParser()),
	COLUMN_SPOOL_VENDOR: CSVColumn(["allFilaments", "profileVendor"], COLUMN_SPOOL_VENDOR, "", FilamentCSVFormattorParser()),
	COLUMN_SPOOL_NAME: CSVColumn(["allFilaments", "spoolName"], COLUMN_SPOOL_NAME, "", FilamentCSVFormattorParser()),
	COLUMN_MATERIAL: CSVColumn(["allFilaments", "material"], COLUMN_MATERIAL, "", FilamentCSVFormattorParser()),
	COLUMN_DIAMETER: CSVColumn(["allFilaments", "diameter"], COLUMN_DIAMETER, "", FilamentCSVFormattorParser()),
	COLUMN_DENSITY: CSVColumn(["allFilaments", "density"], COLUMN_DENSITY, "", FilamentCSVFormattorParser()),
	COLUMN_USED_LENGTH: CSVColumn(["allFilaments", "usedLength"], COLUMN_USED_LENGTH, "", FilamentCSVFormattorParser()),
	COLUMN_CALCULATED_LENGTH: CSVColumn(["allFilaments", "calculatedLength"], COLUMN_CALCULATED_LENGTH, "", FilamentCSVFormattorParser()),
	COLUMN_USED_WEIGHT: CSVColumn(["allFilaments", "usedWeight"], COLUMN_USED_WEIGHT, "", FilamentCSVFormattorParser()),
	COLUMN_USED_FILAMENT_COSTS: CSVColumn(["allFilaments", "usedCost"], COLUMN_USED_FILAMENT_COSTS, "", FilamentCSVFormattorParser()),
}



####################################################################################################### -> EXPORT TO CSV

def transform2CSV(allJobsDict):
	result = None
	si = StringIO()	#TODO maybe a bad idea to use a internal memory based string, needs to be switched to response stream
	# si = io.BytesIO()

	writer = csv.writer(si, quoting=csv.QUOTE_ALL)
	#  Write HEADER
	headerList = list()
	csvLine = ""
	for columnKey in ALL_COLUMNS_SORTED:
		csvColumn = ALL_COLUMNS[columnKey]
		label = '"' + csvColumn.columnLabel + '"'
		headerList.append(label)

	csvLine =  "," .join(headerList) + "\n"
	# writer.writerow(headerList)
	print(csvLine)
	yield csvLine

	# Write CSV-Content
	for job in allJobsDict:
		csvRow = list()
		for columnKey in ALL_COLUMNS_SORTED:
			# print(columnKey)
			csvColumn = ALL_COLUMNS[columnKey]
			csvColumnValue = '"' + csvColumn.getCSV(job)  + '"'
			csvRow.append(csvColumnValue)
		csvLine = ",".join(csvRow) + "\n"
		print(csvLine)
		yield csvLine
		# writer.writerow(csvRow)
	# result = si.getvalue()
	# return result


########################################################################################################## -> IMPORT CSV
mandatoryFieldNames = [
	ALL_COLUMNS[COLUMN_PRINT_RESULT].columnLabel,
	ALL_COLUMNS[COLUMN_FILE_NAME].columnLabel,
	ALL_COLUMNS[COLUMN_START_DATETIME].columnLabel,
	ALL_COLUMNS[COLUMN_DURATION].columnLabel,
]

# mandatoryFieldAvaiable = list()

columnOrderInFile = dict()


def parseCSV(csvFile4Import, errorCollection, logger):

	result = list()	# List with printJobModels
	lineNumber = 0
	try:
		with open(csvFile4Import) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			lineNumber = 0
			for row in csv_reader:
				lineNumber += 1
				if lineNumber == 1:
					# createColumnOrderFromHeader(row)
					# mandatoryFieldCount = 0
					mandatoryFieldAvaiable = list()
					columnIndex = 0
					for column in row:
						column = column.strip()
						if column in ALL_COLUMNS:
							columnOrderInFile[columnIndex] = ALL_COLUMNS[column]
							if column in mandatoryFieldNames:
								mandatoryFieldAvaiable.append(column)
								# mandatoryFieldCount += 1
						columnIndex += 1
					if len(mandatoryFieldAvaiable) != len(mandatoryFieldNames):
					# if mandatoryFieldCount != len(mandatoryFieldNames):
						# identify missing files
						# mandatoryFieldMissing = mandatoryFieldNames - mandatoryFieldAvaiable
						mandatoryFieldMissing = list( set(mandatoryFieldNames) - set(mandatoryFieldAvaiable) )
						errorCollection.append("Mandatory column is missing! <br/><b>'" + "".join(mandatoryFieldMissing) + "'</b><br/>")
						break
				else:
					printJobModel = PrintJobModel()
					# parse line with header defined order
					columnIndex = 0
					for columnValue in row:
						if columnIndex in columnOrderInFile:
							csvColumn = columnOrderInFile[columnIndex]
							if not csvColumn == None:
								columnValue = columnValue.strip()
								csvColumn.parseAndAssignFieldValue(columnValue, printJobModel, errorCollection, lineNumber)
								pass
						columnIndex += 1
					if (len(errorCollection) != 0):
						logger.warn("ERROR(s) occurred!!!!!")
					else:
						result.append(printJobModel)
			pass
	except Exception as e:
		errorMessage = "Error during processing file '" + csvFile4Import + "' error '" + str(e) + "' line '" + str(lineNumber) + "'"
		errorCollection.append(errorMessage)
		logger.error(errorMessage)
	finally:
		logger.info("Removing uploded csv temp-file")
		try:
			os.remove(csvFile4Import)
		except Exception:
			pass

	print("Processed "+str(lineNumber))

	return result


