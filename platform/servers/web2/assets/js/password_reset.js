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
        
        
        var token           = STAMPED_PRELOAD.token;
        var input_selector  = ".password";
        
        var $body           = $("body");
        var $views          = $("#views");
        
        $(".submit-button").attr('disabled', true);
        
        var set_active_view = function(view) {
            $views.removeClass().addClass("active-view-" + view);
        };
        
        var is_valid_input = function(value) {
            valid = (value != "" && value.length > 0);
            
            $(input_selector).each(function(i, elem) {
                if ($(elem).val() !== value) {
                    valid = false;
                    return false;
                }
            });
            
            if (valid) {
                return value;
            } else {
                return null;
            }
        };
        
        $(input_selector).live("keyup change", function(event) {
            var $this   = $(this);
            var value   = $this.val();
            var $form   = $this.parent();
            var $button = $form.find(".submit-button");
            
            if (is_valid_input(value) !== null) {
                $button.removeAttr('disabled').addClass("active-button");
            } else {
                $button.attr('disabled', true).removeClass("active-button");
            }
            
            return true;
        });
        
        $body.on("submit", ".email-form", function(event) {
            event.preventDefault();
            
            var $this   = $(this);
            var $input  = $($this.find(input_selector).get(0));
            var value   = $input.val();
            value       = is_valid_input(value);
            
            if (!value) {
                return false;
            }
            
            var ajaxP  = $.ajax({
                type        : "POST", 
                url         : "/settings/password/reset-password", 
                data        : {
                    "token"     : token, 
                    "password"  : value
                }
            }).done(function () {
                set_active_view("success");
            }).fail(function() {
                $input.attr("value", "An error occurred; please try again later.").parent().addClass("error");
            });
            
            return false;
        });
    });
})();

