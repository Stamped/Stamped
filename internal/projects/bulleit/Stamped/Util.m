//
//  Util.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/20/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "Util.h"

NSString* const kTwitterConsumerKey = @"qGrQ7CoKq00upjxoSSJA";
NSString* const kTwitterConsumerSecret = @"1DQI3LDZiFiDsAorLlu02ZWaHAnuPtbDdaUbvZkPc";
NSString* const kTwitterRequestTokenURL = @"https://api.twitter.com/oauth/request_token";
NSString* const kTwitterAuthorizeURL = @"https://api.twitter.com/oauth/authorize";
NSString* const kTwitterAccessTokenURL = @"https://api.twitter.com/oauth/access_token";

NSString* const kOAuthCallbackURL = @"http://stamped.com/oauth_callback";
NSString* const kTwitterScope = @"http://stamped.com/oauth_scope";

NSString* const kKeychainTwitterToken = @"Twitter for Stamped";

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
  
  CGContextClipToMask(context, CGRectMake(0, 0, width, height), img.CGImage);
  CGFloat colors[] = {pRed, pGreen, pBlue, 1.0, sRed, sGreen, sBlue, 1.0};
  CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
  CGGradientRef gradientRef = CGGradientCreateWithColorComponents(colorSpace, colors, NULL, 2);
  CGPoint gradientStartPoint = CGPointZero;
  CGPoint gradientEndPoint = CGPointMake(width, height);
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

+ (NSString*)userReadableTimeSinceDate:(NSDate*)date {
  NSTimeInterval timeSince = [[NSDate date] timeIntervalSinceDate:date];
  NSString* result = nil;
  if (timeSince > 2629743.83) {
    CGFloat numYears = floorf(timeSince / 262629743.83);
    if (numYears < 2) {
      result = @"last year";
    } else {
      result = [NSString stringWithFormat:@"%.0f years ago", numYears];
    }
  } else if (timeSince > 604800) {
    CGFloat numWeeks = floorf(timeSince / 604800);
    if (numWeeks < 2) {
      result = @"last week";
    } else {
      result = [NSString stringWithFormat:@"%.0f weeks ago", numWeeks];
    }
  } else if (timeSince > 86400) {
    CGFloat numDays = floorf(timeSince / 86400);
    if (numDays < 2) {
      result = [NSString stringWithFormat:@"%.0f day ago", numDays];
    } else {
      result = [NSString stringWithFormat:@"%.0f days ago", numDays];
    }
  } else if (timeSince > 3600) {
    CGFloat numHours = floorf(timeSince / 3600);
    if (numHours < 2) {
      result = [NSString stringWithFormat:@"%.0f hr ago", numHours];
    } else {
      result = [NSString stringWithFormat:@"%.0f hrs ago", numHours];
    }
  } else if (timeSince > 60) {
    result = [NSString stringWithFormat:@"%.0f min ago", floorf(timeSince / 60)];
  } else {
    result = @"just now";
  }
  return result;
}

@end
