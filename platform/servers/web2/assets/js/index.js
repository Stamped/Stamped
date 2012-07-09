/*! index.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global STAMPED_PRELOAD, jQuery, $, History, moment */

(function() {
    $(document).ready(function() {
        jQuery.ease = function(start, end, duration, easing, callback) {
            // create a jQuery element that we'll be animating internally
            var easer = $("<div>");
            var step_index = 0;
            
            // Get the estimated number of steps - this is based on
            // the fact that jQuery appears to use a 13ms timer step.
            //
            // NOTE: Since this is based on a timer, the number of
            // steps is estimated and will vary depending on the
            // processing power of the browser.
            var estimated_num_steps = Math.ceil(duration / 13);
            
            easer.css("easingIndex", start);
            
            easer.animate({
                easingIndex : end
            }, 
            {
                easing      : easing,
                duration    : duration,
                step        : function(index) {
                    callback(index, step_index++, estimated_num_steps, start, end);
                }
            });
        };
        
        $("#iphone-intro").click(function(event) {
            var $this = $(this);
            
            $.ease(1, 100, 200, "linear", function(value) {
                var v = -400 * Math.floor(value / 10);
                
                $this.css('background-position', v + "px 0");
            });
        });
    });
})();

