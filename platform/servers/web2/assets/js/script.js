/* script.js - Main Stamped.com Javascript
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function f(){ log.history = log.history || []; log.history.push(arguments); if(this.console) { var args = arguments, newarr; args.callee = args.callee.caller; newarr = [].slice.call(args); if (typeof console.log === 'object') log.apply.call(console.log, console, newarr); else console.log.apply(console, newarr);}};

// make it safe to use console.log always
(function(a){function b(){}for(var c="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,markTimeline,profile,profileEnd,time,timeEnd,trace,warn".split(","),d;!!(d=c.pop());){a[d]=a[d]||b;}})
(function(){try{console.log();return window.console;}catch(a){return (window.console={});}}());

if (typeof(StampedClient) == "undefined") {
    var StampedClient = function() {
        var base = "http://localhost:18000";
        var that = this;
        
        this.init = function() {
            // pass
        };
        
        this.login = function(login, password) {
            return _post("/v0/oauth2/login.json", {
                login         : login, 
                password      : password, 
                client_id     : 'stampedtest', 
                client_secret : 'august1ftw', 
            }).done(function (data) {
                alert(data.toSource());
            });
        };
        
        var _post = function(uri, params) {
            return _ajax("POST", uri, params);
        };
        
        var _ajax = function(type, uri, params) {
            var url = base + uri;
            
            window.log(type + ": " + url);
            window.log(params);
            
            return $.ajax({
                type        : type, 
                url         : url, 
                data        : params, 
                crossDomain : true, 
                error       : function(jqXHR, textStatus, errorThrown) {
                    window.log("ERROR: '" + type + "' to '" + url + "' returned " + textStatus + " (" + params.toSource() + ")");
                }
            });
        };
    };
}

(function() {
    $(document).ready(function() {
        client = new StampedClient();
        client.init();
        client.login("travis", "cierfshs2");
    });
})();

