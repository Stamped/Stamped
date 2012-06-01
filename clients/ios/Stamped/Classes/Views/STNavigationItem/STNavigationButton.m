//
//  STNavigationButton.m
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import "STNavigationButton.h"

#define kButton @"nav_button.png"
#define kButtonHi @"nav_button_hi.png"

#define kBackButton @"nav_back_button.png"
#define kBackButtonHi @"nav_back_button_hi.png"

#define kDoneButton @"nav_done_btn.png"
#define kDoneButtonHi @"nav_done_btn_hi.png"

#define BUTTON_BUFFER 20.0f
#define BUTTON_IMAGE_BUFFER 18.0f
#define BACK_BUTTON_BUFFER 24.0f

@interface STBackButton : UIButton
@end

@implementation STNavigationButton

+ (id)buttonWithImage:(UIImage*)aImage buttonStyle:(UIBarButtonItemStyle)style {
	
	UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
	[button setImage:aImage forState:UIControlStateNormal];
    
    CGFloat height = 44;
    if (style==UIBarButtonItemStyleBordered || style==UIBarButtonItemStyleDone) {
        
        UIImage *image = [[UIImage imageNamed:(style == UIBarButtonItemStyleDone) ? kDoneButton : kButton] stretchableImageWithLeftCapWidth:5 topCapHeight:0.0f];
        UIImage *imageHI = [[UIImage imageNamed:(style == UIBarButtonItemStyleDone) ? kDoneButtonHi : kButtonHi] stretchableImageWithLeftCapWidth:5 topCapHeight:0.0f];

        height = image.size.height;
        [button setBackgroundImage:image forState:UIControlStateNormal];
        [button setBackgroundImage:imageHI forState:UIControlStateHighlighted];
        
    }
    button.frame = CGRectMake(0, 0, ceilf(aImage.size.width + BUTTON_IMAGE_BUFFER), height);
	
	return button;
	
}

+ (id)buttonWithTitle:(NSString*)aTitle buttonStyle:(UIBarButtonItemStyle)style {

	UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
	[button setTitle:aTitle forState:UIControlStateNormal];
	[button.titleLabel setFont:[UIFont boldSystemFontOfSize:12]];
	[button.titleLabel setShadowOffset:CGSizeMake(0.0f, -1.0f)];
	[button.titleLabel setShadowColor:[UIColor colorWithWhite:0.0f alpha:0.1f]];
	
    UIImage *image = [[UIImage imageNamed:(style == UIBarButtonItemStyleDone) ? kDoneButton : kButton] stretchableImageWithLeftCapWidth:5 topCapHeight:0.0f];
    UIImage *imageHI = [[UIImage imageNamed:(style == UIBarButtonItemStyleDone) ? kDoneButtonHi : kButtonHi] stretchableImageWithLeftCapWidth:5 topCapHeight:0.0f];
	
    CGSize size = [aTitle sizeWithFont:[UIFont boldSystemFontOfSize:12]];
	button.frame = CGRectMake(0.0f, 0.0f, floorf(size.width + BUTTON_BUFFER), image.size.height);
	[button setBackgroundImage:image forState:UIControlStateNormal];
    [button setBackgroundImage:imageHI forState:UIControlStateHighlighted];
	
	return button;
	
}

+ (id)buttonWithTitle:(NSString *)aTitle {
	
	return [STNavigationButton buttonWithTitle:aTitle buttonStyle:UIBarButtonItemStylePlain];
	
}

+ (id)backButtonWithTitle:(NSString*)aTitle {
	
	STBackButton *button = [STBackButton buttonWithType:UIButtonTypeCustom];
	button.autoresizingMask = UIViewAutoresizingFlexibleHeight;
    
    CGSize size = CGSizeZero;

    if (aTitle) {
    
        [button setTitle:aTitle forState:UIControlStateNormal];
        [button.titleLabel setFont:[UIFont boldSystemFontOfSize:12]];
        [button.titleLabel setShadowOffset:CGSizeMake(0.0f, -1.0f)];
        [button.titleLabel setShadowColor:[UIColor colorWithWhite:0.0f alpha:0.1f]];
        size = [aTitle sizeWithFont:[UIFont boldSystemFontOfSize:12]];
            
    } else {
        
        UIImage *image = [UIImage imageNamed:@"back_arrow.png"];
        [button setImage:image forState:UIControlStateNormal];
        [button setImage:image forState:UIControlStateHighlighted];
        button.imageView.contentMode = UIViewContentModeCenter;
        size = image.size;
        
    }

	
	UIImage *image = [[UIImage imageNamed:kBackButton] stretchableImageWithLeftCapWidth:15.0f topCapHeight:0.0f];
	button.frame = CGRectMake(0.0f, 0, floorf(size.width + BACK_BUTTON_BUFFER), image.size.height);
	[button setBackgroundImage:image forState:UIControlStateNormal];
	[button setBackgroundImage:[[UIImage imageNamed:kBackButtonHi] stretchableImageWithLeftCapWidth:15.0f topCapHeight:0.0f] forState:UIControlStateHighlighted];

	return button;
	
}

@end


#pragma mark - STBackButton

@implementation STBackButton

- (CGRect)titleRectForContentRect:(CGRect)contentRect{
	return CGRectMake(contentRect.origin.x + 16.0f, contentRect.origin.y , contentRect.size.width, contentRect.size.height);
}

- (CGRect)imageRectForContentRect:(CGRect)contentRect {	
	return CGRectMake(contentRect.origin.x + 6.0f, contentRect.origin.y , contentRect.size.width-8.0f, contentRect.size.height);
}

@end
