
$("#subnav").on("click", ".subnav_button", function(event) {
    event.preventDefault();
    
    var $this    = $(this);
    var $parent  = $this.parents('.profile-header-subnav');
    var bargraph = false;
    
    $parent.removeClass('subnav-active-0 subnav-active-1 subnav-active-2');
    
    if ($this.hasClass('subnav_button-0')) {
        $parent.find('.header-subsection-0').show();
        $parent.addClass('subnav-active-0');
    } else if ($this.hasClass('subnav_button-1')) {
        $parent.find('.header-subsection-1').show();
        $parent.addClass('subnav-active-1');
    } else if ($this.hasClass('subnav_button-2')) {
        bargraph = true;
        $parent.find('.header-subsection-2').show();
        $parent.addClass('subnav-active-2');
    }
    
    // TODO: better approach here than setTimeout
    setTimeout(function() {
        var $elem   = $parent.find('.header-subsection-1');
        var opacity = parseFloat($elem.css('opacity'));
        
        if (opacity <= 0.05) {
            $elem.hide();
        }
        
        $elem   = $parent.find('.header-subsection-2');
        opacity = parseFloat($elem.css('opacity'));
        
        if (opacity <= 0.05) {
            $elem.hide();
        }
    }, 200);
    
    // update the user's stamp category distribution bargraph via a spiffy animation
    $('.bargraph-row-value').each(function(i, elem) {
        var percentage  = 0;
        var opacity     = 1.0;
        var $this       = $(this);
        
        if (bargraph) {
            var count   = $this.data('count') || 0;
            
            if (count > 0) {
                percentage = 100.0 * Math.min(1.0, (.5 - (1.0 / Math.pow(count + 6, .4))) * 80.0 / 33.0);
            } else {
                percentage = 0.0;
                opacity    = 0.0;
            }
        }
        
        $this.stop(true, false).delay(50).animate({
            width   : percentage + "%", 
            opacity : opacity
        }, {
            duration : 1000, 
            specialEasing : { 
                width  : 'easeInOutBack'
            }, 
            complete : function() {
                $this.css({
                    'width'     : percentage + "%", 
                    'opacity'   : opacity
                });
            }
        });
    });
    
    return false;
});

var init_header_subsections = function() {
    var header_subsection_height = 0;
    var $header_subsections  = $('.header-subsection');
    var $header_subsection_0 = null;
    
    $header_subsections.each(function(i, elem) {
        var $elem = $(elem);
        
        if ($elem.hasClass('header-subsection-0')) {
            $header_subsection_0 = $elem;
        }
        
        header_subsection_height = Math.max($elem.height(), header_subsection_height);
    });
    
    if (!!$header_subsection_0 && header_subsection_height > 0) {
        $header_subsection_0.css({
            'height'     : header_subsection_height, 
            'min-height' : header_subsection_height
        });
    }
};




        /*var $join               = $('.join');
        var $join_button        = $join.find('a.button');
        
        var $login              = $('.login');
        var $already_stamping   = $login.find('span.desc');
        var $login_button       = $login.find('a.button');
        
        var login_button_width  = $login_button.width();
        
        var join_pos            = $join.position();
        var login_pos           = $login.position();
        
        var pad                 = 4;
        var join_width          = $join.width()  + pad;
        var join_height         = $join.height() + pad;
        
        var login_width         = $login.width()  + pad;
        var login_height        = $login.height() + pad;*/

        /*$join.css({
            'position'  : 'absolute', 
            'float'     : 'none', 
            'top'       : join_pos.top, 
            'left'      : join_pos.left, 
            'width'     : join_width, 
            'height'    : join_height
        });
        
        $login.css({
            'position'  : 'absolute', 
            'float'     : 'none', 
            'top'       : login_pos.top, 
            'left'      : login_pos.left, 
            'width'     : login_width, 
            'height'    : login_height
        });*/


        // now that we have the static positions and sizes of the dynamic header 
        // elements, initialize their new positioning /sizing to absolute and 
        // non-auto, respectively.
        /*$header.height(header_height);*/


                // layout and style the header's login / join content
                /*var cur_opacity = cur_ratio * cur_ratio;
                var already_stamping_style = {
                    opacity : cur_opacity
                };
                
                if (cur_opacity <= 0.2) {
                    already_stamping_style['visibility'] = 'hidden';
                } else {
                    already_stamping_style['visibility'] = 'visible';
                }
                
                $already_stamping.css(already_stamping_style);
                
                var cur_left = join_pos.left - inv_cur_ratio * (login_button_width + 16);
                $join.css({
                    left : cur_left
                });
                
                var cur_top  = cur_ratio * login_pos.top + inv_cur_ratio * join_pos.top;
                $login.css({
                    top : cur_top
                });*/


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
            
            init_main(true);
        }, 150);
    }
});


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

