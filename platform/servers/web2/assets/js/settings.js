/* settings.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
    var slider = function() {
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
    
    slider();
})();

