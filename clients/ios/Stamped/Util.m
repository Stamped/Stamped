//
//  Util.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/20/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "Util.h"

#import "EntityDetailViewController.h"
#import <QuartzCore/QuartzCore.h>
#import "STActionMenuFactory.h"
#import "STAppDelegate.h"
#import "STImageCache.h"
#import "STButton.h"
#import "STActionPair.h"
#import "UIFont+Stamped.h"
#import "STStampedAPI.h"
#import "STConfiguration.h"
#import "DDMenuController.h"
#import <RestKit/RestKit.h>
#import <CoreText/CoreText.h>
#import <QuartzCore/QuartzCore.h>
#import "STMenuController.h"
#import "STNavigationItem.h"
#import "STBadgeBarButtonItem.h"
#import "STInboxViewController.h"
#import "STRootViewController.h"
#import "STStampedAPI.h"
#import "STNavigationBar.h"

NSString* const kTwitterConsumerKey = @"kn1DLi7xqC6mb5PPwyXw";
NSString* const kTwitterConsumerSecret = @"AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU";
NSString* const kTwitterRequestTokenURL = @"https://api.twitter.com/oauth/request_token";
NSString* const kTwitterAuthorizeURL = @"https://api.twitter.com/oauth/authorize";
NSString* const kTwitterAccessTokenURL = @"https://api.twitter.com/oauth/access_token";
NSString* const kOAuthCallbackURL = @"http://www.example.com/oauth_callback";
NSString* const kTwitterScope = @"http://www.example.com/oauth_scope";
NSString* const kKeychainTwitterToken = @"Stamped Twitter";

NSString* const STUtilPopupDismissedNotification = @"UtilPopupDismissedNotification";

@interface Util ()
+ (NSString*)userReadableTimeSinceDate:(NSDate*)date shortened:(BOOL)shortened;
@end

@interface STUtilButton : UIButton

@property (nonatomic, assign) id target;
@property (nonatomic, assign) SEL selector; 
@property (nonatomic, retain) id state;
@property (nonatomic, readwrite, copy) STCallback callback;

- (void)callbackMethod:(id)view;

@end

@interface STPopUpView : UIView

@property (nonatomic, retain) UIView* button;
@property (nonatomic, retain) UIView* view;

- (id)initWithFrame:(CGRect)frame view:(UIView*)view dismissible:(BOOL)dismissible andColor:(UIColor*)color;
- (void)buttonCallback:(id)state;

@end

@interface STConfirmationDelegate : NSObject <UIActionSheetDelegate>

@property (nonatomic, readwrite, copy) void(^block)(BOOL);

@end

@interface STWarningDelegate : NSObject <UIActionSheetDelegate>

@property (nonatomic, readwrite, copy) void(^block)(void);

@end

@interface STUtilMenuDelegate : NSObject <UIAlertViewDelegate>

@property (nonatomic, readwrite, copy) void(^block)(NSString*);

@end

@interface STUtilTextInputDelegate : NSObject <UIAlertViewDelegate, UITextFieldDelegate>

- (id)initWithTextField:(UITextField*)textField;

@property (nonatomic, readwrite, copy) void(^block)(NSString*);
@property (nonatomic, readonly, retain) UITextField* textField;

@end

static STPopUpView* volatile _currentPopUp = nil;

@implementation Util


+ (NSString*)floatToHex:(CGFloat)value {
    if (value > 1 || value < 0) return nil;
    int close = MIN(255,(int)(value * 255));
    if (close < 16) {
        return [NSString stringWithFormat:@"0%x",close];
    }
    else {
        return [NSString stringWithFormat:@"%x",close];
    }
}

+ (BOOL)splitHexString:(NSString*)hexString toRGB:(CGFloat*)rgb {
    return [Util splitHexString:hexString toRed:rgb green:rgb+1 blue:rgb+2];
}

+ (BOOL)splitHexString:(NSString*)hexString toRed:(CGFloat*)red green:(CGFloat*)green blue:(CGFloat*)blue {
    if (hexString.length != 6) {
        return NO;
    }
    NSRange range;
    range.location = 0;  
    range.length = 2;
    NSString* rString = [hexString substringWithRange:range];
    range.location = 2;
    NSString* gString = [hexString substringWithRange:range];
    range.location = 4;
    NSString* bString = [hexString substringWithRange:range];
    
    unsigned int r, g, b;
    BOOL success = [[NSScanner scannerWithString:rString] scanHexInt:&r];
    success = success && [[NSScanner scannerWithString:gString] scanHexInt:&g];
    success = success && [[NSScanner scannerWithString:bString] scanHexInt:&b];
    
    if (success) {
        *red = r / 255.0f;
        *green = g / 255.0f;
        *blue = b / 255.0f;
    }
    return success;
}

+ (UIImage*)gradientImage:(UIImage*)img
           withPrimaryRed:(CGFloat)pRed
             primaryGreen:(CGFloat)pGreen
              primaryBlue:(CGFloat)pBlue
             secondaryRed:(CGFloat)sRed
           secondaryGreen:(CGFloat)sGreen
            secondaryBlue:(CGFloat)sBlue 
               startPoint:(CGPoint)start 
                 endPoint:(CGPoint)end {
    if (!img)
        return nil;
    
    CGFloat width = img.size.width;
    CGFloat height = img.size.height;
    
    UIGraphicsBeginImageContextWithOptions(img.size, NO, 0.0);
    CGContextRef context = UIGraphicsGetCurrentContext();
    
    CGContextTranslateCTM(context, 0, height);
    CGContextScaleCTM(context, 1.0, -1.0);
    
    CGContextClipToMask(context, CGRectMake(0, 0, width, height), img.CGImage);
    CGFloat colors[] = {pRed, pGreen, pBlue, 1.0, sRed, sGreen, sBlue, 1.0};
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGGradientRef gradientRef = CGGradientCreateWithColorComponents(colorSpace, colors, NULL, 2);
    CGContextDrawLinearGradient(context,
                                gradientRef,
                                start,
                                end,
                                kCGGradientDrawsAfterEndLocation);
    CGGradientRelease(gradientRef);
    CGColorSpaceRelease(colorSpace);
    UIImage* finalStamp = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    return finalStamp;
}

+ (UIImage*)gradientImage:(UIImage*)img
           withPrimaryRed:(CGFloat)pRed
             primaryGreen:(CGFloat)pGreen
              primaryBlue:(CGFloat)pBlue
             secondaryRed:(CGFloat)sRed
           secondaryGreen:(CGFloat)sGreen
            secondaryBlue:(CGFloat)sBlue {
    if (!img)
        return nil;
    
    CGFloat width = img.size.width;
    CGFloat height = img.size.height;
    CGPoint gradientStartPoint = CGPointMake(0, height);
    CGPoint gradientEndPoint = CGPointMake(width, 0);
    return [self gradientImage:img
                withPrimaryRed:pRed
                  primaryGreen:pBlue
                   primaryBlue:pGreen
                  secondaryRed:sRed
                secondaryGreen:sGreen
                 secondaryBlue:sBlue
                    startPoint:gradientStartPoint
                      endPoint:gradientEndPoint];
}

+ (UIImage*)whiteMaskedImageUsingImage:(UIImage*)img {
    CGFloat width = img.size.width;
    CGFloat height = img.size.height;
    
    UIGraphicsBeginImageContextWithOptions(img.size, NO, 0.0);
    CGContextRef context = UIGraphicsGetCurrentContext();
    
    CGContextTranslateCTM(context, 0, height);
    CGContextScaleCTM(context, 1.0, -1.0);
    
    CGContextClipToMask(context, CGRectMake(0, 0, width, height), img.CGImage);
    CGContextSetFillColorWithColor(context, [UIColor whiteColor].CGColor);
    CGContextFillRect(context, CGRectMake(0, 0, img.size.width, img.size.height));
    UIImage* maskedImage = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    return maskedImage;
}


+ (UIImage*)stampImageWithPrimaryColor:(NSString*)primary secondary:(NSString*)secondary {
    return [Util gradientImage:[UIImage imageNamed:@"stamp_46pt_texture"]
              withPrimaryColor:primary
                     secondary:secondary];
}

+ (UIImage*)creditImageForUser:(id<STUser>)user creditUser:(id<STUser>)creditedUser andSize:(STStampImageSize)stampSize {
    CGSize size = CGSizeMake(stampSize * 1.5, stampSize);
    UIImage* userStamp = [self stampImageForUser:user withSize:stampSize];
    UIImage* creditedUserStamp = [self stampImageForUser:creditedUser withSize:stampSize];
    UIGraphicsBeginImageContextWithOptions(size, NO, 0.0);
    CGContextRef context = UIGraphicsGetCurrentContext();
    
    CGContextDrawImage(context, CGRectMake(0, 0, stampSize, stampSize), creditedUserStamp.CGImage);
    CGContextDrawImage(context, CGRectMake(.5 * stampSize, 0, stampSize, stampSize), userStamp.CGImage);
    
    UIImage* result = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    return result;
}

