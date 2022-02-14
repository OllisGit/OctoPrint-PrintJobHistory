# coding=utf-8
from __future__ import absolute_import

import logging


class ResetAbleLogFileHandler(logging.FileHandler):

	def __init__(self, filename, loggerNameToCapture):
		logging.FileHandler.__init__(self, filename)

		self.loggingStarted = False
		self.loggerNameToCapture = loggerNameToCapture

	# def assignLoggerNameToCapture(self, loggerNameToCapture):
	# 	self.loggerNameToCapture = loggerNameToCapture

	def emit(self, record):
		if (self.loggingStarted):
			name = record.name  # octoprint.plugins.SpoolManager
			if (name.startswith(self.loggerNameToCapture)):
				# super(logging.FileHandler, self).emit(record)
				logging.FileHandler.emit(self, record)

	def startLogging(self):
		self.loggingStarted = True

	def stopLogging(self):
		self.loggingStarted = False

	def resetLog(self):
		self.close()
		import os
		os.remove(self.baseFilename)

	def readLogContent(self):
		self.close()
		# self.baseFilename = os.path.abspath(filename)
		with open(self.baseFilename) as f:
			contents = f.read()
			return contents
