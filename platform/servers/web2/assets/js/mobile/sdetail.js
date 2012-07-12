/*! sdetail.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global STAMPED_PRELOAD, jQuery, $, History, moment */

var g_update_stamps = null;

(function() {
    $(document).ready(function() {
        
        // ---------------------------------------------------------------------
        // initialize page globals
        // ---------------------------------------------------------------------
        
        
        var metadata_item_expanded  = 'metadata-item-expanded';
        var collapsed               = 'collapsed';
        var collapsing              = 'collapsing';
        
        var extract_data = function($target, prefix, default_value) {
            var classes = $target.get(0).className.split(/\s+/);
            var value   = default_value;
            
            for (i = 0; i < classes.length; ++i) {
                var c = classes[i];
                
                if (c.indexOf(prefix) === 0) {
                    c = c.substring(prefix.length);
                    
                    if (c.length > 1) {
                        value = c;
                        break;
                    }
                }
            }
            
            return value;
        };
        
        // use moment.js to make every stamps's timestamp human-readable and 
        // relative to now (e.g., '2 weeks ago' instead of 'May 5th, 2012')
        var update_timestamps = function($scope) {
            if (typeof($scope) === 'undefined') {
                $scope = $(document);
            }
            
            $scope.find('.timestamp_raw').each(function(i, elem) {
                var expl  = "";
                
                try {
                    var $elem = $(elem);
                    var ts    = moment.utc($elem.text(), "YYYY-MM-DD HH:mm:ss.SSSS");
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
        
        // returns the default fancybox options merged with the optional given options
        var get_fancybox_options = function(options) {
            var default_options = {
                openEffect      : 'elastic', 
                openEasing      : 'easeOutBack', 
                openSpeed       : 300, 
                
                closeEffect     : 'elastic', 
                closeEasing     : 'easeInBack', 
                closeSpeed      : 300, 
                
                tpl             : {
				    error       : '<p class="fancybox-error">Whoops! Looks like we messed something up on our end. Our bad.<br/>Please try again later.</p>', 
                    closeBtn    : '<a title="Close" class="close-button"><div class="close-button-inner"></div></a>'
                }, 
                
                helpers         : {
                    overlay     : {
                        speedIn  : 150, 
                        speedOut : 300, 
                        opacity  : 0.8, 
                        
                        css      : {
                            cursor             : 'pointer', 
                            'background-color' : '#fff'
                        }, 
                        
                        closeClick  : true
                    }
                }
            };
            
            var output = {};
            
            for (var key in default_options) {
                if (default_options.hasOwnProperty(key)) {
                    output[key] = default_options[key];
                }
            }
            
            if (!!options) {
                for (var key in options) {
                    if (options.hasOwnProperty(key)) {
                        output[key] = options[key];
                    }
                }
            }
            
            return output;
        };
        
        // returns the default fancybox popup options merged with the optional given options
        var get_fancybox_popup_options = function(options) {
            var output = get_fancybox_options({
                type        : "ajax", 
                scrolling   : 'no', // we prefer our own, custom jScrollPane scrolling
                wrapCSS     : '', 
                padding     : 0, 
                minWidth    : 366, 
                maxWidth    : 366, 
                
                beforeShow  : function() {
                    $('.popup-body').jScrollPane({
                        verticalPadding : 8
                    });
                    
                    // disable page scroll for duration of fancybox popup
                    $("html").css('overflow', 'hidden');
                }, 
                beforeClose : function() {
                    // reenaable page scroll before fancybox closes
                    $("html").css('overflow-y', 'scroll');
                }
            });
            
            if (!!options) {
                for (var key in options) {
                    if (options.hasOwnProperty(key)) {
                        output[key] = options[key];
                    }
                }
            }
            
            return output;
        };
        
        // post-processing of newly added stamps, including:
        //   1) using moment.js to make the stamp's timestamp human-readable and 
        //      relative to now (e.g., '2 weeks ago' instead of 'May 5th, 2012')
        //   2) enforce predence of rhs stamp preview images
        //   3) relayout the stamp gallery lazily whenever a new image is loaded
        var update_stamps = function($scope) {
            // convert iOS emoji unicode characters to inline images in the sdetail stamp blurb
            $scope.find('.normal_blurb').emoji();
            update_timestamps($scope);
            
            $scope.find("a.lightbox").fancybox(get_fancybox_options({
                closeClick : true
            }));
        };
        
        
        // ---------------------------------------------------------------------
        // sDetail
        // ---------------------------------------------------------------------
        
        
        // initializes sdetail after it's been loaded
        var init_sdetail = function($sdetail) {
            if (!$sdetail) {
                $sdetail        = $('.sdetail');
            }
            
            var $comments_div   = $sdetail.find('.comments');
            var $comments_nav   = $comments_div.find('.comments-nav');
            var $comments_list  = $comments_div.find('.comments-list');
            var $comments       = $comments_div.find('.comment');
            var comments_len    = $comments.length;
            
            // convert iOS emoji unicode characters to inline images in the comments
            $comments.find('.normal_blurb').emoji();
            
            // initialize comment collapsing
            if (comments_len > 2) {
                var last_visible_pos = $($comments.get(comments_len - 2)).position();
                var comments_height  = $comments_div.height();
                var comments_initted = false;
                
                $comments_nav.on("click", "a", function(event) {
                    event.preventDefault();
                    
                    $comments.show();
                    
                    var init_comment_defaults = function() {
                        if (comments_initted) {
                            return;
                        }
                        
                        if (comments_height <= 0 || $comments_div.css('max-height') === 'none') {
                            last_visible_pos = $($comments.get(comments_len - 2)).position();
                            comments_height  = $comments_div.height();
                            comments_initted = true;
                        }
                    };
                    
                    if ($comments_div.hasClass(collapsed) || $comments_div.hasClass(collapsing)) {
                        $comments_list.stop(true, false);
                        $comments_div.removeClass(collapsing + " " + collapsed);
                        
                        init_comment_defaults();
                        
                        // expand comments
                        $comments_list.css({
                            top : -last_visible_pos.top
                        }).animate({
                            top : 0
                        }, {
                            duration : 1000, 
                            specialEasing : { 
                                top : 'easeOutExpo'
                            }, 
                            step : function(now, fx) {
                                $comments_div.css('max-height', comments_height + now + "px");
                            }, 
                            complete : function() {
                                $comments_div.css('max-height', 'none');
                            }
                        });
                    } else {
                        init_comment_defaults();
                        
                        $comments_list.stop(true, false);
                        $comments_div.addClass(collapsing);
                        
                        // collapse comments
                        $comments_list.animate({
                            top : -last_visible_pos.top
                        }, {
                            duration : 1000, 
                            specialEasing : { 
                                top : 'easeOutExpo'
                            }, 
                            step : function(now, fx) {
                                $comments_div.css('max-height', comments_height + now + "px");
                            }, 
                            complete : function() {
                                $comments_div.removeClass(collapsing).addClass(collapsed);
                            }
                        });
                    }
                    
                    return false;
                });
            }
            
            // initialize menu action
            var $action_menu = $sdetail.find('.action-menu');
            
            if ($action_menu.length == 1) {
                var $temp = $action_menu.parents('.entity-id');
                var $link = $action_menu.parent('a.action-link');
                
                if ($temp.length == 1 && $link.length == 1) {
                    $link.each(function(i, link) {
                        var $link        = $(link);
                        var entity_id    = extract_data($temp, 'entity-id-', null);
                        var entity_title = $.trim($action_menu.find('.entity-title').text());
                        
                        if (entity_id !== null) {
                            if (entity_title === null) {
                                entity_title = "Menu";
                            } else {
                                entity_title = "Menu for " + entity_title;
                            }
                            
                            var link_type = 'ajax';
                            var link_href = '/entities/menu?entity_id=' + entity_id;
                            
                            // TODO: possibly embed singleplatform page directly if one exists
                            //link_type = 'iframe';
                            //link_href = 'http://www.singlepage.com/joes-stone-crab/menu?ref=Stamped';
                            
                            var popup_options = get_fancybox_popup_options({
                                href            : link_href, 
                                type            : link_type, 
                                maxWidth        : 480, //Math.min((2 * window.innerWidth) / 3, 480), 
                                
                                afterShow       : function() {
                                    $('.menus').jScrollPane({
                                        verticalPadding : 8
                                    });
                                }
                            });
                            
                            $link.attr('href', link_href).click(function(event) {
                                event.preventDefault();
                                
                                $.fancybox.open(popup_options);
                                return false;
                            }).fancybox(popup_options);
                        }
                    });
                }
            }
            
            // initialize expanding / collapsing links for long, overflowed metadata items
            $sdetail.find('a.nav').each(function(i, elem) {
                var $elem  = $(elem);
                var $item  = $elem.parents('.metadata-item');
                var $value = $item.find('p.resizable');
                
                if ($value.length === 1) {
                    $item.removeClass(metadata_item_expanded);
                    var h0 = $value.height();
                    
                    $item.addClass(metadata_item_expanded);
                    var h1 = $value.height();
                    
                    if (h1 <= h0) {
                        // no expansion necessary
                        $elem.hide();
                    } else {
                        $item.removeClass(metadata_item_expanded);
                        
                        $elem.click(function(event) {
                            event.preventDefault();
                            
                            $item.toggleClass(metadata_item_expanded);
                            return false;
                        });
                    }
                }
            });
            
            // sanitize sizing of user-generated image embedded in stamp card
            $sdetail.find(".stamp-card .entity-image-wrapper").each(function(i, elem) {
                var $elem = $(elem);
                var $img  = $elem.find('img');
                
                if (!!$elem && !!$img) {
                    var width  = $img.width();
                    var height = $img.height();
                    
                    if (width > 0 && height > 0) {
                        $elem.css({
                            'width'         : width, 
                            'height'        : height, 
                            
                            'max-width'     : width, 
                            'max-height'    : height
                        });
                    }
                }
            });
            
            $sdetail.find(".expand-popup").click(function(event) {
                event.preventDefault();
                
                var $this = $(this);
                var href  = $this.attr('href');
                
                var popup_options = get_fancybox_popup_options({
                    href  : href
                });
                
                $.fancybox.open(popup_options);
                return false;
            });
            
            update_stamps($sdetail);
        };
        
        $("#stamped-desc").click(function(event) {
            event.preventDefault();
            var $this = $(this);
            
            $this.toggleClass("badass");
            return false;
        });
        
        
        // ---------------------------------------------------------------------
        // base page initialization
        // ---------------------------------------------------------------------
        
        
        init_sdetail();
    });
})();

