# coding=utf-8
from __future__ import absolute_import

import logging
import os
import re

class SlicerSettingsService(object):

	class SlicerSettingsJob:
		databaseId = 0
		fileName = ""
		slicerSettingsAsText = ""
		keyValuesSettings = {}

	class SlicerSettingsCompareResult:
		allKeys = []
		slicerSettingsJobList = []
		pass

	def __init__(self, parentLogger):
		self._logger = logging.getLogger(parentLogger.name + "." + self.__class__.__name__)
		# self._logger.setLevel(logging.DEBUG)
		self._allSlicerPatterns = []

	def compareSlicerSettings(self, slicerSettingsJobList, slicerSettingsExpressions):

		self._parseSlicerExpressions(slicerSettingsExpressions)

		allKeys = []
		for slicerSettingsJob in slicerSettingsJobList:
			slicerSettingsJob.keyValuesSettings = self.parseKeyValues(slicerSettingsJob.slicerSettingsAsText, allKeys)

		allKeys = sorted(allKeys)
		compareResult = self.markDiff(allKeys, slicerSettingsJobList)

		return compareResult

	def parseKeyValues(self, jobSettings, allKeys):
		keyValueSettings = {}
		if (jobSettings != None):
			settingsLines = jobSettings.splitlines(False)
			for line in settingsLines:

				# KeyValue extraction
				# ;   (.*),(.*)
				# ;(.*)=(.*)
				for slicerPattern in self._allSlicerPatterns:
					matched = slicerPattern.match(line)
					if (matched):
						# if ('=' in line):
						# 	keyValue = line.split('=', 1) # 1 == only the first =
						# 	key = keyValue[0].strip()
						# 	value = keyValue[1].strip()
						key = str(matched.group(1)).strip()
						value = str(matched.group(2)).strip()

						keyValueSettings[key] = {"key": key, "value":value }
						# keyValueSettings["value"] = value
						#
						# keyValueSettings["key"] = key
						# keyValueSettings["value"] = value

						if ( (key in allKeys) == False):
							allKeys.append(key)
						# print("Key:" + key)
						# print("Value:" + value)
						# print()
		return keyValueSettings

	def markDiff(self, allKeys, slicerSettingsJobList):

		compareResult = SlicerSettingsService.SlicerSettingsCompareResult()
		compareResult.allKeys = allKeys
		compareResult.slicerSettingsJobList = slicerSettingsJobList
		for currentKey in allKeys:

			diffCount = 0
			# loop over all jobs and look for the key

			firstKeyValue = {}
			index = 0
			for slicerSettingsJob in slicerSettingsJobList:
				if (index == 0):
					if (currentKey in slicerSettingsJob.keyValuesSettings):
						firstKeyValue = slicerSettingsJob.keyValuesSettings[currentKey]
						index = index + 1
						continue
					else:
						firstKeyValue = {
							"key": currentKey,
							"value": "NOT PRESENT",
							"isDifferent": "no" # use no, because we don't want to colorize the first column
						}
						slicerSettingsJob.keyValuesSettings[currentKey] = firstKeyValue
						index = index + 1
						continue
				index = index + 1
				isDiffResult = "no"
				if (currentKey in slicerSettingsJob.keyValuesSettings):
					currentKeyValue = slicerSettingsJob.keyValuesSettings[currentKey]
					if (currentKeyValue["value"] != firstKeyValue["value"] ):
						isDiffResult = "yes"
					slicerSettingsJob.keyValuesSettings[currentKey]["isDifferent"] = isDiffResult
					pass
				else:
					slicerSettingsJob.keyValuesSettings[currentKey] = {
						"key": currentKey,
						"value": "NOT PRESENT",
						"isDifferent": "notPresent"
					}
					pass

		return compareResult

	def _parseSlicerExpressions(self, slicerSettingsExpressions):
		self._allSlicerPatterns = []
		# slicerSettingsExpressions = ;(.*)=(.*)\n;   (.*),(.*)
		lines = slicerSettingsExpressions.split("\n")
		try:
			for line in lines:
				if (len(line.strip()) == 0):
					continue
				slicerExpression = re.compile(line)
				self._allSlicerPatterns.append(slicerExpression)
		except (ValueError, RuntimeError) as error:
			self._logger.exception(""+str(error))
		pass
