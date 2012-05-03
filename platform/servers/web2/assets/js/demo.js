/* demo.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    $(document).ready(function() {
        var client = new StampedClient();
        var screen_name = STAMPED_PRELOAD.user.screen_name;
        console.debug("Stamped profile page for screen_name '" + screen_name + "'");
        
        $(".stamp-gallery-nav a").each(function() {
            var href = $(this).attr('href');
            var limit_re = /([?&])limit=[\d]+/;
            var limit = "limit=10";
            
            if (href.match(limit_re)) {
                href = href.replace(limit_re, "$1" + limit);
            } else if ('?' in href) {
                href = href + "&" + limit;
            } else {
                href = href + "?" + limit;
            }
            
            $(this).attr('href', href);
        });
        
        var $container = $(".stamp-gallery .stamps");
        //$(document).emoji();
        //$container.emoji();
        
        $container.isotope({
            itemSelector    : '.stamp-gallery-item', 
            layoutMode      : "masonry", 
            masonry         : {
                columnWidth: 300
            }
        });
        
        // TODO: customize loading image
        $container.infinitescroll({
            debug           : STAMPED_PRELOAD.DEBUG, 
            bufferPx        : 200, 
            
            navSelector     : "div.stamp-gallery-nav", 
            nextSelector    : "div.stamp-gallery-nav a:last", 
            itemSelector    : "div.stamp-gallery div.stamp-gallery-item", 
            
            loading         : {
                finishedMsg : "No more stamps to load.", 
                msgText     : "<em>Loading more stamps...</em>", 
                img         : "/assets/img/loading.gif", 
                selector    : "div.stamp-gallery-loading"
            }
        }, function(new_elements) {
            var elements = $(new_elements);
            
            $(elements).emoji();
            $container.isotope('appended', elements);
        });
        
        $('.profile-nav a').each(function () {
            $(this).click(function() {
                $(this).parents(".profile-sections").each(function() {
                    $(this).find(".profile-section").slideToggle('fast', function() {
                        
                    });
                });
            });
        });
        
        return;
        
        var userP = client.get_user_by_screen_name(screen_name);
        
        userP.done(function (user) {
            var stampsP = client.get_user_stamps_by_screen_name(screen_name);
            
            stampsP.done(function (stamps) {
                $("#data2").hide();
                var stamps_view = new client.StampsGalleryView({
                    model : stamps, 
                    el : $("#data2")
                });
                
                $("#data").hide('slow', function() {
                    stamps_view.render();
                    $("#data2").show('slow');
                });
            });
        });
    });
})();

