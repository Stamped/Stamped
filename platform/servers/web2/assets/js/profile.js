/* profile.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

/*jslint plusplus: true */
/*global STAMPED_PRELOAD, StampedClient, jQuery, $, History, moment */

var g_update_stamps = null;

/* TODO:
    * gallery infinite scroll doesn't reset properly
 */

(function() {
    $(document).ready(function() {
        
        // ---------------------------------------------------------------------
        // initialize StampedClient
        // ---------------------------------------------------------------------
        
        
        var client                  = new StampedClient();
        var screen_name             = STAMPED_PRELOAD.user.screen_name;
        var user_id                 = STAMPED_PRELOAD.user.user_id;
        var $body                   = $('body');
        var selected                = 'selected';
        var selected_sel            = '.' + selected;
        var sdetail_popup           = 'sdetail_popup';
        var sdetail_wrapper         = 'sdetail_wrapper';
        var sdetail_wrapper_sel     = '.' + sdetail_wrapper;
        var collapsed_header        = 'collapsed-header';
        var metadata_item_expanded  = 'metadata-item-expanded';
        var collapsed               = 'collapsed';
        var collapsing              = 'collapsing';
        var STAMP_GALLERY_PAGE_SIZE = 10;
        
        var static_prefix           = 'http://maps.gstatic.com/mapfiles/place_api/icons';
        var update_navbar_layout    = null;
        var close_sdetail_func      = null;
        
        var is_blacklisted_image    = function(url) {
            return (url.indexOf(static_prefix) != -1);
        };
        
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
        window.g_extract_data = extract_data;
        
        
        // ---------------------------------------------------------------------
        // initialize profile header navigation
        // ---------------------------------------------------------------------
        
        
        $('.profile-nav a').each(function () {
            $(this).click(function(event) {
                event.preventDefault();
                var $link = $(this);
                
                $link.parents(".profile-sections").each(function() {
                    var elems = $(this).find(".profile-section");
                    
                    $(elems).slideToggle('fast', function() { });
                });
                
                return false;
            });
        });
        
        $(".stamp-gallery-nav a").each(function() {
            var href = $(this).attr('href');
            var limit_re = /([?&])limit=[\d]+/;
            var limit = "limit=" + STAMP_GALLERY_PAGE_SIZE;
            
            if (href.match(limit_re)) {
                href = href.replace(limit_re, "$1" + limit);
            } else if (href.indexof('?') !== -1) {
                href = href + "&" + limit;
            } else {
                href = href + "?" + limit;
            }
            
            $(this).attr('href', href);
        });
        
        window.g_init_social_sharing = function() {
            // initialize animated social sharing widgets
            $(".share-widget").each(function(i, elem) {
                var $elem   = $(elem);
                var $share  = $elem.find('.share-buttons');
                
                $elem.css({
                    'display' : 'inline-block', 
                    'width'   : 'auto', 
                    'height'  : 'auto'
                });
                
                var width0  = $elem.width();
                var height0 = $elem.height();
                
                $elem.css('display', 'block');
                $share.show();
                
                var width1  = $elem.width();
                var height1 = $elem.height();
                
                $share.hide();
                
                $elem.css({
                    width  : width0, 
                    height : height0
                });
                
                $elem.hover(function(event) {
                    $elem.stop(true, false);
                    
                    $share.show();
                    $elem.animate({
                        width  : width1, 
                        height : height1
                    }, {
                        duration : 500, 
                        specialEasing : { 
                            width  : 'easeOutCubic', 
                            height : 'easeOutCubic'
                        }
                    });
                }, function(event) {
                    $elem.stop(true, false);
                    
                    $share.hide();
                    $elem.animate({
                        width  : width0, 
                        height : height0
                    }, {
                        duration : 500, 
                        specialEasing : { 
                            width  : 'easeOutCubic', 
                            height : 'easeOutCubic'
                        }
                    });
                });
            });
        };
        
        $(".subnav_button").click(function(event) {
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
                var $this = $(this);
                var percentage = 0;
                var opacity = 1.0;
                
                if (bargraph) {
                    var count  = $this.data('count') || 0;
                    
                    if (count > 0) {
                        percentage = 100.0 * Math.min(1.0, (.5 - (1.0 / Math.pow(count + 6, .4))) * 80.0 / 33.0);
                    } else {
                        percentage = 0.0;
                        opacity    = 0.0;
                    }
                }
                
                $this.stop(true, false).animate({
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
            
            setTimeout(function() {
            }, 200);
            
            return false;
        });
        
        var $header_subsections = $('.header-subsection');
        var header_subsection_height = 0;
        var $header_subsection_0 = null;
        
        $header_subsections.each(function(i, elem) {
            var $elem = $(elem);
            if ($elem.hasClass('header-subsection-0')) {
                $header_subsection_0 = $elem;
            }
            
            header_subsection_height = Math.max($elem.height(), header_subsection_height);
        });
        
        if (!!$header_subsection_0) {
            $header_subsection_0.css({
                'height'     : header_subsection_height, 
                'min-height' : header_subsection_height
            });
        }
        
        // TODO: may not be recursive
        //$(document).emoji();
        //$container.emoji();
        
        
        // ---------------------------------------------------------------------
        // initialize stamp-gallery, isotope layout, and infinite scroll
        // ---------------------------------------------------------------------
        
        var $gallery = null;
        var infinite_scroll = null;
        
        var destroy_infinite_scroll = function() {
            if (!!infinite_scroll) {
                if (!!$gallery) {
                    $gallery.infinitescroll('destroy');
                    $gallery.data('infinitescroll', null);
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
        var update_timestamps = function($scope) {
            if (typeof($scope) === 'undefined') {
                $scope = $(document);
            }
            
            $scope.find('.timestamp_raw').each(function(i, elem) {
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
        var gallery_is_visible = false;
        
        // lazily relayout the stamp gallery using isotope
        // NOTE: we apply time-based coalescing here s.t. if this function is 
        // called several times, it will attempt to only update the layout once
        // to avoid doing extra, unnecessary work / rendering that could result 
        // in a choppier end-user experience.
        var update_gallery_layout = function(is_visible, callback) {
            is_visible = (typeof(is_visible) === 'undefined' ? false : is_visible);
            gallery_is_visible |= is_visible;
            
            var set_gallery_visible = function() {
                var style = {
                    visibility : 'visible'
                };
                
                $('#main-content').css(style);
                $('#stamp-category-nav-bar').css(style);
            };
            
            update_gallery(function() {
                update_navbar_layout(false);
                last_layout = new Date().getTime();
                
                if (gallery_is_visible) {
                    set_gallery_visible();
                }
                
                if (_.isFunction(callback)) {
                    callback();
                }
            });
            
            if (gallery_is_visible && !!last_layout) {
                set_gallery_visible();
            }
            
            return;
        };
        
        var get_fancybox_options = function(options) {
            var default_options = {
                openEffect      : 'elastic', 
                openEasing      : 'easeOutBack', 
                openSpeed       : 300, 
                
                closeEffect     : 'elastic', 
                closeEasing     : 'easeInBack', 
                closeSpeed      : 300, 
                
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
            
            return options;
        };
        
        var find_valid_image = function($elem, selector, is_sdetail) {
            var $elements = $elem.find(selector);
            $elements     = $elements.filter(function() {
                var $this = $(this);
                
                if (is_blacklisted_image($this.attr('src'))) {
                    $this.addClass('hidden').parent().addClass('hidden');
                    return false;
                } else {
                    return !$this.hasClass('hidden');
                }
            });
            
            $elements.each(function(i, element) {
                element.onerror = function() {
                    var $element = $(element);
                    $element.addClass('hidden').parent().addClass('hidden');
                    
                    // TODO: what to update here?
                    //update_images();
                    init_stamp_preview_images($elem, is_sdetail);
                };
            });
            
            return $elements;
        };
        
        // enforce precedence of stamp preview images
        var init_stamp_preview_images = function($elem, is_sdetail) {
            var images = [];
            
            var $stamp_user_images   = find_valid_image($elem, '.stamp-user-image   img', is_sdetail);
            var $stamp_entity_images = find_valid_image($elem, '.stamp-entity-image img', is_sdetail);
            
            var $map  = $elem.find('.stamp-map');
            var $icon = $elem.find('.stamp-icon');
            
            if (is_sdetail) {
                images.push.apply(images, $map);
                images.push.apply(images, $stamp_entity_images);
                images.push.apply(images, $icon);
                
                // note: user image is included in stamp-card
                images.push.apply(images, $stamp_user_images);
            } else {
                images.push.apply(images, $stamp_user_images);
                images.push.apply(images, $stamp_entity_images);
                images.push.apply(images, $map);
                images.push.apply(images, $icon);
            }
            
            if (images.length > 0) {
                var preview  = images[0];
                var $preview = $(preview);
                var i;
                
                if ($preview.is("img")) {
                    // ensure gallery's layout is updated whenever this 
                    preview.onload = function() {
                        update_gallery_layout();
                        //setTimeout(update_gallery_layout, 100);
                    };
                }
                
                $preview.removeClass('hidden').parent().removeClass('hidden');
                $preview.show();
                
                for (i = 1; i < images.length; i++) {
                    var $image = $(images[i]);
                    
                    $image.hide().addClass('hidden').parent().addClass('hidden');
                }
                
                if (is_sdetail) {
                    if (!$preview.hasClass('preview-image')) {
                        $preview = $preview.parents('.preview-image');
                    }
                    
                    // TODO: modify static-map-small for sDetail to not be crinkled
                    // TODO: experiment w/ initial scale at .25 scale and tween to this transform
                    var width = "200px";
                    var t = "perspective(600) scaleX(1.15) scaleY(1.15) rotateZ(25deg) rotateX(25deg) rotateY(-25deg)";
                    $preview.css({
                        'width'     : width, 
                        'max-width' : width, 
                        '-webkit-transform' : t, 
                        '-moz-transform'    : t, 
                        '-ms-transform'     : t, 
                        '-o-transform'      : t, 
                        'transform'         : t
                    }).hover(function() {
                        var t2 = "perspective(600)";
                        
                        // TODO: remove duplication of CSS here
                        $preview.css({
                            '-webkit-transform' : t2, 
                            '-moz-transform'    : t2, 
                            '-ms-transform'     : t2, 
                            '-o-transform'      : t2, 
                            'transform'         : t2
                        });
                    }, function() {
                        $preview.css({
                            '-webkit-transform' : t, 
                            '-moz-transform'    : t, 
                            '-ms-transform'     : t, 
                            '-o-transform'      : t, 
                            'transform'         : t
                        });
                    });
                }
            }
            
            update_gallery_layout();
        };
        
        // post-processing of newly added stamps, including:
        //   1) using moment.js to make the stamp's timestamp human-readable and 
        //      relative to now (e.g., '2 weeks ago' instead of 'May 5th, 2012')
        //   2) enforce predence of rhs stamp preview images
        //   3) relayout the stamp gallery lazily whenever a new image is loaded
        var update_stamps = function($scope) {
            var $items = $scope;
            
            /*if (!!$items) {
                console.debug("update_stamps: " + $items.length);
            }*/
            
            if (typeof($scope) === 'undefined') {
                $scope = $(document);
                $items = $scope.find('.stamp-gallery-item');
            } else if ($scope.hasClass(sdetail_wrapper)) {
                $items = null;
            }
            
            update_timestamps($scope);
            
            $scope.find('.stamp-preview-raw').each(function(i, elem) {
                var $this       = $(this);
                var is_sdetail  = ($this.parents('.sdetail_body').length >= 1);
                
                $this.removeClass('stamp-preview-raw').addClass('stamp-preview');
                
                //var category    = extract_data($this, 'stamp-category-', 'other');
                //console.debug("CATEGORY: " + category + "; is_sdetail: " + is_sdetail);
                
                // enforce precedence of stamp preview images
                init_stamp_preview_images($this, is_sdetail);
                //update_images();
            });
            
            if (!!$items) {
                $items.click(function(event) {
                    var $target = $(event.target);
                    if ($target.is('a') && $target.hasClass('lightbox')) {
                        // override the sdetail popup if a lightbox target was clicked
                        return true;
                    }
                    
                    event.preventDefault();
                    
                    var $this = $(this);
                    var $link = ($this.is('a') ? $this : $this.find('a.sdetail'));
                    var href  = $link.attr('href');
                    
                    href = href.replace('http://www.stamped.com', '');
                    href = href + "?ajax=true";
                    //href = href + "&" + new Date().getTime();
                    
                    $(sdetail_wrapper_sel).remove();
                    var $target = $("<div class='" + sdetail_wrapper + " sdetail-loading'><div class='sdetail-loading-content'></div></div>");
                    
                    console.debug("AJAX: " + href);
                    
                    // TODO: disable infinite scroll for sdetail popup
                    destroy_infinite_scroll();
                    
                    $(sdetail_wrapper_sel).hide().remove();
                    $target.insertAfter($('#main-page-content-body').get(0));
                    $target = $(sdetail_wrapper_sel);
                    
                    update_dynamic_header();
                    
                    var scroll_top = $window.scrollTop();
                    
                    resize_sdetail_wrapper($target, 'opening', function() {
                        $target.removeClass('animating');
                    });
                    
                    close_sdetail_func = function() {
                        close_sdetail_func = null;
                        $body.addClass('sdetail_popup_animation').removeClass('sdetail_popup');
                        
                        var close_sdetail_inner_func = function() {
                            init_infinite_scroll();
                            update_dynamic_header();
                            update_navbar_layout();
                            
                            // reset window's vertical scroll position to where it was 
                            // before the sDetail popup
                            $window.scrollTop(scroll_top);
                            
                            resize_sdetail_wrapper($target, 'closing', function() {
                                $(sdetail_wrapper_sel).removeClass('animating').hide().remove();
                            });
                        };
                        
                        /*if (!!$gallery) {
                            update_gallery_layout(true, function() {
                                //$window.scrollTop(scroll_top);
                                //init_infinite_scroll();
                                
                                close_sdetail_inner_func();
                            });
                        } else {
                        }*/
                        
                        if (!!$gallery) {
                            update_gallery_layout(true);
                        }
                        
                        close_sdetail_inner_func();
                    };
                    
                    // initialize sDetail popup after AJAX load
                    $target.load(href, {}, function(response, status, xhr) {
                        if (status == "error") {
                            console.debug("AJAX ERROR (sdetail): " + url);
                            console.debug(response);
                            console.debug(xhr);
                            
                            //alert("TODO: handle AJAX and backend errors gracefuly");
                            return;
                        }
                        
                        $target.removeClass('sdetail-loading');
                        init_sdetail($target);
                        
                        // initialize sDetail close button logic
                        $target.find('.close-button a').click(function(event) {
                            event.preventDefault();
                            
                            if (!!close_sdetail_func) {
                                close_sdetail_func();
                            }
                            
                            return false;
                        });
                    });
                    
                    return false;
                });
            }
            
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
            
            $scope.find("a.lightbox").fancybox(get_fancybox_options({
                closeClick : true
            }));
            
            /*$('.stamp-gallery-item .pronounced-title').each(function(i, elem) {
                var $this = $(this);
                $this.fitText();
            });*/
        };
        
        // handle sizing / layout of sdetail popup, including opening / closing animations
        var resize_sdetail_wrapper = function($sdetail_wrapper, sdetail_status, anim_callback) {
            sdetail_status = (typeof(sdetail_status) !== 'undefined' ? sdetail_status : null);
            var anim_duration = 600;
            
            if (!$sdetail_wrapper) {
                $sdetail_wrapper = $(sdetail_wrapper_sel);
            }
            
            if ($sdetail_wrapper.length === 1) {
                var offset = cur_header_height + 16;
                var hidden = window.innerHeight + "px";
                
                if (!!$body && $body.hasClass('map')) {
                    offset += 0;
                }
                
                offset += "px";
                
                //var offset = $window.scrollTop()  + "px";
                //var hidden = ($window.scrollTop() + window.innerHeight - (cur_header_height + 16));
                
                if (sdetail_status === 'opening') {
                    $body.addClass('sdetail_popup_animation').removeClass('sdetail_popup');
                    
                    $sdetail_wrapper
                        .stop(true, false)
                        .css({
                            'top' : hidden, 
                        })
                        .addClass('animating')
                        .animate({
                            top : offset, 
                        }, {
                            duration : anim_duration, 
                            specialEasing : { 
                                top : 'easeInOutCubic'
                            }, 
                            complete : function() {
                                /*$sdetail_wrapper.css({
                                    'top' : 0, 
                                });*/
                                
                                $body.addClass('sdetail_popup').removeClass('sdetail_popup_animation');
                                
                                if (_.isFunction(anim_callback)) {
                                    anim_callback();
                                }
                            }
                        });
                } else if (sdetail_status == 'closing') {
                    //$body.removeClass('sdetail_popup_animation sdetail_popup');
                    
                    $sdetail_wrapper
                        .stop(true, false)
                        .addClass('animating')
                        .animate({
                            top : hidden, 
                        }, {
                            duration : anim_duration, 
                            specialEasing : { 
                                top : 'easeInOutCubic'
                            }, 
                            complete : function() {
                                $body.removeClass('sdetail_popup_animation');
                                
                                if (_.isFunction(anim_callback)) {
                                    anim_callback();
                                }
                            }
                        });
                } else if (!$sdetail_wrapper.hasClass('animating')) {
                    $sdetail_wrapper.css({
                        'top' : offset, 
                    });
                }
                
                // constrain entity header's width to fit onto a single line
                var $stamp_card_header  = $sdetail_wrapper.find('.stamp-card-header');
                var $entity_header      = $stamp_card_header.find('.entity-header');
                var width               = $stamp_card_header.width() - (96 + 48);
                
                $entity_header.css({
                    'width'     : width, 
                    'max-width' : width
                });
            }
        };
        
        g_update_stamps = update_stamps;
        var infinite_scroll_next_selector = "div.stamp-gallery-nav a:last";
        
        var init_infinite_scroll = function() {
            if (!!$gallery && !infinite_scroll) {
                var $next = $(infinite_scroll_next_selector);
                var init  = false;
                
                //console.debug("NEXT: " + .length);
                //console.debug("NAV:  " + $("div.stamp-gallery-nav").length);
                //console.debug("ITEM: " + $("div.stamp-gallery div.stamp-gallery-item").length);
                
                // only initialize infinite scroll if the page's content calls for it
                if ($next.length === 1) {
                    var href = $next.attr('href');
                    
                    if (!!href && href.length > 1) {
                        init = true;
                    }
                }
                
                if (init) {
                    // TODO: customize loading image
                    infinite_scroll = $gallery.infinitescroll({
                        bufferPx        : window.innerHeight * .8, 
                        debug           : true, 
                        
                        navSelector     : "div.stamp-gallery-nav", 
                        nextSelector    : infinite_scroll_next_selector, 
                        itemSelector    : "div.stamp-gallery div.stamp-gallery-item", 
                        
                        pathParse       : function(path, page) {
                            var offset_re = /([?&])offset=([\d]+)/;
                            var match = path.match(offset_re);
                            
                            if (!!match) {
                                offset = parseInt(match[2]);
                                
                                // TODO: this is a hack..
                                return {
                                    'join' : function(page) {
                                        var cur_offset = offset + (page - 2) * STAMP_GALLERY_PAGE_SIZE;
                                        cur_offset = "offset=" + cur_offset;
                                        
                                        return path.replace(offset_re, "$1" + cur_offset);
                                    }
                                };
                            } else {
                                return [ path ];
                            }
                        }, 
                        
                        dataType        : 'html', 
                        
                        loading         : {
                            finishedMsg : "No more stamps to load.", 
                            msgText     : "<em>Loading more stamps...</em>", 
                            img         : "/assets/img/loading.gif", 
                            selector    : "div.stamp-gallery-loading"
                        }, 
                        
                        state           : {
                            isDuringAjax: false,
                            isInvalidPage: false,
                            isDestroyed : false,
                            isDone      : false
                        }
                    }, function(new_elements) {
                        var $elements = $(new_elements);
                        
                        //$elements.emoji();
                        $gallery.isotope('appended', $elements);
                        update_stamps();
                    });
                    
                    $gallery.infinitescroll('bind');
                }
            }
        };
        
        // initialize the stamp gallery's layout with isotope and infinite scroll
        var init_gallery = function() {
            $gallery = $(".stamp-gallery .stamps");
            
            if ($gallery.length <= 0) {
                $gallery = null;
            } else {
                $gallery.isotope({
                    itemSelector        : '.stamp-gallery-item', 
                    layoutMode          : "masonry"/*, 
                    animationOptions    : {
                        duration        : 800,
                        easing          : 'easeOut',
                        queue           : true
                    }*/
                });
                
                init_infinite_scroll();
            }
        };
        
        
        // ---------------------------------------------------------------------
        // stamp gallery controls (currently sorting and map view)
        // ---------------------------------------------------------------------
        
        
        $('.stamp-gallery-sort a.item').click(function(event) {
            event.preventDefault();
            var $this   = $(this);
            var $parent = $this.parent('.stamp-gallery-sort');
            
            if ($parent.hasClass('expanded')) {
                $parent.removeClass('expanded').find(selected_sel).removeClass(selected);
                $this.addClass('selected');
                
                var sort = undefined;
                
                if ($this.hasClass('sort-modified')) {
                    sort = 'modified';
                } else if ($this.hasClass('sort-popularity')) {
                    sort = 'popularity';
                }
                
                if (typeof(sort) !== 'undefined') {
                    var params = get_custom_params({
                        sort : sort
                    });
                    
                    console.debug("SORT: " + sort);
                    
                    if (History && History.enabled) {
                        var params_str = get_custom_params_string(params);
                        
                        History.pushState(params, document.title, params_str);
                    } else {
                        alert("TODO: support navigation when browser history is disabled");
                    }
                }
            } else {
                $parent.addClass('expanded');
            }
            
            return false;
        });
        
        $('.stamp-gallery-view-map a').click(function(event) {
            event.preventDefault();
            
            var url   = get_custom_url({}, "/" + screen_name + "/map");
            var title = "Stamped - " + screen_name + " - map";
            
            window.location = url;
            return false;
        });
        
        /*
        $('a.map-profile-link').hover(function() {
            var $this   = $(this);
            var $inner  = $this.find('.inner');
            var $shadow = $this.find('.inner-shadow');
            
            $inner.stop(true, false);
            $shadow.stop(true, false);
            
            var animate = function() {
                $inner.animate({
                    top : -18px
                }, {
                    duration : 200, 
                    specialEasing : { 
                        width  : 'ease-out', 
                        height : 'ease-out'
                    }, 
                    complete : function() {
                        animate();
                    }
                });
            };
        }, function() {
            var $this = $(this);
            
        });*/
        
        
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
        var user_logo_top       = parseFloat($user_logo.css('top'));
        var user_logo_left      = parseFloat($user_logo.css('left'));
        var user_logo_width     = parseFloat($user_logo.css('width'));
        var user_logo_height    = parseFloat($user_logo.css('height'));
        
        var $window             = $(window);
        var $header             = $('header .header-body');
        var $content            = $('#main-page-content');
        var header_height       = $header.height();
        var cur_header_height   = header_height || 0;
        var min_height_ratio    = 0.5;
        var min_header_height   = header_height * min_height_ratio;
        
        var $join               = $('.join');
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
        var login_height        = $login.height() + pad;
        
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
        
        $login.css({
            position : 'absolute', 
            float    : 'none', 
            top      : login_pos.top, 
            left     : login_pos.left, 
            width    : login_width, 
            height   : login_height
        });
        
        var last_ratio = null;
        
        var update_dynamic_header = function() {
            // note: if sdetail's up, we round the dynamic header's size ratio to the 
            // nearest value s.t. it's either at maximum size or minimum size
            var cur_ratio = 0.0;
            
            if (last_ratio !== null) {
                cur_ratio = Math.round(last_ratio);
            }
            
            if (!($body.hasClass(sdetail_popup) || 
                $body.hasClass('sdetail_popup_animation') || 
                $body.hasClass(collapsed_header)))
            {
                // if we're not in sdetail, set the dynamic header's size ratio to be 
                // proportional to the window's current vertical scroll offset
                cur_ratio = (header_height - $window.scrollTop()) / header_height;
                cur_ratio = Math.min(Math.max(cur_ratio, 0.0), 1.0);
            }
            
            // only update the dynamic header's properties if the dynamic header's 
            // size ratio has changed since the last time we updated the header
            if (cur_ratio !== last_ratio) {
                last_ratio = cur_ratio;
                var inv_cur_ratio = 1.0 - cur_ratio;
                
                var cur_height_ratio = Math.max(cur_ratio, min_height_ratio);
                var cur_height = header_height * cur_height_ratio;
                
                if (cur_height !== cur_header_height) {
                    cur_header_height = cur_height;
                    $header.height(cur_header_height);
                }
                
                // ensure main body content's vertical offset respects the dynamic 
                // header's height
                $content.css({
                    top : cur_header_height + 16
                });
                
                // layout and style the header's login / join content
                var cur_opacity = cur_ratio * cur_ratio;
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
                });
                
                // resize user's stamp logo
                var cur_logo_width  = user_logo_width  - inv_cur_ratio * (user_logo_width - 166);
                var cur_logo_height = user_logo_height - inv_cur_ratio * (user_logo_width - 166);
                var cur_logo_size   = cur_logo_width + 'px ' + cur_logo_height + 'px';
                //var cur_logo_top    = user_logo_top  + (user_logo_width  - cur_logo_height) / 2.0;
                //var cur_logo_left   = user_logo_left + (user_logo_height - cur_logo_width)  / 2.0;
                
                $user_logo.css({
                    width               : cur_logo_width, 
                    height              : cur_logo_height, 
                    'background-size'   : cur_logo_size, 
                    '-webkit-mask-size' : cur_logo_size, 
                    //top                 : cur_logo_top, 
                    //left                : cur_logo_left
                });
                
                //console.debug("DYNAMIC HEADER: ratio=" + cur_ratio);
            }
        };
        
        
        // ---------------------------------------------------------------------
        // initialize stamp category nav bar
        // ---------------------------------------------------------------------
        
        
        var $nav_bar   = $('#stamp-category-nav-bar');
        var categories = 'default place music book film app';
        
        var set_body_class = function(category) {
            $body.removeClass(categories).addClass(category);
        };
        
        var g_category = null;
        
        // TODO: if history is disabled but JS is enabled, user will be unable 
        // to navigate categories
        
        if (History && History.enabled) {
            History.Adapter.bind(window, 'statechange', function() {
                var State    = History.getState();
                var category = 'default';
                var custom_params = {
                    'ajax' : true
                };
                
                for (var key in State.data) {
                    if (State.data.hasOwnProperty(key)) {
                        custom_params[key] = State.data[key];
                    }
                }
                
                if (typeof(custom_params['category']) !== 'undefined') {
                    category = custom_params['category'];
                }
                
                console.debug("NEW CATEGORY: " + category);
                console.debug("user_id: " + user_id);
                
                History.log(State.data, State.title, State.url);
                var orig_category = category;
                
                if (category === 'default') {
                    category = null;
                    custom_params['category'] = null;
                }
                
                var params    = get_custom_params(custom_params);
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
                
                // animated transition between category-specific headers
                if (category !== g_category) {
                    var sel = '.header-category-' + orig_category;
                    var $elem = $(sel);
                    
                    if ($elem.length == 1 && !$elem.hasClass('header-selected')) {
                        var completion_func = function() {
                            $('.header-selected').removeClass('header-animating header-selected');
                            $elem.removeClass('header-animating').addClass('header-selected');
                            
                            g_category = category;
                            set_body_class(orig_category);
                            window.g_init_social_sharing();
                        };
                        
                        if (category === null) {
                            completion_func();
                        } else {
                            $elem.addClass('header-animating').stop(true, false).css({
                                top : "-100%", 
                            }).animate({
                                top : 0, 
                            }, {
                                duration : 600, 
                                specialEasing : { 
                                    top : 'easeOutCubic'
                                }, 
                                complete : completion_func
                            });
                        }
                    }
                }
                
                $('body,html').stop(true, false).animate({
                    scrollTop: 0
                }, {
                    duration : 200, 
                    specialEasing : { 
                        scrollTop : 'easeInOutCubic'
                    }
                });
                
                var $target = $("<div></div>");
                $target.load(url + " .stamp-gallery", params, function(response, status, xhr) {
                    if (status == "error") {
                        console.debug("AJAX ERROR (stamps category=" + category + "): " + url);
                        console.debug(response);
                        console.debug(xhr);
                        
                        //alert("TODO: handle AJAX and backend errors gracefuly");
                        return;
                    }
                    
                    // TODO: optimize!!
                    var $elements = $target.find('.stamp-gallery-item').remove();
                    
                    //$('.stamp-gallery-nav').show();
                    //$('.inset-stamp .number').html(stamps.length);
                    var s = ".stamp-gallery-nav a";
                    var href = $($target.find(s).get(0)).attr('href');
                    if (typeof(href) === 'undefined') {
                        href = "#";
                    }
                    //log("NEW HREF: " + href);
                    //console.debug("NEW HREF: " + href);
                    
                    var $next = $(infinite_scroll_next_selector);
                    if ($next.length === 1) {
                        $next.attr('href', href);
                    } else {
                        // no previous next selector, so add one
                        $(".stamp-gallery-nav ul").append("<li><a href='" + href + "'>Next</a></li>");
                    }
                    
                    destroy_infinite_scroll();
                    
                    $gallery.append($elements);
                    update_stamps();
                    
                    $gallery.isotope('remove',   $items,    function() {
                        $('.loading').hide();
                    });
                    
                    $gallery.isotope('appended', $elements, function() {
                        init_infinite_scroll();
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
        $nav_bar.find('a.active').click(function(event) {
            event.preventDefault();
            
            var $link    = $(this);
            var orig_category = $link.parent().attr('class');
            var category = orig_category;
            
            if (category === 'default') {
                category = null;
            }
            
            var params   = { category : category };
            
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
                    } else if (category === 'app') {
                        text = 'apps';
                    }
                    
                    title += " - " + text;
                }
                
                if (!params['category']) {
                    delete params['category'];
                }
                
                History.pushState(params, title, params_str);
            } else {
                var next_url = get_custom_url(params);
                
                //alert("TODO: support navigation when browser history is disabled: " + next_url);
                window.location = next_url;
            }
            
            return false;
        });
        
        var fixed_width     = 1000;
        var fixed_padding   = 80;
        var min_col_width   = 305;
        var last_nav_pos_x  = null;
        
        // control stamp category navbar's location
        update_navbar_layout = function(should_update_gallery) {
            if (!$nav_bar || $nav_bar.length !== 1) {
                return;
            }
            
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
            var max_blurb_width = 125;
            var min_blurb_width = (gallery_width - (24 + 58 + 48 + 148));
            
            var width           = window.innerWidth;
            var left            = gallery_x + gallery_width + fixed_padding;
            var right           = (width - (gallery_x + fixed_width + nav_bar_width + 1.5 * fixed_padding));
            var pos             = left;
            
            var force_no_update = false;
            var update          = false;
            var gallery         = false;
            
            var reset_stamp_gallery_items = function(desired_width) {
                $stamp_gallery.find('.content').each(function(i, elem) {
                    var $elem = $(elem);
                    var desired_width_px = desired_width + "px";
                    var desired_width_header_px;
                    
                    if (gallery) {
                        desired_width_header_px = Math.max(min_col_width - (148 + 48 + 32), 200) + "px";
                        desired_width_px = "auto";
                    } else {
                        //desired_width_header_px = (desired_width + 148) + "px";
                        desired_width_header_px = Math.max(desired_width - 48, 200) + "px";
                    }
                    
                    $elem.find('.content_1').css({
                        'width'     : desired_width_px, 
                        'max-width' : desired_width_px
                    });
                    
                    $elem.find('.entity-header').css({
                        'width'     : desired_width_header_px, 
                        'max-width' : desired_width_header_px
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
                //console.debug("STAMP LIST VIEW: width=" + width + ", pos=" + pos);
                
                if ($stamp_gallery.hasClass(wide_gallery) || $stamp_gallery.hasClass(narrow_gallery)) {
                    $stamp_gallery.removeClass(wide_gallery + " " + narrow_gallery);
                    update = true;
                }
                
                reset_stamp_gallery_items(min_blurb_width);
            } else {
                //console.debug("STAMP GALLERY VIEW: width=" + width + ", pos=" + pos);
                gallery = true;
                
                if (!$stamp_gallery.hasClass(wide_gallery)) {
                    $stamp_gallery.removeClass(narrow_gallery).addClass(wide_gallery);
                    update = true;
                    
                    reset_stamp_gallery_items(max_blurb_width);
                }
            }
            
            if (!force_no_update) {
                if (update || last_nav_pos_x !== pos) {
                    if (!gallery) {
                        var min_fixed_width = min_col_width + nav_bar_width + fixed_padding / 2;
                        var new_fixed_width = Math.max((width - (fixed_padding + nav_bar_width)), min_fixed_width)
                        
                        $('.fixedwidth').width(new_fixed_width);
                        update = true;
                    } else {
                        //var cur_fixed_width_px = Math.Max(1000, 1 * width) + "px";
                        var cur_fixed_width_px = fixed_width + "px";
                        
                        $('.fixedwidth').width(cur_fixed_width_px);
                    }
                }
                
                if (should_update_gallery) {
                    update_gallery_layout(update);
                }
            }
            
            var clamped = 'stamp-category-nav-bar-clamped';
            
            if (window.innerHeight / 2 - 198 <= 250) {
                if (!$nav_bar.hasClass(clamped)) {
                    $nav_bar.addClass(clamped);
                }
            } else if ($nav_bar.hasClass(clamped)) {
                $nav_bar.removeClass(clamped);
            }
            
            if (last_nav_pos_x !== pos) {
                var style = {
                    left : pos + "px"
                };
                
                if (last_nav_pos_x === null) {
                    style['right'] = 'auto';
                }
                
                last_nav_pos_x = pos;
                $nav_bar.css(style);
            }
        };
        
        
        // ---------------------------------------------------------------------
        // sDetail
        // ---------------------------------------------------------------------
        
        
        var init_sdetail = function($sdetail) {
            if (!$sdetail) {
                $sdetail        = $('.sdetail_body');
            }
            
            var $comments_div   = $sdetail.find('.comments');
            var $comments_nav   = $comments_div.find('.comments-nav');
            var $comments_list  = $comments_div.find('.comments-list');
            var $comments       = $comments_div.find('.comment');
            var comments_len    = $comments.length;
            
            // initialize comment collapsing
            if (comments_len > 2) {
                var last_visible_pos = $($comments.get(comments_len - 2)).position();
                var comments_height  = $comments_div.height();
                var comments_initted = false;
                
                $comments_nav.find('a').click(function(event) {
                    event.preventDefault();
                    
                    $comments.show();
                    /*$comments.each(function (i, comment) {
                        console.debug("COMMENT " + i + ") " + $(comment).position().top);
                    });*/
                    
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
                                resize_sdetail_wrapper();
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
                                resize_sdetail_wrapper();
                            }
                        });
                    }
                    
                    //$comments_div.toggleClass(collapsed);
                    return false;
                });
                
                $comments.each(function (i, comment) {
                    //console.debug("COMMENT " + i + ") " + $(comment).position().top);
                    /*var $comment = $(comment);
                    
                    if (i < comments_len - 2) {
                        var comment_pos = $comment.position();
                        
                        // TODO: z-indexing
                        $comment.css({
                            position : 'absolute', 
                            top      : 0, //-comment_pos.top, 
                            left     : comment_pos.left, 
                            border   : '1px solid red'
                            //, opacity : 0
                        });
                    }*/
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
                            
                            // TODO: possibly embed singleplatform page directly if one exists!
                            //link_type = 'iframe';
                            //link_href = 'http://www.singlepage.com/joes-stone-crab/menu?ref=Stamped';
                            
                            var popup_options = get_fancybox_options({
                                href            : link_href, 
                                type            : link_type, 
                                title           : entity_title, 
                                maxWidth        : 480, //Math.min((2 * window.innerWidth) / 3, 480), 
                                
                                afterShow       : function() {
                                    $('.entity-menu').jScrollPane();
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
            
            // initialize reserve action
            var $action_reserve = $sdetail.find('.action-reserve');
            
            if ($action_reserve.length == 1) {
                var $link = $action_reserve.parent('a.action-link');
                
                if ($link.length == 1) {
                    $link.each(function(i, link) {
                        var $link        = $(link);
                        var entity_title = $.trim($action_reserve.find('.entity-title').text());
                        
                        if (entity_title === null) {
                            entity_title = "Reservations";
                        } else {
                            entity_title = entity_title + " Reservations";
                        }
                        
                        var link_href = $link.attr('href');
                        
                        var popup_options = get_fancybox_options({
                            href            : link_href, 
                            type            : 'iframe', 
                            title           : entity_title
                        });
                        
                        $link.attr('href', '#').click(function(event) {
                            event.preventDefault();
                            
                            $.fancybox.open(popup_options);
                            return false;
                        }).fancybox(popup_options);
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
                        /*var params = "max-height .4s easeOutExpo";
                        
                        $value.css({
                            "-webkit-transition"    : params, 
                            "-moz-transition"       : params, 
                            "-ms-transition"        : params, 
                            "-o-transition"         : params, 
                            "transition"            : params
                        });*/
                        
                        $elem.click(function(event) {
                            event.preventDefault();
                            
                            $item.toggleClass(metadata_item_expanded);
                            return false;
                        });
                    }
                }
            });
            
            update_stamps($sdetail);
            init_social_sharing();
        };
        
        
        // ---------------------------------------------------------------------
        // setup misc bindings
        // ---------------------------------------------------------------------
        
        
        // whenever the window scrolls, check if the header's layout needs to be updated
        $window.bind("scroll", update_dynamic_header);
        
        // whenever the window's resized, update the navbar layout
        $window.resize(update_navbar_layout);
        
        $(document).bind('keydown', function(e) {
            // close lightboxes, sDetail, and/or map popups when the user presses ESC
            // TODO: only close lightbox if one is up instead of closing sdetail as well
            if (e.which == 27) { // ESC
                if (typeof(close_sdetail_func) !== 'undefined' && !!close_sdetail_func) {
                    if ($('.fancybox-opened').length <= 0) {
                        close_sdetail_func();
                    }
                }
                
                if (typeof(g_close_map_popup) !== 'undefined' && !!g_close_map_popup) {
                    g_close_map_popup();
                }
            }
        });
        
        
        // ---------------------------------------------------------------------
        // base page initialization
        // ---------------------------------------------------------------------
        
        
        window.g_init_social_sharing();
        update_dynamic_header();
        update_stamps();
        init_gallery();
        update_navbar_layout();
        
        var __init = false;
        var show_initial_gallery = function() {
            if (!__init || $('#main-content').css('visibility') !== 'visible') {
                __init = true;
                
                update_gallery_layout(true);
                setTimeout(show_initial_gallery, 150);
            }
        };
        
        setTimeout(show_initial_gallery, 150);
    });
})();

