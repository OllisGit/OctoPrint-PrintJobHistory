

function PrintJobHistoryPluginCheckDialog(){

    self = this;

    this.apiClient = null;
    this.pluginSettings = null;

    this.missingPluginsDialog = null;
    this.missingPluginMessage = null;
    this.confirmButton = null;
    this.deactivatePluginCheck = ko.observable(false);

    this.init = function(apiClient, pluginSettings){
        self.apiClient = apiClient;
        self.pluginSettings = pluginSettings
        self.missingPluginsDialog = $("#dialog_printJobHistory_missingPlugins");
        self.missingPluginMessage = $("#missingPluginMessage");
        self.confirmButton = $("button.btn-confirm", self.missingPluginsDialog);
    }

    this.hideDialog = function(){
        self.missingPluginsDialog.modal('hide');
    }

    this.showMissingPluginsDialog = function(dialogMessage){
        if (self.missingPluginsDialog != null && self.missingPluginsDialog.is(":visible")){
            return;
        }

        self.missingPluginMessage.html(dialogMessage);

        self.confirmButton.unbind("click");
        self.confirmButton.bind("click", function() {
            disableCheck = self.deactivatePluginCheck()
            if (disableCheck == true) {
                self.pluginSettings.pluginCheckActivated(false)
                self.apiClient.callDeactivatePluginCheck();
            }
            self.hideDialog();
        });

        self.missingPluginsDialog.modal({
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



}
