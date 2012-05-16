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
            $(this).click(function() {
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
         
        $('.sign-in a.button').click(function() {
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
        
        $('.sign-in a.button').click(function() {
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

