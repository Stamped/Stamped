/* profile.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

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
            });
        });
        
        $(".stamp-gallery-nav a").each(function() {
            var href = $(this).attr('href');
            var limit_re = /([?&])limit=[\d]+/;
            var limit = "limit=10";
            
            if (href.match(limit_re)) {
                href = href.replace(limit_re, "$1" + limit);
            } else if ('?' in href) {
                href = href + "&" + limit;
            } else {
                href = href + "?" + limit;
            }
            
            $(this).attr('href', href);
        });
        
        // ---------------------------------------------------------------------
        // initialize stamp-gallery isotope / masonry layout and infinite scroll
        // ---------------------------------------------------------------------
        
        var $container = $(".stamp-gallery .stamps");
        // TODO: may not be recursive
        //$(document).emoji();
        //$container.emoji();
        
        $container.isotope({
            itemSelector    : '.stamp-gallery-item', 
            layoutMode      : "straightDown", 
        });
        
        // TODO: customize loading image
        $container.infinitescroll({
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
            $container.isotope('appended', elements);
        });
        
        var client = new StampedClient();
        var screen_name = STAMPED_PRELOAD.user.screen_name;
        console.debug("Stamped profile page for screen_name '" + screen_name + "'");
        
        // ---------------------------------------------------------------------
        // initialize parallax scrolling
        // ---------------------------------------------------------------------
        
        /*var $target1 = $('.profile-content-page .profile-header-post');
        var $target2 = $('.profile-content-page .profile-header-body');
        var t1_h     = $target1.height();
        var t2_h     = $target2.height();
        var duration = 1200;
         
        $('.sign-in a.button').click(function(event) {
            event.stopPropagation();
            
            $target1 = $target1.stop(true, false);
            $target2 = $target2.stop(true, false);
            
            var is_hiding = function($t) {
                return $t.hasClass('hidden') || $t.hasClass('hiding');
            }
            
            var show = function($t, options) {
                options = (typeof options === 'undefined' ? { } : options);
                
                $t.removeClass('hidden').removeClass('hiding').animate({
                    opacity : 1, 
                    height  : t2_h, 
                }, {
                    duration : (typeof options['duration'] === 'undefined' ? options['duration'] : duration), 
                    specialEasing : {
                        opacity : 'easeOutCubic', 
                        height  : 'easeInOutCubic'
                    }, 
                    complete : function() {
                        var complete = options['complete'];
                        
                        if (_.isFunction(complete)) {
                            complete();
                        }
                    }
                });
            };
            
            var hide = function($t, options) {
                options = (typeof options === 'undefined' ? { } : options);
                
                $t.addClass('hiding').animate({
                    opacity : 0, 
                    height  : 0, 
                }, {
                    duration : (typeof options['duration'] === 'undefined' ? options['duration'] : duration), 
                    specialEasing : {
                        opacity : 'easeInCubic', 
                        height  : 'easeInOutCubic'
                    }, 
                    complete : function() {
                        $t.addClass('hidden');
                        $t.removeClass('hiding');
                        var complete = options['complete'];
                        
                        if (_.isFunction(complete)) {
                            complete();
                        }
                    }
                });
            }
            
            if (is_hiding($target1)) {
                show($target1, {
                    complete : function() {
                        show($target2);
                    }
                });
            } else if (is_hiding($target2)) {
                show($target2);
            } else {
                hide($target2);
                
                setTimeout(function() {
                    hide($target1, {
                        duration : duration / 3
                    });
                }, (2 * duration) / 3);
            }
        });*/
        
        var $target         = $('.profile-content-page');
        var target_height   = $target.height();
        var duration        = 1200;
        
        $('.sign-in a.button').click(function(event) {
            event.stopPropagation();
            
            $target = $target.stop(true, false);
            
            // demo animation of profile header's body
            if ($target.hasClass('hidden') || $target.hasClass('hiding')) {
                $target.removeClass('hidden').removeClass('hiding').animate({
                    opacity : 1, 
                    height  : target_height
                    //top     : 0
                }, {
                    duration : duration, 
                    specialEasing : {
                        opacity : 'easeOutCubic', 
                        height  : 'easeInOutCubic'
                    }
                });
            } else {
                $target.addClass('hiding');
                
                $target.animate({
                    opacity : 0, 
                    height  : 0
                    //top     : -target_height
                }, {
                    duration : duration, 
                    specialEasing : {
                        opacity : 'easeInCubic', 
                        height  : 'easeInOutCubic'
                    }, 
                    complete : function() {
                        $target.addClass('hidden');
                        $target.removeClass('hiding');
                    }
                });
            }
        });
        
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
            height   : join_height, 
        });
        
        $sign_in.css({
            position : 'absolute', 
            float    : 'none', 
            top      : sign_in_pos.top, 
            left     : sign_in_pos.left, 
            width    : sign_in_width, 
            height   : sign_in_height, 
        });
        
        var last_ratio = null;
        
        $window.bind("scroll", function(n) {
            var cur_ratio = Math.max((target_height - $window.scrollTop()) / target_height, 0);
            
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
                
                var cur_width  = user_logo_width  - inv_cur_ratio * (user_logo_width  / 4.0);
                var cur_height = user_logo_height - inv_cur_ratio * (user_logo_height / 4.0);
                var cur_size   = cur_width + 'px ' + cur_height + 'px';
                
                $user_logo.css({
                    width  : cur_width, 
                    height : cur_height, 
                    'background-size'   : cur_size, 
                    '-webkit-mask-size' : cur_size
                });
                console.debug("cur_ratio: " + cur_ratio);
            }
        });
        
        // ---------------------------------------------------------------------
        // initialize stamp category nav bar
        // ---------------------------------------------------------------------
        
        var $nav_bar = $('#stamp-category-nav-bar');
        
        $nav_bar.find('a').each(function () {
            $(this).click(function(event) {
                event.stopPropagation();
                
                var link     = $(this);
                var category = link.parent().attr('class');
                
                // TODO: how to best update stamp-gallery contents
                console.debug(category);
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

