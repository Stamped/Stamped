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
        
        var marker  = new google.maps.Marker({
            position    : center,
            map         : map,
            shadow      : shadow,
            icon        : image,
            shape       : null,
            title       : 'TEST',
            zIndex      : 1
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

