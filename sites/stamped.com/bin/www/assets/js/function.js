if(typeof(stamped) == "undefined") {
    stamped = {};
}

stamped.init = function(){
    inputManager = function(){
        var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
        
        validateEmail = function(){
            if(!emailReg.test(currentText) || currentText.indexOf(' ') > -1) {
                $('.signup form').removeClass('validated');
                console.log('not valid');
            } else {
                $('.signup form').addClass('validated');
            };
        };
        
        $('.signup input').each(function(){
            targetInput = $(this);
            defaultText = targetInput.attr('rel');
            $(this).val(defaultText);
            
            targetInput.focus(function(){
                currentText = targetInput.val();
                $('.signup form').addClass('active');
                if(currentText == defaultText) {
                    targetInput.val('')
                } else {
                    validateEmail();
                }
            });
            
            targetInput.blur(function(){
                currentText = targetInput.val();
                $('.signup form').removeClass('active');
                if(currentText.length == 0) {
                    targetInput.val(defaultText);
                };
            });
            
            targetInput.keypress(function(){
                currentText = targetInput.val();
                if(currentText.length > 3) {
                    validateEmail();
                };
            });
        });
        
        showSignup = function(){
            $('#entity .header').animate({
                'margin-top' : '0'
            }, 250);
        }
        
        
        hideSignup = function(){
            $('#entity .header').animate({
                'margin-top' : '-108px'
            }, 250);
        }
        
        $('.signup form').submit(function(){
            if($('.signup form').hasClass('validated')) {
                $.getJSON(
                    this.action + "?callback=?",
                    $(this).serialize(),
                    function (data) {
                        if (data.Status === 400) {
                            console.log('Error submitting the email address.');
                        } else { // 200
                            $('.signup').fadeOut('fast', function(){
                                $('.thanks').fadeIn('fast');
                                if($('#entity').length) {
                                    setTimeout('hideSignup()', 2000);
                                }
                            });
                        }
                    }
                );
            };
            
            event.preventDefault();
        });
        
        $('.signup-toggle').live('click', function(){
            showSignup();
            event.preventDefault();
        });
        
        $('.hide').live('click', function(){
            hideSignup();
            event.preventDefault();
        });
    }; // input manager
    
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
            //console.log('small display!');
        } else {
            $('body').removeClass('smalldisplay').addClass('talldisplay');
            //console.log('big display!');
        }
    }; // windowHeight
    
    $(window).resize(function(){
        //console.log('resize');
        windowHeight();
    });
    
    // typeInspector();
    agentInspector();
    windowHeight();
    inputManager();
    
};
