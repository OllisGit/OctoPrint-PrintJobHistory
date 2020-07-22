# -*- encoding: utf-8 -*-

import os
import logging
import tempfile
import lzma
from octoprint_PrintJobHistory.common.SlicerSettingsParser import SlicerSettingsParser

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "testdata", "gcode")


def test_decodes_bytes_correctly():

    ssp = SlicerSettingsParser(logging.root)
    with tempfile.TemporaryDirectory() as tmpd:
        gcode_fn = os.path.join(tmpd, "treefrog.gcode")

        with lzma.open(os.path.join(FIXTURES, "Treefrog_0.2mm_FLEX_MK3S_1h5m.gcode.xz")) as ifp:
            with open(gcode_fn, "wb") as ofp:
                ofp.write(ifp.read())

        slicerSettings = ssp.extractSlicerSettings(gcode_fn, None)

    assert slicerSettings.settingsAsText
    assert "Printer Settings → Extruder 1" in slicerSettings.settingsAsText
