/* script.js - Core Stamped.com Javascript Interface
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint strict: true, plusplus: false */
/*global window, navigator, document, jQuery, setTimeout, opera, Backbone, Handlebars, _ */

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
        
        var _token = null;
        var _user  = null;
        
        /* ------------------------------------------------------------------
         * Public API Functions
         * ------------------------------------------------------------------ */
        
        /* AUTH */
        
        this.login = function(login, password) {
            return _post("/v0/oauth2/login.json", {
                login         : login, 
                password      : password, 
                client_id     : client_id, 
                client_secret : client_secret, 
            }).pipe(function (data) {
                _user  = new User(data['user']);
                _token = data['token'];
                
                return _user;
            });
        };
        
        this.is_authorized_user  = function() {
            return !!_token;
        };
        
        this.get_authorized_user = function() {
            _verify_auth();
            
            return _user;
        };
        
        /* USERS */
        
        this.get_user_by_id = function(user_id) {
            return _get("/users/show.json", { 'user_id' : user_id })
                .pipe(function (data) {
                    return new User(data);
                });
        };
        
        this.get_user_by_screen_name = function(screen_name) {
            return _get("/users/show.json", {
                'screen_name' : screen_name
            }).pipe(function (data) {
                return new User(data);
            });
        };
        
        /* STAMPS */
        
        this.get_user_stamps_by_id = function(user_id) {
            return _get("/collections/user.json", {
                'user_id' : user_id
            }).pipe(function (data) {
                return new Stamps(data);
            });
        };
        
        this.get_user_stamps_by_screen_name = function(screen_name) {
            return _get("/collections/user.json", {
                'screen_name' : screen_name
            }).pipe(function (data) {
                return new Stamps(data);
            });
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
            
            window.log("StampedClient - " + type + ": " + url, this);
            window.log(params, this);
            
            // TODO: augment params with auth token if required or available
            // TODO: handle oauth-related token renewal special-case
            
            return $.ajax({
                type        : type, 
                url         : url, 
                data        : params, 
                crossDomain : true, 
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
        
        var _get_value = function(object, prop) {
            if (object) {
                value = object[prop];
                
                if (value !== undefined) {
                    return _.isFunction(value) ? value() : value;
                }
            }
            
            return null;
        };
        
        var _type_check = function(value, type) {
            var array = false;
            
            if (type == 'array') {
                type  = 'object';
                array = true;
            }
            
            return (typeof(value) == type && (!array || typeof(value.length) != "undefined"));
        };
        
        var _throw = function(msg) {
            console.debug(msg);
            // TODO: if (DEBUG)
            debugger;
            
            throw msg;
        };
        
        var _verify_auth = function() {
            if (!that.is_authorized_user) {
                var func = arguments.callee.caller.name || "authorized function";
                
                _throw(func + " requires authorization; please login first.");
            }
        };
        
        /* ------------------------------------------------------------------
         * Private API Classes / Models
         * ------------------------------------------------------------------ */
        
        /*
         * SchemaElement provides a way to validate the type and integrity of a 
         * normal JS object. It takes in a dictionary of constraints to be 
         * enforced when validating a given value.
         * 
         * Note that as with all SchemaElements, the schema definition is 
         * decoupled from the value(s) themselves.
         * 
         * Note that SchemaElement, SchemaList, and Schema together form the 
         * basis for typing and validating arbitrarily deep, nested JSON 
         * documents (as well as normal JS objects).
         * 
         * This example creates a schema that validates number array values.
         * 
         * new SchemaList(new SchemaElement({ 'type' : "number" }));
         */
        var SchemaElement = Class.extend({
            // optional String name, Object constraints
            init : function(name, constraints) {
                if (typeof(constraints) == "undefined" && typeof(name) != "string") {
                    constraints = name;
                    name = null;
                }
                
                this.name = name || "";
                this.constraints = constraints || {};
                
                this.has_default = ('default' in this.constraints);
                
                if (!('type' in this.constraints)) {
                    _throw("(element '" + this.name + "') type is required");
                }
                
                if (this.has_default) {
                    var d = this.constraints['default'];
                    var type = this.constraints['type'];
                    
                    if (!_type_check(d, type)) {
                        _throw("(element '" + this.name + "') invalid default '" + d + "' (not of required type '" + type + "')");
                    }
                }
            }, 
            
            validate : function(value) {
                if (!_is_defined(value)) {
                    if ('required' in this.constraints && !!_get_value(this.constraints, 'required')) {
                        _throw("missing required element '" + this.name + "'");
                    }
                    
                    if ("default" in this.constraints) {
                        return _get_value(this.constraints, "default");
                    } else {
                        return undefined;
                    }
                } else {
                    var type = this.constraints['type'];
                    
                    if (!_type_check(value, type)) {
                        _throw("(element '" + name + "') type mismatch '" + typeof(value) + "' not of type '" + type + "'");
                    }
                    
                    return value;
                }
            }
        });
        
        /*
         * SchemaList provides a way to validate the structure and integrity of a 
         * normal JS array. It takes in a SchemaElement instance subelements of 
         * the array should adhere to. This SchemaElement effectively acts as the 
         * validator for each array element.
         * 
         * Note that SchemaList itself is a SchemaElement, s.t. recursive Schema 
         * definitions are easily allowed.
         * 
         * Note that as with all SchemaElements, the schema definition is 
         * decoupled from the value(s) themselves.
         * 
         * This example creates a schema that validates number array values.
         * 
         * new SchemaList(new SchemaElement({ 'type' : "number" }));
         */
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
                    _throw("SchemaList.init must be given exactly one subelement type: " + index + " vs " + length);
                } else {
                    this.schema = varargs[index];
                    
                    if (!(this.schema instanceof SchemaElement)) {
                        try {
                            this.schema = varargs[index].schema();
                        } catch(e) {
                            this.schema = null;
                        }
                        
                        if (!(this.schema instanceof SchemaElement)) {
                            _throw("invalid subelement type for SchemaList");
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
        
        /*
         * Schema provides a way to validate the structure and integrity of a 
         * normal JS object / dictionary. It takes in zero or more top-level 
         * SchemaElements representing the keys allowed / expected in the 
         * constrainted dictionary.
         * 
         * Note that Schema itself is a SchemaElement, s.t. recursive Schema 
         * definitions are easily allowed.
         * 
         * Note that as with all SchemaElements, the schema definition is 
         * decoupled from the value(s) themselves.
         * 
         * This example creates a schema that validates dictionary values 
         * containing a single, required element called 'name'.
         * 
         * new Schema(new SchemaElement('name, { 'required' : true }));
         */
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
                
                // attempt to parse name and constraints parameters via order and type constraints
                function parse_args(args, i) {
                    var length2 = args.length;
                    
                    if (length2 > i && _type_check(args[i], "string")) {
                        name = args[i];
                        i   += 1;
                    }
                    
                    if (length2 > i && _type_check(args[i], "object") && !(args[i] instanceof SchemaElement)) {
                        $.each(args[i], function(k, v) {
                            constraints[k] = v;
                        });
                        
                        i += 1;
                    }
                    
                    return i;
                }
                
                // small hack to allow name and constraints to be passed to init as arguments from 
                // another function invokation (allows for more flexible chaining).
                if (length > index && _type_check(varargs[index], "array")) {
                    args = varargs[index];
                    
                    while (args.length == 1 && _type_check(args, "array")) {
                        args = args[0];
                    }
                    
                    parse_args(args, 0);
                    index += 1;
                } else {
                    index = parse_args(varargs, index);
                }
                
                this._super(name, constraints);
                
                this.elements = [];
                this.schema   = {};
                this.defaults = {};
                
                // if there are elements
                if (index < length) {
                    $.each(varargs.slice(index), function(i, element) {
                        if (!(element instanceof SchemaElement)) {
                            var msg = "all arguments to Schema must be SchemaElements; element '" + (index + i) + 
                                      "' of incorrect type: '" + typeof(element) + "'";
                            
                            _throw(msg);
                        }
                        
                        if (_get_value(element.constraints, 'primary_id')) {
                            if (primary != null) {
                                _throw("only one key may be primary; primary_id set on '" + primary + "' and '" + element.name + "'");
                            }
                            
                            primary = element.name;
                        }
                        
                        that.elements.push(element);
                        that.schema[element.name] = element;
                    });
                    
                    $.each(this.elements, function(i, element) {
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
                    element.validate(_get_value(value, element.name));
                });
                
                if (!_get_value(this.constraints, 'allow_overflow')) {
                    $.each(value, function(key, _) {
                        if (!(key in that.schema)) {
                            _throw("unrecognized attribute '" + key + "'");
                        }
                    });
                }
            }
        });
        
        /*
         * AStampedModel is the superclass of all stamped models, combining the 
         * attribute binding benefits of Backbone.Model with the strict data 
         * validation provided by Schema.
         */
        var AStampedModel = Backbone.Model.extend({
            validate    : function(attributes) {
                try {
                    this.schema().validate(attributes);
                } catch(e) {
                    console.debug(e);
                    _throw(e);
                    
                    return "" + e;
                }
            }, 
            
            schema      : function() {
                if (arguments.length > 0) {
                    return this._get_schema(arguments);
                }
                
                if (this.__schema === undefined) {
                    this.__schema = this._get_schema();
                }
                
                if (this.__schema === null || this.__schema === undefined) {
                    _throw("stamped model schema error: undefined schema");
                }
                
                if (!(this.__schema instanceof Schema)) {
                    _throw("stamped model schema error: schema is of wrong type '" + type(this.__schema) + "'");
                }
                
                return this.__schema;
            }, 
            
            defaults    : function() {
                return _get_value(this.schema(), 'defaults');
            }, 
            
            idAttribute : function() {
                return _get_value(this.schema(), 'idAttribute');
            }, 
            
            _get_schema : function() { _throw("must override _get_schema"); }
        });
        
        var AStampedCollection = Backbone.Collection.extend({ });
        
        var AStampedView = Backbone.View.extend({
            render : function() {
                var render_template = _get_value(this, '_render_template');
                $(this.el).html(render_template(this.model.toJSON()));
                
                return this;
            }, 
            
            _render_template : function() {
                if (this.__template === undefined) {
                    this.__template = _get_value(this, '_template');
                }
                
                if (this.__template_cache === undefined) {
                    this.__template_cache = Handlebars.compile(this.__template);
                }
                
                return this.__template_cache;
            }, 
            
            _load_template  : function(template_id) {
                /*function load(url, onComplete) {
                    return $.Deferred(function (dfd) {
                        $.get(url)
                            .done(function (templates) {
                                $(templates).filter('script').each(function (i, el) {
                                    add(el.id, $(el).html().trim());
                                });
                                
                                if ($.isFunction(onComplete)) {
                                    onComplete();
                                }
                                dfd.resolve();
                            })
                            .fail(dfd.reject);
                    }).promise();
                }*/
            }, 
            
            _template       : function() { _throw("must override _template"); }
        });
        
        var StampsView = AStampedView.extend({
            _template       : function() {
                // TODO: where to load templates from? ideally pre-compiled and pre-inserted into DOM?
                // TODO: import templates.html containing any necessary precompiled Handlebars templates?
            }
        });
        
        var User = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('user_id',            { 'type' : "string", 'required' : true, 'primary_id' : true }), 
                    new SchemaElement('name',               { 'type' : "string", 'required' : true }), 
                    new SchemaElement('screen_name',        { 'type' : "string", 'required' : true }), 
                    new SchemaElement('color_primary',      { 'type' : "string", 'default'  : "004AB2" }), 
                    new SchemaElement('color_secondary',    { 'type' : "string", 'default'  : "0057D1" }), 
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
                    new SchemaList   ('distribution',       new Schema(
                        new SchemaElement('category',       { 'type' : "string", 'required' : true }), 
                        new SchemaElement('name',           { 'type' : "string" }), 
                        new SchemaElement('icon',           { 'type' : "string" }), 
                        new SchemaElement('count',          { 'type' : "number", 'default'  : 0 })
                    ))
                );
            }
        });
        
        var UserMini = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('user_id',            { 'type' : "string", 'required' : true, 'primary_id' : true }), 
                    new SchemaElement('screen_name',        { 'type' : "string", 'required' : true }), 
                    new SchemaElement('color_primary',      { 'type' : "string", 'default'  : "004AB2" }), 
                    new SchemaElement('color_secondary',    { 'type' : "string", 'default'  : "0057D1" }), 
                    new SchemaElement('privacy',            { 'type' : "boolean", 'required' : true }), 
                    new SchemaElement('image_url',          { 'type' : "string", 'default'  : _get_static_asset_url('/img/default.jpg') })
                );
            }
        });
        
        var Action = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('type',               { 'type' : "string", 'required' : true }), 
                    new SchemaElement('name',               { 'type' : "string", 'required' : true }), 
                    new SchemaList('sources',               { 'required' : true }, new Schema(
                        new SchemaElement('name',               { 'type' : "string", 'required' : true }), 
                        new SchemaElement('source',             { 'type' : "string", 'required' : true }), 
                        new SchemaElement('source_id',          { 'type' : "string", }), 
                        new SchemaElement('source_data',        { 'type' : "string", }), 
                        new SchemaElement('endpoint',           { 'type' : "string", }), 
                        new SchemaElement('link',               { 'type' : "string", }), 
                        new SchemaElement('icon',               { 'type' : "string", }), 
                        new SchemaElement('completion_endpoint',{ 'type' : "string", }), 
                        new SchemaElement('completion_data',    { 'type' : "string", })
                    ))
                );
            }
        });
        
        var Image = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('image',              { 'type' : "string" }), 
                    new SchemaElement('width',              { 'type' : "number" }), 
                    new SchemaElement('height',             { 'type' : "number" }), 
                    new SchemaElement('source',             { 'type' : "string" })
                );
            }
        });
        
        var Credit = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('user_id',            { 'type' : "string", 'required' : true }), 
                    new SchemaElement('screen_name',        { 'type' : "string", 'required' : true }), 
                    new SchemaElement('stamp_id',           { 'type' : "string" }), 
                    new SchemaElement('color_primary',      { 'type' : "string" }), 
                    new SchemaElement('color_secondary',    { 'type' : "string" }), 
                    new SchemaElement('privacy',            { 'type' : "boolean" })
                );
            }
        });
        
        var Badge = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('user_id',            { 'type' : "string" }), 
                    new SchemaElement('genre',              { 'type' : "string", 'required' : true })
                );
            }
        });
        
        var TextReference = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaList('indices',               new SchemaElement({ 'type' : 'number' })), 
                    new Action().schema('action')
                );
            }
        });
        
        var StampContent = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('blurb',              { 'type' : "string" }), 
                    new SchemaList('blurb_references',      new TextReference().schema()), 
                    new SchemaList('images',                new Image().schema()), 
                    new SchemaElement('created',            { 'type' : "string" }), 
                    new SchemaElement('modified',           { 'type' : "string" })
                );
            }
        });
        
        var StampPreviews = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaList('likes',                 new UserMini().schema()), 
                    new SchemaList('todos',                 new UserMini().schema()), 
                    new SchemaList('credits',               new StampMini().schema()), 
                    new SchemaList('comments',              new Comment().schema())
                );
            }
        });
        
        var Stamp = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('stamp_id',           { 'type' : "string", 'required' : true, 'primary_id' : true }), 
                    new EntityMini().schema('entity',       { 'required' : true }), 
                    new UserMini().schema('user',           { 'required' : true }), 
                    
                    new SchemaList('contents',              new StampContent().schema()), 
                    new SchemaList('credit',                new Credit().schema()), 
                    new SchemaList('badges',                new Badge().schema()), 
                    new SchemaList('previews',              new StampPreviews().schema()), 
                    
                    new SchemaElement('via',                { 'type' : "string" }), 
                    new SchemaElement('url',                { 'type' : "string" }), 
                    new SchemaElement('created',            { 'type' : "string" }), 
                    new SchemaElement('modified',           { 'type' : "string" }), 
                    new SchemaElement('stamped',            { 'type' : "string" }), 
                    new SchemaElement('num_comments',       { 'type' : "number", 'default' : 0 }), 
                    new SchemaElement('num_likes',          { 'type' : "number", 'default' : 0 })
                );
            }
        });
        
        var StampMini = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('stamp_id',           { 'type' : "string", 'required' : true, 'primary_id' : true }), 
                    new EntityMini().schema('entity',       { 'required' : true }), 
                    new UserMini().schema('user',           { 'required' : true }), 
                    
                    new SchemaList('contents',              new StampContent().schema()), 
                    new SchemaList('credit',                new Credit().schema()), 
                    new SchemaList('badges',                new Badge().schema()), 
                    
                    new SchemaElement('via',                { 'type' : "string" }), 
                    new SchemaElement('url',                { 'type' : "string" }), 
                    new SchemaElement('created',            { 'type' : "string" }), 
                    new SchemaElement('modified',           { 'type' : "string" }), 
                    new SchemaElement('stamped',            { 'type' : "string" }), 
                    new SchemaElement('num_comments',       { 'type' : "number", 'default' : 0 }), 
                    new SchemaElement('num_likes',          { 'type' : "number", 'default' : 0 })
                );
            }
        });
        
        var Stamps = AStampedCollection.extend({
            model : Stamp
        });
        
        var EntityMini = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('entity_id',          { 'type' : "string", 'required' : true, 'primary_id' : true }), 
                    new SchemaElement('title',              { 'type' : "string", 'required' : true }), 
                    new SchemaElement('subtitle',           { 'type' : "string", 'required' : true }), 
                    new SchemaElement('category',           { 'type' : "string", 'required' : true }), 
                    new SchemaElement('subcategory',        { 'type' : "string", 'required' : true }), 
                    new SchemaElement('coordinates',        { 'type' : "string" })
                );
            }
        });
        
        var Comment = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('comment_id',         { 'type' : "string", 'required' : true, 'primary_id' : true }), 
                    new UserMini('user',                    { 'required' : true }).schema(), 
                    new SchemaElement('stamp_id',           { 'type' : "string", 'required' : true }), 
                    new SchemaElement('restamp_id',         { 'type' : "string" }), 
                    new SchemaElement('blurb',              { 'type' : "string", 'required' : true }), 
                    new SchemaList('mentions',              new Mention().schema()), 
                    new SchemaElement('created',            { 'type' : "string" })
                );
            }
        });
        
        var Mention = AStampedModel.extend({
            _get_schema : function() {
                return new Schema(arguments, 
                    new SchemaElement('screen_name',        { 'type' : "string", 'required' : true }), 
                    new SchemaElement('user_id',            { 'type' : "string" }), 
                    new SchemaList('indices',               new SchemaElement({ 'type' : "number" }))
                );
            }
        });
    };
}

