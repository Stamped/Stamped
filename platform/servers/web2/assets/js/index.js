/*! index.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global STAMPED_PRELOAD, jQuery, $, History, moment */

/* TODO:
    * what easing function should we use for the iPhone reveal animation?
 */

(function() {
    $(document).ready(function() {
        
        // ---------------------------------------------------------------------
        // initialize globals and utils
        // ---------------------------------------------------------------------
        
        
        var $window             = $(window);
        var $body               = $("body");
        var $main               = $("#main");
        var $main_body          = $("#main-body");
        var $main_iphone        = $("#main-iphone");
        var $tastemaker_gallery = $("#tastemaker-gallery");
        var $tastemakers        = $(".tastemaker");
        var $map_window_url     = $("#fake-url");
        var $map_window         = $("#tastemaker-map-window");
        var $map_window_overlay = $("#tastemaker-map-window-overlay");
        var $map_window_iframe  = null;
        var $app_store_button   = $("footer .app-store-button");
        
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
            return Math.ceil(-125 * (height / (window.innerHeight || 1))) + "%";
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
        
        var fit_text_compression_factor = 0.7;
        $(".line").fitText(fit_text_compression_factor, {
            maxFontSize : '250px'
        });
        
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
                        duration : 1000, 
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
        // NOTE: if noop is false, this method will not make any modifications
        var update_main_layout = function(noop) {
            var height = $main.height();
            var offset = Math.max(0, (window.innerHeight - height) / 2);
            
            if (typeof(noop) !== 'boolean' || !noop) {
                $main.css('top', offset + "px");
            }
            
            return {
                height : height, 
                offset : offset
            };
        };
        
        var resize_panes = function(noop) {
            var $panes = $(".pane").css('min-height', 0);
            var height = 0;
            
            // find max height of all panes
            $panes.each(function(i, elem) {
                var $elem = $(elem);
                
                height = Math.max($elem.height(), height);
            });
            
            // constrain the minimum pane height to the height of the tallest pane
            if (height > 0) {
                $panes.css('min-height', height);
                
                if (typeof(noop) !== 'boolean' || !noop) {
                    return update_main_layout(noop);
                }
            }
            
            return false;
        };
        
        // initialize and display the main page content
        var init_main = function() {
            $body.addClass("main");
            resize_panes(true);
            
            var result = update_main_layout(true);
            var start  = window.innerHeight + result.height;
            
            // load the main content with a spiffy animation, translating in from beneath 
            // the bottom of the page
            $main
                .addClass("main-animating")
                .css('top', start + "px")
                .animate({
                    'top'       : result.offset + "px"
                }, {
                    easing      : "easeOutCubic", 
                    duration    : 1000, 
                    step        : function(value) {
                        var percent = (value - result.offset) / (start - result.offset);
                        
                        if (percent < 0.1) {
                            $main.removeClass("main-animating");
                        }
                    }, 
                    complete    : function() {
                        if (!resize_panes()) {
                            update_main_layout();
                        }
                        
                        $main.removeClass("main-animating");
                    }
                });
            
            // load the main content's interactive iphone with a spiffy animation, 
            // translating in from beneath the bottom of the page
            $main_iphone
                .delay(300)
                .css('top', "200%")
                .animate({
                    'top'       : "50%"
                }, {
                    easing      : "easeOutCubic", 
                    duration    : 800
                });
        };
        
        var map_window_show = function() {
            $app_store_button.hide(800);
            
            $map_window
                .stop(true, false)
                .show()
                .animate({
                    left        : "50%"
                }, {
                    easing      : "easeOutExpo", 
                    duration    : 800
                });
        };
        
        var map_window_hide = function() {
            $map_window
                .stop(true, false)
                .animate({
                    left        : "100%"
                }, {
                    easing      : "easeInQuad", 
                    duration    : 600, 
                    complete    : function() {
                        $map_window.hide();
                    }
                });
            
            $app_store_button.show(600);
        };
        
        var map_window_switch_user = function(screen_name) {
            var active = $map_window.data("active");
            
            if (screen_name !== active) {
                $map_window.data("active", screen_name);
                
                // TODO: temporary until all tastemakers have valid accounts
                var screen_name_lower = screen_name.toLowerCase();
                
                if (screen_name_lower === "justinbieber") {
                    screen_name = "robby"
                } else if (screen_name_lower === "passionpit") {
                    screen_name = "travis"
                } else if (screen_name_lower === "nytimes") {
                    screen_name = "edmuki"
                } else if (screen_name_lower === "time") {
                    screen_name = "bart"
                }
                
                $map_window_url
                    .attr("href", "/" + screen_name + "/map")
                    .text("www.stamped.com/" + screen_name + "/map");
                
                var iframe_src = "/" + screen_name + "/map?lite=true";
                
                if (!$map_window_iframe) {
                    var iframe = '<iframe id="tastemaker-map-window-iframe" frameborder="0" scrolling="no" src="' + iframe_src + '"></iframe>';
                    
                    $map_window.append(iframe);
                    $map_window_iframe = $("#tastemaker-map-window-iframe");
                } else {
                    $map_window_iframe.attr("src", iframe_src)
                    
                    $map_window_overlay
                        .stop(true, false)
                        .fadeIn(200);
                    
                    $map_window_iframe.ready(function() {
                        //console.debug("LOADED " + iframe_src);
                        
                        setTimeout(function() {
                            $map_window_overlay
                                .stop(true, false)
                                .fadeOut(500);
                        }, 3000);
                    });
                }
            }
        };
        
        // sets the active (visible) pane to the given index (valid indexes are in [0,4] inclusive)
        var set_active_pane = function(index) {
            if (index >= 0 && index <= 4) {
                var active  = "active-pane-" + index;
                
                if (!$main_body.hasClass(active)) {
                    $main_body.removeClass().addClass(active);
                    index = parseInt(index);
                    
                    // TODO: animation here
                    if (index >= 3) {
                        $main_iphone.css("visibility", "hidden");
                    } else {
                        $main_iphone.css("visibility", "visible");
                    }
                    
                    if (index === 3) {
                        map_window_show();
                    } else {
                        map_window_hide();
                    }
                    
                    return true;
                }
            }
            
            return false;
        };
        
        // switch active pane on pane nav button click
        $main.on("click", ".pane-nav-button", function(event) {
            event.preventDefault();
            
            var $this   = $(this);
            var id      = $this.attr("id");
            var index   = id.slice("pane-nav-".length);
            
            set_active_pane(index);
            return false;
        });
        
        // cycle active pane on continue button click
        $main.on("click", ".continue-button", function(event) {
            event.preventDefault();
            
            var $this   = $(this);
            var href    = $this.attr("href");
            var index   = href.slice("#pane-".length);
            
            set_active_pane(index);
            return false;
        });
        
        $main.on("click", ".lightbox-video", function(event) {
            event.preventDefault();
            
            $.fancybox({
                'padding'       : 0,
                'autoScale'     : false, 
                
                'transitionIn'  : 'none', 
                'transitionOut' : 'none', 
                
                'openEffect'    : 'elastic', 
                'openEasing'    : 'easeOutBack', 
                'openSpeed'     : 300, 
                
                'closeEffect'   : 'elastic', 
                'closeEasing'   : 'easeInBack', 
                'closeSpeed'    : 300, 
                
                'tpl'           : {
				    'error'     : '<p class="fancybox-error">Whoops! Looks like we messed something up on our end. Our bad.<br/>Please try again later.</p>', 
                    'closeBtn'  : '<a title="Close" class="close-button"><div class="close-button-inner"></div></a>'
                }, 
                
                'title'         : this.title, 
                'width'         : 680, 
                'height'        : 495,
                'href'          : this.href.replace(new RegExp("watch\\?v=", "i"), 'v/'),
                'type'          : 'swf',
                'swf'           : {
                    'wmode'             : 'transparent',
                    'allowfullscreen'   : 'true'
                }, 
            });
            
            return false;
        });
        
        $main.on("click", ".tastemaker", function(event) {
            event.preventDefault();
            
            var $this = $(this);
            var screen_name = $this.data("screen-name");
            
            map_window_switch_user(screen_name);
            return false;
        });
        
        var update_debug_transform = function() {
            /*var t = "perspective(" + $("input[title='perspective']").attr("value") + "px) " + 
                    "scale3d(" + $("input[title='scale-x']").attr("value") + ", " + 
                        $("input[title='scale-y']").attr("value") + ", " + 
                        $("input[title='scale-z']").attr("value") + ") " + 
                    "rotateY(" + $("input[title='rotate-y']").attr("value") + "deg) " + 
                    "rotateX(" + $("input[title='rotate-x']").attr("value") + "deg) " + 
                    "rotateZ(" + $("input[title='rotate-z']").attr("value") + "deg) " + 
                    "translate3d(" + $("input[title='trans-x']").attr("value") + "px, " + 
                        $("input[title='trans-y']").attr("value") + "px, " + 
                        $("input[title='trans-z']").attr("value") + "px) ";*/
            
            /*var t = $("input[title='trans']").attr("value");*/
            
            var t = "perspective(" + $("input[title='perspective']").attr("value") + "px) " + 
                    "rotate3d(" + $("input[title='x-axis']").attr("value") + ", " + 
                        $("input[title='y-axis']").attr("value") + ", " + 
                        $("input[title='z-axis']").attr("value") + ", " + 
                        $("input[title='angle']").attr("value") + "deg) " + 
                    "scale3d(" + $("input[title='scale-x']").attr("value") + ", " + 
                        $("input[title='scale-y']").attr("value") + ", " + 
                        $("input[title='scale-z']").attr("value") + ")";
            
            console.debug(t);
            
            $(".iphone-screen").css({
                '-webkit-transform' : t, 
                '-moz-transform'    : t, 
                '-ms-transform'     : t, 
                '-o-transform'      : t, 
                'transform'         : t
            });
        };
        
        $("input").change(update_debug_transform);
        
        
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
        
        update_debug_transform();
        map_window_switch_user("justinbieber");
    });
})();

