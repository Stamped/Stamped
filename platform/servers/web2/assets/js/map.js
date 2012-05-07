/* map.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    $(document).ready(function() {
        var canvas  = $(".stamp-map .stamp-map-canvas")[0];
        var $canvas = $(canvas);
        $canvas.css("width: 100%; height: 100%; background: red;");
        
        // TODO: load in preloaded stamps
        
        var center  = new google.maps.LatLng(40.707913, -74.013696);
        
        var map     = new google.maps.Map(canvas, {
            center      : center, 
            zoom        : 8, 
	        mapTypeId   : google.maps.MapTypeId.ROADMAP
            /*zoomControl : true,
            
            disableDefaultUI    : true,
            zoomControlOptions  : {
                style   : google.maps.ZoomControlStyle.LARGE,
                position: google.maps.ControlPosition.TOP_RIGHT
            }*/
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
        //var stamps = new client.Stamps(STAMPED_PRELOAD.stamps);
        
        //var popup  = new google.maps.InfoWindow({ });
        var popup  = new InfoBox({
             disableAutoPan: false, 
             maxWidth: 0, 
             pixelOffset: new google.maps.Size(-140, 0), 
             zIndex: null, 
             boxStyle: {
                 width: "280px"
             }, 
             closeBoxMargin: "16px 6px 2px 2px", 
             closeBoxURL: "http://www.google.com/intl/en_us/mapfiles/close.gif", 
             infoBoxClearance: new google.maps.Size(1, 1), 
             isHidden: false, 
             pane: "floatPane", 
             enableEventPropagation: false
        });
        
        if (stamps.length > 0) {
            var coords0     = (stamps[0]['entity']['coordinates']).split(",");
            var lat0        = parseFloat(coords0[0]);
            var lng0        = parseFloat(coords0[1]);
            var pos0        = new google.maps.LatLng(lat0, lng0);
            var bounds      = new google.maps.LatLngBounds(pos0, pos0);
            
            var markers     = []
            
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
                
                var info = "<div class='marker'><div class='top-wave'></div><div class='marker-content'><p class='pronounced-title'><a href='" + stamp['url'] + "'>" + title + "</a></p>";
                
                for (var i = 0; i < stamp['contents'].length; ++i) {
                    var content = stamp['contents'][i];
                    var blurb   = content['blurb'];
                    
                    info += "<p class='blurb'>" + blurb + "</p>";
                }
                info += "</div><div class='bottom-wave'></div></div>";
                
                google.maps.event.addListener(marker, 'click', function() {
                    popup.setContent(info);
                    popup.open(map, marker);
                    this.stop();
                });
                
                var close_popup = function() {
                    popup.close();
                };
                
                google.maps.event.addListener(map, 'click',        close_popup);
                google.maps.event.addListener(map, 'zoom_changed', close_popup);
            });
            
            var clusterer   = new MarkerClusterer(map, markers, {
                gridSize : 3
            });
        }
        
        var resize_map = function() {
            var header_height = $canvas.offset().top || 0;
            var margin = 0;
            var height = (window.innerHeight - header_height - margin) + 'px';
            
            $canvas.height(height);
            
            map.fitBounds(bounds);
            map.setCenter(bounds.getCenter());
        };
        
        resize_map();
        setTimeout(resize_map, 150);
        
        window.addEventListener('resize', resize_map, false);
    });
})();

