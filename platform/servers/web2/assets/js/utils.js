/*! utils.js - Core Stamped.com JS Utils
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: false */
/*global window, navigator, document, jQuery, setTimeout, opera */

(function() {
// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
    window.log = function f(){ log.history = log.history || []; log.history.push(arguments); if(this.console) { var args = arguments, newarr; args.callee = args.callee.caller; newarr = [].slice.call(args); if (typeof console.log === 'object') log.apply.call(console.log, console, newarr); else console.log.apply(console, newarr);}};
    
    if(typeof(console.debug) === 'undefined') {
        console.debug = console.log;
    }
})();

