
var init_social_sharing = function($scope, params) {
    if (!!$scope && !!params) {
        var $tweet_buttons   = $scope.find('.twitter-share-button');
        var $fb_like_buttons = $scope.find('.fb-like');
        var $google_buttons  = $scope.find('.google');
        
        var text = "Check out this stamp of " + params.title;
        
        // TODO: prefer .data or .attr?
        $tweet_buttons.attr("data-text",    text);
        $tweet_buttons.attr("data-url",     params.url);
        
        $fb_like_buttons.attr("data-href",  params.url);
        $google_buttons.attr("href",        params.url);
    }
    
    // Twitter
    if (typeof(twttr) !== 'undefined' && !!twttr.widgets) {
        twttr.widgets.load();
    }
    
    // Google
    if (typeof(gapi) !== 'undefined' && !!gapi.plusone) {
        gapi.plusone.go();
    }
    
    // Facebook
    if (typeof(FB) !== 'undefined' && !!FB.XFBML) {
        FB.XFBML.parse();
        //FB.Share.renderAll();
    }
    
    if (typeof(g_init_social_sharing) !== 'undefined') {
        g_init_social_sharing();
    }
};

window.fbAsyncInit = function() {
    if (typeof(FB) !== 'undefined') {
        FB.init({
            appId       : '297022226980395', // App ID
            channelUrl  : '//www.stamped.com/channel.html', // Channel File (TODO)
            status      : true, // check login status
            cookie      : true, // enable cookies to allow the server to access the session
            xfbml       : true  // parse XFBML
            //oauth       : true
        });
        
        /*var update_fb_auth_status = function(response) {
            alert(response);
            if (response.authResponse) {
                console.log("logged in");
                var $user = document.getElementById('user-info');
                
                alert($user.html());
                
                FB.api('/me', function(response) {
                  alert(response.name);
                });
            } else {
                console.log("logged out");
            }
        };
        window.fb_login = update_fb_auth_status;
        
        FB.getLoginStatus(function(response) {
            if (response.status === 'connected') {
                // the user is logged in and has authenticated your
                // app, and response.authResponse supplies
                // the user's ID, a valid access token, a signed
                // request, and the time the access token 
                // and signed request each expire
                var uid = response.authResponse.userID;
                var accessToken = response.authResponse.accessToken;
                console.log("FB: authorized; " + uid + "; " + accessToken);
            } else if (response.status === 'not_authorized') {
                console.log("FB: not authorized");
                // the user is logged in to Facebook, 
                // but has not authenticated your app
            } else {
                console.log("FB: not logged in");
                // the user isn't logged in to Facebook.
            }
        }, true);
        
        FB.Event.subscribe('auth.statusChange', update_fb_auth_status);*/
    }
};

