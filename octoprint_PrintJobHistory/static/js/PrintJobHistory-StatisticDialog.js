
function StatisticDialog(){

    var self = this;

    self.apiClient = null;

    self.statisticDialog = null;
    self.closeDialogHandler = null;

    self.query = ko.observable();
    self.fromToDate = ko.observable();
    self.duration = ko.observable();
    self.usedLenght = ko.observable();
    self.usedWeight = ko.observable();
    self.fileSize = ko.observable();
    self.printResults = ko.observable();
    self.materials = ko.observable();
    self.spools = ko.observable();

    /////////////////////////////////////////////////////////////////////////////////////////////////// INIT

    this.init = function(apiClient){
        self.apiClient = apiClient;

        self.statisticDialog = $("#dialog_printJobHistory_statistic");
    }

    this.isInitialized = function() {
        return self.apiClient != null;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////// SHOW DIALOG
    this.showDialog = function(tableQuery, closeDialogHandler){
        self.tableQuery = tableQuery;
        self.closeDialogHandler = closeDialogHandler;

        self.statisticDialog.modal({
            //minHeight: function() { return Math.max($.fn.modal.defaults.maxHeight() - 80, 250); }
            keyboard: true,
            clickClose: false,
            showClose: false,
            backdrop: true
//            backdrop: "static"
        }).css({
            width: 'auto',
            'margin-left': function() { return -($(this).width() /2); }
        });

//        self.busyIcon(true);
        self.loadStatistics();
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////// SOME FUNCTIONs
    self.loadStatistics = function(){
        self.apiClient.callLoadStatisticsByQuery(self.tableQuery, function(responseData){

                self.query(responseData["query"]);
                self.fromToDate(responseData["fromToDate"]);
                self.duration(responseData["duration"]);
                self.usedLenght(responseData["usedLength"]);
                self.usedWeight(responseData["usedWeight"]);
                self.fileSize(responseData["fileSize"]);
                self.printResults(responseData["printStatus"]);
                self.materials(responseData["material"]);
                self.spools(responseData["spools"]);

            });
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////// CLOSE
    this.closeDialog  = function(){
        self.statisticDialog.modal('hide');

        self.closeDialogHandler();
    }


}