+ (UIImage*)gradientImage:(UIImage*)image withPrimaryColor:(NSString*)primary secondary:(NSString*)secondary andStyle:(STGradientStyle)style {
    CGFloat r1, g1, b1, r2, g2, b2;
    [Util splitHexString:primary toRed:&r1 green:&g1 blue:&b1];
    
    if (secondary) {
        [Util splitHexString:secondary toRed:&r2 green:&g2 blue:&b2];
    } else {
        r2 = r1;
        g2 = g1;
        b2 = b1;
    }
    
    CGPoint start;
    CGPoint end;
    if (style == STGradientStyleHorizontal) {
        start = CGPointMake(0, image.size.height / 2);
        end = CGPointMake(image.size.width, image.size.height / 2);
    }
    else if (style == STGradientStyleVertical) {
        start = CGPointMake(image.size.width / 2, image.size.height);
        end = CGPointMake(image.size.width / 2, 0);
    }
    else {
        start = CGPointMake(0, image.size.height);
        end = CGPointMake(image.size.width, 0);
    }
    
    return [Util gradientImage:image
                withPrimaryRed:r1
                  primaryGreen:g1
                   primaryBlue:b1
                  secondaryRed:r2
                secondaryGreen:g2
                 secondaryBlue:b2 
                    startPoint:start
                      endPoint:end];
}


+ (UIImage*)gradientImage:(UIImage*)image withPrimaryColor:(NSString*)primary secondary:(NSString*)secondary {
    return [self gradientImage:image withPrimaryColor:primary secondary:secondary andStyle:STGradientStyleStamp];
}


