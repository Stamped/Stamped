/*! fancybox_utils.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global jQuery, $ */

(function() {
    
    
    // ---------------------------------------------------------------------
    // fancybox utility methods
    // ---------------------------------------------------------------------
    
    
    // returns the default fancybox options merged with the optional given options
    window.g_get_fancybox_options = function(options) {
        var default_options = {
            openEffect      : 'elastic', 
            openEasing      : 'easeOutBack', 
            openSpeed       : 300, 
            
            closeEffect     : 'elastic', 
            closeEasing     : 'easeInBack', 
            closeSpeed      : 300, 
            
            maxWidth        : 320, 
            
            tpl             : {
                error       : '<p class="fancybox-error">Whoops! Looks like we messed something up on our end. Our bad.<br/>Please try again later.</p>', 
                closeBtn    : '<a title="Close" class="close-button"><div class="close-button-inner"></div></a>'
            }, 
            
            helpers         : {
                overlay     : {
                    speedIn  : 150, 
                    speedOut : 300, 
                    opacity  : 0.8, 
                    
                    css      : {
                        cursor             : 'pointer', 
                        'background-color' : '#fff'
                    }, 
                    
                    closeClick  : true
                }
            }
        };
        
        var output = {};
        
        for (var key in default_options) {
            if (default_options.hasOwnProperty(key)) {
                output[key] = default_options[key];
            }
        }
        
        if (!!options) {
            for (var key in options) {
                if (options.hasOwnProperty(key)) {
                    output[key] = options[key];
                }
            }
        }
        
        return output;
    };
    
    window.g_get_fancybox_popup_large_options = function(options) {
        var output = g_get_fancybox_options({
            scrolling   : 'no', // we prefer our own, custom jScrollPane scrolling
            wrapCSS     : '', 
            padding     : 0
        });
        
        if (!!options) {
            for (var key in options) {
                if (options.hasOwnProperty(key)) {
                    output[key] = options[key];
                }
            }
        }
        
        return output;
    };
})();

