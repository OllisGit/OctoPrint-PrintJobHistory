import io
from io import StringIO
import csv
import datetime
import os
import re

from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from octoprint_PrintJobHistory.models.TemperatureModel import TemperatureModel
from octoprint_PrintJobHistory.models.FilamentModel import FilamentModel
from octoprint_PrintJobHistory.models.CostModel import CostModel
from octoprint_PrintJobHistory.common import StringUtils

FORMAT_DATETIME = "%d.%m.%Y %H:%M"
FORMAT_DATE = "%d.%m.%Y"

COLUMN_USER = "User"
COLUMN_PRINT_RESULT = "Print result [success canceled failed]"
COLUMN_START_DATETIME = "Start Datetime [dd.mm.yyyy hh:mm]"
COLUMN_END_DATETIME = "End Datetime [dd.mm.yyyy hh:mm]"
COLUMN_DURATION = "Duration"
COLUMN_FILE_NAME = "File Name"
COLUMN_FILE_PATH = "File Path"
COLUMN_FILE_SIZE = "File Size [bytes]"
COLUMN_LAYERS = "Layers [current / total]"
COLUMN_HEIGHT = "Height [current / total]"
COLUMN_NOTE = "Note"
COLUMN_TEMPERATURES = "Temperatures [bed:temp toolX:temp]"
COLUMN_SPOOL_VENDOR = "Spool Vendor"
COLUMN_SPOOL_NAME = "Spool Name"
COLUMN_MATERIAL = "Material"
COLUMN_DIAMETER = "Diameter [mm]"
COLUMN_DENSITY = "Density [g/cm3]"
COLUMN_USED_LENGTH = "Used Length [mm]"
COLUMN_CALCULATED_LENGTH = "Calculated Length [mm]"
COLUMN_USED_WEIGHT = "Used Weight [g]"
COLUMN_USED_FILAMENT_COSTS = "Used Filament Cost"

COLUMN_ESTIMATED_FILAMENT_COSTS = "Estimated Filament Cost"
COLUMN_ESTIMATED_ELECTRICITY_COSTS = "Estimated Electricity Cost"
COLUMN_ESTIMATED_PRINTER_COSTS = "Estimated Printer Cost"
COLUMN_OTHER_COSTS = "Other Cost [label:value]"

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

		columnValue = StringUtils.to_native_str(columnValue)

		return columnValue

	def parseAndAssignFieldValue(self, fieldValue, printJobModel, errorCollection, lineNumber):
		try:
			self.formattorParser.parseAndAssignFieldValue(self.columnLabel, self.fieldName, fieldValue, printJobModel, errorCollection, lineNumber)
		except Exception as e:
			errorMessage = str(e)
			errorMessage = re.sub(r"[^a-zA-Z0-9()]"," ", errorMessage) # fix for: #32 'invalid literal for float(): 0.00 <k> '
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
			adjustedValue = StringUtils.to_native_str(adjustedValue)
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
			adjustedValue = StringUtils.to_native_str(adjustedValue)

		adjustedValue = adjustedValue.replace('\n', ' ').replace('\r', '')

		return adjustedValue

	def parseAndAssignFieldValue(self, fieldLabel, fieldName, fieldValue, printJobModel, errorCollection, lineNumber):
		if ("" == fieldValue or "-" == fieldValue or fieldValue == None):
			# check if mandatory
			return
		SUCCESS = "success"
		CANCELED = "canceled"
		FAILED = "failed"
		if (SUCCESS == fieldValue or CANCELED == fieldValue or FAILED == fieldValue):
			setattr(printJobModel, fieldName, fieldValue)
		elif("0" == fieldValue):
			setattr(printJobModel, fieldName, CANCELED)
		elif("1" == fieldValue):
			setattr(printJobModel, fieldName, SUCCESS)
		elif("2" == fieldValue):
			setattr(printJobModel, fieldName, FAILED)
		else:
			errorCollection.append("["+str(lineNumber)+"]"+" Wrong print job status type '"+fieldValue+"'. Allowed: '"+SUCCESS+"' or 1, '"+CANCELED+"' or 0, '"+FAILED+"' or 2")
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
			fieldDateTime = datetime.datetime.strptime(fieldValue, FORMAT_DATE)
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

	tempPattern = re.compile("bed:([0-9]*\.?[0-9]*) (tool[0-9]):([0-9]*\.?[0-9]*)")

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
			toolId = matched.group(2)	# e.g. tool1
			toolTemp = float(matched.group(3))

			tempModel = TemperatureModel()
			tempModel.sensorName = "bed"
			tempModel.sensorValue = bedTemp
			printJobModel.addTemperatureModel(tempModel)

			tempModel = TemperatureModel()
			tempModel.sensorName = toolId
			tempModel.sensorValue = toolTemp
			printJobModel.addTemperatureModel(tempModel)
			pass
		else:
			errorCollection.append("[" + str(
				lineNumber) + "]" + " Wrong temperature format. Allowed: 'bed:60.0 tool0:200.0'")
		pass

