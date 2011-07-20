//
//  User.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/19/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "User.h"


@implementation ImageToDataTransformer

+ (BOOL)allowsReverseTransformation {
  return YES;
}

+ (Class)transformedValueClass {
  return [NSData class];
}

- (id)transformedValue:(id)value {
  return UIImagePNGRepresentation(value);
}

- (id)reverseTransformedValue:(id)value {
	return [[[UIImage alloc] initWithData:value] autorelease];
}

@end

@interface User ()
- (void)splitHexString:(NSString*)hexString toRed:(CGFloat*)red green:(CGFloat*)green blue:(CGFloat*)blue;
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


- (void)splitHexString:(NSString*)hexString toRed:(CGFloat*)red green:(CGFloat*)green blue:(CGFloat*)blue {
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

- (void)generateStampImage {
  CGFloat r1, g1, b1, r2, g2, b2;
  [self splitHexString:self.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (self.secondaryColor) {
    [self splitHexString:self.secondaryColor toRed:&r2 green:&g2 blue:&b2];
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
}

@end
