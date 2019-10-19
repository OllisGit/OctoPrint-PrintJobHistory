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
		this.noteDelta = ko.observable();
		this.noteHtml = ko.observable();
		this.printedLayers = ko.observable();
		this.printedHeight = ko.observable();
		this.temperatureBed = ko.observable();
		this.temperatureNozzel = ko.observable();

		this.profileVendor = ko.observable();
		this.diameter = ko.observable();
		this.density = ko.observable();
		this.material = ko.observable();
		this.spoolName = ko.observable();
		this.spoolCost = ko.observable();
		this.spoolCostUnit = ko.observable();
		this.spoolWeight = ko.observable();
		this.usedLength = ko.observable();
		this.calculatedLength = ko.observable();
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
        this.noteDelta(updateData.noteDelta);
        this.noteHtml(updateData.noteHtml);
        this.printedLayers(updateData.printedLayers);
        this.printedHeight(updateData.printedHeight);
        //Tool
        tempDataArray = data["temperatureEntities"];
/* TODO
        sensorName = tempDataArray[0]["sensorName"]
        sensorValue = tempDataArray[0]["sensorValue"]
        this.temperatureNozzel(sensorValue);
        if (tempDataArray.length == 2){
            sensorName = tempDataArray[1]["sensorName"]
            sensorValue = tempDataArray[1]["sensorValue"]

            this.temperatureBed(sensorValue);
        }
*/
        //Filament
        if (updateData.filamentEntity != null){
            this.profileVendor(updateData.filamentEntity.profileVendor);
            this.diameter(updateData.filamentEntity.diameter);
            this.density(updateData.filamentEntity.density);
            this.material(updateData.filamentEntity.material);
            this.spoolName(updateData.filamentEntity.spoolName);
            this.spoolCost(updateData.filamentEntity.spoolCost);
            this.spoolCostUnit(updateData.filamentEntity.spoolCostUnit);
            this.spoolWeight(updateData.filamentEntity.spoolWeight);
//            this.usedLength( formatFilamentLength(updateData.filamentEntity.usedLength) );
//            this.calculatedLength( formatFilamentLength(updateData.filamentEntity.calculatedLength) );
            this.usedLength( updateData.filamentEntity.usedLength );
            this.calculatedLength( updateData.filamentEntity.calculatedLength );
            this.usedWeight( updateData.filamentEntity.usedWeight );
            this.usedCost( updateData.filamentEntity.usedCost );
        } else {
            this.profileVendor(updateData.profileVendor);
            this.diameter(updateData.diameter);
            this.density(updateData.density);
            this.material(updateData.material);
            this.spoolName(updateData.spoolName);
            this.spoolCost(updateData.spoolCost);
            this.spoolCostUnit(updateData.spoolCostUnit);
            this.spoolWeight(updateData.spoolWeight);
//            this.usedLength( formatFilamentLength(updateData.filamentEntity.usedLength) );
//            this.calculatedLength( formatFilamentLength(updateData.filamentEntity.calculatedLength) );
            this.usedLength( updateData.usedLength );
            this.calculatedLength( updateData.calculatedLength );
            this.usedWeight( updateData.usedWeight );
            this.usedCost( updateData.usedCost );
        }

		this.snapshotFilename(updateData.snapshotFilename);
    };


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
                "temperatureNozzel" : "200C",
                "printedHeight" : "23mm / 23mm",
                "printedLayers" : "149 / 149",
                "spoolName" : "myspool",
                "spoolCost" : "2,23",
                "spoolCostUnit" : "Euro",
                "material" : "PLA",
                "usedLength" : "1m22mm",
                "calculatedLength" : "12,5g",
                "usedWeight" : "12,5g",
                "usedCost" : "0,003",
                "noteText" : "Good output of Legolas",
                "noteDelta" : "Good output of Legolas",
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
                "temperatureNozzel" : "220C",

                "printedHeight" : "13mm / 143mm",
                "printedLayers" : "3 / 68",
                "spoolName" : "Master",
                "spoolCost" : "2,23",
                "spoolCostUnit" : "Euro",
                "material" : "ABS",
                "usedLength" : "2m22mm",
                "calculatedLength" : "312,6g",
                "usedWeight" : "312,6g",
                "usedCost" : "1,34",

                "noteText" : "Bad quality",
                "noteDelta" : "Bad quality",
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
        self.printJobEditDialog = new PrintJobHistoryEditDialog(null, null);
        self.pluginCheckDialog = new PrintJobHistoryPluginCheckDialog();

        self.printJobForEditing = ko.observable()
        self.printJobForEditing(new PrintJobItem(printHistoryJobItems[0]));


        ////////////////////////////////////////////////////// Knockout model-binding/observer


        ///////////////////////////////////////////////////// START: OctoPrint Hooks
        self.onBeforeBinding = function() {
            // assign current pluginSettings
            self.pluginSettings = self.settingsViewModel.settings.plugins[PLUGIN_ID];

            self.printJobEditDialog.init(self.apiClient, self.settingsViewModel.settings.webcam.streamUrl());
            self.pluginCheckDialog.init(self.apiClient, self.pluginSettings);

        }

        // receive data from server
        self.onDataUpdaterPluginMessage = function (plugin, data) {

            if (plugin != PLUGIN_ID) {
                return;
            }

            if ("missingPlugin" == data.action){
                self.pluginCheckDialog.showMissingPluginsDialog(data.message);
                return;
            }

            if ("printFinished" == data.action){
                self.reloadTableData();
            }
        }

        self.onTabChange = function(next, current){
            //alert("Next:"+next +" Current:"+current);
            if ("#tab_plugin_PrintJobHistory" == next){
                //self.reloadTableData();
            }
        }

        self.reloadTableData = function(){
            self.apiClient.callLoadPrintHistoryJobs( self.handleAllPrintJobDataResponse );
        }

        ///////////////////////////////////////////////////// END: OctoPrint Hooks

        self.handleAllPrintJobDataResponse = function (allPrintJobs){
            // Print Jobs from Backend
            var dataRows = ko.utils.arrayMap(allPrintJobs, function (data) {
                return new PrintJobItem(data);
            });

            //self.pureData = data.history;

            //self.dataIsStale = false;
            self.printJobHistorylistHelper.updateItems(dataRows);
        }


        // helper.js
        // listType, supportedSorting, supportedFilters, defaultSorting, defaultFilters, exclusiveFilters, defaultPageSize)
        self.printJobHistorylistHelper = new ItemListHelper(
            "printJobHistoryItems",
            // sorting stuff
            {
                "column1": function (a,b){
                    //some sort stuff
                    return 0;
                }
            },
            // filtering
            {
                "all": function(item){
                    return true;
                },
                "successful": function (item) {
                    return (item.success() == 1);
                },
                "failed": function (item) {
                    return (item.success() == 0);
                }
            },
            // defaultSorting
            "defaultSorting",
            // defaultFilter
            ["all"],
            // exclusiveFilter
            [["all", "successful", "failed"]],
            // pageSize
            10
        );

        ///////////////////////////////////////////////////// START: DAILOG Stuff


        self.showPrintJobDetailsDialogAction = function(selectedPrintJobItem) {

            self.printJobForEditing(new PrintJobItem(ko.mapping.toJS(selectedPrintJobItem)));
            self.printJobEditDialog.showDialog(self.printJobForEditing(), function(allPrintJobs){
                debugger
                self.handleAllPrintJobDataResponse(allPrintJobs);

            });
        };

        ///////////////////////////////////////////////////// END: DAILOG Stuff



        self.exportUrl = function(exportType) {
            if (self.printJobHistorylistHelper.items().length > 0) {
                return self.apiClient.getExportUrl(exportType)
            } else {
                return false;
            }
        };


        //////////// TABLE BEHAVIOR


        self.snapshotUrl = function(printJobItem){
            return self.apiClient.getSnapshotUrl(printJobItem.snapshotFilename());
        }

        self.removePrintJobAction = function(printJobItem) {
            self.apiClient.callRemovePrintJob(printJobItem.databaseId(), self.handleAllPrintJobDataResponse)
        };


        self.sortOrderLabel = function(orderType) {
            var order = "";

            if (orderType == "fileName") {
                order = (self.printJobHistorylistHelper.currentSorting() == 'fileNameAsc') ? '(' + _('ascending') + ')' : (self.printJobHistorylistHelper.currentSorting() == 'fileNameDesc') ? '(' + _('descending') + ')' : '';
            } else if (orderType == "timestamp") {
                order = (self.printJobHistorylistHelper.currentSorting() == 'timestampAsc') ? '(' + _('ascending') + ')' : (self.printJobHistorylistHelper.currentSorting() == 'timestampDesc') ? '(' + _('descending') + ')' : '';
            } else {
                order = (self.printJobHistorylistHelper.currentSorting() == 'printTimeAsc') ? '(' + _('ascending') + ')' : (self.printJobHistorylistHelper.currentSorting() == 'printTimeDesc') ? '(' + _('descending') + ')' : '';
            }

            return order;
        };


        self.changeSortOrder = function(columnToSort) {
            if (self.printJobHistorylistHelper.currentSorting() == "fileNameAsc") {
                self.printJobHistorylistHelper.changeSorting("fileNameDesc");
            } else {
                self.printJobHistorylistHelper.changeSorting("fileNameAsc");
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
