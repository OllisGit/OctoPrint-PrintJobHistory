# -*- encoding: utf-8 -*-

import logging

from octoprint_PrintJobHistory.common import StringUtils
from octoprint_PrintJobHistory.common.SlicerSettingsParser import SlicerSettingsParser


def test_parseSettings():

	gcodeForParsing="../../testdata/slicer-settings/PRUSA_Treefrog_0.2mm_FLEX_MK3S_1h5m.gcode"

	testLogger = logging.getLogger("testLogger")
	settingsParser = SlicerSettingsParser(testLogger)

	slicerSettings = settingsParser.extractSlicerSettings(gcodeForParsing, ";(.*)=(.*)")
	assert slicerSettings.settingsAsText
	assert 245 == len(slicerSettings.settingsAsDict)
	assert "Printer Settings → Extruder 1" in  StringUtils.to_native_str(slicerSettings.settingsAsText)
	assert "80°, I'm printing at 40°" in StringUtils.to_native_str(slicerSettings.settingsAsText)

	gcodeForParsing="../../testdata/slicer-settings/CURA_schieberdeckel2.gcode"
	slicerSettings = settingsParser.extractSlicerSettings(gcodeForParsing, ";(.*)=(.*)")
	assert slicerSettings.settingsAsText
	assert 4 == len(slicerSettings.settingsAsDict)
	assert "Cura" in slicerSettings.settingsAsText
	assert "bottom_layers" in slicerSettings.settingsAsText

	print(" Test passed")
	pass

def test_slicerexpresions():
	testLogger = logging.getLogger("testLogger")
	settingsParser = SlicerSettingsParser(testLogger)
	settingsParser._parseSlicerExpressions(";(.*)=(.*)\n;   (.*),(.*)")

if __name__ == '__main__':
	print("Start SlicerSettingsParser Test")
	# test_parseSettings()
	# test_slicerexpresions()
	print("Finished")

