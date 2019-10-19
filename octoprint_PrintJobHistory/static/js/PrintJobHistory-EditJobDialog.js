
function PrintJobHistoryEditDialog(){

    var self = this;

    this.apiClient = null;
    this.streamUrl = null;

    this.editPrintJobItemDialog = null;
    this.printJobItemForEdit = null;
    this.saveDoneHandler = null;

    this.lastSnapshotImageSource = null;
    this.snapshotSuccessMessageSpan = null;
    this.snapshotErrorMessageSpan = null;

    this.snapshotImage = null;
    this.captureButtonText = null;
    this.cameraShutterUrl = null;

    this.noteEditor = null;

    this.snapshotUploadName = ko.observable();
    this.snapshotUploadInProgress = ko.observable(false);


    function _setSnapshotImageSource(snapshotUrl){
        self.lastSnapshotImageSource = self.snapshotImage.attr("src")
        if (self.lastSnapshotImageSource="#"){
            self.lastSnapshotImageSource = snapshotUrl;
        }
        self.snapshotImage.attr("src", snapshotUrl);
    }
    function _restoreSnapshotImageSource(){
        _setSnapshotImageSource(self.lastSnapshotImageSource);
    }
    /////////////////////////////////////////////////////////////////////////////////////////////////// INIT

    this.init = function(apiClient, videoStreamUrl){
        self.apiClient = apiClient;
        self.streamUrl = videoStreamUrl;
// TODO WebCam-Settigs as an Object
//self.settingsViewModel.webcam_streamTimeout()

//        self.captureImageInProgress = ko.observable(true)

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
                debugger
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

    /////////////////////////////////////////////////////////////////////////////////////////////////// SHOW DIALOG
    this.showDialog = function(printJobItemForEdit, saveDoneHandler){

        self.printJobItemForEdit = printJobItemForEdit;
        self.saveDoneHandler = saveDoneHandler;

//        TODO Wieso this statt self????
        _setSnapshotImageSource(self.apiClient.getSnapshotUrl(printJobItemForEdit.snapshotFilename()));

        delta = JSON.parse(printJobItemForEdit.noteDelta());
        self.noteEditor.setContents(delta, 'api');


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


    /////////////////////////////////////////////////////////////////////////////////////////////////// SAVE PRINT JOB
    this.savePrintJobItem  = function(){
            var noteText = self.noteEditor.getText();
            var noteDelta = self.noteEditor.getContents();
            var noteHtml = self.noteEditor.getHtml();

            self.printJobItemForEdit.noteText(noteText);
            self.printJobItemForEdit.noteDelta(noteDelta);
            self.printJobItemForEdit.noteHtml(noteHtml);

            self.apiClient.callUpdatePrintJob(self.printJobItemForEdit.databaseId(), self.printJobItemForEdit, function(responseData){
                self.editPrintJobItemDialog.modal('hide');
                self.saveDoneHandler(responseData);
            });
    }


    /////////////////////////////////////////////////////////////////////////////////////////////////// DELETE IMAGE
    this.deleteImage  = function(){
            self.apiClient.callDeleteSnapshotImage(self.printJobItemForEdit.snapshotFilename(), function(responseData){
                // Update Image URL is the same, backend send the "no photo"-image
                _setSnapshotImageSource(self.apiClient.getSnapshotUrl(responseData.snapshotFilename));
            });
    }


    /////////////////////////////////////////////////////////////////////////////////////////////////// CAPTURE IMAGE
    var reCaptureText = "Re-Capture";
    var takeSnapshotText = "Take snapshot";

    this.captureImage = function(){

        self.snapshotSuccessMessageSpan.hide();
        self.snapshotErrorMessageSpan.hide();

        var newImageUrl = null;
        // check is in capture mode
        if (self.captureButtonText.text() == reCaptureText){

            $("#printJobHistory-captureInProgress").show();

            OctoPrint.util.testUrl(self.streamUrl, {
                method: "GET",
                response: "bytes",
                timeout: 5, //TODO real timeoutsettings
//                validSsl: self.webcam_snapshotSslValidation(),
                content_type_whitelist: ["image/*"]
            })
            .done(function(response){
                if (!response.result && response.result == false && response.status == 0){
                    _restoreSnapshotImageSource();
                    self.captureButtonText.text(reCaptureText);
                    $("#printJobHistory-cancelCaptureButton").hide();
                    self.snapshotSuccessMessageSpan.text("Something wrong with the camera!");
                    self.snapshotSuccessMessageSpan.show();
                } else {
                    newImageUrl  = self.streamUrl;
                    $("#printJobHistory-cancelCaptureButton").show();
                    self.captureButtonText.text(takeSnapshotText);
                    _setSnapshotImageSource(newImageUrl);
                }
                $("#printJobHistory-captureInProgress").hide();
            })
            .fail(function() {
                _restoreSnapshotImageSource();
                self.captureButtonText.text(reCaptureText);
                $("#printJobHistory-cancelCaptureButton").hide();
                $("#printJobHistory-captureInProgress").hide();
                self.snapshotSuccessMessageSpan.text("Something wrong with the camera!");
                self.snapshotSuccessMessageSpan.show();
            });
        } else {
            $("#printJobHistory-cancelCaptureButton").hide();

            newImageUrl = self.cameraShutterUrl;
            _setSnapshotImageSource(newImageUrl);

            self.apiClient.callTakeSnapshot(self.printJobItemForEdit.snapshotFilename(), function(responseData){
                self.snapshotSuccessMessageSpan.show();
                self.snapshotSuccessMessageSpan.text("Snapshot captured!");
                self.snapshotImage.attr("src", self.apiClient.getSnapshotUrl(responseData.snapshotFilename));
                self.captureButtonText.text(reCaptureText);
            });
        }
    }


    this.cancelCaptureImage = function(){
        _restoreSnapshotImageSource();
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
        };
        perform();
//            showConfirmationDialog(_.sprintf(gettext("You are about to upload and restore the backup file \"%(name)s\". This cannot be undone."), {name: self.backupUploadName()}),
//                perform);
    };

//        self.selectedSnapshotlFilenameUrl = ko.observable();
//        self.selectedUploaadSnapshotlUrl =  ko.observable();


}
