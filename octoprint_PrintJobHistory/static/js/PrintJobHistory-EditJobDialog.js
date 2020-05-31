
function PrintJobHistoryEditDialog(){

    var self = this;

    this.apiClient = null;

    this.editPrintJobItemDialog = null;
    this.printJobItemForEdit = null;
    this.closeDialogHandler = null;

    this.lastSnapshotImageSource = null;
    this.snapshotSuccessMessageSpan = null;
    this.snapshotErrorMessageSpan = null;

    this.snapshotImage = null;
    this.captureButtonText = null;
    this.cameraShutterUrl = null;

    this.noteEditor = null;

    this.shouldPrintJobTableReload = false;

    var SHUTTER_DURATION = 4;   // in seconds
    var IMAGEDISPLAYMODE_SNAPSHOTIMAGE = "snapshotImage";
    var IMAGEDISPLAYMODE_VIDEOSTREAM = "videoStream";
    var IMAGEDISPLAYMODE_VIDEOSTREAM_WITH_SHUTTER = "videoStreamWithShutter";
    var IMAGEDISPLAYMODE_VIDEOSTREAM_LOADING = "videoStreamLoading";
    var IMAGEDISPLAYMODE_VIDEOSTREAM_ERROR = "videoStreamError";

    this.imageDisplayMode = ko.observable(IMAGEDISPLAYMODE_SNAPSHOTIMAGE);

    this.snapshotUploadName = ko.observable();
    this.snapshotUploadInProgress = ko.observable(false);

    self.webCamSettings = null;

    // "Computed" field-binding
    self.webCamEnabled = ko.pureComputed(function(){
        if (self.webCamSettings.webcamEnabled != null){
            return self.webCamSettings.webcamEnabled();
        } else {
            return self.webCamSettings.snapshotUrl() != null && self.webCamSettings.streamUrl();
        }
    });
    // "Computed" field-binding
    self.webcamRatioClass = ko.pureComputed(function() {
        if (self.webCamSettings.streamRatio() == "4:3") {
            return "ratio43";
        } else {
            return "ratio169";
        }
    });

    // Image functions
    function _setSnapshotImageSource(snapshotUrl){
        self.lastSnapshotImageSource = self.snapshotImage.attr("src")
        if (self.lastSnapshotImageSource="#"){
            self.lastSnapshotImageSource = snapshotUrl;
        }
        self.snapshotImage.attr("src", snapshotUrl+"?" + new Date().getTime()); // new Date == cache breaker
    }

    function _restoreSnapshotImageSource(){
        _setSnapshotImageSource(self.lastSnapshotImageSource);
    }
    /////////////////////////////////////////////////////////////////////////////////////////////////// INIT

    this.init = function(apiClient, webCamSettings){
        self.apiClient = apiClient;

        self.webCamSettings = webCamSettings

        self.editPrintJobItemDialog = $("#dialog_printJobHistory_editPrintJobItem");
        self.snapshotSuccessMessageSpan = $("#printJobHistory-editdialog-success-message");
        self.snapshotErrorMessageSpan = $("#printJobHistory-editdialog-error-message");
        self.snapshotImage = $("#printJobHistory-snapshotImage");
        self.captureButtonText = $("#printJobHistory-captureButtonText");
        self.cameraShutterUrl = "plugin/PrintJobHistory/static/images/camera-shutter.png";   // TODO replace with PLUGIN_ID

        // INIT Note Editor
        self.noteEditor = new Quill('#note-quill-editor', {
            modules: {
                toolbar: [
                    ['bold', 'italic', 'underline'],
                    [{ 'color': [] }, { 'background': [] }],
                    [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                    ['link']
                ]
            },
            theme: 'snow'
        });
        Quill.prototype.getHtml = function() {
            return this.container.querySelector('.ql-editor').innerHTML;
        };

        // INIT FileUpload
        self.snapshotUploadData = undefined;    // data with submit function
        self.snapshotUploadButton = $("#printJobHistory-snapshotUploadButton");
        self.snapshotUploadButton.fileupload({
            dataType: "json",
            maxNumberOfFiles: 1,
            autoUpload: false,
            headers: OctoPrint.getRequestHeaders(),
            add: function(e, data) {
                self.snapshotSuccessMessageSpan.hide();
                self.snapshotErrorMessageSpan.hide();
                if (data.files.length === 0) {
                    // no files? ignore
                    return false;
                }
                data.url = self.apiClient.uploadSnapshotUrl(self.printJobItemForEdit.snapshotFilename());
                self.snapshotUploadName(data.files[0].name);
                self.snapshotUploadData = data;
            },
            done: function(e, data) {
                self.snapshotSuccessMessageSpan.show();
                self.snapshotSuccessMessageSpan.text("Snapshot uploaded!");
                self.snapshotUploadName(undefined);
                self.snapshotUploadData = undefined;
                _setSnapshotImageSource(self.apiClient.getSnapshotUrl(data.result.snapshotFilename));

                self.snapshotUploadInProgress(false);
            },
            fail: function(e, data) {
                new PNotify({
                    title: gettext("Something went wrong"),
                    text: gettext("Maybe the filesize was to big (limit 5MB). Please consult octoprint.log for details"),
                    type: "error",
                    hide: false
                });

//                self.uploadButton.unbind("click");
                self.snapshotUploadName(undefined);
                self.snapshotUploadInProgress(false);
            }
        });
    }

    this.isInitialized = function() {
        return self.apiClient != null;
    }


    /////////////////////////////////////////////////////////////////////////////////////////////////// SHOW DIALOG
    this.showDialog = function(printJobItemForEdit, closeDialogHandler){

        self.printJobItemForEdit = printJobItemForEdit;
        self.closeDialogHandler = closeDialogHandler;

        self.shouldPrintJobTableReload = false;
//        TODO Wieso this statt self????
        _setSnapshotImageSource(self.apiClient.getSnapshotUrl(printJobItemForEdit.snapshotFilename()));

//        reset message
        self.snapshotSuccessMessageSpan.hide();
        self.snapshotErrorMessageSpan.hide();
        self.imageDisplayMode(IMAGEDISPLAYMODE_SNAPSHOTIMAGE);

        // assign content to the Note-Section
        var noteContent = null;
        if (printJobItemForEdit.noteDeltaFormat() == null){
            // Fallback is text (if present), not Html
            if (printJobItemForEdit.noteText() != null){
                self.noteEditor.setText(printJobItemForEdit.noteText(), 'api');
            }
        } else {
            deltaFormat = JSON.parse(printJobItemForEdit.noteDeltaFormat());
            self.noteEditor.setContents(deltaFormat, 'api');
        }

        self.editPrintJobItemDialog.modal({
            //minHeight: function() { return Math.max($.fn.modal.defaults.maxHeight() - 80, 250); }
            keyboard: false,
            clickClose: false,
            showClose: false,
            backdrop: "static"
        }).css({
            width: 'auto',
            'margin-left': function() { return -($(this).width() /2); }
        });
    }


    /////////////////////////////////////////////////////////////////////////////////////////////////// ABORT PRINT JOB ITEM
    this.abortPrintJobItem  = function(){
        self.editPrintJobItemDialog.modal('hide');
        self.closeDialogHandler(self.shouldPrintJobTableReload);
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////// SAVE PRINT JOB ITEM
    this.savePrintJobItem  = function(){
        var noteText = self.noteEditor.getText();
        var noteDeltaFormat = self.noteEditor.getContents();
        var noteHtml = self.noteEditor.getHtml();
        self.printJobItemForEdit.noteText(noteText);
        self.printJobItemForEdit.noteDeltaFormat(noteDeltaFormat);
        self.printJobItemForEdit.noteHtml(noteHtml);

        self.apiClient.callUpdatePrintJob(self.printJobItemForEdit.databaseId(), self.printJobItemForEdit, function(allPrintJobsResponse){
            self.editPrintJobItemDialog.modal('hide');
            self.closeDialogHandler(true);
        });

    }


    /////////////////////////////////////////////////////////////////////////////////////////////////// DELETE PRINT JOB
    this.deletePrintJobItem  = function(){
        var result = confirm("Do you really want to delete the print job?");
        if (result == true){
            self.apiClient.callRemovePrintJob(self.printJobItemForEdit.databaseId(), function(responseData) {
                self.editPrintJobItemDialog.modal('hide');
                self.closeDialogHandler(true);
            });
        }
    }


    /////////////////////////////////////////////////////////////////////////////////////////////////// DELETE IMAGE
    this.deleteImage  = function(){


        var result = confirm("Do you really want to delete the image?");
        if (result == true){
            self.apiClient.callDeleteSnapshotImage(self.printJobItemForEdit.snapshotFilename(), function(responseData){
                // Update Image URL is the same, backend send the "no photo"-image
                _setSnapshotImageSource(self.apiClient.getSnapshotUrl(responseData.snapshotFilename));
                self.shouldPrintJobTableReload = true;
            });
        }
    }


    /////////////////////////////////////////////////////////////////////////////////////////////////// CAPTURE IMAGE
    var reCaptureText = "Capture";
    var takeSnapshotText = "Take snapshot";

    this.captureImage = function(){
        self.snapshotSuccessMessageSpan.hide();
        self.snapshotErrorMessageSpan.hide();

        var newImageUrl = null;
        // check is in capture mode
        if (self.captureButtonText.text() == reCaptureText){
            // SHOW VIDEOSTREAM
            self.imageDisplayMode(IMAGEDISPLAYMODE_VIDEOSTREAM_LOADING);

            snapshotUrl = self.webCamSettings.snapshotUrl();
            streamUrl = self.webCamSettings.streamUrl();

            if (snapshotUrl == null || streamUrl == null || snapshotUrl.length == 0 || streamUrl.length == 0) {
                alert("Camera-Error: Please make sure that both stream- and snapshot-url is configured in your camera-settings")
            }

            OctoPrint.util.testUrl(snapshotUrl, {
                method: "GET",
                response: "bytes",
                timeout: self.webCamSettings.streamTimeout(),
//                validSsl: self.webcam_snapshotSslValidation(),
                content_type_whitelist: ["image/*"]
            })
            .done(function(response){
                // Check if videoStream is available
                if (response.status == 200 && response.result == true){
                    //show stream in image
                    self.imageDisplayMode(IMAGEDISPLAYMODE_VIDEOSTREAM);

                    $("#printJobHistory-videoStream").attr("src", self.webCamSettings.streamUrl());
                    self.captureButtonText.text(takeSnapshotText);
                } else {
                    // VideoStream is not available
                    self.imageDisplayMode(IMAGEDISPLAYMODE_VIDEOSTREAM_ERROR);
                }
            })
            .fail(function() {
                self.imageDisplayMode(IMAGEDISPLAYMODE_VIDEOSTREAM_ERROR);

                self.snapshotErrorMessageSpan.show();
                self.snapshotErrorMessageSpan.text("Something went wrong. Try again!");
            });
        } else {
            // TAKE SNAPSHOT
            var startShutter = new Date().getTime();
            self.imageDisplayMode(IMAGEDISPLAYMODE_VIDEOSTREAM_WITH_SHUTTER);
            // freeze video stream -> show current tken snapshot
            var mySnapshotUrl = self.apiClient.getProxiedSnapshotUrl();
            $("#printJobHistory-videoStream").attr("src", mySnapshotUrl);

            self.apiClient.callTakeSnapshot(self.printJobItemForEdit.snapshotFilename(), function(responseData){
                if (responseData["snapshotFilename"] != undefined){
                    self.snapshotSuccessMessageSpan.show();
                    self.snapshotSuccessMessageSpan.text("Snapshot captured!");

                } else {
                    self.snapshotErrorMessageSpan.show();
                    self.snapshotErrorMessageSpan.text("Something went wrong. Try again!");
                }

                self.snapshotImage.attr("src", self.apiClient.getSnapshotUrl(responseData.snapshotFilename));
                self.captureButtonText.text(reCaptureText);

                // SOME UI-SUGAR, if a minimum of time is not passed, just wait and after that remove the "nice" shutter
                var now = new Date().getTime();
                var captureDuration = now-startShutter;
                if (captureDuration < (SHUTTER_DURATION*1000)){
                    waitingDelta = (SHUTTER_DURATION*1000) - captureDuration
                    setTimeout(function() {
                        self.imageDisplayMode(IMAGEDISPLAYMODE_SNAPSHOTIMAGE);
                    }, waitingDelta);
                } else {
                    // server call takes already a long time
                    self.imageDisplayMode(IMAGEDISPLAYMODE_SNAPSHOTIMAGE);
                }
                self.shouldPrintJobTableReload = true;
            });
        }
    }


    this.cancelCaptureImage = function(){
        self.imageDisplayMode(IMAGEDISPLAYMODE_SNAPSHOTIMAGE);
        self.captureButtonText.text(reCaptureText);
        $("#printJobHistory-cancelCaptureButton").hide();
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////// UPLOAD IMAGE

    this.performSnapshotUpload = function() {
        if (self.snapshotUploadData === undefined) return;

        var perform = function() {
            self.snapshotUploadInProgress(true);
//                self.loglines.removeAll();
//                self.loglines.push({line: "Uploading backup, this can take a while. Please wait...", stream: "message"});
//                self.loglines.push({line: " ", stream: "message"});
//                self.restoreDialog.modal({keyboard: false, backdrop: "static", show: true});

            self.snapshotUploadData.submit();
            self.shouldPrintJobTableReload = true;
        };
        perform();
//            showConfirmationDialog(_.sprintf(gettext("You are about to upload and restore the backup file \"%(name)s\". This cannot be undone."), {name: self.backupUploadName()}),
//                perform);
    };

//        self.selectedSnapshotlFilenameUrl = ko.observable();
//        self.selectedUploaadSnapshotlUrl =  ko.observable();


}
