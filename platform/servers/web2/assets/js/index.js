// NOTE (travis): used to be Eli's magic.js

if (typeof(stamped) == "undefined") {
    stamped = {};
}

stamped.init = function() {
    inputManager = function() {
        var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
        
        validateEmail = function() {
            if (!emailReg.test(currentText) || currentText.indexOf(' ') > -1) {
                $('.signup form').removeClass('validated');
            } else {
                $('.signup form').addClass('validated');
            };
        };
        
        $('.signup input').each(function() {
            targetInput = $(this);
            defaultText = targetInput.attr('rel');
            $(this).val(defaultText);
            
            targetInput.focus(function() {
                currentText = targetInput.val();
                $('.signup form').addClass('active');
                if (currentText == defaultText) {
                    targetInput.val('')
                } else {
                    validateEmail();
                }
            });
            
            targetInput.blur(function() {
                currentText = targetInput.val();
                $('.signup form').removeClass('active');
                if (currentText.length == 0) {
                    targetInput.val(defaultText);
                };
            });
            
            targetInput.keypress(function() {
                currentText = targetInput.val();
                if (currentText.length > 3) {
                    validateEmail();
                };
            });
        });
        
        showSignup = function() {
            $('#entity .header').animate({
                'margin-top' : '0'
            }, 250);
        }
        
        hideSignup = function() {
            $('#entity .header').animate({
                'margin-top' : '-108px'
            }, 250);
        }
        
        $('.signup form').submit(function(event) {
            if ($('.signup form').hasClass('validated')) {
                $.getJSON(
                    this.action + "?callback=?",
                    $(this).serialize(),
                    function (data) {
                        if (data.Status === 200) {
                            $('.signup').fadeOut('fast', function() {
                                $('.thanks').fadeIn('fast');
                                if ($('#entity').length) {
                                    setTimeout('hideSignup()', 2000);
                                }
                            });
                        }
                    }
                );
            };
            
            event.preventDefault();
        });
        
        $('.signup-toggle').live('click', function(event) {
            showSignup();
            event.preventDefault();
        });
        
        $('.hide').live('click', function(event) {
            hideSignup();
            event.preventDefault();
        });
    };
    
    rotator = function() {
        time = '6000';
        speed = 'slow ';
        
        // set up the first one
        $('#tool-tipper .tooltip:first .image-active').show();
        
        updateSlide = function() {
            if ($('#tool-tipper .tooltip:last').hasClass('active')) {
                $('#tool-tipper .tooltip').removeClass('active').find('.image-active').fadeOut(speed);
                $('#tool-tipper .tooltip:first').addClass('active').find('.image-active').fadeIn(speed);
                
                $('#iphone .screen').fadeOut(speed);
                $('#iphone .screen:first').fadeIn(speed);
            } else {
                $('#tool-tipper .tooltip.active').find('.image-active').fadeOut(speed)
                $('#tool-tipper .tooltip.active').removeClass('active').next().addClass('active').find('.image-active').fadeIn(speed);
                $('#iphone .screen:visible').fadeOut(speed).next().fadeIn(speed);
            }
        }
        
        forceSlide = function(target) {
            if (!$(target).hasClass('active')) {
                $('#tool-tipper .tooltip.active').removeClass('active').find('.image-active').stop(true, true).fadeOut(speed);
                $(target).addClass('active').find('.image-active').stop(true, true).fadeIn(speed);
                targetScreen = $(target).attr('rel');
                targetScreen = parseInt(targetScreen) - 1;
                $('.screen:visible').stop(true, true).fadeOut(speed);
                $('.screen:eq('+targetScreen+')').stop(true, true).fadeIn(speed);
            };
        };

        slidechanger = setInterval(updateSlide, time);
        
        $('.tooltip').mouseenter(function() {
            clearInterval(slidechanger);
            forceSlide(this);
        });
        
        $('.tooltip').mouseleave(function() {
            slidechanger = setInterval(updateSlide, time);
        });
        
        $('.tooltip').live('click', function() {
            forceSlide(this);
        });
    };
    
    agentInspector = function() {
        agent = navigator.userAgent.toLowerCase();
        
        is_iphone  = ((agent.indexOf('iphone')!=-1));
        is_ipad    = ((agent.indexOf('ipad')!=-1));
        is_android = ((agent.indexOf('android'))!=-1);
        
        if (is_iphone) {
            $('body').addClass('mobile-iphone');
        }
        if (is_ipad) {
            $('body').addClass('mobile-ipad');
        }
        if (is_android) {
            $('body').addClass('mobile-android');
        }
    };
    
    $('.video-launcher').live('click', function(event) {    
        $('body').append('<div class="shadow"></div><div class="lightbox"><a class="close replaced" href="#">close</a><iframe src="http://player.vimeo.com/video/31275415?title=0&amp;byline=0&amp;portrait=0" width="854" height="482" frameborder="0" webkitAllowFullScreen allowFullScreen></iframe></div>');
        clearInterval(slidechanger);
        $('.shadow, .lightbox').fadeIn('slow');
        event.preventDefault();
    });
    
    $('.close').live('click', function(event) {
        $('.shadow, .lightbox').fadeOut('slow', function() {
            $('.shadow, .lightbox').remove();
        });
        slidechanger = setInterval(updateSlide, time);
        event.preventDefault();
    });
    
    var clearStutterTimer = null;
    stutterBar = function(type, message) {
        clearStutter = function() {
            $('.stutter-bar').stop('true', 'true').fadeOut('slow', function() {
                $('.stutter-bar').remove();
            });
        }
        
        clearTimeout(clearStutterTimer);
        clearStutterTimer = setTimeout(clearStutter, 1500);
        
        // check for presence and update innerHTML if stutter-bar is there. otherwise do this:
        if (type == 'success') {    
            if ($('.stutter-bar').length) {
                $('.stutter-bar').html('<span class="success text">'+message+'</span>');
            } else {
                $('body').append('<div class="stutter-bar"><span class="success text">'+message+'</span></div>');
            }
            
        } else {
            $('body').append('<div class="stutter-bar"><span class="success text">Something went very very wrong</span></div>');
        }
        
        $('.stutter-bar').fadeIn('slow');
    };
    
    slider = function() {
        sliderAnimateOff = function(target) {
            target.find('.knob').animate({
                'left' : '-2px'
            }, 175);
            target.find('.background').animate({
                'background-position-x' : '-66px'
            }, 175);
            target.removeClass('on');
        };
        
        sliderAnimateOn = function(target) {
            target.find('.knob').animate({
                'left' : '49px'
            }, 175);
            target.find('.background').animate({
                'background-position-x' : '-17px'
            }, 175);
            target.addClass('on');
        };
        
        updateParams = function() {
            updatedParams = {};
            
            $('.slider').each(function() {
                sliderID = $(this).attr('id');
                if ($(this).hasClass('on')) {
                    sliderBool = true;
                } else {
                    sliderBool = false;
                }
                
                updatedParams[sliderID] = sliderBool;
            });
            updatedParams['token'] = _TOKEN;
            $.ajax({
              type: 'POST',
              url: '/settings/alerts/update.json',
              data: updatedParams,
              success: function() {
                stutterBar('success', 'Notification settings updated successfully.');
              },
              error: function() {
                stutterBar('error', 'Something went wrong. Try again?');
              }
            });
        }
        
        $('.toggle-all').live('click', function(event) {
            if ($('.slider.on').length) {
                $('.slider').each(function() {
                    targetSetting = $(this);
                    sliderAnimateOff(targetSetting); 
                });
            } else {
                $('.slider').each(function() {
                    targetSetting = $(this);
                    sliderAnimateOn(targetSetting); 
                });
            };
            
            updateParams();
            event.preventDefault();
        });
        
        if (typeof(_PARAMS) != 'undefined') {
            $.each(_PARAMS, function(key, value) {
                if (value == true) {
                    $('#' + key).addClass('on');
                }
            });
        };
        
        $('.slider').live('click', function() {
            targetSetting = $(this);
            
            if (targetSetting.hasClass('on')) {
                sliderAnimateOff(targetSetting);
            } else {
               sliderAnimateOn(targetSetting)
            }
            
            updateParams();
        });
    };
    
    capsuleMore = function() {
        what = $('div.capsule .what');
        
        if (what.length) {
            if ($('div.capsule .feature').length) {
                featureHeight = $('div.capsule .feature').innerHeight();
            }
            
            whatWidth  = what.outerWidth();
            lineHeight = what.css('lineHeight').replace('px','');
            capLines   = 9;
            capHeight  = parseInt(capLines * lineHeight);
            
            if (what.outerHeight() > capHeight) {
                $('div.capsule .what').css({
                    'height' : capHeight + 2,
                    'overflow' : 'hidden',
                    'text-overflow' : 'clip',
                    'width' : whatWidth
                });
                $('<a class="more-toggle" href="#">Read more...</a>').insertAfter('div.capsule .what');
            }
            $('.more-toggle').click(function(event) {
                $(this).hide();
                what.css({
                    'height' : 'auto'
                });
                event.preventDefault();
            });
            
            if ($('#mobile-entity .what.contd *').length) {
                $('.what.contd').wrapInner('<div class="more-cap"/>');
                $('<a href="#" class="more-toggle-mobile">Show more information</a>').insertBefore('.more-cap');
            };
            
            $('.more-toggle-mobile').click(function(event) {
                $(this).hide();
                $('.more-cap').fadeIn();
                event.preventDefault();
            });
        }
    };
    
    // setTimeout(capsuleMore, 150);
    capsuleMore();
    
    windowHeight = function() {
        currentWindowHeight = window.innerHeight;
        smallBrowser = '700';
        
        if (currentWindowHeight < smallBrowser) {
            $('body').removeClass('talldisplay').addClass('smalldisplay');
        } else {
            $('body').removeClass('smalldisplay').addClass('talldisplay');
        }
    };
    
    $(window).resize(function() {
        windowHeight();
    });
    
    login = function(login, password) {
        params = "login=" + login + "&password=" + password + "&client_id=" + "stampedtest" + "&client_secret=" + "august1ftw";
        
        call("/v0/oauth2/login.json", {
            login : login, 
            password : password, 
            client_id : 'stampedtest', 
            client_secret : 'august1ftw', 
        }, function(data) {
            console.log("success: " + data.toSource());
            alert("success" + data.toSource());
        });
        
        return false;
    };
    
    call = function(uri, params, success) {
        var base = "http://localhost:18000";
        var url  = base + uri;
        
        window.log(url);
        
        $.ajax({
            type        : "POST", 
            url         : url, 
            data        : params, 
            success     : success, 
            crossDomain : true, 
            error       : function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.responseText)
                console.log(this.toSource());
                console.log(textStatus);
                console.log(errorThrown);
            }, 
        });
    };
    
    agentInspector();
    windowHeight();
    inputManager();
    rotator();
    slider();
    
    login("travis", "****");
};