+ (NSString*)userReadableTimeSinceDate:(NSDate*)date shortened:(BOOL)shortened {
    if (date == nil) {
        if (shortened) {
            return @"?";
        }
        else {
            return @"no timestamp";
        }
    }
    NSInteger timeSince = [[NSDate date] timeIntervalSinceDate:date];
    if (timeSince < 56) {
        if (shortened) {
            return [NSString stringWithFormat:@"%ds", timeSince];
        }
        else {
            if (timeSince < 10) {
                if (timeSince < 0) {
                    return @"%d seconds!";
                }
                else {
                    return @"just now";
                }
            }
            else {
                return [NSString stringWithFormat:@"%d seconds ago", timeSince];
            }
        }
    }
    else {
        NSInteger minutes = roundf(timeSince / 60.0);
        NSAssert1(minutes > 0, @"minutes should be > 0, was %d", minutes);
        if (minutes < 56) {
            if (shortened) {
                return [NSString stringWithFormat:@"%dm", minutes];
            }
            else {
                if (minutes == 1) {
                    return @"a minute ago";
                }
                else {
                    return [NSString stringWithFormat:@"%d minutes ago", minutes];
                }
            }
        }
        else {
            NSInteger hours = (NSInteger) roundf(minutes / 60.0);
            if (hours < 23) {
                if (shortened) {
                    return [NSString stringWithFormat:@"%dh", hours];
                }
                else {
                    if (hours == 1) {
                        return @"an hour ago";
                    }
                    else {
                        return [NSString stringWithFormat:@"%d hours ago", hours];
                    }
                }
            }
            else {
                NSInteger days = (NSInteger) roundf(hours / 24.0);
                if (days < 7) {
                    if (shortened) {
                        return [NSString stringWithFormat:@"%dd", days];
                    }
                    else {
                        if (days == 1) {
                            return @"a day ago";
                        }
                        else {
                            return [NSString stringWithFormat:@"%d days ago", days];
                        }
                    }
                }
                else {
                    NSInteger weeks = (NSInteger) roundf(days / 7.0);
                    if (weeks < 4) {
                        if (shortened) {
                            return [NSString stringWithFormat:@"%dw", weeks];
                        }
                        else {
                            if (weeks == 1) {
                                return @"a week ago";
                            }
                            else {
                                return [NSString stringWithFormat:@"%d weeks ago", weeks];
                            }
                        }
                    }
                    else {
                        NSInteger months = (NSInteger) roundf(days / 30.0);
                        if (months < 12) {
                            if (shortened) {
                                return [NSString stringWithFormat:@"%dw", weeks];
                            }
                            else {
                                if (months == 1) {
                                    return @"a month ago";
                                }
                                else {
                                    return [NSString stringWithFormat:@"%d months ago", months];
                                }
                            }
                        }
                        else {
                            NSInteger years = (NSInteger) roundf(days / 365.0);
                            if (shortened) {
                                return [NSString stringWithFormat:@"%dy", years];
                            }
                            else {
                                if (years == 1) {
                                    return @"a year ago";
                                }
                                else {
                                    return [NSString stringWithFormat:@"%d years ago", years];
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

+ (NSString*)shortUserReadableTimeSinceDate:(NSDate*)date {
    return [Util userReadableTimeSinceDate:date shortened:YES];
}

+ (NSString*)userReadableTimeSinceDate:(NSDate*)date {
    return [Util userReadableTimeSinceDate:date shortened:NO];
}

+ (NSString*)sanitizedPhoneNumberFromString:(NSString*)originalNum {
    if (!originalNum)
        return nil;
    
    NSString* num = originalNum;
    num = [[num componentsSeparatedByCharactersInSet:[NSCharacterSet punctuationCharacterSet]] componentsJoinedByString: @""];
    num = [[num componentsSeparatedByCharactersInSet:[NSCharacterSet symbolCharacterSet]] componentsJoinedByString: @""];
    num = [[num componentsSeparatedByCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]] componentsJoinedByString: @""];
    num = [[num componentsSeparatedByCharactersInSet:[NSCharacterSet letterCharacterSet]] componentsJoinedByString: @""];
    NSNumberFormatter* f = [[NSNumberFormatter alloc] init];
    [f setNumberStyle:NSNumberFormatterDecimalStyle];
    NSNumber* number = [f numberFromString:num];
    [f release];
    num = number.stringValue;
    return num;
}

// Thanks to cncool. http://stackoverflow.com/questions/389342/how-to-get-the-size-of-a-scaled-uiimage-in-uiimageview
+ (CGRect)frameForImage:(UIImage*)image inImageViewAspectFit:(UIImageView*)imageView {
    CGFloat imageRatio = image.size.width / image.size.height;
    CGFloat viewRatio = imageView.frame.size.width / imageView.frame.size.height;
    
    if (imageRatio < viewRatio) {
        CGFloat scale = imageView.frame.size.height / image.size.height;
        CGFloat width = scale * image.size.width;
        CGFloat topLeftX = (imageView.frame.size.width - width) * 0.5;
        return CGRectMake(topLeftX, 0, width, imageView.frame.size.height);
    } else {
        CGFloat scale = imageView.frame.size.width / image.size.width;
        CGFloat height = scale * image.size.height;
        CGFloat topLeftY = (imageView.frame.size.height - height) * 0.5;
        return CGRectMake(0, topLeftY, imageView.frame.size.width, height);
    }
}

// Fix for long back button titles overlapping the Stamped logo.
+ (NSString*)truncateTitleForBackButton:(NSString*)title {
    CGSize titleSize = [title sizeWithFont:[UIFont stampedBoldFontWithSize:12]];
    if (titleSize.width > 70) {
        BOOL firstLoop = YES;
        while (titleSize.width > 70) {
            if (firstLoop) {
                firstLoop = NO;
                title = [[title substringToIndex:title.length - 1] stringByAppendingString:@"…"];
            } else {
                title = [[title substringToIndex:title.length - 2] stringByAppendingString:@"…"];
            }
            // -2 because we've already appended the ellipsis.
            titleSize = [title sizeWithFont:[UIFont stampedBoldFontWithSize:12]];
        }
    }
    return title;
}

+ (NSString*)truncateTitleForNavBar:(NSString*)title {
    return [self truncateTitleForBackButton:title];
}

+ (UIView*)imageViewWithURL:(NSURL*)url andFrame:(CGRect)frame {
    NSData* data = [[NSData alloc] initWithContentsOfURL:url];
    UIImage* image = [UIImage imageWithData:data];
    if (CGRectIsNull(frame)) {
        frame = CGRectMake(0, 0, image.size.width * [Util legacyImageScale], image.size.height * [Util legacyImageScale]);
    }
    UIImageView* imageView = [[UIImageView alloc] initWithFrame:frame];
    imageView.image = image;
    [data release];
    [imageView autorelease];
    return imageView;
}

+ (UIView*)imageViewWithImage:(UIImage*)image andFrame:(CGRect)frame {
    if (CGRectIsNull(frame)) {
        frame = CGRectMake(0, 0, image.size.width, image.size.height);
    }
    UIImageView* imageView = [[[UIImageView alloc] initWithFrame:frame] autorelease];
    imageView.image = image;
    //[imageView autorelease];
    return imageView;
}

+ (UILabel*)viewWithText:(NSString*)text font:(UIFont*)font color:(UIColor*)color mode:(UILineBreakMode)mode andMaxSize:(CGSize)size {
    CGSize actualSize = [text sizeWithFont:font constrainedToSize:size lineBreakMode:mode];
    
    UILabel* label = [[UILabel alloc] initWithFrame:CGRectMake(0, 0, actualSize.width, actualSize.height)];
    label.numberOfLines = 0;
    label.lineBreakMode = mode;
    label.text = text;
    label.font = font;
    label.textColor = color;
    label.backgroundColor = [UIColor clearColor];
    return [label autorelease];
}

+ (CGSize)sizeWithText:(NSString*)text font:(UIFont*)font mode:(UILineBreakMode)mode andMaxSize:(CGSize)size {
    return [text sizeWithFont:font constrainedToSize:size lineBreakMode:mode];
}


+ (UILabel*)viewWithText:(NSString*)text 
                    font:(UIFont*)font 
                   color:(UIColor*)color
              lineHeight:(CGFloat)lineHeight
                    mode:(UILineBreakMode)mode 
              andMaxSize:(CGSize)size {
    return [self viewWithText:text font:font color:color mode:mode andMaxSize:size];
}

+ (CGSize)sizeWithText:(NSString*)text 
                  font:(UIFont*)font 
            lineHeight:(CGFloat)lineHeight 
                  mode:(UILineBreakMode)mode 
            andMaxSize:(CGSize)size {
    return [self sizeWithText:text font:font mode:mode andMaxSize:size];
}

+ (CGRect)centeredAndBounded:(CGSize)size inFrame:(CGRect)frame {
    CGFloat delta_w = frame.size.width - size.width;
    CGFloat delta_h = frame.size.height - size.height;
    if (delta_w < 0 || delta_h < 0) {
        CGFloat scale = frame.size.width / size.width;
        CGFloat scale_h = frame.size.height / size.height;
        if (scale_h < scale) {
            scale = scale_h;
        }
        size.width *= scale;
        size.height *= scale;
        delta_w = frame.size.width - size.width;
        delta_h = frame.size.height - size.height;
    }
    return CGRectMake(frame.origin.x + delta_w / 2, frame.origin.y + delta_h / 2, size.width, size.height);
}

+ (CGSize)size:(CGSize)size withScale:(CGFloat)scale {
    size.width *= scale;
    size.height *= scale;
    return size;
}

+ (UIView*)tapViewWithFrame:(CGRect)frame target:(id)target selector:(SEL)selector andMessage:(id)message {
    STUtilButton* button = [[[STUtilButton alloc] initWithFrame:frame] autorelease];
    button.selector = selector;
    button.target = target;
    button.state = message;
    [button addTarget:button action:@selector(callbackMethod:) forControlEvents:UIControlEventTouchUpInside];
    button.backgroundColor = [UIColor clearColor];
    return button;
}

+ (UIView*)tapViewWithFrame:(CGRect)frame andCallback:(STCallback)callback {
    STUtilButton* button = [[[STUtilButton alloc] initWithFrame:frame] autorelease];
    button.callback = callback;
    [button addTarget:button action:@selector(callbackMethod:) forControlEvents:UIControlEventTouchUpInside];
    button.backgroundColor = [UIColor clearColor];
    return button;
}


+ (void)setFullScreenPopUp:(UIView*)view dismissible:(BOOL)dismissible withBackground:(UIColor*)color {
    [self setFullScreenPopUp:view dismissible:dismissible animated:YES withBackground:color];
}

+ (void)setFullScreenPopUp:(UIView*)view dismissible:(BOOL)dismissible animated:(BOOL)animated withBackground:(UIColor*)color {
    UIView* window = [UIApplication sharedApplication].keyWindow;
    STPopUpView* cur = _currentPopUp;
    if (cur && cur.superview) {
        [cur removeFromSuperview];
    }
    if (view) {
        STPopUpView* popup = [[[STPopUpView alloc] initWithFrame:[Util fullscreenFrameAdjustedForStatusBar] view:view dismissible:dismissible andColor:color] autorelease];
        [window addSubview:popup];
        _currentPopUp = popup;
        if (animated) {
            popup.alpha = 0;
            [UIView animateWithDuration:.25 animations:^{
                popup.alpha = 1;
            }];
        }
        //Pointer retained solely for comparison, not ownership
    }
    else {
        _currentPopUp = nil;
    }
}

+ (CGFloat)legacyImageScale {
    return .5;
}

+ (CGFloat)imageScale {
    return 2.0;
}


+ (BOOL)oncePerUserWithID:(NSString*)userDefaultsKey {
    
    NSString* lastUserID = [[NSUserDefaults standardUserDefaults] objectForKey:userDefaultsKey];
    NSString* currentUserID = [STStampedAPI sharedInstance].currentUser.userID;
    BOOL result = currentUserID != nil && ![currentUserID isEqualToString:lastUserID];
    [[NSUserDefaults standardUserDefaults] setObject:currentUserID ? currentUserID : @" invalid userID " forKey:userDefaultsKey];
    return result;
}

+ (void)logOperationException:(NSException*)exception withMessage:(NSString*)message {
    if (message) {
        NSLog(@"%@: %@", message, exception);
    }
    else {
        NSLog(@"exception occurred! %@", exception);
    }
    NSLog(@"%@",[NSThread callStackSymbols]);
}

+ (CGRect)getAbsoluteFrame:(UIView*)view {
    return [view convertRect:view.frame toView:nil];
}

+ (void)runOperationAsynchronously:(NSOperation*)operation {
    dispatch_queue_t aQueue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    dispatch_async(aQueue, ^{
        @autoreleasepool {
            [operation start];
        }
    });
}

+ (UINavigationController*)sharedNavigationController {
    
    STAppDelegate *delegate = (STAppDelegate*) [UIApplication sharedApplication].delegate;
    STMenuController *menuController = delegate.menuController;
    if (menuController.modalViewController) {
        
        if ([menuController.modalViewController isKindOfClass:[UINavigationController class]]) {
            return (UINavigationController*)menuController.modalViewController;
        }
        
    }
    
    return (UINavigationController*)delegate.menuController.rootViewController;
    
}

+ (void)globalLoadingLock {
    //NSLog(@"GlobalLoadingLock");
    UIWindow* window = [[UIApplication sharedApplication] keyWindow];
    UIActivityIndicatorView* activityView = [[[UIActivityIndicatorView alloc] 
                                              initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhiteLarge] autorelease];
    activityView.frame = [Util centeredAndBounded:CGSizeMake(44, 44) inFrame:window.frame];
    activityView.backgroundColor = [UIColor colorWithRed:.8 green:.8 blue:.8 alpha:.4];
    
    activityView.layer.cornerRadius = 2.0;
    activityView.layer.borderColor =[UIColor colorWithRed:.8 green:.8 blue:.8 alpha:.7].CGColor;
    activityView.layer.borderWidth = 1.0;
    activityView.layer.shadowColor = [UIColor blackColor].CGColor;
    activityView.layer.shadowOpacity = .1;
    activityView.layer.shadowRadius = 1.0;
    activityView.layer.shadowOffset = CGSizeMake(0, 1);
    
    activityView.alpha = 0;
    
    [window addSubview:activityView];
    activityView.hidden = NO;
    [activityView startAnimating];
    [UIView animateWithDuration:.5 animations:^{
        activityView.alpha = 1;
    }];
    //activityView.backgroundColor = [UIColor redColor];
    window.userInteractionEnabled = NO;
}

+ (void)globalLoadingUnlock {
    //NSLog(@"GlobalLoadingUnlock");
    UIWindow* window = [[UIApplication sharedApplication] keyWindow];
    [[window.subviews lastObject] removeFromSuperview];
    window.userInteractionEnabled = YES;
}

+ (void)globalInteractionLock {
    UIWindow* window = [[UIApplication sharedApplication] keyWindow];
    window.userInteractionEnabled = NO;
}

+ (void)globalInteractionUnlock {
    UIWindow* window = [[UIApplication sharedApplication] keyWindow];
    window.userInteractionEnabled = YES;
}

+ (void)executeAsync:(void(^)(void))block {
    void(^block2)(void) = [block copy];
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        @autoreleasepool {
            block2();
            [block2 release];
        }
    });
}

+ (void)executeOnMainThread:(void(^)(void))block {
    void(^block2)(void) = [block copy];
    dispatch_async(dispatch_get_main_queue(), ^{
        @autoreleasepool {
            block2();
            [block2 release];
        }
    });
}

+ (void)executeWithDelay:(NSTimeInterval)timeInterval 
            onMainThread:(void(^)(void))block {
    void(^block2)(void) = [block copy];
    double delayInSeconds = timeInterval;
    dispatch_time_t popTime = dispatch_time(DISPATCH_TIME_NOW, delayInSeconds * NSEC_PER_SEC);
    dispatch_after(popTime, dispatch_get_main_queue(), ^(void){
        @autoreleasepool {
            block2();
            [block2 release];
        }
    });
}

+ (void)reframeView:(UIView*)view withDeltas:(CGRect)deltas {
    CGRect frame = view.frame;
    frame.origin.x += deltas.origin.x;
    frame.origin.y += deltas.origin.y;
    frame.size.width += deltas.size.width;
    frame.size.height += deltas.size.height;
    view.frame = frame;
}


+ (NSString*)titleForCategory:(NSString*)category {
    //OPTIMIZE
    NSDictionary* aliases = [NSDictionary dictionaryWithObjectsAndKeys:
                             @"Places", @"place",
                             @"Movies and TV", @"film",
                             @"Books", @"book",
                             @"Music", @"music",
                             @"Apps", @"app",
                             nil];
    NSString* result = [aliases objectForKey:category];
    if (!result) {
        result = @"Other";
    }
    return result;
}

+ (CGSize)size:(CGSize)a unionedWith:(CGSize)b
{
    return CGSizeMake(MAX(a.width, b.width), MAX(a.height, b.height));
}

+ (CGSize)packViews:(NSArray*)views padding:(CGFloat)padding vertical:(BOOL)vertical uniform:(BOOL)uniform
{
    if (uniform) {
        CGSize max = CGSizeZero;
        for (UIView* view in views)
        {
            max = [Util size:max unionedWith:view.frame.size];
        }
        CGRect frame = CGRectMake(0, 0, max.width, max.height);
        CGRect lastFrame = CGRectNull;
        for (UIView* view in views) 
        {
            view.frame = [Util centeredAndBounded:view.frame.size inFrame:frame];
            CGFloat dx = 0;
            CGFloat dy = 0;
            if (vertical) {
                dy = padding + max.height;
            }
            else {
                dx = padding + max.width;
            }
            lastFrame = frame;
            frame = CGRectOffset(frame, dx, dy);
        }
        return CGSizeMake(CGRectGetMaxX(lastFrame), CGRectGetMaxY(lastFrame));
    }
    else {
        //TODO
        return CGSizeZero;
    }
}

+ (void)offsetViews:(NSArray*)views byX:(CGFloat)dx andY:(CGFloat)dy
{
    for (UIView* view in views) 
    {
        view.frame = CGRectOffset(view.frame, dx, dy);
    }
}

+ (void)reloadStampedData {
    if ([NSThread isMainThread]) {
        UINavigationController* controller = [Util sharedNavigationController];
        id viewController = controller.topViewController;
        if ([viewController respondsToSelector:@selector(reloadStampedData)]) {
            [viewController reloadStampedData];
        }
    }
    else {
        [Util executeOnMainThread:^{
            [Util reloadStampedData];
        }];
    }
}

+ (UIImage*)imageForCategory:(NSString*)category {
    if ([category isEqualToString:@"place"]) {
        return [self imageForCategory:@"food"];
    }
    if (category)
        return [UIImage imageNamed:[NSString stringWithFormat:@"cat_icon_sDetail_%@", category.lowercaseString]];
    
    return [UIImage imageNamed:@"cat_icon_sDetail_other"];
}

+ (UIImage*)categoryIconForCategory:(NSString*)category subcategory:(NSString*)subcategory filter:(NSString*)filter andSize:(STCategoryIconSize)size {
    NSString* base = [NSString stringWithFormat:@"icon_%dpt", size];
    UIImage* image = nil;
    if (category) {
        NSString* categoryPath = [NSString stringWithFormat:@"%@_%@", base, category];
        if (subcategory) {
            NSString* subcategoryPath = [NSString stringWithFormat:@"%@_%@", categoryPath, subcategory];
            if (filter) {
                NSString* filterPath = [NSString stringWithFormat:@"%@_%@", subcategoryPath, filter];
                image = [UIImage imageNamed:filterPath];
            }
            if (!image) {
                image = [UIImage imageNamed:subcategoryPath];
            }
        }
        if (!image) {
            image = [UIImage imageNamed:categoryPath];
        }
    }
    if (!image && !([category isEqualToString:@"other"] && subcategory == nil && filter == nil)) {
        image = [self categoryIconForCategory:@"other" subcategory:nil filter:nil andSize:size];
    }
    return image;
}

+ (UIImage*)stampImageForUser:(id<STUser>)user withSize:(STStampImageSize)size {
    return [Util gradientImage:[UIImage imageNamed:[NSString stringWithFormat:@"stamp_%dpt_texture", size]]
              withPrimaryColor:user.primaryColor
                     secondary:user.secondaryColor];
}


+ (UIImage*)invertedStampImageForUser:(id<STUser>)user withSize:(STStampImageSize)size {
    return [Util whiteMaskedImageUsingImage:[UIImage imageNamed:[NSString stringWithFormat:@"stamp_%dpt_texture", size]]];
}


+ (UIImage*)inboxTodoCategoryImage:(NSString*)category {
    if (category)
        return [UIImage imageNamed:[NSString stringWithFormat:@"cat_icon_inbox-todo_%@", category.lowercaseString]];
    
    return [UIImage imageNamed:@"cat_icon_inbox-todo_other"];
}

+ (UIImage*)highlightedInboxTodoCategoryImage:(NSString*)category {
    if (category)
        return [UIImage imageNamed:[NSString stringWithFormat:@"cat_icon_inbox-todo_%@_white", category.lowercaseString]];
    
    return [UIImage imageNamed:@"cat_icon_inbox-todo_other_white"];
}

+ (NSString*)profileImageURLForUser:(id<STUser>)user withSize:(STProfileImageSize)size {
    if (user.imageURL) {
        NSString* original = [NSString stringWithFormat:@"/users/%@.jpg", user.screenName.lowercaseString];
        NSString* replacement =
        [NSString stringWithFormat:@"/users/%@-%dx%d.jpg",
         user.screenName.lowercaseString, size, size];
        NSString* URL = [user.imageURL stringByReplacingOccurrencesOfString:original withString:replacement];
        return URL;
    }
    
    return [NSString stringWithFormat:@"http://static.stamped.com/users/%@-144x144.jpg",
            user.screenName.lowercaseString];
}

+ (void)confirmWithMessage:(NSString*)message action:(NSString*)action destructive:(BOOL)destructive withBlock:(void(^)(BOOL))block {
    STConfirmationDelegate* delegate = [[[STConfirmationDelegate alloc] init] autorelease];
    delegate.block = block;
    UIActionSheet* sheet;
    if (destructive) {
        sheet = [[[UIActionSheet alloc] initWithTitle:message
                                             delegate:delegate
                                    cancelButtonTitle:@"Cancel"
                               destructiveButtonTitle:action
                                    otherButtonTitles:nil] autorelease];
    }
    else {
        sheet = [[[UIActionSheet alloc] initWithTitle:message
                                             delegate:delegate
                                    cancelButtonTitle:@"Cancel"
                               destructiveButtonTitle:nil
                                    otherButtonTitles:action, nil] autorelease];
    }
    sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    [sheet showInView:[UIApplication sharedApplication].keyWindow];
}

+ (void)warnWithMessage:(NSString*)message andBlock:(void(^)(void))block {
    STWarningDelegate* delegate = [[[STWarningDelegate alloc] init] autorelease];
    delegate.block = block;
    UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:message
                                                        delegate:delegate
                                               cancelButtonTitle:nil
                                          destructiveButtonTitle:nil
                                               otherButtonTitles:@"Ok", nil] autorelease];
    sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
    [sheet showInView:[UIApplication sharedApplication].keyWindow];
}

+ (void)menuWithTitle:(NSString*)title 
              message:(NSString*)message 
              choices:(NSArray*)strings 
             andBlock:(void(^)(NSString* string))block {
    STUtilMenuDelegate* delegate = [[[STUtilMenuDelegate alloc] init] autorelease];
    delegate.block = block;
    UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:title
                                                     message:message 
                                                    delegate:delegate 
                                           cancelButtonTitle:@"Cancel" 
                                           otherButtonTitles: nil] autorelease];
    for (NSString* string in strings) {
        [alert addButtonWithTitle:string];
    }
    [alert show];
}

+ (CGRect)relativeFrameForView:(UIView*)view inAncestorView:(UIView*)ancestor {
    UIView* cur = view.superview;
    CGRect frame = view.frame;
    while (cur != nil) {
        if (cur == ancestor) {
            break;
        }
        else {
            frame = CGRectOffset(frame, cur.frame.origin.x, cur.frame.origin.y);
        }
        cur = cur.superview;
    }
    return frame;
}

+ (NSString*)trackLengthString:(NSInteger)length {
    NSInteger seconds = length % 60;
    NSString* secondsString = seconds > 9 ? [NSString stringWithFormat:@"%d", seconds] : [NSString stringWithFormat:@"0%d", seconds]; 
    return [NSString stringWithFormat:@"%d:%@", length / 60, secondsString];
}

+ (CAGradientLayer*)addGradientToLayer:(CALayer*)layer withColors:(NSArray*)colors vertical:(BOOL)vertical {
    CAGradientLayer* gradient = [CAGradientLayer layer];
    gradient.anchorPoint = CGPointMake(0, 0);
    gradient.position = CGPointMake(0, 0);
    gradient.contentsScale = [[UIScreen mainScreen] scale];
    if (!vertical) {
        gradient.startPoint = CGPointMake(0,.5);
        gradient.endPoint = CGPointMake(1,.5);
    }
    NSMutableArray* cgColors = [NSMutableArray array];
    for (UIColor* color in colors) {
        [cgColors addObject:(id)color.CGColor];
    }
    gradient.bounds = layer.bounds;
    gradient.cornerRadius = layer.cornerRadius;
    gradient.colors = cgColors;
    [layer insertSublayer:gradient atIndex:0];
    return gradient;
}

+ (UIImageView*)profileImageViewForUser:(id<STUser>)user withSize:(NSInteger)size {
    
    UIImageView* imageView = [[[UIImageView alloc] initWithFrame:CGRectMake(0, 0, size, size)] autorelease];
    imageView.layer.borderWidth = 1.5;
    imageView.backgroundColor = [UIColor colorWithWhite:.9 alpha:1];
    imageView.layer.borderColor = [UIColor whiteColor].CGColor;
    imageView.layer.shadowOffset = CGSizeMake(0,1);
    imageView.layer.shadowOpacity = .3;
    imageView.layer.shadowRadius = 1;
    imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:imageView.bounds].CGPath;
    
    if (user) {
        size = size * [UIScreen mainScreen].scale;
        STProfileImageSize profileSize = STProfileImageSize24;
        if (size > profileSize) {
            profileSize = STProfileImageSize48;
            if (size > profileSize) {
                profileSize = STProfileImageSize60;
                if (size > profileSize) {
                    profileSize = STProfileImageSize96;
                    if (size > profileSize) {
                        profileSize = STProfileImageSize144;
                    }
                }
            }
        }
        UIImage* cachedImage = nil;
        if (IS_CURRENT_USER(user.userID)) {
            cachedImage = [[STStampedAPI sharedInstance] currentUserImageForSize:profileSize];
        }
        if (!cachedImage) {
            cachedImage = [[STImageCache sharedInstance] cachedUserImageForUser:user size:profileSize];
        }
        if (cachedImage) {
            imageView.image = cachedImage;
        }
        else {
            [[STImageCache sharedInstance] userImageForUser:user size:profileSize andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
                imageView.image = image;
            }];
        }
    }
    return imageView;
    
}

