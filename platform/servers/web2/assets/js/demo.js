/* demo.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    $(document).ready(function() {
        var client = new StampedClient();
        client.init();
        
        var screen_name = "travis";
        
        var userP = client.get_user_by_screen_name(screen_name);
        userP.done(function (user) {
            var user_model = new client.User(user);
            user_model.validate(user_model.attributes);
            
            //alert(user_model.idAttribute());
            //$("#data").append("<pre><code style='font-size: 12px; font-family: \"courier new\" monospace;'>" + JSON.stringify(user_model.toJSON(), null, 4) + "</code></pre>");
            
            var stampsP = client.get_user_stamps_by_screen_name(screen_name);
            stampsP.done(function (stamps) {
                //console.debug(stamps);
                //stamps = JSON.stringify(stamps, null, 4);
                var s = new client.Stamps(stamps);
                
                $("#data").append("<pre><code style='font-size: 12px; font-family: \"courier new\" monospace;'>" + JSON.stringify(s.toJSON(), null, 4) + "</code></pre>");
            });
        });
    });
})();

