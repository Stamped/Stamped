        
        /*var update_debug_transform = function() {
            var t = "perspective(" + $("input[title='perspective']").attr("value") + "px) " + 
                    "scale3d(" + $("input[title='scale-x']").attr("value") + ", " + 
                        $("input[title='scale-y']").attr("value") + ", " + 
                        $("input[title='scale-z']").attr("value") + ") " + 
                    "rotateY(" + $("input[title='rotate-y']").attr("value") + "deg) " + 
                    "rotateX(" + $("input[title='rotate-x']").attr("value") + "deg) " + 
                    "rotateZ(" + $("input[title='rotate-z']").attr("value") + "deg) " + 
                    "translate3d(" + $("input[title='trans-x']").attr("value") + "px, " + 
                        $("input[title='trans-y']").attr("value") + "px, " + 
                        $("input[title='trans-z']").attr("value") + "px) ";
            
            t = "perspective(" + $("input[title='perspective']").attr("value") + "px) " + 
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
        
        $("input").change(update_debug_transform);*/




                // NOTE: metadata embedding approach doesn't work because it 
                // includes unicode u'' prefix on strings
                
                /*var $metadata = $this.prev('.source-metadata');
                console.debug("METADATA: " + );
                var metadata  = $.parseJSON($metadata.text());
                console.debug("METADATA: " + metadata);*/

            
            /*// initialize actions
            $sdetail.find('.action').each(function(i, elem) {
                var $elem = $(elem);
                
                if ($elem.hasClass('action-menu')) {
                    $elem.find('a.link').click(
                }
            });*/

                        /*var $comments_div = $target.find('.comments');
                        $comments_div.css({
                            'height' : $comments_div.height(), 
                            'overflow-y' : 'scroll'
                        });*/

document.URL.replace(/^.*\/(\w{1,20})\/?/, "$1");
//$("#data").append("<pre><code style='font-size: 12px; font-family: \"courier new\" monospace;'>" + JSON.stringify(user.toJSON(), null, 4) + "</code></pre>");

//stamps = JSON.stringify(stamps, null, 4);
//$("#data").append("<pre><code style='font-size: 12px; font-family: \"courier new\" monospace;'>" + JSON.stringify(stamps.toJSON(), null, 4) + "</code></pre>");
                            
                    var complete_animation = function() {
                        if (completed) {
                            /*
                            destroy_gallery();
                            stamps_view.render();
                            
                            $gallery = $('.gallery').stop(true, false);
                            init_gallery();
                            
                            $gallery.css({opacity : 1});
                            
                            update_gallery(function() {
                                $gallery.css({ opacity : 0 });
                                
                                $gallery.animate({
                                    opacity : 1
                                }, {
                                    duration : 1000, 
                                    specialEasing : {
                                        opacity : 'easeInOutCubic'
                                    }
                                });
                            });*/

                        } else {
                            setTimeout(complete_animation, 50);
                        }


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
            
            return false;
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
            
            return false;
        });
        
        /*$gallery.stop(true, false).animate({
            opacity : 0
        }, {
            duration : 1000, 
            specialEasing : {
                opacity : 'easeInOutCubic'
            }, 
            complete    : function() {
                completed = true;
            }
        });*/


        /*
        $('.sign-in a.button').click(function() {
            client.login('travis', '*******').done(function(user) {
                console.debug("login:");
                console.debug(user);
                
                client.get_authorized_user().done(function(auth_user) {
                    console.debug("authorized:");
                    console.debug(auth_user);
                });
            });
        });*/

