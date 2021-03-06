/*! map.js
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
        var lite     = STAMPED_PRELOAD.lite;
        
        var init_stamp_id = STAMPED_PRELOAD.stamp_id;
        var center   = new google.maps.LatLng(40.707913, -74.013696);
        var user_pos = null;
        
        /*if (typeof(google.loader.ClientLocation) !== 'undefined') {
            var lat  = google.loader.ClientLocation.latitude;
            var lng  = google.loader.ClientLocation.longitude;
            var pos  = new google.maps.LatLng(lat, lng);
            
            center   = position;
        }*/
        
        var stamps   = STAMPED_PRELOAD.stamps;
        var stamps_  = {};
        var markers  = [];
        var def_zoom = 12;
        var map      = null;
        var init_marker_clusterer = null;
        
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
        
        if (!lite) {
            var options = {
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
            };
            
            map = new google.maps.Map(canvas, options);
            
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
            
            var stamp_map_popups            = {};
            var marker_clusterer            = null;
            var marker_clusterer_enabled    = false;
            
            var popup = new InfoBox({
                disableAutoPan: false, 
                maxWidth: 0, 
                pixelOffset: new google.maps.Size(-44, -50), 
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
            
            init_marker_clusterer = function() {
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
                        maxZoom             : def_zoom, 
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
                var coords0     = (stamps[0].entity.coordinates).split(",");
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
                
                google.maps.event.addListener(map, 'click',         close_popup);
                google.maps.event.addListener(map, 'zoom_changed',  close_popup);
                
                var partial_templates = {};
                
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
                        for (var image in multires_image.sizes) {
                            if (image.width === size) {
                                url  = image.url;
                                okay = true;
                                break;
                            }
                        }
                        
                        if (!okay) {
                            for (var image2 in multires_image.sizes) {
                                url  = image2.url;
                                okay = true;
                                break;
                            }
                        }
                    }
                    
                    if (!okay) {
                        //console.debug("no image of size '" + size + "' for user '" + screen_name + "'");
                    }
                    
                    return new Handlebars.SafeString('<img alt="' + alt + '" src="' + url + '" />');
                };
                
                Handlebars.registerHelper('user_profile_image', user_profile_image);
                var template = Handlebars.compile($('#stamp-map-item').html());
                
                // for each stamp, initialize a marker and add it to the map
                $.each(stamps, function(i, stamp) {
                    var coords  = (stamp.entity.coordinates).split(",");
                    var lat     = parseFloat(coords[0]);
                    var lng     = parseFloat(coords[1]);
                    var pos     = new google.maps.LatLng(lat, lng);
                    var title   = stamp.entity.title;
                    
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
                                if (!map.getBounds().contains(pos) || map.getZoom() < def_zoom) {
                                    map.fitBounds(stamp_bounds);
                                    map.setCenter(pos);
                                }
                            }
                            
                            popup.setContent(popup_content);
                            popup.open(map, marker);
                            
                            if (!!g_update_stamps) {
                                setTimeout(function() {
                                    var $s = $('.stamp-map-item');
                                    
                                    $s.find('.close').click(function(event) {
                                        event.preventDefault();
                                        close_popup();
                                        
                                        return false;
                                    });
                                    
                                    if (!lite) {
                                        $s.click(function(event) {
                                            if ($(event.target).is("a.close")) {
                                                return true;
                                            }
                                            
                                            return g_open_sdetail_click(event);
                                        });
                                        
                                        if (!!$.browser.msie) {
                                            // fix for IE stamp-map-item clickability
                                            $s.find(".sdetail").click(function(event) {
                                                return g_open_sdetail_click(event);
                                            });
                                            
                                            $s.find(".entity-header").click(function(event) {
                                                return g_open_sdetail_click(event);
                                            });
                                            
                                            $s.find(".content").click(function(event) {
                                                event.target = $(this).parents(".stamp-map-item");
                                                
                                                return g_open_sdetail_click(event);
                                            });
                                            
                                            $s.find("p").click(function(event) {
                                                event.target = $(this).parents(".stamp-map-item");
                                                
                                                return g_open_sdetail_click(event);
                                            });
                                        }
                                    }
                                    
                                    g_update_stamps($s);
                                }, 150);
                            }
                            
                            popup.selected = marker;
                        }
                        
                        if (!!e) {
                            e.stop();
                        }
                    };
                    
                    stamp_map_popups[stamp.stamp_id] = open_popup;
                    google.maps.event.addListener(marker, 'click', open_popup);
                });
            }
            
            var open_stamp_map_popup = function(stamp_id) {
                //console.debug("open_stamp_map_popup: " + stamp_id);
                
                if (!stamp_map_popups.hasOwnProperty(stamp_id)) {
                    //console.debug("ERROR: couldn't find stamp-list-view-item for stamp_id " + stamp_id);
                    // TODO: better error reporting!
                    
                    return;
                } else {
                    stamp_map_popups[stamp_id](null, true);
                }
            };
        }
        
        
        // ---------------------------------------------------------------------
        // Initialize stamp map navigation column
        // ---------------------------------------------------------------------
        
        
        var $stamp_map_nav_layout   = $('.stamp-map-nav-layout');
        var $stamp_map_nav_wrapper  = $('.stamp-map-nav-wrapper');
        var $list                   = $stamp_map_nav_wrapper.find('.stamp-list-view');
        
        var min_cls                 = 'stamp-map-nav-wrapper-collapsed';
        var list_height_expanded_px = 0;
        var footer_height           = 0;
        var center_main_cluster     = false;
        var centered_main_cluster   = false;
        
        var update_stamp_list_scrollbars = function() {
            $list.jScrollPane({
                contentWidth    : "0", 
                verticalPadding : 8
            });
        };
        
        var degrees_to_radians = function(x) {
            return x * Math.PI / 180;
        };
        
        var get_spherical_dist = function(p1, p2) {
            //var R = 6371; // earth's mean radius in km
            var R = 3959; // earth's mean radius in miles
            var dLat  = degrees_to_radians(p2.lat() - p1.lat());
            var dLong = degrees_to_radians(p2.lng() - p1.lng());
            
            var b = Math.cos(degrees_to_radians(p1.lat())) * Math.cos(degrees_to_radians(p2.lat()));
            var a = Math.sin(dLat/2) * Math.sin(dLat/2) + b * Math.sin(dLong/2) * Math.sin(dLong/2);
            var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            var d = R * c;
            
            return d;
        };
        
        var set_temp_max_zoom = function(zoom) {
            var bc = google.maps.event.addListener(map, 'idle', function() {
                if (this.getZoom() > zoom) {
                    this.setZoom(zoom);
                }
                
                google.maps.event.removeListener(bc);
            });
        };
        
        // resize map to fit viewport without scrolling page and also reset map bounds
        var resize_map = function() {
            var header_height = $canvas.offset().top || 0;
            var height        = (window.innerHeight - header_height);
            var height_px     = height + 'px';
            
            $canvas.height(height_px);
            
            if (!lite && !!center_main_cluster && !centered_main_cluster) {
                // optionally center map on specific stamp
                if (!!init_stamp_id) {
                    var stamp = get_stamp(init_stamp_id);
                    
                    if (!!stamp) {
                        center_main_cluster   = false;
                        centered_main_cluster = true;
                        
                        map.setCenter(stamp.pos);
                        map.setZoom(14);
                        
                        // open initial stamp popup and repaint marker clusterer
                        open_stamp_map_popup(init_stamp_id);
                        if (!!marker_clusterer) {
                            marker_clusterer.repaint();
                        }
                    }
                } else if (!!marker_clusterer) {
                    var init_clusterer = function(depth) {
                        if (depth >= 2) {
                            return;
                        }
                        
                        var clusters = marker_clusterer.getClusters();
                        var max_mark = null;
                        var max_pos  = null;
                        var max_size = -1;
                        
                        $.each(clusters, function(i, cluster) {
                            var size = cluster.getSize();
                            
                            if (size > max_size) {
                                max_size = size;
                                max_mark = cluster.getMarkers();
                                max_pos  = cluster.getCenter();
                            }
                        });
                        
                        if (max_pos !== null && max_size >= 4 && (depth === 0 || max_size > 10)) {
                            var max_cluster_bounds = new google.maps.LatLngBounds();
                            var total_dist  = 0.0;
                            var total_dist2 = 0.0;
                            
                            // calculate mean and stdev dist of each marker to the cluster's center
                            $.each(max_mark, function(i, marker) {
                                var pos  = marker.getPosition();
                                var dist = get_spherical_dist(max_pos, pos);
                                
                                total_dist  += dist;
                                total_dist2 += dist * dist;
                            });
                            
                            var mean   = (total_dist / max_size);
                            var stdev  = Math.sqrt((total_dist2 / max_size) - mean * mean);
                            var offset = 2.0 * stdev;
                            var pts    = [];
                            
                            // add all markers to the initial viewport bounds, disregarding obvious 
                            // outliers to produce a nice-fitting overall map
                            $.each(max_mark, function(i, marker) {
                                var pos  = marker.getPosition();
                                var dist = get_spherical_dist(max_pos, pos);
                                
                                if (Math.abs(mean - dist) < offset) {
                                    max_cluster_bounds.extend(pos);
                                    pts.push(pos);
                                }
                            });
                            
                            if (pts.length === 1) {
                                map.setCenter(pts[0]);
                            } else {
                                //console.debug(pts.length + " vs " + max_size);
                                //console.debug(max_cluster_bounds.toString());
                                
                                /*if (lite) {
                                    // shift the map's bounds west a bit to optimize stamp cluster placement on stamped.com landing page
                                    var b  = max_cluster_bounds;
                                    var sw = b.getSouthWest();
                                    var ne = b.getNorthEast();
                                    var dLng = 1.5 * (ne.lng() - sw.lng());
                                    
                                    max_cluster_bounds = new google.maps.LatLngBounds(new google.maps.LatLng(sw.lat(), sw.lng() + dLng), 
                                                                                      new google.maps.LatLng(ne.lat(), ne.lng() + dLng));
                                }*/
                                
                                map.fitBounds(max_cluster_bounds);
                            }
                            
                            set_temp_max_zoom(13);
                            
                            if (pts.length > 1) {
                                marker_clusterer.repaint();
                                
                                init_clusterer(depth + 1);
                            }
                        } else if (depth === 0 && max_size > 0) {
                            set_temp_max_zoom(13);
                        }
                    };
                    
                    center_main_cluster   = false;
                    centered_main_cluster = true;
                    init_clusterer(0);
                }
            }
            
            var nav_header_height = $stamp_map_nav_wrapper.find('.nav-header').height();
            var list_height       = (height - footer_height - 24 - nav_header_height);
            var list_height_px    = list_height + "px";
            
            list_height_expanded_px = list_height_px;
            
            if (!$stamp_map_nav_wrapper.hasClass(min_cls)) {
                $list.css({
                    'height'     : list_height_px, 
                    'max-height' : list_height_px
                });
                
                update_stamp_list_scrollbars();
            }
            
            var layout_clamped = "layout-clamped";
            
            $stamp_map_nav_layout.removeClass(layout_clamped);
            if ($stamp_map_nav_layout.offset().left < 0) {
                $stamp_map_nav_layout.addClass(layout_clamped);
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
                    'pointer-events' : 'none'
                });
                
                $canvas.addClass("blur-none").removeClass("blur-nohover");
                
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
                $canvas.removeClass("blur-none").addClass("blur-nohover");
                
                $list.animate({
                    height : list_height_expanded_px
                }, {
                    duration : duration, 
                    specialEasing : { 
                        width  : easing, 
                        height : easing
                    }, 
                    complete : function() {
                        update_stamp_list_scrollbars();
                    }
                });
            }
            
            return false;
        });
        
        var $stamp_list_view_items = $list.find('.stamp-list-view-item');
        
        var get_stamp_list_view_item_id = function($elem) {
            var stamp_id = g_extract_data($elem, 'stamp-id-', null);
            
            if (stamp_id === null) {
                //console.debug("ERROR: no stamp_id for stamp-list-view-item: " + $elem);
            }
            
            return stamp_id;
        };
        
        // initialize stamp-list-view functionality
        $stamp_list_view_items.click(function(event) {
            event.preventDefault();
            
            var $this       = $(this);
            var stamp_id    = get_stamp_list_view_item_id($this);
            
            if (stamp_id !== null) {
                if (lite) {
                    var stamp = get_stamp(stamp_id);
                    
                    if (!!stamp && !!stamp.url && parent.frames.length > 0) {
                        var url = stamp.url.replace('http://www.stamped.com', '');
                        
                        top.location = url;
                    }
                } else {
                    open_stamp_map_popup(stamp_id);
                }
            }
            
            return false;
        });
        
        if (!lite) {
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
                
                var duration = 200;
                var easing   = 'easeOutCubic';
                var done     = 0;
                 
                var complete = function() {
                    if (++done >= 2) {
                        // update the stamp-list-view's scrollbar once we're done hiding & 
                        // showing the relevant stamp-list-view-item's
                        update_stamp_list_scrollbars();
                    }
                };
                
                // animate width, height, and opacity
                //$to_show.stop(true, false).show(duration, easing, complete);
                //$to_hide.stop(true, false).hide(duration, easing, complete);
                
                // animate height and opacity
                $to_show.stop(true, false).slideDown(duration, easing, complete).animate({
                    'opacity' : 1
                }, {
                    duration : duration, 
                    easing   : easing, 
                    queue    : false
                });
                
                $to_hide.stop(true, false).slideUp(duration, easing, complete).animate({
                    'opacity' : 0
                }, {
                    duration : duration, 
                    easing   : easing, 
                    queue    : false
                });
            };
        } else {
            var handle_lite_link = function(event) {
                var url = $(this).attr("href");
                
                if (!!url && parent.frames.length > 0) {
                    event.preventDefault();
                    
                    top.location = url;
                    return false;
                } else {
                    return true;
                }
            };
            
            $(".profile-image-medium-ish").click(handle_lite_link);
            $(".screen-name").click(handle_lite_link);
            $(".user-logo-large").click(handle_lite_link);
        }
        
        
        // ---------------------------------------------------------------------
        // Initialize the 'jump to my location' control
        // ---------------------------------------------------------------------
        
        
        if (!lite && navigator.geolocation) {
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
                                
                                //console.debug("user_pos: " + user_pos);
                                update_map_center(user_pos);
                            }
                            
                            finally_func();
                        }, function() {
                            //console.debug("ERROR: navigator.geolocation.getCurrentPosition failed!");
                            
                            finally_func();
                        });
                    }
                    
                    return false;
                });
        }
        
        
        // ---------------------------------------------------------------------
        // Misc bindings and base page initialization
        // ---------------------------------------------------------------------
        
        
        window.addEventListener('resize', resize_map, false);
        
        if (lite) {
            resize_map();
        } else {
            $(document).bind('keydown', 'ctrl+t', function() {
                toggle_marker_clusterer();
            });
            
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
            
            setTimeout(function() {
                if (typeof(g_init_social_sharing) !== 'undefined') {
                    g_init_social_sharing();
                }
            }, 1000);
        }
        
        setTimeout(resize_map, 150);
    });
})();

