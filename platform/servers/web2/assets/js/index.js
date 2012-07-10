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
        
        
        jQuery.ease = function(start, end, duration, easing, callback, complete) {
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
            
            var params = {
                easing      : easing,
                duration    : duration,
                step        : function(index) {
                    callback(index, step_index++, estimated_num_steps, start, end);
                }
            };
            
            if (!!complete) {
                params.complete = complete;
            }
            
            return easer.css("easingIndex", start).animate({ easingIndex : end }, params);
        };
        
        var Animation = Class.extend({
            init : function(params) {
                this.params = {
                    start       : 0.0, 
                    end         : 1.0, 
                    duration    : 1000, 
                    easing      : 'linear', 
                    step        : null, 
                    complete    : null
                };
                
                for (var key in params) {
                    if (params.hasOwnProperty(key)) {
                        this.params[key] = params[key];
                    }
                }
                
                this._easer = null;
            },
            
            start : function() {
                if (!!this._easer) {
                    /// animation is already running
                    return this._easer;
                }
                
                var that       = this;
                var params     = this.params;
                var p_step     = params.step;
                var p_complete = params.complete;
                
                var callback = function(now, fx) {
                    if (!!p_step) {
                        p_step(now, fx, that);
                    }
                };
                
                var complete = function() {
                    if (!!p_complete) {
                        p_complete(that);
                    }
                };
                
                this._easer  = $.ease(params.start, params.end, params.duration, 
                                      params.easing, callback, complete);
                
                return this._easer;
            }, 
            
            stop : function(clearQueue, jumpToEnd) {
                if (!!this._easer) {
                    clearQueue = (typeof(clearQueue) !== 'undefined' ? clearQueue : false);
                    jumpToEnd  = (typeof(jumpToEnd)  !== 'undefined' ? jumpToEnd  : false);
                    
                    this._easer.stop(clearQueue, jumpToEnd);
                    this._easer = null;
                }
            }, 
            
            restart : function() {
                this.stop(true, false);
                
                return this.start();
            }
        });
        
        var get_relative_offset = function(height) {
            return Math.ceil(-100 * (height / (window.innerHeight||1))) + "%";
        };
        
        
        // ---------------------------------------------------------------------
        // intro animation
        // ---------------------------------------------------------------------
        
        
        var active_text = 'active-text';
        var active_line = 'active-line';
        
        // choose a random stanza of text to use for the intro animation
        var $texts = $(".text");
        var index  = Math.floor(Math.random() * $texts.length);
        $texts.eq(index).addClass(active_text);
        
        $(".line").fitText();
        
        var $intro_iphone   = $("#intro-iphone");
        var $intro_hero     = $("#intro-hero");
        var $body           = $("body");
        
        var intro_iphone_animation = new Animation({
            start       : 1, 
            end         : 100, 
            duration    : 400, 
            
            step        : function(value) {
                var v = -400 * Math.floor(value / 10);
                
                $intro_iphone.css('background-position', v + "px 0");
            }, 
            
            complete    : function() {
                var height = $intro_iphone.height();
                height     = (!!height ? height : 632);
                var offset = get_relative_offset(height);
                
                $intro_iphone.delay(700).animate({
                    top : offset
                }, {
                    duration : 800, 
                    easing   : "swing", 
                    complete : function() {
                        // intro animation is fully complete here
                        $body.removeClass("intro");
                        init_main();
                    }
                });
            }
        });
        
        var intro_animation = new Animation({
            duration    : 2100, 
            complete    : function() {
                var $active     = $(".active-line");
                var $next       = $active.next(".line").filter(":visible");
                
                if ($next.length > 0) {
                    $active.removeClass(active_line);
                    $next.addClass(active_line);
                    
                    intro_animation.restart();
                } else {
                    intro_iphone_animation.start();
                    
                    setTimeout(function() {
                        var height = $active.height();
                        var offset = get_relative_offset(height);
                        
                        $intro_hero.animate({
                            top : offset
                        }, {
                            duration : 600, 
                            easing   : "swing"
                        });
                    }, 50);
                }
            }
        });
        
        intro_animation.start();
        
        
        // ---------------------------------------------------------------------
        // core page content
        // ---------------------------------------------------------------------
        
        
        var init_main = function() {
            // vertically center the page's main content
            var $main = $("#main");
            var height = $main.height();
            var offset = Math.max(0, (window.innerHeight - height) / 2);
            
            $main.css('top', offset + "px");
        };
    });
})();