/*
 + (UIView*)profileImageViewForUser:(id<STUser>)user 
 size:(STProfileImageSize)size 
 andAction:(id<STAction>)action 
 withContext:(STActionContext*)context {
 UIImageView* imageView = [[[UIImageView alloc] initWithFrame:CGRectMake(0, 0, size, size)] autorelease];
 imageView.layer.borderWidth = 1.5;
 imageView.backgroundColor = [UIColor colorWithWhite:.9 alpha:1];
 imageView.layer.borderColor = [UIColor whiteColor].CGColor;
 imageView.layer.shadowOffset = CGSizeMake(0,2);
 imageView.layer.shadowOpacity = .3;
 imageView.layer.shadowRadius = 2;
 imageView.clipsToBounds = YES;
 UIView* activeView = [[[UIView alloc] initWithFrame:imageView.frame] autorelease];
 activeView.backgroundColor = [UIColor colorWithRed:0 green:0 blue:.3 alpha:.3];
 
 UIImage* cachedImage = [[STImageCache sharedInstance] cachedUserImageForUser:user size:size];
 if (cachedImage) {
 imageView.image = cachedImage;
 STActionPair* pair = [[STActionPair actionPairWithAction:action andContext:context] retain];
 STButton* button = [[STButton alloc] initWithFrame:imageView.frame 
 normalView:[[[UIView alloc] initWithFrame:imageView.frame] autorelease]
 activeView:activeView
 target:pair andAction:@selector(executeActionWithArg:)];
 [imageView addSubview:button];
 }
 else {
 [[STImageCache sharedInstance] userImageForUser:user size:size andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
 imageView.image = image;
 STActionPair* pair = [[STActionPair actionPairWithAction:action andContext:context] retain];
 STButton* button = [[STButton alloc] initWithFrame:imageView.frame 
 normalView:[[[UIView alloc] initWithFrame:imageView.frame] autorelease]
 activeView:activeView
 target:pair andAction:@selector(executeActionWithArg:)];
 [imageView addSubview:button];
 }];
 }
 return imageView;
 }
 */
