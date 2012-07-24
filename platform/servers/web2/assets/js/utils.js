/*! utils.js - Core Stamped.com JS Utils
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: false */
/*global window, navigator, document, jQuery, setTimeout, opera */

(function() {
// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
    window.log = function f() { log.history = log.history || []; log.history.push(arguments); if(this.console) { var args = arguments, newarr; args.callee = args.callee.caller; newarr = [].slice.call(args); if (typeof console.log === 'object') log.apply.call(console.log, console, newarr); else console.log.apply(console, newarr);}};
    
    if(typeof(console.debug) === 'undefined') {
        console.debug = console.log;
    }
    
    /*! Simple JavaScript Inheritance
     * By John Resig http://ejohn.org/
     * MIT Licensed.
     */
    
    // Inspired by base2 and Prototype
    (function() {
        var initializing = false, fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;
        
        // The base Class implementation (does nothing)
        window.Class = function() {};
        
        // Create a new Class that inherits from this class
        Class.extend = function(prop) {
            var _super = this.prototype;
            
            // Instantiate a base class (but only create the instance,
            // don't run the init constructor)
            initializing  = true;
            var prototype = new this();
            initializing  = false;
         
            // Copy the properties over onto the new prototype
            for (var name in prop) {
                // Check if we're overwriting an existing function
                prototype[name] = typeof prop[name] == "function" && 
                typeof _super[name] == "function" && fnTest.test(prop[name]) ? (function(name, fn){
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
                })(name, prop[name]) : prop[name];
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
})();

