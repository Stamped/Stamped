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
    
    // TODO: use Class.extend here instead of functional object syntax.
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
        
        var _getValue = function(object, prop) {
            if (object) {
                value = object[prop];
                
                if (value !== undefined) {
                    return _.isFunction(value) ? value() : value;
                }
            }
            
            return null;
        };
        
        var _typeCheck = function(value, type) {
            var array = false;
            
            if (type == 'array') {
                type  = 'object';
                array = true;
            }
            
            return (typeof(value) == type && (!array || typeof(value.length) != "undefined"));
        }
        
        var SchemaElement = Class.extend({
            // optional String name, Object constraints
            init : function(name, constraints) {
                if (typeof(constraints) == "undefined" && typeof(name) != "string") {
                    name = null;
                    constraints = name;
                }
                
                this.name = name;
                this.constraints = constraints;
                this.has_default = ('default' in constraints);
                
                if (!('type' in constraints)) {
                    throw "(element '" + name + "') type is required";
                }
                
                if (this.has_default) {
                    d = constraints['default'];
                    type = constraints['type'];
                    
                    if (!_typeCheck(d, type)) {
                        throw "(element '" + name + "') invalid default '" + d + "' (not of required type '" + type + "')";
                    }
                }
            }, 
            
            validate : function(value) {
                if (!_is_defined(value)) {
                    if ('required' in this.constraints && !!_getValue(this.constraints, 'required')) {
                        throw "missing required element '" + this.name + "'";
                    }
                    
                    if ("default" in this.constraints) {
                        return _getValue(this.constraints, "default");
                    } else {
                        return undefined;
                    }
                } else {
                    var type = this.constraints['type'];
                    
                    if (!_typeCheck(value, type)) {
                        throw "(element '" + name + "') type mismatch '" + typeof(value) + "' not of type '" + type + "'";
                    }
                    
                    return value;
                }
            }
        });
        
        var SchemaList = SchemaElement.extend({
            // optional String name, optional Object constraints, subelement schema
            init : function() {
                var varargs = Array.prototype.slice.call(arguments);
                
                var constraints = {
                    'type' : "array", 
                };
                
                var length = varargs.length;
                var index  = 0;
                var name   = null;
                var that   = this;
                
                if (length > index && typeof(varargs[index]) == "string") {
                    name   = varargs[index];
                    index += 1;
                }
                
                if (length > index && typeof(varargs[index]) == "object" && !(varargs[index] instanceof SchemaElement)) {
                    $.each(varargs[index], function(k, v) {
                        constraints[k] = v;
                    });
                    
                    index += 1;
                }
                
                this._super(name, constraints);
                
                if (index != length - 1) {
                    throw "SchemaList.init must be given exactly one subelement type: " + index + " vs " + length;
                } else {
                    this.schema = varargs[index];
                    
                    if (!(this.schema instanceof SchemaElement)) {
                        try {
                            this.schema = varargs[index].schema();
                        } catch(e) {
                            this.schema = null;
                        }
                        
                        if (!(this.schema instanceof SchemaElement)) {
                            throw "invalid subelement type for SchemaList";
                        }
                    }
                }
            }, 
            
            validate : function(value) {
                this._super(value);
                var that = this;
                
                $.each(value, function(index, element) {
                    that.schema.validate(element);
                });
            }
        });
        
        var Schema = SchemaElement.extend({
            // optional String name, optional Object constraints, optional varargs elements
            init : function() {
                var varargs = Array.prototype.slice.call(arguments);
                
                var constraints = {
                    'type' : "object", 
                    'allow_overflow' : true, 
                };
                
                var length  = varargs.length;
                var index   = 0;
                var name    = null;
                var primary = null;
                var that    = this;
                
                if (length > index && typeof(varargs[index]) == "string") {
                    name   = varargs[index];
                    index += 1;
                }
                
                if (length > index && typeof(varargs[index]) == "object" && !(varargs[index] instanceof SchemaElement)) {
                    $.each(varargs[index], function(k, v) {
                        constraints[k] = v;
                    });
                    
                    index += 1;
                }
                
                this._super(name, constraints);
                
                this.elements = [];
                this.schema   = {};
                this.defaults = {};
                
                // if there are elements
                if (index < length) {
                    $.each(varargs.slice(index), function(index, element) {
                        if (!(element instanceof SchemaElement)) {
                            throw "all arguments to Schema must be SchemaElements";
                        }
                        
                        if (_getValue(element.constraints, 'primary_id')) {
                            if (primary != null) {
                                throw "only one key may be primary; primary_id set on '" + primary + "' and '" + element.name + "'";
                            }
                            
                            primary = element.name;
                        }
                        
                        that.elements.push(element);
                        that.schema[element.name] = element;
                    });
                    
                    $.each(this.elements, function(index, element) {
                        if (element.has_default) {
                            that.defaults[element.name] = element.constraints["default"];
                        }
                    });
                    
                    if (primary != null) {
                        this.idAttribute = primary;
                    }
                }
            }, 
            
            validate : function(value) {
                //$("data").html("<pre><code style='font-size: 12px; font-family: \"courier new\" monospace;'>" + d + "</code></pre>");
                this._super(value);
                var that = this;
                
                $.each(this.elements, function(index, element) {
                    element.validate(_getValue(value, element.name));
                });
                
                if (!_getValue(this.constraints, 'allow_overflow')) {
                    $.each(value, function(key, _) {
                        if (!(key in that.schema)) {
                            throw "unrecognized attribute '" + key + "'";
                        }
                    });
                }
            }
        });
        
        var AStampedModel = Backbone.Model.extend({
            validate    : function(attributes) {
                try {
                    this.schema().validate(attributes);
                } catch(e) {
                    console.debug(e);
                    throw e;
                    
                    return "" + e;
                }
            }, 
            
            schema      : function() {
                if (this.__schema === undefined) {
                    this.__schema = this._get_schema();
                }
                
                if (this.__schema === null || this.__schema === undefined) {
                    throw "stamped model schema error: undefined schema";
                }
                
                if (!(this.__schema instanceof Schema)) {
                    throw "stamped model schema error: schema is of wrong type '" + type(this.__schema) + "'";
                }
                
                return this.__schema;
            }, 
            
            defaults    : function() {
                return _getValue(this.schema(), 'defaults');
            }, 
            
            idAttribute : function() {
                return _getValue(this.schema(), 'idAttribute');
            }, 
            
            _get_schema : function() { throw "must override _get_schema"; }
        });
        
        this.User = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(
                    new SchemaElement('user_id',            { 'type' : "string", 'required' : true, 'primary_id' : true }), 
                    new SchemaElement('name',               { 'type' : "string", 'required' : true }), 
                    new SchemaElement('screen_name',        { 'type' : "string", 'required' : true }), 
                    new SchemaElement('color_primary',      { 'type' : "string", 'default'  : "004AB2" }), 
                    new SchemaElement('color_secondary',    { 'type' : "string", }), 
                    new SchemaElement('bio',                { 'type' : "string", }), 
                    new SchemaElement('website',            { 'type' : "string", }), 
                    new SchemaElement('location',           { 'type' : "string", }), 
                    new SchemaElement('privacy',            { 'type' : "boolean", 'required' : true }), 
                    new SchemaElement('image_url',          { 'type' : "string", 'default'  : _get_static_asset_url('/img/default.jpg') }), 
                    new SchemaElement('identifier',         { 'type' : "string", }), 
                    new SchemaElement('num_stamps',         { 'type' : "number", 'default'  : 0 }), 
                    new SchemaElement('num_stamps_left',    { 'type' : "number", 'default'  : 100 }), 
                    new SchemaElement('num_friends',        { 'type' : "number", 'default'  : 0 }), 
                    new SchemaElement('num_followers',      { 'type' : "number", 'default'  : 0 }), 
                    new SchemaElement('num_faves',          { 'type' : "number", 'default'  : 0 }), 
                    new SchemaElement('num_credits',        { 'type' : "number", 'default'  : 0 }), 
                    new SchemaElement('num_credits_given',  { 'type' : "number", 'default'  : 0 }), 
                    new SchemaElement('num_likes',          { 'type' : "number", 'default'  : 0 }), 
                    new SchemaElement('num_likes_given',    { 'type' : "number", 'default'  : 0 }), 
                    new SchemaList   ('distribution', new Schema(
                        new SchemaElement('category',       { 'type' : "string", 'required' : true }), 
                        new SchemaElement('name',           { 'type' : "string" }), 
                        new SchemaElement('icon',           { 'type' : "string" }), 
                        new SchemaElement('count',          { 'type' : "number", 'default'  : 0 })
                    ))
                );
            }
        });
        
        var Action = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(
                    new SchemaElement('type',               { 'type' : "string", 'required' : true }), 
                    new SchemaElement('name',               { 'type' : "string", 'required' : true }), 
                    new SchemaList('sources', { 'required' : true }, new Schema(
                        new SchemaElement('name',           { 'type' : "string", 'required' : true }), 
                        new SchemaElement('source',         { 'type' : "string", 'required' : true }), 
                        new SchemaElement('source_id',      { 'type' : "string", }), 
                        new SchemaElement('source_data',    { 'type' : "string", }), 
                        new SchemaElement('endpoint',       { 'type' : "string", }), 
                        new SchemaElement('link',           { 'type' : "string", }), 
                        new SchemaElement('icon',           { 'type' : "string", }), 
                        new SchemaElement('completion_endpoint',    { 'type' : "string", }), 
                        new SchemaElement('completion_data',{ 'type' : "string", })
                    ))
                );
            }
        });
        
        var Image = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(
                    new SchemaElement('image',              { 'type' : "string" }), 
                    new SchemaElement('width',              { 'type' : "number" }), 
                    new SchemaElement('height',             { 'type' : "number" }), 
                    new SchemaElement('source',             { 'type' : "string" })
                );
            }
        });
        
        /*
        this.Stamp = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(
                    new SchemaElement('stamp_id',           { 'type' : "string", 'required' : true, 'primary_id' : true }), 
                    //TODO: new Entity('entity', 
                    
                    new SchemaList   ('contents', new Schema(
                        new SchemaElement('blurb',              { 'type' : "string" }), 
                        new SchemaElement('blurb_references', new SchemaList(new Schema(
                            new SchemaList('indices', new SchemaList(new SchemaElement({ 'type' : 'number' }))), 
                            
                            // TODO: how to create an Action here and utilize its schema?
                            new Action('action').schema()
                        ))), 
                        new SchemaElement('images', new SchemaList(new Image().schema())), 
                        new SchemaElement('created',        { 'type' : "string" }), 
                        new SchemaElement('modified',       { 'type' : "string" })
                    ))
                );
            }
        });*/
    };
}