+ (UIView*)badgeViewForGenre:(NSString*)genre {
    UIView* result = nil;
    NSString* imagePath = nil;
    if ([genre isEqualToString:@"entity_first_stamp"]) {
        imagePath = @"badge_1stStamped";
    }
    else if ([genre isEqualToString:@"friends_first_stamp"]) {
        imagePath = @"badge_1stFriends";
    }
    else if ([genre isEqualToString:@"user_first_stamp"]) {
        imagePath = @"badge_1stYou";
    }
    if (imagePath) {
        result = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:imagePath]] autorelease];
    }
    return result;
}

+ (CGRect)fullscreenFrame {
    return [[UIScreen mainScreen] bounds];
}

+ (CGRect)fullscreenFrameAdjustedForStatusBar {
    return [[UIScreen mainScreen] applicationFrame];
}

+ (CGRect)navigatedViewFrame {
    CGRect almostFullscreen = [Util fullscreenFrameAdjustedForStatusBar];
    CGFloat height = [Util sharedNavigationController].navigationBar.frame.size.height;
    almostFullscreen.size.height -= height;
    almostFullscreen.origin.y += height;
    return almostFullscreen;
}

+ (CGRect)standardFrameWithNavigationBar:(BOOL)navigationBar {
    CGRect frame;
    if (navigationBar) {
        frame = [Util navigatedViewFrame];
    }
    else {
        frame = [Util fullscreenFrameAdjustedForStatusBar];
    }
    frame.origin.x = 0;
    frame.origin.y = 0;
    return frame;
}

+ (NSMutableDictionary*)sparseDictionaryForObject:(id)object andKeyPaths:(NSArray*)keyPaths {
    NSMutableDictionary* dictionary = [NSMutableDictionary dictionary];
    for (NSString* keyPath in keyPaths) {
        id value = [object valueForKeyPath:keyPath];
        if (value) {
            [dictionary setObject:value forKey:keyPath];
        }
    }
    return dictionary;
}

+ (NSString*)largeProfileImageURLWithUser:(id<STUser>)userDetail {
    if (userDetail.imageURL)
        return userDetail.imageURL;
    return [NSString stringWithFormat:@"http://static.stamped.com/users/%@.jpg", userDetail.screenName.lowercaseString];
}

+ (NSArray*)categories {
    NSArray* categories = [NSArray arrayWithObjects:
                           @"food",
                           @"book",
                           @"music",
                           @"film",
                           @"download",
                           nil];
    return categories;
}

+ (NSString*)entityImageURLForEntityDetail:(id<STEntityDetail>)entityDetail {
    return [self entityImageURLForEntity:entityDetail];
}

+ (NSString*)entityImageURLForEntity:(id<STEntity>)entity {
    NSString* imagePath = nil;
    if (entity.images && [entity.images count] > 0) {
        id<STImageList> imageList = [entity.images objectAtIndex:0];
        if (imageList.sizes.count > 0) {
            id<STImage> image = [imageList.sizes objectAtIndex:0];
            imagePath = image.url;
        }
    }
    return imagePath;
}

+ (CGFloat)lineHeightForFont:(UIFont*)font {
    return font.lineHeight;
}

+ (void)textInputWithDefault:(NSString*)string andCallback:(void (^)(NSString* value))block {
    UITextField *passwordField = [[UITextField alloc] initWithFrame:CGRectMake(16,83,252,25)];
    STUtilTextInputDelegate* delegate = [[[STUtilTextInputDelegate alloc] initWithTextField:passwordField] autorelease];
    delegate.block = block;
    UIAlertView *passwordAlert = [[UIAlertView alloc] initWithTitle:@"Enter Value" message:@"\n\n\n"
                                                           delegate:delegate cancelButtonTitle:NSLocalizedString(@"Cancel",nil) otherButtonTitles:NSLocalizedString(@"OK",nil), nil];
    
    passwordField.font = [UIFont systemFontOfSize:18];
    passwordField.backgroundColor = [UIColor whiteColor];
    passwordField.keyboardAppearance = UIKeyboardAppearanceAlert;
    passwordField.delegate = delegate;
    passwordField.text = string;
    passwordField.font = [UIFont stampedFontWithSize:14];
    [passwordField becomeFirstResponder];
    [passwordAlert addSubview:passwordField];
    
    [passwordAlert show];
    [passwordAlert release];
    [passwordField release];
}

