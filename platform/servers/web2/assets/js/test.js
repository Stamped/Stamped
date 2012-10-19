/*! test.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global jQuery, $, History, dp, Processing */

(function() {
    $(document).ready(function() {
        
        // ---------------------------------------------------------------------
        // global initializations
        // ---------------------------------------------------------------------
        
        
        if (window.isBloggerMode == true) {
            dp.SyntaxHighlighter.BloggerMode();
        }
        
        dp.SyntaxHighlighter.ClipboardSwf = '/assets/js/libs/syntaxhighlighter/clipboard.swf';
        
        
        // ---------------------------------------------------------------------
        // URL / history initialization and handling
        // ---------------------------------------------------------------------
        
        
        // parse the given URL for its base URL and parameters
        var parse_url = function(url, title) {
            var parts         = url.split('?');
            var base_url_s    = parts[0];
            var base_uri0_s   = base_url_s.split('/');
            var base_uri_s    = base_uri0_s[base_uri0_s.length - 1];
            var options_s     = {};
            
            if (parts.length === 2) {
                var opts = parts[1].match(/[a-zA-Z0-9_]*=[^&]*/g);
                
                if (!!opts) {
                    $.each(opts, function(i, opt) {
                        var opt_parts = opt.split('=');
                        var key = opt_parts[0];
                        
                        if (opt_parts.length === 2) {
                            var value = opt_parts[1];
                            
                            options_s[key] = value;
                        }
                    });
                }
            }
            
            return {
                base_url : base_url_s, 
                options  : options_s, 
                base_uri : base_uri_s, 
                title    : title
            };
        };
        
        // returns a new dictionary of parameters, comprised of (opts | params) 
        // with values in params taking precedence over the default values in 
        // opts. Note that if no opts are passed in, the options parsed from 
        // this page's URL will be used as the defaults.
        var get_custom_params = function(params, opts) {
            if (typeof(opts) === 'undefined') {
                opts = orig_url.options;
            }
            
            var custom_params = {};
            var key, value;
            
            for (key in opts) {
                if (opts.hasOwnProperty(key)) {
                    value = opts[key];
                    
                    if (value !== null) {
                        custom_params[key] = value;
                    } else {
                        delete custom_params[key];
                    }
                }
            }
            
            for (key in params) {
                if (params.hasOwnProperty(key)) {
                    value = params[key];
                    
                    if (value !== null) {
                        custom_params[key] = value;
                    } else {
                        delete custom_params[key];
                    }
                }
            }
            
            return custom_params;
        };
        
        var get_custom_params_string = function(params, uri) {
            if (typeof(uri) === 'undefined') {
                uri = orig_url.base_uri;
            }
            
            var custom_params = get_custom_params(params);
            var first = true;
            var str   = "/" + uri;
            var key;
            
            for (key in custom_params) {
                if (custom_params.hasOwnProperty(key)) {
                    if (first) {
                        str += '?';
                        first = false;
                    } else {
                        str += "&";
                    }
                    
                    str += key + "=" + custom_params[key];
                }
            }
            
            return str;
        };
        
        var get_custom_url = function(params, url) {
            if (typeof(url) === 'undefined') {
                url = orig_url.base_url;
            }
            
            var custom_params = get_custom_params(params);
            var first = true;
            var key;
            
            for (key in custom_params) {
                if (custom_params.hasOwnProperty(key)) {
                    if (first) {
                        url += '?';
                        first = false;
                    } else {
                        url += "&";
                    }
                    
                    url += key + "=" + custom_params[key];
                }
            }
            
            return url;
        };
        
        // parse and store page's original URL for different parts, options, etc.
        var url         = document.URL;
        var title       = document.title;
        var orig_url    = parse_url(url, title);
        var key;
        
        var abstraction_params = {};
        var empty = true;
        
        for (key in orig_url.options) {
            var i = parseInt(key);
            
            if (!isNaN(i)) {
                abstraction_params[key] = unescape(orig_url.options[key]);
                empty = false;
            }
        }
        
        if (!empty) {
            if (typeof(window.console) !== 'undefined' && typeof(window.console.debug) !== 'undefined') {
                console.debug(abstraction_params);
            }
        }
        
        var init_abstraction = function() {
            var processing = Processing.getInstanceById("processing");
            
            if (!processing) {
                setTimeout(init_abstraction, 500);
                
                return;
            }
            
            var model = processing.abstraction_model;
            var vars  = processing.abstraction_variables;
            
            if (!!model) {
                for (key in abstraction_params) {
                    var variable = vars[key];
                    
                    if (!!variable) {
                        model.set(key, variable.parse_value(abstraction_params[key]));
                    } else {
                        if (typeof(window.console) !== 'undefined' && typeof(window.console.log) !== 'undefined') {
                            console.log("invalid abstraction param: " + key);
                        }
                    }
                }
                
                model.on("change", function() {
                    console.debug(model.changed);
                    // extract current params and update URL via History.js
                    for (key in model.changed) {
                        var variable = vars[key];
                        
                        if (!!variable) {
                            abstraction_params[key] = variable.toString(model.attributes[key]);
                        }
                    }
                    
                    var params_str = get_custom_params_string(abstraction_params);
                    
                    if (History && History.enabled) {
                        History.pushState(abstraction_params, document.title, params_str);
                    }
                });
            }
        };
        
        init_abstraction();
        
        var open_context_help = function(event, method) {
            event.preventDefault();
            
            var $target = $(event.target);
            var keyword = $.trim($target.text());
            
            var href = "http://processingjs.org/reference/" + keyword;
            
            if (method) {
                href += "_";
            }
            
            href += "/";
            
            //console.debug(href);
            $.fancybox.open({
                href  : href, 
                type  : 'iframe'
            });
            return false;
        };
        
        $(document).on("click", ".dp-j .keyword", function(event) {
            open_context_help(event, false);
        });
        $(document).on("click", ".dp-j .builtin", function(event) {
            open_context_help(event, true);
        });
    });
})();

