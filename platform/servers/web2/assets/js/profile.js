/* profile.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global STAMPED_PRELOAD, StampedClient, debugger, jQuery, $, History, Backbone, Handlebars, Persist, moment */

var g_update_stamps = null;

(function() {
    $(document).ready(function() {
        // ---------------------------------------------------------------------
        // initialize StampedClient
        // ---------------------------------------------------------------------
        
        
        var client      = new StampedClient();
        var screen_name = STAMPED_PRELOAD.user.screen_name;
        var update_navbar_layout = null;
        
        
        // ---------------------------------------------------------------------
        // initialize profile header navigation
        // ---------------------------------------------------------------------
        
        
        $('.profile-nav a').each(function () {
            $(this).click(function(event) {
                event.preventDefault();
                var link = $(this);
                
                link.parents(".profile-sections").each(function() {
                    var elems = $(this).find(".profile-section");
                    
                    $(elems).slideToggle('fast', function() { });
                });
                
                return false;
            });
        });
        
        $(".stamp-gallery-nav a").each(function() {
            var href = $(this).attr('href');
            var limit_re = /([?&])limit=[\d]+/;
            var limit = "limit=10";
            
            if (href.match(limit_re)) {
                href = href.replace(limit_re, "$1" + limit);
            } else if (href.indexof('?') !== -1) {
                href = href + "&" + limit;
            } else {
                href = href + "?" + limit;
            }
            
            $(this).attr('href', href);
        });
        
        // TODO: may not be recursive
        //$(document).emoji();
        //$container.emoji();
        
        
        // ---------------------------------------------------------------------
        // initialize stamp-gallery, isotope layout, and infinite scroll
        // ---------------------------------------------------------------------
        
        var $gallery = null;
        var infinite_scroll = null;
        
        var destroy_infinite_scroll = function() {
            if (infinite_scroll !== null) {
                if ($gallery !== null) {
                    $gallery.infinitescroll('destroy');
                }
                
                infinite_scroll = null;
            }
        };
        
        var destroy_gallery = function() {
            if ($gallery !== null) {
                $gallery = $(".stamp-gallery .stamps");
                $gallery.stop(true, false);
                
                destroy_infinite_scroll();
                
                $gallery.isotope('destroy');
                $gallery = null;
            }
        };
        
        var update_gallery = function(callback) {
            if ($gallery !== null) {
                $gallery = $(".stamp-gallery .stamps");
                
                $gallery.isotope('reLayout', callback);
            }
        };
        
        // use moment.js to make every stamps's timestamp human-readable and 
        // relative to now (e.g., '2 weeks ago' instead of 'May 5th, 2012')
        var update_timestamps = function() {
            $('.timestamp_raw').each(function(i, elem) {
                var expl  = "";
                
                try {
                    var $elem = $(elem);
                    var ts    = moment($elem.text())
                    var now   = moment();
                    
                    if (now.diff(ts, 'months') < 1) { // within 1 month
                        expl = ts.fromNow();
                    } else if (now.diff(ts, 'years') <= 1) { // within 1 year
                        expl = ts.format("MMM Do");
                    } else { // after 1 year
                        expl = ts.format("MMM Do YYYY");
                    }
                } catch(e) { 
                    return;
                }
                
                $elem.removeClass('timestamp_raw').text(expl).addClass('timestamp');
            });
        };
        
        var last_layout = null;
        
        // lazily relayout the stamp gallery using isotope
        // NOTE: we apply time-based coalescing here s.t. if this function is 
        // called several times, it will attempt to only update the layout once
        // to avoid doing extra, unnecessary work / rendering that could result 
        // in a choppier end-user experience.
        var update_gallery_layout = function(force) {
            force   = (typeof(force) === 'undefined' ? false : force);
            var now = new Date().getTime();
            
            if (force || last_layout === null || now - last_layout > 100) {
                last_layout = now;
                
                update_gallery(function() {
                    update_navbar_layout(true);
                    last_layout = new Date().getTime();
                });
            }
        };
        
        // post-processing of newly added stamps, including:
        //   1) using moment.js to make the stamp's timestamp human-readable and 
        //      relative to now (e.g., '2 weeks ago' instead of 'May 5th, 2012')
        //   2) enforce predence of rhs stamp preview images
        //   3) relayout the stamp gallery lazily whenever a new image is loaded
        var update_stamps = function() {
            update_timestamps();
            
            $('.stamp-preview').each(function(i, elem) {
                var $this = $(this);
                
                // enforce precedence of stamp preview images
                var update_images = function() {
                    var images = [];
                    
                    var find = function(selector) {
                        var $elements = $this.find(selector);
                        $elements     = $elements.filter(function() {
                            return !$(this).hasClass('hidden');
                        });
                        
                        $elements.each(function(i, element) {
                            element.onerror = function() {
                                var $element = $(element);
                                $element.addClass('hidden');
                                
                                update_images();
                            };
                        });
                        
                        return $elements;
                    };
                    
                    images.push.apply(images, $this.find('.stamp-map'));
                    images.push.apply(images, find('.stamp-user-image img'));
                    images.push.apply(images, find('.stamp-entity-image img'));
                    images.push.apply(images, $this.find('.stamp-icon'));
                    
                    if (images.length > 0) {
                        var preview  = images[0];
                        var $preview = $(preview);
                        var i;
                        
                        if ($preview.is("img")) {
                            // ensure gallery's layout is updated whenever this 
                            preview.onload = function() {
                                setTimeout(update_gallery_layout, 100);
                            };
                        }
                        
                        $preview.show();
                        
                        for (i = 1; i < images.length; i++) {
                            var $image = $(images[i]);
                            
                            $image.hide();
                        }
                    }
                    
                    update_gallery_layout(true);
                };
                
                update_images();
            });
            
            $('a.sdetail').click(function(event) {
                event.preventDefault();
                
                var $this = $(this);
                var $link  = $($this.find('.pronounced-title a').get(0));
                var href  = $link.attr('href');
                href      = href.replace('http://www.stamped.com', '');
                
                console.debug(href);
                $.colorbox({
                    'href' : href
                });
                
                return false;
            });
            
            /*$('.stamp-gallery-item').click(function(event) {
                //event.preventDefault();
                
                return;
                var $this = $(this);
                $this.find('.pronounced-title a').each(function(i, elem) {
                    var $elem = $(elem);
                    var href  = $elem.attr('href');
                    href      = href.replace('http://www.stamped.com', '');
                    
                    console.debug(href);
                    window.location = href;
                    //$.colorbox({
                    //    'href' : href
                    //});
                });
            });*/
            
			$("a.lightbox").fancybox({
                openEffect      : 'elastic', 
                openEasing      : 'easeOutBack', 
                openSpeed       : 300, 
                
                closeEffect     : 'elastic', 
                closeEasing     : 'easeInBack', 
                closeSpeed      : 300, 
                
				closeClick      : true, 
                maxWidth        : (2 * window.innerWidth) / 3
			});
            
            /*$('.stamp-gallery-item .pronounced-title').each(function(i, elem) {
                var $this = $(this);
                $this.fitText();
            });*/
        };
        
        g_update_stamps = update_stamps;
        var infinite_scroll_next_selector = "div.stamp-gallery-nav a:last";
        
        var init_infinite_scroll = function() {
            // TODO: customize loading image
            infinite_scroll = $gallery.infinitescroll({
                debug           : STAMPED_PRELOAD.DEBUG, 
                bufferPx        : 200, 
                
                navSelector     : "div.stamp-gallery-nav", 
                nextSelector    : infinite_scroll_next_selector, 
                itemSelector    : "div.stamp-gallery div.stamp-gallery-item", 
                
                loading         : {
                    finishedMsg : "No more stamps to load.", 
                    msgText     : "<em>Loading more stamps...</em>", 
                    img         : "/assets/img/loading.gif", 
                    selector    : "div.stamp-gallery-loading"
                }
            }, function(new_elements) {
                var $elements = $(new_elements);
                
                //$elements.emoji();
                $gallery.isotope('appended', $elements);
                update_stamps();
            });
        };
        
        // initialize the stamp gallery's layout with isotope and infinite scroll
        var init_gallery = function() {
            $gallery = $(".stamp-gallery .stamps");
            
            $gallery.isotope({
                itemSelector    : '.stamp-gallery-item', 
                layoutMode      : "masonry"
            });
            
            init_infinite_scroll();
        };
        
        
        // ---------------------------------------------------------------------
        // URL / history initialization and handling
        // ---------------------------------------------------------------------
        
        
        // parse the given URL for its base URL and parameters
        var parse_url = function(url) {
            var parts         = url.split('?');
            var base_url_s    = parts[0];
            var base_uri0_s   = base_url_s.split('/');
            var base_uri_s    = base_uri0_s[base_uri0_s.length - 1];
            var options_s     = {};
            
            if (parts.length === 2) {
                var opts = parts[1].match(/[a-zA-Z_][a-zA-Z0-9_]*=[^&]*/g);
                
                $.each(opts, function(i, opt) {
                    var opt_parts = opt.split('=');
                    var key = opt_parts[0];
                    
                    if (opt_parts.length === 2) {
                        var value = opt_parts[1];
                        
                        options_s[key] = value;
                    }
                });
            }
            
            return {
                base_url : base_url_s, 
                options  : options_s, 
                base_uri : base_uri_s
            };
        };
        
        var url         = document.URL;
        var parsed_url  = parse_url(url);
        
        var base_url    = parsed_url.base_url;
        var options     = parsed_url.options;
        var base_uri    = parsed_url.base_uri;
        
        // Returns a new dictionary of parameters, comprised of (opts | params) 
        // with values in params taking precedence over the default values in 
        // opts. Note that if no opts are passed in, the options parsed from 
        // this page's URL will be used as the defaults.
        var get_custom_params = function(params, opts) {
            if (typeof(opts) === 'undefined') {
                opts = options;
            }
            
            var custom_params = {};
            var key, value;
            
            for (key in opts) {
                if (opts.hasOwnProperty(key)) {
                    value = opts[key];
                    
                    if (value !== null) {
                        custom_params[key] = value;
                    } else {
                        delete custom_params[key];
                    }
                }
            }
            
            for (key in params) {
                if (params.hasOwnProperty(key)) {
                    value = params[key];
                    
                    if (value !== null) {
                        custom_params[key] = value;
                    } else {
                        delete custom_params[key];
                    }
                }
            }
            
            return custom_params;
        };
        
        var get_custom_params_string = function(params, uri) {
            if (typeof(uri) === 'undefined') {
                uri = base_uri;
            }
            
            var custom_params = get_custom_params(params);
            var first = true;
            var str   = "/" + uri;
            var key;
            
            for (key in custom_params) {
                if (custom_params.hasOwnProperty(key)) {
                    if (first) {
                        str += '?';
                        first = false;
                    } else {
                        str += "&";
                    }
                    
                    str += key + "=" + custom_params[key];
                }
            }
            
            return str;
        };
        
        var get_custom_url = function(params, url) {
            if (typeof(url) === 'undefined') {
                url = base_url;
            }
            
            var custom_params = get_custom_params(params);
            var first = true;
            var key;
            
            for (key in custom_params) {
                if (custom_params.hasOwnProperty(key)) {
                    if (first) {
                        url += '?';
                        first = false;
                    } else {
                        url += "&";
                    }
                    
                    url += key + "=" + custom_params[key];
                }
            }
            
            return url;
        };
        
        console.debug("Stamped profile page for screen_name '" + screen_name + "'");
        console.debug(options);
        
        
        // ---------------------------------------------------------------------
        // initialize responsive header that gets smaller as you scroll
        // ---------------------------------------------------------------------
        
        
        // collect the default, static positions and sizes of all header 
        // elements that we'll be animating
        var $user_logo          = $('header .user-logo-large');
        var user_logo_width     = parseFloat($user_logo.css('width'));
        var user_logo_height    = parseFloat($user_logo.css('height'));
        
        var $window             = $(window);
        var $header             = $('header .header-body');
        var header_height       = $header.height();
        var cur_header_height   = header_height;
        var min_height_ratio    = 0.5;
        
        var $join               = $('.join');
        var $join_button        = $join.find('a.button');
        
        var $sign_in            = $('.sign-in');
        var $already_stamping   = $sign_in.find('span.desc');
        var $sign_in_button     = $sign_in.find('a.button');
        
        var sign_in_button_width = $sign_in_button.width();
        
        var join_pos            = $join.position();
        var sign_in_pos         = $sign_in.position();
        
        var pad                 = 4;
        var join_width          = $join.width()  + pad;
        var join_height         = $join.height() + pad;
        
        var sign_in_width       = $sign_in.width()  + pad;
        var sign_in_height      = $sign_in.height() + pad;
        
        // now that we have the static positions and sizes of the dynamic header  
        // elements, initialize their new positioning /sizing to absolute and 
        // non-auto, respectively.
        $header.height(header_height);
        
        $join.css({
            position : 'absolute', 
            float    : 'none', 
            top      : join_pos.top, 
            left     : join_pos.left, 
            width    : join_width, 
            height   : join_height
        });
        
        $sign_in.css({
            position : 'absolute', 
            float    : 'none', 
            top      : sign_in_pos.top, 
            left     : sign_in_pos.left, 
            width    : sign_in_width, 
            height   : sign_in_height
        });
        
        var last_ratio = null;
        
        // whenever the window scrolls, check if the header's layout needs to be updated
        $window.bind("scroll", function(n) {
            var cur_ratio = (header_height - $window.scrollTop()) / header_height;
            cur_ratio     = Math.min(Math.max(cur_ratio, 0.0), 1.0);
            
            if (cur_ratio !== last_ratio) {
                last_ratio = cur_ratio;
                var inv_cur_ratio = 1.0 - cur_ratio;
                
                var cur_height_ratio = Math.max(cur_ratio, min_height_ratio);
                var cur_height = header_height * cur_height_ratio;
                
                if (cur_height !== cur_header_height) {
                    cur_header_height = cur_height;
                    $header.height(cur_header_height);
                }
                
                var cur_opacity = cur_ratio * cur_ratio;
                var style = {
                    opacity : cur_opacity
                };
                
                if (cur_opacity <= 0.2) {
                    style['visibility'] = 'hidden';
                } else {
                    style['visibility'] = 'visible';
                }
                
                $already_stamping.css(style);
                
                var cur_left = join_pos.left - inv_cur_ratio * (sign_in_button_width + 16);
                $join.css({
                    left : cur_left
                });
                
                var cur_top  = cur_ratio * sign_in_pos.top + inv_cur_ratio * join_pos.top;
                $sign_in.css({
                    top : cur_top
                });
                
                
                var cur_logo_width  = user_logo_width  - inv_cur_ratio * (user_logo_width  / 4.0);
                var cur_logo_height = user_logo_height - inv_cur_ratio * (user_logo_height / 4.0);
                var cur_logo_size   = cur_logo_width + 'px ' + cur_logo_height + 'px';
                
                $user_logo.css({
                    width  : cur_logo_width, 
                    height : cur_logo_height, 
                    'background-size'   : cur_logo_size, 
                    '-webkit-mask-size' : cur_logo_size
                });
                
                //console.debug("DYNAMIC HEADER: ratio=" + cur_ratio);
            }
        });
        
        
        // ---------------------------------------------------------------------
        // initialize stamp category nav bar
        // ---------------------------------------------------------------------
        
        
        var $nav_bar   = $('#stamp-category-nav-bar');
        var categories = 'default place music book film other';
        
        var set_body_class = function(category) {
            var $body  = $('body');
            
            $body.removeClass(categories).addClass(category);
        };
        
        // TODO: if history is disabled but JS is enabled, user will be unable 
        // to navigate categories
        
        if (History && History.enabled) {
            History.Adapter.bind(window, 'statechange', function() {
                var State    = History.getState();
                var category = 'default';
                
                if (typeof(State.data['category']) !== 'undefined') {
                    category = State.data['category'];
                }
                
                History.log(State.data, State.title, State.url);
                set_body_class(category);
                
                if (category === 'default') {
                    category = null;
                }
                
                var params    = get_custom_params({
                    category : category
                });
                
                var url       = get_custom_url(params);
                var $items    = $('.stamp-gallery-item');
                
                $gallery.css({
                    visibility : 'hidden', 
                    opacity    : 0
                });
                
                $('.stamp-gallery-nav').hide();
                $('.loading').show();
                
                $(".stamp-gallery-nav a").each(function() {
                    var href   = $(this).attr('href');
                    var parsed = parse_url(href);
                    var params = get_custom_params({ category : category }, parsed.options);
                    var url    = get_custom_url(params, parsed.base_url);
                    //console.debug('HREF: ' + url);
                    
                    $(this).attr('href', url);
                });
                
                var $target = $("<div></div>");
                
                $target.load(url + " .stamp-gallery", params, function() {
                    var $elements = $target.find('.stamp-gallery-item').remove();
                    
                    //$('.stamp-gallery-nav').show();
                    //$('.inset-stamp .number').html(stamps.length);
                    var s = ".stamp-gallery-nav a";
                    var href = $($target.find(s).get(0)).attr('href');
                    if (typeof(href) === 'undefined') {
                        href = "#";
                    }
                    console.debug("NEW HREF: " + href);
                    
                    $(infinite_scroll_next_selector).attr('href', href);
                    
                    destroy_infinite_scroll();
                    init_infinite_scroll();
                    
                    $gallery.append($elements);
                    update_stamps();
                    
                    $gallery.isotope('remove',   $items,    function() {
                        $('.loading').hide();
                    });
                    
                    $gallery.isotope('appended', $elements, function() {
                    });
                    
                    $gallery.stop(true, false).css({
                        visibility : 'visible'
                    }).animate({
                        opacity : 1
                    }, {
                        duration : 200, 
                        specialEasing : { 
                            opacity : 'easeInCubic'
                        }
                    });
                });
                
                /*
                // load stamps for new category selection via AJAX
                client.get_user_stamps_by_screen_name(screen_name, params).done(function(stamps) {
                    //console.debug("num_stamps: " + stamps.length);
                    
                    if (stamps.length > 0) {
                        var $target = $("<div></div>");
                        
                        var stamps_view = new client.StampsGalleryView({
                            model : stamps, 
                            el : $target
                        });
                        
                        stamps_view.render();
                        
                        var $elements = $target.find('.stamp-gallery-item').remove();
                        
                        //$('.stamp-gallery-nav').show();
                        //$('.inset-stamp .number').html(stamps.length);
                        
                        $gallery.append($elements);
                        update_stamps();
                        
                        $gallery.isotope('remove',   $items,    function() {
                            $('.loading').hide();
                        });
                        
                        $gallery.isotope('appended', $elements, function() {
                        });
                        
                        $gallery.stop(true, false).css({
                            visibility : 'visible'
                        }).animate({
                            opacity : 1
                        }, {
                            duration : 200, 
                            specialEasing : { 
                                opacity : 'easeInCubic'
                            }
                        });
                    }
                });*/
            });
        }
        
        // handle nav bar click routing
        $nav_bar.find('a').each(function () {
            $(this).click(function(event) {
                event.preventDefault();
                
                var link     = $(this);
                var orig_category = link.parent().attr('class');
                var category = orig_category;
                
                if (category === 'default') {
                    category = null;
                }
                
                var params   = get_custom_params({
                    category : category
                });
                
                if (History && History.enabled) {
                    var params_str = get_custom_params_string(params);
                    
                    console.debug(params);
                    console.debug(orig_category);
                    console.debug(params_str);
                    
                    var title = "Stamped - " + screen_name;
                    if (category !== null) {
                        var text = category;
                        
                        if (category === 'place') {
                            text = 'places';
                        } else if (category === 'music') {
                            text = 'music';
                        } else if (category === 'book') {
                            text = 'books';
                        } else if (category === 'film') {
                            text = 'film and tv';
                        } else if (category === 'other') {
                            text = 'other';
                        }
                        
                        title += " - " + text;
                    }
                    
                    History.pushState(params, title, params_str);
                }
                
                return false;
            });
        });
        
        var fixed_width     = 1000;
        var fixed_padding   = 80;
        var min_col_width   = 305;
        var last_nav_pos    = null;
        
        // control stamp category navbar's location
        update_navbar_layout = function(should_update_gallery) {
            should_update_gallery = (typeof(should_update_gallery) !== 'boolean' ? true : should_update_gallery);
            
            var nav_bar_width   = $nav_bar.width();
            var $stamp_gallery  = $('.stamp-gallery');
            
            if (typeof($stamp_gallery.get(0)) === 'undefined') {
                return;
            }
            
            var gallery_x       = $stamp_gallery.offset().left;
            var gallery_width   = $stamp_gallery.width();
            var wide_gallery    = 'wide-gallery';
            var narrow_gallery  = 'wide-gallery';
            var max_blurb_width = "149px";
            var min_blurb_width = (gallery_width - (62 + 24 + 148 + 24)) + "px";
            
            var width = window.innerWidth;
            var left  = gallery_x + gallery_width + fixed_padding;
            var right = (width - (gallery_x + fixed_width + nav_bar_width + fixed_padding));
            
            var pos   = left;
            var update= false;
            var large = false;
            var force_no_update = false;
            
            var reset_stamp_gallery_items = function(desired_width) {
                $stamp_gallery.find('.content').each(function(i, elem) {
                    var $elem = $(elem);
                    
                    $elem.find('.content_1').css({
                        'width'     : desired_width, 
                        'max-width' : desired_width
                    });
                });
            };
            
            /*if (gallery_width <= min_col_width + 144) {
                if (!$stamp_gallery.hasClass(narrow_gallery)) {
                    $stamp_gallery.removeClass(wide_gallery).addClass(narrow_gallery);
                    update = true;
                    
                    reset_stamp_gallery_items(max_blurb_width);
                } else {
                    force_no_update = true;
                }
            } else */
            if (right < fixed_padding / 2) {
                console.debug("SMALL GALLERY: width=" + width + ", pos=" + pos);
                
                if ($stamp_gallery.hasClass(wide_gallery) || $stamp_gallery.hasClass(narrow_gallery)) {
                    $stamp_gallery.removeClass(wide_gallery + " " + narrow_gallery);
                    update = true;
                }
                
                reset_stamp_gallery_items(min_blurb_width);
            } else {
                console.debug("LARGE GALLERY: width=" + width + ", pos=" + pos);
                large = true;
                
                if (!$stamp_gallery.hasClass(wide_gallery)) {
                    $stamp_gallery.removeClass(narrow_gallery).addClass(wide_gallery);
                    update = true;
                    
                    reset_stamp_gallery_items(max_blurb_width);
                }
            }
            
            if (!force_no_update) {
                if (update || last_nav_pos !== pos) {
                    
                    if (!large) {
                        var min_fixed_width = min_col_width + nav_bar_width + fixed_padding / 2;
                        var new_fixed_width = Math.max((width - (fixed_padding + nav_bar_width)), min_fixed_width)
                        
                        $('.fixedwidth').width(new_fixed_width);
                        update = true;
                    } else {
                        $('.fixedwidth').width("1000px");
                    }
                }
                
                if (should_update_gallery) {
                    update_gallery_layout(update);
                }
            }
            
            if (last_nav_pos !== pos) {
                var style = {
                    left  : pos + "px"
                };
                
                if (last_nav_pos === null) {
                    style['right'] = 'auto';
                }
                
                last_nav_pos = pos;
                $nav_bar.css(style);
            }
        };
        
        $(window).resize(update_navbar_layout);
        
        // TODO: initial gallery opening animation by adding items one at a time
        update_stamps();
        init_gallery ();
        update_navbar_layout();
        
        return;
        
        var userP = client.get_user_by_screen_name(screen_name);
        
        userP.done(function (user) {
            var stampsP = client.get_user_stamps_by_screen_name(screen_name);
            
            stampsP.done(function (stamps) {
                $("#data2").hide();
                var stamps_view = new client.StampsGalleryView({
                    model : stamps, 
                    el : $("#data2")
                });
                
                $("#data").hide('slow', function() {
                    stamps_view.render();
                    $("#data2").show('slow');
                });
            });
        });
    });
})();

