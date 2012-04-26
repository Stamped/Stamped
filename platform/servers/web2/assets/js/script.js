/* script.js - Core Stamped.com Javascript Interface
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function f(){ log.history = log.history || []; log.history.push(arguments); if(this.console) { var args = arguments, newarr; args.callee = args.callee.caller; newarr = [].slice.call(args); if (typeof console.log === 'object') log.apply.call(console.log, console, newarr); else console.log.apply(console, newarr);}};

// make it safe to use console.log always
(function(a){function b(){}for(var c="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,markTimeline,profile,profileEnd,time,timeEnd,trace,warn".split(","),d;!!(d=c.pop());){a[d]=a[d]||b;}})
(function(){try{console.log();return window.console;}catch(a){return (window.console={});}}());

/* Simple JavaScript Inheritance
 * By John Resig http://ejohn.org/
 * MIT Licensed.
 */

// Inspired by base2 and Prototype
(function() {
  var initializing = false, fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;
  // The base Class implementation (does nothing)
  this.Class = function(){};
  
  // Create a new Class that inherits from this class
  Class.extend = function(prop) {
    var _super = this.prototype;
    
    // Instantiate a base class (but only create the instance,
    // don't run the init constructor)
    initializing = true;
    var prototype = new this();
    initializing = false;
    
    // Copy the properties over onto the new prototype
    for (var name in prop) {
      // Check if we're overwriting an existing function
      prototype[name] = typeof prop[name] == "function" && 
        typeof _super[name] == "function" && fnTest.test(prop[name]) ?
        (function(name, fn){
          return function() {
            var tmp = this._super;
            
            // Add a new ._super() method that is the same method
            // but on the super-class
            this._super = _super[name];
            
            // The method only need to be bound temporarily, so we
            // remove it when we're done executing
            var ret = fn.apply(this, arguments);        
            this._super = tmp;
            
            return ret;
          };
        })(name, prop[name]) :
        prop[name];
    }
    
    // The dummy class constructor
    function Class() {
      // All construction is actually done in the init method
      if ( !initializing && this.init )
        this.init.apply(this, arguments);
    }
    
    // Populate our constructed prototype object
    Class.prototype = prototype;
    
    // Enforce the constructor to be what we expect
    Class.prototype.constructor = Class;
    
    // And make this class extendable
    Class.extend = arguments.callee;
    
    return Class;
  };
})();

(function() {
    var agentInspector = function() {
        agent = navigator.userAgent.toLowerCase();
        
        is_iphone  = ((agent.indexOf('iphone')!=-1));
        is_ipad    = ((agent.indexOf('ipad')!=-1));
        is_android = ((agent.indexOf('android'))!=-1);
        
        if (is_iphone) {
            $('body').addClass('mobile-iphone');
        }
        if (is_ipad) {
            $('body').addClass('mobile-ipad');
        }
        if (is_android) {
            $('body').addClass('mobile-android');
        }
    };
    
    var windowHeight = function() {
        currentWindowHeight = window.innerHeight;
        smallBrowser = '700';
        
        if (currentWindowHeight < smallBrowser) {
            $('body').removeClass('talldisplay').addClass('smalldisplay');
        } else {
            $('body').removeClass('smalldisplay').addClass('talldisplay');
        }
    };
    
    $(window).resize(windowHeight);
    
    agentInspector();
    windowHeight();
})();

