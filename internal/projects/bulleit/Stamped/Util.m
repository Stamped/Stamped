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
#import "GenericItemDetailViewController.h"
#import "MusicDetailViewController.h"
#import "BookDetailViewController.h"
#import "OtherDetailViewController.h"
#import "FilmDetailViewController.h"

NSString* const kTwitterConsumerKey = @"kn1DLi7xqC6mb5PPwyXw";
NSString* const kTwitterConsumerSecret = @"AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU";
NSString* const kTwitterRequestTokenURL = @"https://api.twitter.com/oauth/request_token";
NSString* const kTwitterAuthorizeURL = @"https://api.twitter.com/oauth/authorize";
NSString* const kTwitterAccessTokenURL = @"https://api.twitter.com/oauth/access_token";

NSString* const kOAuthCallbackURL = @"http://www.example.com/oauth_callback";
NSString* const kTwitterScope = @"http://www.example.com/oauth_scope";

NSString* const kKeychainTwitterToken = @"Stamped Twitter";

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
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:primary toRed:&r1 green:&g1 blue:&b1];
  
  if (secondary) {
    [Util splitHexString:secondary toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  
  return [Util gradientImage:[UIImage imageNamed:@"stamp_46pt_texture"]
              withPrimaryRed:r1
                primaryGreen:g1
                 primaryBlue:b1
                secondaryRed:r2
              secondaryGreen:g2
               secondaryBlue:b2];
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
      result = @"a week ago";
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

+ (UIViewController*)detailViewControllerForEntity:(Entity*)entityObject {
  UIViewController* detailViewController = nil;
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
      detailViewController = [[GenericItemDetailViewController alloc] initWithEntityObject:entityObject];
      break;
  }

  return [detailViewController autorelease];
}

+ (UIViewController*)detailViewControllerForSearchResult:(SearchResult*)searchResult {
  UIViewController* detailViewController = nil;
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
      detailViewController = [[GenericItemDetailViewController alloc] initWithSearchResult:searchResult];
      break;
  }

  return [detailViewController autorelease];
}

@end
