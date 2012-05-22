/* sdetail.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global STAMPED_PRELOAD, g_update_stamps, StampedClient, debugger, jQuery, $, History, Backbone, Handlebars, Persist, moment */

(function() {
    $(document).ready(function() {
        if (typeof(g_update_stamps) !== 'undefined') {
            g_update_stamps();
        }
    });
})();

