/*! settings.js
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
        
        
        var token   = STAMPED_PRELOAD.token;
        var $body   = $("body");
        
        $body.on("submit", ".alert-settings-form", function(event) {
            event.preventDefault();
            
            var $this    = $(this);
            var settings = {};
            
            $this.find("input").each(function(i, elem) {
                var $elem = $(elem);
                
                settings[$elem.attr("name")] = (!!$elem.attr("checked"));
            });
            
            $(".loading").show();
            //console.debug(settings);
            settings.token = token;
            
            var ajaxP  = $.ajax({
                type        : "POST", 
                url         : "/settings/alerts/update", 
                data        : settings
            }).done(function () {
                $(".loading").hide();
                
                $("#status")
                    .text("Changes saved!")
                    .removeClass("error")
                    .show()
                    .delay(4500)
                    .fadeOut(500);
            }).fail(function() {
                $(".loading").hide();
                
                $("#status")
                    .text("Error saving changes (Please try again later)")
                    .addClass("error")
                    .show()
                    .delay(4500)
                    .fadeOut(500);
            });
            
            return false;
        });
    });
})();

