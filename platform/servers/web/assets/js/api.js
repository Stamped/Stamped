
if (typeof(api) == "undefined") {
    api = {};
    _api = {};
}

api.init = function() {
    "/v0/oauth2/token.json"
    
    windowHeight = function(){
        currentWindowHeight = window.innerHeight;
        smallBrowser = '700';
        
        if(currentWindowHeight < smallBrowser) {
            $('body').removeClass('talldisplay').addClass('smalldisplay');
        } else {
            $('body').removeClass('smalldisplay').addClass('talldisplay');
        }
    }; // windowHeight
    
    $(window).resize(function(){
        windowHeight();
    });
    
    agentInspector();
    windowHeight();
    inputManager();
    rotator();
    slider();
};

api.login = function() {
    api.
    "/v0/oauth2/login.json"
};

_api.call = function(uri, params) {
    uri = "localhost"
};

