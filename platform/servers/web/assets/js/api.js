
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
    params = "login=" + login + "&password=" + password + "&client_id=" + "stampedtest" + "&client_secret=" + "august1ftw";
    
    _api.call("/v0/oauth2/login.json", {
        login : login, 
        password : password, 
        client_id : 'stampedtest', 
        client_secret : 'august1ftw', 
    }, function(data) {
        console.log("success: " + data.toSource());
        alert("success" + data.toSource());
    });
    
    return false;
};

_api.call = function(uri, params, success) {
    var base = "http://localhost:19000";
    var url  = base + uri;
    
    console.log(url);
    /*var request = new XMLHttpRequest();
    
    request.open('POST', url, true);
    request.onreadystatechange = function() {
        if (request.readyState != 4) {
            return;
        }
        
        if (request.status != 200) {
            alert("error: " + request.status);
            return;
        }
        
        success(request.responseText);
    };
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    request.setRequestHeader("Content-length", params.length);
    request.send(params);
    return;*/
    
    // TODO: why doesn't this jQuery ajax request work?
    $.ajax({
        type     : "POST", 
        url      : url, 
        data     : params, 
        success  : success, 
        crossDomain : true, 
        error    : function(jqXHR, textStatus, errorThrown) {
            console.log("error");
            console.log(jqXHR.responseText)
            console.log(this.toSource());
            console.log(textStatus);
            console.log(errorThrown);
        }, 
    });
};

