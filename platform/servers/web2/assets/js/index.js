/*! index.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global STAMPED_PRELOAD, jQuery, $, History, moment */

/* TODO:
    * what easing should we use for iPhone reveal animation?
    * set pane-0 min-height to max(pane-0.height(), pane-1.height(), pane-2.height(), etc.)
 */

(function() {
    $(document).ready(function() {
        
        // ---------------------------------------------------------------------
        // initialize globals and utils
        // ---------------------------------------------------------------------
        
        
        var $window     = $(window);
        var $body       = $("body");
        var $main       = $("#main");
        var $main_body  = $("#main-body");
        
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
            return Math.ceil(-100 * (height / (window.innerHeight || 1))) + "%";
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
        
        var intro_iphone_animation = new Animation({
            start       : 1, 
            end         : 100, 
            duration    : 250, 
            
            step        : function(value) {
                var v = -400 * Math.floor(value / 10);
                
                $intro_iphone.css('background-position', v + "px 0");
            }, 
            
            complete    : function() {
                var height = $intro_iphone.height();
                height     = (!!height ? height : 632);
                var offset = get_relative_offset(height);
                
                setTimeout(function() {
                    $intro_iphone.animate({
                        top : offset
                    }, {
                        duration : 800, 
                        easing   : "swing", 
                        complete : function() {
                            // intro animation is fully complete here
                            $body.removeClass("intro");
                        }
                    });
                    
                    init_main();
                }, 150);
            }
        });
        
        var intro_animation = new Animation({
            duration    : 1600, 
            complete    : function() {
                var $active     = $(".active-line");
                var $next       = $active.next(".line").filter(":visible");
                
                // if there is another line of intro text to display, toggle it to be active 
                // and restart the intro animation
                if ($next.length > 0) {
                    $active.removeClass(active_line);
                    $next.addClass(active_line);
                    
                    intro_animation.restart();
                } else {
                    // otherwise, start the iphone flipping animation and hero text translation
                    intro_iphone_animation.start();
                    
                    var height = $active.height();
                    var offset = get_relative_offset(height);
                    
                    // hide the intro hero text by translating it off the top of the screen
                    $intro_hero.animate({
                        top : offset
                    }, {
                        duration : 600, 
                        easing   : "swing"
                    });
                }
            }
        });
        
        
        // ---------------------------------------------------------------------
        // core page content
        // ---------------------------------------------------------------------
        
        
        // vertically centers the page's main content
        // NOTE: if noop is truthy, this method will not make any modifications
        var update_main_layout = function(noop) {
            var height = $main.height();
            var offset = Math.max(0, (window.innerHeight - height) / 2);
            
            if (!!noop) {
                $main.css('top', offset + "px");
            }
            
            return {
                height : height, 
                offset : offset
            };
        };
        
        // initialize and display the main page content
        var init_main = function() {
            $body.addClass("main");
            
            var $panes = $(".pane");
            var height = 0;
            
            // find max height of all panes
            $panes.each(function(i, elem) {
                var $elem = $(elem);
                
                height = Math.max($elem.height(), height);
            });
            
            // constrain the minimum pane height to the height of the tallest pane
            if (height > 0) {
                $panes.css('min-height', height);
            }
            
            var result = update_main_layout(true);
            var start  = $window.height() + result.height;
            
            // load the main content with a spiffy animation, translating in from beneath 
            // the bottom of the page
            $main
                .addClass("main-animating")
                .css('top', start + "px")
                .animate({
                    'top'       : result.offset + "px"
                }, {
                    easing      : "easeOutExpo", 
                    duration    : 1000, 
                    step        : function(value) {
                        var percent = (value - result.offset) / (start - result.offset);
                        
                        if (percent < 0.1) {
                            $main.removeClass("main-animating");
                        }
                    }, 
                    complete    : function() {
                        $main.removeClass("main-animating");
                        update_main_layout();
                    }
                });
        };
        
        var set_active_pane = function(num) {
            var active  = "active-pane-" + num;
            
            if (!$main_body.hasClass(active)) {
                $main_body.removeClass().addClass(active);
                
                return true;
            } else {
                return false;
            }
        };
        
        $main.on("click", ".pane-nav-button", function(event) {
            event.preventDefault();
            
            var $this   = $(this);
            var id      = $this.attr("id");
            var num     = id.slice("pane-nav-".length);
            
            set_active_pane(num);
            return false;
        });
        
        $main.on("click", ".continue-button", function(event) {
            event.preventDefault();
            
            var $this   = $(this);
            var href    = $this.attr("href");
            var num     = href.slice("#pane-".length);
            var active  = "active-pane-" + num;
            
            set_active_pane(num);
            return false;
        });
        
        // ---------------------------------------------------------------------
        // setup misc bindings and start initial animations
        // ---------------------------------------------------------------------
        
        
        $window.resize(update_main_layout);
        
        if ($body.hasClass("intro")) {
            // start the intro animation sequence
            intro_animation.start();
        } else {
            // bypass intro animation and go directly to the main page content
            init_main();
        }
    });
})();