+ (void)_homeButtonClicked:(id)button {
    
    [((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController showLeftController:YES];
    
}

+ (void)addHomeButtonToController:(UIViewController*)controller withBadge:(BOOL)flag {
    
    STBadgeBarButtonItem *button = [[STBadgeBarButtonItem alloc] initWithImage:[UIImage imageNamed:@"menu_list_icon.png"] style:UIBarButtonItemStyleBordered target:self action:@selector(_homeButtonClicked:)];
    controller.navigationItem.leftBarButtonItem = button;
    
    [button release];
    
}

+ (void)setTitle:(NSString*)title forController:(UIViewController*)controller {
    STNavigationBar* bar = (id)[Util sharedNavigationController].navigationBar;
    bar.title = title;
}

+ (STCancellation*)addUnreadBadgeToView:(UIView*)view origin:(CGPoint)origin {
    return [[STStampedAPI sharedInstance] unreadCountWithCallback:^(id<STActivityCount> count, NSError *error, STCancellation *cancellation) {
        if (count && count.numberUnread.integerValue >0) {
            UIView* countView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 19, 19)] autorelease];
            countView.userInteractionEnabled = NO;
            NSString* badgeString;
            if (count.numberUnread.integerValue < 100) {
                badgeString = [NSString stringWithFormat:@"%d", count.numberUnread.integerValue ];
            }
            else {
                badgeString = @"99+";
            }
            UILabel* label = [Util viewWithText:badgeString
                                           font:[UIFont boldSystemFontOfSize:10]
                                          color:[UIColor whiteColor]
                                           mode:UILineBreakModeTailTruncation
                                     andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
            label.frame = CGRectMake(ceilf((countView.bounds.size.width-label.bounds.size.width)/2), floorf((countView.bounds.size.height-label.bounds.size.height)/2), label.bounds.size.width, label.bounds.size.height);
            label.userInteractionEnabled = NO;
            label.shadowOffset = CGSizeMake(0.0f, -1.0f);
            label.shadowColor = [UIColor colorWithWhite:0.0f alpha:0.2f];
            
            [countView addSubview:label];
            [Util reframeView:countView withDeltas:CGRectMake(26, -5, 0, 0)];
            countView.layer.borderWidth = 1;
            countView.layer.borderColor = [UIColor whiteColor].CGColor;
            countView.layer.cornerRadius = countView.frame.size.width / 2;
            countView.layer.shadowPath = [UIBezierPath bezierPathWithRoundedRect:countView.bounds cornerRadius:(countView.bounds.size.width/2)].CGPath;
            countView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
            countView.layer.shadowRadius = 2.0f;
            countView.layer.shadowOpacity = 0.4f;
            
            CAGradientLayer *layer = [Util addGradientToLayer:countView.layer
                                                   withColors:[NSArray arrayWithObjects:
                                                               [UIColor colorWithRed:0.890f green:0.364f blue:0.2588f alpha:1.0f],
                                                               [UIColor colorWithRed:0.717f green:0.207f blue:0.1019f alpha:1.0f],
                                                               nil]
                                                     vertical:YES];
            CGRect frame = layer.frame;
            frame = CGRectInset(frame, .5, .5);
            layer.frame = frame;
            
            [view addSubview:countView];
        }
    }];
}

+ (void)_createStampButtonClicked:(id)notImportant {
    
    [((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController showRightController:YES];
    
}

+ (void)addCreateStampButtonToController:(UIViewController*)controller {
    
    id<STUser> user = [STStampedAPI sharedInstance].currentUser;
    
    UIImage* baseImage = [UIImage imageNamed:@"nav_btn_createStamp_color"];
    UIImage* normalImage = [Util gradientImage:baseImage withPrimaryColor:user.primaryColor secondary:user.secondaryColor];
    UIImage* activeImage = [Util whiteMaskedImageUsingImage:baseImage];
    
    UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
    button.frame = CGRectMake(0.0f, 0.0f, 44.0f, 44.0f);
    [button setImage:normalImage forState:UIControlStateNormal];
    [button setImage:activeImage forState:UIControlStateHighlighted];
    [button addTarget:self action:@selector(_createStampButtonClicked:) forControlEvents:UIControlEventTouchUpInside];
    
    UIImageView *overlay = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"nav_btn_createStamp_overlay"]];
    [button addSubview:overlay];
    [overlay release];
    
    CGRect frame = overlay.frame;
    frame.origin.x = floorf((button.bounds.size.width-frame.size.width)/2);
    frame.origin.y = floorf((button.bounds.size.height-frame.size.height)/2);
    overlay.frame = frame;
    
    UIBarButtonItem *item = [[UIBarButtonItem alloc] initWithCustomView:button];
    controller.navigationItem.rightBarButtonItem = item;
    [item release];
    
}

+ (void)_configurationButtonClicked:(id)notImportant {
    [[Util sharedNavigationController] pushViewController:[STConfiguration sharedInstance].controller animated:YES];
}

+ (void)addConfigurationButtonToController:(UIViewController*)controller {
    
    controller.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Configuration"
                                                                                     style:UIBarButtonItemStyleDone
                                                                                    target:self 
                                                                                    action:@selector(_configurationButtonClicked:)] autorelease];
}

+ (NSNumber*)numberFromString:(NSString*)string {
    NSNumberFormatter* f = [[[NSNumberFormatter alloc] init] autorelease];
    [f setNumberStyle:NSNumberFormatterDecimalStyle];
    return [f numberFromString:string];
}

+ (void)appendView:(UIView*)child toParentView:(UIView*)parent {
    CGFloat height = parent.frame.size.height;
    [Util reframeView:child withDeltas:CGRectMake(0, height, 0, 0)];
    CGRect parentFrame = parent.frame;
    parentFrame.size.height = CGRectGetMaxY(child.frame);
    parent.frame = parentFrame;
    [parent addSubview:child];
}

+ (NSString*)_baseCache {
    NSArray* paths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
    return [paths objectAtIndex:0];
}

+ (NSString*)_cachePrefix {
    return @"com.stamped.cache.";
}

+ (NSURL*)_cacheForVersion:(NSString*)version {
    return [[NSURL fileURLWithPath:[self _baseCache]] URLByAppendingPathComponent:[NSString stringWithFormat:@"%@%@",[self _cachePrefix], version]];
}

+ (void)removeOldCacheDirectories {
    NSString* current = [self cacheDirectory].lastPathComponent;
    NSArray* items = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:[self _baseCache] error:nil];
    for (NSString* item in items) {
        if ([item hasPrefix:[self _cachePrefix]] && ![item isEqualToString:current]) {
            NSURL* url = [[NSURL fileURLWithPath:[self _baseCache]] URLByAppendingPathComponent:item];
            //NSLog(@"Removing old cached: %@", item);
            NSError* error = nil;
            [[NSFileManager defaultManager] removeItemAtURL:url error:&error];
            if (error) {
                //NSLog(@"Removal failed!: %@", error);
            }
        }
    }
}

+ (NSString*)versionString {
    NSDictionary *appInfo = [[NSBundle mainBundle] infoDictionary];
    return [NSString stringWithFormat:@"%@.%@", 
            [appInfo objectForKey:@"CFBundleShortVersionString"], 
            [appInfo objectForKey:@"CFBundleVersion"]];
}

+ (NSURL *)cacheDirectory {
    NSString *versionStr = [self versionString];
    return [self _cacheForVersion:versionStr];
}

+ (BOOL)isOffline {
    RKClient* client = [RKClient sharedClient];
    return client.reachabilityObserver.isReachabilityDetermined && !client.isNetworkReachable;
}

+ (void)launchFirstRun {
    NSLog(@"showing first run");
    STAppDelegate* appDelegate = (id)[UIApplication sharedApplication].delegate;
    [appDelegate.menuController showWelcome:NO];
}


+ (CGSize)sizeForString:(NSAttributedString *)inString thatFits:(CGSize)inSize
{
    CTFramesetterRef theFramesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)inString);
    if (theFramesetter == NULL)
    {
        NSLog(@"Could not create CTFramesetter with %@", inString);
        return(CGSizeZero);
    }
    
    CGSize theSize = CTFramesetterSuggestFrameSizeWithConstraints(theFramesetter, (CFRange){}, NULL, inSize, NULL);
    CFRelease(theFramesetter);
    
    if (inSize.width < CGFLOAT_MAX && inSize.height == CGFLOAT_MAX)
    {
        //theSize.width = inSize.width;
    }
    
    // On iOS 5.0 the function `CTFramesetterSuggestFrameSizeWithConstraints` returns rounded float values (e.g. "15.0").
    // Prior to iOS 5.0 the function returns float values (e.g. "14.7").
    // Make sure the return value for `sizeForString:thatFits:" is equal for both versions:
    theSize = (CGSize){ .width = ceilf(theSize.width), .height = ceilf(theSize.height) };
    
    return(theSize);
}

+ (CGFloat)endForString:(NSAttributedString*)string withSize:(CGSize)bounds {
    // Create a path to render text in
    // create the framesetter and render text
    CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)string); 
    CGSize size = CTFramesetterSuggestFrameSizeWithConstraints(framesetter, (CFRange){}, NULL, bounds, NULL);
    CGMutablePathRef path = CGPathCreateMutable();
    CGPathAddRect(path, NULL, CGRectMake(0, 0, bounds.width, size.height) );
    
    CTFrameRef frame = CTFramesetterCreateFrame(framesetter,
                                                CFRangeMake(0, [string length]), path, NULL);
    CFArrayRef lines = CTFrameGetLines(frame);
    CGFloat result = 0;
    if (CFArrayGetCount(lines) != 0 ) {
        CTLineRef lastLine = CFArrayGetValueAtIndex(lines, CFArrayGetCount(lines)-1);
        CFRange range = CTLineGetStringRange(lastLine);
        if (range.length > 0) {
            //OPTIMIZE
            UIGraphicsBeginImageContextWithOptions(CGSizeMake(bounds.width, 40), NO, 0.0);
            CGContextRef context = UIGraphicsGetCurrentContext();
            CGRect imageBounds = CTLineGetImageBounds(lastLine, context);
            UIGraphicsEndImageContext();
            result = imageBounds.size.width;
        }
    }
    // Clean up
    CFRelease(frame);
    CFRelease(path);
    CFRelease(framesetter);
    return result;
}