class FilamentCSVFormattorParser:

	def formatValue(self, printJob, fieldName):

		# only support for total model
		totalFilamentModel = printJob.getFilamentModelByToolId("total")
		if (totalFilamentModel == None):
			return "-"
		if (hasattr(totalFilamentModel, fieldName) == False):
			return "-"
		valueToFormat = getattr(totalFilamentModel, fieldName)

		if ("usedLength" == fieldName or
			"calculatedLength" == fieldName or
			"usedWeight" == fieldName):

			if (valueToFormat != None and valueToFormat != "" and valueToFormat != "-"):
				valueToFormat = StringUtils.formatFloatSave(StringUtils.FLOAT_DEFAULT_FORMAT, valueToFormat, "-")

		if valueToFormat is None or "" == valueToFormat:
			return "-"

		return valueToFormat

	def parseAndAssignFieldValue(self, fieldLabel, fieldName, fieldValue, printJobModel, errorCollection, lineNumber):
		if ("" == fieldValue or "-" == fieldValue or fieldValue == None):
			# check if mandatory
			return

		# allFilemanentModel  = printJobModel.getFilamentModels()
		filamanentModel = printJobModel.getFilamentModelByToolId("total")

		if (filamanentModel == None):
			filamanentModel  = FilamentModel()
			filamanentModel.toolId = "total"
			printJobModel.addFilamentModel(filamanentModel)

		if (COLUMN_SPOOL_VENDOR == fieldLabel):
			filamanentModel.vendor = fieldValue
			pass
		elif (COLUMN_SPOOL_NAME == fieldLabel):
			filamanentModel.spoolName = fieldValue
			pass
		elif (COLUMN_MATERIAL == fieldLabel):
			filamanentModel.material = fieldValue
			pass
		elif (COLUMN_DIAMETER == fieldLabel):
			filamanentModel.diameter = float(fieldValue)
			pass
		elif (COLUMN_DENSITY == fieldLabel):
			filamanentModel.density = float(fieldValue)
			pass
		elif (COLUMN_USED_LENGTH == fieldLabel):
			filamanentModel.usedLength = float(fieldValue)
			pass
		elif (COLUMN_CALCULATED_LENGTH == fieldLabel):
			filamanentModel.calculatedLength = float(fieldValue)
			pass
		elif (COLUMN_USED_WEIGHT == fieldLabel):
			filamanentModel.usedWeight = float(fieldValue)
			pass
		pass

