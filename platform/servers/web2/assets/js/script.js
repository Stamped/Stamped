/*! script.js - Core Stamped.com Javascript Interface
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: false */
/*global window, navigator, document, jQuery, setTimeout, opera */

// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function f(){ log.history = log.history || []; log.history.push(arguments); if(this.console) { var args = arguments, newarr; args.callee = args.callee.caller; newarr = [].slice.call(args); if (typeof console.log === 'object') log.apply.call(console.log, console, newarr); else console.log.apply(console, newarr);}};

// make it safe to use console.log always
(function(a){function b(){}for(var c="assert,count,debug,dir,dirxml,error,exception,group,groupCollapsed,groupEnd,info,log,markTimeline,profile,profileEnd,time,timeEnd,trace,warn".split(","),d;!!(d=c.pop());){a[d]=a[d]||b;}})
(function(){try{console.log();return window.console;}catch(a){return (window.console={});}}());

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

