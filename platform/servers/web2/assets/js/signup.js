/*! signup.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global jQuery, $ */

(function() {
    $(document).ready(function() {
        var g_page              = STAMPED_PRELOAD.page;
        var screen_name         = STAMPED_PRELOAD.user.screen_name;
        var screen_name_lower   = screen_name.toLowerCase();
        var $body               = $("body");
        
        
        // ---------------------------------------------------------------------
        // initialize signup functionality
        // ---------------------------------------------------------------------
        
        
        var open_popup_signup = function() {
            var popup_options = g_get_fancybox_popup_large_options({
                content     : $("#popup-signup").html(), 
                type        : "html", 
                width       : 480, 
                minWidth    : 480
            });
            
            popup_options.helpers.overlay.opacity = 0.9;
            
            $.fancybox.open(popup_options);
            return false;
        };
        
        $body.on("click", ".download-stamped-popup", function(event) {
            event.preventDefault();
            
            return open_popup_signup();
        });
        
        var default_phone_number = "555-555-5555";
        var sms_message_success  = "SMS Sent!";
        var sms_message_error    = "SMS Error!";
        
        $body.on("focus", ".phone-number", function(event) {
            var $this = $(this);
            var $sms  = $this.parent();
            var value = $this.attr("value");
            
            if (value === default_phone_number || value === sms_message_success || value === sms_message_error) {
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
            if (value === default_phone_number || value === sms_message_success || value === sms_message_error || value.length <= 3) {
                return null;
            }
            
            value = value.replace(/-/g, "");
            value = value.replace(/ /g, "");
            
            var len = 10;
            if (value[0] === "+") {
                len = 12;
            }
            
            if (value.length < len) {
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
        
        // autoshow the signup popup if certain conditions are met
        if (g_page === "profile" || g_page === "sdetail") {
            var referrer = document.referrer;
            var likely_tweet = true; //(!!referrer && !!referrer.match(/.*(t\.co|twitter\.com|facebook\.com|m\.facebook\.com).*/i));
            
            if (likely_tweet && (screen_name === "travis" || screen_name === "justinbieber" || screen_name === "ellendegeneres")) {
                var key = "stamped.v1.cookies.popups.signup";
                
                if (!$.cookie(key)) {
                    $.cookie(key, "true");
                    
                    open_popup_signup();
                }
            }
        }
    });
})();

