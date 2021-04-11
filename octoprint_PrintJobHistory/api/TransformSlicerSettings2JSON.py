# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.services.SlicerSettingsService import SlicerSettingsService


def transformSlicerSettingsCompareResult(compareResult):

	def serialize(obj):
		"""JSON serializer for objects not serializable by default json code"""
		if (isinstance(obj, SlicerSettingsService.SlicerSettingsJob)):
			# we don't need the settings as text
			obj.slicerSettingsAsText = ""
		return obj.__dict__

	import json
	compareResultAsJson = json.dumps(compareResult.__dict__, default=serialize, indent=4)
	return compareResultAsJson


