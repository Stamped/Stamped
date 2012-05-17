/* profile.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: false */
/*global STAMPED_PRELOAD, StampedClient, debugger, jQuery, $, History, Backbone, Handlebars, Persist */

(function() {
    $(document).ready(function() {
        // ---------------------------------------------------------------------
        // initialize profile header navigation
        // ---------------------------------------------------------------------
        
        $('.profile-nav a').each(function () {
            $(this).click(function(event) {
                event.stopPropagation();
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
        // initialize stamp-gallery isotope / masonry layout and infinite scroll
        // ---------------------------------------------------------------------
        
        var $gallery = null;
        var infinite_scroll = null;
        
        var init_gallery = function() {
            $gallery = $(".stamp-gallery .stamps");
            
            $gallery.isotope({
                itemSelector    : '.stamp-gallery-item', 
                layoutMode      : "straightDown"
            });
            
            // TODO: customize loading image
            infinite_scroll = $gallery.infinitescroll({
                debug           : STAMPED_PRELOAD.DEBUG, 
                bufferPx        : 200, 
                
                navSelector     : "div.stamp-gallery-nav", 
                nextSelector    : "div.stamp-gallery-nav a:last", 
                itemSelector    : "div.stamp-gallery div.stamp-gallery-item", 
                
                loading         : {
                    finishedMsg : "No more stamps to load.", 
                    msgText     : "<em>Loading more stamps...</em>", 
                    img         : "/assets/img/loading.gif", 
                    selector    : "div.stamp-gallery-loading"
                }
            }, function(new_elements) {
                var elements = $(new_elements);
                
                $(elements).emoji();
                $gallery.isotope('appended', elements);
            });
        };
        
        var destroy_gallery = function() {
            if ($gallery !== null) {
                $gallery = $(".stamp-gallery .stamps");
                $gallery.stop(true, false);
                
                if (infinite_scroll !== null) {
                    $gallery.infinitescroll('destroy');
                    infinite_scroll = null;
                }
                
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
        
        // TODO: initial gallery opening animation by adding items one at a time
        init_gallery();
        
        var client      = new StampedClient();
        var screen_name = STAMPED_PRELOAD.user.screen_name;
        
        // ---------------------------------------------------------------------
        // initialize URL / history handling
        // ---------------------------------------------------------------------
        
        var parse_url = function(url) {
            var _parts       = url.split('?');
            var _base_url    = _parts[0];
            var _options     = {};
            var _base_uri0   = _base_url.split('/')
            var _base_uri    = _base_uri0[_base_uri0.length - 1];
            
            if (_parts.length === 2) {
                var _opts = _parts[1].match(/[a-zA-Z_][a-zA-Z0-9_]*=[^&]*/g);
                
                $.each(_opts, function(i, opt) {
                    var opt_parts = opt.split('=');
                    var key = opt_parts[0];
                    
                    if (opt_parts.length === 2) {
                        var value = opt_parts[1];
                        
                        _options[key] = value;
                    }
                });
            }
            
            return {
                base_url : _base_url, 
                options  : _options, 
                base_uri : _base_uri
            };
        };
        
        var url         = document.URL;
        var parsed_url  = parse_url(url);
        
        var base_url    = parsed_url.base_url;
        var options     = parsed_url.options;
        var base_uri    = parsed_url.base_uri;
        
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
            var str = "/" + uri + "?";
            var key;
            
            for (key in custom_params) {
                if (custom_params.hasOwnProperty(key)) {
                    str += key + "=" + custom_params[key];
                }
            }
            
            return str;
        };
        
        var get_custom_url = function(params, url) {
            if (typeof(url) === 'undefined') {
                url = base_url;
            }
            
            url += '?';
            
            var custom_params = get_custom_params(params);
            var first = true;
            var key;
            
            for (key in custom_params) {
                if (custom_params.hasOwnProperty(key)) {
                    if (first) {
                        first = false;
                    } else {
                        url += "?";
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
        
        $window.bind("scroll", function(n) {
            var cur_ratio = Math.max((header_height - $window.scrollTop()) / header_height, 0);
            
            if (cur_ratio !== last_ratio) {
                last_ratio = cur_ratio;
                var inv_cur_ratio = 1.0 - cur_ratio;
                
                var cur_height_ratio = Math.max(cur_ratio, min_height_ratio);
                var cur_height = header_height * cur_height_ratio;
                
                if (cur_height !== cur_header_height) {
                    cur_header_height = cur_height;
                    $header.height(cur_header_height);
                }
                
                var style = {
                    opacity : cur_ratio
                };
                
                if (cur_ratio < 0.1) {
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
                //console.debug("cur_ratio: " + cur_ratio);
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
                
                var params   = get_custom_params({
                    category : category
                });
                
                var $items    = $('.stamp-gallery-item');
                var completed = false;
                
                $gallery.isotope('remove', $items, function() {
                    $items.remove();
                    completed = true;
                });
                $('.loading').show();
                
                $(".stamp-gallery-nav a").each(function() {
                    var href   = $(this).attr('href');
                    var parsed = parse_url(href);
                    var params = get_custom_params({ category : category }, parsed.options);
                    var url    = get_custom_url(params, parsed.base_url);
                    console.debug('HREF: ' + url);
                    
                    $(this).attr('href', url);
                });

                client.get_user_stamps_by_screen_name(screen_name, params).done(function(stamps) {
                    //console.debug("num_stamps: " + stamps.length);
                    
                    if (stamps.length > 0) {
                        var $target = $("<div></div>");
                        
                        var stamps_view = new client.StampsGalleryView({
                            model : stamps, 
                            el : $target
                        });
                        
                        var complete_animation = function() {
                            if (completed) {
                                stamps_view.render();
                                
                                var $elements = $target.find('.stamp-gallery-item').remove();
                                
                                $('.loading').hide();
                                /*$('.inset-stamp .number').html(stamps.length);*/
                                
                                $gallery.append($elements);
                                $gallery.isotope('appended', $elements, function() { });
                            } else {
                                setTimeout(complete_animation, 50);
                            }
                        };
                        
                        complete_animation();
                    }
                });
            });
        }
        
        $nav_bar.find('a').each(function () {
            $(this).click(function(event) {
                event.stopPropagation();
                
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
                    
                    //console.debug(params);
                    //console.debug(orig_category);
                    //console.debug(params_str);
                    
                    History.pushState(params, orig_category, params_str);
                }
                
                return false;
            });
        });
        
        return;
        
        /*
        $('.sign-in a.button').click(function() {
            client.login('travis', 'cierfshs2').done(function(user) {
                console.debug("login:");
                console.debug(user);
                
                client.get_authorized_user().done(function(auth_user) {
                    console.debug("authorized:");
                    console.debug(auth_user);
                });
            });
        });*/
        
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

