/*! password.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global window, jQuery, $ */

(function() {
    $(document).ready(function() {
        
        // ---------------------------------------------------------------------
        // initialize globals and utils
        // ---------------------------------------------------------------------
        
        
        var $body = $("body");
        
        var message_default  = "email address";
        var message_success  = "Email sent..";
        var message_error    = "Error sending email.";
        var input_selector   = ".email";
        var $views           = $("#views");
        
        $(".submit-button").attr('disabled', true);
        
        var set_active_view = function(view) {
            $views.removeClass().addClass("active-view-" + view);
        };
        
        $body.on("focus", input_selector, function(event) {
            var $this = $(this);
            var $form = $this.parent();
            var value = $this.val().trim();
            
            if (value == message_default || value == message_success || value == message_error) {
                $this.attr("value", "");
            }
            
            $form.removeClass("error").addClass("active");
            
            return true;
        });
        
        $body.on("focusout", input_selector, function(event) {
            var $this = $(this);
            var $form = $this.parent();
            var value = $this.val().trim();
            
            if (value.length <= 0) {
                $this.attr("value", message_default);
            }
            
            $form.removeClass("active error");
            
            return true;
        });
        
        var is_valid_input = function(value) {
            if (value == message_default || value == message_success || value == message_error) {
                return null;
            }
            
            var email_re = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
            
            if (email_re.test(value) && value != '') {
                return value;
            } else {
                return null;
            }
        };
        
        $(input_selector).live("keyup change", function(event) {
            var $this   = $(this);
            var value   = $this.val().trim();
            var $form   = $this.parent();
            var $button = $form.find(".submit-button");
            
            if (is_valid_input(value) !== null) {
                //console.log("VALID: " + value);
                $button.removeAttr('disabled').addClass("active-button");
            } else {
                //console.log("INVALID: " + value);
                $button.attr('disabled', true).removeClass("active-button");
            }
            
            return true;
        });
        
        $body.on("submit", ".email-form", function(event) {
            event.preventDefault();
            
            var $this   = $(this);
            var $input  = $this.find(input_selector);
            var value   = $input.val().trim();
            value       = is_valid_input(value);
            
            //console.log(value);
            if (!value) {
                return false;
            }
            
            var ajaxP  = $.ajax({
                type        : "POST", 
                url         : "/settings/password/send-reset-email", 
                data        : { "email" : value }
            }).done(function () {
                set_active_view("email");
            }).fail(function() {
                $input.attr("value", message_error).parent().addClass("error");
            });
            
            return false;
        });
    });
})();

