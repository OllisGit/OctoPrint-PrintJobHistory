/*
 * View model for PrintJobHistory
 *
 * Author: OllisGit
 * License: AGPLv3
 */
$(function() {

    var PLUGIN_ID = "PrintJobHistory"; // from setup.py plugin_identifier
    var missingPluginsDialog = null;


    function showDialog(dialogId, dialogMessage, confirmFunction){
        if (missingPluginsDialog != null && missingPluginsDialog.is(":visible")){
            return;
        }

        $("#missingPluginMessage").html(dialogMessage);

        missingPluginsDialog = $(dialogId);
        var confirmButton = $("button.btn-confirm", missingPluginsDialog);

        confirmButton.unbind("click");
        confirmButton.bind("click", function() {
            confirmFunction(missingPluginsDialog);
        });

        missingPluginsDialog.modal({
            //minHeight: function() { return Math.max($.fn.modal.defaults.maxHeight() - 80, 250); }
            keyboard: false,
            clickClose: false,
            showClose: false
        }).css({
            width: 'auto',
            'margin-left': function() { return -($(this).width() /2); }
        });
    }

    function PrintjobhistoryViewModel(parameters) {

        var self = this;

        // assign the injected parameters, e.g.:
        self.loginStateViewModel = parameters[0];
        self.loginState = parameters[0];
        self.settingsViewModel = parameters[1];

        // receive data from server
        self.onDataUpdaterPluginMessage = function (plugin, data) {

            if (plugin != PLUGIN_ID) {
                return;
            }
            if ("missingPlugin" == data.action){

                showDialog("#navbar_missingPluginsDialog", data.message, function(dialog){


                    missingPluginsDialog.modal('hide');
                    /*
                    $.ajax({
                        url: API_BASEURL + "plugin/"+PLUGIN_ID+"?action=stopCountdown",
                        type: "GET"
                    }).done(function( data ){
                        new PNotify({
                            title: "Stopped autostart print!",
                            text: "The autostart print was canceled!",
                            type: "info",
                            hide: true
                        });
                        //shoud be done by the server to make sure the server is informed countdownDialog.modal('hide');
                        countdownDialog.modal('hide');
                        countdownCircle = null;
                    });
                    */
                });
            }
        }

        self.isPrinting = ko.observable(undefined);

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


        var printHistoryJobItems = [
             {
                "success" : ko.observable("1"),
                "formatedStartDate" : "19.09.2019 16:25",
                "formatedEndDate" : "19.09.2019 17:25",
                "formatedDuration" : "1h12min",
                "fileName" : "Legolas.gcode",
                "fileSize" : "134KB",
                "temperature" : "50C / 200C",
                "heightInfo" : "23mm / 23mm",
                "layerInfo" : "149 / 149",
                "spool" : "myspool",
                "material" : "PLA",
                "filamentLength" : "1m22mm",
                "filamentWeight" : "12,5g",
                "filamentCost" : "3,5Euro",
                "imageLink" : "../images/no-photo-icon.jpg",
                "note" : "Good output of Legolas",

                "user" : "ich",
                "formatedDate" : "10/10/2010",
                "formatedTimeAgo" : "12/10/2010",
                "filamentUsage" : "22mm",
            },{
                "success" : ko.observable("0"),
                "formatedStartDate" : "20.09.2019 15:25",
                "formatedEndDate" : "20.09.2019 17:25",
                "formatedDuration" : "2h34min",
                "fileName" : "Benchy3D.gcode",
                "fileSize" : "324KB",
                "temperature" : "60C / 220C",
                "heightInfo" : "13mm / 143mm",
                "layerInfo" : "3 / 68",
                "spool" : "Master",
                "material" : "ABS",
                "filamentLength" : "2m22mm",
                "filamentWeight" : "312,6g",
                "filamentCost" : "6,5Euro",
                "imageLink" : "../images/no-photo-icon.jpg",
                "note" : "Bad quality",

                "user" : "ich",
                "formatedDate" : "10/10/2010",
                "formatedTimeAgo" : "12/10/2010",
                "filamentUsage" : "22mm",
            }
        ];
        //printHistoryJobItems.push(item);

        self.printJobHistorylistHelper.updateItems(printHistoryJobItems);


        //////////// TABLE BEHAVIOR
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
            debugger
            if (self.printJobHistorylistHelper.currentSorting() == "fileNameAsc") {
                self.printJobHistorylistHelper.changeSorting("fileNameDesc");
            } else {
                self.printJobHistorylistHelper.changeSorting("fileNameAsc");
            }
        };
/*
        self.listHelper = new ItemListHelper(
            "historyItems",
            {
                "fileNameAsc": function (a, b) {
                    // sorts ascending
                    if (a.fileName().toLocaleLowerCase() < b.fileName().toLocaleLowerCase()) return -1;
                    if (a.fileName().toLocaleLowerCase() > b.fileName().toLocaleLowerCase()) return 1;
                    return 0;
                },
                "fileNameDesc": function (a, b) {
                    // sorts ascending
                    if (a.fileName().toLocaleLowerCase() < b.fileName().toLocaleLowerCase()) return 1;
                    if (a.fileName().toLocaleLowerCase() > b.fileName().toLocaleLowerCase()) return -1;
                    return 0;
                },
                "timestampAsc": function (a, b) {
                    // sorts descending
                    if (a.timestamp() > b.timestamp()) return 1;
                    if (a.timestamp() < b.timestamp()) return -1;
                    return 0;
                },
                "timestampDesc": function (a, b) {
                    // sorts descending
                    if (a.timestamp() > b.timestamp()) return -1;
                    if (a.timestamp() < b.timestamp()) return 1;
                    return 0;
                },
                "printTimeAsc": function (a, b) {
                    // sorts descending
                    if (a.printTime() > b.printTime()) return 1;
                    if (a.printTime() < b.printTime()) return -1;
                    return 0;
                },
                "printTimeDesc": function (a, b) {
                    // sorts descending
                    if (a.printTime() > b.printTime()) return -1;
                    if (a.printTime() < b.printTime()) return 1;
                    return 0;
                }
            },
            {
                "all": function (item) {
                    return true;
                },
                "successful": function (item) {
                    return (item.success() == 1);
                },
                "failed": function (item) {
                    return (item.success() == 0);
                }
            },
            "timestamp", ["all"], [["all", "successful", "failed"]], 10
        );
*/

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
            document.getElementById("printJobHistory_tab")
        ]
    });
});
