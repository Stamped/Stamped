var stamped = stamped || {};
stamped.init = function(){
    agentInspector = function(){
        agent = navigator.userAgent.toLowerCase();
        is_iphone = ((agent.indexOf('iphone')!=-1));
        is_ipad = ((agent.indexOf('ipad')!=-1));
        is_android = ((agent.indexOf('android'))!=-1);
        if (is_iphone) {
            $('body').addClass('mobile-iphone');
        };
        if (is_ipad) {
            $('body').addClass('mobile-ipad');
        };
        if (is_android) {
            $('body').addClass('mobile-android');
        };
    };

    windowHeight = function(){
        currentWindowHeight = window.innerHeight;
        smallBrowser = '700';
        
        if(currentWindowHeight < smallBrowser) {
            $('body').removeClass('talldisplay').addClass('smalldisplay');
        } else {
            $('body').removeClass('smalldisplay').addClass('talldisplay');
        }
    }; // windowHeight
    
    $(window).resize(function(){
        windowHeight();
    });
    agentInspector();
    windowHeight();
};
