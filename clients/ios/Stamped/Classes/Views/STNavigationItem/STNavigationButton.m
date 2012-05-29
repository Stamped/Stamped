//
//  STNavigationButton.m
//  Stamped
//
//  Created by Devin Doty on 5/18/12.
//
//

#import "STNavigationButton.h"

#define kButton @"nav_button.png"
#define kButtonHi @"nav_button.png"

#define kBackButton @"nav_back_button.png"
#define kBackButtonHi @"nav_back_button.png"

#define kDoneButton @"nav_done_btn.png"
#define kDoneButtonHi @"nav_done_btn.png"

#define BUTTON_BUFFER 20.0f
#define BUTTON_IMAGE_BUFFER 24.0f
#define BACK_BUTTON_BUFFER 24.0f

@interface FTNavButton : UIButton
@end
@implementation FTNavButton 

- (void)setEnabled:(BOOL)enabled {
    if (self.enabled != enabled) {
        [UIView animateWithDuration:0.15 animations:^{
            self.alpha = enabled ? 1 : 0;
        }];
    }
    [super setEnabled:enabled];    
}
@end


@interface FTImageButton : UIButton
@end
@implementation FTImageButton 

- (CGRect)imageRectForContentRect:(CGRect)contentRect {
	
	return CGRectInset(contentRect, 12.0f, 5.0f);
	return CGRectMake(floorf(contentRect.origin.x + (BUTTON_IMAGE_BUFFER/2)), contentRect.origin.y + 5.0f, floorf(contentRect.size.width - (BUTTON_IMAGE_BUFFER/2)), contentRect.size.height - 10.0f);
	
}

- (void)setEnabled:(BOOL)enabled {

    if (self.enabled != enabled) {
        [UIView animateWithDuration:0.2 animations:^{
            self.alpha = enabled ? 1 : 0;
        }];
    }
    [super setEnabled:enabled];    
}


@end

@interface FTBackButton : UIButton {}
@end
@implementation FTBackButton

- (CGRect)titleRectForContentRect:(CGRect)contentRect{
	return CGRectMake(contentRect.origin.x + 16.0f, contentRect.origin.y , contentRect.size.width, contentRect.size.height);
}
- (CGRect)imageRectForContentRect:(CGRect)contentRect {	
	return CGRectMake(contentRect.origin.x + 6.0f, contentRect.origin.y , contentRect.size.width-8.0f, contentRect.size.height);
}
@end



@implementation STNavigationButton

+ (id)buttonWithImage:(UIImage*)aImage buttonStyle:(UIBarButtonItemStyle)style {
	
	FTImageButton *button = [FTImageButton buttonWithType:UIButtonTypeCustom];
	button.adjustsImageWhenHighlighted = YES;
    button.frame = CGRectMake(0.0f, 0, floorf(aImage.size.width + BUTTON_IMAGE_BUFFER), 44);
	[button setImage:aImage forState:UIControlStateNormal];
    //[button setImage:aImage forState:UIControlStateDisabled];
	//[button setImage:aImage forState:UIControlStateHighlighted];
	[button.imageView setContentMode:UIViewContentModeScaleAspectFit];
    
    CGFloat height = 44;
    if (style==UIBarButtonItemStyleBordered) {
        UIImage *image = [[UIImage imageNamed:kButton] stretchableImageWithLeftCapWidth:13/2 topCapHeight:0.0f];
        height = image.size.height;
        [button setBackgroundImage:image forState:UIControlStateNormal];
        [button setBackgroundImage:[[UIImage imageNamed:kButtonHi] stretchableImageWithLeftCapWidth:13/2 topCapHeight:0.0f] forState:UIControlStateHighlighted];
    }
    button.frame = CGRectMake(0.0f, 0, floorf(aImage.size.width + BUTTON_IMAGE_BUFFER), height);
	
	return button;
	
}

+ (id)buttonWithTitle:(NSString*)aTitle buttonStyle:(UIBarButtonItemStyle)style {
	
	//BOOL _landscape = UIInterfaceOrientationIsLandscape([[UIApplication sharedApplication] statusBarOrientation]);
	//CGFloat barHeight = _landscape ? 32.0f : 44.0f;
	
	FTNavButton *button = [FTNavButton buttonWithType:UIButtonTypeCustom];
	//button.autoresizingMask = UIViewAutoresizingFlexibleHeight;
	[button setTitle:aTitle forState:UIControlStateNormal];
	[button.titleLabel setFont:[UIFont boldSystemFontOfSize:12]];
	[button.titleLabel setShadowOffset:CGSizeMake(0.0f, -1.0f)];
	[button.titleLabel setShadowColor:[UIColor blackColor]];
	
    UIImage *image = [[UIImage imageNamed:(style == UIBarButtonItemStyleDone) ? kDoneButton : kButton] stretchableImageWithLeftCapWidth:15.0f topCapHeight:0.0f];
	CGSize size = [aTitle sizeWithFont:[UIFont boldSystemFontOfSize:12]];
	button.frame = CGRectMake(0.0f, 0.0f, floorf(size.width + BUTTON_BUFFER), image.size.height);
	[button setBackgroundImage:[image stretchableImageWithLeftCapWidth:13/2 topCapHeight:0.0f] forState:UIControlStateNormal];
    [button setBackgroundImage:[[UIImage imageNamed:(style == UIBarButtonItemStyleDone) ? kDoneButtonHi : kButtonHi] stretchableImageWithLeftCapWidth:13/2 topCapHeight:0.0f] forState:UIControlStateHighlighted];
	
	return button;
	
}

+ (id)buttonWithTitle:(NSString *)aTitle {
	
	return [STNavigationButton buttonWithTitle:aTitle buttonStyle:UIBarButtonItemStylePlain];
	
}

+ (id)backButtonWithTitle:(NSString*)aTitle {
	
	FTBackButton *button = [FTBackButton buttonWithType:UIButtonTypeCustom];
	button.autoresizingMask = UIViewAutoresizingFlexibleHeight;
    
    CGSize size = CGSizeZero;

    if (aTitle) {
    
        [button setTitle:aTitle forState:UIControlStateNormal];
        [button.titleLabel setFont:[UIFont boldSystemFontOfSize:12]];
        [button.titleLabel setShadowOffset:CGSizeMake(0.0f, -1.0f)];
        [button.titleLabel setShadowColor:[UIColor blackColor]];
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