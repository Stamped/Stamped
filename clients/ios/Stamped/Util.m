//
//  Util.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/20/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "Util.h"

#import "User.h"
#import "Entity.h"
#import "SearchResult.h"
#import "PlaceDetailViewController.h"
#import "MusicDetailViewController.h"
#import "BookDetailViewController.h"
#import "OtherDetailViewController.h"
#import "FilmDetailViewController.h"
#import "EntityDetailViewController.h"
#import <QuartzCore/QuartzCore.h>
#import "STActionMenuFactory.h"

NSString* const kTwitterConsumerKey = @"kn1DLi7xqC6mb5PPwyXw";
NSString* const kTwitterConsumerSecret = @"AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU";
NSString* const kTwitterRequestTokenURL = @"https://api.twitter.com/oauth/request_token";
NSString* const kTwitterAuthorizeURL = @"https://api.twitter.com/oauth/authorize";
NSString* const kTwitterAccessTokenURL = @"https://api.twitter.com/oauth/access_token";
NSString* const kOAuthCallbackURL = @"http://www.example.com/oauth_callback";
NSString* const kTwitterScope = @"http://www.example.com/oauth_scope";
NSString* const kKeychainTwitterToken = @"Stamped Twitter";


@interface Util ()
+ (NSString*)userReadableTimeSinceDate:(NSDate*)date shortened:(BOOL)shortened;
@end

@interface STUtilButton : UIButton

@property (nonatomic, assign) id target;
@property (nonatomic, assign) SEL selector; 
@property (nonatomic, retain) id state;

- (void)callback:(id)view;

@end

@interface STPopUpView : UIView

@property (nonatomic, retain) UIView* button;
@property (nonatomic, retain) UIView* view;

- (id)initWithFrame:(CGRect)frame view:(UIView*)view dismissible:(BOOL)dismissible andColor:(UIColor*)color;
- (void)buttonCallback:(id)state;

@end

static STPopUpView* volatile _currentPopUp = nil;

@implementation Util

