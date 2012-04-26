/* entity.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    var clearStutterTimer = null;
    
    var stutterBar = function(type, message) {
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
    
    var capsuleMore = function() {
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
})();

