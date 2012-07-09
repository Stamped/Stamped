/*! index.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

if (typeof(stamped) == "undefined") {
    stamped = {};
}

stamped.init = function() {
    var rotator = function() {
        time  = '6000';
        speed = 'slow';
        
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
    
    rotator();
};

