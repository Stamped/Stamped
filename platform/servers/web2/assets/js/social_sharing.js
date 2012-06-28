
var init_social_sharing = function($scope, params) {
    if (!!$scope && !!params) {
        var $tweet_buttons = $scope.find('.twitter-share-button');
        var text = "Check out this stamp of " + params.title;
        
        $tweet_buttons.attr("data-text", text);
        $tweet_buttons.attr("data-url",  params.url);
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

$(document).ready(function() {
    FB.init({
        appId      : '297022226980395', // App ID
        channelUrl : '//www.stamped.com/channel.html', // Channel File (TODO)
        status     : true, // check login status
        cookie     : true, // enable cookies to allow the server to access the session
        xfbml      : true  // parse XFBML
    });
});

