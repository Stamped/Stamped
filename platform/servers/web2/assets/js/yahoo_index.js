/*! yahoo_index.js
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
        
        $body.on("focus", "input", function(event) {
            var $this = $(this);
            var $form = $this.parent();
            var value = $this.val().trim();
            
            if (value == "Your email or username") {
                $this.attr("value", "");
            }
            
            return true;
        });
        
        $body.on("focusout", "input", function(event) {
            var $this = $(this);
            var $form = $this.parent();
            var value = $this.val().trim();
            
            if (value.length <= 0) {
                $this.attr("value", "Your email or username");
            }
            
            return true;
        });
        
        $body.on("submit", ".export-form", function(event) {
            event.preventDefault();
            
            var $this   = $(this);
            var $input  = $this.find("input");
            var value   = $input.val().trim();
            
            if (!value) {
                return false;
            }
            
            console.log(value);
            
            $(".loading").show();
            window.location = "/export-stamps?login=" + value;
            
            return false;
        });
    });
})();

