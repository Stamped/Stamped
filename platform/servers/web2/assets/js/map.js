/* map.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    $(document).ready(function() {
        
        // ---------------------------------------------------------------------
        // Initialize Google Maps canvas
        // ---------------------------------------------------------------------
        
        
        var canvas  = $(".stamp-map .stamp-map-canvas")[0];
        var $canvas = $(canvas);
        
        // TODO: load in preloaded stamps
        
        var center  = new google.maps.LatLng(40.707913, -74.013696);
        
        var map     = new google.maps.Map(canvas, {
	        mapTypeId           : google.maps.MapTypeId.ROADMAP, 
            center              : center, 
            zoom                : 8, 
            
            // disable all default controls in favor of enabling a few explicitly
            disableDefaultUI    : true,
            
            zoomControl         : true,
            zoomControlOptions  : {
                style           : google.maps.ZoomControlStyle.LARGE,
                position        : google.maps.ControlPosition.TOP_RIGHT
            }, 
            
            panControl          : true, 
            panControlOptions   : {
                position        : google.maps.ControlPosition.TOP_RIGHT
            }
        });
        
        var image   = new google.maps.MarkerImage('/assets/img/pin.png',
                                                 new google.maps.Size(26, 36),
                                                 new google.maps.Point(0,0),
                                                 new google.maps.Point(13, 30));
        
        var shadow  = new google.maps.MarkerImage('/assets/img/pin_shadow.png',
                                                 new google.maps.Size(24, 18),
                                                 new google.maps.Point(0,0),
                                                 new google.maps.Point(2, 17));
        
        var client = new StampedClient();
        var stamps = STAMPED_PRELOAD.stamps;
        
        var popup  = new InfoBox({
            disableAutoPan: false, 
            maxWidth: 0, 
            pixelOffset: new google.maps.Size(-140, -25), 
            zIndex: null, 
            boxStyle: {
                width: "280px"
            }, 
            closeBoxMargin: "16px 6px 2px 2px", 
            closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif", 
            infoBoxClearance: new google.maps.Size(2, 2), 
            isHidden: false, 
            pane: "floatPane", 
            enableEventPropagation: false, 
            alignBottom: true
        });
        
        if (stamps.length > 0) {
            var coords0     = (stamps[0]['entity']['coordinates']).split(",");
            var lat0        = parseFloat(coords0[0]);
            var lng0        = parseFloat(coords0[1]);
            var pos0        = new google.maps.LatLng(lat0, lng0);
            var bounds      = new google.maps.LatLngBounds(pos0, pos0);
            
            var markers     = []
            
            var close_popup = function() {
                if (!!popup.selected) {
                    popup.close();
                    popup.selected = null;
                }
            };
            
            google.maps.event.addListener(map, 'click',        close_popup);
            google.maps.event.addListener(map, 'zoom_changed', close_popup);
            
            var partial_templates = {}
            
            $(".handlebars-template").each(function (i) {
                var key = $(this).attr('id');
                var val = $(this).html();
                
                partial_templates[key] = val;
            });
            
            var user_profile_image = function(size) {
                size = (typeof(size) === 'undefined' ? 144 : size);
                
                var name = this.name;
                var screen_name = this.screen_name;
                var alt  = screen_name;
                var url  = "http://static.stamped.com/users/default.jpg";
                var okay = false;
                var multires_image = this.image;
                
                if (!!name) {
                    alt  = name + "(" + alt + ")";
                }
                
                if (!!multires_image) {
                    for (image in multires_image.sizes) {
                        if (image.width === size) {
                            url  = image.url;
                            okay = true;
                            break
                        }
                    }
                    
                    if (!okay) {
                        for (image in multires_image.sizes) {
                            url  = image.url;
                            okay = true;
                            break;
                        }
                    }
                }
                
                if (!okay) {
                    console.debug("no image of size '" + size + "' for user '" + screen_name + "'");
                }
                
                return new Handlebars.SafeString('<img alt="' + alt + '" src="' + url + '" />');
            };
            
            Handlebars.registerHelper('user_profile_image', user_profile_image);
            var template = Handlebars.compile($('#stamp-map-item').html());
            
            // for each stamp, initialize a marker and add it to the map
            $.each(stamps, function(i, stamp) {
                var coords  = (stamp['entity']['coordinates']).split(",");
                var lat     = parseFloat(coords[0]);
                var lng     = parseFloat(coords[1]);
                var pos     = new google.maps.LatLng(lat, lng);
                var title   = stamp['entity']['title'];
                
                var marker  = new google.maps.Marker({
                    position    : pos, 
                    map         : map, 
                    shadow      : shadow, 
                    icon        : image, 
                    shape       : null, 
                    title       : title, 
                    zIndex      : 1
                });
                
                //console.debug("lat: " + lat + "; lng: " + lng);
                bounds.extend(pos);
                markers.push(marker);
                
                // create the html content for the popup InfoBox
                /*var info = "<div class='marker stamp-category-" + stamp['entity']['category'] + "'><div class='top-wave'></div><div class='marker-content'><p class='pronounced-title'><a href='" + stamp['url'] + "'>" + title + "</a></p>";
                
                info += "<p class='subtitle-line'>" + 
                            "<span class='icon'></span>" + 
                            "<span class='subtitle'>" + 
                                stamp['entity']['subtitle'] + 
                            "</span>" + 
                        "</p>";
                
                // stamps may have more than one blurb associated with them, so add each one
                // in turn to this marker's InfoBox content
                for (var i = 0; i < stamp['contents'].length; ++i) {
                    var content = stamp['contents'][i];
                    var blurb   = content['blurb'];
                    
                    if (blurb.length > 0) {
                        info += "<p class='blurb'>" + blurb + "</p>";
                    }
                }
                
                info += "</div><div class='bottom-wave'></div></div>";*/
                
                var info = template(stamp, { partials : partial_templates });
                //console.debug(stamp.entity.title + ":");
                //console.debug(info);
                //var info = "<div class='stamp-map-item'>" + stamp.entity.title + "</div>";
                
                var open_popup = function(e) {
                    // guard to only display a single marker InfoBox at a time
                    if (popup.selected === marker) {
                        close_popup();
                    } else {
                        popup.setContent(info);
                        popup.open(map, marker);
                        popup.selected = marker;
                    }
                    
                    e.stop();
                }
                
                google.maps.event.addListener(marker, 'click', open_popup);
            });
            
            var minimumClusterSize = 3;
            var gridSize = 20;
            
            // only enable marker clustering if there are enough stamps
            if (stamps.length > minimumClusterSize) {
                new MarkerClusterer(map, markers, {
                    minimumClusterSize : minimumClusterSize, 
                    gridSize : gridSize
                });
            }
        }
        
        
        // ---------------------------------------------------------------------
        // Initialize stamp map navigation column
        // ---------------------------------------------------------------------
        
        
        var $stamp_map_nav_wrapper  = $('.stamp-map-nav-wrapper');
        var $list = $stamp_map_nav_wrapper.find('.stamp-list-view');
        var list_height_expanded_px = 0;
        var min_cls = 'stamp-map-nav-wrapper-collapsed';
        var footer_height = 0;
        
        var update_stamp_list_scrollbars = function($elem) {
            if (!!$elem) {
                $elem.jScrollPane({
                    contentWidth : "0"
                });
            }
        };
        
        // resize map to fit viewport without scrolling page and also reset map bounds
        var resize_map = function() {
            var header_height = $canvas.offset().top || 0;
            var height = (window.innerHeight - header_height);
            var height_px = height + 'px';
            
            $canvas.height(height_px);
            
            map.fitBounds(bounds);
            map.setCenter(bounds.getCenter());
            
            var nav_header_height = $stamp_map_nav_wrapper.find('.nav-header').height();
            var list_height       = (height - footer_height - 64 - nav_header_height);
            var list_height_px    = list_height + "px";
            
            list_height_expanded_px = list_height_px;
            
            if (!$stamp_map_nav_wrapper.hasClass(min_cls)) {
                $list.css({
                    'height'     : list_height_px, 
                    'max-height' : list_height_px
                });
                
                update_stamp_list_scrollbars($list);
            }
        };
        
        $stamp_map_nav_wrapper.find('.nav-footer, .nav-dummy-footer').each(function(i, elem) {
            var $elem  = $(elem);
            var height = $elem.height();
            
            if (height > 0) {
                footer_height = height;
                
                $elem.css({
                    'min-height' : height, 
                    'max-height' : height
                });
            }
        });
        
        $('.list-view-nav a').click(function(event) {
            event.preventDefault();
            
            var $this   = $(this);
            var $nav    = $this.parents('.stamp-map-nav-wrapper');
            var $list   = $nav.find('.stamp-list-view').stop(true, false);
            
            $nav.toggleClass(min_cls);
            
            if ($nav.hasClass(min_cls)) { // collapsing animation
                
                $nav.parent().css({
                    'pointer-events' : 'none', 
                });
                
                $list.animate({
                    height : "0"
                }, {
                    duration : 600, 
                    specialEasing : { 
                        width  : 'easeOutCubic', 
                        height : 'easeOutCubic'
                    }
                });
            } else { // expanding animation
                $list.animate({
                    height : list_height_expanded_px
                }, {
                    duration : 600, 
                    specialEasing : { 
                        width  : 'easeOutCubic', 
                        height : 'easeOutCubic'
                    }, 
                    complete : function() {
                        update_stamp_list_scrollbars($list);
                    }
                })
            }
            
            return false;
        });
        
        
        // ---------------------------------------------------------------------
        // Misc bindings and base page initialization
        // ---------------------------------------------------------------------
        
        
        // TODO: put this in a generic page initialization handler
        resize_map();
        setTimeout(resize_map, 150);
        
        window.addEventListener('resize', resize_map, false);
        
        setTimeout(function() {
            if (typeof(g_init_social_sharing) !== 'undefined') {
                g_init_social_sharing();
            }
        }, 1000);
    });
})();

