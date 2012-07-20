/* signup.js
 * 
 * Copyright (c) 2011-2012 Stamped Inc.
 */

(function() {
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
    
    inputManager();
}();