class CostsCSVFormattorParser:

	def formatValue(self, printJob, fieldName):

		costModel = printJob.getCosts()
		if (costModel == None):
			return "-"

		if (hasattr(costModel, fieldName) == False):
			return "-"

		valueToFormat = getattr(costModel, fieldName)

		if ("filamentCost" == fieldName or
			"electricityCost" == fieldName or
			"printerCost" == fieldName or
			"otherCost" == fieldName):
			if (valueToFormat != None and valueToFormat != "" and valueToFormat != "-"):
				valueToFormat = StringUtils.formatFloatSave(StringUtils.FLOAT_DEFAULT_FORMAT, valueToFormat, "-")
				if ("otherCost" == fieldName):
					otherCostLabel = ""
					if (StringUtils.isNotEmpty(costModel.otherCostLabel)):
						otherCostLabel = costModel.otherCostLabel
					valueToFormat = otherCostLabel + ":" + valueToFormat

		if valueToFormat is None or "" == valueToFormat:
			return "-"

		return valueToFormat

	def parseAndAssignFieldValue(self, fieldLabel, fieldName, fieldValue, printJobModel, errorCollection, lineNumber):
		if ("" == fieldValue or "-" == fieldValue or fieldValue == None):
			# check if mandatory
			return

		costModel = printJobModel.getCosts()
		if (costModel == None):
			costModel  = CostModel()
			costModel.withDefaultSpoolValues = True
			printJobModel.setCosts(costModel)
		#
		# COLUMN_ESTIMATED_FILAMENT_COSTS = "Estimated Filament Cost"
		# COLUMN_ESTIMATED_ELECTRICITY_COSTS = "Estimated Electricity Cost"
		# COLUMN_ESTIMATED_PRINTER_COSTS = "Estimated Printer Cost"
		# COLUMN_OTHER_COSTS = "Other Cost [label:value]"

		if (COLUMN_ESTIMATED_FILAMENT_COSTS == fieldLabel):
			costModel.filamentCost = float(fieldValue)
			pass
		elif (COLUMN_ESTIMATED_ELECTRICITY_COSTS == fieldLabel):
			costModel.electricityCost = float(fieldValue)
			pass
		elif (COLUMN_ESTIMATED_PRINTER_COSTS == fieldLabel):
			costModel.printerCost = float(fieldValue)
			pass
		elif (COLUMN_OTHER_COSTS == fieldLabel):

			otherTokens = fieldValue.split(":")
			if (len(otherTokens) != 2):
				errorCollection.append(str(lineNumber) + ":Wrong format for 'Other Cost' need label:value<br/>")
				pass
			label = otherTokens[0]
			value = otherTokens[1]
			costModel.otherCostLabel = label
			costModel.otherCost = float(value)
			pass
		pass

######################################################################################################################
## CSV HEADER-ORDER
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
	COLUMN_HEIGHT,
	COLUMN_NOTE,
	COLUMN_TEMPERATURES,
	COLUMN_SPOOL_VENDOR,
	COLUMN_SPOOL_NAME,
	COLUMN_MATERIAL,
	COLUMN_DIAMETER,
	COLUMN_DENSITY,
	COLUMN_USED_LENGTH,
	COLUMN_CALCULATED_LENGTH,
	COLUMN_USED_WEIGHT,
	COLUMN_USED_FILAMENT_COSTS,
	COLUMN_ESTIMATED_FILAMENT_COSTS,
	COLUMN_ESTIMATED_ELECTRICITY_COSTS,
	COLUMN_ESTIMATED_PRINTER_COSTS,
	COLUMN_OTHER_COSTS
]

