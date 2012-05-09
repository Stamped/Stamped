/* profile.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    $(document).ready(function() {
        // ---------------------------------------------------------------------
        // initialize profile header navigation
        // ---------------------------------------------------------------------
        
        $('.profile-nav a').each(function () {
            $(this).click(function() {
                var link = $(this);
                
                link.parents(".profile-sections").each(function() {
                    var elems = $(this).find(".profile-section");
                    /*var to_hide = -1;
                    
                    $(elems).each(function (i, elem) {
                        if ($(elem).is(":visible")) {
                            to_hide = i;
                            return false;
                        }
                    });
                    
                    var offset  = (link.hasClass("up-arrow") ? -1 : 1);
                    var to_show = (to_hide + offset) % elems.length;
                    
                    var elem_to_hide = $(elems[to_hide]);
                    var elem_to_show = $(elems[to_show]);
                    
                    elem_to_hide.css("height: 100%; opacity: 1;");
                    elem_to_show.css("height: 0; opacity: 0;");
                    elem_to_show.show();
                    
                    elem_to_hide.animate({
                        opacity  : 0, 
                        height   : 0
                    }, {
                        queue    : false, 
                        duration : 2000, 
                        easing   : 'swing', 
                    });
                    
                    elem_to_show.animate({
                        opacity  : 1, 
                        height   : "100%"
                    }, {
                        queue    : false, 
                        duration : 2000, 
                        easing   : 'swing', 
                        complete : function() {
                            elem_to_hide.hide();
                        }
                    });*/
                    
                    $(elems).slideToggle('fast', function() {
                        
                    });
                });
            });
        });
        
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
        
        // ---------------------------------------------------------------------
        // initialize stamp-gallery isotope / masonry layout and infinite scroll
        // ---------------------------------------------------------------------
        
        var $container = $(".stamp-gallery .stamps");
        // TODO: may not be recursive
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
        
        var client = new StampedClient();
        var screen_name = STAMPED_PRELOAD.user.screen_name;
        console.debug("Stamped profile page for screen_name '" + screen_name + "'");
        
        $('.sign-in a.button').click(function() {
            client.login('travis', 'cierfshs2').done(function(user) {
                console.debug("login:");
                console.debug(user);
                
                client.get_authorized_user().done(function(auth_user) {
                    console.debug("authorized:");
                    console.debug(auth_user);
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

