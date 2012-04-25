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
        var base = "https://dev.stamped.com";
        var that = this;
        
        var client_id     = "stampedtest";
        var client_secret = "august1ftw";
        
        /*
         * Public API Functions
         */
        
        this.init = function() {
            // pass
        };
        
        this.login = function(login, password) {
            return _post("/v0/oauth2/login.json", {
                login         : login, 
                password      : password, 
                client_id     : client_id, 
                client_secret : client_secret, 
            }).done(function (data) {
                alert(data.toSource());
            });
        };
        
        this.get_user_by_id = function(user_id) {
            return _get("/v0/collections/user.json", { 'user_id' : user_id });
        };
        
        this.get_user_by_screen_name = function(screen_name) {
            return _get("/v0/collections/user.json", { 'screen_name' : screen_name });
        };
        
        /*
         * Private API Functions
         */
        
        var _is_defined = function(v) {
            return (typeof v != "undefined" && v != null);
        };
         
        var _get = function(uri, params) {
            return _ajax("GET", uri, params);
        };
        
        var _post = function(uri, params) {
            return _ajax("POST", uri, params);
        };
        
        var _ajax = function(type, uri, params) {
            var url = base + uri;
            
            window.log(type + ": " + url, this);
            window.log(params, this);
            
            return $.ajax({
                type        : type, 
                url         : url, 
                data        : params, 
                crossDomain : true, 
                error       : function(jqXHR, textStatus, errorThrown) {
                    msg = "ERROR: '" + type + "' to '" + url + "' returned " + textStatus + " (" + params.toSource() + ")"
                    window.log(msg, this);
                }
            });
        };
    };
}

(function() {
    $(document).ready(function() {
        client = new StampedClient();
        client.init();
        
        userP = client.get_user_by_screen_name("travis");
        userP.done(function (user) {
            alert(JSON.stringify(user, undefined, 2));
        });
        //client.login("travis", "cierfshs2");
    });
})();

