/*! index.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global STAMPED_PRELOAD, jQuery, $, History, moment */

(function() {
    $(document).ready(function() {
        jQuery.ease = function( start, end, duration, easing, callback ){
            // Create a jQuery collection containing the one element
            // that we will be animating internally.
            var easer = $("<div>");
            
            // Keep track of the iterations.
            var stepIndex = 0;
            
            // Get the estimated number of steps - this is based on
            // the fact that jQuery appears to use a 13ms timer step.
            //
            // NOTE: Since this is based on a timer, the number of
            // steps is estimated and will vary depending on the
            // processing power of the browser.
            var estimatedSteps = Math.ceil(duration / 13);
            
            // Set the start index of the easer.
            easer.css("easingIndex", start);
            
            // Animate the easing index to the final value. For each
            // step of the animation, we are going to pass the
            // current step value off to the callback.
            easer.animate({
                easingIndex: end
            }, 
            {
                easing: easing,
                duration: duration,
                step: function(index) {
                    callback(index, stepIndex++, estimatedSteps, start, end);
                }
            });
        };
        
        $("#iphone-intro").click(function(event) {
            var $this = $(this);
            
            $.ease(1, 100, 200, "linear", function(value) {
                var v = -400 * Math.floor(value / 10);
                
                //console.debug(arguments);
                $this.css('background-position', v + "px 0");
            });
        });
    });
})();

