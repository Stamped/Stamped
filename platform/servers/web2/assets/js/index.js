/*! index.js
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
        
        
        // high-level containers
        var $window                 = $(window);
        var $body                   = $("body");
        var $main                   = $("#main");
        var $vertically_centered    = $(".vertically-centered");
        
        // main elements
        var $main_body              = $("#main-body");
        var $main_iphone            = $("#main-iphone");
        var $main_footer            = $("#main-footer");
        var $main_stamped_logo      = $("#stamped-logo");
        
        // main iphone elements
        var $iphone_screens         = $(".iphone-screens");
        var $iphone_inbox_body      = $(".iphone-inbox-body");
        var $iphone_inbox_selection = $(".iphone-inbox-selection");
        var $iphone_back_button     = $(".iphone-screen-back-button");
        var iphone_inbox_selection  = false;
        
        // tastemaker gallery
        //var $tastemaker_gallery     = $("#tastemaker-gallery");
        var $tastemakers            = $(".tastemaker");
        
        // embedded map window
        var $map_window_url         = $("#fake-url");
        var $map_window             = $("#tastemaker-map-window");
        var $map_window_overlay     = $("#tastemaker-map-window-overlay");
        var $map_window_iframe      = null;
        
        // social links
        var $social                 = $("#social");
        
        // intro animation elements
        var $intro_iphone           = $("#intro-iphone");
        var $intro_hero             = $("#intro-hero");
        var active_text             = 'active-text';
        var active_line             = 'active-line';
        
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
        
        // utility class to control higher-level animations which are not tied directly 
        // to one or more CSS attributes
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
                    this._easer = null;
                    
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
            }, 
            
            is_running : function() {
                return !!this._easer;
            }
        });
        
        var get_relative_offset = function(height) {
            return Math.ceil(-125 * (height / (window.innerHeight || 1))) + "%";
        };
        
        
        // ---------------------------------------------------------------------
        // intro animation
        // ---------------------------------------------------------------------
        
        
        // choose a random stanza of text to use for the intro animation
        var $texts = $(".text");
        var index  = Math.floor(Math.random() * $texts.length);
        $texts.eq(index).addClass(active_text);
        
        var fit_text_compression_factor = 0.5;
        $(".line").fitText(fit_text_compression_factor);
        
        var hide_intro = function(autoplay) {
            // start the main page content animation
            init_main(autoplay);
            
            var height = $(".active-line").height();
            var offset = get_relative_offset(height);
            
            // hide the intro hero text by translating it off the top of the screen
            $intro_hero.delay(50).animate({
                top : offset
            }, {
                duration : 600, 
                easing   : "easeInCubic", 
                complete : function() {
                    $body.removeClass("intro");
                }
            });
        };
        
        // intro hero text animation
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
                    // otherwise, start the main page content animation and hide the intro hero text
                    hide_intro(true);
                }
            }
        });
        
        
        // ---------------------------------------------------------------------
        // core page content
        // ---------------------------------------------------------------------
        
        
        // auto-cycles the active pane until the user stops the animation by 
        // clicking one of the pane nav buttons
        var main_pane_cycle_animation = new Animation({
            duration    : 5000, 
            complete    : function() {
                var active  = parseInt($main_body.get(0).className.replace("active-pane-", ""));
                var next    = ((active + 1) % 5);
                
                set_active_pane(next);
                main_pane_cycle_animation.restart();
            }
        });
        
        var stamped_logo_top  = parseFloat($main_stamped_logo.css("top"));
        var stamped_logo_left = parseFloat($main_stamped_logo.css("left"));
        
        var update_stamped_logo_layout = function() {
            var scrollY     = $window.scrollTop();
            var min_offset  = -50;
            
            if ($main_stamped_logo.hasClass("stamped-logo-fixed")) {
                var p_offset    = $main_stamped_logo.parent().offset();
                
                if (p_offset.top + stamped_logo_top - scrollY >= min_offset) {
                    $main_stamped_logo.removeClass("stamped-logo-fixed").css({
                        "top"  : stamped_logo_top  + "px", 
                        "left" : stamped_logo_left + "px"
                    });
                }
            } else {
                var offset  = $main_stamped_logo.offset();
                
                if (offset.top - scrollY < min_offset) {
                    $main_stamped_logo.addClass("stamped-logo-fixed").css({
                        "top"  : min_offset  + "px", 
                        "left" : offset.left + "px"
                    });
                }
            }
        };
        
        // vertically centers the page's main content
        // NOTE: if noop is true, this method will not make any modifications
        var update_main_layout = function(noop) {
            var height = $vertically_centered.height();
            var offset = Math.max(0, (window.innerHeight - height) / 2);
            
            //console.log("height: " + height + "; offset: " + offset);
            
            if (typeof(noop) !== 'boolean' || !noop) {
                $main.css('top', offset + "px");
                
                update_stamped_logo_layout();
                
            }
            
            return {
                height : height, 
                offset : offset
            };
        };
        
        var resize_panes = function(noop) {
            var $panes = $(".pane");//.css('min-height', 0);
            var height = 0;
            
            // find max height of all panes
            $panes.each(function(i, elem) {
                var $elem = $(elem);
                
                height = Math.max($elem.height(), height);
            });
            
            // constrain the minimum pane height to the height of the tallest pane
            if (height > 0) {
                //$panes.css('min-height', height);
                
                if (typeof(noop) !== 'boolean' || !noop) {
                    return update_main_layout(noop);
                }
            }
            
            return false;
        };
        
        // initialize and display the main page content
        var init_main = function(autoplay) {
            autoplay = (typeof(autoplay) === 'undefined' ? true : autoplay);
            
            $body.addClass("main");
            resize_panes(true);
            
            var result = update_main_layout(true);
            var start  = window.innerHeight + result.height;
            
            // load the main content with a spiffy animation, translating in from beneath 
            // the bottom of the page
            $body.addClass("main-animating");
            $main
                .css('top', start + "px")
                .animate({
                    'top'       : result.offset + "px"
                }, {
                    easing      : "easeOutCubic", 
                    duration    : 1000, 
                    step        : function(value) {
                        var percent = (value - result.offset) / (start - result.offset);
                        
                        if (percent < 0.1) {
                            $body.removeClass("main-animating");
                        }
                    }, 
                    complete    : function() {
                        if (!resize_panes()) {
                            update_main_layout();
                        }
                        
                        $body.removeClass("main-animating");
                        
                        if (!!autoplay) {
                            main_pane_cycle_animation.start();
                        }
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
        
        // reveals the embedded map window via a translation from the right-hand-side of the window onto the page
        var map_window_show = function() {
            $social.hide(800);
            
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
        
        // hides the embedded map window via a translation off the right-hand-side of the window
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
            
            $social.show(600);
        };
        
        // reloads the embedded map iframe with the specified user's map page via a simple opacity animation + loading spinner
        var map_window_switch_user = function(screen_name) {
            if ($map_window.length <= 0) {
                return;
            }
            
            var active = $map_window.data("active");
            
            if (screen_name !== active) {
                $map_window.data("active", screen_name);
                $tastemakers.removeClass("active");
                $(".tastemaker-" + screen_name).addClass("active");
                
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
            if (!$body.hasClass("index")) {
                return;
            }
            
            if (index >= 0 && index <= 4) {
                var active  = "active-pane-" + index;
                
                if (!$main_body.hasClass(active)) {
                    $main_body.removeClass().addClass(active);
                    index = parseInt(index);
                    
                    if (index < 3) {
                        set_active_iphone_screen(index);
                        $main_iphone.css("visibility", "visible");
                    } else {
                        // TODO: animation here
                        $main_iphone.css("visibility", "hidden");
                    }
                    
                    if (index === 3) {
                        map_window_show();
                    } else {
                        map_window_hide();
                    }
                    
                    if (index === 4) {
                        $main_footer.addClass("watch-video-overview");
                    } else {
                        $main_footer.removeClass("watch-video-overview");
                    }
                    
                    return true;
                }
            }
            
            return false;
        };
        
        // switch active pane on pane nav button click
        $main.on("click", ".pane-nav-button", function(event) {
            event.preventDefault();
            main_pane_cycle_animation.stop();
            
            var $this   = $(this);
            var id      = $this.attr("id");
            var index   = id.slice("pane-nav-".length);
            
            set_active_pane(index);
            return false;
        });
        
        // cycle active pane on continue button click
        /*$main.on("click", ".continue-button", function(event) {
            event.preventDefault();
            main_pane_cycle_animation.stop();
            
            var $this   = $(this);
            var href    = $this.attr("href");
            var index   = href.slice("#pane-".length);
            
            set_active_pane(index);
            return false;
        });*/
        
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
        
        var iphone_screens_index_map  = {
            "0" : "inbox", 
            "1" : "sdetail", 
            "2" : "guide"
        };
        
        var iphone_screens_all = "iphone-screen-active-inbox iphone-screen-active-sdetail iphone-screen-active-guide";
        
        var set_active_iphone_screen = function(index) {
            if ($iphone_screens.length <= 0) {
                return;
            }
            
            var current_classes = $iphone_screens.get(0).className.split(/\s+/);
            var active = "iphone-screen-active-" + iphone_screens_index_map["" + index];
            
            //console.debug(active + " -- " + current_classes[0] + " -- " + current_classes[1]);
            for (var i = 0; i < current_classes.length; ++i) {
                var current = current_classes[i];
                
                if (active === current) {
                    // this iphone screen is already active
                    return;
                }
            }
            
            $iphone_screens.removeClass(iphone_screens_all).addClass(active);
        };
        
        
        // ---------------------------------------------------------------------
        // interactive iphone screen
        // ---------------------------------------------------------------------
        
        
        /*iphone_inbox_stamps = [
            {
                id : "Son of a Gun Restaurant", 
                y0 : 49, 
                y1 : 150
            }, 
            {
                id : "The Hunger Games", 
                y1 : 220
            }, 
            {
                id : "Taxi Driver", 
                y1 : 291
            }, 
            {
                id : "The Baxter Garage", 
                y1 : 396
            }, 
            {
                id : "Instagram", 
                y1 : 466
            }, 
            {
                id : "The Bourne Ultimatum (0)", 
                y1 : 537
            }, 
            {
                id : "The Bourne Ultimatum (1)", 
                y1 : 608
            }, 
            {
                id : "The Bourne Ultimatum (2)", 
                y1 : 688
            }
        ];
        
        var get_iphone_screen_body_selection = function(event) {
            var bg_y     = get_iphone_inbox_bg_pos();
            var offset_y = event.pageY - $iphone_inbox_body.offset().top;
            var offset   = offset_y - bg_y;
            
            var l  = iphone_inbox_stamps.length;
            var y0 = iphone_inbox_stamps[0].y0;
            var i, y1, stamp = null;
            
            //console.debug("bg_y: " + bg_y + "; offset_y: " + offset_y + "; offset: " + offset);
            
            for (i = 0; i < l; ++i) {
                stamp = iphone_inbox_stamps[i];
                y1    = stamp.y1;
                
                if (offset >= y0 && offset <= y1) {
                    break;
                } else {
                    y0 = y1;
                }
            }
            
            return {
                y0 : y0 + bg_y, 
                y1 : y1 + bg_y, 
                id : stamp.id
            };
        };
        
        var iphone_inbox_selection_hide = function(event) {
            if (iphone_inbox_selection) {
                $iphone_inbox_selection.css('display', 'none');
                iphone_inbox_selection = false;
            }
        };
        
        var iphone_inbox_selection_show = function(event) {
            var selection = get_iphone_screen_body_selection(event);
            
            if (!!selection) {
                iphone_inbox_selection = true;
                
                $iphone_inbox_selection.css({
                    'display'   : 'block', 
                    'height'    : (selection.y1 - selection.y0 + 1) + "px", 
                    'top'       : selection.y0 + "px"
                });
            }
            
            return selection;
        };
        
        var get_iphone_inbox_bg_pos = function() {
            var bg_pos = $iphone_inbox_body.css("background-position").split(" ");
            
            return parseInt(bg_pos[1]);
        };
        
        $iphone_inbox_body
            .drag("start", function(event, dd) {
                dd.orig_y  = -get_iphone_inbox_bg_pos();
                
                iphone_inbox_selection_hide();
            })
            .drag(function(event, dd) {
                var $this  = $(this);
                var offset = -Math.max(0, Math.min(318, dd.orig_y - dd.deltaY));
                
                $this.css('background-position', "0 " + offset + "px");
            });
        
        $iphone_inbox_body.click(function(event) {
            event.preventDefault();
            
            selection = iphone_inbox_selection_show(event);
            
            if (!!selection) {
                console.debug(selection);
                
                set_active_iphone_screen(1); // sdetail
            }
            
            return false;
        });
        
        $iphone_inbox_body.mousedown(function(event) {
            event.preventDefault();
            
            iphone_inbox_selection_show(event);
            return false;
        });
        
        $body.on("mouseup", iphone_inbox_selection_hide);*/
        
        $iphone_back_button.click(function(event) {
            event.preventDefault();
            
            main_pane_cycle_animation.stop();
            set_active_pane(0); // inbox
            
            return false;
        });
        
        var disable_main_pane_cycle_animation = function(event) {
            main_pane_cycle_animation.stop();
            
            return true;
        };
        
        // stop main cycling animation whenever the user hovers over the main 
        // stamp card, iphone, or navigation-pane
        $main_body.hover(disable_main_pane_cycle_animation);
        $main_iphone.hover(disable_main_pane_cycle_animation);
        $("#pane-nav").hover(disable_main_pane_cycle_animation);
        
        
        // ---------------------------------------------------------------------
        // setup misc bindings and start initial animations
        // ---------------------------------------------------------------------
        
        
        $(document).bind('keydown', function(e) {
            if (e.which == 27) { // ESC
                // skip the intro animation if the user presses escape
                if (intro_animation.is_running()) {
                    intro_animation.stop(true, true);
                    
                    hide_intro(false);
                } else {
                    main_pane_cycle_animation.stop();
                }
            }
        });
        
        $window.resize(update_main_layout);
        $window.scroll(update_stamped_logo_layout);
        
        $window.bind("load", function() {
            if ($body.hasClass("intro")) {
                // start the intro animation sequence
                intro_animation.start();
            } else {
                // bypass intro animation and go directly to the main page content
                init_main(true);
            }
            
            // note: we load the initial embedded map window here as opposed to including it in 
            // the page's raw html as an optimization because iframes block initial page load
            map_window_switch_user("mariobatali");
        });
    });
})();

