
if (typeof(api) == "undefined") {
    api = {};
    _api = {};
}

api.init = function() {
    //"/v0/oauth2/token.json"
    
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
};

api.login = function(login, password) {
    _api.call("/v0/oauth2/login.json", {
        login : login, 
        password : password, 
        client_id : 'stampedtest', 
        client_secret : 'august1ftw', 
    }, function() {
        console.log("success");
    });
    
    return false;
};

_api.call = function(uri, params, success) {
    base = "http://localhost:19000";
    var url  = base + uri;
    //var url  = "http://localhost:18000/index"
    
    console.log(url);
    $.ajax({
        type     : "POST", 
        dataType : "json", 
        url      : url, 
        data     : params, 
        success  : function() { alert('SUCCESS'); }, 
        //crossDomain : true, 
        error    : function(jqXHR, textStatus, errorThrown) {
            console.log("error");
            console.log(jqXHR.responseText)
            console.log(this.toSource());
            console.log(textStatus);
            console.log(errorThrown);
        }, 
    });
};