if (typeof(StampedClient) == "undefined") {
    var StampedClient = function() {
        var stamped_api_url_base    = "https://dev.stamped.com/v0";
        var stamped_static_url_base = "http://static.stamped.com/assets";
        var that = this;
        
        var client_id     = "stampedtest";
        var client_secret = "august1ftw";
        
        /* ------------------------------------------------------------------
         * Public API Functions
         * ------------------------------------------------------------------ */
        
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
        
        /* USERS */
        
        this.get_user_by_id = function(user_id) {
            return _get("/users/show.json", { 'user_id' : user_id });
        };
        
        this.get_user_by_screen_name = function(screen_name) {
            return _get("/users/show.json", { 'screen_name' : screen_name });
        };
        
        /* STAMPS */
        
        this.get_user_stamps_by_id = function(user_id) {
            return _get("/collections/user.json", { 'user_id' : user_id });
        };
        
        this.get_user_stamps_by_screen_name = function(screen_name) {
            return _get("/collections/user.json", { 'screen_name' : screen_name });
        };
        
        /* ------------------------------------------------------------------
         * Private API Functions
         * ------------------------------------------------------------------ */
        
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
            var url = stamped_api_url_base + uri;
            
            window.log("AJAX " + type + ": " + url + " " + params, this);
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
            }).pipe(function (data) {
                return $.parseJSON(data);
            });
        };
        
        var _get_static_asset_url = function(path) {
            if (path.length > 0 && path[0] != '/') {
                path = "/" + path;
            }
            
            return stamped_static_url_base + path;
        };
        
        /* ------------------------------------------------------------------
         * Private API Classes / Models
         * ------------------------------------------------------------------ */
        
        /*
        var SchemaElement = Class.extend({
            'init' : function(name, constraints) {
                this.name = name;
                this.constraints = constraints;
                
                if (!('type' in constraints)) {
                    throw "(element '" + name + "') type is required";
                }
                if (!('required' in constraints)) {
                    constraints['required'] = true;
                }
                
                if ('default' in constraints) {
                    d = constraint['default'];
                    
                    if (!(d instanceof constraints['type'])) {
                        throw "(element '" + name + "') invalid default '" + d + "' (not of required type '" + constraints['type'] + "')";
                    }
                }
            }, 
            
            validate : function(value) {
                if (!_is_defined(value)) {
                    if (constraints.required) {
                        throw "missing required element '" + name + "'";
                    }
                    
                    if ("default" in constraints) {
                        return constraints["default"];
                    } else {
                        return constraints['type']();
                    }
                } else {
                    if (!value instanceof constraints['type']) {
                        throw "(element '" + name + "') type mismatch '" + value + "' not of type '" + constraints['type'] + "'";
                    }
                    
                    return value;
                }
            }
        };
        
        var Schema = SchemaElement.extend({
            'init' : function(name) {
                
            var varargs  = Array.prototype.slice.call(arguments);
            var elements = []
            var schema   = {}
            
            for (element in arguments) {
                if (!(element instanceof SchemaElement)) {
                    throw "all arguments to Schema must be SchemaElements";
                }
                
                elements.push(element);
                schema[element.name] = element;
            }
            
            this.validate = function(value) {
                if (!(value instanceof Object)) {
                    throw "invalid schema object";
                }
                
                for (element in elements) {
                    element.validate(value[element.name] || null);
                }
                
                for (k in value) {
                    if (!(k in schema)) {
                        throw "unrecognized attribute '" + k + "'";
                    }
                }
            };
        });
        
        var Schema = Backbone.Model.extend({
            get_schema : function() {
                return Schema(
                    SchemaElement('user_id',            { 'type' : String, 'required' : true }), 
                    SchemaElement('name',               { 'type' : String, 'required' : true }), 
                    SchemaElement('screen_name',        { 'type' : String, 'required' : true }), 
                    SchemaElement('color_primary',      { 'type' : String, 'default'  : "004AB2" }), 
                    SchemaElement('color_secondary',    { 'type' : String, }), 
                    SchemaElement('bio',                { 'type' : String, }), 
                    SchemaElement('website',            { 'type' : String, }), 
                    SchemaElement('location',           { 'type' : String, }), 
                    SchemaElement('privacy',            { 'type' : Boolean, 'required' : true }), 
                    SchemaElement('image_url',          { 'type' : String, 'default'  : _get_static_asset_url('/img/default.jpg') }), 
                    SchemaElement('identifier',         { 'type' : String, }), 
                    SchemaElement('num_stamps',         { 'type' : Number, 'default'  : 0 }), 
                    SchemaElement('num_stamps_left',    { 'type' : Number, 'default'  : 100 }), 
                    SchemaElement('num_friends',        { 'type' : Number, 'default'  : 0 }), 
                    SchemaElement('num_followers',      { 'type' : Number, 'default'  : 0 }), 
                    SchemaElement('num_faves',          { 'type' : Number, 'default'  : 0 }), 
                    SchemaElement('num_credits',        { 'type' : Number, 'default'  : 0 }), 
                    SchemaElement('num_credits_given',  { 'type' : Number, 'default'  : 0 }), 
                    SchemaElement('num_likes',          { 'type' : Number, 'default'  : 0 }), 
                    SchemaElement('num_likes_given',    { 'type' : Number, 'default'  : 0 }), 
                );
            }
            
            defaults : 
        });
        
        var User = Backbone.Model.extend({
            initialize : function() { }, 
        });
        */
    };
}

