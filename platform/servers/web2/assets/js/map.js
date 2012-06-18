/* map.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    $(document).ready(function() {
        
        // ---------------------------------------------------------------------
        // Initialize Google Maps canvas
        // ---------------------------------------------------------------------
        
        
        var canvas   = $(".stamp-map .stamp-map-canvas")[0];
        var $canvas  = $(canvas);
        
        // TODO: load in preloaded stamps
        
        var center   = new google.maps.LatLng(40.707913, -74.013696);
        var user_pos = null;
        
        /*if (typeof(google.loader.ClientLocation) !== 'undefined') {
            var lat  = google.loader.ClientLocation.latitude;
            var lng  = google.loader.ClientLocation.longitude;
            var pos  = new google.maps.LatLng(lat, lng);
            
            center   = position;
        }*/
        
        var map      = new google.maps.Map(canvas, {
	        mapTypeId           : google.maps.MapTypeId.ROADMAP, 
            center              : center, 
            zoom                : 8, 
            
            // disable all default controls in favor of enabling a few explicitly
            disableDefaultUI    : true,
            
            zoomControl         : true,
            zoomControlOptions  : {
                style           : google.maps.ZoomControlStyle.DEFAULT, 
                position        : google.maps.ControlPosition.TOP_RIGHT
            }, 
            
            panControl          : true, 
            panControlOptions   : {
                position        : google.maps.ControlPosition.TOP_RIGHT
            }
        });
        
        var update_map_center = function(pos) {
            // TODO: only use user_pos or update center on resize if we're still at the default center
            if (user_pos !== null) {
                map.setCenter(user_pos);
                map.setZoom(14);
            } else {
                map.setCenter(pos);
            }
        };
        
        var image   = new google.maps.MarkerImage('/assets/img/pin.png',
                                                  new google.maps.Size(26, 36),
                                                  new google.maps.Point(0,0),
                                                  new google.maps.Point(13, 30));
        
        var shadow  = new google.maps.MarkerImage('/assets/img/pin_shadow.png',
                                                  new google.maps.Size(24, 18),
                                                  new google.maps.Point(0,0),
                                                  new google.maps.Point(2, 17));
        
        var stamps  = STAMPED_PRELOAD.stamps;
        var stamps_ = {};
        var markers = [];
        
        // build dict of stamp_id => stamp for fast lookups
        $.each(stamps, function(i, stamp) {
            stamps_[stamp.stamp_id] = stamp;
        });
        
        var get_stamp = function(stamp_id) {
            if (stamps_.hasOwnProperty(stamp_id)) {
                return stamps_[stamp_id];
            } else {
                return null;
            }
        };
        
        var stamp_map_popups            = {};
        var marker_clusterer            = null;
        var marker_clusterer_enabled    = false;
        
        /*var popup  = new google.maps.InfoWindow({
            maxWidth : 340
        });*/
        
        var popup = new InfoBox({
            disableAutoPan: false, 
            maxWidth: 0, 
            pixelOffset: new google.maps.Size(-48, -32), 
            zIndex: null, 
            boxStyle: {
                width: "340px"
            }, 
            closeBoxMargin: "16px 6px 2px 2px", 
            closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif", 
            infoBoxClearance: new google.maps.Size(2, 2), 
            isHidden: false, 
            pane: "floatPane", 
            enableEventPropagation: false, 
            alignBottom: true
        });
        
        var init_marker_clusterer = function() {
            if (!!marker_clusterer) {
                return;
            }
            
            var minimumClusterSize = 4;
            var gridSize = 20;
            
            // only enable marker clustering if there are enough stamps
            if (stamps.length > minimumClusterSize) {
                marker_clusterer = new MarkerClusterer(map, markers, {
                    minimumClusterSize  : minimumClusterSize, 
                    gridSize            : gridSize, 
                    averageCenter       : true, 
                    maxZoom             : 12, 
                    title               : "Expand Stamp Cluster"
                });
                
                marker_clusterer_enabled = true;
                
                google.maps.event.addListener(marker_clusterer, "clusteringend", function() {
                    if (!centered_main_cluster) {
                        center_main_cluster = true;
                        resize_map();
                    }
                });
            }
        };
        
        // enable or disable the marker clusterer
        var toggle_marker_clusterer = function() {
            if (!marker_clusterer) {
                init_marker_clusterer();
            } else if (marker_clusterer_enabled) {
                marker_clusterer.setMap(null);
                marker_clusterer = null;
                marker_clusterer_enabled = false;
            } else {
                marker_clusterer.setMap(map);
                marker_clusterer.resetViewport();
                marker_clusterer_enabled = true;
            }
        };
        
        if (stamps.length > 0) {
            var coords0     = (stamps[0]['entity']['coordinates']).split(",");
            var lat0        = parseFloat(coords0[0]);
            var lng0        = parseFloat(coords0[1]);
            var pos0        = new google.maps.LatLng(lat0, lng0);
            var bounds      = new google.maps.LatLngBounds(pos0, pos0);
            
            var close_popup = function() {
                if (!!popup.selected) {
                    popup.close();
                    popup.selected = null;
                }
            };
            
            window.g_close_map_popup = close_popup;
            
            google.maps.event.addListener(map, 'click',          close_popup);
            google.maps.event.addListener(map, 'zoom_changed',   close_popup);
            
            var partial_templates = {}
            
            $(".handlebars-template").each(function (i) {
                var $this = $(this);
                var key   = $this.attr('id');
                var val   = $this.html();
                
                partial_templates[key] = val;
            });
            
            // TODO: this Handlebars template helper doesn work
            var user_profile_image = function(size) {
                size = (typeof(size) === 'undefined' ? 144 : size);
                
                var multires_image  = this.image;
                var screen_name     = this.screen_name;
                var name            = this.name;
                
                var alt  = screen_name;
                var url  = "http://static.stamped.com/users/default.jpg";
                var okay = false;
                
                if (!!name) {
                    alt  = name + "(" + alt + ")";
                }
                
                if (!!multires_image) {
                    for (image in multires_image.sizes) {
                        if (image.width === size) {
                            url  = image.url;
                            okay = true;
                            break;
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
                
                stamp.pos = pos;
                
                var popup_content = template(stamp, {
                    partials : partial_templates
                });
                
                var dLat = 0.05;
                var dLng = 0.1;
                
                var stamp_bounds = new google.maps.LatLngBounds(new google.maps.LatLng(lat - dLat, lng - dLng), 
                                                                new google.maps.LatLng(lat + dLat, lng + dLng));
                
                var open_popup = function(e, should_center) {
                    // guard to only display a single marker InfoBox at a time
                    if (popup.selected === marker) {
                        close_popup();
                    } else {
                        if (typeof(should_center) !== 'undefined' && !!should_center) {
                            
                            // only adjust map bounds / center if we're not already zoomed 
                            // in on the desired marker
                            if (!map.getBounds().contains(pos) || map.getZoom() < 12) {
                                map.fitBounds(stamp_bounds);
                                map.setCenter(pos);
                            }
                        }
                        
                        popup.setContent(popup_content);
                        popup.open(map, marker);
                        
                        if (!!g_update_stamps) {
                            setTimeout(function() {
                                var $s = $('.stamp-map-item');
                                g_update_stamps($s);
                            }, 150);
                        }
                        
                        popup.selected = marker;
                    }
                    
                    if (!!e) {
                        e.stop();
                    }
                }
                
                stamp_map_popups[stamp.stamp_id] = open_popup;
                google.maps.event.addListener(marker, 'click', open_popup);
            });
        }
        
        var open_stamp_map_popup = function(stamp_id) {
            console.debug("open_stamp_map_popup: " + stamp_id);
            
            if (!stamp_map_popups.hasOwnProperty(stamp_id)) {
                console.debug("ERROR: couldn't find stamp-list-view-item for stamp_id " + stamp_id);
                
                return;
            } else {
                stamp_map_popups[stamp_id](null, true);
            }
        };
        
        
        // ---------------------------------------------------------------------
        // Initialize stamp map navigation column
        // ---------------------------------------------------------------------
        
        
        var $stamp_map_nav_wrapper  = $('.stamp-map-nav-wrapper');
        var $list                   = $stamp_map_nav_wrapper.find('.stamp-list-view');
        
        var min_cls                 = 'stamp-map-nav-wrapper-collapsed';
        var list_height_expanded_px = 0;
        var footer_height           = 0;
        var center_main_cluster     = false;
        var centered_main_cluster   = false;
        
        var update_stamp_list_scrollbars = function($elem) {
            if (!!$elem) {
                $elem.jScrollPane({
                    contentWidth : "0", 
                });
            }
        };
        
        // resize map to fit viewport without scrolling page and also reset map bounds
        var resize_map = function() {
            var header_height = $canvas.offset().top || 0;
            var height        = (window.innerHeight - header_height);
            var height_px     = height + 'px';
            
            $canvas.height(height_px);
            
            if (!!center_main_cluster && !centered_main_cluster) {
                if (!!marker_clusterer) {
                    var init_clusterer = function(depth) {
                        if (depth >= 2) {
                            return;
                        }
                        
                        var clusters = marker_clusterer.getClusters();
                        var max_mark = null;
                        var max_size = -1;
                        
                        $.each(clusters, function(i, cluster) {
                            var size = cluster.getSize();
                            
                            if (size > max_size) {
                                max_size = size;
                                max_mark = cluster.getMarkers();
                            }
                        });
                        
                        if (max_size > 0 && (depth == 0 || max_size > 4)) {
                            var max_cluster_bounds = new google.maps.LatLngBounds();
                            
                            $.each(max_mark, function(i, marker) {
                                max_cluster_bounds.extend(marker.getPosition());
                            });
                            
                            map.fitBounds(max_cluster_bounds);
                            
                            marker_clusterer.repaint();
                            init_clusterer(depth + 1);
                        }
                    };
                    
                    center_main_cluster   = false;
                    centered_main_cluster = true;
                    init_clusterer(0);
                }
            }
            
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
        
        // initialize collapsable stamp list view behavior
        $('.list-view-nav a').click(function(event) {
            event.preventDefault();
            
            var $this    = $(this);
            var $nav     = $this.parents('.stamp-map-nav-wrapper');
            var $list    = $nav.find('.stamp-list-view').stop(true, false);
            
            var duration = 600;
            var easing   = 'easeOutCubic';
            
            $nav.toggleClass(min_cls);
            
            if ($nav.hasClass(min_cls)) { // collapsing animation
                $nav.parent().css({
                    'pointer-events' : 'none', 
                });
                
                $list.animate({
                    height : "0"
                }, {
                    duration : duration, 
                    specialEasing : { 
                        width  : easing, 
                        height : easing
                    }
                });
            } else { // expanding animation
                $list.animate({
                    height : list_height_expanded_px
                }, {
                    duration : duration, 
                    specialEasing : { 
                        width  : easing, 
                        height : easing
                    }, 
                    complete : function() {
                        update_stamp_list_scrollbars($list);
                    }
                })
            }
            
            return false;
        });
        
        var $stamp_list_view_items = $list.find('.stamp-list-view-item');
        
        var get_stamp_list_view_item_id = function($elem) {
            var stamp_id = g_extract_data($elem, 'stamp-id-', null);
            
            if (stamp_id === null) {
                console.debug("ERROR: no stamp_id for stamp-list-view-item: " + $elem);
            }
            
            return stamp_id;
        };
        
        // initialize stamp-list-view functionality
        $stamp_list_view_items.click(function(event) {
            event.preventDefault();
            
            var $this       = $(this);
            var stamp_id    = get_stamp_list_view_item_id($this);
            
            if (stamp_id !== null) {
                open_stamp_map_popup(stamp_id);
            }
            
            return false;
        });
        
        // filter stamp-list-view contents w.r.t. current viewport
        var bounds_changed = function(event) {
            var bounds = map.getBounds();
            /*var sw = bounds.getSouthWest();
            var ne = bounds.getNorthEast();
            
            var dLat = 0.05 * (ne.latitude  - sw.latitude);
            var dLng = 0.05 * (ne.longitude - sw.longitude);
            
            // enlarge the bounds slightly to provide a small cushion
            bounds = new google.maps.LatLngBounds(new google.maps.LatLng(sw.latitude - dLat, sw.longitude - dLng), 
                                                  new google.maps.LatLng(ne.latitude + dLat, ne.longitude + dLng));*/
            
            var $to_hide = $([]);
            var $to_show = $([]);
            
            $stamp_list_view_items.each(function(i, elem) {
                var $elem    = $(elem);
                var stamp_id = get_stamp_list_view_item_id($elem);
                var visible  = false;
                
                if (stamp_id !== null) {
                    var stamp   = get_stamp(stamp_id);
                    
                    if (!!stamp) {
                        visible = bounds.contains(stamp.pos);
                    }
                }
                
                if (visible) {
                    $to_show = $to_show.add($elem);
                } else {
                    $to_hide = $to_hide.add($elem);
                }
            });
            
            var duration = 100;
            var done = 0;
             
            var complete = function() {
                if (++done >= 2) {
                    // update the stamp-list-view's scrollbar once we're done hiding & 
                    // showing the relevant stamp-list-view-item's
                    update_stamp_list_scrollbars($list);
                }
            };
            
            // TODO: animate only height and opacity
            $to_show.stop(true, false).show(duration, 'easeOutCubic', complete);
            $to_hide.stop(true, false).hide(duration, 'easeOutCubic', complete);
        };
        
        
        // ---------------------------------------------------------------------
        // Initialize the 'jump to my location' control
        // ---------------------------------------------------------------------
        
        
        if (navigator.geolocation) {
            $('a.my-location')
                .css('display', 'block')
                .click(function(event) {
                    event.stopPropagation();
                    
                    if (user_pos !== null) {
                        update_map_center(user_pos);
                    } else {
                        var $this = $(this);
                        $this.addClass('my-location-loading');
                        
                        var finally_func = function() {
                            $this.removeClass('my-location-loading');
                        };
                        
                        navigator.geolocation.getCurrentPosition(function(position) {
                            if (!!position) {
                                var lat  = position.coords.latitude;
                                var lng  = position.coords.longitude;
                                user_pos = new google.maps.LatLng(lat, lng);
                                
                                console.debug("user_pos: " + user_pos);
                                update_map_center(user_pos);
                            }
                            
                            finally_func();
                        }, function() {
                            console.debug("ERROR: navigator.geolocation.getCurrentPosition failed!");
                            
                            finally_func();
                        });
                    }
                    
                    return false;
                });
        }
        

        
        // ---------------------------------------------------------------------
        // Misc bindings and base page initialization
        // ---------------------------------------------------------------------
        
        
        $(document).bind('keydown', 'ctrl+t', function() {
            toggle_marker_clusterer();
        });
        
        window.addEventListener('resize', resize_map, false);
        
        google.maps.event.addListener(map, 'idle', bounds_changed);
        
        var update_map_bounds = function() {
            map.fitBounds(bounds);
            update_map_center(bounds.getCenter());
        };
        
        // TODO: put this in a generic page initialization handler
        // note: ordering of initialization is important here
        
        update_map_bounds();
        resize_map();
        init_marker_clusterer();
        
        setTimeout(resize_map, 150);
        
        setTimeout(function() {
            if (typeof(g_init_social_sharing) !== 'undefined') {
                g_init_social_sharing();
            }
        }, 1000);
    });
})();

