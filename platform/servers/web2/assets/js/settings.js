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
                
                settings[$elem.attr("name")] = (!!$elem.atr("checked"));
            });
            
            var ajaxP  = $.ajax({
                type        : "POST", 
                url         : "/settings/alerts/update", 
                data        : {
                    "token"     : token, 
                    "settings"  : settings
                }
            }).done(function () {
                alert("success");
            }).fail(function() {
                alert("Error updating settings. We've been notified of the error; please try again later. And sorry about that!!");
            });
            
            return false;
        });
    });
})();