+ (NSAttributedString *)attributedStringForString:(NSString*)aString 
                                       references:(NSArray<STActivityReference>*)references 
                                             font:(UIFont*)aFont 
                                            color:(UIColor*)aColor 
                                    referenceFont:(UIFont*)referenceFont 
                                   referenceColor:(UIColor*)referenceColor
                                       lineHeight:(CGFloat)lineHeight 
                                           indent:(CGFloat)indent 
                                          kerning:(CGFloat)kerning {
    NSAttributedString* original = [self attributedStringForString:aString font:aFont color:aColor lineHeight:lineHeight indent:indent kerning:kerning];
    NSMutableAttributedString* copy = [[[NSMutableAttributedString alloc] initWithAttributedString:original] autorelease];
    id fontAttr = [NSMakeCollectable(CTFontCreateWithName((CFStringRef)referenceFont.fontName, referenceFont.pointSize, NULL)) autorelease];
    id foregroundColorAttr = (id)(referenceColor ? referenceColor.CGColor : [UIColor blackColor].CGColor);
    NSDictionary* attributes = [NSDictionary dictionaryWithObjectsAndKeys:
                                fontAttr, kCTFontAttributeName,
                                foregroundColorAttr, kCTForegroundColorAttributeName,
                                nil];
    for (id<STActivityReference> reference in references) {
        if (reference.indices.count == 2) {
            NSInteger start = [[reference.indices objectAtIndex:0] integerValue];
            NSInteger end = [[reference.indices objectAtIndex:1] integerValue];
            if (start >= 0 && end > start && end <= aString.length) {
                [copy setAttributes:attributes range:NSMakeRange(start, end - start)];
            }
        }
    }
    return copy;
}

+ (NSAttributedString *)attributedStringForString:(NSString *)aString 
                                             font:(UIFont *)aFont 
                                            color:(UIColor *)aColor 
                                       lineHeight:(CGFloat)lineHeight 
                                           indent:(CGFloat)indent 
                                        alignment:(CTTextAlignment)alignment
                                  extraAttributes:(NSDictionary*)attributes {    
    if (!aString)
        return nil;
    
    id fontAttr = [NSMakeCollectable(CTFontCreateWithName((CFStringRef)aFont.fontName, aFont.pointSize, NULL)) autorelease];
    id foregroundColorAttr = (id)(aColor ? aColor.CGColor : [UIColor blackColor].CGColor);
    id paragraphStyleAttr = ((^ {
        
        CTParagraphStyleSetting paragraphStyles[] = (CTParagraphStyleSetting[]){
            (CTParagraphStyleSetting){ kCTParagraphStyleSpecifierAlignment, sizeof(alignment), &alignment },
            (CTParagraphStyleSetting){ kCTParagraphStyleSpecifierLineHeightMultiple, sizeof(float_t), (float_t[]){ 0.01f } },
            (CTParagraphStyleSetting){ kCTParagraphStyleSpecifierMinimumLineHeight, sizeof(float_t), (float_t[]){ lineHeight } },
            (CTParagraphStyleSetting){ kCTParagraphStyleSpecifierMaximumLineHeight, sizeof(float_t), (float_t[]){ lineHeight } },
            (CTParagraphStyleSetting){ kCTParagraphStyleSpecifierLineSpacing, sizeof(float_t), (float_t[]){ 0.0f } },
            (CTParagraphStyleSetting){ kCTParagraphStyleSpecifierMinimumLineSpacing, sizeof(float_t), (float_t[]){ 0.0f } },
            (CTParagraphStyleSetting){ kCTParagraphStyleSpecifierMaximumLineSpacing, sizeof(float_t), (float_t[]){ 0.0f } },
            (CTParagraphStyleSetting){ kCTParagraphStyleSpecifierFirstLineHeadIndent, sizeof(float_t), (float_t[]){ indent } },
            (CTParagraphStyleSetting){ kCTParagraphStyleSpecifierLineBreakMode, sizeof(CTLineBreakMode), (CTLineBreakMode[]){ kCTLineBreakByWordWrapping } },
        };
        
        CTParagraphStyleRef paragraphStyleRef = CTParagraphStyleCreate(paragraphStyles, sizeof(paragraphStyles) / sizeof(CTParagraphStyleSetting));
        return [NSMakeCollectable(paragraphStyleRef) autorelease];
        
    })());
    
    NSMutableDictionary* attrs = [NSMutableDictionary dictionaryWithObjectsAndKeys:
                                  fontAttr, kCTFontAttributeName,
                                  foregroundColorAttr, kCTForegroundColorAttributeName,
                                  paragraphStyleAttr, kCTParagraphStyleAttributeName,
                                  nil];
    [attrs addEntriesFromDictionary:attributes];
    NSAttributedString *returnedString = [[[NSAttributedString alloc] initWithString:aString attributes:attrs] autorelease];
    return returnedString;
    
}


+ (NSAttributedString *)attributedStringForString:(NSString *)aString 
                                             font:(UIFont *)aFont 
                                            color:(UIColor *)aColor 
                                       lineHeight:(CGFloat)lineHeight 
                                           indent:(CGFloat)indent {
    return [self attributedStringForString:aString
                                      font:aFont 
                                     color:aColor
                                lineHeight:lineHeight
                                    indent:indent 
                                 alignment:kCTLeftTextAlignment
                           extraAttributes:[NSDictionary dictionary]];
}


+ (NSAttributedString *)attributedStringForString:(NSString *)aString 
                                             font:(UIFont *)aFont 
                                            color:(UIColor *)aColor 
                                       lineHeight:(CGFloat)lineHeight 
                                           indent:(CGFloat)indent 
                                          kerning:(CGFloat)kerning {
    return [self attributedStringForString:aString
                                      font:aFont 
                                     color:aColor 
                                lineHeight:lineHeight
                                    indent:indent
                                 alignment:kCTLeftTextAlignment
                           extraAttributes:[NSDictionary dictionaryWithObject:[NSNumber numberWithFloat:kerning] forKey:(id)kCTKernAttributeName]];
}
//
//[NSNumber numberWithFloat:5.0],kCTKernAttributeName,

+ (void)drawAttributedString:(NSAttributedString*)string atPoint:(CGPoint)origin withWidth:(CGFloat)width andMaxHeight:(CGFloat)height {
    CGContextRef context = UIGraphicsGetCurrentContext();
    CGContextSaveGState(context);
    CGSize size = [Util sizeForString:string thatFits:CGSizeMake(width, height)];
    
    size.width = width;
    // Flip the coordinate system
    CGContextSetTextMatrix(context, CGAffineTransformIdentity);
    CGContextTranslateCTM(context, origin.x, origin.y + size.height);
    CGContextScaleCTM(context, 1.0, -1.0);
    
    // Create a path to render text in
    CGMutablePathRef path = CGPathCreateMutable();
    CGPathAddRect(path, NULL, CGRectMake(0, 0, size.width, size.height) );
    
    // create the framesetter and render text;
    CTFramesetterRef framesetter = CTFramesetterCreateWithAttributedString((CFAttributedStringRef)string); 
    CTFrameRef frame = CTFramesetterCreateFrame(framesetter,
                                                CFRangeMake(0, [string length]), path, NULL);
    
    CTFrameDraw(frame, context);
    
    // Clean up
    CFRelease(frame);
    CFRelease(path);
    CFRelease(framesetter);
    CGContextRestoreGState(context);
}


+ (void)setTopRightForView:(UIView*)view toPoint:(CGPoint)point {
    CGRect frame = view.frame;
    frame.origin.x = point.x - frame.size.width;
    frame.origin.y = point.y;
    view.frame = frame;
}

+ (void)setBottomLeftForView:(UIView*)view toPoint:(CGPoint)point {
    CGRect frame = view.frame;
    frame.origin.x = point.x;
    frame.origin.y = point.y - frame.size.height;
    view.frame = frame;
}

+ (CGRect)scaledRectWithRect:(CGRect)original andScale:(CGFloat)scale {
    CGFloat newWidth = original.size.width * scale;
    CGFloat newHeight = original.size.height * scale;
    CGFloat deltaX = -(newWidth - original.size.width) / 2.0;
    CGFloat deltaY = -(newHeight - original.size.height) / 2.0;
    return CGRectMake(original.origin.x + deltaX, original.origin.y + deltaY, newWidth, newHeight);
}

