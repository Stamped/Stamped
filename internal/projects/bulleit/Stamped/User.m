//
//  User.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "User.h"

#import "Util.h"

@interface User ()
- (void)generateStampImage;
@end

@implementation User
@dynamic bio;
@dynamic displayName;
@dynamic primaryColor;
@dynamic firstName;
@dynamic lastName;
@dynamic userID;
@dynamic website;
@dynamic secondaryColor;
@dynamic profileImageURL;
@dynamic profileImage;
@dynamic screenName;
@dynamic stampImage;
@dynamic Stamps;

- (void)generateStampImage {
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:self.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (self.secondaryColor) {
    [Util splitHexString:self.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  UIImage* img = [UIImage imageNamed:@"stamp_shape_textured"];
  CGFloat width = img.size.width;
  CGFloat height = img.size.height;
  
  UIGraphicsBeginImageContextWithOptions(img.size, NO, 0.0);
  CGContextRef context = UIGraphicsGetCurrentContext();

  CGContextClipToMask(context, CGRectMake(0, 0, width, height), img.CGImage);
  CGFloat colors[] = {r1, g1, b1, 1.0,  r2, g2, b2, 1.0};
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
  self.stampImage = UIGraphicsGetImageFromCurrentImageContext();
  UIGraphicsEndImageContext();
}

- (void)awakeFromFetch {
  [super awakeFromFetch];
  if (!self.stampImage)
    [self generateStampImage];
  if (!self.profileImage) {
    NSData* imageData = [NSData dataWithContentsOfURL:[NSURL URLWithString:self.profileImageURL]];
    self.profileImage = [UIImage imageWithData:imageData];
  }
}

@end
