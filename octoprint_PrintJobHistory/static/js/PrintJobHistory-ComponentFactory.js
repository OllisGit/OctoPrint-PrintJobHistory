

function ComponentFactory(pluginId) {

    this.pluginId = pluginId
    this.COMPONENT_PREFIX = "component_";

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