+ (NSString*)userStringWithBackendType:(NSString*)string andArticle:(BOOL)withArticle {
    //OPTIMIZE
    NSString* article = @"a";
    NSString* noun = string;
    if ([string isEqualToString:@"tv"]) {
        noun = @"tv show";
    }
    else if ([string isEqualToString:@"app"]) {
        article = @"an";
    }
    else if ([string isEqualToString:@"artist"]) {
        article = @"an";
    }
    else if ([string isEqualToString:@"album"]) {
        article = @"an";
    }
    else if ([string isEqualToString:@"establishment"]) {
        article = @"an";
    }
    else if ([string isEqualToString:@"other"]) {
        noun = @"thing";
        if (withArticle) {
            return @"";
        }
    }
    else {
        NSSet* others = [NSSet setWithObjects:
                         @"restaurant",
                         @"bar",
                         @"cafe",
                         @"bakery",
                         @"music",
                         @"song",
                         @"book",
                         @"movie",
                         @"film",
                         nil];
        if (![others containsObject:string] && withArticle) {
            return @"";
        }
    }
    if (withArticle) {
        return [NSString stringWithFormat:@"%@ %@", article, noun];
    }
    else {
        return noun;
    }
}

+ (CGRect)originRectWithRect:(CGRect)rect {
    return CGRectMake(0, 0, rect.size.width, rect.size.height);
}

+ (id<STImage>)bestImageFromImages:(NSArray<STImage>*)images forSize:(CGSize)size {
    if (images.count == 0) return nil;
    CGSize bestSize = CGSizeZero;
    id<STImage> best = nil;
    for (id<STImage> image in images) {
        if (!best) {
            best = image;
        }
        else {
            if (image.height && image.width && image.url) {
                CGSize curSize = CGSizeMake(image.width.floatValue, image.height.floatValue);
                if (!best || (curSize.width > size.width && curSize.width < bestSize.width) ) {
                    bestSize = curSize;
                    best = image;   
                }
            }
        }
    }
    return best;
}

+ (STMenuController*)sharedMenuController {
    STAppDelegate* delegate = (id)[UIApplication sharedApplication].delegate;
    return delegate.menuController;
}

+ (UINavigationController*)currentNavigationController {
    STMenuController* root = [self sharedMenuController];
    UIViewController* presented = root.presentedViewController;
    if (!presented) {
        return (id) root.rootViewController;
    }
    return (id)presented;
}

+ (void)pushController:(UIViewController*)controller modal:(BOOL)modal animated:(BOOL)animated {
    if (modal) {
        STMenuController* root = [self sharedMenuController];
        STRootViewController* nav = [[[STRootViewController alloc] initWithRootViewController:controller] autorelease];
        [root presentModalViewController:nav animated:animated];
    }
    else {
        UINavigationController* cur = [self currentNavigationController];
        if (cur) {
            [cur pushViewController:controller animated:animated];
        }
        else {
            NSLog(@"\n\n\n\nNav problem\n\n\n\n%@\n", [self sharedMenuController].rootViewController);
        }
    }
}

+ (void)popControllerAnimated:(BOOL)animated {
    UINavigationController* cur = [self currentNavigationController];
    if (cur) {
        if (cur.viewControllers.count > 1) {
            [cur popViewControllerAnimated:animated];
        }
        else if (cur.viewControllers.count == 1) {
            STMenuController* root = [self sharedMenuController];
            [root dismissModalViewControllerAnimated:animated];
        }
        else {
            NSLog(@"\n\n\nEmpty nav controller\n\n\n");
        }
    }
    else {
        NSLog(@"\n\n\n\nDifferent Nav problem\n\n\n\n");
    }
}

+ (UIViewController*)topController {
    UINavigationController* cur = [self currentNavigationController];
    UIViewController* current = cur.topViewController;
    return current;
}

+ (BOOL)compareAndPopController:(UIViewController*)controller animated:(BOOL)animated {
    UINavigationController* cur = [self currentNavigationController];
    UIViewController* current = cur.topViewController;
    if (current == controller) {
        [self popControllerAnimated:animated];
        return YES;
    }
    else {
        return NO;
    }
}

+ (BOOL)compareAndPushOnto:(UIViewController*)current 
            withController:(UIViewController*)controller
                     modal:(BOOL)modal 
                  animated:(BOOL)animated {
    UINavigationController* cur = [self currentNavigationController];
    UIViewController* current2 = cur.topViewController;
    if (current == current2) {
        [Util pushController:controller modal:modal animated:animated];
        return YES;
    }
    else {
        return NO;
    }
}

+ (void)setRootViewController:(UIViewController*)controller animated:(BOOL)animated {
    STRootViewController* nav = [[[STRootViewController alloc] initWithRootViewController:controller] autorelease];
    [[Util sharedMenuController] setRootController:nav animated:YES];
}

+ (void)goToInboxWithScope:(STStampedAPIScope)scope animated:(BOOL)animated {
    STInboxViewController* controller = [[[STInboxViewController alloc] init] autorelease];
    [Util addHomeButtonToController:controller withBadge:YES];
    [self setRootViewController:controller animated:animated];
}

+ (void)warnWithAPIError:(NSError*)error andBlock:(void (^)())block {
    [self warnWithMessage:error.localizedDescription andBlock:block];
}

+ (NSError*)errorWithDescription:(NSString*)description {
    return [NSError errorWithDomain:@"" code:0 userInfo:[NSDictionary dictionaryWithObject:description forKey:NSLocalizedDescriptionKey]];
}

+ (BOOL)showingFullscreenPopUp {
    return _currentPopUp != nil;
}

@end

@implementation STPopUpView

@synthesize button = button_;
@synthesize view = view_;

- (id)initWithFrame:(CGRect)frame view:(UIView*)view dismissible:(BOOL)dismissible andColor:(UIColor*)color {
    self = [super initWithFrame:frame];
    if (self) {
        self.backgroundColor = color;
        UIView* button = [Util tapViewWithFrame:frame target:self selector:@selector(buttonCallback:) andMessage:nil];
        [self addSubview:button];
        [self addSubview:view];
    }
    return self;
}

- (void)dealloc {
    self.button = nil;
    self.view = nil;
    [super dealloc];
}

-(void)buttonCallback:(id)state {
    [[NSNotificationCenter defaultCenter] postNotificationName:STUtilPopupDismissedNotification object:self];
    [Util setFullScreenPopUp:nil dismissible:NO withBackground:nil];
}

@end

@implementation STUtilButton

@synthesize target = target_;
@synthesize selector = selector_;
@synthesize state = _state;
@synthesize callback = _callback;


- (void)dealloc {
    [_state release];
    [_callback release];
    [super dealloc];
}

- (void)callbackMethod:(id)view {
    if (self.callback) {
        self.callback();
    }
    else {
        [self.target performSelector:self.selector withObject:self.state];
    }
}

@end

@implementation STConfirmationDelegate

@synthesize block = _block;

- (id)init
{
    self = [super init];
    if (self) {
        [self retain];
    }
    return self;
}

- (void)dealloc
{
    [_block release];
    [super dealloc];
}

- (void)actionSheet:(UIActionSheet *)actionSheet clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (self.block) {
        self.block(![[actionSheet buttonTitleAtIndex:buttonIndex] isEqualToString:@"Cancel"]);
    }
    [self autorelease];
}

- (void)actionSheetCancel:(UIActionSheet *)actionSheet {
    if (self.block) {
        self.block(NO);
    }
    [self autorelease];
}

@end

@implementation STWarningDelegate

@synthesize block = _block;

- (id)init
{
    self = [super init];
    if (self) {
        [self retain];
    }
    return self;
}

- (void)dealloc
{
    [_block release];
    [super dealloc];
}

- (void)actionSheet:(UIActionSheet *)actionSheet clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (self.block) {
        self.block();
    }
    [self autorelease];
}

- (void)actionSheetCancel:(UIActionSheet *)actionSheet {
    if (self.block) {
        self.block();
    }
    [self autorelease];
}

@end

@implementation STUtilMenuDelegate

@synthesize block = _block;

- (id)init
{
    self = [super init];
    if (self) {
        [self retain];
    }
    return self;
}

- (void)dealloc
{
    [_block release];
    [super dealloc];
}

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex {
    [self autorelease];
    if (self.block) {
        if (buttonIndex == -1 || buttonIndex == alertView.cancelButtonIndex) {
            self.block(nil);
        }
        else {
            self.block([alertView buttonTitleAtIndex:buttonIndex]);
        }
    }
}

@end

@implementation STUtilTextInputDelegate

@synthesize block = _block;
@synthesize textField = textField_;

- (id)initWithTextField:(UITextField*)textField
{
    self = [super init];
    if (self) {
        [self retain];
        textField_ = [textField retain];
    }
    return self;
}

- (void)dealloc
{
    [textField_ release];
    [_block release];
    [super dealloc];
}

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex {
    [self autorelease];
    if (self.block) {
        if (buttonIndex == -1 || buttonIndex == alertView.cancelButtonIndex) {
            self.block(nil);
        }
        else {
            self.block(self.textField.text);
        }
    }
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
    [textField resignFirstResponder];
    return YES;
}
@end