+ (void)splitHexString:(NSString*)hexString toRed:(CGFloat*)red green:(CGFloat*)green blue:(CGFloat*)blue {
  NSRange range;
  range.location = 0;  
  range.length = 2;
  NSString* rString = [hexString substringWithRange:range];
  range.location = 2;
  NSString* gString = [hexString substringWithRange:range];
  range.location = 4;
  NSString* bString = [hexString substringWithRange:range];
  
  unsigned int r, g, b;
  [[NSScanner scannerWithString:rString] scanHexInt:&r];
  [[NSScanner scannerWithString:gString] scanHexInt:&g];
  [[NSScanner scannerWithString:bString] scanHexInt:&b];
  
  *red = r / 255.0f;
  *green = g / 255.0f;
  *blue = b / 255.0f;
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
  
  UIGraphicsBeginImageContextWithOptions(img.size, NO, 0.0);
  CGContextRef context = UIGraphicsGetCurrentContext();
  
  CGContextTranslateCTM(context, 0, height);
  CGContextScaleCTM(context, 1.0, -1.0);
  
  CGContextClipToMask(context, CGRectMake(0, 0, width, height), img.CGImage);
  CGFloat colors[] = {pRed, pGreen, pBlue, 1.0, sRed, sGreen, sBlue, 1.0};
  CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
  CGGradientRef gradientRef = CGGradientCreateWithColorComponents(colorSpace, colors, NULL, 2);
  CGPoint gradientStartPoint = CGPointMake(0, height);
  CGPoint gradientEndPoint = CGPointMake(width, 0);
  CGContextDrawLinearGradient(context,
                              gradientRef,
                              gradientStartPoint,
                              gradientEndPoint,
                              kCGGradientDrawsAfterEndLocation);
  CGGradientRelease(gradientRef);
  CGColorSpaceRelease(colorSpace);
  UIImage* finalStamp = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
  return finalStamp;
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

+ (UIImage*)stampImageForUser:(User*)user {
  return [Util stampImageWithPrimaryColor:user.primaryColor secondary:user.secondaryColor];
}

+ (UIImage*)stampImageWithPrimaryColor:(NSString*)primary secondary:(NSString*)secondary {
  return [Util gradientImage:[UIImage imageNamed:@"stamp_46pt_texture"]
            withPrimaryColor:primary
                   secondary:secondary];
}

+ (UIImage*)gradientImage:(UIImage*)image withPrimaryColor:(NSString*)primary secondary:(NSString*)secondary {
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:primary toRed:&r1 green:&g1 blue:&b1];
  
  if (secondary) {
    [Util splitHexString:secondary toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  
  return [Util gradientImage:image
              withPrimaryRed:r1
                primaryGreen:g1
                 primaryBlue:b1
                secondaryRed:r2
              secondaryGreen:g2
               secondaryBlue:b2];
}

+ (NSString*)userReadableTimeSinceDate:(NSDate*)date shortened:(BOOL)shortened {
  NSTimeInterval timeSince = fmaxf(0, [[NSDate date] timeIntervalSinceDate:date]);
  if (timeSince > 31556926) {
    CGFloat numYears = floorf(timeSince / 31556926);
    if (shortened)
      return [NSString stringWithFormat:@"%.0fy", numYears];
    
    if (numYears < 2) {
      return @"a year ago";
    } else {
      return [NSString stringWithFormat:@"%.0f years ago", numYears];
    }
  } else if (timeSince > 2629743.83 && !shortened) {  // Don't include months in shortened version.
    CGFloat numMonths = floorf(timeSince / 2629743.83);
    if (numMonths < 2) {
      return @"a month ago";
    } else {
      return [NSString stringWithFormat:@"%.0f months ago", numMonths];
    }
  } else if (timeSince > 604800) {
    CGFloat numWeeks = floorf(timeSince / 604800);
    if (shortened)
      return [NSString stringWithFormat:@"%.0fw", numWeeks];
    
    if (numWeeks < 2) {
      return @"a week ago";
    } else {
      return [NSString stringWithFormat:@"%.0f weeks ago", numWeeks];
    }
  } else if (timeSince > 86400) {
    CGFloat numDays = floorf(timeSince / 86400);
    if (shortened)
      return [NSString stringWithFormat:@"%.0fd", numDays];
    
    if (numDays < 2) {
      return [NSString stringWithFormat:@"%.0f day ago", numDays];
    } else {
      return [NSString stringWithFormat:@"%.0f days ago", numDays];
    }
  } else if (timeSince > 3600) {
    CGFloat numHours = floorf(timeSince / 3600);
    if (shortened)
      return [NSString stringWithFormat:@"%.0fh", numHours];
    
    if (numHours < 2) {
      return [NSString stringWithFormat:@"%.0f hr ago", numHours];
    } else {
      return [NSString stringWithFormat:@"%.0f hrs ago", numHours];
    }
  } else if (timeSince > 60) {
    CGFloat numMin = floorf(timeSince / 60);
    
    if (shortened)
      return [NSString stringWithFormat:@"%.0fm", numMin];
    
    return [NSString stringWithFormat:@"%.0f min ago", numMin];
  } else {
    if (shortened)
      return [NSString stringWithFormat:@"%.0fs", timeSince];
    
    return @"just now";
  }
  return nil;
}

+ (NSString*)shortUserReadableTimeSinceDate:(NSDate*)date {
  return [Util userReadableTimeSinceDate:date shortened:YES];
}

+ (NSString*)userReadableTimeSinceDate:(NSDate*)date {
  return [Util userReadableTimeSinceDate:date shortened:NO];
}

+ (UIViewController*)detailViewControllerForEntity:(Entity*)entityObject {
  UIViewController* detailViewController = nil;
  if (newEDetail) {
    detailViewController = [[EntityDetailViewController alloc] initWithEntityObject:entityObject];
  }
  else {
    switch (entityObject.entityCategory) {
      case EntityCategoryFood:
        detailViewController = [[PlaceDetailViewController alloc] initWithEntityObject:entityObject];
        break;
      case EntityCategoryMusic:
        detailViewController = [[MusicDetailViewController alloc] initWithEntityObject:entityObject];
        break;
      case EntityCategoryBook:
        detailViewController = [[BookDetailViewController alloc] initWithEntityObject:entityObject];
        break;
      case EntityCategoryFilm:
        detailViewController = [[FilmDetailViewController alloc] initWithEntityObject:entityObject];
        break;
      case EntityCategoryOther:
        detailViewController = [[OtherDetailViewController alloc] initWithEntityObject:entityObject];
        break;
      default:
        //      detailViewController = [[GenericItemDetailViewController alloc] initWithEntityObject:entityObject];
        break;
    }
  }
  return [detailViewController autorelease];
}

+ (UIViewController*)detailViewControllerForSearchResult:(SearchResult*)searchResult {
  UIViewController* detailViewController = nil;
  if (newEDetail) {
    detailViewController = [[EntityDetailViewController alloc] initWithSearchResult:searchResult];
  }
  else {
    switch (searchResult.searchCategory) {
      case SearchCategoryFood:
        detailViewController = [[PlaceDetailViewController alloc] initWithSearchResult:searchResult];
        break;
      case SearchCategoryMusic:
        detailViewController = [[MusicDetailViewController alloc] initWithSearchResult:searchResult];
        break;
      case SearchCategoryBook:
        detailViewController = [[BookDetailViewController alloc] initWithSearchResult:searchResult];
        break;
      case SearchCategoryFilm:
        detailViewController = [[FilmDetailViewController alloc] initWithSearchResult:searchResult];
        break;
      case SearchCategoryOther:
        detailViewController = [[OtherDetailViewController alloc] initWithSearchResult:searchResult];
        break;
      default:
        //      detailViewController = [[GenericItemDetailViewController alloc] initWithSearchResult:searchResult];
        break;
    }
  }
  return [detailViewController autorelease];
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
  CGSize titleSize = [title sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:12]];
  if (titleSize.width > 87) {
    BOOL firstLoop = YES;
    while (titleSize.width > 87) {
      if (firstLoop) {
        firstLoop = NO;
        title = [[title substringToIndex:title.length - 1] stringByAppendingString:@"…"];
      } else {
        title = [[title substringToIndex:title.length - 2] stringByAppendingString:@"…"];
      }
      // -2 because we've already appended the ellipsis.
      titleSize = [title sizeWithFont:[UIFont fontWithName:@"Helvetica-Bold" size:12]];
    }
  }
  return title;
}

+ (UIView*)imageViewWithURL:(NSURL*)url andFrame:(CGRect)frame {
  NSData* data = [[NSData alloc] initWithContentsOfURL:url];
  UIImage* image = [UIImage imageWithData:data];
  if (CGRectIsNull(frame)) {
    frame = CGRectMake(0, 0, image.size.width, image.size.height);
  }
  UIImageView* imageView = [[UIImageView alloc] initWithFrame:frame];
  imageView.image = image;
  [data release];
  [imageView autorelease];
  return imageView;
}

+ (UIView*)viewWithText:(NSString*)text font:(UIFont*)font color:(UIColor*)color mode:(UILineBreakMode)mode andMaxSize:(CGSize)size {
  CGSize actualSize = [text sizeWithFont:font constrainedToSize:size lineBreakMode:mode];
  
  UILabel* label = [[UILabel alloc] initWithFrame:CGRectMake(0, 0, actualSize.width, actualSize.height)];
  label.numberOfLines = 0;
  label.lineBreakMode = mode;
  label.text = text;
  label.font = font;
  label.textColor = color;
  label.backgroundColor = [UIColor clearColor];
  [label autorelease];
  return label;
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
  size.width /= scale;
  size.height /= scale;
  return size;
}

+ (UIView*)tapViewWithFrame:(CGRect)frame target:(id)target selector:(SEL)selector andMessage:(id)message {
  STUtilButton* button = [[[STUtilButton alloc] initWithFrame:frame] autorelease];
  button.selector = selector;
  button.target = target;
  button.state = message;
  [button addTarget:button action:@selector(callback:) forControlEvents:UIControlEventTouchUpInside];
  button.backgroundColor = [UIColor clearColor];
  return button;
}

+ (void)setFullScreenPopUp:(UIView*)view dismissible:(BOOL)dismissible withBackground:(UIColor*)color {
  UIWindow* window = [[UIApplication sharedApplication] keyWindow];
  STPopUpView* cur = _currentPopUp;
  if (cur) {
    [cur removeFromSuperview];
    [cur release];
  }
  if (view) {
    STPopUpView* popup = [[[STPopUpView alloc] initWithFrame:window.frame view:view dismissible:dismissible andColor:color] autorelease];
    [window addSubview:popup];
    _currentPopUp = [popup retain];
  }
  else {
    _currentPopUp = nil;
  }
}

+ (CGFloat)imageScale {
  return 2.0;
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

+ (void)didChooseAction:(id<STAction>)action {
  if (action.sources && [action.sources count] > 1) {
    STActionMenuFactory* factory = [[[STActionMenuFactory alloc] init] autorelease];
    NSOperation* operation = [factory createViewWithAction:action forBlock:^(STViewCreator init) {
      if (init) {
        UIView* view = init(nil);
        view.frame = [Util centeredAndBounded:view.frame.size inFrame:[[UIApplication sharedApplication] keyWindow].frame];
        [Util setFullScreenPopUp:view dismissible:YES withBackground:[UIColor colorWithRed:0 green:0 blue:0 alpha:.3]];
      }
    }];
    dispatch_queue_t aQueue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
    
  }
  if (action.sources && [action.sources count] == 1) {
    [Util didChooseSource:[action.sources objectAtIndex:0] withAction:action.action];
  }
}

+ (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action {
  
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
  [Util setFullScreenPopUp:nil dismissible:NO withBackground:nil];
}

@end

@implementation STUtilButton

@synthesize target = target_;
@synthesize selector = selector_;
@synthesize state = state_;

- (void)dealloc {
  self.state = nil;
  [super dealloc];
}

- (void)callback:(id)view {
  [self.target performSelector:self.selector withObject:self.state];
}

@end
