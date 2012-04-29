/* demo.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    $(document).ready(function() {
        var client = new StampedClient();
        var screen_name = "travis";
        
        var userP = client.get_user_by_screen_name(screen_name);
        userP.done(function (user) {
            log(user.get('user_id'));
            //$("#data").append("<pre><code style='font-size: 12px; font-family: \"courier new\" monospace;'>" + JSON.stringify(user.toJSON(), null, 4) + "</code></pre>");
            
            var stampsP = client.get_user_stamps_by_screen_name(screen_name);
            stampsP.done(function (stamps) {
                //console.debug(stamps);
                //stamps = JSON.stringify(stamps, null, 4);
                //$("#data").append("<pre><code style='font-size: 12px; font-family: \"courier new\" monospace;'>" + JSON.stringify(stamps.toJSON(), null, 4) + "</code></pre>");
                
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

