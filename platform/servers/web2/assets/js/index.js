/*! index.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global STAMPED_PRELOAD, jQuery, $, History, moment */

(function() {
    $(document).ready(function() {
        
        // ---------------------------------------------------------------------
        // initialize utils
        // ---------------------------------------------------------------------
        
        
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
        
        
        // ---------------------------------------------------------------------
        // initialize intro animation
        // ---------------------------------------------------------------------
        
        
        $("#iphone-intro").click(function(event) {
            var $this = $(this);
            
            $.ease(1, 100, 200, "linear", function(value) {
                var v = -400 * Math.floor(value / 10);
                
                $this.css('background-position', v + "px 0");
            });
        });
        
        
        var active_text = 'active-text';
        var active_line = 'active-line';
        
        var $texts = $(".text");
        var index  = Math.floor(Math.random() * $texts.length);
        $texts.eq(index).addClass("active-text");
        
        $(".line").fitText();
        $(".line").click(function(event) {
            event.preventDefault();
            var $active = $(".active-line");
            
            var $next = $active.next('.line');
            
            if ($next.length <= 0) {
                $next = $active.parents(".text").find(".line").first();
            }
            
            if ($next.length > 0) {
                $active.removeClass(active_line);
                $next.addClass(active_line);
            }
            
            return false;
        });
    });
})();

