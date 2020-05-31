from octoprint_PrintJobHistory import DatabaseManager
from octoprint_PrintJobHistory.common import StringUtils
import logging

databaselocation = "/Users/o0632/Library/Application Support/OctoPrint/data/PrintJobHistory/"

def clientOutput(message1, message2):
	print(message1)
	print(message2)

testLogger = logging.getLogger("testLogger")
logging.info("Start Database-Test")
databaseManager = DatabaseManager(testLogger, True)
databaseManager.initDatabase(databaselocation, clientOutput)


def convert(value):
	result = StringUtils.to_native_str(value)
	print(result)

# def convert(value):
# 	result = value  #okay, take str
# 	if (not isinstance(value, str)):
# 		# okay, it is not a string. Maybe unicode
# 		result = value.encode("utf-8")
# 	return result

printJob = databaseManager.loadPrintJob(1)
# python2 -> unicode
# python3 -> str (es gibt kein unicode)
fileName = printJob.fileName
convert(fileName)
fileSize = printJob.fileSize
convert(fileSize)
printStartDateTime = printJob.printStartDateTime
convert(printStartDateTime)
diameter = printJob.loadFilamentFromAssoziation().diameter
convert(diameter)

