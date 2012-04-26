/* demo.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    $(document).ready(function() {
        client = new StampedClient();
        client.init();
        
        screen_name = "travis";
        
        userP = client.get_user_by_screen_name(screen_name);
        userP.done(function (user) {
            stampsP = client.get_user_stamps_by_screen_name(screen_name);
            stampsP.done(function (stamps) {
                //console.debug(stamps);
                stamps = JSON.stringify(stamps, null, 4);
                $("#data").html("<pre><code style='font-size: 12px; font-family: \"courier new\" monospace;'>" + stamps + "</code></pre>");
            });
        });
    });
})();

