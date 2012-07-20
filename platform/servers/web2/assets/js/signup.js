/*! signup.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global jQuery, $ */

(function() {
    $(document).ready(function() {
        var $body = $("body");
        
        
        // ---------------------------------------------------------------------
        // helpers
        // ---------------------------------------------------------------------
        
        
        // returns the default fancybox options merged with the optional given options
        var get_fancybox_options = function(options) {
            var default_options = {
                openEffect      : 'elastic', 
                openEasing      : 'easeOutBack', 
                openSpeed       : 300, 
                
                closeEffect     : 'elastic', 
                closeEasing     : 'easeInBack', 
                closeSpeed      : 300, 
                
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
        
        var get_fancybox_popup_large_options = function(options) {
            var output = get_fancybox_options({
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
        
        
        // ---------------------------------------------------------------------
        // initialize signup functionality
        // ---------------------------------------------------------------------
        
        
        $body.on("click", ".download-stamped-popup", function(event) {
            event.preventDefault();
            
            var popup_options = get_fancybox_popup_large_options({
                content     : $("#popup-signup").html(), 
                type        : "html", 
                width       : 480, 
                minWidth    : 480
            });
            
            $.fancybox.open(popup_options);
            return false;
        });
        
        var default_phone_number = "555-555-5555";
        var sms_message_success  = "SMS Sent!";
        var sms_message_error    = "SMS Error!";
        
        $body.on("focus", ".phone-number", function(event) {
            var $this = $(this);
            var $sms  = $this.parent();
            var value = $this.attr("value");
            
            if (value == default_phone_number || value == sms_message_success || value == sms_message_error) {
                $this.attr("value", "");
            }
            
            $sms.removeClass("error").addClass("active");
            
            return true;
        });
        
        $body.on("focusout", ".phone-number", function(event) {
            var $this = $(this);
            var $sms  = $this.parent();
            var value = $this.attr("value").trim();
            
            if (value.length <= 0) {
                $this.attr("value", default_phone_number);
            }
            
            $sms.removeClass("active error");
            
            return true;
        });
        
        var is_valid_number = function(value) {
            if (value == default_phone_number || value == sms_message_success || value == sms_message_error || value.length <= 3) {
                return null;
            }
            
            value = value.replace(/-/g, "");
            value = value.replace(/ /g, "");
            
            var len = 10;
            if (value[0] == "+") {
                len = 12;
            }
            
            if (value.length !== len) {
                return null;
            }
            
            return value;
        };
        
        $(".phone-number").live("keyup change", function(event) {
            var $this   = $(this);
            var value   = $this.attr("value").trim();
            var active  = "active";
            var $button = $this.parent().find(".send-button");
            
            if (is_valid_number(value) !== null) {
                $button.addClass(active);
            } else {
                $button.removeClass(active);
            }
            
            return true;
        });
        
        $body.on("submit", ".sms-form", function(event) {
            event.preventDefault();
            
            var $this   = $(this);
            var $input  = $this.find(".phone-number");
            var value   = $input.attr("value").trim();
            value       = is_valid_number(value);
            
            if (!value) {
                return false;
            }
            
            var ajaxP  = $.ajax({
                type        : "POST", 
                url         : "/download-app", 
                data        : { "phone_number" : value }
            }).done(function () {
                $input.attr("value", sms_message_success);
            }).fail(function() {
                $input.attr("value", sms_message_error).parent().addClass("error");
            });
            
            return false;
        });
    });
})();

