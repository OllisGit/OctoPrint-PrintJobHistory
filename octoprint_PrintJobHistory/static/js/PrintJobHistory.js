/*
 * View model for PrintJobHistory
 *
 * Author: OllisGit
 * License: AGPLv3
 */
$(function() {

    ////////////////////////////////////////////////////////////
//    function formatFilamentLength(length){
//        var pattern = "%.02fm"
//        var result = _.sprintf(pattern, length)
//        return result
//    }

    var global = this;
    global.componentFactory = new PrintJobComponentFactory();
    ////////////////////////////////////////////////////////////
    var PrintJobItem = function(data) {

        // Init Item
		this.databaseId = ko.observable();
		this.userName = ko.observable();
		this.fileName = ko.observable();
		this.filePathName = ko.observable();
		this.fileSize = ko.observable();

        var printStartDateTimeViewModel = global.componentFactory.createDateTimePicker("printStartDateTime-picker");
		this.printStartDateTimeFormatted = printStartDateTimeViewModel.currentDateTime;
		this.printStartDateTime = ko.observable();
//		this.printStartDateTimeFormatted = ko.observable();

        var printEndDateTimeViewModel = global.componentFactory.createDateTimePicker("printEndDateTime-picker");
		this.printEndDateTimeFormatted = printEndDateTimeViewModel.currentDateTime;
		this.printEndDateTime = ko.observable();
//		this.printEndDateTimeFormatted = ko.observable();

		this.printStatusResult = ko.observable();
		this.duration = ko.observable();
		this.durationFormatted = ko.observable();
		this.noteText = ko.observable();
		this.noteDeltaFormat = ko.observable();
		this.noteHtml = ko.observable();
		this.printedLayers = ko.observable();
		this.printedHeight = ko.observable();
		this.temperatureBed = ko.observable();
		this.temperatureNozzle = ko.observable();

//        this.usedSpoolManagerPlugin = ko.observable();
//        this.spoolItem = ko.observable();
		this.diameter = ko.observable();
		this.density = ko.observable();
		this.material = ko.observable();
        this.vendor = ko.observable();
		this.spoolName = ko.observable();
		this.spoolCost = ko.observable();
		this.spoolCostUnit = ko.observable();
		this.weight = ko.observable();
		this.usedLengthFormatted = ko.observable();
		this.calculatedLengthFormatted = ko.observable();
		this.usedWeight = ko.observable(""); // empty sting, because length-check is needed in PringHistory_tab.jinja2
		this.usedCost = ko.observable();

		this.snapshotFilename = ko.observable();
		this.slicerSettingsAsText = ko.observable();

		this.isMultiToolPrint = ko.observable(false);
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
        if ( isNaN(updateData.fileSize)){
            this.fileSize(updateData.fileSize);
        } else {
            this.fileSize(formatSize(updateData.fileSize));
        }
        this.printStartDateTime(updateData.printStartDateTime);
        this.printEndDateTime(updateData.printEndDateTime);
        this.printStartDateTimeFormatted(updateData.printStartDateTimeFormatted);
        this.printEndDateTimeFormatted(updateData.printEndDateTimeFormatted);
        this.printStatusResult(updateData.printStatusResult);
        this.duration(updateData.duration);
        this.durationFormatted(updateData.durationFormatted);
        this.noteText(updateData.noteText);
        this.noteDeltaFormat(updateData.noteDeltaFormat);
        if (updateData.noteHtml != null){
            this.noteHtml(updateData.noteHtml);
        } else {
            // Fallback text
            this.noteHtml(updateData.noteText);
        }

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

//        this.usedSpoolManagerPlugin(updateData.usedSpoolManagerPlugin);
//        if (updateData.spoolItemData != null){
//            this.spoolItem = self.spoolDialog.createSpoolItemForTable(updateData.spoolItemData);
//        } else {
//            this.spoolItem = null;
//        }

        //Filament
        if (updateData.filamentModels == null){
            if (updateData.allFilamentModels != null) {
                updateData.filamentModels = updateData.allFilamentModels;
            }
        }
        if (updateData.filamentModels != null && Object.keys(updateData.filamentModels).length != 0){
            // result from backend

            this.allFilamentModels = updateData.filamentModels;
            this.allToolKeys = Object.keys(this.allFilamentModels);
            this.isMultiToolPrint(Object.keys(this.allFilamentModels).length > 1)

            totalFilamentModel = updateData.filamentModels["total"];    // should always be present
            // should never happen, but in the past we have some jobs where "total" is missing
            if (totalFilamentModel != null){
                this.diameter(totalFilamentModel.diameter);
                this.density(totalFilamentModel.density);
                this.material(totalFilamentModel.material);
                this.vendor(totalFilamentModel.vendor);
                this.spoolName(totalFilamentModel.spoolName);
                this.spoolCost(totalFilamentModel.spoolCost);
                this.spoolCostUnit(totalFilamentModel.spoolCostUnit);
                this.weight(totalFilamentModel.weight);
    //            this.usedLength( formatFilamentLength(updateData.filamentEntity.usedLength) );
    //            this.calculatedLength( formatFilamentLength(updateData.filamentEntity.calculatedLength) );
                this.usedLengthFormatted(totalFilamentModel.usedLengthFormatted );
                this.calculatedLengthFormatted(totalFilamentModel.calculatedLengthFormatted );
                this.usedWeight(totalFilamentModel.usedWeight );
                this.usedCost(totalFilamentModel.usedCost );
            }
        }

		this.snapshotFilename(updateData.snapshotFilename);
		this.slicerSettingsAsText(updateData.slicerSettingsAsText)
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
        this.vendor = ko.observable(true);
        this.spool = ko.observable(true);
        this.usedLength = ko.observable(true);
        this.usedWeight = ko.observable(true);
        this.note = ko.observable(true);
        this.image = ko.observable(true);
    }


    ////////////////////////////////////////////////////////////////////////////// VIEW MODEL
    function PrintjobhistoryViewModel(parameters) {

        var PLUGIN_ID = "PrintJobHistory"; // from setup.py plugin_identifier

        var self = this;

/// START MOCK MODEL
        var emptyPrintJobItemAsJson = {
                "databaseId" : null,
                "printStartDateTimeFormatted" : "",
                "printEndDateTimeFormatted" : "",
                "printStatusResult" : "success",
                "duration" : "",
                "durationFormatted" : "",
                "fileName" : "",
                "fileSize" : "",
                "temperatureBed" : "0.0",
                "temperatureNozzle" : "0.0",
                "printedHeight" : "0.0 / 0.0",
                "printedLayers" : "0 / 0",
                "spoolName" : "",
                "spoolCost" : "",
                "spoolCostUnit" : "TODO",
                "material" : "",
                "usedLengthFormatted" : "",
                "calculatedLengthFormatted" : "",
                "usedWeight" : "",
                "usedCost" : "",
                "noteText" : "",
                "noteDeltaFormat" : null,
                "noteHtml" : "",
                "snapshotFilename" : "empty",
                "slicerSettingsAsText" : ""
        }

        var printHistoryJobItems = [
             {
                "databaseId" : ko.observable(1),
                "success" : ko.observable("1"),
                "printStartDateTimeFormatted" : "19.09.2019 16:25",
                "printEndDateTimeFormatted" : "19.09.2019 17:25",
                "printStatusResult" : ko.observable("success"),
                "duration" : "123",
                "durationFormatted" : "1h12min",
                "fileName" : "Legolas.gcode",
                "fileSize" : "134KB",
                "temperatureBed" : "50C",
                "temperatureNozzle" : "200C",
                "printedHeight" : "23 / 23mm",
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
                "snapshotFilename" : ko.observable("20191003-123322"),
                "slicerSettingsAsText" : ko.observable()
//                "usedSpoolManagerPlugin": ko.observable()
            },{
                "databaseId" : ko.observable(2),
                "success" : ko.observable("0"),
                "printStartDateTimeFormatted" : "20.09.2019 15:25",
                "printEndDateTimeFormatted" : "20.09.2019 17:25",
                "printStatusResult" : ko.observable("fail"),
                "duration" : "321",
                "durationFormatted" : "2h34min",
                "fileName" : "Benchy3D.gcode",
                "fileSize" : "324KB",
                "temperatureBed" : "60C",
                "temperatureNozzle" : "220C",

                "printedHeight" : "13 / 143mm",
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
                "snapshotFilename" : ko.observable("20191003-153312"),
                "slicerSettingsAsText" : ko.observable()
//                "usedSpoolManagerPlugin": ko.observable()
            }
        ];
//        self.printJobHistorylistHelper.updateItems(printHistoryJobItems);

/// END MOCK MODEL

        // assign the injected parameters, e.g.:
        self.loginStateViewModel = parameters[0];
        self.loginState = parameters[0];
        self.settingsViewModel = parameters[1];
//        self.spoolManagerViewModel = parameters[2];
        self.pluginSettings = null;

        self.apiClient = new PrintJobHistoryAPIClient(PLUGIN_ID, BASEURL);
        self.componentFactory = new PrintJobComponentFactory(PLUGIN_ID);
        self.printJobEditDialog = new PrintJobHistoryEditDialog(null, null);
        self.pluginCheckDialog = new PrintJobHistoryPluginCheckDialog();
        self.statisticDialog = new StatisticDialog();
        self.compareSlicerSettingsDialog = new CompareSlicerSettingsDialog();

        self.printJobForEditing = ko.observable();
        self.printJobForEditing(new PrintJobItem(printHistoryJobItems[0]));

        self.printJobToShowAfterStartup = null;
        self.missingPluginDialogMessage = null;

        //self.tableAttributeVisibility = ko.observable();
        self.tableAttributeVisibility = new TableAttributeVisibility();

        self.csvFileUploadName = ko.observable();
        self.csvImportInProgress = ko.observable(false);

        self.isPrintHistoryPluginAvailable = ko.observable(false);
        self.isMultiSpoolManagerPluginsAvailable = ko.observable(false);

        self.databaseFileLocation = ko.observable();
        self.snapshotFileLocation = ko.observable();

        self.csvImportDialog = new PrintJobHistoryImportDialog();

        ////////////////////////////////////////////////////// Knockout model-binding/observer

        ///////////////////////////////////////////////////// START: HELPER
        loadSettingsFromBrowserStore = function(){
            initTableVisibilities();


            // TODO maybe in a separate js-file
            // load all settings from browser storage
            if (!Modernizr.localstorage) {
                // damn!!!
                return false;
            }
            var storageKey = "pjh.table.selectedPageSize";
            if (localStorage[storageKey] == null){
                localStorage[storageKey] = "25"; // default page size
            } else {
                self.printJobHistoryTableHelper.selectedPageSize(localStorage[storageKey]);
            }
            self.printJobHistoryTableHelper.selectedPageSize.subscribe(function(newValue){
                localStorage[storageKey] = newValue;
            });
        }


        self.showPopUp = function(popupType, popupTitle, message){
            var title = popupType.toUpperCase() + ": " + popupTitle;
            var popupId = (title+message).replace(/([^a-z0-9]+)/gi, '-');
            if($("."+popupId).length <1) {
                new PNotify({
                    title: title,
                    text: message,
                    type: popupType,
                    hide: false,
                    addclass: popupId
                });
            }
        };

        ///////////////////////////////////////////////////// END: HELPER

        ///////////////////////////////////////////////////// START: SETTINGS
        self.busyIndicatorActive = ko.observable(false);

        self.downloadDatabaseUrl = ko.observable();
        self.takeSnapshotAfterPrintDisabled = ko.observable(false);
        self.takeSnapshotOnGCodeCommndDisabled = ko.observable(false);
        self.takeSnapshotGCodeCommndPatternDisabled = ko.observable(false);
        self.cameraSnapShotURLAvailable = ko.observable(false);

        isSnapshotUrlPresent = function(snapshotUrl){
            return snapshotUrl != null && snapshotUrl.trim().length != 0;
        }
        self.initCameraSettingsBehaviour = function(){

            if (self.settingsViewModel.settings.webcam.snapshotUrl != null){
                // assign inital values
                self.cameraSnapShotURLAvailable(isSnapshotUrlPresent(self.settingsViewModel.settings.webcam.snapshotUrl()));

                self.settingsViewModel.settings.webcam.snapshotUrl.subscribe(function(newSnapShotUrl){
                    self.cameraSnapShotURLAvailable(isSnapshotUrlPresent(newSnapShotUrl));
                });
            }

            // Checkbox - stuff
            self.pluginSettings.takeSnapshotAfterPrint.subscribe(function(newValue){

                    if (newValue == true){
                        self.pluginSettings.takeSnapshotOnGCodeCommnd(false);
                    }
            });
            self.pluginSettings.takeSnapshotOnGCodeCommnd.subscribe(function(newValue){

                    if (newValue == true){
                        self.pluginSettings.takeSnapshotAfterPrint(false);
                    }
            });
        }

        self.deleteDatabaseAction = function() {
            var result = confirm("Do you really want to delete all PrintJobHistory data?");
            if (result == true){
                self.apiClient.callDeleteDatabase(function(responseData) {
                    self.printJobHistoryTableHelper.reloadItems();
                });
            }
        };

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
                self.csvImportInProgress(false);
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
            self.csvImportDialog.showDialog(function(shouldTableReload){
                    //
                    if (shouldTableReload == true){
                        self.printJobHistoryTableHelper.reloadItems();
                    }
                }
            );
            self.csvImportUploadData.submit();
        };

        // download sample csv-file
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
            self.csvImportDialog.init(self.apiClient);
            self.statisticDialog.init(self.apiClient);
            self.compareSlicerSettingsDialog.init(self.apiClient, self.busyIndicatorActive);

            // load browser stored settings
            loadSettingsFromBrowserStore();

            // resetSettings-Stuff
            new ResetSettingsUtilV3(self.pluginSettings).assignResetSettingsFeature(PLUGIN_ID, function(data){
                // no additional reset function
             });

            self.initCameraSettingsBehaviour();
        }

        self.onAfterBinding = function() {
            // all inits were done
            self.downloadDatabaseUrl(self.apiClient.getDownloadDatabaseUrl());
            // to bring up dialogs the binding must be already done
            if (self.printJobToShowAfterStartup != null){
                self.showPrintJobDetailsDialogAction(self.printJobToShowAfterStartup, true);
            }
            if (self.missingPluginDialogMessage != null){
                self.pluginCheckDialog.showMissingPluginsDialog(self.missingPluginDialogMessage);
                self.missingPluginDialogMessage = null;
            }
        }

        self.onUserLoggedIn = function(currentUser) {
            self.printJobEditDialog.setCurrentUser(currentUser);
        }
        self.onUserLoggedOut = function() {
            if (self.printJobEditDialog != null) {
                self.printJobEditDialog.setCurrentUser(null);
            }
        }
        // receive data from server
        self.onDataUpdaterPluginMessage = function (plugin, data) {

            if (plugin != PLUGIN_ID) {
                return;
            }

            if ("initalData" == data.action){
                self.databaseFileLocation(data.databaseFileLocation);
                self.snapshotFileLocation(data.snapshotFileLocation);
                self.isPrintHistoryPluginAvailable(data.isPrintHistoryPluginAvailable);
                self.isMultiSpoolManagerPluginsAvailable(data.isMultiSpoolManagerPluginsAvailable);
                return;
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
                    self.showPrintJobDetailsDialogAction(data.printJobItem, true);
                }
                return;
            }

            if ("reloadTableItems" == data.action){
                self.printJobHistoryTableHelper.reloadItems();
                return;
            }

            if ("closeEditDialog" == data.action){
                self.printJobEditDialog.closeDialog();
                return;
            }


            if ("showPrintJobDialogAfterClientConnection" == data.action){
                if (data.printJobItem != null){
                    self.printJobToShowAfterStartup = data.printJobItem;
                    self.showPrintJobDetailsDialogAction(data.printJobItem, true);
                }
                return;
            }

            if ("csvImportStatus" == data.action){
                self.csvImportDialog.updateText(data);
            }

            if ("errorPopUp" == data.action){
                self.showPopUp("error", 'ERROR:' + data.title, data.message);
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

        self.showStatisticDialog = function(){
            self.statisticDialog.showDialog(self.printJobHistoryTableHelper.getTableQuery(), function(shouldTableReload){
            });
        }


        printJobDialogCloseHandler = function(shouldTableReload){
            // refresh snapshotImage
            printJob = self.printJobForEditing();
            var snapshotImageId = "#"+self.snapshotImageId(printJob);
            var snapshotImage = $(snapshotImageId);
            var snapshotUrl = snapshotImage.attr("src");
            snapshotImage.attr("src", snapshotUrl+"?" + new Date().getTime()); // cache - break

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
        }

        self.showPrintJobDetailsDialogAction = function(selectedPrintJobItem, forceCloseDialog) {

            if (forceCloseDialog == null){
                forceCloseDialog = false;
            }
            self.printJobForEditing(new PrintJobItem(ko.mapping.toJS(selectedPrintJobItem)));
//            self.printJobEditDialog.showDialog(self.printJobForEditing(), printJobDialogCloseHandler);
            self.printJobEditDialog.showDialog(self.printJobForEditing(), function(shouldTableReload){
                // delegate to default close handler
                printJobDialogCloseHandler(shouldTableReload);
                if (forceCloseDialog == true){

                    self.apiClient.callForceCloseEditDialog(function(responseData){
                        // do nothing
                    });
                }
            });
        };

        ///////////////////////////////////////////////////// END: DIALOG Stuff

        ///////////////////////////////////////////////////// START: TABLE BEHAVIOR

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
            assignVisibility("vendor");
            assignVisibility("spool");
            assignVisibility("usedLength");
            assignVisibility("usedWeight");
            assignVisibility("note");
            assignVisibility("image");
        }

        self.addNewPrintJobItem = function(){
//            debugger
            var emptyItem = new PrintJobItem(emptyPrintJobItemAsJson);
            self.printJobForEditing(emptyItem);

            self.printJobEditDialog.showDialog(self.printJobForEditing(), printJobDialogCloseHandler, true);
        }

        loadJobFunction = function(tableQuery, observableTableModel, observableTotalItemCount, observableCurrentItemCount){
            // api-call
            self.apiClient.callLoadPrintJobsByQuery(tableQuery, function(responseData){
                // handle response
                totalItemCount = responseData["totalItemCount"];
                allPrintJobs = responseData["allPrintJobs"];
                var dataRows = ko.utils.arrayMap(allPrintJobs, function (data) {
                    return new PrintJobItem(data);
                });
                observableTotalItemCount(totalItemCount);
                observableCurrentItemCount(dataRows.length);
                observableTableModel(dataRows);

            });
        }

        self.printJobHistoryTableHelper = new PrintJobTableItemHelper(loadJobFunction, 25, "printStartDateTime", "all");

        // - timeframe query
        self.allTimeFrames = ko.observableArray([
            { key: "all", label: "all" },
            { key: "custom", label: "custom" },
            { key: "lastWeek", label: "last 7 days" },
            { key: "lastMonth", label: "last 30 days" },
            { key: "lastThreeMonth", label: "last 90 days" },
            { key: "lastYear", label: "last 365 days" },
        ]);

        self.selectedTimeFrame = ko.observable("all");
        self.isCustomTimeFrame = ko.observable(false);

        self.selectedTimeFrame.subscribe(function(newValue){
                    self.isCustomTimeFrame("custom" == newValue);


                    if ("custom" == newValue){
                        self.isQueryStartEnabled(true);
                        self.isQueryEndEnabled(true);
                        return
                    }
                    self.isQueryStartEnabled(false);
                    self.isQueryEndEnabled(false);
                    // calculate new start/end date
                    var startDate = new Date(Date.now());
                    var endDate = new Date(Date.now());

                    if ("lastWeek" == newValue){
                        startDate.setDate(startDate.getDate() - 7);
                    } else
                    if ("lastMonth" == newValue){
                        startDate.setDate(startDate.getDate() - 30);
                    } else
                    if ("lastThreeMonth" == newValue){
                        startDate.setDate(startDate.getDate() - 90);
                    } else
                    if ("lastYear" == newValue){
                        startDate.setDate(startDate.getDate() - 365);
                    } else
                    if ("all" == newValue ){
                        startDate = null;
                        endDate = null;
                        self.printJobHistoryTableHelper.queryStartDate("");
                        self.printJobHistoryTableHelper.queryEndDate("");
                    }

                    if (startDate != null && endDate != null){
                        var yyyy = startDate.getFullYear().toString();
                        var mm = (startDate.getMonth() + 101).toString().slice(-2);
                        var dd = (startDate.getDate() + 100).toString().slice(-2);
                        self.printJobHistoryTableHelper.queryStartDate(dd + "." + mm + "." + yyyy);

                        yyyy = endDate.getFullYear().toString();
                        mm = (endDate.getMonth() + 101).toString().slice(-2);
                        dd = (endDate.getDate() + 100).toString().slice(-2);
                        self.printJobHistoryTableHelper.queryEndDate(dd + "." + mm + "." + yyyy);
                    }
                    self.printJobHistoryTableHelper.reloadItems();
            });
        var queryStartViewModel = self.componentFactory.createDateTimePicker("queryStart-date-picker", false);
        self.printJobHistoryTableHelper.queryStartDate = queryStartViewModel.currentDateTime;
        self.isQueryStartEnabled = queryStartViewModel.isEnabled;
        self.isQueryStartEnabled(false);

        var queryEndViewModel = self.componentFactory.createDateTimePicker("queryEnd-date-picker", false);
        self.printJobHistoryTableHelper.queryEndDate = queryEndViewModel.currentDateTime;
        self.isQueryEndEnabled = queryEndViewModel.isEnabled;
        self.isQueryEndEnabled(false);

        // - export csv data
        self.exportUrl = function(exportType) {
            if (self.printJobHistoryTableHelper.items().length > 0) {
                var defaultURL =  self.apiClient.getExportUrl(exportType)
                return defaultURL;
            } else {
                return false;
            }
        };
        self.exportedSelectedURL = ko.observable();

        // - delete
        self.exportUrl = function(exportType) {
            if (self.printJobHistoryTableHelper.items().length > 0) {
                var defaultURL =  self.apiClient.getExportUrl(exportType)
                return defaultURL;
            } else {
                return false;
            }
        };
        self.exportedSelectedURL = ko.observable();

        // Will be filled by table-item checkbox-subscriber
        self.selectedDatabaseIdsAsCSV = "";

        self.deleteSelectedPrintJobs = function(){
            if (self.selectedDatabaseIdsAsCSV.trim().length >1) {
                var result = confirm("Do you really want to delete all selected(" + self.printJobHistoryTableHelper.selectedTableItems().length + ") printjobs?");
                if (result == true) {
                    self.apiClient.callRemovePrintJob("0?databaseIds=" + self.selectedDatabaseIdsAsCSV, function (responseData) {

                        self.printJobHistoryTableHelper.selectedTableItems.removeAll();
                        self.printJobHistoryTableHelper.reloadItems();

                    });
                }
            }
            return false;
        }

        self.compareSelectedPrintJobs = function(){
            if (self.selectedDatabaseIdsAsCSV.split(",").length >=2){
                self.compareSlicerSettingsDialog.showDialog(self.selectedDatabaseIdsAsCSV, function(shouldTableReload){
                    // nothing special to do here
                    });
            }
            return false;
        }

        self.printJobHistoryTableHelper.selectedTableItems.subscribe(function(newValue) {

            var newCSVUrl = self.apiClient.getExportUrl("CSV");
            if (newValue != null && newValue.length > 0){
                var databaseIds = "";
                for (var itemIndex = 0; itemIndex<newValue.length; itemIndex++){
                    databaseIds = databaseIds + newValue[itemIndex].databaseId();
                    if (itemIndex+1 < newValue.length){
                        databaseIds = databaseIds + ",";
                    }
                }
                newCSVUrl = newCSVUrl + "?databaseIds="+ databaseIds;
                self.selectedDatabaseIdsAsCSV = databaseIds;
            }

            self.exportedSelectedURL(newCSVUrl);
        });

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
            return self.apiClient.getSnapshotUrl(printJobItem.snapshotFilename()) + "?" + new Date().getTime();
        }

        self.snapshotImageId = function(printJobItem){
            return "pjh-imageid-" + printJobItem.databaseId();
        }

        // - tableSearch
        self.clearTableSearchQuery = function () {
            self.printJobHistoryTableHelper.searchQuery("");
            self.printJobHistoryTableHelper.reloadItems();
        };

        self.printJobHistoryTableHelper.searchQuery.subscribe(function(newValue){
                    if (newValue != null && newValue.length > 3){
                        self.printJobHistoryTableHelper.reloadItems();
                    }
                });

        ///////////////////////////////////////////////////// END: TABLE BEHAVIOR

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
            "settingsViewModel",
//            "spoolManagerViewModel"
        ],
        // Elements to bind to, e.g. #settings_plugin_PrintJobHistory, #tab_plugin_PrintJobHistory, ...
        elements: [
            document.getElementById("tab_printJobHistory"),
            document.getElementById("settings_printJobHistory"),
            document.getElementById("modal-dialogs-printJobHistory")
        ]
    });
});
