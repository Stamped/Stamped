
var init_social_sharing = function() {
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

