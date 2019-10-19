

function PrintJobHistoryAPIClient(pluginId, baseUrl) {

    this.pluginId = pluginId
    this.baseUrl = baseUrl;


    this.getExportUrl = function(exportType){
        return "plugin/" + this.pluginId + "/exportPrintJobHistory/" + exportType;
    }

    this.getSnapshotUrl = function(snapshotFilename){
        //http://localhost:5000/plugin/PrintJobHistory/printJobSnapshot/20191003-153311
        return "plugin/" + this.pluginId + "/printJobSnapshot/" + snapshotFilename;
    }

    this.uploadSnapshotUrl = function(snapshotFilename){
        //http://localhost:5000/plugin/PrintJobHistory/printJobSnapshot/20191003-153311
        return "plugin/" + this.pluginId + "/upload/snapshot/" + snapshotFilename;
    }

    // load all PrintJob-Items
    this.callLoadPrintHistoryJobs = function (responseHandler){
        $.ajax({
            //url: API_BASEURL + "plugin/"+PLUGIN_ID+"/loadPrintJobHistory",
            url: this.baseUrl + "plugin/"+this.pluginId+"/loadPrintJobHistory",
            type: "GET"
        }).done(function( data ){
            responseHandler(data)
            //shoud be done by the server to make sure the server is informed countdownDialog.modal('hide');
            //countdownDialog.modal('hide');
            //countdownCircle = null;
        });
    }

    // remove PrintJob-Item
    this.callUpdatePrintJob = function (databaseId, printJobItem, responseHandler){
        jsonPayload = ko.toJSON(printJobItem)

        $.ajax({
            //url: API_BASEURL + "plugin/"+PLUGIN_ID+"/loadPrintJobHistory",
            url: this.baseUrl + "plugin/" + this.pluginId + "/updatePrintJob/" + databaseId,
            dataType: "json",
            contentType: "application/json; charset=UTF-8",
            data: jsonPayload,
            type: "PUT"
        }).done(function( data ){
            responseHandler(data)
        });
    }

    // remove PrintJob-Item
    this.callRemovePrintJob = function (databaseId, responseHandler){
        $.ajax({
            //url: API_BASEURL + "plugin/"+PLUGIN_ID+"/loadPrintJobHistory",
            url: this.baseUrl + "plugin/" + this.pluginId + "/removePrintJob/" + databaseId,
            type: "DELETE"
        }).done(function( data ){
            responseHandler(data)
        });
    }

    // deactivate the Plugin/Check
    this.callDeactivatePluginCheck =  function (){
        $.ajax({
            url: this.baseUrl + "plugin/"+ this.pluginId +"/deactivatePluginCheck",
            type: "PUT"
        }).done(function( data ){
            //responseHandler(data)
        });
    }

    // deactivate the Plugin/Check
    this.callTakeSnapshot =  function (snapshotFilename, responseHandler){
        $.ajax({
            url: this.baseUrl + "plugin/"+ this.pluginId +"/takeSnapshot/"+snapshotFilename,
            type: "PUT"
        }).done(function( data ){
            responseHandler(data)
        });
    }

    // delete snapshotImage
    this.callDeleteSnapshotImage =  function (snapshotFilename, responseHandler){
        $.ajax({
            url: this.baseUrl + "plugin/"+ this.pluginId +"/deleteSnapshotImage/"+snapshotFilename,
            type: "DELETE"
        }).done(function( data ){
            responseHandler(data)
        });
    }



}
