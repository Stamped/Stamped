/*! legal.js
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
        
        var $views = $("#views");
        
        $(".view-switcher").click(function(event) {
            event.preventDefault();
            
            var $this = $(this);
            $views.removeClass().addClass(this.className);
            
            return false;
        });
    });
})();

