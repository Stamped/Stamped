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
        //var stamps = new client.Stamps(STAMPED_PRELOAD.stamps);
        var stamps = STAMPED_PRELOAD.stamps;
        
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
            
            var info = "<div class='marker'><p class='pronounced-title'>" + title + "</p>";
            
            for (var i = 0; i < stamp['contents'].length; ++i) {
                var content = stamp['contents'][i];
                var blurb = content['blurb'];
                
                info += "<p>" + blurb + "</p>";
            }
            info += "</div>";
            
            var infowindow = new google.maps.InfoWindow({
                content: info
            });
            
            google.maps.event.addListener(marker, 'click', function() {
                infowindow.open(map, marker);
            });
        });
        
        var resize_map = function() {
            var header_height = $canvas.offset().top || 0;
            var margin = 0;
            var height = (window.innerHeight - header_height - margin) + 'px';
            
            $canvas.height(height);
        };
        
        resize_map();
        setTimeout(resize_map, 150);
        
        window.addEventListener('resize', resize_map, false);
    });
})();

/*
  var infowindow = new google.maps.InfoWindow({
      content: contentString
  });
  google.maps.event.addListener(marker, 'click', function() {
    infowindow.open(map, marker);
  });
*/

