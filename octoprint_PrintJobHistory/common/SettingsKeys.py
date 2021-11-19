# coding=utf-8
from __future__ import absolute_import

class SettingsKeys():

	# All dependent P3rd Party Plugins
	PLUGIN_PREHEAT = { "key": "preheat", "minVersion": "0.4.0"}
	PLUGIN_FILAMENT_MANAGER = { "key": "filamentmanager", "minVersion": "1.7.2"}
	PLUGIN_DISPLAY_LAYER_PROGRESS = { "key": "DisplayLayerProgress", "minVersion": "1.26.0"}
	PLUGIN_SPOOL_MANAGER = { "key": "SpoolManager", "minVersion": "1.4.2"}
	PLUGIN_ULTIMAKER_FORMAT_PACKAGE = { "key": "UltimakerFormatPackage", "minVersion": "1.0.0"}
	PLUGIN_PRUSA_SLICER_THUMNAIL = { "key": "prusaslicerthumbnails", "minVersion": "1.0.0"}
	PLUGIN_COST_ESTIMATION = { "key": "costestimation", "minVersion": "3.4.0"}
	PLUGIN_PRINT_HISTORY = { "key": "printhistory", "minVersion": None}

	## General
	SETTINGS_KEY_PLUGIN_DEPENDENCY_CHECK = "pluginCheckActivated"
	SETTINGS_KEY_SHOW_PRINTJOB_DIALOG_AFTER_PRINT = "showPrintJobDialogAfterPrint"
	SETTINGS_KEY_SHOW_PRINTJOB_DIALOG_AFTER_PRINT_JOB_ID = "showPrintJobDialogAfterPrint_jobId"

	SETTINGS_KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE = "showPrintJobDialogAfterPrintMode"
	KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE_ALWAYS = "always"
	KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE_SUCCESSFUL = "successful"
	KEY_SHOWPRINTJOBDIALOGAFTERPRINT_MODE_FAILED = "failed"

	SETTINGS_KEY_CAPTURE_PRINTJOBHISTORY_MODE = "capturePrintJobHistoryMode"
	KEY_CAPTURE_PRINTJOBHISTORY_MODE_NONE = "none"
	KEY_CAPTURE_PRINTJOBHISTORY_MODE_ALWAYS = "always"
	KEY_CAPTURE_PRINTJOBHISTORY_MODE_SUCCESSFUL = "successful"

	SETTINGS_KEY_SELECTED_FILAMENTTRACKER_PLUGIN = "selectedFilamentTrackerPlugin"
	KEY_SELECTED_SPOOLMANAGER_PLUGIN = "SpoolManager Plugin"	# visible inn plugin-settings
	KEY_SELECTED_FILAMENTMANAGER_PLUGIN = "FilamentManager Plugin"	# visible inn plugin-settings
	KEY_SELECTED_NONE_PLUGIN = "none"
	SETTINGS_KEY_NO_NOTIFICATION_FILAMENTTRACKERING_PLUGIN_SELECTION = "noNotificationTrackingPluginSelection"


	SETTINGS_KEY_CURRENCY_SYMBOL = "currencySymbol"
	SETTINGS_KEY_CURRENCY_FORMAT = "currencyFormat"

	SETTINGS_KEY_SLICERSETTINGS_KEYVALUE_EXPRESSION = "slicerSettingsKeyValueExpression"
	SETTINGS_KEY_SINGLE_PRINTJOB_REPORT_TEMPLATENAME = "singlePrintJobTemplateName"
	SETTINGS_DEFAULT_VALUE_SINGLE_PRINTJOB_REPORT_TEMPLATENAME = "defaultSinglePrintJobReport"

	## Camera
	SETTINGS_KEY_TAKE_SNAPSHOT_AFTER_PRINT = "takeSnapshotAfterPrint"
	SETTINGS_KEY_TAKE_PLUGIN_THUMBNAIL_AFTER_PRINT = "takePluginThumbnailAfterPrint"
	SETTINGS_KEY_TAKE_SNAPSHOT_ON_GCODE_COMMAND = "takeSnapshotOnGCodeCommnd"
	SETTINGS_KEY_TAKE_SNAPSHOT_GCODE_COMMAND_PATTERN = "takeSnapshotGCodeCommndPattern"
	SETTINGS_KEY_PREFERED_IMAGE_SOURCE = "preferedImageSource"
	KEY_PREFERED_IMAGE_SOURCE_THUMBNAIL = "thumbnail"
	KEY_PREFERED_IMAGE_SOURCE_CAMERA = "camera"

	# Temperatrue
	SETTINGS_KEY_DEFAULT_TOOL_ID = "defaultTemperatureToolId"
	SETTINGS_KEY_TAKE_TEMPERATURE_FROM_PREHEAT = "takeTemperatureFromPreHeatPlugin"
	SETTINGS_KEY_DELAY_READING_TEMPERATURE_FROM_PRINTER = "delayReadingTemperatureFromPrinter"

	## Export / Import
	SETTINGS_KEY_IMPORT_CSV_MODE = "importCSVMode"
	KEY_IMPORTCSV_MODE_REPLACE = "replace"
	KEY_IMPORTCSV_MODE_APPEND = "append"

	## Storage
	SETTINGS_KEY_DATABASE_PATH = "databaseFileLocation"
	SETTINGS_KEY_SNAPSHOT_PATH = "snapshotFileLocation"

	## Debugging
	SETTINGS_KEY_SQL_LOGGING_ENABLED = "sqlLoggingEnabled"

	# Other stuff
	SETTINGS_KEY_MESSAGE_CONFIRM_DATA = "messageConfirmData"
	SETTINGS_KEY_LAST_PLUGIN_DEPENDENCY_CHECK = "lastPluginDependencyCheck"
