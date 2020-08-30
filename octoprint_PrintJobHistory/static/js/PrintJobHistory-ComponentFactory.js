

function PrintJobComponentFactory(pluginId) {

    this.pluginId = pluginId
    this.COMPONENT_PREFIX = "component_";

    ////////////////////////////////////////////////////////////////////////////////////////////////// DATETIME - PICKER
    /*
    <div class="input-append datetime">
        <input id="DueDate" type="text" value="13.11.2017 13:24" class="input-large; text-right"><span class="add-on" id="DueDate-Icon"><i class="icon-th"></i></span>
    </div>
    */
    this.createDateTimePicker = function(elementId, showTimePicker){

        if (showTimePicker == null){
            showTimePicker = true;
            dateTimeFormat = 'd.m.Y H:i';
        }
        if (showTimePicker == false){
            dateTimeFormat = 'd.m.Y';
        }

        var elementSelector = "#" + elementId ;
        // Build defualt widget
        var datePicker = $(elementSelector).datetimepicker({
            format:dateTimeFormat,
            closeOnDateSelect:true,
            closeOnTimeSelect:false,
            timepicker:showTimePicker,
            weeks:true
        });

        $($(elementSelector).parent().find('span[class=add-on]')[0]).on('click', function () {
            if (componentViewModel.isEnabled() == true){
                $(elementSelector).datetimepicker('show');
            }
        });

        // sync: jquery -> observable

        var componentViewModel = {
            currentDateTime: ko.observable(),
            isEnabled: ko.observable(true),
            datePicker: datePicker
        }

        return componentViewModel;
    }











/*
    <component_printstatusselection-bla></component_printstatusselection-bla>

            blaViewModel = self.componentFactory.createHelloWorldComponent("bla");
            blaViewModel.hello("SUPER!!!!");

*/
    this.createHelloWorldComponent = function(name){

        componentName = this.COMPONENT_PREFIX + "printstatusselection-" + name;

        var componentViewModel = {
            hello: ko.observable("World")
        }

        componentTemplate = "<b>Hello <span data-bind='text: hello'></span></b>";

        ko.components.register(componentName, {
            viewModel: { instance: componentViewModel },
            template: componentTemplate
        });
        return componentViewModel;
    }


}
