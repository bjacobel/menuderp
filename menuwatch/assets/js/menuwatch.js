// Remove items from the navbar depending on the page's context
// @params OPTIONAL a JSON object specifying IDs of elements and whether they should be "disabled" or "enabled"
// If no parameters are set, sets the default navbar (specified in var "elements")
// @returns nothing
navbar_customize = function(params){
    //default params to holding nothing
    params = typeof params !== 'undefined' ? params : {};

    $context = $("ul.nav");

    elements = {"about":"disabled", "news":"enabled", "login":"disabled", "logout":"enabled", "signup":"disabled", "account":"enabled"};

    $.each(elements, function(element, state) {
        if(params[element]!==undefined){
            elements[element] = params[element];
        }
        if(elements[element]=="disabled"){
            $("li#"+element, $context).remove();
        }
    });
};

$(document).ready(function() {

});