
function CompareSlicerSettingsDialog(){

    var self = this;

    self.apiClient = null;
    self.busyIndicatorActive = null;

    self.compareSlicerSettingsDialog = null;
    self.closeDialogHandler = null;

    self.selectedJobs = null;
    // self.printJobCount = ko.observable();
    self.compareResultTableHeaders = ko.observableArray();
    self.compareResultTableItems = ko.observableArray();


    /////////////////////////////////////////////////////////////////////////////////////////////////// INIT

    this.init = function(apiClient, busyIndicatorActive){
        self.apiClient = apiClient;
        self.busyIndicatorActive = busyIndicatorActive;
        self.compareSlicerSettingsDialog = $("#dialog_printJobHistory_compareSlicerSettings");
    }

    this.isInitialized = function() {
        return self.apiClient != null;
    }

    this.getDiffColor = function(settingsJob){
        var color = "black"
        if (settingsJob["isDifferent"]){
            if (settingsJob["isDifferent"] == "yes"){
                color = "red"
            } else if (settingsJob["isDifferent"] == "notPresent"){
                color = "blue"
            }
        }
        return color;
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////// SHOW DIALOG
    this.showDialog = function(selectedJobIds, closeDialogHandler){
        // Workflow
        // - Load compare result
        // - Setup table/compare model
        // - show compare dialog

        self.selectedJobs = selectedJobIds;
        self.closeDialogHandler = closeDialogHandler;

        // Clear compare table
        self.compareResultTableHeaders([]);
        self.compareResultTableItems([]);

        self.loadSlicerSettingsCompareResult();
    }

    self._openDialog = function(){
        self.compareSlicerSettingsDialog.modal({
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

    }

    /////////////////////////////////////////////////////////////////////////////////////////////////// SOME FUNCTIONs
    self.loadSlicerSettingsCompareResult = function(){
        self.busyIndicatorActive(true);
        self.apiClient.callCompareSlicerSettings(self.selectedJobs, function(responseData){

                var compareResult = JSON.parse(responseData);
                // Fill headers
                self.compareResultTableHeaders.push({fileName:"Keys"});
                for (slicerSettingJob of compareResult.slicerSettingsJobList){
                    self.compareResultTableHeaders.push({fileName:slicerSettingJob.fileName});
                }
                // Fill rows
                for (currentKey of compareResult.allKeys){
                    var rowItem = [{value:currentKey}];
                    for (currentJob of compareResult.slicerSettingsJobList) {
                        var keyValue = currentJob.keyValuesSettings[currentKey];
                        rowItem.push(keyValue)
                    }
                    self.compareResultTableItems.push({row: rowItem});
                }
                self.busyIndicatorActive(false);
                self._openDialog();
            });
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////// CLOSE
    this.closeDialog  = function(){
        self.compareSlicerSettingsDialog.modal('hide');

        self.closeDialogHandler();
    }


}