## ALL COLUMNS WITH THERE PARSER/EXPORTER
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
	COLUMN_HEIGHT: CSVColumn("printedHeight", COLUMN_HEIGHT, "", DefaultCSVFormattorParser()),
	COLUMN_NOTE: CSVColumn("noteText", COLUMN_NOTE, "", DefaultCSVFormattorParser()),
	COLUMN_TEMPERATURES: CSVColumn("allTemperatures", COLUMN_TEMPERATURES, "", TemperaturCSVFormattorParser()),
	COLUMN_SPOOL_VENDOR: CSVColumn("vendor", COLUMN_SPOOL_VENDOR, "", FilamentCSVFormattorParser()),
	COLUMN_SPOOL_NAME: CSVColumn("spoolName", COLUMN_SPOOL_NAME, "", FilamentCSVFormattorParser()),
	COLUMN_MATERIAL: CSVColumn("material", COLUMN_MATERIAL, "", FilamentCSVFormattorParser()),
	COLUMN_DIAMETER: CSVColumn("diameter", COLUMN_DIAMETER, "", FilamentCSVFormattorParser()),
	COLUMN_DENSITY: CSVColumn("density", COLUMN_DENSITY, "", FilamentCSVFormattorParser()),
	COLUMN_USED_LENGTH: CSVColumn("usedLength", COLUMN_USED_LENGTH, "", FilamentCSVFormattorParser()),
	COLUMN_CALCULATED_LENGTH: CSVColumn("calculatedLength", COLUMN_CALCULATED_LENGTH, "", FilamentCSVFormattorParser()),
	COLUMN_USED_WEIGHT: CSVColumn("usedWeight", COLUMN_USED_WEIGHT, "", FilamentCSVFormattorParser()),
	COLUMN_USED_FILAMENT_COSTS: CSVColumn("usedCost", COLUMN_USED_FILAMENT_COSTS, "", FilamentCSVFormattorParser()),

	COLUMN_ESTIMATED_FILAMENT_COSTS: CSVColumn("filamentCost", COLUMN_ESTIMATED_FILAMENT_COSTS, "", CostsCSVFormattorParser()),
	COLUMN_ESTIMATED_ELECTRICITY_COSTS: CSVColumn("electricityCost", COLUMN_ESTIMATED_ELECTRICITY_COSTS, "", CostsCSVFormattorParser()),
	COLUMN_ESTIMATED_PRINTER_COSTS: CSVColumn("printerCost", COLUMN_ESTIMATED_PRINTER_COSTS, "", CostsCSVFormattorParser()),
	COLUMN_OTHER_COSTS: CSVColumn("otherCost", COLUMN_OTHER_COSTS, "", CostsCSVFormattorParser()),

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
	# print(csvLine)
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
		# print(csvLine)
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


def parseCSV(csvFile4Import, updateParsingStatus, errorCollection, logger, deleteAfterParsing=True):

	result = list()	# List with printJobModels
	lineNumber = 0
	try:
		with open(csvFile4Import) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			lineNumber = 0
			for row in csv_reader:
				lineNumber += 1

				# import time
				# time.sleep(1)
				updateParsingStatus(str(lineNumber))

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
					# pre check, do we have values in the line?
					isEmptyLine = True
					for columnValue in row:
						if (StringUtils.isNotEmpty(columnValue)):
							isEmptyLine = False
							break
					if (isEmptyLine == True):
						# errorCollection.append("CSV Line: "+str(lineNumber)+" without values! <br/>")
						# just skip this line
						continue
					printJobModel = PrintJobModel()
					# parse line with header defined order
					columnIndex = 0
					for columnValue in row:
						if columnIndex in columnOrderInFile:
							csvColumn = columnOrderInFile[columnIndex]
							if not csvColumn == None:
								columnValue = columnValue.strip()
								# check if mandatory value is missing
								if (len(columnValue) == 0):
									columnName = csvColumn.columnLabel
									if columnName in mandatoryFieldNames:
										errorCollection.append("["+str(lineNumber)+"] Mandatory value for column '" + columnName + "' is missing!")
										pass
								else:
									csvColumn.parseAndAssignFieldValue(columnValue, printJobModel, errorCollection, lineNumber)
								pass
						columnIndex += 1
					if (len(errorCollection) != 0):
						logger.error("Reading error line '" + str(lineNumber) + "' in Column '" + column + "' ")
					else:
						result.append(printJobModel)
			pass
	except Exception as e:
		errorMessage = "CSV Parsing error. Line:'" + str(lineNumber) + "' Error:'" + str(e) + "' File:'" + csvFile4Import + "'"
		errorCollection.append(errorMessage)
		logger.error(errorMessage)
	finally:
		if (deleteAfterParsing):
			logger.info("Removing uploded csv temp-file")
			try:
				os.remove(csvFile4Import)
			except Exception:
				pass
	return result
