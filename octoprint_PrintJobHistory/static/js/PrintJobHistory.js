/*
 * View model for PrintJobHistory
 *
 * Author: OllisGit
 * License: AGPLv3
 */
$(function() {

    var PLUGIN_ID = "PrintJobHistory"; // from setup.py plugin_identifier

    ////////////////////////////////////////////////////////////
//    function formatFilamentLength(length){
//        var pattern = "%.02fm"
//        var result = _.sprintf(pattern, length)
//        return result
//    }


    ////////////////////////////////////////////////////////////
    var PrintJobItem = function(data) {

        // Init Item
		this.databaseId = ko.observable();
		this.userName = ko.observable();
		this.fileName = ko.observable();
		this.filePathName = ko.observable();
		this.fileSize = ko.observable();
		this.printStartDateTime = ko.observable();
		this.printEndDateTime = ko.observable();
		this.printStartDateTimeFormatted = ko.observable();
		this.printEndDateTimeFormatted = ko.observable();
		this.printStatusResult = ko.observable();
		this.durationFormatted = ko.observable();
		this.noteText = ko.observable();
		this.noteDeltaFormat = ko.observable();
		this.noteHtml = ko.observable();
		this.printedLayers = ko.observable();
		this.printedHeight = ko.observable();
		this.temperatureBed = ko.observable();
		this.temperatureNozzle = ko.observable();

		this.diameter = ko.observable();
		this.density = ko.observable();
		this.material = ko.observable();
        this.spoolVendor = ko.observable();
		this.spoolName = ko.observable();
		this.spoolCost = ko.observable();
		this.spoolCostUnit = ko.observable();
		this.spoolWeight = ko.observable();
		this.usedLengthFormatted = ko.observable();
		this.calculatedLengthFormatted = ko.observable();
		this.usedWeight = ko.observable();
		this.usedCost = ko.observable();

		this.snapshotFilename = ko.observable();
/*
        this.successful = ko.computed(function() {
            return this.success() == 1;
        }, this);
        this.filamentUsage = ko.computed(self.formatFilament, this);
        this.formattedDate = ko.computed(function () {
            return formatDate(this.timestamp());
        }, this);

*/
        // Fill Item with data
        this.update(data);
    }

    PrintJobItem.prototype.update = function (data) {
        var updateData = data || {}

        this.databaseId(updateData.databaseId);
        this.userName(updateData.userName);
        this.fileName(updateData.fileName);
        this.filePathName(updateData.filePathName);
        this.fileSize(formatSize(updateData.fileSize));
        this.printStartDateTime(updateData.printStartDateTime);
        this.printEndDateTime(updateData.printEndDateTime);
        this.printStartDateTimeFormatted(updateData.printStartDateTimeFormatted);
        this.printEndDateTimeFormatted(updateData.printEndDateTimeFormatted);
        this.printStatusResult(updateData.printStatusResult);
        this.durationFormatted(updateData.durationFormatted);
        this.noteText(updateData.noteText);
        this.noteDeltaFormat(updateData.noteDeltaFormat);
        this.noteHtml(updateData.noteHtml);
        this.printedLayers(updateData.printedLayers);
        this.printedHeight(updateData.printedHeight);

        // Flatten all releations
        // Temperature
        tempDataArray = data["temperatureModels"];
        // Just grab the first value
        if (tempDataArray != null && tempDataArray.length >=2) {
            this.temperatureBed(tempDataArray[0].sensorValue);
            this.temperatureNozzle(tempDataArray[1].sensorValue);
        } else {
            this.temperatureBed(updateData.temperatureBed);
            this.temperatureNozzle(updateData.temperatureNozzle);
        }

        //Filament
        if (updateData.filamentModel != null){
            this.diameter(updateData.filamentModel.diameter);
            this.density(updateData.filamentModel.density);
            this.material(updateData.filamentModel.material);
            this.spoolVendor(updateData.filamentModel.profileVendor);
            this.spoolName(updateData.filamentModel.spoolName);
            this.spoolCost(updateData.filamentModel.spoolCost);
            this.spoolCostUnit(updateData.filamentModel.spoolCostUnit);
            this.spoolWeight(updateData.filamentModel.spoolWeight);
//            this.usedLength( formatFilamentLength(updateData.filamentEntity.usedLength) );
//            this.calculatedLength( formatFilamentLength(updateData.filamentEntity.calculatedLength) );
            this.usedLengthFormatted( updateData.filamentModel.usedLengthFormatted );
            this.calculatedLengthFormatted( updateData.filamentModel.calculatedLengthFormatted );
            this.usedWeight( updateData.filamentModel.usedWeight );
            this.usedCost( updateData.filamentModel.usedCost );
        } else {
            this.diameter(updateData.diameter);
            this.density(updateData.density);
            this.material(updateData.material);
            this.spoolVendor(updateData.spoolVendor);
            this.spoolName(updateData.spoolName);
            this.spoolCost(updateData.spoolCost);
            this.spoolCostUnit(updateData.spoolCostUnit);
            this.spoolWeight(updateData.spoolWeight);
//            this.usedLength( formatFilamentLength(updateData.filamentEntity.usedLength) );
//            this.calculatedLength( formatFilamentLength(updateData.filamentEntity.calculatedLength) );
            this.usedLengthFormatted( updateData.usedLengthFormatted );
            this.calculatedLengthFormatted( updateData.calculatedLengthFormatted );
            this.usedWeight( updateData.usedWeight );
            this.usedCost( updateData.usedCost );
        }

		this.snapshotFilename(updateData.snapshotFilename);
    };


    var TableAttributeVisibility = function (){
        this.status = ko.observable(true);
        this.user = ko.observable(true);
        this.date = ko.observable(true);
        this.startDateTime = ko.observable(true);
        this.endDateTime = ko.observable(true);
        this.duration = ko.observable(true);
        this.file = ko.observable(true);
        this.fileName = ko.observable(true);
        this.fileSize = ko.observable(true);
        this.tempBed = ko.observable(true);
        this.tempTool = ko.observable(true);
        this.height = ko.observable(true);
        this.layer = ko.observable(true);
        this.usage = ko.observable(true);
        this.material = ko.observable(true);
        this.spoolVendor = ko.observable(true);
        this.spool = ko.observable(true);
        this.usedLength = ko.observable(true);
        this.usedWeight = ko.observable(true);
        this.note = ko.observable(true);
        this.image = ko.observable(true);
    }


    ////////////////////////////////////////////////////////////////////////////// VIEW MODEL
    function PrintjobhistoryViewModel(parameters) {

        var self = this;

/// START MOCK MODEL
        var printHistoryJobItems = [
             {
                "databaseId" : ko.observable(1),
                "success" : ko.observable("1"),
                "printStartDateTimeFormatted" : "19.09.2019 16:25",
                "printEndDateTimeFormatted" : "19.09.2019 17:25",
                "printStatusResult" : ko.observable("success"),
                "durationFormatted" : "1h12min",
                "fileName" : "Legolas.gcode",
                "fileSize" : "134KB",
                "temperatureBed" : "50C",
                "temperatureNozzle" : "200C",
                "printedHeight" : "23mm / 23mm",
                "printedLayers" : "149 / 149",
                "spoolName" : "myspool",
                "spoolCost" : "2,23",
                "spoolCostUnit" : "Euro",
                "material" : "PLA",
                "usedLengthFormatted" : "1m22mm",
                "calculatedLengthFormatted" : "12,5g",
                "usedWeight" : "12,5g",
                "usedCost" : "0,003",
                "noteText" : "Good output of Legolas",
                "noteDeltaFormat" : "Good output of Legolas",
                "noteHtml" : "<h1>Good output of Legolas</h1>",
                "snapshotFilename" : ko.observable("20191003-123322")

            },{
                "databaseId" : ko.observable(2),
                "success" : ko.observable("0"),
                "printStartDateTimeFormatted" : "20.09.2019 15:25",
                "printEndDateTimeFormatted" : "20.09.2019 17:25",
                "printStatusResult" : ko.observable("fail"),
                "durationFormatted" : "2h34min",
                "fileName" : "Benchy3D.gcode",
                "fileSize" : "324KB",
                "temperatureBed" : "60C",
                "temperatureNozzle" : "220C",

                "printedHeight" : "13mm / 143mm",
                "printedLayers" : "3 / 68",
                "spoolName" : "Master",
                "spoolCost" : "2,23",
                "spoolCostUnit" : "Euro",
                "material" : "ABS",
                "usedLengthFormatted" : "2m22mm",
                "calculatedLengthFormatted" : "312,6g",
                "usedWeight" : "312,6g",
                "usedCost" : "1,34",

                "noteText" : "Bad quality",
                "noteDeltaFormat" : "Bad quality",
                "noteHtml" : "<h2>Bad quality,/h2>",
                "snapshotFilename" : ko.observable("20191003-153312")

            }
        ];
//        self.printJobHistorylistHelper.updateItems(printHistoryJobItems);

/// END MOCK MODEL

        // assign the injected parameters, e.g.:
        self.loginStateViewModel = parameters[0];
        self.loginState = parameters[0];
        self.settingsViewModel = parameters[1];
        self.pluginSettings = null;

        self.apiClient = new PrintJobHistoryAPIClient(PLUGIN_ID, BASEURL);
        self.componentFactory = new ComponentFactory(PLUGIN_ID);
        self.printJobEditDialog = new PrintJobHistoryEditDialog(null, null);
        self.pluginCheckDialog = new PrintJobHistoryPluginCheckDialog();

        self.printJobForEditing = ko.observable();
        self.printJobForEditing(new PrintJobItem(printHistoryJobItems[0]));

        self.printJobToShowAfterStartup = null;
        self.missingPluginDialogMessage = null;

        //self.tableAttributeVisibility = ko.observable();
        self.tableAttributeVisibility = new TableAttributeVisibility();

        self.csvFileUploadName = ko.observable();
        self.csvImportInProgress = ko.observable(false);

        self.databaseFileLocation = ko.observable();
        self.snapshotFileLocation = ko.observable();
        ////////////////////////////////////////////////////// Knockout model-binding/observer


        ///////////////////////////////////////////////////// START: SETTINGS
        self.deleteDatabaseAction = function() {
            var result = confirm("Do you really want to delete all printjob history data?");
            if (result == true){
                self.apiClient.callDeleteDatabase(function(responseData) {
                    self.printJobHistoryTableHelper.reloadItems();
                });
            }
        };

        self.downloadDatabaseUrl = ko.observable();


        self.csvImportUploadButton = $("#settings-pjh-importcsv-upload");
        self.csvImportUploadData = undefined;
        self.csvImportUploadButton.fileupload({
            dataType: "json",
            maxNumberOfFiles: 1,
            autoUpload: false,
            headers: OctoPrint.getRequestHeaders(),
            add: function(e, data) {
                if (data.files.length === 0) {
                    // no files? ignore
                    return false;
                }

                self.csvFileUploadName(data.files[0].name);
                self.csvImportUploadData = data;
            },
            done: function(e, data) {
                self.csvFileUploadName(undefined);
                self.csvImportUploadData = undefined;
            },
            error: function(response, data, errorMessage){
                self.csvImportInProgress(false);
                statusCode = response.status;       // e.g. 400
                statusText = response.statusText;   // e.g. BAD REQUEST
                responseText = response.responseText; // e.g. Invalid request
            }
        });

        self.performCSVImportFromUpload = function() {
            if (self.csvImportUploadData === undefined) return;

            self.csvImportInProgress(true);
            self.csvImportUploadData.submit();
        };

        self.sampleCSVUrl = function(printJobItem){
            return self.apiClient.getSampleCSVUrl();
        }

        ///////////////////////////////////////////////////// END: SETTINGS

        ///////////////////////////////////////////////////// START: OctoPrint Hooks

        self.onBeforeBinding = function() {
            // assign current pluginSettings
            self.pluginSettings = self.settingsViewModel.settings.plugins[PLUGIN_ID];
            self.printJobEditDialog.init(self.apiClient, self.settingsViewModel.settings.webcam);
            self.pluginCheckDialog.init(self.apiClient, self.pluginSettings);

            initTableVisibilities();

            // resetSettings-Stuff
             new ResetSettingsUtilV2(self.pluginSettings).assignResetSettingsFeature(PLUGIN_ID, function(data){
                // no additional reset function
             });
        }

        self.onAfterBinding = function() {
            // all inits were done
            self.downloadDatabaseUrl(self.apiClient.getDownloadDatabaseUrl());
            // to bring up dialogs the binding must be already done
            if (self.printJobToShowAfterStartup != null){
                self.showPrintJobDetailsDialogAction(self.printJobToShowAfterStartup);
            }
            if (self.missingPluginDialogMessage != null){
                self.pluginCheckDialog.showMissingPluginsDialog(self.missingPluginDialogMessage);
                self.missingPluginDialogMessage = null;
            }
        }

        // receive data from server
        self.onDataUpdaterPluginMessage = function (plugin, data) {

            if (plugin != PLUGIN_ID) {
                return;
            }

            if ("updateStorageInformation" == data.action){
                self.databaseFileLocation(data.databaseFileLocation);
                self.snapshotFileLocation(data.snapshotFileLocation);
            }

            if ("missingPlugin" == data.action){
                // NOT POSSIBLE, because init not done
                if (self.pluginCheckDialog != null && self.pluginCheckDialog.isInitialized()){
                    self.pluginCheckDialog.showMissingPluginsDialog(data.message);
                } else {
                    // save message for later use
                    self.missingPluginDialogMessage = data.message;
                }
                return;
            }

            if ("printFinished" == data.action){
                self.printJobHistoryTableHelper.reloadItems();
                if (data.printJobItem != null){
                    self.printJobToShowAfterStartup = data.printJobItem;
                    self.showPrintJobDetailsDialogAction(data.printJobItem);
                }
                return;
            }

            if ("showPrintJobDialogAfterClientConnection" == data.action){
                if (data.printJobItem != null){
                    self.printJobToShowAfterStartup = data.printJobItem;
                    self.showPrintJobDetailsDialogAction(data.printJobItem);
                }
                return;
            }

            if ("csvImportResult" == data.action){
                self.csvImportInProgress(false);

//                new PNotify({
//                    title: 'Attention',
//                    text: notifyMessage,
//                    type: notfiyType,
//                    hide: false
//                    });
                messageText = data.errorCollection.join(" <br> ")
                new PNotify({
                    title: data.message,
                    text: messageText
//                    type: notfiyType,
//                    hide: false
                    });

                return;
            }
            self.csvImportInProgress(false);
            if ("errorPopUp" == data.action){
                new PNotify({
                    title: 'ERROR:' + data.title,
                    text: data.message,
                    type: "error",
                    hide: false
                    });

                return;
            }
        }

        self.onTabChange = function(next, current){
            //alert("Next:"+next +" Current:"+current);
            if ("#tab_plugin_PrintJobHistory" == next){
                //self.reloadTableData();
            }
        }

        ///////////////////////////////////////////////////// END: OctoPrint Hooks



        ///////////////////////////////////////////////////// START: DIALOG Stuff


        self.showPrintJobDetailsDialogAction = function(selectedPrintJobItem) {

            self.printJobForEditing(new PrintJobItem(ko.mapping.toJS(selectedPrintJobItem)));

            self.printJobEditDialog.showDialog(self.printJobForEditing(), function(shouldTableReload){
                if (shouldTableReload == true){
                    self.printJobHistoryTableHelper.reloadItems();
                }

                if (self.printJobToShowAfterStartup != null){
                    // PrintJob was presented to user and user confirmed
                    self.printJobToShowAfterStartup = null;
                    payload = {
                        "showPrintJobDialogAfterPrint_jobId": null
                    };
                    OctoPrint.settings.savePluginSettings(PLUGIN_ID, payload);
                }
            });
        };

        ///////////////////////////////////////////////////// END: DIALOG Stuff



        //////////// TABLE BEHAVIOR
        initTableVisibilities = function(){
            // load all settings from browser storage
            if (!Modernizr.localstorage) {
                // damn!!!
                return false;
            }

            assignVisibility = function(attributeName){
                var storageKey = "pjh.table.visible." + attributeName;
                if (localStorage[storageKey] == null){
                    localStorage[storageKey] = true
                } else {
                    self.tableAttributeVisibility[attributeName]( "true" == localStorage[storageKey]);
                }
                self.tableAttributeVisibility[attributeName].subscribe(function(newValue){
                    localStorage[storageKey] = newValue;
                });
            }

            assignVisibility("status");
            assignVisibility("user");
            assignVisibility("date");
            assignVisibility("startDateTime");
            assignVisibility("endDateTime");
            assignVisibility("duration");
            assignVisibility("file");
            assignVisibility("fileName");
            assignVisibility("fileSize");
            assignVisibility("tempBed");
            assignVisibility("tempTool");
            assignVisibility("height");
            assignVisibility("layer");
            assignVisibility("usage");
            assignVisibility("material");
            assignVisibility("spoolVendor");
            assignVisibility("spool");
            assignVisibility("usedLength");
            assignVisibility("usedWeight");
            assignVisibility("note");
            assignVisibility("image");
        }

        loadJobFunction = function(tableQuery, observableTableModel, observableTotalItemCount){
            // api-call
            self.apiClient.callLoadPrintJobsByQuery(tableQuery, function(responseData){
                totalItemCount = responseData["totalItemCount"];
                allPrintJobs = responseData["allPrintJobs"];
                var dataRows = ko.utils.arrayMap(allPrintJobs, function (data) {
                    return new PrintJobItem(data);
                });

                observableTotalItemCount(totalItemCount);
                observableTableModel(dataRows);

            });
        }

        self.printJobHistoryTableHelper = new TableItemHelper(loadJobFunction, 10, "printStartDateTime", "all");

        self.exportUrl = function(exportType) {
            if (self.printJobHistoryTableHelper.items().length > 0) {
                return self.apiClient.getExportUrl(exportType)
            } else {
                return false;
            }
        };


//        self.handleAllPrintJobDataResponse = function (allPrintJobs){
//            // Print Jobs from Backend
//            var dataRows = ko.utils.arrayMap(allPrintJobs, function (data) {
//                return new PrintJobItem(data);
//            });
//
//            //self.pureData = data.history;
//
//            //self.dataIsStale = false;
//            self.printJobHistorylistHelper.updateItems(dataRows);
//        }

        self.sortOrderLabel = function(orderType) {
            var order = "";

            if (orderType == "fileName") {
                order = (self.printJobHistorylistHelper.currentSorting() == 'fileNameAsc') ? '(' + _('ascending') + ')' : (self.printJobHistorylistHelper.currentSorting() == 'fileNameDesc') ? '(' + _('descending') + ')' : '';
            } else if (orderType == "startDateTime") {
                order = (self.printJobHistorylistHelper.currentSorting() == 'startDateTimeAsc') ? '(' + _('ascending') + ')' : (self.printJobHistorylistHelper.currentSorting() == 'startDateTimeDesc') ? '(' + _('descending') + ')' : '';
            }
            return order;
        };


        self.changeSortOrder = function(columnToSort) {
            if ("fileName" == columnToSort){
                if (self.printJobHistorylistHelper.currentSorting() == "fileNameAsc") {
                    self.printJobHistorylistHelper.changeSorting("fileNameDesc");
                } else {
                    self.printJobHistorylistHelper.changeSorting("fileNameAsc");
                }
            }
            if ("startDateTime" == columnToSort){
                if (self.printJobHistorylistHelper.currentSorting() == "startDateTimeAsc") {
                    self.printJobHistorylistHelper.changeSorting("startDateTimeDesc");
                } else {
                    self.printJobHistorylistHelper.changeSorting("startDateTimeAsc");
                }
            }
        };


        self.snapshotUrl = function(printJobItem){
            return self.apiClient.getSnapshotUrl(printJobItem.snapshotFilename());
        }

        self.removePrintJobAction = function(printJobItem) {
            var result = confirm("Do you really want to delete the print job?");
            if (result == true){
                self.apiClient.callRemovePrintJob(printJobItem.databaseId(), function(responseData) {
                    self.printJobHistoryTableHelper.reloadItems();
                });
            }
        };

    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: PrintjobhistoryViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [
            "loginStateViewModel",
            "settingsViewModel"
        ],
        // Elements to bind to, e.g. #settings_plugin_PrintJobHistory, #tab_plugin_PrintJobHistory, ...
        elements: [
            document.getElementById("tab_printJobHistory"),
            document.getElementById("settings_printJobHistory"),
            document.getElementById("modal-dialogs-printJobHistory")
        ]
    });
});
